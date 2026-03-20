"""add v3 safety events reviews and audit logs

Revision ID: 2f1b7aa901c1
Revises: c54a6c9d2f10
Create Date: 2026-03-19 00:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "2f1b7aa901c1"
down_revision = "c54a6c9d2f10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "safety_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("safety_flag_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("risk_level", sa.String(length=30), nullable=False),
        sa.Column("queue_status", sa.String(length=50), server_default="queued", nullable=False),
        sa.Column(
            "requires_human_review",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column("escalation_channel", sa.String(length=50), nullable=True),
        sa.Column(
            "escalation_status",
            sa.String(length=50),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("event_payload_json", sa.JSON(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["conversation_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["safety_flag_id"], ["safety_flags.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_safety_events")),
    )
    op.create_index(op.f("ix_safety_events_user_id"), "safety_events", ["user_id"], unique=False)
    op.create_index(op.f("ix_safety_events_session_id"), "safety_events", ["session_id"], unique=False)
    op.create_index(op.f("ix_safety_events_safety_flag_id"), "safety_events", ["safety_flag_id"], unique=False)
    op.create_index(op.f("ix_safety_events_event_type"), "safety_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_safety_events_severity"), "safety_events", ["severity"], unique=False)
    op.create_index(op.f("ix_safety_events_risk_level"), "safety_events", ["risk_level"], unique=False)
    op.create_index(op.f("ix_safety_events_queue_status"), "safety_events", ["queue_status"], unique=False)
    op.create_index(
        op.f("ix_safety_events_requires_human_review"),
        "safety_events",
        ["requires_human_review"],
        unique=False,
    )
    op.create_index(op.f("ix_safety_events_escalation_status"), "safety_events", ["escalation_status"], unique=False)
    op.create_index(op.f("ix_safety_events_detected_at"), "safety_events", ["detected_at"], unique=False)
    op.create_index(op.f("ix_safety_events_created_at"), "safety_events", ["created_at"], unique=False)

    op.create_table(
        "safety_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("safety_event_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("safety_flag_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("reviewer_id", sa.String(length=100), nullable=True),
        sa.Column("review_status", sa.String(length=50), server_default="pending", nullable=False),
        sa.Column("resolution_type", sa.String(length=100), nullable=True),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("human_summary", sa.Text(), nullable=True),
        sa.Column("decision_rationale", sa.Text(), nullable=True),
        sa.Column("review_payload_json", sa.JSON(), nullable=True),
        sa.Column("escalation_required", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("escalation_status", sa.String(length=50), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["safety_event_id"], ["safety_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["safety_flag_id"], ["safety_flags.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["conversation_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_safety_reviews")),
    )
    op.create_index(op.f("ix_safety_reviews_safety_event_id"), "safety_reviews", ["safety_event_id"], unique=False)
    op.create_index(op.f("ix_safety_reviews_safety_flag_id"), "safety_reviews", ["safety_flag_id"], unique=False)
    op.create_index(op.f("ix_safety_reviews_user_id"), "safety_reviews", ["user_id"], unique=False)
    op.create_index(op.f("ix_safety_reviews_session_id"), "safety_reviews", ["session_id"], unique=False)
    op.create_index(op.f("ix_safety_reviews_reviewer_id"), "safety_reviews", ["reviewer_id"], unique=False)
    op.create_index(op.f("ix_safety_reviews_review_status"), "safety_reviews", ["review_status"], unique=False)
    op.create_index(op.f("ix_safety_reviews_resolution_type"), "safety_reviews", ["resolution_type"], unique=False)
    op.create_index(
        op.f("ix_safety_reviews_escalation_required"),
        "safety_reviews",
        ["escalation_required"],
        unique=False,
    )
    op.create_index(op.f("ix_safety_reviews_created_at"), "safety_reviews", ["created_at"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("safety_event_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("safety_review_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("actor_type", sa.String(length=50), nullable=False),
        sa.Column("actor_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("event_payload_json", sa.JSON(), nullable=True),
        sa.Column("is_immutable", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["session_id"], ["conversation_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["safety_event_id"], ["safety_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["safety_review_id"], ["safety_reviews.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(op.f("ix_audit_logs_event_type"), "audit_logs", ["event_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_session_id"), "audit_logs", ["session_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_safety_event_id"), "audit_logs", ["safety_event_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_safety_review_id"), "audit_logs", ["safety_review_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_actor_type"), "audit_logs", ["actor_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_actor_id"), "audit_logs", ["actor_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_is_immutable"), "audit_logs", ["is_immutable"], unique=False)
    op.create_index(op.f("ix_audit_logs_occurred_at"), "audit_logs", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_occurred_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_is_immutable"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_safety_review_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_safety_event_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_session_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_event_type"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_safety_reviews_created_at"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_escalation_required"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_resolution_type"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_review_status"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_reviewer_id"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_session_id"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_user_id"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_safety_flag_id"), table_name="safety_reviews")
    op.drop_index(op.f("ix_safety_reviews_safety_event_id"), table_name="safety_reviews")
    op.drop_table("safety_reviews")

    op.drop_index(op.f("ix_safety_events_created_at"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_detected_at"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_escalation_status"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_requires_human_review"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_queue_status"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_risk_level"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_severity"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_event_type"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_safety_flag_id"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_session_id"), table_name="safety_events")
    op.drop_index(op.f("ix_safety_events_user_id"), table_name="safety_events")
    op.drop_table("safety_events")