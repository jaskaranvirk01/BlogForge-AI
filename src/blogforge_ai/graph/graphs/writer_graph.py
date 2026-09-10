from blogforge_ai.graph.nodes.writer_agent_nodes import get_fact_check_node, prepare_llm_input_node, blog_writing_node, create_writer_result_node, save_blog_draft_node
from blogforge_ai.graph.states.writer_state import WriterState, BlogRequest
from langgraph.graph import StateGraph, START, END
from uuid import UUID

builder = StateGraph(WriterState)

builder.add_node('get_fact_check', get_fact_check_node)
builder.add_node('prepare_input', prepare_llm_input_node)
builder.add_node('blog_writing', blog_writing_node)
builder.add_node('create_writer_result', create_writer_result_node)
builder.add_node('save_draft', save_blog_draft_node)


builder.add_edge(START, 'get_fact_check')
builder.add_edge('get_fact_check', 'prepare_input')
builder.add_edge('prepare_input', 'blog_writing')
builder.add_edge('blog_writing', 'create_writer_result')
builder.add_edge('create_writer_result', 'save_draft')
builder.add_edge('save_draft', END)


writer_graph = builder.compile()

blog_request = BlogRequest(
    topic="Iphone 17",
    target_audience="Teenagers",
    content_type="Brief summary",
    desired_length=150,
    tone="professional",
    additional_instructions="Focus on a brief introduction type blog",
)
