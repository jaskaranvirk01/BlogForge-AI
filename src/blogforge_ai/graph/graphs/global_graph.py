from blogforge_ai.graph.states.global_state import GlobalState, BlogRequest
from blogforge_ai.graph.nodes.global_graph_nodes import research_workflow_node, analysis_workflow_node, fact_check_workflow_node, writer_workflow_node, human_review_node
from langgraph.graph import StateGraph, START, END
from rich import print
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from uuid import UUID
checkpointer = InMemorySaver()


def router(state: GlobalState):

    return state['human_decision']


builder = StateGraph(GlobalState)

builder.add_node('research_node', research_workflow_node)
builder.add_node('analysis_node', analysis_workflow_node)
builder.add_node('fact_check_node', fact_check_workflow_node)
builder.add_node('writer_node', writer_workflow_node)
builder.add_node('human_review_node', human_review_node)


builder.add_edge(START, 'research_node')
builder.add_edge('research_node', 'analysis_node')
builder.add_edge('analysis_node', 'fact_check_node')
builder.add_edge('fact_check_node', 'writer_node')
builder.add_edge('writer_node', 'human_review_node')
builder.add_conditional_edges('human_review_node', router, {
    'Approve': END,
    'Reject': 'writer_node'
})


global_graph = builder.compile(checkpointer=checkpointer)


# blog_request = BlogRequest(
#     topic="Iphone 17",
#     target_audience="Teenagers",
#     content_type="Brief summary",
#     desired_length=150,
#     tone="professional",
#     additional_instructions="Focus on a brief introduction type blog",
# )
# initial_state = {
#     'blog_request': blog_request,
#     'workflow_status': 'Started'
# }


# config = {
#     'configurable': {
#         'thread_id': 'blog-review-001'
#     }
# }


# res = global_graph.invoke(initial_state, config=config)

# while True:

#     decision = input("Approve or Reject? ").strip()

#     feedback = None

#     if decision.lower() == "reject":
#         feedback = input("Enter Your Feedback: ").strip()

#     resume_command = Command(
#         resume={
#             "decision": decision.capitalize(),
#             "feedback": feedback
#         }
#     )

#     result = global_graph.invoke(
#         resume_command,
#         config=config
#     )

#     if decision.lower() == "approve":
#         print(result)
#         break

#     # If rejected, the graph runs Writer again
#     # and interrupts again at human_review_node.
