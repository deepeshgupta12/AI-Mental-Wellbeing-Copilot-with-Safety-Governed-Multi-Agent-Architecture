from mental_wellbeing_api.db import models as _models  # noqa: F401
from mental_wellbeing_api.db.base import Base


def test_v2_tables_are_registered() -> None:
    expected_tables = {
        "users",
        "user_profiles",
        "user_preferences",
        "check_ins",
        "journal_entries",
        "journal_themes",
        "conversation_sessions",
        "conversation_messages",
        "action_plans",
        "safety_flags",
        "memory_chunks",
        "agent_traces",
        "trend_snapshots",
        "intervention_logs",
        "trigger_clusters",
    }

    assert expected_tables.issubset(set(Base.metadata.tables.keys()))


def test_v2_columns_exist_on_expanded_tables() -> None:
    journal_entries = Base.metadata.tables["journal_entries"]
    conversation_sessions = Base.metadata.tables["conversation_sessions"]
    action_plans = Base.metadata.tables["action_plans"]
    memory_chunks = Base.metadata.tables["memory_chunks"]
    user_profiles = Base.metadata.tables["user_profiles"]

    assert "summary" in journal_entries.c
    assert "emotional_tone" in journal_entries.c
    assert "structured_insights_json" in journal_entries.c

    assert "support_mode" in conversation_sessions.c
    assert "resolved_mode" in conversation_sessions.c
    assert "session_summary" in conversation_sessions.c

    assert "plan_type" in action_plans.c
    assert "source" in action_plans.c
    assert "recommendation_context_json" in action_plans.c

    assert "memory_kind" in memory_chunks.c
    assert "importance_score" in memory_chunks.c

    assert "preferred_support_mode" in user_profiles.c
    assert "preference_profile_json" in user_profiles.c