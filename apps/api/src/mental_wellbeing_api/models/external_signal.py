from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class ExternalSignal(Base):
    __tablename__ = "external_signals"
    __table_args__ = (
        UniqueConstraint(
            "connection_id",
            "signal_type",
            "source_item_id",
            name="uq_external_signals_connection_signal_source_item",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    connection_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("external_integration_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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

    integration_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    provider_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_item_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    signal_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    signal_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signal_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    numeric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    text_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    signal_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

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