from fastapi import FastAPI
from blogforge_ai.api.schemas.blog import CreateBlogRequest
from blogforge_ai.services.graph_service import graph_service
from blogforge_ai.schemas.research_schemas import BlogRequest
app = FastAPI()


@app.post('/blogs')
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
    return graph_result
