from uuid import uuid4
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.rag.knowledge_base_repository import KnowledgeBaseRepository
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.analysis import AnalysisPersistenceError
from blogforge_ai.database.models.analysis import Analysis
import uuid
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service


def test_analysis_save_success():
    analysis = MagicMock()
    mock_session = MagicMock()
    repository = KnowledgeBaseRepository(session=mock_session)

    result = repository.save_analysis(analysis=analysis)
    mock_session.add.assert_called_once_with(analysis)
    mock_session.flush.assert_called_once()
    assert result is analysis


def test_analysis_save_error():

    analysis = MagicMock()
    mock_session = MagicMock()

    sql_error = SQLAlchemyError("simulated database failure")
    mock_session.flush.side_effect = sql_error

    repository = KnowledgeBaseRepository(session=mock_session)

    with pytest.raises(DatabaseError) as exc_info:
        repository.save_analysis(analysis=analysis)

    error = exc_info.value

    assert error.error_code == ErrorCodes.DATABASE_OPERATION_FAILED
    assert error.workflow == "analysis"
    assert error.node == "save_analysis"
    assert error.retryable is False
    assert error.cause is sql_error

    mock_session.add.assert_called_once_with(analysis)
    mock_session.flush.assert_called_once()


def create_analysis() -> Analysis:

    return Analysis(
        research_id=uuid.uuid4(),
        title='title',
        overview='overview',
        developments=[],
        limitations=[],
        future_scope=[],
        references=[]
    )


def test_ingest_analysis_success():

    research_id = uuid4()
    analysis_id = uuid4()

    analysis_result = MagicMock()
    analysis = MagicMock()
    analysis.id = analysis_id

    mock_session = MagicMock()
    mock_repository = MagicMock()

    mock_repository.save_analysis.return_value = analysis

    with patch(
        "blogforge_ai.rag.knowledge_base_service.db_manager.session"
    ) as mock_db_session, patch(
        "blogforge_ai.rag.knowledge_base_service.KnowledgeBaseRepository",
        return_value=mock_repository,
    ) as mock_repository_class, patch.object(
        knowledge_base_service,
        "_create_analysis",
        return_value=analysis,
    ) as mock_create_analysis:

        mock_db_session.return_value.__enter__.return_value = mock_session

        result = knowledge_base_service.ingest_analysis(
            research_id=research_id,
            analysis_result=analysis_result,
        )

    assert result == analysis_id

    mock_create_analysis.assert_called_once_with(
        research_id=research_id,
        analysis_result=analysis_result,
    )

    mock_repository_class.assert_called_once_with(session=mock_session)

    mock_repository.save_analysis.assert_called_once_with(analysis)


def test_analysis_persist_failure():
    database_error = DatabaseError(
        message='Analysis Saving Failed',
        error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
        workflow='analysis',
        node='save_analysis',
        retryable=False,
        cause=Exception('simulated persistence Failure')
    )
    mock_repository = MagicMock()
    mock_repository.save_analysis.side_effect = database_error

    mock_session = MagicMock()
    mock_db_session = MagicMock()

    mock_db_session.__enter__.return_value = mock_session
    research_id = uuid4()
    analysis_result = MagicMock()

    with patch(
        "blogforge_ai.rag.knowledge_base_service.db_manager.session",
        return_value=mock_db_session,
    ), patch(
        "blogforge_ai.rag.knowledge_base_service.KnowledgeBaseRepository",
        return_value=mock_repository,
    ):
        with pytest.raises(AnalysisPersistenceError) as exc_info:
            knowledge_base_service.ingest_analysis(
                research_id=research_id,
                analysis_result=analysis_result,
            )
    error = exc_info.value
    assert error.error_code == ErrorCodes.ANALYSIS_PERSISTENCE_FAILED
    assert error.workflow == "analysis"
    assert error.node == "ingest_analysis"
    assert error.retryable is False
    assert error.cause is database_error
    mock_repository.save_analysis.assert_called_once()
