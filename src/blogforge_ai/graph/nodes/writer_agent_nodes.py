from blogforge_ai.agents.writer_agent import writer_agent
from blogforge_ai.graph.states.writer_state import WriterState
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


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
    llm_input, evidence_map, reference_map = writer_agent.prepare_writer_input(
        fact_check=state['fact_check'], blog_request=state['blog_request'], human_feedback=state['human_feedback'])

    return {
        'llm_input': llm_input,
        'evidence_map': evidence_map,
        'reference_map': reference_map,
        'writer_status': 'LLM Input prepared'
    }


def blog_writing_node(state: WriterState) -> dict:
    print(state['writer_status'])
    llm_result = writer_agent.write_blog(llm_input=state['llm_input'])
    return {
        'llm_result': llm_result,
        'writer_status': 'Blog Drafted'
    }


def create_writer_result_node(state: WriterState) -> dict:
    print(state['writer_status'])
    writer_result = writer_agent.create_writer_result(
        llm_result=state['llm_result'], reference_map=state['reference_map'])
    return {
        'writer_result': writer_result,
        'writer_status': "Writer Result created"
    }


def save_blog_draft_node(state: WriterState) -> dict:
    print(state['writer_status'])
    draft_id = knowledge_base_service.ingest_blog_draft(
        fact_check_id=state['fact_check_id'], writer_result=state['writer_result'])
    return {
        'draft_id': draft_id,
        'writer_status': 'Blog Draft Saved'
    }
