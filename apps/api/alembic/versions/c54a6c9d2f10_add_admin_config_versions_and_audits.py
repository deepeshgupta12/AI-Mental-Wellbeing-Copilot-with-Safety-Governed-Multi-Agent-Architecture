"""add admin config versions and audits

Revision ID: c54a6c9d2f10
Revises: 9c1d4d4e8b21
Create Date: 2026-03-19 16:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "c54a6c9d2f10"
down_revision = "9c1d4d4e8b21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_config_versions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("config_key", sa.String(length=100), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("change_note", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_config_versions")),
    )
    op.create_index(op.f("ix_admin_config_versions_config_key"), "admin_config_versions", ["config_key"], unique=False)
    op.create_index(op.f("ix_admin_config_versions_is_active"), "admin_config_versions", ["is_active"], unique=False)
    op.create_index(op.f("ix_admin_config_versions_created_at"), "admin_config_versions", ["created_at"], unique=False)

    op.create_table(
        "admin_config_audits",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("config_key", sa.String(length=100), nullable=False),
        sa.Column("from_version_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("to_version_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("changed_keys_json", sa.JSON(), nullable=True),
        sa.Column("diff_json", sa.JSON(), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["from_version_id"], ["admin_config_versions.id"], name=op.f("fk_admin_config_audits_from_version_id_admin_config_versions"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_version_id"], ["admin_config_versions.id"], name=op.f("fk_admin_config_audits_to_version_id_admin_config_versions"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_config_audits")),
    )
    op.create_index(op.f("ix_admin_config_audits_config_key"), "admin_config_audits", ["config_key"], unique=False)
    op.create_index(op.f("ix_admin_config_audits_from_version_id"), "admin_config_audits", ["from_version_id"], unique=False)
    op.create_index(op.f("ix_admin_config_audits_to_version_id"), "admin_config_audits", ["to_version_id"], unique=False)
    op.create_index(op.f("ix_admin_config_audits_created_at"), "admin_config_audits", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_admin_config_audits_created_at"), table_name="admin_config_audits")
    op.drop_index(op.f("ix_admin_config_audits_to_version_id"), table_name="admin_config_audits")
    op.drop_index(op.f("ix_admin_config_audits_from_version_id"), table_name="admin_config_audits")
    op.drop_index(op.f("ix_admin_config_audits_config_key"), table_name="admin_config_audits")
    op.drop_table("admin_config_audits")

    op.drop_index(op.f("ix_admin_config_versions_created_at"), table_name="admin_config_versions")
    op.drop_index(op.f("ix_admin_config_versions_is_active"), table_name="admin_config_versions")
    op.drop_index(op.f("ix_admin_config_versions_config_key"), table_name="admin_config_versions")
    op.drop_table("admin_config_versions")