from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_wellbeing_api.db.base import Base


class AdminConfigAudit(Base):
    __tablename__ = "admin_config_audits"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    config_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_version_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("admin_config_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    to_version_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("admin_config_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_keys_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    diff_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    actor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )