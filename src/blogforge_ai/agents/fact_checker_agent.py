from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult
from blogforge_ai.schemas.analysis_schemas import AnalysisResult, AnalysisItem
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.database.models.analysis import Analysis
from uuid import UUID


class FactCheckingAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.fact_checking_llm = self.llm.with_structured_output(
            FactCheckResult)

    def retrieve_analyses(self, research_id: UUID) -> list[Analysis]:
        analyses = self.knowledge_base_service.retrieve_analysis(
            research_id=research_id)

        return analyses

    def retrieve_claims(self, analyses: list[Analysis]) -> list[AnalysisItem]:
        claims = []

        for analysis in analyses:
            for claim in analysis.developments:
                claims.append(claim)
