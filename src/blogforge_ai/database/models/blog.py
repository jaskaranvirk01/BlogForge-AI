from sqlalchemy import DateTime, func, text, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from blogforge_ai.database.base import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blogforge_ai.database.models.draft import Draft
    from blogforge_ai.database.models.user import User
    from blogforge_ai.database.models.research import Research


class Blog(Base):
    __tablename__ = 'blogs'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    topic: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    target_audience: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    content_type: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    desired_length: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    tone: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    additional_instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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

    drafts: Mapped[list['Draft']] = relationship(
        back_populates='blog', cascade='all, delete-orphan'
    )

    user: Mapped["User"] = relationship(
        back_populates="blogs"
    )

    research: Mapped['Research | None'] = relationship(
        back_populates='blog',
        uselist=False)
