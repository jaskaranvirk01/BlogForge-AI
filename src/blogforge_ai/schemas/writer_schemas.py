from pydantic import BaseModel
from uuid import UUID
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.schemas.fact_checker_schemas import FactCheckItem, Reference


class WriterInput(BaseModel):
    blog_request: BlogRequest
    fact_check_id: UUID


class WriterLLMInput(BaseModel):
    blog_request: BlogRequest
    fact_check_title: str
    fact_check_overview: str
    verified_claims: list[FactCheckItem]
    references: list[Reference]


class BlogSection(BaseModel):
    heading: str
    content: str


class WriterLLMResult(BaseModel):
    blog_title: str
    blog_introduction: str
    sections: list[BlogSection]
    conclusion: str
    references: list[Reference]
