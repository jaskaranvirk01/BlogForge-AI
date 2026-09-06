from typing import TypedDict
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult, RetrievedClaims
from blogforge_ai.database.models.analysis import Analysis
from uuid import UUID


class FactCheckState(TypedDict):
    research_id: UUID
    analysis: Analysis
    retrieved_claims: RetrievedClaims
    fact_check_result: FactCheckResult
    fact_check_status: str
    fact_check_id: UUID
