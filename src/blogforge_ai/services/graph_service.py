from blogforge_ai.graph.graphs.global_graph import global_graph
from uuid import uuid4
from blogforge_ai.schemas.research_schemas import BlogRequest


class GraphService:

    def start_blog_workflow(self, blog_request: BlogRequest):
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
        print(result)
        return result


graph_service = GraphService()
