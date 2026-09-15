from blogforge_ai.graph.states.global_state import GlobalState
from blogforge_ai.graph.graphs.research_graph import research_graph
from blogforge_ai.graph.graphs.analysis_graph import analysis_graph
from blogforge_ai.graph.graphs.fact_check_graph import fact_check_graph
from blogforge_ai.graph.graphs.writer_graph import writer_graph
from blogforge_ai.schemas.global_graph_schema import BlogWorkflowStatus
from langgraph.types import interrupt


def research_workflow_node(state: GlobalState) -> dict:
    initial_state = {
        'blog_request': state['blog_request'],
        'research_status': 'Researching'
    }
    research_ressult = research_graph.invoke(initial_state)
    return {
        'research_id': research_ressult['research_id'],
    }


def analysis_workflow_node(state: GlobalState) -> dict:
    initial_state = {
        'blog_request': state['blog_request'],
        'research_id': state['research_id'],
        'analysis_status': 'Started'
    }
    analysis_result = analysis_graph.invoke(initial_state)
    return {
        'analysis_id': analysis_result['analysis_id'],

    }


def fact_check_workflow_node(state: GlobalState) -> dict:
    initial_state = {
        'research_id': state['research_id'],
        'fact_check_status': 'Started'
    }
    fact_check_result = fact_check_graph.invoke(initial_state)
    return {
        'fact_check_id': fact_check_result['fact_check_id'],

    }


def writer_workflow_node(state: GlobalState) -> dict:
    initial_state = {
        'blog_request': state['blog_request'],
        'fact_check_id': state['fact_check_id'],
        'human_feedback': state.get('human_feedback'),
        'writer_status': 'Started'
    }
    writer_result = writer_graph.invoke(initial_state)
    return {
        'blog_draft': writer_result['writer_result'],
        'draft_id': writer_result['draft_id'],

    }


def human_review_node(state: GlobalState) -> dict:
    review_request = interrupt({
        'blog_draft': state['blog_draft'],
        'message': 'Review the generated blog draft',
        'required': {
            'decision': 'Approve | Reject',
            'feedback': 'Required only if Reject',
        },
    })

    decision = review_request['decision']
    feedback = review_request.get('feedback', '')

    if decision not in ('Approve', 'Reject'):
        raise ValueError('Decision must be "Approve" or "Reject"')

    if decision == 'Reject' and not feedback.strip():
        raise ValueError('Feedback is required when rejecting the draft')

    return {
        'human_decision': decision,
        'human_feedback': feedback

    }


def set_research_status_node(state: GlobalState) -> dict:
    return {
        'workflow_status': BlogWorkflowStatus.RESEARCHING
    }


def set_analysis_status_node(state: GlobalState) -> dict:
    return {
        'workflow_status': BlogWorkflowStatus.ANALYZING
    }


def set_fact_check_status_node(state: GlobalState) -> dict:
    return {
        'workflow_status': BlogWorkflowStatus.FACT_CHECKING
    }


def set_writing_status_node(state: GlobalState) -> dict:
    return {
        'workflow_status': BlogWorkflowStatus.WRITING
    }


def set_review_status_node(state: GlobalState) -> dict:
    return {
        "workflow_status": BlogWorkflowStatus.WAITING_FOR_REVIEW
    }


def set_completed_status_node(state: GlobalState) -> dict:
    return {
        "workflow_status": BlogWorkflowStatus.COMPLETED
    }
