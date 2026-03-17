from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class SafetyFlag(Base):
    __tablename__ = "safety_flags"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    flag_type: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )