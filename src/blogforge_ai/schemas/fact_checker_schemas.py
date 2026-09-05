from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from blogforge_ai.schemas.analysis_schemas import Evidence, Reference


class VerificationVerdict(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class FactCheckItem(BaseModel):
    claim: str
    explanation: str
    verdict: VerificationVerdict
    evidence: list[Evidence]


class FactCheckResult(BaseModel):
    title: str
    overview: str

    developments: list[FactCheckItem]
    limitations: list[FactCheckItem]
    future_scope: list[FactCheckItem]

    references: list[Reference]
