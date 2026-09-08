from typing import TypedDict
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult, RetrievedClaims, AnalysisContent
from uuid import UUID


class FactCheckState(TypedDict):
    research_id: UUID
    analysis: AnalysisContent
    retrieved_claims: RetrievedClaims
    fact_check_result: FactCheckResult
    fact_check_status: str
    fact_check_id: UUID
