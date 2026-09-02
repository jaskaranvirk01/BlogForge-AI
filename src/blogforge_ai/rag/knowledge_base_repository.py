from blogforge_ai.database.session import db_manager, Session
from blogforge_ai.database.models.research import Research
from blogforge_ai.database.models.research_source import ResearchSource
from blogforge_ai.database.models.research_chunk import ResearchChunk


class KnowledgeBaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_research_sources(self, sources: list[ResearchSource]):
        self.session.add_all(sources)
        self.session.flush()
        return sources

    def save_research_chunks(self, chunks: list[ResearchChunk]):
        self.session.add_all(chunks)
        self.session.flush()
        return chunks

    def save_research(self, research: Research):
        self.session.add(research)
        self.session.flush()
        return research
