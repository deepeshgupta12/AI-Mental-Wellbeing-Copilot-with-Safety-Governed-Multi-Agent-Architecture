from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversation_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    safety_event_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("safety_events.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    safety_review_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("safety_reviews.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    actor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    before_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    event_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    is_immutable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )