from pydantic import BaseModel
from enum import Enum
from blogforge_ai.schemas.analysis_schemas import Evidence, Reference
from blogforge_ai.schemas.analysis_schemas import AnalysisItem


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


class FactCheckResult(BaseModel):
    title: str
    overview: str
    claims: list[FactCheckItem]
    references: list[Reference]
