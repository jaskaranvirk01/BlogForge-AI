from blogforge_ai.llm.client import llm
from blogforge_ai.schemas.analysis_schemas import AnalysisQuery, AnalysisQueries, AnalysisResult, AnalysisChunks, RetrievalResult
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.prompts.analysis_prompts import QUERY_PLANNING_PROMPT
from uuid import UUID


class AnalysisAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service
        self.query_planning_llm = self.llm.with_structured_output(
            AnalysisQueries)
        self.analysis_llm = self.llm.with_structured_output(AnalysisResult)

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
