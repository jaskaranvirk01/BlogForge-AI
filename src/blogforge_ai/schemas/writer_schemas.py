from pydantic import BaseModel, ConfigDict
from uuid import UUID
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.schemas.fact_checker_schemas import FactCheckItem, Reference


class WriterInput(BaseModel):
    blog_request: BlogRequest
    fact_check_id: UUID


class LLMFactCheckEvidence(BaseModel):
    evidence_id: str


class LLMFactCheckItem(BaseModel):
    claim: str
    explanation: str
    evidence: list[LLMFactCheckEvidence]


class LLMReference(BaseModel):
    source_id: str
    title: str
    url: str


class WriterLLMInput(BaseModel):
    blog_request: BlogRequest
    human_feedback: str | None
    fact_check_title: str
    fact_check_overview: str
    verified_claims: list[LLMFactCheckItem]
    references: list[LLMReference]


class BlogSection(BaseModel):
    heading: str
    content: str


class WriterLLMResult(BaseModel):
    blog_title: str
    blog_introduction: str
    sections: list[BlogSection]
    conclusion: str
    references: list[LLMReference]


class WriterResult(BaseModel):
    blog_title: str
    blog_introduction: str
    sections: list[BlogSection]
    conclusion: str
    references: list[Reference]


class FactCheckContent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    analysis_id: UUID
    title: str
    overview: str
    claims: list[FactCheckItem]
    references: list[Reference]
