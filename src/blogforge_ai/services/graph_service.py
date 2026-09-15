from blogforge_ai.graph.graphs.global_graph import global_graph, checkpointer
from uuid import uuid4
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.schemas.global_graph_schema import GraphWorkflowResult, BlogWorkflowStatus
from langgraph.types import Command
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.workflow import WorkflowNotFoundError


class GraphService:

    def start_blog_workflow(self, blog_request: BlogRequest) -> GraphWorkflowResult:
        thread_id = str(uuid4())
        config = {
            'configurable': {
                'thread_id': thread_id
            }
        }

        initial_state = {
            'blog_request': blog_request,
            'workflow_status': 'Started'
        }

        result = global_graph.invoke(initial_state, config=config)

        if '__interrupt__' in result:
            status = BlogWorkflowStatus.WAITING_FOR_REVIEW
        else:
            status = BlogWorkflowStatus.COMPLETED

        return GraphWorkflowResult(
            thread_id=thread_id,
            status=status,
            draft=result.get('blog_draft')
        )

    def resume_blog_workflow(self, thread_id: str, decision: str, feedback: str | None):
        config = {
            'configurable': {
                'thread_id': thread_id
            }
        }
        checkpoint = checkpointer.get(config)

        if not checkpoint:
            raise WorkflowNotFoundError(
                message='Workflow with the provided Thread id not found',
                error_code=ErrorCodes.WORKFLOW_NOT_FOUND,
                workflow='review',
                node='resume_blog_workflow',
            )

        resume_value = {
            'decision': decision,
            'feedback': feedback
        }

        result = global_graph.invoke(
            Command(resume=resume_value),
            config=config
        )
        if '__interrupt__' in result:
            status = BlogWorkflowStatus.WAITING_FOR_REVIEW
        else:
            status = BlogWorkflowStatus.COMPLETED

        return GraphWorkflowResult(
            thread_id=thread_id,
            status=status,
            draft=result.get('blog_draft')
        )


graph_service = GraphService()
