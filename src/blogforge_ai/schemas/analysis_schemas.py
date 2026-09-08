from pydantic import BaseModel
from uuid import UUID
from blogforge_ai.rag.rag_schemas import RetrievalResult


class Evidence(BaseModel):
    source_id: UUID
    chunk_id: UUID


class AnalysisItem(BaseModel):
    claim: str
    explanation: str
    evidence: list[Evidence]


class Reference(BaseModel):
    source_id: UUID
    title: str
    url: str


class LLMEvidence(BaseModel):
    evidence_id: str


class LLMReference(BaseModel):
    source_id: str
    title: str
    url: str


class LLMAnalysisItem(BaseModel):
    claim: str
    explanation: str
    evidence: list[LLMEvidence]


class LLMResult(BaseModel):
    title: str
    overview: str
    developments: list[LLMAnalysisItem]
    limitations: list[LLMAnalysisItem]
    future_scope: list[LLMAnalysisItem]
    references: list[LLMReference]


class AnalysisResult(BaseModel):
    title: str
    overview: str
    developments: list[AnalysisItem]
    limitations: list[AnalysisItem]
    future_scope: list[AnalysisItem]
    references: list[Reference]


class AnalysisQuery(BaseModel):
    query: str
    purpose: str


class AnalysisQueries(BaseModel):
    queries: list[AnalysisQuery]


class AnalysisChunks(BaseModel):
    query: AnalysisQuery
    chunks: list[RetrievalResult]
