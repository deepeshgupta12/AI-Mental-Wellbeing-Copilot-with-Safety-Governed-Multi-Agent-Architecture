"""add v4 pack3 stored artifacts

Revision ID: 8c2f7a4d91b0
Revises: 5a8b7d13c4e1
Create Date: 2026-03-20 12:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "8c2f7a4d91b0"
down_revision: str | Sequence[str] | None = "5a8b7d13c4e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stored_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("scope_type", sa.String(length=80), nullable=False),
        sa.Column("scope_id", sa.String(length=120), nullable=False),
        sa.Column("artifact_kind", sa.String(length=80), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("storage_provider", sa.String(length=40), nullable=False),
        sa.Column("bucket_name", sa.String(length=255), nullable=True),
        sa.Column("object_key", sa.String(length=500), nullable=False),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("local_path", sa.Text(), nullable=True),
        sa.Column("byte_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stored_artifacts")),
    )
    op.create_index(op.f("ix_stored_artifacts_scope_type"), "stored_artifacts", ["scope_type"], unique=False)
    op.create_index(op.f("ix_stored_artifacts_scope_id"), "stored_artifacts", ["scope_id"], unique=False)
    op.create_index(op.f("ix_stored_artifacts_artifact_kind"), "stored_artifacts", ["artifact_kind"], unique=False)
    op.create_index(op.f("ix_stored_artifacts_storage_provider"), "stored_artifacts", ["storage_provider"], unique=False)
    op.create_index(op.f("ix_stored_artifacts_checksum_sha256"), "stored_artifacts", ["checksum_sha256"], unique=False)
    op.create_index(op.f("ix_stored_artifacts_created_at"), "stored_artifacts", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stored_artifacts_created_at"), table_name="stored_artifacts")
    op.drop_index(op.f("ix_stored_artifacts_checksum_sha256"), table_name="stored_artifacts")
    op.drop_index(op.f("ix_stored_artifacts_storage_provider"), table_name="stored_artifacts")
    op.drop_index(op.f("ix_stored_artifacts_artifact_kind"), table_name="stored_artifacts")
    op.drop_index(op.f("ix_stored_artifacts_scope_id"), table_name="stored_artifacts")
    op.drop_index(op.f("ix_stored_artifacts_scope_type"), table_name="stored_artifacts")
    op.drop_table("stored_artifacts")