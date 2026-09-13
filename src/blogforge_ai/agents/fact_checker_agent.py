from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult, RetrievedClaims, VerificationResult, FactCheckItem, AnalysisContent, LLMVerificationResult, Evidence, VerificationItem
from blogforge_ai.schemas.analysis_schemas import AnalysisItem
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.prompts.fact_checking_prompts import FACT_CHECKING_PROMPT
from uuid import UUID
import json
from blogforge_ai.exceptions.fact_checker import FactCheckGenerationError
from blogforge_ai.exceptions.error_codes import ErrorCodes


class FactCheckingAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.fact_checking_llm = self.llm.with_structured_output(
            LLMVerificationResult)

    def retrieve_analysis(self, research_id: UUID) -> AnalysisContent:
        analysis = self.knowledge_base_service.retrieve_latest_analysis(
            research_id=research_id)

        return AnalysisContent.model_validate(analysis)

    def retrieve_claims(self, analysis: AnalysisContent) -> RetrievedClaims:
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

    def verify_claims(self, claims: RetrievedClaims) -> tuple[LLMVerificationResult, dict[str, Evidence]]:

        verification_inputs = []
        evidence_map = {}
        evidence_count = 1

        for analysis_item in claims.claims:

            evidence_chunks = self.retrieve_evidence(
                analysis_item=analysis_item)

            llm_evidence = []

            for chunk in evidence_chunks:
                evidence_id = f'E{evidence_count}'
                evidence_count += 1

                evidence_map[evidence_id] = Evidence(
                    source_id=chunk.research_source_id,
                    chunk_id=chunk.id
                )

                llm_evidence.append({
                    'evidence_id': evidence_id,
                    'content': chunk.content
                })

            verification_inputs.append({
                'claim': analysis_item.claim,
                'explanation': analysis_item.explanation,
                'evidence': llm_evidence
            })

        verification_input = {
            "claims": verification_inputs
        }

        messages = [SystemMessage(content=FACT_CHECKING_PROMPT), HumanMessage(
            content=json.dumps(verification_input)
        )]
        try:
            verification_results = self.fact_checking_llm.invoke(messages)
        except Exception as e:
            raise FactCheckGenerationError(
                message="Fact Check Generation Failed",
                error_code=ErrorCodes.FACT_CHECK_GENERATION_FAILED,
                workflow="fact_check",
                node="verify_claims",
                retryable=False,
                cause=e
            )

        expected_count = len(claims.claims)
        actual_count = len(verification_results.verifications)

        if actual_count != expected_count:
            raise ValueError(
                f"Fact-checking LLM returned {actual_count} verifications "
                f"for {expected_count} claims."
            )
        return verification_results, evidence_map

    def resolve_evidence(self, verification_result: LLMVerificationResult, evidence_map: dict[str, Evidence]) -> VerificationResult:
        verifications = []
        for verification in verification_result.verifications:
            evidences = []
            for item in verification.evidence:
                evidence = evidence_map[item.evidence_id]
                evidences.append(Evidence(
                    chunk_id=evidence.chunk_id,
                    source_id=evidence.source_id
                ))
            verifications.append(VerificationItem(
                claim=verification.claim,
                explanation=verification.explanation,
                verdict=verification.verdict,
                evidence=evidences
            ))

        return VerificationResult(
            verifications=verifications
        )

    def build_fact_check_result(self, analysis: AnalysisContent,  verification_result: VerificationResult) -> FactCheckResult:
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
