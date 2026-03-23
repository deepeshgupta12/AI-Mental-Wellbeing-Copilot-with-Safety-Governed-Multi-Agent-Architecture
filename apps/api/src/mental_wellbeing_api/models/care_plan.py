from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class CarePlan(Base):
    __tablename__ = "care_plans"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversation_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action_plan_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("action_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_agent: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    program_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    plan_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="care_program",
        server_default="care_program",
        index=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )
    current_step_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    preferred_language: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="en",
        server_default="en",
        index=True,
    )
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_check_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    last_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cadence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sequence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    progress_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    adherence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    schedule_contract_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

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