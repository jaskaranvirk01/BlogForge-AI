from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, ArgumentError
from blogforge_ai.core.settings import settings


class DatabaseManager:
    def __init__(self):
        try:
            self.engine = create_engine(
                settings.supabase_database_url, echo=True, pool_pre_ping=True)
            self.session_local = sessionmaker(
                bind=self.engine, autoflush=False)
        except (SQLAlchemyError, ArgumentError) as e:
            raise e

    def get_session(self) -> Session:
        return self.session_local()
