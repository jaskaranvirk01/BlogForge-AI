from blogforge_ai.rag.chunker import chunking_service
from blogforge_ai.rag.embeddings import embedding_service
from blogforge_ai.schemas.research_schemas import ResearchResult
from blogforge_ai.database.models.research import Research
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.database.models.research_source import ResearchSource
from blogforge_ai.rag.knowledge_base_repository import KnowledgeBaseRepository
from blogforge_ai.database.session import db_manager


class KnowledgeBaseService:
    def __init__(self):
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service

    def ingest_research(self, research_output: ResearchResult):

        with db_manager.session() as session:

            knowledge_repository = KnowledgeBaseRepository(session=session)

            research = Research()

            saved_research = knowledge_repository.save_research(
                research=research)

            research_sources = self._create_research_source(
                research_output=research_output, research_id=saved_research.id)

            saved_research_sources = knowledge_repository.save_research_sources(
                sources=research_sources)

            source_ids = {
                source.source_id: source.id for source in saved_research_sources
            }

            research_chunks = self._create_research_chunks(
                research_output=research_output, source_ids=source_ids, research_id=saved_research.id)

            knowledge_repository.save_research_chunks(chunks=research_chunks)

        return saved_research.id

    def retrieve_relevant_chunks(self, research_id, query: str, top_k: int = 5):
        query_embedding = self.embedding_service.embed_query(query=query)
        with db_manager.session() as session:
            knowledge_repository = KnowledgeBaseRepository(session=session)

            retrieved_chunks = knowledge_repository.retrieve_relevant_chunks(
                research_id=research_id, query_embedding=query_embedding, top_k=top_k)

        return retrieved_chunks

    def _create_research_chunks(self, research_output: ResearchResult, source_ids: dict, research_id) -> list[ResearchChunk]:
        chunks = self.chunking_service.chunk_research(
            research_result=research_output)

        if not chunks:
            return []

        embeddings = self.embedding_service.embed_chunks(chunks=chunks)

        research_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            db_source_id = source_ids[chunk.research_source_id]
            research_chunks.append(ResearchChunk(
                research_id=research_id,
                research_source_id=db_source_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
            ))

        return research_chunks

    def _create_research_source(self, research_output: ResearchResult, research_id):

        research_sources = []

        for source in research_output.selected_sources:
            research_sources.append(ResearchSource(
                research_id=research_id,
                source_id=source.source.id,
                title=source.source.title,
                url=source.source.url,
                selection_reason=source.selection_reason
            ))

        return research_sources
