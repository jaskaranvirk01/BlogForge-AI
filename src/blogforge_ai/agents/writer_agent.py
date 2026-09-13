from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.schemas.writer_schemas import WriterLLMInput, BlogRequest, WriterLLMResult, WriterResult, FactCheckContent, LLMFactCheckEvidence, LLMFactCheckItem, LLMReference
from blogforge_ai.prompts.writer_prompts import BLOG_WRITING_SYSTEM_PROMPT
from blogforge_ai.schemas.fact_checker_schemas import VerificationVerdict, Evidence, Reference
from langchain_core.messages import SystemMessage, HumanMessage
from uuid import UUID
from blogforge_ai.exceptions.writer import WriterGenerationError
from blogforge_ai.exceptions.error_codes import ErrorCodes


class WriterAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.blog_writing_llm = self.llm.with_structured_output(
            WriterLLMResult)

    def retrieve_fact_check(self, fact_check_id: UUID) -> FactCheckContent:
        fact_check = self.knowledge_base_service.retrieve_fact_check_by_id(
            fact_check_id=fact_check_id)
        return FactCheckContent.model_validate(fact_check)

    def prepare_writer_input(self, fact_check: FactCheckContent, blog_request: BlogRequest, human_feedback: str | None) -> tuple[WriterLLMInput, dict[str, Evidence], dict[str, Reference]]:

        evidence_map = {}
        evidence_counter = 1

        reference_map = {}
        reference_counter = 1

        fact_check_claims = fact_check.claims

        verified_claims = [
            claim for claim in fact_check_claims if claim.verdict == VerificationVerdict.SUPPORTED]

        llm_claims = []

        for claim in verified_claims:
            llm_evidences = []

            for fact_check_evidence in claim.evidence:
                evidence_id = f'E{evidence_counter}'
                evidence_counter += 1

                evidence_map[evidence_id] = Evidence(
                    source_id=fact_check_evidence.source_id,
                    chunk_id=fact_check_evidence.chunk_id
                )
                llm_evidences.append(
                    LLMFactCheckEvidence(
                        evidence_id=evidence_id
                    )
                )

            llm_claims.append(
                LLMFactCheckItem(
                    claim=claim.claim,
                    explanation=claim.explanation,
                    evidence=llm_evidences
                )
            )

        for reference in fact_check.references:
            reference_id = f'S{reference_counter}'
            reference_counter += 1

            reference_map[reference_id] = Reference(
                source_id=reference.source_id,
                title=reference.title,
                url=reference.url
            )

        llm_references = [LLMReference(
            source_id=reference_id,
            title=reference.title,
            url=reference.url
        )
            for reference_id, reference in reference_map.items()]

        return WriterLLMInput(
            blog_request=blog_request,
            human_feedback=human_feedback,
            fact_check_title=fact_check.title,
            fact_check_overview=fact_check.overview,
            verified_claims=llm_claims,
            references=llm_references
        ), evidence_map, reference_map

    def write_blog(self, llm_input: WriterLLMInput) -> WriterLLMResult:

        messages = [SystemMessage(content=BLOG_WRITING_SYSTEM_PROMPT), HumanMessage(
            content=llm_input.model_dump_json()
        )]
        try:
            return self.blog_writing_llm.invoke(messages)
        except Exception as e:
            raise WriterGenerationError(
                message="Blog Draft Generation failed",
                error_code=ErrorCodes.WRITER_GENERATION_FAILED,
                workflow="writing",
                node="write_blog",
                retryable=False,
                cause=e,
            )

    def create_writer_result(self, llm_result: WriterLLMResult, reference_map: dict[str, Reference]) -> WriterResult:

        references = []

        for llm_reference in llm_result.references:
            reference = reference_map[llm_reference.source_id]
            references.append(
                Reference(
                    source_id=reference.source_id,
                    title=reference.title,
                    url=reference.url
                )
            )

        return WriterResult(
            blog_title=llm_result.blog_title,
            blog_introduction=llm_result.blog_introduction,
            sections=llm_result.sections,
            conclusion=llm_result.conclusion,
            references=references
        )


writer_agent = WriterAgent()
