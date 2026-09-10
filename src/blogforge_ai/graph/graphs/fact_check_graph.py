from blogforge_ai.graph.states.fact_checking_state import FactCheckState
from blogforge_ai.graph.nodes.fact_checker_nodes import retrieve_analysis_node, retrieve_claims_node, verify_claims_node, resolve_evidence_node, prepare_result_node, save_fact_check_node
from langgraph.graph import StateGraph, START, END
from uuid import UUID
from rich import print

builder = StateGraph(FactCheckState)

builder.add_node('retrieve_analysis', retrieve_analysis_node)
builder.add_node('retrieve_claims', retrieve_claims_node)
builder.add_node('verify_claims', verify_claims_node)
builder.add_node('resolve_evidence', resolve_evidence_node)
builder.add_node('prepare_result', prepare_result_node)
builder.add_node('save_fact_check', save_fact_check_node)

builder.add_edge(START, 'retrieve_analysis')
builder.add_edge('retrieve_analysis', 'retrieve_claims')
builder.add_edge('retrieve_claims', 'verify_claims')
builder.add_edge('verify_claims', 'resolve_evidence')
builder.add_edge('resolve_evidence', 'prepare_result')
builder.add_edge('prepare_result', 'save_fact_check')
builder.add_edge('save_fact_check', END)


fact_check_graph = builder.compile()
