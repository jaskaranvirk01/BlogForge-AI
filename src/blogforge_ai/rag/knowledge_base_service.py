from urllib.parse import urlparse
from blogforge_ai.rag.chunker import chunking_service
from blogforge_ai.rag.embeddings import embedding_service
from blogforge_ai.schemas.research_schemas import ResearchResult
from blogforge_ai.database.models.research import Research
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.database.models.research_source import ResearchSource


class KnowledgeBaseService:
    def __init__(self):
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.knowledge_repository = None  # will create later

    def ingest_research(self, research_output: ResearchResult):
        research_sources = self._create_research_source(
            research_output=research_output)
        research_chunks = self._create_research_chunks(
            research_output=research_output)

    def _create_research_chunks(self, research_output: ResearchResult) -> list[ResearchChunk]:
        chunks = self.chunking_service.chunk_research(
            research_result=research_output)

        if not chunks:
            return []

        embeddings = self.embedding_service.embed_chunks(chunks=chunks)

        research_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            research_chunks.append(ResearchChunk(
                research_id=research_output.research_id,
                research_source_id=chunk.research_source_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
            ))

        return research_chunks

    def _create_research_source(self, research_output: ResearchResult):

        research_sources = []

        for source in research_output.selected_sources:
            research_sources.append(ResearchSource(
                research_id=research_output.research_id,
                source_id=source.source.id,
                title=source.source.title,
                url=source.source.url,
                selection_reason=source.selection_reason
            ))

        return research_sources
