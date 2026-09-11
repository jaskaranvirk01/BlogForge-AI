from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.database.session import DatabaseManager


def test_session_commit_failure_raises_database_error():
    mock_session = MagicMock()

    commit_error = SQLAlchemyError('Simulated commit failure')

    mock_session.commit.side_effect = commit_error

    database_manager = DatabaseManager.__new__(DatabaseManager)

    with patch.object(
        database_manager,
        'get_session',
        return_value=mock_session,
    ):
        with pytest.raises(DatabaseError) as exc_info:
            with database_manager.session():
                pass

    error = exc_info.value

    assert error.error_code == ErrorCodes.DATABASE_OPERATION_FAILED
    assert error.workflow == 'database'
    assert error.node == 'session_commit'
    assert error.retryable is False
    assert error.cause is commit_error

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


def test_session_failure_raises_value_error():
    mock_session = MagicMock()

    value_error = ValueError("Simulated value error")

    mock_session.commit.side_effect = value_error

    database_manager = DatabaseManager.__new__(DatabaseManager)

    with patch.object(
        database_manager,
        'get_session',
        return_value=mock_session
    ):
        with pytest.raises(ValueError) as exc_info:
            with database_manager.session():
                pass

    error = exc_info.value

    assert error is value_error
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


def test_session_completes_commit_transaction():
    mock_session = MagicMock()

    database_manager = DatabaseManager.__new__(DatabaseManager)

    with patch.object(
        database_manager,
        'get_session',
        return_value=mock_session
    ):
        with database_manager.session():
            pass

    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
