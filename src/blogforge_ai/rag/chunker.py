from blogforge_ai.schemas.research_schemas import ResearchResult
from blogforge_ai.rag.rag_schemas import ResearchChunk
from langchain_text_splitters.character import RecursiveCharacterTextSplitter


class ChunkingService:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

    def chunk_research(self, research_result: ResearchResult, source_ids: dict) -> list[ResearchChunk]:

        chunks = []

        for selected_source in research_result.selected_sources:
            if selected_source.extracted_content:
                content = selected_source.extracted_content.content.content
            elif selected_source.source.content:
                content = selected_source.source.content
            else:
                continue

            db_source_id = source_ids[selected_source.source.id]
            text_chunks = self.text_splitter.split_text(content)

            for chunk_index, chunk in enumerate(text_chunks):
                chunks.append(ResearchChunk(
                    research_id=research_result.research_id,
                    research_source_id=db_source_id,
                    content=chunk,
                    chunk_index=chunk_index,
                    source_title=selected_source.source.title,
                    source_url=selected_source.source.url
                ))

        return chunks


chunking_service = ChunkingService()
