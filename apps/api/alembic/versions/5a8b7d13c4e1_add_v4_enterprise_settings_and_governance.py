"""add v4 enterprise settings and governance

Revision ID: 5a8b7d13c4e1
Revises: 3d91d7e4b4aa
Create Date: 2026-03-20 00:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "5a8b7d13c4e1"
down_revision: str | Sequence[str] | None = "3d91d7e4b4aa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "enterprise_settings",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("scope_type", sa.String(length=50), nullable=False),
        sa.Column("scope_id", sa.String(length=120), nullable=False),
        sa.Column("setting_key", sa.String(length=120), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.Column("change_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_enterprise_settings")),
        sa.UniqueConstraint(
            "scope_type",
            "scope_id",
            "setting_key",
            name="uq_enterprise_settings_scope_type_scope_id_setting_key",
        ),
    )
    op.create_index(op.f("ix_enterprise_settings_scope_type"), "enterprise_settings", ["scope_type"], unique=False)
    op.create_index(op.f("ix_enterprise_settings_scope_id"), "enterprise_settings", ["scope_id"], unique=False)
    op.create_index(op.f("ix_enterprise_settings_setting_key"), "enterprise_settings", ["setting_key"], unique=False)
    op.create_index(op.f("ix_enterprise_settings_is_active"), "enterprise_settings", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_enterprise_settings_is_active"), table_name="enterprise_settings")
    op.drop_index(op.f("ix_enterprise_settings_setting_key"), table_name="enterprise_settings")
    op.drop_index(op.f("ix_enterprise_settings_scope_id"), table_name="enterprise_settings")
    op.drop_index(op.f("ix_enterprise_settings_scope_type"), table_name="enterprise_settings")
    op.drop_table("enterprise_settings")