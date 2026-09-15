
from blogforge_ai.api.schemas.error import ErrorResponse
from fastapi import FastAPI
from blogforge_ai.api.schemas.blog import CreateBlogRequest, BlogWorkflowResponse, ReviewBlogRequest
from blogforge_ai.services.graph_service import graph_service
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.exceptions.handler import register_exception_handlers
app = FastAPI()

register_exception_handlers(app)


@app.post('/blogs', response_model=BlogWorkflowResponse, responses={
    500: {"model": ErrorResponse},
})
def create_blog(create_blog_request: CreateBlogRequest):
    blog_request = BlogRequest(
        topic=create_blog_request.topic,
        target_audience=create_blog_request.target_audience,
        content_type=create_blog_request.content_type,
        desired_length=create_blog_request.desired_length,
        tone=create_blog_request.tone,
        additional_instructions=create_blog_request.additional_instructions
    )

    graph_result = graph_service.start_blog_workflow(blog_request=blog_request)
    return BlogWorkflowResponse(
        thread_id=graph_result.thread_id,
        status=graph_result.status,
        draft=graph_result.draft
    )


@app.post('/blogs/{thread_id}/review', response_model=BlogWorkflowResponse,
          responses={
              404: {"model": ErrorResponse},
              500: {"model": ErrorResponse},
          },)
def review_blog(thread_id: str, request: ReviewBlogRequest):

    graph_result = graph_service.resume_blog_workflow(
        thread_id=thread_id, decision=request.decision, feedback=request.feedback)
    return BlogWorkflowResponse(
        thread_id=graph_result.thread_id,
        status=graph_result.status,
        draft=graph_result.draft
    )
