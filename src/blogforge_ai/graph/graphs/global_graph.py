from blogforge_ai.graph.states.global_state import GlobalState, BlogRequest
from blogforge_ai.graph.nodes.global_graph_nodes import research_workflow_node, analysis_workflow_node, fact_check_workflow_node, writer_workflow_node
from langgraph.graph import StateGraph, START, END
from rich import print

builder = StateGraph(GlobalState)

builder.add_node('research_node', research_workflow_node)
builder.add_node('analysis_node', analysis_workflow_node)
builder.add_node('fact_check_node', fact_check_workflow_node)
builder.add_node('writer_node', writer_workflow_node)


builder.add_edge(START, 'research_node')
builder.add_edge('research_node', 'analysis_node')
builder.add_edge('analysis_node', 'fact_check_node')
builder.add_edge('fact_check_node', 'writer_node')
builder.add_edge('writer_node', END)

global_graph = builder.compile()


blog_request = BlogRequest(
    topic="BMW M5 Competition",
    target_audience="Car enthusiasts",
    content_type="Informative blog",
    desired_length=1500,
    tone="professional",
    additional_instructions="Focus on providing details outlook of the car",
)

initial_state = {
    'blog_request': blog_request,
    'workflow_status': 'Started'
}

res = global_graph.invoke(initial_state)

print(res)
