from blogforge_ai.schemas.fact_checker_schemas import (
    AnalysisContent,
    FactCheckResult,
    RetrievedClaims,
    VerificationResult,
    LLMVerificationResult,
)
from blogforge_ai.graph.graphs.fact_check_graph import (
    fact_check_graph,
)
from blogforge_ai.exceptions.fact_checker import (
    FactCheckGenerationError,
    FactCheckRetrievalError,
    FactCheckPersistenceError,
)
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


def test_fact_check_workflow_success():
    research_id = uuid4()
    analysis_id = uuid4()
    fact_check_id = uuid4()

    analysis = MagicMock(spec=AnalysisContent)
    analysis.id = analysis_id

    retrieved_claims = MagicMock(spec=RetrievedClaims)
    llm_result = MagicMock(spec=LLMVerificationResult)
    evidence_map = {
        "E1": MagicMock(),
    }
    verification_result = MagicMock(spec=VerificationResult)
    fact_check_result = MagicMock(spec=FactCheckResult)

    with (
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.retrieve_analysis",
            return_value=analysis,
        ) as mock_retrieve_analysis,
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.retrieve_claims",
            return_value=retrieved_claims,
        ) as mock_retrieve_claims,
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.verify_claims",
            return_value=(llm_result, evidence_map),
        ) as mock_verify_claims,
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.resolve_evidence",
            return_value=verification_result,
        ) as mock_resolve_evidence,
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.build_fact_check_result",
            return_value=fact_check_result,
        ) as mock_build_fact_check_result,
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "knowledge_base_service.ingest_fact_check",
            return_value=fact_check_id,
        ) as mock_ingest_fact_check,
    ):
        initial_state = {
            "research_id": research_id,
            "fact_check_status": "Starting Fact Check",
        }

        result = fact_check_graph.invoke(initial_state)

    # Final state
    assert result["research_id"] == research_id
    assert result["analysis"] is analysis
    assert result["retrieved_claims"] is retrieved_claims
    assert result["llm_result"] is llm_result
    assert result["evidence_map"] == evidence_map
    assert result["verification_result"] is verification_result
    assert result["fact_check_result"] is fact_check_result
    assert result["fact_check_id"] == fact_check_id
    assert result["fact_check_status"] == "Fact Check Saved"

    # Node interactions
    mock_retrieve_analysis.assert_called_once_with(
        research_id=research_id,
    )

    mock_retrieve_claims.assert_called_once_with(
        analysis=analysis,
    )

    mock_verify_claims.assert_called_once_with(
        claims=retrieved_claims,
    )

    mock_resolve_evidence.assert_called_once_with(
        verification_result=llm_result,
        evidence_map=evidence_map,
    )

    mock_build_fact_check_result.assert_called_once_with(
        analysis=analysis,
        verification_result=verification_result,
    )

    mock_ingest_fact_check.assert_called_once_with(
        analysis_id=analysis_id,
        fact_check_result=fact_check_result,
    )


def test_fact_check_workflow_analysis_retrieval_failure():
    research_id = uuid4()

    retrieval_error = FactCheckRetrievalError(
        message="Analysis Retrieval Failed",
        error_code="FACT_CHECK_RETRIEVAL_FAILED",
        workflow="fact_check",
        node="retrieve_analysis",
        retryable=False,
        cause=Exception("simulated retrieval failure"),
    )

    with patch(
        "blogforge_ai.graph.nodes.fact_checker_nodes."
        "fact_checking_agent.retrieve_analysis",
        side_effect=retrieval_error,
    ):
        initial_state = {
            "research_id": research_id,
            "fact_check_status": "Starting Fact Check",
        }

        with pytest.raises(FactCheckRetrievalError) as exc_info:
            fact_check_graph.invoke(initial_state)

    assert exc_info.value is retrieval_error


def test_fact_check_workflow_generation_failure():
    research_id = uuid4()

    analysis = MagicMock(spec=AnalysisContent)

    generation_error = FactCheckGenerationError(
        message="Fact Check Generation Failed",
        error_code="FACT_CHECK_GENERATION_FAILED",
        workflow="fact_check",
        node="verify_claims",
        retryable=False,
        cause=Exception("simulated LLM failure"),
    )

    with (
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.retrieve_analysis",
            return_value=analysis,
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.retrieve_claims",
            return_value=MagicMock(spec=RetrievedClaims),
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.verify_claims",
            side_effect=generation_error,
        ),
    ):
        initial_state = {
            "research_id": research_id,
            "fact_check_status": "Starting Fact Check",
        }

        with pytest.raises(FactCheckGenerationError) as exc_info:
            fact_check_graph.invoke(initial_state)

    assert exc_info.value is generation_error


def test_fact_check_workflow_persistence_failure():
    research_id = uuid4()
    analysis_id = uuid4()

    analysis = MagicMock(spec=AnalysisContent)
    analysis.id = analysis_id

    persistence_error = FactCheckPersistenceError(
        message="Fact Check Persistence Failed",
        error_code="FACT_CHECK_PERSISTENCE_FAILED",
        workflow="fact_check",
        node="ingest_fact_check",
        retryable=False,
        cause=Exception("simulated persistence failure"),
    )

    with (
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.retrieve_analysis",
            return_value=analysis,
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.retrieve_claims",
            return_value=MagicMock(spec=RetrievedClaims),
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.verify_claims",
            return_value=(
                MagicMock(spec=LLMVerificationResult),
                {},
            ),
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.resolve_evidence",
            return_value=MagicMock(spec=VerificationResult),
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "fact_checking_agent.build_fact_check_result",
            return_value=MagicMock(spec=FactCheckResult),
        ),
        patch(
            "blogforge_ai.graph.nodes.fact_checker_nodes."
            "knowledge_base_service.ingest_fact_check",
            side_effect=persistence_error,
        ),
    ):
        initial_state = {
            "research_id": research_id,
            "fact_check_status": "Starting Fact Check",
        }

        with pytest.raises(FactCheckPersistenceError) as exc_info:
            fact_check_graph.invoke(initial_state)

    assert exc_info.value is persistence_error
