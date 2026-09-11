from blogforge_ai.database.session import Session
from blogforge_ai.database.models.research import Research
from blogforge_ai.database.models.research_source import ResearchSource
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.database.models.fact_check import FactCheck
from blogforge_ai.database.models.analysis import Analysis
from blogforge_ai.database.models.draft import Draft
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.error_codes import ErrorCodes


class KnowledgeBaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_research_sources(self, sources: list[ResearchSource]) -> list[ResearchSource]:
        try:
            self.session.add_all(sources)
            self.session.flush()
            return sources
        except SQLAlchemyError as e:
            raise DatabaseError(
                message='Research Sources Saving Failed',
                error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
                workflow='research',
                node='save_research_sources',
                retryable=False,
                cause=e
            )

    def save_research_chunks(self, chunks: list[ResearchChunk]) -> list[ResearchChunk]:
        try:
            self.session.add_all(chunks)
            self.session.flush()
            return chunks
        except SQLAlchemyError as e:
            raise DatabaseError(
                message='Research Chunk Saving Failed',
                error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
                workflow='research',
                node='save_research_chunks',
                retryable=False,
                cause=e
            )

    def save_research(self, research: Research) -> Research:
        try:
            self.session.add(research)
            self.session.flush()
            return research
        except SQLAlchemyError as e:
            raise DatabaseError(
                message='Research Saving Failed',
                error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
                workflow='research',
                node='save_research',
                retryable=False,
                cause=e
            )

    def save_analysis(self, analysis: Analysis) -> Analysis:
        try:
            self.session.add(analysis)
            self.session.flush()
            return analysis
        except SQLAlchemyError as e:
            raise DatabaseError(
                message='Analysis Saving Failed',
                error_code=ErrorCodes.DATABASE_OPERATION_FAILED,
                workflow='analysis',
                node='save_analysis',
                retryable=False,
                cause=e
            )

    def save_fact_check(self, fact_check: FactCheck) -> FactCheck:
        self.session.add(fact_check)
        self.session.flush()
        return fact_check

    def save_blog_draft(self, draft: Draft) -> Draft:
        self.session.add(draft)
        self.session.flush()
        return draft

    def retrieve_fact_check_by_id(self, fact_check_id: UUID) -> FactCheck | None:
        result = self.session.query(FactCheck).where(
            FactCheck.id == fact_check_id).first()
        return result

    def retrieve_similar_chunks(self, research_id: UUID, query_embedding: list[float], top_k: int = 5) -> list:
        cosine_distance = ResearchChunk.embedding.cosine_distance(
            query_embedding)

        stmt = (
            select(ResearchChunk,
                   ResearchSource,
                   cosine_distance.label('cosine_distance'),
                   )
            .select_from(ResearchChunk)
            .join(ResearchSource,
                  ResearchChunk.research_source_id == ResearchSource.id
                  )
            .where(ResearchChunk.research_id == research_id)
            .order_by(cosine_distance.asc())
            .limit(top_k)
        )

        results = self.session.execute(stmt)
        return results.all()

    def retrieve_analyses(self, research_id: UUID) -> list[Analysis]:
        results = self.session.query(Analysis).where(
            Analysis.research_id == research_id)
        return results.all()

    def retrieve_latest_analysis(self, research_id: UUID) -> Analysis | None:
        result = self.session.query(Analysis).where(
            Analysis.research_id == research_id).order_by(Analysis.created_at.desc()).first()
        return result

    def retrieve_chunks_by_ids(self, chunk_ids: list[UUID]) -> list[ResearchChunk]:

        if len(chunk_ids) == 0:
            return []

        chunks = self.session.query(ResearchChunk).filter(
            ResearchChunk.id.in_(chunk_ids)).all()

        return chunks
