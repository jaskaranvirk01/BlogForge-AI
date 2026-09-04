from blogforge_ai.agents.analysis_agent import analysis_agent
from blogforge_ai.graph.states.analysis_state import AnalysisState
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


def query_planning_node(state: AnalysisState) -> dict:
    print(state['analysis_status'])
    queries = analysis_agent.plan_retrieval_queries(
        blog_request=state['blog_request'])
    return {
        'queries': queries,
        'analysis_status': 'Queries Generated'
    }


def chunk_retrieval_node(state: AnalysisState) -> dict:
    print(state['analysis_status'])
    chunks = analysis_agent.retrieve_analysis_chunks(
        analysis_queries=state['queries'], research_id=state['research_id'])
    return {
        'retrieved_chunks': chunks,
        'analysis_status': 'Chunks Retrieved'
    }


def chunk_ranking_node(state: AnalysisState) -> dict:
    print(state['analysis_status'])
    ranked_chunks = analysis_agent.rank_and_deduplicate_chunks(
        analysis_chunks=state['retrieved_chunks'])
    return {
        'ranked_chunks': ranked_chunks,
        'analysis_status': 'Chunks Ranked'
    }


def context_building_node(state: AnalysisState) -> dict:
    print(state['analysis_status'])
    context = analysis_agent.build_analysis_context(
        chunks=state['ranked_chunks'])
    return {
        'analysis_context': context,
        'analysis_status': 'Context Generated'
    }


def generate_analysis_node(state: AnalysisState) -> dict:
    print(state['analysis_status'])
    analysis = analysis_agent.generate_analysis(
        blog_request=state['blog_request'], analysis_context=state['analysis_context'])
    return {
        'generated_analysis': analysis,
        'analysis_status': 'Analysis Generated'
    }


def save_analysis_node(state: AnalysisState) -> dict:
    print(state['analysis_status'])
    analysis_id = knowledge_base_service.ingest_analysis(
        research_id=state['research_id'], analysis_result=state['generated_analysis'])
    return {
        'analysis_id': analysis_id,
        'analysis_status': 'Analysis Saved'
    }
