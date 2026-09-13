from blogforge_ai.rag.chunker import chunking_service
from blogforge_ai.rag.embeddings import embedding_service
from blogforge_ai.rag.rag_schemas import RetrievalResult
from blogforge_ai.schemas.research_schemas import ResearchResult
from blogforge_ai.database.models.research import Research
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.database.models.research_source import ResearchSource
from blogforge_ai.database.models.analysis import Analysis
from blogforge_ai.database.models.draft import Draft
from blogforge_ai.schemas.writer_schemas import WriterLLMResult
from blogforge_ai.database.models.fact_check import FactCheck
from blogforge_ai.schemas.fact_checker_schemas import FactCheckResult
from blogforge_ai.schemas.analysis_schemas import AnalysisResult
from blogforge_ai.rag.knowledge_base_repository import KnowledgeBaseRepository
from blogforge_ai.database.session import db_manager
from uuid import UUID
from blogforge_ai.exceptions.database import DatabaseError
from blogforge_ai.exceptions.research import ResearchPersistenceError
from blogforge_ai.exceptions.analysis import AnalysisPersistenceError
from blogforge_ai.exceptions.fact_checker import FactCheckPersistenceError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.writer import WriterPersistenceError


class KnowledgeBaseService:
    def __init__(self):
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service

    def ingest_research(self, research_output: ResearchResult) -> UUID:
        try:
            with db_manager.session() as session:

                knowledge_repository = KnowledgeBaseRepository(session=session)

                research = Research()

                saved_research = knowledge_repository.save_research(
                    research=research)

                research_sources = self._create_research_source(
                    research_output=research_output, research_id=saved_research.id)

                saved_research_sources = knowledge_repository.save_research_sources(
                    sources=research_sources)

                source_ids = {
                    source.source_id: source.id for source in saved_research_sources
                }

                research_chunks = self._create_research_chunks(
                    research_output=research_output, source_ids=source_ids, research_id=saved_research.id)

                knowledge_repository.save_research_chunks(
                    chunks=research_chunks)

            return saved_research.id
        except DatabaseError as e:
            raise ResearchPersistenceError(
                message='Research Persistence Failed',
                error_code=ErrorCodes.RESEARCH_PERSISTENCE_FAILED,
                workflow='research',
                node='ingest_research',
                retryable=e.retryable,
                cause=e
            )

    def retrieve_relevant_chunks(self, research_id: UUID, query: str, top_k: int = 5) -> list[RetrievalResult]:
        query_embedding = self.embedding_service.embed_query(query=query)
        with db_manager.session() as session:
            knowledge_repository = KnowledgeBaseRepository(session=session)

            retrieved_chunks = knowledge_repository.retrieve_similar_chunks(
                research_id=research_id, query_embedding=query_embedding, top_k=top_k)

            results = []
            for chunk, source, cosine_distance in retrieved_chunks:
                results.append(RetrievalResult(
                    chunk_id=chunk.id,
                    research_id=chunk.research_id,
                    source_id=source.id,
                    content=chunk.content,
                    source_title=source.title,
                    source_url=source.url,
                    similarity_score=1-cosine_distance
                ))
            return results

    def ingest_analysis(self, research_id: UUID, analysis_result: AnalysisResult) -> UUID:
        try:
            with db_manager.session() as session:
                knowledge_repository = KnowledgeBaseRepository(session=session)
                analysis = self._create_analysis(
                    research_id=research_id, analysis_result=analysis_result)
                analysis = knowledge_repository.save_analysis(analysis)
                return analysis.id
        except DatabaseError as e:
            raise AnalysisPersistenceError(
                message='Analysis Persistence Failed',
                error_code=ErrorCodes.ANALYSIS_PERSISTENCE_FAILED,
                workflow='analysis',
                node='ingest_analysis',
                retryable=e.retryable,
                cause=e
            )

    def retrieve_analyses(self, research_id: UUID) -> list[Analysis]:
        with db_manager.session() as session:
            knowledge_repository = KnowledgeBaseRepository(session=session)
            analyses = knowledge_repository.retrieve_analyses(
                research_id=research_id)
        return analyses

    def retrieve_latest_analysis(self, research_id: UUID) -> Analysis:
        with db_manager.session() as session:
            knowledge_repository = KnowledgeBaseRepository(session=session)
            analysis = knowledge_repository.retrieve_latest_analysis(
                research_id=research_id)
        return analysis

    def ingest_fact_check(self, analysis_id: UUID, fact_check_result: FactCheckResult) -> UUID:
        try:
            with db_manager.session() as session:
                knowledge_repository = KnowledgeBaseRepository(session=session)
                fact_check = self._create_fact_check(
                    analysis_id=analysis_id, fact_check_result=fact_check_result)

                fact_check = knowledge_repository.save_fact_check(
                    fact_check=fact_check)
                return fact_check.id
        except DatabaseError as e:
            raise FactCheckPersistenceError(
                message='Fact Check Persistence Failed',
                error_code=ErrorCodes.FACT_CHECK_PERSISTENCE_FAILED,
                workflow='fact_check',
                node='ingest_fact_check',
                retryable=e.retryable,
                cause=e
            )

    def retrieve_fact_check_by_id(self, fact_check_id: UUID) -> FactCheck:
        with db_manager.session() as session:
            knowledge_repository = KnowledgeBaseRepository(session=session)
            fact_check = knowledge_repository.retrieve_fact_check_by_id(
                fact_check_id=fact_check_id)
        return fact_check

    def ingest_blog_draft(self, fact_check_id: UUID, writer_result: WriterLLMResult) -> UUID:
        try:
            with db_manager.session() as session:
                knowledge_repository = KnowledgeBaseRepository(session=session)
                draft = self._create_draft(
                    fact_check_id=fact_check_id, writer_result=writer_result)
                draft = knowledge_repository.save_blog_draft(draft=draft)
            return draft.id
        except DatabaseError as e:
            raise WriterPersistenceError(
                message='Blog Draft Persistence Failed',
                error_code=ErrorCodes.WRITER_PERSISTENCE_FAILED,
                workflow='writing',
                node='ingest_blog_draft',
                retryable=e.retryable,
                cause=e
            )

    def retrieve_chunks_by_ids(self, chunk_ids: list[UUID]) -> list[ResearchChunk]:
        with db_manager.session() as session:
            knowledge_repository = KnowledgeBaseRepository(session=session)
            chunks = knowledge_repository.retrieve_chunks_by_ids(chunk_ids)

        return chunks

    def _create_research_chunks(self, research_output: ResearchResult, source_ids: dict, research_id: UUID) -> list[ResearchChunk]:
        chunks = self.chunking_service.chunk_research(
            research_result=research_output, source_ids=source_ids)

        if not chunks:
            return []

        embeddings = self.embedding_service.embed_chunks(chunks=chunks)

        research_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            research_chunks.append(ResearchChunk(
                research_id=research_id,
                research_source_id=chunk.research_source_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
            ))

        return research_chunks

    def _create_research_source(self, research_output: ResearchResult, research_id: UUID) -> list[ResearchSource]:

        research_sources = []

        for source in research_output.selected_sources:
            research_sources.append(ResearchSource(
                research_id=research_id,
                source_id=source.source.id,
                title=source.source.title,
                url=source.source.url,
                selection_reason=source.selection_reason
            ))

        return research_sources

    def _create_analysis(self, research_id: UUID, analysis_result: AnalysisResult) -> Analysis:

        return Analysis(
            research_id=research_id,
            title=analysis_result.title,
            overview=analysis_result.overview,
            developments=[
                item.model_dump(mode="json")
                for item in analysis_result.developments],
            limitations=[
                item.model_dump(mode="json")
                for item in analysis_result.limitations],
            future_scope=[
                item.model_dump(mode="json")
                for item in analysis_result.future_scope],
            references=[
                item.model_dump(mode="json")
                for item in analysis_result.references]
        )

    def _create_fact_check(self, analysis_id: UUID, fact_check_result: FactCheckResult) -> FactCheck:
        return FactCheck(
            analysis_id=analysis_id,
            title=fact_check_result.title,
            overview=fact_check_result.overview,
            claims=[claim.model_dump(mode="json")
                    for claim in fact_check_result.claims],
            references=[reference.model_dump(mode="json")
                        for reference in fact_check_result.references]
        )

    def _create_draft(self, fact_check_id: UUID, writer_result: WriterLLMResult) -> Draft:
        return Draft(
            fact_check_id=fact_check_id,
            title=writer_result.blog_title,
            introduction=writer_result.blog_introduction,
            sections=[section.model_dump(mode='json')
                      for section in writer_result.sections],
            conclusion=writer_result.conclusion,
            references=[reference.model_dump(mode="json")
                        for reference in writer_result.references]
        )


knowledge_base_service = KnowledgeBaseService()
