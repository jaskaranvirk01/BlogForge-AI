from unittest.mock import MagicMock, patch
import pytest
from blogforge_ai.exceptions.analysis import AnalysisGenerationError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.agents.analysis_agent import analysis_agent


def test_plan_retrieval_queries_generation_failure():

    mock_query_planning_llm = MagicMock()
    blog_request = MagicMock()

    llm_error = Exception("simulated analysis failure")

    mock_query_planning_llm.invoke.side_effect = llm_error

    analysis_agent.query_planning_llm = mock_query_planning_llm

    with pytest.raises(AnalysisGenerationError) as exc_info:
        analysis_agent.plan_retrieval_queries(
            blog_request=blog_request
        )

    error = exc_info.value

    assert error.error_code == ErrorCodes.ANALYSIS_GENERATION_FAILED
    assert error.workflow == "analysis"
    assert error.node == "plan_retrieval_queries"
    assert error.retryable is False
    assert error.cause is llm_error

    mock_query_planning_llm.invoke.assert_called_once()


def test_generate_analysis_llm_failure():
    mock_analysis_llm = MagicMock()
    blog_request = MagicMock()
    context = MagicMock()
    llm_error = Exception('simulated analysis failure')
    mock_analysis_llm.invoke.side_effect = llm_error
    analysis_agent.analysis_llm = mock_analysis_llm

    with pytest.raises(AnalysisGenerationError) as exc_info:
        analysis_agent.generate_analysis(
            blog_request=blog_request, analysis_context=context)

    error = exc_info.value
    assert error.error_code == ErrorCodes.ANALYSIS_GENERATION_FAILED
    assert error.workflow == 'analysis'
    assert error.node == 'generate_analysis'
    assert error.retryable is False
    assert error.cause is llm_error

    mock_analysis_llm.invoke.assert_called_once()
