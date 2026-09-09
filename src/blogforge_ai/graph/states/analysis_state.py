from typing import TypedDict
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.schemas.analysis_schemas import AnalysisQueries, AnalysisChunks, Evidence, Reference, RetrievalResult, AnalysisResult, LLMResult
from uuid import UUID


class AnalysisState(TypedDict):
    blog_request: BlogRequest
    research_id: UUID
    queries: AnalysisQueries
    retrieved_chunks: list[AnalysisChunks]
    ranked_chunks: list[RetrievalResult]
    analysis_context: str
    evidence_map: dict[str, Evidence]
    source_map: dict[str, Reference]
    llm_result: LLMResult
    analysis_result: AnalysisResult
    analysis_id: UUID
    analysis_status: str
