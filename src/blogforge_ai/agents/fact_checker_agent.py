from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult, RetrievedClaims, VerificationResult, FactCheckItem
from blogforge_ai.schemas.analysis_schemas import AnalysisItem
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.database.models.analysis import Analysis
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.prompts.fact_checking_prompts import FACT_CHECKING_PROMPT
from uuid import UUID
import json


class FactCheckingAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.fact_checking_llm = self.llm.with_structured_output(
            VerificationResult)

    def retrieve_analysis(self, research_id: UUID) -> Analysis:
        analysis = self.knowledge_base_service.retrieve_latest_analysis(
            research_id=research_id)

        return analysis

    def retrieve_claims(self, analysis: Analysis) -> RetrievedClaims:
        claims = []

        for claim in analysis.developments:
            claims.append(AnalysisItem.model_validate(claim))

        for claim in analysis.limitations:
            claims.append(AnalysisItem.model_validate(claim))

        for claim in analysis.future_scope:
            claims.append(AnalysisItem.model_validate(claim))

        return RetrievedClaims(
            claims=claims
        )

    def retrieve_evidence(self, analysis_item: AnalysisItem) -> list[ResearchChunk]:
        chunk_ids = []
        for evidence in analysis_item.evidence:
            chunk_ids.append(evidence.chunk_id)

        if len(chunk_ids) == 0:
            return []

        chunks = self.knowledge_base_service.retrieve_chunks_by_ids(
            chunk_ids=chunk_ids)
        return chunks

    def verify_claims(self, claims: RetrievedClaims) -> VerificationResult:

        verification_inputs = []

        for analysis_item in claims.claims:

            evidence_chunks = self.retrieve_evidence(
                analysis_item=analysis_item)

            verification_inputs.append({
                'claim': analysis_item.claim,
                'explanation': analysis_item.explanation,
                'evidence': [{
                    "source_id": str(chunk.research_source_id),
                    "chunk_id": str(chunk.id),
                    "content": chunk.content
                } for chunk in evidence_chunks
                ]
            })

        verification_input = {
            "claims": verification_inputs
        }
        print(f'Vrification input len :{len(verification_inputs)} ')
        for item in verification_inputs:
            print(item)
        messages = [SystemMessage(content=FACT_CHECKING_PROMPT), HumanMessage(
            content=json.dumps(verification_input)
        )]

        verification_results = self.fact_checking_llm.invoke(messages)
        print('llm result')
        print(verification_results)

        return verification_results

    def build_fact_check_result(self, analysis: Analysis,  verification_result: VerificationResult) -> FactCheckResult:
        claims = []

        for verification in verification_result.verifications:

            claims.append(
                FactCheckItem(
                    claim=verification.claim,
                    explanation=verification.explanation,
                    verdict=verification.verdict,
                    evidence=verification.evidence
                )
            )

        return FactCheckResult(
            title=analysis.title,
            overview=analysis.overview,
            claims=claims,
            references=analysis.references
        )


fact_checking_agent = FactCheckingAgent()
