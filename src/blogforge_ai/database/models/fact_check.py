from sqlalchemy import DateTime, func, text, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from uuid import UUID
from blogforge_ai.database.base import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blogforge_ai.database.models.analysis import Analysis


class FactCheck(Base):
    __tablename__ = 'fact_checks'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
        nullable=False
    )

    analysis_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('analysis.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
        unique=True
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    overview: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    claims: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )

    references: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    analysis: Mapped['Analysis'] = relationship(
        back_populates='fact_check'
    )
