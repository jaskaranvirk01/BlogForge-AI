from blogforge_ai.graph.nodes.writer_agent_nodes import get_fact_check_node, prepare_llm_input_node, blog_writing_node, save_blog_draft_node
from blogforge_ai.graph.states.writer_state import WriterState, BlogRequest
from langgraph.graph import StateGraph, START, END


builder = StateGraph(WriterState)

builder.add_node('get_fact_check', get_fact_check_node)
builder.add_node('prepare_input', prepare_llm_input_node)
builder.add_node('blog_writing', blog_writing_node)
builder.add_node('save_draft', save_blog_draft_node)


builder.add_edge(START, 'get_fact_check')
builder.add_edge('get_fact_check', 'prepare_input')
builder.add_edge('prepare_input', 'blog_writing')
builder.add_edge('blog_writing', 'save_draft')
builder.add_edge('save_draft', END)


writer_graph = builder.compile()
