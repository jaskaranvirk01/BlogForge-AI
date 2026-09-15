from typing import TypedDict, Literal
from uuid import UUID
from blogforge_ai.graph.states.research_state import BlogRequest
from blogforge_ai.schemas.writer_schemas import WriterResult
from blogforge_ai.schemas.global_graph_schema import BlogWorkflowStatus


class GlobalState(TypedDict):
    blog_request: BlogRequest
    research_id: UUID
    analysis_id: UUID
    fact_check_id: UUID
    blog_draft: WriterResult
    draft_id: UUID
    human_decision: Literal['Approve', 'Reject'] | None
    human_feedback: str | None
    workflow_status: BlogWorkflowStatus
