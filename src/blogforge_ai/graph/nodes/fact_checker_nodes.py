from blogforge_ai.agents.fact_checker_agent import fact_checking_agent
from blogforge_ai.graph.states.fact_checking_state import FactCheckState


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
    print(
        f"INPUT CLAIMS: {len(state['retrieved_claims'].claims)}"
    )

    print(
        f"OUTPUT VERIFICATIONS: {len(verifications.verifications)}"
    )
    result = fact_checking_agent.build_fact_check_result(
        analysis=state['analysis'], verification_result=verifications)
    return {
        'fact_check_result': result,
        'fact_check_status': 'Fact Checked'
    }
