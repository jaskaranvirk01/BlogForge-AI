from pydantic import BaseModel
from uuid import UUID
from blogforge_ai.schemas.research_schemas import BlogRequest


class WriterInput(BaseModel):
    blog_request: BlogRequest
    fact_check_id: UUID
