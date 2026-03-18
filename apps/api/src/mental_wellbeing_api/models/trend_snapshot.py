from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

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
    window_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    snapshot_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    snapshot_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    summary_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )