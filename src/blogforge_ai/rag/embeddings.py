from langchain_huggingface import HuggingFaceEmbeddings
from blogforge_ai.rag.rag_schemas import ResearchChunk
from blogforge_ai.core.settings import settings


class EmbeddingService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={
                "device": "cpu",
            },
        )

    def embed_chunks(self, chunks: list[ResearchChunk]) -> list[list[float]]:

        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]

        return self.embeddings.embed_documents(texts=texts)

    def embed_query(self, query: str) -> list[float]:
        return self.embeddings.embed_query(text=query)


embedding_service = EmbeddingService()
