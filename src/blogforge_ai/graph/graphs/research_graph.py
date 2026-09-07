from langgraph.graph import StateGraph, START, END
from blogforge_ai.graph.nodes.research_nodes import plan_research_node, search_sources_node, source_selection_node, get_selected_sources_node, extract_selected_sources_node, create_research_result_node, save_research_node
from blogforge_ai.graph.states.research_state import ResearchState

builder = StateGraph(ResearchState)


builder.add_node('plan_research', plan_research_node)
builder.add_node('search_sources', search_sources_node)
builder.add_node('source_selection', source_selection_node)
builder.add_node('select_sources', get_selected_sources_node)
builder.add_node('extract_sources', extract_selected_sources_node)
builder.add_node('create_research_result', create_research_result_node)
builder.add_node('save_research', save_research_node)


builder.add_edge(START, 'plan_research')
builder.add_edge('plan_research', 'search_sources')
builder.add_edge('search_sources', 'source_selection')
builder.add_edge('source_selection', 'select_sources')
builder.add_edge('select_sources', 'extract_sources')
builder.add_edge('extract_sources', 'create_research_result')
builder.add_edge('create_research_result', 'save_research')
builder.add_edge('save_research', END)


research_graph = builder.compile()
