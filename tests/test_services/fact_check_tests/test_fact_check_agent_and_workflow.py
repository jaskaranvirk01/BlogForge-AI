from unittest.mock import MagicMock, patch
import pytest
from uuid import uuid4
from blogforge_ai.agents.fact_checker_agent import fact_checking_agent
from blogforge_ai.exceptions.fact_checker import FactCheckGenerationError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.schemas.analysis_schemas import Evidence


def test_verify_claims_generation_failure():
    claims = MagicMock()
    claims.claims = []

    llm_error = Exception('simulated generation error')

    mock_fact_checking_llm = MagicMock()
    mock_fact_checking_llm.invoke.side_effect = llm_error

    fact_checking_agent.fact_checking_llm = mock_fact_checking_llm

    with pytest.raises(FactCheckGenerationError) as exc_info:
        fact_checking_agent.verify_claims(claims=claims)

    error = exc_info.value

    assert error.error_code == ErrorCodes.FACT_CHECK_GENERATION_FAILED
    assert error.workflow == "fact_check"
    assert error.node == "verify_claims"
    assert error.retryable is False
    assert error.cause is llm_error

    mock_fact_checking_llm.invoke.assert_called_once()


def test_verify_claims_count_mismatch():
    claims = MagicMock()

    claim_1 = MagicMock()
    claim_1.claim = "Claim 1"
    claim_1.explanation = "Explanation 1"
    claim_1.evidence = []

    claim_2 = MagicMock()
    claim_2.claim = "Claim 2"
    claim_2.explanation = "Explanation 2"
    claim_2.evidence = []

    claims.claims = [claim_1, claim_2]

    verification_results = MagicMock()
    verification_results.verifications = [MagicMock()]

    mock_fact_checking_llm = MagicMock()
    mock_fact_checking_llm.invoke.return_value = verification_results

    fact_checking_agent.fact_checking_llm = mock_fact_checking_llm

    with pytest.raises(
        ValueError,
        match="returned 1 verifications for 2 claims",
    ):
        fact_checking_agent.verify_claims(
            claims=claims
        )

    mock_fact_checking_llm.invoke.assert_called_once()


def test_verify_claims_success():
    chunk_id = uuid4()
    source_id = uuid4()

    analysis_item = MagicMock()
    analysis_item.claim = "AI improves developer productivity."
    analysis_item.explanation = "AI tools can automate repetitive coding tasks."
    analysis_item.evidence = [
        MagicMock(chunk_id=chunk_id)
    ]

    claims = MagicMock()
    claims.claims = [analysis_item]

    chunk = MagicMock()
    chunk.id = chunk_id
    chunk.research_source_id = source_id
    chunk.content = "AI coding assistants can automate repetitive development tasks."

    verification_results = MagicMock()
    verification_results.verifications = [MagicMock()]

    with (
        patch.object(
            fact_checking_agent,
            "retrieve_evidence",
            return_value=[chunk],
        ) as mock_retrieve_evidence,
        patch.object(
            fact_checking_agent,
            "fact_checking_llm",
        ) as mock_fact_checking_llm,
    ):
        mock_fact_checking_llm.invoke.return_value = verification_results

        result, evidence_map = fact_checking_agent.verify_claims(
            claims=claims
        )

    assert result is verification_results

    assert "E1" in evidence_map
    assert evidence_map["E1"].source_id == source_id
    assert evidence_map["E1"].chunk_id == chunk_id

    mock_retrieve_evidence.assert_called_once_with(
        analysis_item=analysis_item
    )

    mock_fact_checking_llm.invoke.assert_called_once()


def test_resolve_evidence_success():
    chunk_id = uuid4()
    source_id = uuid4()

    verification = MagicMock()
    verification.claim = "AI improves productivity."
    verification.explanation = "AI tools automate repetitive tasks."
    verification.verdict = "supported"

    verification.evidence = [
        MagicMock(evidence_id="E1")
    ]

    verification_result = MagicMock()
    verification_result.verifications = [verification]

    evidence_map = {
        "E1": Evidence(
            chunk_id=chunk_id,
            source_id=source_id,
        )
    }

    result = fact_checking_agent.resolve_evidence(
        verification_result=verification_result,
        evidence_map=evidence_map,
    )

    assert len(result.verifications) == 1

    resolved_verification = result.verifications[0]

    assert resolved_verification.claim == verification.claim
    assert resolved_verification.explanation == verification.explanation
    assert resolved_verification.verdict == verification.verdict

    assert len(resolved_verification.evidence) == 1

    resolved_evidence = resolved_verification.evidence[0]

    assert resolved_evidence.chunk_id == chunk_id
    assert resolved_evidence.source_id == source_id


def test_resolve_evidence_unknown_evidence_id():
    verification = MagicMock()
    verification.claim = "AI improves productivity."
    verification.explanation = "AI tools automate repetitive tasks."
    verification.verdict = "supported"
    verification.evidence = [
        MagicMock(evidence_id="E999")
    ]

    verification_result = MagicMock()
    verification_result.verifications = [verification]

    evidence_map = {
        "E1": Evidence(
            chunk_id=uuid4(),
            source_id=uuid4(),
        )
    }

    with pytest.raises(KeyError):
        fact_checking_agent.resolve_evidence(
            verification_result=verification_result,
            evidence_map=evidence_map,
        )
