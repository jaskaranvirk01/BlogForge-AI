from pydantic import BaseModel, ConfigDict
from enum import Enum
from blogforge_ai.schemas.analysis_schemas import Evidence, Reference
from blogforge_ai.schemas.analysis_schemas import AnalysisItem
from uuid import UUID


class VerificationVerdict(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class FactCheckItem(BaseModel):
    claim: str
    explanation: str
    verdict: VerificationVerdict
    evidence: list[Evidence]


class RetrievedClaims(BaseModel):
    claims:  list[AnalysisItem]


class VerificationItem(BaseModel):
    claim: str
    explanation: str
    verdict: VerificationVerdict
    evidence: list[Evidence]


class VerificationResult(BaseModel):
    verifications: list[VerificationItem]


class AnalysisContent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    research_id: UUID
    title: str
    overview: str
    developments: list[AnalysisItem]
    limitations: list[AnalysisItem]
    future_scope: list[AnalysisItem]
    references: list[Reference]


class FactCheckResult(BaseModel):
    title: str
    overview: str
    claims: list[FactCheckItem]
    references: list[Reference]
