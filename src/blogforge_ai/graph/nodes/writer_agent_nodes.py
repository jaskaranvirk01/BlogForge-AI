from blogforge_ai.agents.writer_agent import writer_agent
from blogforge_ai.graph.states.writer_state import WriterState


def get_fact_check_node(state: WriterState) -> dict:
    print(state['writer_status'])
    fact_check = writer_agent.retrieve_fact_check(
        fact_check_id=state['fact_check_id'])
    return {
        'fact_check': fact_check,
        'writer_status': 'Fact Check Retrieved'
    }


def prepare_llm_input_node(state: WriterState) -> dict:
    print(state['writer_status'])
    llm_input = writer_agent.prepare_writer_input(
        fact_check=state['fact_check'], blog_request=state['blog_request'])

    return {
        'llm_input': llm_input,
        'writer_status': 'LLM Input prepared'
    }


def blog_writing_node(state: WriterState) -> dict:
    print(state['writer_status'])
    blog_draft = writer_agent.write_blog(llm_input=state['llm_input'])
    return {
        'blog_draft': blog_draft,
        'writer_status': 'Blog Drafted'
    }
