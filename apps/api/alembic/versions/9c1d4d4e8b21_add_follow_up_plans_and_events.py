"""add follow up plans and events

Revision ID: 9c1d4d4e8b21
Revises: 4b7d9d6e2c11
Create Date: 2026-03-19 16:10:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "9c1d4d4e8b21"
down_revision = "4b7d9d6e2c11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "follow_up_plans",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("action_plan_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("source_agent", sa.String(length=100), nullable=False),
        sa.Column("plan_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="planned",
        ),
        sa.Column(
            "delivery_channel",
            sa.String(length=50),
            nullable=False,
            server_default="in_app",
        ),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=True),
        sa.Column("cadence_json", sa.JSON(), nullable=True),
        sa.Column("scheduling_contract_json", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["action_plan_id"], ["action_plans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["session_id"], ["conversation_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_follow_up_plans_user_id"),
        "follow_up_plans",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_session_id"),
        "follow_up_plans",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_action_plan_id"),
        "follow_up_plans",
        ["action_plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_source_agent"),
        "follow_up_plans",
        ["source_agent"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_plan_type"),
        "follow_up_plans",
        ["plan_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_status"),
        "follow_up_plans",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_delivery_channel"),
        "follow_up_plans",
        ["delivery_channel"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_scheduled_for"),
        "follow_up_plans",
        ["scheduled_for"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_plans_created_at"),
        "follow_up_plans",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "follow_up_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("follow_up_plan_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("outcome_status", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("event_payload_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["follow_up_plan_id"],
            ["follow_up_plans.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_follow_up_events_follow_up_plan_id"),
        "follow_up_events",
        ["follow_up_plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_events_user_id"),
        "follow_up_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_events_event_type"),
        "follow_up_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_events_outcome_status"),
        "follow_up_events",
        ["outcome_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_events_created_at"),
        "follow_up_events",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_follow_up_events_created_at"), table_name="follow_up_events")
    op.drop_index(op.f("ix_follow_up_events_outcome_status"), table_name="follow_up_events")
    op.drop_index(op.f("ix_follow_up_events_event_type"), table_name="follow_up_events")
    op.drop_index(op.f("ix_follow_up_events_user_id"), table_name="follow_up_events")
    op.drop_index(op.f("ix_follow_up_events_follow_up_plan_id"), table_name="follow_up_events")
    op.drop_table("follow_up_events")

    op.drop_index(op.f("ix_follow_up_plans_created_at"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_scheduled_for"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_delivery_channel"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_status"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_plan_type"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_source_agent"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_action_plan_id"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_session_id"), table_name="follow_up_plans")
    op.drop_index(op.f("ix_follow_up_plans_user_id"), table_name="follow_up_plans")
    op.drop_table("follow_up_plans")