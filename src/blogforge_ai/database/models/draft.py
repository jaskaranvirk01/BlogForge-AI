from sqlalchemy import String, DateTime, func, text, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from uuid import UUID
from blogforge_ai.database.base import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blogforge_ai.database.models.fact_check import FactCheck


class Draft(Base):
    __tablename__ = 'drafts'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    fact_check_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('fact_checks.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    introduction: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    sections: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )

    conclusion: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    references: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    fact_check: Mapped['FactCheck'] = relationship(
        back_populates='drafts'
    )
