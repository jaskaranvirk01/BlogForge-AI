from typing import TypedDict
from blogforge_ai.schemas.writer_schemas import WriterLLMResult, WriterLLMInput, BlogRequest
from blogforge_ai.database.models.fact_check import FactCheck
from uuid import UUID


class WriterState(TypedDict):
    fact_check_id: UUID
    blog_request: BlogRequest
    fact_check: FactCheck
    llm_input: WriterLLMInput
    blog_draft: WriterLLMResult
    draft_id: UUID
    writer_status: str
