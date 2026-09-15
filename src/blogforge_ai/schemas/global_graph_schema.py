from pydantic import BaseModel
from blogforge_ai.schemas.writer_schemas import WriterResult
from enum import Enum


class BlogWorkflowStatus(str, Enum):
    WAITING_FOR_REVIEW = "waiting_for_review"
    COMPLETED = "completed"


class GraphWorkflowResult(BaseModel):
    thread_id: str
    status: BlogWorkflowStatus
    draft: WriterResult | None
