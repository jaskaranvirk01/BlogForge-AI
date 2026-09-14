from pydantic import BaseModel, Field
from blogforge_ai.schemas.writer_schemas import WriterResult
from enum import Enum


class CreateBlogRequest(BaseModel):
    topic: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    desired_length: int = Field(gt=0)
    tone: str = Field(min_length=1)
    additional_instructions: str | None = None


class BlogWorkflowStatus(str, Enum):
    WAITING_FOR_REVIEW = "waiting_for_review"
    COMPLETED = "completed"


class BlogWorkflowResponse(BaseModel):
    thread_id: str
    status: BlogWorkflowStatus
    draft: WriterResult | None
