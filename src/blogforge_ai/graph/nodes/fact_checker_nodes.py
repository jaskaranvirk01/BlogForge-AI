from blogforge_ai.agents.fact_checker_agent import fact_checking_agent
from blogforge_ai.graph.states.fact_checking_state import FactCheckState
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


def retrieve_analysis_node(state: FactCheckState) -> dict:
    print(state['fact_check_status'])
    analysis = fact_checking_agent.retrieve_analysis(
        research_id=state['research_id'])
    return {
        'analysis': analysis,
        'fact_check_status': 'Analysis Retrieved'
    }


def retrieve_claims_node(state: FactCheckState) -> dict:
    print(state['fact_check_status'])
    claims = fact_checking_agent.retrieve_claims(
        analysis=state['analysis'])
    return {
        'retrieved_claims': claims,
        'fact_check_status': 'Claims Retrieved'
    }


def verify_claims_node(state: FactCheckState) -> dict:
    print(state['fact_check_status'])
    verifications = fact_checking_agent.verify_claims(
        claims=state['retrieved_claims'])
    result = fact_checking_agent.build_fact_check_result(
        analysis=state['analysis'], verification_result=verifications)
    return {
        'fact_check_result': result,
        'fact_check_status': 'Fact Checked'
    }


def save_fact_check_node(state: FactCheckState) -> dict:
    print(state['fact_check_status'])
    fact_check_id = knowledge_base_service.ingest_fact_check(
        analysis_id=state['analysis'].id, fact_check_result=state['fact_check_result'])
    return {
        'fact_check_id': fact_check_id,
        'fact_check_status': 'Fact Check Saved'
    }
