from pydantic import BaseModel, Field, model_validator
from blogforge_ai.schemas.writer_schemas import WriterResult
from blogforge_ai.schemas.global_graph_schema import BlogWorkflowStatus
from enum import Enum


class CreateBlogRequest(BaseModel):
    topic: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    desired_length: int = Field(gt=0)
    tone: str = Field(min_length=1)
    additional_instructions: str | None = None


class BlogWorkflowStatusResponse(BaseModel):
    thread_id: str
    status: BlogWorkflowStatus


class BlogWorkflowResponse(BaseModel):
    thread_id: str
    status: BlogWorkflowStatus
    draft: WriterResult | None


class ReviewDecision(str, Enum):
    APPROVE = 'Approve'
    REJECT = 'Reject'


class ReviewBlogRequest(BaseModel):
    decision: ReviewDecision
    feedback: str | None = None

    @model_validator(mode='after')
    def validate_decision_feedback(self):
        if self.decision == ReviewDecision.REJECT and (
            not self.feedback or not self.feedback.strip()
        ):
            raise ValueError("Feedback is required when rejecting a draft")
        return self
