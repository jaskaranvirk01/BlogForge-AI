from blogforge_ai.graph.states.global_state import GlobalState
from blogforge_ai.graph.graphs.research_graph import research_graph
from blogforge_ai.graph.graphs.analysis_graph import analysis_graph
from blogforge_ai.graph.graphs.fact_check_graph import fact_check_graph
from blogforge_ai.graph.graphs.writer_graph import writer_graph
from uuid import UUID


def research_workflow_node(state: GlobalState) -> dict:
    print(state['workflow_status'])
    initial_state = {
        'blog_request': state['blog_request'],
        'research_status': 'Researching'
    }
    research_ressult = research_graph.invoke(initial_state)
    return {
        'research_id': research_ressult['research_id'],
        'workflow_status': 'Researched'
    }


def analysis_workflow_node(state: GlobalState) -> dict:
    print(state['workflow_status'])
    initial_state = {
        'blog_request': state['blog_request'],
        'research_id': state['research_id'],
        'analysis_status': 'Started'
    }
    analysis_result = analysis_graph.invoke(initial_state)
    return {
        'analysis_id': analysis_result['analysis_id'],
        'workflow_status': 'Analysed'
    }


def fact_check_workflow_node(state: GlobalState) -> dict:
    print(state['workflow_status'])
    initial_state = {
        'research_id': state['research_id'],
        'fact_check_status': 'Started'
    }
    fact_check_result = fact_check_graph.invoke(initial_state)
    return {
        'fact_check_id': fact_check_result['fact_check_id'],
        'workflow_status': 'Facts Checked'
    }


def writer_workflow_node(state: GlobalState) -> dict:
    print(state['workflow_status'])
    initial_state = {
        'blog_request': state['blog_request'],
        'fact_check_id': state['fact_check_id'],
        'writer_status': 'Started'
    }
    writer_result = writer_graph.invoke(initial_state)
    return {
        'blog_draft': writer_result['blog_draft'],
        'draft_id': writer_result['draft_id'],
        'workflow_status': 'Drafted'
    }
