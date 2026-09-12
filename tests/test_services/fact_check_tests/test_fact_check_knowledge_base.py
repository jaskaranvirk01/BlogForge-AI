from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from blogforge_ai.exceptions.fact_checker import FactCheckPersistenceError
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.rag.knowledge_base_repository import KnowledgeBaseRepository
from uuid import uuid4


def test_fact_check_persistence_success():
    mock_session = MagicMock()
    mock_repository = KnowledgeBaseRepository(session=mock_session)
    fact_check = MagicMock()

    result = mock_repository.save_fact_check(fact_check=fact_check)

    mock_session.add.assert_called_once_with(fact_check)
    mock_session.flush.assert_called_once_with()

    assert result is fact_check


def test_fact_persistence_error():
    mock_session = MagicMock()
    fact_check = MagicMock()
    mock_repository = KnowledgeBaseRepository(session=mock_session)
    db_error = SQLAlchemyError('simulated Databse error')

    mock_session.flush.side_effect = db_error

    with pytest.raises(DatabaseError) as exc_info:
        mock_repository.save_fact_check(fact_check=fact_check)

    error = exc_info.value
    assert error.error_code == ErrorCodes.DATABASE_OPERATION_FAILED
    assert error.workflow == "fact-check"
    assert error.node == "save_fact_check"
    assert error.retryable is False
    assert error.cause is db_error

    mock_session.add.assert_called_once_with(fact_check)
    mock_session.flush.assert_called_once()


def test_ingest_fact_check_success():
    analysis_id = uuid4()
    fact_check_id = uuid4()

    fact_check_result = MagicMock()

    fact_check = MagicMock()
    fact_check.id = fact_check_id

    mock_repository = MagicMock()
    mock_repository.save_fact_check.return_value = fact_check

    mock_session = MagicMock()
    mock_db_session = MagicMock()
    mock_db_session.__enter__.return_value = mock_session

    with (
        patch(
            "blogforge_ai.rag.knowledge_base_service.db_manager.session",
            return_value=mock_db_session,
        ),
        patch(
            "blogforge_ai.rag.knowledge_base_service.KnowledgeBaseRepository",
            return_value=mock_repository,
        ),
        patch.object(
            knowledge_base_service,
            "_create_fact_check",
            return_value=fact_check,
        ) as mock_create_fact_check,
    ):
        result = knowledge_base_service.ingest_fact_check(
            analysis_id=analysis_id,
            fact_check_result=fact_check_result,
        )

    assert result == fact_check_id

    mock_create_fact_check.assert_called_once_with(
        analysis_id=analysis_id,
        fact_check_result=fact_check_result,
    )

    mock_repository.save_fact_check.assert_called_once_with(
        fact_check=fact_check,
    )


def test_fact_check_persistence_failure():
    analysis_id = uuid4()
    fact_check_result = MagicMock()
    fact_check = MagicMock()
    database_error = DatabaseError(
        message="Fact Check Saving Failed",
        error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
        workflow="fact_check",
        node="save_fact_check",
        retryable=False,
        cause=Exception("simulated persistence failure"),
    )

    mock_repository = MagicMock()
    mock_repository.save_fact_check.side_effect = database_error

    mock_session = MagicMock()
    mock_db_session = MagicMock()
    mock_db_session.__enter__.return_value = mock_session

    with (
        patch(
            'blogforge_ai.rag.knowledge_base_service.db_manager.session',
            return_value=mock_db_session
        ),
        patch(
            'blogforge_ai.rag.knowledge_base_service.KnowledgeBaseRepository',
            return_value=mock_repository
        ),
        patch.object(
            knowledge_base_service,
            '_create_fact_check',
            return_value=fact_check,
        )
    ):
        with pytest.raises(FactCheckPersistenceError) as exc_info:
            knowledge_base_service.ingest_fact_check(
                analysis_id=analysis_id, fact_check_result=fact_check_result)

        error = exc_info.value

        assert error.error_code == ErrorCodes.FACT_CHECK_PERSISTENCE_FAILED
        assert error.workflow == 'fact_check'
        assert error.node == 'ingest_fact_check'
        assert error.retryable is False
        assert error.cause is database_error

    mock_repository.save_fact_check.assert_called_once_with(
        fact_check=fact_check,
    )
