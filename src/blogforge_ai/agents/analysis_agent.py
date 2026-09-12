from blogforge_ai.llm.client import llm
from blogforge_ai.schemas.analysis_schemas import AnalysisQueries, AnalysisResult, AnalysisItem, AnalysisChunks, RetrievalResult, Evidence, LLMResult, Reference
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.prompts.analysis_prompts import QUERY_PLANNING_PROMPT, ANALYSIS_PROMPT
from uuid import UUID
from blogforge_ai.exceptions.analysis import AnalysisGenerationError
from blogforge_ai.exceptions.error_codes import ErrorCodes


class AnalysisAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.query_planning_llm = self.llm.with_structured_output(
            AnalysisQueries)
        self.analysis_llm = self.llm.with_structured_output(LLMResult)
        self.chunk_limit = 10

    def plan_retrieval_queries(self, blog_request: BlogRequest) -> AnalysisQueries:
        messages = [SystemMessage(
            content=QUERY_PLANNING_PROMPT), HumanMessage(content=blog_request.model_dump_json(indent=1))]
        try:

            return self.query_planning_llm.invoke(messages)
        except Exception as e:
            raise AnalysisGenerationError(
                message='Retrievel Query Generation failed',
                error_code=ErrorCodes.ANALYSIS_GENERATION_FAILED,
                workflow='analysis',
                node='plan_retrieval_queries',
                retryable=False,
                cause=e
            )

    def retrieve_analysis_chunks(self, analysis_queries: AnalysisQueries, research_id: UUID) -> list[AnalysisChunks]:

        retrieved_chunks = []

        for query in analysis_queries.queries:
            chunks = self.knowledge_base_service.retrieve_relevant_chunks(
                research_id=research_id, query=query.query)
            retrieved_chunks.append(AnalysisChunks(query=query, chunks=chunks))

        return retrieved_chunks

    def rank_and_deduplicate_chunks(self, analysis_chunks: list[AnalysisChunks]) -> list[RetrievalResult]:
        unique_chunks: dict[UUID, RetrievalResult] = {}

        for analysis_chunk in analysis_chunks:
            for chunk in analysis_chunk.chunks:
                existing = unique_chunks.get(chunk.chunk_id)
                if existing is None:
                    unique_chunks[chunk.chunk_id] = chunk
                elif chunk.similarity_score > existing.similarity_score:
                    unique_chunks[chunk.chunk_id] = chunk

        sorted_chunks = sorted(unique_chunks.values(),
                               key=lambda chunk: chunk.similarity_score,
                               reverse=True
                               )

        return sorted_chunks

    def build_analysis_context(self, chunks: list[RetrievalResult]) -> tuple[str, dict[str, Evidence], dict[str, Reference]]:

        chunks_to_include = chunks[:self.chunk_limit]

        evidence_map = self._map_evidence(chunks_to_include)
        source_map = self._map_sources(chunks=chunks_to_include)

        source_id_map = {
            reference.source_id: llm_source_id
            for llm_source_id, reference in source_map.items()
        }

        evidence_blocks = []
        source_blocks = []

        for index, chunk in enumerate(chunks_to_include):
            llm_evidence_id = f'E{index+1}'
            llm_source_id = source_id_map[chunk.source_id]
            evidence_blocks.append(f'''\n
            EVIDENCE ID - {llm_evidence_id}\n
            SOURCE ID : {llm_source_id}\n
            Source Title:{chunk.source_title}\n
            Source URL:{chunk.source_url}\n
            \n\n
            Content :\n
            {chunk.content}\n
            ''')

        for llm_source_id, reference in source_map.items():
            source_blocks.append(
                f'''
            SOURCE ID : {llm_source_id}\n
            Source Title : {reference.title}\n
            Source Url : {reference.url}\n
            '''
            )

        evidence_context = '\n\n'.join(evidence_blocks)
        source_context = '\n\n'.join(source_blocks)

        analysis_context = f"""
        SOURCE CONTEXT:

        {source_context}


        EVIDENCE CONTEXT:

        {evidence_context}
        """

        return analysis_context, evidence_map, source_map

    def generate_analysis(self, blog_request: BlogRequest, analysis_context: str) -> LLMResult:
        messages = [SystemMessage(
            content=ANALYSIS_PROMPT), HumanMessage(content=f'''
            BLOG REQUEST:
            {blog_request.model_dump_json(indent=1)}
            \n\n
            ANALYSIS CONTEXT:
            {analysis_context}
            ''')]
        try:
            return self.analysis_llm.invoke(messages)
        except Exception as e:
            raise AnalysisGenerationError(
                message='Analysis Generation failed',
                error_code=ErrorCodes.ANALYSIS_GENERATION_FAILED,
                workflow='analysis',
                node='generate_analysis',
                retryable=False,
                cause=e
            )

    def _map_evidence(self, chunks: list[RetrievalResult]) -> dict[str, Evidence]:

        mapped_evidences = {}

        for index, chunk in enumerate(chunks):
            mapped_evidences[f'E{index+1}'] = Evidence(
                chunk_id=chunk.chunk_id,
                source_id=chunk.source_id
            )

        return mapped_evidences

    def _map_sources(self, chunks: list[RetrievalResult]) -> dict[str, Reference]:
        mapped_sources = {}
        unique_sources = {}

        for chunk in chunks:
            if chunk.source_id not in unique_sources:
                unique_sources[chunk.source_id] = chunk

        for index, chunk in enumerate(unique_sources.values()):
            mapped_sources[f'S{index+1}'] = Reference(
                source_id=chunk.source_id,
                title=chunk.source_title,
                url=chunk.source_url
            )

        return mapped_sources

    def prepare_analysis_result(self, llm_result: LLMResult, evidence_map: dict[str, Evidence], source_map: dict[str, Reference]) -> AnalysisResult:

        developments = []
        limitations = []
        future_scope = []
        references = []

        for llm_item in llm_result.developments:
            result_evidence = []

            for llm_evidence in llm_item.evidence:
                evidence = evidence_map[llm_evidence.evidence_id]
                result_evidence.append(
                    Evidence(
                        chunk_id=evidence.chunk_id,
                        source_id=evidence.source_id
                    )
                )

            developments.append(AnalysisItem(
                claim=llm_item.claim,
                explanation=llm_item.explanation,
                evidence=result_evidence
            ))

        for llm_item in llm_result.limitations:
            result_evidence = []

            for llm_evidence in llm_item.evidence:
                evidence = evidence_map[llm_evidence.evidence_id]
                result_evidence.append(
                    Evidence(
                        chunk_id=evidence.chunk_id,
                        source_id=evidence.source_id
                    )
                )

            limitations.append(AnalysisItem(
                claim=llm_item.claim,
                explanation=llm_item.explanation,
                evidence=result_evidence
            ))
        for llm_item in llm_result.future_scope:
            result_evidence = []

            for llm_evidence in llm_item.evidence:
                evidence = evidence_map[llm_evidence.evidence_id]
                result_evidence.append(
                    Evidence(
                        chunk_id=evidence.chunk_id,
                        source_id=evidence.source_id
                    )
                )

            future_scope.append(AnalysisItem(
                claim=llm_item.claim,
                explanation=llm_item.explanation,
                evidence=result_evidence
            ))

        for llm_item in llm_result.references:
            reference = source_map[llm_item.source_id]

            references.append(Reference(
                source_id=reference.source_id,
                title=reference.title,
                url=reference.url
            ))

        return AnalysisResult(
            title=llm_result.title,
            overview=llm_result.overview,
            developments=developments,
            limitations=limitations,
            future_scope=future_scope,
            references=references
        )


analysis_agent = AnalysisAgent()


# ==============================================
