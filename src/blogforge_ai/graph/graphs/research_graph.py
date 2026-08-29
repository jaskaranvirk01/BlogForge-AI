from langgraph.graph import StateGraph, START, END
from blogforge_ai.graph.nodes.research_nodes import plan_research_node, search_sources_node, source_selection_node, get_selected_sources_node, extract_selected_sources_node, create_research_result_node
from blogforge_ai.schemas.research_schemas import BlogRequest
from blogforge_ai.graph.states.research_state import ResearchState

builder = StateGraph(ResearchState)


builder.add_node('plan_research', plan_research_node)
builder.add_node('search_sources', search_sources_node)
builder.add_node('source_selection', source_selection_node)
builder.add_node('select_sources', get_selected_sources_node)
builder.add_node('extract_sources', extract_selected_sources_node)
builder.add_node('create_research_result', create_research_result_node)


builder.add_edge(START, 'plan_research')
builder.add_edge('plan_research', 'search_sources')
builder.add_edge('search_sources', 'source_selection')
builder.add_edge('source_selection', 'select_sources')
builder.add_edge('select_sources', 'extract_sources')
builder.add_edge('extract_sources', 'create_research_result')
builder.add_edge('create_research_result', END)


research_graph = builder.compile()


# blog_request = BlogRequest(
#     topic="Impact of Artificial Intelligence on Software Development",
#     target_audience="Software developers",
#     content_type="technical blog",
#     desired_length=1500,
#     tone="professional",
#     additional_instructions="Focus on practical benefits, risks, and current trends",
# )

# initial_state = {
#     'blog_request': blog_request,
#     'research_status': 'Researching'

# }


# result = graph.invoke(initial_state)


# print(result['research_plan'])
# print()
# print()
# print(result['search_output'])
# print()
# print()
# print(result['source_selection'])
# print()
# print()
# print(result['selected_sources'])
# print()
# print()
# print(result['extracted_sources'])
# print()
# print()
# print(result['research_result'])
# print()
# print()
# print(result['research_status'])
