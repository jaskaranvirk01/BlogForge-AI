from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.database.models.fact_check import FactCheck
from blogforge_ai.schemas.writer_schemas import WriterLLMInput, BlogRequest, WriterLLMResult
from blogforge_ai.prompts.writer_prompts import BLOG_WRITING_SYSTEM_PROMPT
from blogforge_ai.schemas.fact_checker_schemas import VerificationVerdict
from langchain_core.messages import SystemMessage, HumanMessage
from uuid import UUID
import json


class WriterAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.blog_writing_llm = self.llm.with_structured_output(
            WriterLLMResult)

    def retrieve_fact_check(self, fact_check_id: UUID) -> FactCheck:
        fact_check = self.knowledge_base_service.retrieve_fact_check_by_id(
            fact_check_id=fact_check_id)
        return fact_check

    def prepare_writer_input(self, fact_check: FactCheck, blog_request: BlogRequest) -> WriterLLMInput:
        return WriterLLMInput(
            blog_request=blog_request,
            fact_check_title=fact_check.title,
            fact_check_overview=fact_check.overview,
            verified_claims=[
                claim for claim in fact_check.claims if claim.verdict == VerificationVerdict.SUPPORTED],
            references=fact_check.references
        )

    def write_blog(self, llm_input: WriterLLMInput) -> WriterLLMResult:

        messages = [SystemMessage(content=BLOG_WRITING_SYSTEM_PROMPT), HumanMessage(
            content=json.dumps(llm_input.model_dump())
        )]

        return self.blog_writing_llm.invoke(messages)
