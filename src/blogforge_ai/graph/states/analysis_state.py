from typing import TypedDict
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.schemas.analysis_schemas import AnalysisQueries, AnalysisChunks, RetrievalResult, AnalysisResult
from uuid import UUID


class AnalysisState(TypedDict):
    blog_request: BlogRequest
    research_id: UUID
    queries: AnalysisQueries
    retrieved_chunks: list[AnalysisChunks]
    ranked_chunks: list[RetrievalResult]
    analysis_context: str
    generated_analysis: AnalysisResult
    analysis_id: UUID
    analysis_status: str
