from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from blogforge_ai.agents.analysis_agent import analysis_agent
from blogforge_ai.exceptions.analysis import (
    AnalysisGenerationError,
    AnalysisPersistenceError,
)
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.graph.graphs.analysis_graph import analysis_graph
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


def test_analysis_workflow_success():
    # Arrange

    blog_request = MagicMock()
    research_id = uuid4()
    analysis_id = uuid4()

    mock_queries = MagicMock()
    mock_retrieved_chunks = [MagicMock()]
    mock_ranked_chunks = [MagicMock()]

    mock_context = "mock analysis context"
    mock_evidence_map = {"E1": MagicMock()}
    mock_source_map = {"S1": MagicMock()}

    mock_llm_result = MagicMock()
    mock_analysis_result = MagicMock()

    with (
        patch.object(
            analysis_agent,
            "plan_retrieval_queries",
            return_value=mock_queries,
        ) as mock_plan_queries,
        patch.object(
            analysis_agent,
            "retrieve_analysis_chunks",
            return_value=mock_retrieved_chunks,
        ) as mock_retrieve_chunks,
        patch.object(
            analysis_agent,
            "rank_and_deduplicate_chunks",
            return_value=mock_ranked_chunks,
        ) as mock_rank_chunks,
        patch.object(
            analysis_agent,
            "build_analysis_context",
            return_value=(
                mock_context,
                mock_evidence_map,
                mock_source_map,
            ),
        ) as mock_build_context,
        patch.object(
            analysis_agent,
            "generate_analysis",
            return_value=mock_llm_result,
        ) as mock_generate_analysis,
        patch.object(
            analysis_agent,
            "prepare_analysis_result",
            return_value=mock_analysis_result,
        ) as mock_prepare_result,
        patch.object(
            knowledge_base_service,
            "ingest_analysis",
            return_value=analysis_id,
        ) as mock_ingest_analysis,
    ):
        initial_state = {
            "blog_request": blog_request,
            "research_id": research_id,
            "analysis_status": "Started",
        }

        # Act

        result = analysis_graph.invoke(initial_state)

    # Assert

    assert result["queries"] is mock_queries
    assert result["retrieved_chunks"] is mock_retrieved_chunks
    assert result["ranked_chunks"] is mock_ranked_chunks

    assert result["analysis_context"] == mock_context
    assert result["evidence_map"] is mock_evidence_map
    assert result["source_map"] is mock_source_map

    assert result["llm_result"] is mock_llm_result
    assert result["analysis_result"] is mock_analysis_result

    assert result["analysis_id"] == analysis_id
    assert result["analysis_status"] == "Analysis Saved"

    mock_plan_queries.assert_called_once_with(
        blog_request=blog_request
    )

    mock_retrieve_chunks.assert_called_once_with(
        analysis_queries=mock_queries,
        research_id=research_id,
    )

    mock_rank_chunks.assert_called_once_with(
        analysis_chunks=mock_retrieved_chunks,
    )

    mock_build_context.assert_called_once_with(
        chunks=mock_ranked_chunks,
    )

    mock_generate_analysis.assert_called_once_with(
        blog_request=blog_request,
        analysis_context=mock_context,
    )

    mock_prepare_result.assert_called_once_with(
        llm_result=mock_llm_result,
        evidence_map=mock_evidence_map,
        source_map=mock_source_map,
    )

    mock_ingest_analysis.assert_called_once_with(
        research_id=research_id,
        analysis_result=mock_analysis_result,
    )


def test_analysis_workflow_llm_generation_failure():
    # Arrange

    blog_request = MagicMock()
    research_id = uuid4()

    llm_error = AnalysisGenerationError(
        message="Analysis Generation Failed",
        error_code=ErrorCodes.ANALYSIS_GENERATION_FAILED,
        workflow="analysis",
        node="generate_analysis",
        retryable=False,
        cause=Exception("simulated analysis failure"),
    )

    mock_queries = MagicMock()
    mock_retrieved_chunks = [MagicMock()]
    mock_ranked_chunks = [MagicMock()]

    mock_context = "mock analysis context"
    mock_evidence_map = {"E1": MagicMock()}
    mock_source_map = {"S1": MagicMock()}

    with (
        patch.object(
            analysis_agent,
            "plan_retrieval_queries",
            return_value=mock_queries,
        ),
        patch.object(
            analysis_agent,
            "retrieve_analysis_chunks",
            return_value=mock_retrieved_chunks,
        ),
        patch.object(
            analysis_agent,
            "rank_and_deduplicate_chunks",
            return_value=mock_ranked_chunks,
        ),
        patch.object(
            analysis_agent,
            "build_analysis_context",
            return_value=(
                mock_context,
                mock_evidence_map,
                mock_source_map,
            ),
        ),
        patch.object(
            analysis_agent,
            "generate_analysis",
            side_effect=llm_error,
        ) as mock_generate_analysis,
        patch.object(
            analysis_agent,
            "prepare_analysis_result",
        ) as mock_prepare_result,
        patch.object(
            knowledge_base_service,
            "ingest_analysis",
        ) as mock_ingest_analysis,
    ):
        initial_state = {
            "blog_request": blog_request,
            "research_id": research_id,
            "analysis_status": "Started",
        }

        # Act

        with pytest.raises(AnalysisGenerationError) as exc_info:
            analysis_graph.invoke(initial_state)

    # Assert

    error = exc_info.value

    assert error is llm_error
    assert error.error_code == ErrorCodes.ANALYSIS_GENERATION_FAILED
    assert error.workflow == "analysis"
    assert error.node == "generate_analysis"
    assert error.retryable is False

    mock_generate_analysis.assert_called_once()

    mock_prepare_result.assert_not_called()
    mock_ingest_analysis.assert_not_called()


def test_analysis_workflow_persistence_failure():
    # Arrange

    blog_request = MagicMock()
    research_id = uuid4()

    mock_queries = MagicMock()
    mock_retrieved_chunks = [MagicMock()]
    mock_ranked_chunks = [MagicMock()]

    mock_context = "mock analysis context"
    mock_evidence_map = {"E1": MagicMock()}
    mock_source_map = {"S1": MagicMock()}

    mock_llm_result = MagicMock()
    mock_analysis_result = MagicMock()

    database_error = DatabaseError(
        message="Analysis Saving Failed",
        error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
        workflow="analysis",
        node="save_analysis",
        retryable=False,
        cause=Exception("simulated persistence failure"),
    )

    persistence_error = AnalysisPersistenceError(
        message="Analysis Persistence Failed",
        error_code=ErrorCodes.ANALYSIS_PERSISTENCE_FAILED,
        workflow="analysis",
        node="ingest_analysis",
        retryable=False,
        cause=database_error,
    )

    with (
        patch.object(
            analysis_agent,
            "plan_retrieval_queries",
            return_value=mock_queries,
        ),
        patch.object(
            analysis_agent,
            "retrieve_analysis_chunks",
            return_value=mock_retrieved_chunks,
        ),
        patch.object(
            analysis_agent,
            "rank_and_deduplicate_chunks",
            return_value=mock_ranked_chunks,
        ),
        patch.object(
            analysis_agent,
            "build_analysis_context",
            return_value=(
                mock_context,
                mock_evidence_map,
                mock_source_map,
            ),
        ),
        patch.object(
            analysis_agent,
            "generate_analysis",
            return_value=mock_llm_result,
        ),
        patch.object(
            analysis_agent,
            "prepare_analysis_result",
            return_value=mock_analysis_result,
        ),
        patch.object(
            knowledge_base_service,
            "ingest_analysis",
            side_effect=persistence_error,
        ) as mock_ingest_analysis,
    ):
        initial_state = {
            "blog_request": blog_request,
            "research_id": research_id,
            "analysis_status": "Started",
        }

        # Act

        with pytest.raises(AnalysisPersistenceError) as exc_info:
            analysis_graph.invoke(initial_state)

    # Assert

    error = exc_info.value

    assert error is persistence_error
    assert error.error_code == ErrorCodes.ANALYSIS_PERSISTENCE_FAILED
    assert error.workflow == "analysis"
    assert error.node == "ingest_analysis"
    assert error.retryable is False

    mock_ingest_analysis.assert_called_once_with(
        research_id=research_id,
        analysis_result=mock_analysis_result,
    )
