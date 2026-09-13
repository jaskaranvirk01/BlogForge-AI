from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError

from blogforge_ai.rag.knowledge_base_repository import (
    KnowledgeBaseRepository,
)
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes

import pytest

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.writer import WriterPersistenceError
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


def test_save_blog_draft_success():
    mock_session = MagicMock()
    repository = KnowledgeBaseRepository(session=mock_session)

    draft = MagicMock()

    result = repository.save_blog_draft(draft=draft)

    mock_session.add.assert_called_once_with(draft)
    mock_session.flush.assert_called_once()
    assert result is draft


def test_save_blog_draft_database_error():
    mock_session = MagicMock()
    sql_error = SQLAlchemyError("simulated database failure")
    mock_session.flush.side_effect = sql_error

    repository = KnowledgeBaseRepository(session=mock_session)

    draft = MagicMock()

    with pytest.raises(DatabaseError) as exc_info:
        repository.save_blog_draft(draft=draft)

    error = exc_info.value

    assert error.error_code == ErrorCodes.DATABASE_OPERATION_FAILED
    assert error.workflow == "writing"
    assert error.node == "save_blog_draft"
    assert error.retryable is False
    assert error.cause is sql_error

    mock_session.add.assert_called_once_with(draft)
    mock_session.flush.assert_called_once()


def test_ingest_blog_draft_success():
    fact_check_id = uuid4()
    draft_id = uuid4()

    writer_result = MagicMock()
    draft = MagicMock()
    draft.id = draft_id

    mock_repository = MagicMock()
    mock_repository.save_blog_draft.return_value = draft

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
            "_create_draft",
            return_value=draft,
        ) as mock_create_draft,
    ):
        result = knowledge_base_service.ingest_blog_draft(
            fact_check_id=fact_check_id,
            writer_result=writer_result,
        )

    assert result == draft_id

    mock_create_draft.assert_called_once_with(
        fact_check_id=fact_check_id,
        writer_result=writer_result,
    )

    mock_repository.save_blog_draft.assert_called_once_with(
        draft=draft,
    )


def test_ingest_blog_draft_persistence_failure():
    fact_check_id = uuid4()
    writer_result = MagicMock()
    draft = MagicMock()

    database_error = DatabaseError(
        message="Blog Draft Saving Failed",
        error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
        workflow="writing",
        node="save_blog_draft",
        retryable=False,
        cause=Exception("simulated persistence failure"),
    )

    mock_repository = MagicMock()
    mock_repository.save_blog_draft.side_effect = database_error

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
            "_create_draft",
            return_value=draft,
        ),
    ):
        with pytest.raises(WriterPersistenceError) as exc_info:
            knowledge_base_service.ingest_blog_draft(
                fact_check_id=fact_check_id,
                writer_result=writer_result,
            )

    error = exc_info.value

    assert error.error_code == ErrorCodes.WRITER_PERSISTENCE_FAILED
    assert error.workflow == "writing"
    assert error.node == "ingest_blog_draft"
    assert error.retryable is False
    assert error.cause is database_error

    mock_repository.save_blog_draft.assert_called_once_with(
        draft=draft,
    )
