from pydantic import BaseModel
from blogforge_ai.schemas.writer_schemas import WriterResult
from enum import Enum


class BlogWorkflowStatus(str, Enum):
    STARTED = "started"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    FACT_CHECKING = "fact_checking"
    WRITING = "writing"
    WAITING_FOR_REVIEW = "waiting_for_review"
    COMPLETED = "completed"


class GraphWorkflowResult(BaseModel):
    thread_id: str
    status: BlogWorkflowStatus
    draft: WriterResult | None
