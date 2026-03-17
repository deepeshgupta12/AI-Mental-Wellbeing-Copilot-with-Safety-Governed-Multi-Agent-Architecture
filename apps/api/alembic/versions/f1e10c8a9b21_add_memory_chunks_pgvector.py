"""add memory chunks pgvector

Revision ID: f1e10c8a9b21
Revises: d2fdfef5e964
Create Date: 2026-03-17 19:30:00.000000

"""
from typing import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "f1e10c8a9b21"
down_revision: str | Sequence[str] | None = "d2fdfef5e964"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "memory_chunks",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_memory_chunks_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_memory_chunks")),
    )
    op.create_index(op.f("ix_memory_chunks_user_id"), "memory_chunks", ["user_id"], unique=False)
    op.create_index(op.f("ix_memory_chunks_source_type"), "memory_chunks", ["source_type"], unique=False)
    op.create_index(op.f("ix_memory_chunks_source_id"), "memory_chunks", ["source_id"], unique=False)
    op.create_index(op.f("ix_memory_chunks_created_at"), "memory_chunks", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_memory_chunks_created_at"), table_name="memory_chunks")
    op.drop_index(op.f("ix_memory_chunks_source_id"), table_name="memory_chunks")
    op.drop_index(op.f("ix_memory_chunks_source_type"), table_name="memory_chunks")
    op.drop_index(op.f("ix_memory_chunks_user_id"), table_name="memory_chunks")
    op.drop_table("memory_chunks")