from typing import TypedDict
from blogforge_ai.schemas.writer_schemas import WriterLLMResult, WriterLLMInput, BlogRequest, FactCheckContent
from uuid import UUID


class WriterState(TypedDict):
    fact_check_id: UUID
    blog_request: BlogRequest
    fact_check: FactCheckContent
    llm_input: WriterLLMInput
    blog_draft: WriterLLMResult
    human_feedback: str | None
    draft_id: UUID
    writer_status: str
