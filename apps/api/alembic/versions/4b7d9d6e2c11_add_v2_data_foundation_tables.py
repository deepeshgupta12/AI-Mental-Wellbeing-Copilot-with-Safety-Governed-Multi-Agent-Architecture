"""add v2 data foundation tables

Revision ID: 4b7d9d6e2c11
Revises: f1e10c8a9b21
Create Date: 2026-03-18 14:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4b7d9d6e2c11"
down_revision: str | Sequence[str] | None = "f1e10c8a9b21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("preferred_support_mode", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("preference_profile_json", sa.JSON(), nullable=True),
    )

    op.add_column(
        "journal_entries",
        sa.Column("summary", sa.Text(), nullable=True),
    )
    op.add_column(
        "journal_entries",
        sa.Column("emotional_tone", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "journal_entries",
        sa.Column("structured_insights_json", sa.JSON(), nullable=True),
    )

    op.add_column(
        "conversation_sessions",
        sa.Column("support_mode", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "conversation_sessions",
        sa.Column("resolved_mode", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "conversation_sessions",
        sa.Column("session_summary", sa.Text(), nullable=True),
    )

    op.add_column(
        "action_plans",
        sa.Column("plan_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "action_plans",
        sa.Column("source", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "action_plans",
        sa.Column("recommendation_context_json", sa.JSON(), nullable=True),
    )

    op.add_column(
        "memory_chunks",
        sa.Column(
            "memory_kind",
            sa.String(length=50),
            nullable=False,
            server_default="episodic",
        ),
    )
    op.add_column(
        "memory_chunks",
        sa.Column("importance_score", sa.Float(), nullable=True),
    )
    op.create_index(
        op.f("ix_memory_chunks_memory_kind"),
        "memory_chunks",
        ["memory_kind"],
        unique=False,
    )
    op.alter_column("memory_chunks", "memory_kind", server_default=None)

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("preference_key", sa.String(length=100), nullable=False),
        sa.Column("preference_value_json", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_preferences_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_preferences")),
    )
    op.create_index(op.f("ix_user_preferences_user_id"), "user_preferences", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_preferences_preference_key"), "user_preferences", ["preference_key"], unique=False)
    op.create_index(op.f("ix_user_preferences_created_at"), "user_preferences", ["created_at"], unique=False)

    op.create_table(
        "agent_traces",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("session_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("message_id", sa.String(length=64), nullable=True),
        sa.Column("trace_name", sa.String(length=100), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("handoff_from_agent", sa.String(length=100), nullable=True),
        sa.Column("handoff_to_agent", sa.String(length=100), nullable=True),
        sa.Column("input_payload_json", sa.JSON(), nullable=True),
        sa.Column("output_payload_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_agent_traces_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["conversation_sessions.id"],
            name=op.f("fk_agent_traces_session_id_conversation_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_traces")),
    )
    op.create_index(op.f("ix_agent_traces_user_id"), "agent_traces", ["user_id"], unique=False)
    op.create_index(op.f("ix_agent_traces_session_id"), "agent_traces", ["session_id"], unique=False)
    op.create_index(op.f("ix_agent_traces_message_id"), "agent_traces", ["message_id"], unique=False)
    op.create_index(op.f("ix_agent_traces_trace_name"), "agent_traces", ["trace_name"], unique=False)
    op.create_index(op.f("ix_agent_traces_agent_name"), "agent_traces", ["agent_name"], unique=False)
    op.create_index(op.f("ix_agent_traces_created_at"), "agent_traces", ["created_at"], unique=False)

    op.create_table(
        "trend_snapshots",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("window_type", sa.String(length=50), nullable=False),
        sa.Column("snapshot_start_date", sa.Date(), nullable=False),
        sa.Column("snapshot_end_date", sa.Date(), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_trend_snapshots_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trend_snapshots")),
    )
    op.create_index(op.f("ix_trend_snapshots_user_id"), "trend_snapshots", ["user_id"], unique=False)
    op.create_index(op.f("ix_trend_snapshots_window_type"), "trend_snapshots", ["window_type"], unique=False)
    op.create_index(op.f("ix_trend_snapshots_created_at"), "trend_snapshots", ["created_at"], unique=False)

    op.create_table(
        "intervention_logs",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("action_plan_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("intervention_type", sa.String(length=100), nullable=False),
        sa.Column("recommendation_text", sa.Text(), nullable=True),
        sa.Column("outcome_status", sa.String(length=50), nullable=True),
        sa.Column("effectiveness_rating", sa.Float(), nullable=True),
        sa.Column("feedback_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_intervention_logs_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["conversation_sessions.id"],
            name=op.f("fk_intervention_logs_session_id_conversation_sessions"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["action_plan_id"],
            ["action_plans.id"],
            name=op.f("fk_intervention_logs_action_plan_id_action_plans"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_intervention_logs")),
    )
    op.create_index(op.f("ix_intervention_logs_user_id"), "intervention_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_intervention_logs_session_id"), "intervention_logs", ["session_id"], unique=False)
    op.create_index(op.f("ix_intervention_logs_action_plan_id"), "intervention_logs", ["action_plan_id"], unique=False)
    op.create_index(op.f("ix_intervention_logs_intervention_type"), "intervention_logs", ["intervention_type"], unique=False)
    op.create_index(op.f("ix_intervention_logs_created_at"), "intervention_logs", ["created_at"], unique=False)

    op.create_table(
        "journal_themes",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("journal_entry_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("theme_name", sa.String(length=100), nullable=False),
        sa.Column("sentiment", sa.String(length=50), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            ["journal_entries.id"],
            name=op.f("fk_journal_themes_journal_entry_id_journal_entries"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_journal_themes_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_journal_themes")),
    )
    op.create_index(op.f("ix_journal_themes_journal_entry_id"), "journal_themes", ["journal_entry_id"], unique=False)
    op.create_index(op.f("ix_journal_themes_user_id"), "journal_themes", ["user_id"], unique=False)
    op.create_index(op.f("ix_journal_themes_theme_name"), "journal_themes", ["theme_name"], unique=False)
    op.create_index(op.f("ix_journal_themes_created_at"), "journal_themes", ["created_at"], unique=False)

    op.create_table(
        "trigger_clusters",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("cluster_name", sa.String(length=120), nullable=False),
        sa.Column("trigger_text", sa.Text(), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_trigger_clusters_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trigger_clusters")),
    )
    op.create_index(op.f("ix_trigger_clusters_user_id"), "trigger_clusters", ["user_id"], unique=False)
    op.create_index(op.f("ix_trigger_clusters_cluster_name"), "trigger_clusters", ["cluster_name"], unique=False)
    op.create_index(op.f("ix_trigger_clusters_created_at"), "trigger_clusters", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trigger_clusters_created_at"), table_name="trigger_clusters")
    op.drop_index(op.f("ix_trigger_clusters_cluster_name"), table_name="trigger_clusters")
    op.drop_index(op.f("ix_trigger_clusters_user_id"), table_name="trigger_clusters")
    op.drop_table("trigger_clusters")

    op.drop_index(op.f("ix_journal_themes_created_at"), table_name="journal_themes")
    op.drop_index(op.f("ix_journal_themes_theme_name"), table_name="journal_themes")
    op.drop_index(op.f("ix_journal_themes_user_id"), table_name="journal_themes")
    op.drop_index(op.f("ix_journal_themes_journal_entry_id"), table_name="journal_themes")
    op.drop_table("journal_themes")

    op.drop_index(op.f("ix_intervention_logs_created_at"), table_name="intervention_logs")
    op.drop_index(op.f("ix_intervention_logs_intervention_type"), table_name="intervention_logs")
    op.drop_index(op.f("ix_intervention_logs_action_plan_id"), table_name="intervention_logs")
    op.drop_index(op.f("ix_intervention_logs_session_id"), table_name="intervention_logs")
    op.drop_index(op.f("ix_intervention_logs_user_id"), table_name="intervention_logs")
    op.drop_table("intervention_logs")

    op.drop_index(op.f("ix_trend_snapshots_created_at"), table_name="trend_snapshots")
    op.drop_index(op.f("ix_trend_snapshots_window_type"), table_name="trend_snapshots")
    op.drop_index(op.f("ix_trend_snapshots_user_id"), table_name="trend_snapshots")
    op.drop_table("trend_snapshots")

    op.drop_index(op.f("ix_agent_traces_created_at"), table_name="agent_traces")
    op.drop_index(op.f("ix_agent_traces_agent_name"), table_name="agent_traces")
    op.drop_index(op.f("ix_agent_traces_trace_name"), table_name="agent_traces")
    op.drop_index(op.f("ix_agent_traces_message_id"), table_name="agent_traces")
    op.drop_index(op.f("ix_agent_traces_session_id"), table_name="agent_traces")
    op.drop_index(op.f("ix_agent_traces_user_id"), table_name="agent_traces")
    op.drop_table("agent_traces")

    op.drop_index(op.f("ix_user_preferences_created_at"), table_name="user_preferences")
    op.drop_index(op.f("ix_user_preferences_preference_key"), table_name="user_preferences")
    op.drop_index(op.f("ix_user_preferences_user_id"), table_name="user_preferences")
    op.drop_table("user_preferences")

    op.drop_index(op.f("ix_memory_chunks_memory_kind"), table_name="memory_chunks")
    op.drop_column("memory_chunks", "importance_score")
    op.drop_column("memory_chunks", "memory_kind")

    op.drop_column("action_plans", "recommendation_context_json")
    op.drop_column("action_plans", "source")
    op.drop_column("action_plans", "plan_type")

    op.drop_column("conversation_sessions", "session_summary")
    op.drop_column("conversation_sessions", "resolved_mode")
    op.drop_column("conversation_sessions", "support_mode")

    op.drop_column("journal_entries", "structured_insights_json")
    op.drop_column("journal_entries", "emotional_tone")
    op.drop_column("journal_entries", "summary")

    op.drop_column("user_profiles", "preference_profile_json")
    op.drop_column("user_profiles", "preferred_support_mode")