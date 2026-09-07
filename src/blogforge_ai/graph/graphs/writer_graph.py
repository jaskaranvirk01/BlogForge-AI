from blogforge_ai.graph.nodes.writer_agent_nodes import get_fact_check_node, prepare_llm_input_node, blog_writing_node
from blogforge_ai.graph.states.writer_state import WriterState, BlogRequest
from uuid import UUID
from langgraph.graph import StateGraph, START, END


builder = StateGraph(WriterState)

builder.add_node('get_fact_check', get_fact_check_node)
builder.add_node('prepare_input', prepare_llm_input_node)
builder.add_node('blog_writing', blog_writing_node)


builder.add_edge(START, 'get_fact_check')
builder.add_edge('get_fact_check', 'prepare_input')
builder.add_edge('prepare_input', 'blog_writing')
builder.add_edge('blog_writing', END)


writer_graph = builder.compile()


blog_request = BlogRequest(
    topic="Impact of Artificial Intelligence on Software Development",
    target_audience="Software developers",
    content_type="technical blog",
    desired_length=1500,
    tone="professional",
    additional_instructions="Focus on practical benefits, risks, and current trends",
)

fact_check_id = 'd10ab30f-30fd-4010-9f50-c8f1271b363d'

initial_state = WriterState(
    blog_request=blog_request,
    fact_check_id=UUID(fact_check_id),
    writer_status='Started'
)


res = writer_graph.invoke(initial_state)
print(res)
