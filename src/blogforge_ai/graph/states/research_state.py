from typing import TypedDict
from blogforge_ai.schemas.research_schemas import BlogRequest, ResearchPlan, SearchOutput, SourceSelection, SelectedSourceData, ResearchResult
from uuid import UUID


class ResearchState(TypedDict):
    blog_request: BlogRequest
    research_plan: ResearchPlan
    search_output: SearchOutput
    source_selection: SourceSelection
    selected_sources: list[SelectedSourceData]
    extracted_sources: list[SelectedSourceData]
    research_result: ResearchResult
    research_status: str  # 'process stages'
    research_id: UUID
