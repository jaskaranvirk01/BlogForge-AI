from blogforge_ai.llm.client import llm
from blogforge_ai.schemas.analysis_schemas import AnalysisQueries, AnalysisResult, AnalysisChunks, RetrievalResult, Evidence, LLMResult, Reference
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.prompts.analysis_prompts import QUERY_PLANNING_PROMPT, ANALYSIS_PROMPT
from uuid import UUID
from rich import print


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

        return self.query_planning_llm.invoke(messages)

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

    def build_analysis_context(self, chunks: list[RetrievalResult]) -> tuple[str, dict[str, Evidence]]:

        chunks_to_include = chunks[:self.chunk_limit]

        evidence_map = self._map_evidence(chunks_to_include)

        evidence_blocks = []

        for index, chunk in enumerate(chunks_to_include):
            llm_id = f'E{index+1}'
            evidence_blocks.append(f'''\n
            EVIDENCE ID - {llm_id}\n
            Source Title:{chunk.source_title}\n
            Source URL:{chunk.source_url}\n
            \n\n
            Content :\n
            {chunk.content}\n
            ''')
        analysis_context = '\n\n'.join(evidence_blocks)
        return analysis_context, evidence_map

    def generate_analysis(self, blog_request: BlogRequest, analysis_context: str) -> LLMResult:
        messages = [SystemMessage(
            content=ANALYSIS_PROMPT), HumanMessage(content=f'''
            BLOG REQUEST: 
            {blog_request.model_dump_json(indent=1)}
            \n\n
            ANALYSIS CONTEXT:
            {analysis_context}
            ''')]

        return self.analysis_llm.invoke(messages)

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


analysis_agent = AnalysisAgent()


# ==============================================

research_id = '39f9a357-8d53-4862-9bce-73f35ac8108e'


blog_request = BlogRequest(
    topic="Iphone 17",
    target_audience="Teenagers",
    content_type="Brief summary",
    desired_length=150,
    tone="professional",
    additional_instructions="Focus on a brief introduction type blog",
)


queries = analysis_agent.plan_retrieval_queries(blog_request=blog_request)
chunks = analysis_agent.retrieve_analysis_chunks(
    analysis_queries=queries, research_id=research_id)
selected_chunks = analysis_agent.rank_and_deduplicate_chunks(
    analysis_chunks=chunks)

context, evidence_map = analysis_agent.build_analysis_context(
    chunks=selected_chunks)


analysis = analysis_agent.generate_analysis(
    blog_request=blog_request, analysis_context=context)

print(analysis)
