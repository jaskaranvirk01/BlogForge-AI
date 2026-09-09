from typing import TypedDict
from blogforge_ai.schemas.writer_schemas import WriterLLMResult, WriterLLMInput, BlogRequest, FactCheckContent, WriterResult
from blogforge_ai.schemas.fact_checker_schemas import Evidence, Reference
from uuid import UUID


class WriterState(TypedDict):
    fact_check_id: UUID
    blog_request: BlogRequest
    fact_check: FactCheckContent
    llm_input: WriterLLMInput
    evidence_map: dict[str, Evidence]
    reference_map: dict[str, Reference]
    llm_result: WriterLLMResult
    writer_result: WriterResult
    human_feedback: str | None
    draft_id: UUID
    writer_status: str
