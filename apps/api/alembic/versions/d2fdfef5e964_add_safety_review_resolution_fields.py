"""add safety review resolution fields

Revision ID: d2fdfef5e964
Revises: c10c1d80beab
Create Date: 2026-03-17 16:35:41.577764

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d2fdfef5e964"
down_revision: str | Sequence[str] | None = "c10c1d80beab"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "safety_flags",
        sa.Column(
            "is_resolved",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "safety_flags",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "safety_flags",
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "safety_flags",
        sa.Column("reviewer_note", sa.Text(), nullable=True),
    )
    op.alter_column("safety_flags", "is_resolved", server_default=None)


def downgrade() -> None:
    op.drop_column("safety_flags", "reviewer_note")
    op.drop_column("safety_flags", "resolved_at")
    op.drop_column("safety_flags", "reviewed_at")
    op.drop_column("safety_flags", "is_resolved")