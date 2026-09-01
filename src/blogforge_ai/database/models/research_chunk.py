from typing import TYPE_CHECKING
from datetime import datetime
from blogforge_ai.database.base import Base
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import DateTime, func, text, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

if TYPE_CHECKING:
    from blogforge_ai.database.models.research import Research
    from blogforge_ai.database.models.research_source import ResearchSource


class ResearchChunk(Base):
    __tablename__ = 'research_chunks'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    research_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('research.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    research_source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('research_sources.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    source: Mapped['ResearchSource'] = relationship(
        back_populates='chunks'
    )
    research: Mapped["Research"] = relationship(
        back_populates="chunks"
    )
