from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class InterventionLog(Base):
    __tablename__ = "intervention_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
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
    action_plan_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("action_plans.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    intervention_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    recommendation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    effectiveness_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback_note: Mapped[str | None] = mapped_column(Text, nullable=True)
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