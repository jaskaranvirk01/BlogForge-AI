from blogforge_ai.database.session import Session
from blogforge_ai.database.models.research import Research
from blogforge_ai.database.models.research_source import ResearchSource
from blogforge_ai.database.models.research_chunk import ResearchChunk
from blogforge_ai.database.models.analysis import Analysis
from sqlalchemy import select
from uuid import UUID


class KnowledgeBaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_research_sources(self, sources: list[ResearchSource]) -> list[ResearchSource]:
        self.session.add_all(sources)
        self.session.flush()
        return sources

    def save_research_chunks(self, chunks: list[ResearchChunk]) -> list[ResearchChunk]:
        self.session.add_all(chunks)
        self.session.flush()
        return chunks

    def save_research(self, research: Research) -> Research:
        self.session.add(research)
        self.session.flush()
        return research

    def save_analysis(self, analysis: Analysis) -> Analysis:
        self.session.add(analysis)
        self.session.flush()
        return analysis

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
