from typing import TypedDict
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult, Evidence, RetrievedClaims, AnalysisContent, LLMVerificationResult, VerificationResult
from uuid import UUID


class FactCheckState(TypedDict):
    research_id: UUID
    analysis: AnalysisContent
    retrieved_claims: RetrievedClaims
    llm_result: LLMVerificationResult
    evidence_map: dict[str, Evidence]
    verification_result: VerificationResult
    fact_check_result: FactCheckResult
    fact_check_status: str
    fact_check_id: UUID
