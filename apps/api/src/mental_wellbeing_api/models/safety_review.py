from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class SafetyReview(Base):
    __tablename__ = "safety_reviews"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    safety_event_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("safety_events.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    safety_flag_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("safety_flags.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversation_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    reviewer_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    review_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )
    resolution_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    review_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    escalation_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )
    escalation_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )