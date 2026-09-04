from sqlalchemy import DateTime, func, text, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from blogforge_ai.database.base import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blogforge_ai.database.models.research_source import ResearchSource
    from blogforge_ai.database.models.research_chunk import ResearchChunk
    from blogforge_ai.database.models.analysis import Analysis


class Research(Base):
    __tablename__ = 'research'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    sources: Mapped[list['ResearchSource']] = relationship(
        back_populates='research',
        cascade="all, delete-orphan"
    )
    chunks: Mapped[list["ResearchChunk"]] = relationship(
        back_populates="research",
        cascade="all, delete-orphan"
    )

    analyses: Mapped[list['Analysis']] = relationship(
        back_populates='research',
        cascade='all,delete-orphan'
    )
