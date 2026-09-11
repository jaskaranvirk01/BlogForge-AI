
from unittest.mock import MagicMock, patch

import pytest

from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.research import ResearchPersistenceError
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


def test_ingest_research_translate_database_error_to_research_persistence_error():

    # Arrange
    research_output = MagicMock()

    database_error = DatabaseError(
        message="Research Saving Failed",
        error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
        workflow="research",
        node="save_research",
        retryable=False,
        cause=Exception("simulated database failure"),
    )

    mock_repository = MagicMock()
    mock_repository.save_research.side_effect = database_error

    mock_session = MagicMock()

    mock_context_manager = MagicMock()
    mock_context_manager.__enter__.return_value = mock_session
    mock_context_manager.__exit__.return_value = False

    with patch(
        "blogforge_ai.rag.knowledge_base_service.db_manager.session",
        return_value=mock_context_manager,
    ), patch(
        "blogforge_ai.rag.knowledge_base_service.KnowledgeBaseRepository",
        return_value=mock_repository,
    ):

        # Act + Assert
        with pytest.raises(ResearchPersistenceError) as exc_info:
            knowledge_base_service.ingest_research(
                research_output=research_output
            )

    error = exc_info.value

    # Verify translated error
    assert error.error_code == ErrorCodes.RESEARCH_PERSISTENCE_FAILED
    assert error.workflow == "research"
    assert error.node == "ingest_research"
    assert error.retryable is False
    assert error.cause is database_error

    # Verify repository was actually called
    mock_repository.save_research.assert_called_once()


def test_ingest_research_translate_commit_error_to_research_persistence_error():
    research_output = MagicMock()
    database_error = DatabaseError(
        message='Database Commit Failed',
        error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
        workflow='database',
        node='session_commit',
        retryable=False,
        cause=Exception('Simulated Commit failure')
    )

    mock_repository = MagicMock()
    mock_saved_research = MagicMock()
    mock_saved_research.id = 'research-id'

    mock_repository.save_research.return_value = mock_saved_research
    mock_repository.save_research_sources.return_value = []

    mock_session = MagicMock()
    mock_context_manager = MagicMock()
    mock_context_manager.__enter__.return_value = mock_session

    mock_context_manager.__exit__.side_effect = database_error

    with patch(
        'blogforge_ai.rag.knowledge_base_service.db_manager.session', return_value=mock_context_manager
    ), patch(
        'blogforge_ai.rag.knowledge_base_repository', return_value=mock_repository
    ):
        with pytest.raises(ResearchPersistenceError) as exc_info:
            knowledge_base_service.ingest_research(
                research_output=research_output)

    error = exc_info.value

    assert error.error_code == ErrorCodes.RESEARCH_PERSISTENCE_FAILED
    assert error.workflow == "research"
    assert error.node == "ingest_research"
    assert error.retryable is False
    assert error.cause is database_error
