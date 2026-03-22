"""add v4 pack6 external integrations

Revision ID: b41a9a6d0f22
Revises: 8c2f7a4d91b0, 2f1b7aa901c1
Create Date: 2026-03-22 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b41a9a6d0f22"
down_revision: str | Sequence[str] | None = ("8c2f7a4d91b0", "2f1b7aa901c1")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "external_integration_connections",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("integration_key", sa.String(length=80), nullable=False),
        sa.Column("provider_key", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column(
            "connection_status",
            sa.String(length=50),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "consent_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("access_scope_json", sa.JSON(), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_status", sa.String(length=50), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_integration_connections")),
        sa.UniqueConstraint(
            "user_id",
            "integration_key",
            "provider_key",
            name="uq_external_integration_connections_user_provider",
        ),
    )
    op.create_index(
        op.f("ix_external_integration_connections_user_id"),
        "external_integration_connections",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_organization_id"),
        "external_integration_connections",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_integration_key"),
        "external_integration_connections",
        ["integration_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_provider_key"),
        "external_integration_connections",
        ["provider_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_category"),
        "external_integration_connections",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_connection_status"),
        "external_integration_connections",
        ["connection_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_consent_status"),
        "external_integration_connections",
        ["consent_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_last_synced_at"),
        "external_integration_connections",
        ["last_synced_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_last_sync_status"),
        "external_integration_connections",
        ["last_sync_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_integration_connections_created_at"),
        "external_integration_connections",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "external_sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("integration_key", sa.String(length=80), nullable=False),
        sa.Column("provider_key", sa.String(length=80), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="queued"),
        sa.Column("requested_by", sa.String(length=120), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signal_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cursor_json", sa.JSON(), nullable=True),
        sa.Column("request_payload_json", sa.JSON(), nullable=True),
        sa.Column("result_payload_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["external_integration_connections.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_sync_jobs")),
    )
    op.create_index(op.f("ix_external_sync_jobs_connection_id"), "external_sync_jobs", ["connection_id"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_user_id"), "external_sync_jobs", ["user_id"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_organization_id"), "external_sync_jobs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_integration_key"), "external_sync_jobs", ["integration_key"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_provider_key"), "external_sync_jobs", ["provider_key"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_job_type"), "external_sync_jobs", ["job_type"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_status"), "external_sync_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_external_sync_jobs_created_at"), "external_sync_jobs", ["created_at"], unique=False)

    op.create_table(
        "external_signals",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("integration_key", sa.String(length=80), nullable=False),
        sa.Column("provider_key", sa.String(length=80), nullable=False),
        sa.Column("signal_type", sa.String(length=80), nullable=False),
        sa.Column("source_item_id", sa.String(length=120), nullable=False),
        sa.Column("signal_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signal_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signal_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("numeric_value", sa.Float(), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("signal_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["external_integration_connections.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_signals")),
        sa.UniqueConstraint(
            "connection_id",
            "signal_type",
            "source_item_id",
            name="uq_external_signals_connection_signal_source_item",
        ),
    )
    op.create_index(op.f("ix_external_signals_connection_id"), "external_signals", ["connection_id"], unique=False)
    op.create_index(op.f("ix_external_signals_user_id"), "external_signals", ["user_id"], unique=False)
    op.create_index(op.f("ix_external_signals_organization_id"), "external_signals", ["organization_id"], unique=False)
    op.create_index(op.f("ix_external_signals_integration_key"), "external_signals", ["integration_key"], unique=False)
    op.create_index(op.f("ix_external_signals_provider_key"), "external_signals", ["provider_key"], unique=False)
    op.create_index(op.f("ix_external_signals_signal_type"), "external_signals", ["signal_type"], unique=False)
    op.create_index(op.f("ix_external_signals_source_item_id"), "external_signals", ["source_item_id"], unique=False)
    op.create_index(op.f("ix_external_signals_signal_at"), "external_signals", ["signal_at"], unique=False)
    op.create_index(op.f("ix_external_signals_created_at"), "external_signals", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_external_signals_created_at"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_signal_at"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_source_item_id"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_signal_type"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_provider_key"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_integration_key"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_organization_id"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_user_id"), table_name="external_signals")
    op.drop_index(op.f("ix_external_signals_connection_id"), table_name="external_signals")
    op.drop_table("external_signals")

    op.drop_index(op.f("ix_external_sync_jobs_created_at"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_status"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_job_type"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_provider_key"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_integration_key"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_organization_id"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_user_id"), table_name="external_sync_jobs")
    op.drop_index(op.f("ix_external_sync_jobs_connection_id"), table_name="external_sync_jobs")
    op.drop_table("external_sync_jobs")

    op.drop_index(op.f("ix_external_integration_connections_created_at"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_last_sync_status"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_last_synced_at"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_consent_status"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_connection_status"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_category"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_provider_key"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_integration_key"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_organization_id"), table_name="external_integration_connections")
    op.drop_index(op.f("ix_external_integration_connections_user_id"), table_name="external_integration_connections")
    op.drop_table("external_integration_connections")