from typing import TypedDict
from uuid import UUID
from blogforge_ai.graph.states.research_state import BlogRequest
from blogforge_ai.schemas.writer_schemas import WriterLLMResult


class GlobalState(TypedDict):
    blog_request: BlogRequest
    research_id: UUID
    analysis_id: UUID
    fact_check_id: UUID
    blog_draft: WriterLLMResult
    draft_id: UUID
    workflow_status: str
