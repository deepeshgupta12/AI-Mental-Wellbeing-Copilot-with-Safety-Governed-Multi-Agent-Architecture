from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class CarePlanEvent(Base):
    __tablename__ = "care_plan_events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    care_plan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("care_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_status: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    step_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    adherence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )