from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, ArgumentError
from blogforge_ai.core.settings import settings
from contextlib import contextmanager
from collections.abc import Generator
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes


class DatabaseManager:
    '''Manages the SQLAlchemy database engine and session factory'''

    def __init__(self):
        try:
            self.engine = create_engine(
                settings.supabase_database_url, echo=True, pool_pre_ping=True)
            self.session_local = sessionmaker(
                bind=self.engine, autoflush=False, expire_on_commit=False)
        except (SQLAlchemyError, ArgumentError) as e:
            raise e

    def get_session(self) -> Session:
        return self.session_local()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        db = self.get_session()
        try:
            yield db
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise DatabaseError(
                message="Database Commit Failed",
                error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
                workflow='database',
                node="session_commit",
                retryable=False,
                cause=e
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


db_manager = DatabaseManager()
