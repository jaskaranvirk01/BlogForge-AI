from sqlalchemy import DateTime, func, text, ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from blogforge_ai.database.base import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blogforge_ai.database.models.research import Research
    from blogforge_ai.database.models.research_chunk import ResearchChunk


class ResearchSource(Base):
    __tablename__ = 'research_sources'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    research_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('research.id', ondelete='CASCADE'),
        index=True,
        nullable=False
    )

    source_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    selection_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    research: Mapped['Research'] = relationship(
        back_populates='sources'
    )

    chunks: Mapped[list['ResearchChunk']] = relationship(
        back_populates='source',
        cascade='all, delete-orphan'
    )
