from langgraph.graph import StateGraph, START, END
from blogforge_ai.graph.nodes.analysis_nodes import query_planning_node, chunk_ranking_node, chunk_retrieval_node, generate_analysis_node, context_building_node, create_analysis_result_node, save_analysis_node
from blogforge_ai.graph.states.analysis_state import AnalysisState
from blogforge_ai.schemas.research_schemas import BlogRequest
from uuid import UUID
builder = StateGraph(AnalysisState)

builder.add_node('query_planning', query_planning_node)
builder.add_node('chunk_retrieval', chunk_retrieval_node)
builder.add_node('chunk_ranking', chunk_ranking_node)
builder.add_node('build_context', context_building_node)
builder.add_node('generate_analysis', generate_analysis_node)
builder.add_node('analysis_object_creation', create_analysis_result_node)
builder.add_node('save_analysis', save_analysis_node)


builder.add_edge(START, 'query_planning')
builder.add_edge('query_planning', 'chunk_retrieval')
builder.add_edge('chunk_retrieval', 'chunk_ranking')
builder.add_edge('chunk_ranking', 'build_context')
builder.add_edge('build_context', 'generate_analysis')
builder.add_edge('generate_analysis', 'analysis_object_creation')
builder.add_edge('analysis_object_creation', 'save_analysis')
builder.add_edge('save_analysis', END)


analysis_graph = builder.compile()


# research_id = '39f9a357-8d53-4862-9bce-73f35ac8108e'


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
#     'research_id': UUID(research_id),
#     'analysis_status': 'started'
# }

# res = analysis_graph.invoke(initial_state)

# print(res)
