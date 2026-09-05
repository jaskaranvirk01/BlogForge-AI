from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult
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
            FactCheckResult)

    def retrieve_analyses(self, research_id: UUID) -> list[Analysis]:
        analyses = self.knowledge_base_service.retrieve_analyses(
            research_id=research_id)

        return analyses

    def retrieve_claims(self, analyses: list[Analysis]) -> list[AnalysisItem]:
        claims = []

        for analysis in analyses:
            for claim in analysis.developments:
                claims.append(AnalysisItem.model_validate(claim))

            for claim in analysis.limitations:
                claims.append(AnalysisItem.model_validate(claim))

            for claim in analysis.future_scope:
                claims.append(AnalysisItem.model_validate(claim))

        return claims

    def retrieve_evidence(self, analysis_item: AnalysisItem) -> list[ResearchChunk]:
        chunk_ids = []
        for evidence in analysis_item.evidence:
            chunk_ids.append(evidence.chunk_id)

        if len(chunk_ids) == 0:
            return []

        chunks = self.knowledge_base_service.retrieve_chunks_by_ids(
            chunk_ids=chunk_ids)
        return chunks

    def verify_claims(self, analysis_items: list[AnalysisItem]) -> FactCheckResult:

        verification_items = []

        for analysis_item in analysis_items:

            evidence_chunks = self.retrieve_evidence(
                analysis_item=analysis_item)

            verification_items.append({
                'claim': analysis_item.claim,
                'explanation': analysis_item.explanation,
                'evidence': [{
                    'id': str(chunk.id),
                    'content': chunk.content
                } for chunk in evidence_chunks]
            })

        messages = [SystemMessage(content=FACT_CHECKING_PROMPT), HumanMessage(
            content=json.dumps(verification_items)
        )]

        return self.fact_checking_llm.invoke(messages)
