from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ResearchChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    research_id: UUID
    research_source_id: str
    content: str
    chunk_index: int
    source_title: str
    source_url: str
    metadata: dict | None = None


class RetrievalResult(BaseModel):
    chunk_id: UUID
    research_id: UUID
    source_id: str
    content: str
    source_title: str
    source_url: str
    similarity_score: float
    metadata: dict | None = None
