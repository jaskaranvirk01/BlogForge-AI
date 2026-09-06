from blogforge_ai.graph.states.fact_checking_state import FactCheckState
from blogforge_ai.graph.nodes.fact_checker_nodes import retrieve_analysis_node, retrieve_claims_node, verify_claims_node
from langgraph.graph import StateGraph, START, END
import uuid
from rich import print
builder = StateGraph(FactCheckState)

builder.add_node('retrieve_analysis', retrieve_analysis_node)
builder.add_node('retrieve_claims', retrieve_claims_node)
builder.add_node('verify_claims', verify_claims_node)

builder.add_edge(START, 'retrieve_analysis')
builder.add_edge('retrieve_analysis', 'retrieve_claims')
builder.add_edge('retrieve_claims', 'verify_claims')
builder.add_edge('verify_claims', END)


fact_check_graph = builder.compile()

research_id = 'b09b3a8b-de07-41d6-8a64-56d1672eb784'
initial_state = {
    'research_id': uuid.UUID(research_id),
    'fact_check_status': 'Started'
}


res = fact_check_graph.invoke(initial_state)


print(res)
