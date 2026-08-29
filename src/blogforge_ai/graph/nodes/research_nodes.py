from blogforge_ai.agents.research_agent import research_agent, ResearchResult
from blogforge_ai.graph.states.research_state import ResearchState


def plan_research_node(state: ResearchState) -> dict:
    response = research_agent.plan_research(blog_request=state['blog_request'])
    print('Research Planned')
    return {
        'research_plan': response,
        'research_status': 'Research Planned'
    }


def search_sources_node(state: ResearchState) -> dict:
    response = research_agent.search_sources(
        research_plan=state['research_plan'], max_results=3)
    print('Sources Searched')
    return {
        'search_output': response,
        'research_status': 'Sources Searched'
    }


def source_selection_node(state: ResearchState) -> dict:
    response = research_agent.select_sources(
        research_plan=state['research_plan'], search_output=state['search_output'])
    print('Sources Selected')
    return {
        'source_selection': response,
        'research_status': 'Sources Selected'
    }


def get_selected_sources_node(state: ResearchState) -> dict:
    response = research_agent.get_selected_sources(
        source_selection=state['source_selection'], search_output=state['search_output'])
    print('Selected Sources Confirmed')
    return {
        'selected_sources': response,
        'research_status': 'Selected Sources Confirmed'
    }


def extract_selected_sources_node(state: ResearchState) -> dict:
    response = research_agent.extract_selected_sources(
        selected_sources=state['selected_sources'])
    print('Source Data Extracted')
    return {
        'extracted_sources': response,
        'research_status': 'Source Data Extracted'
    }


def create_research_result_node(state: ResearchState) -> dict:
    research_result = ResearchResult(
        research_plan=state['research_plan'], selected_sources=state['extracted_sources'])
    print('Completed')
    return {
        'research_result': research_result,
        'research_status': 'Completed'
    }
