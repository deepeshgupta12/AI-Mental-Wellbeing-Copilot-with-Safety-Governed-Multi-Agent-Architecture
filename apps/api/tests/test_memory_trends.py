from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_memory_and_trend_basics() -> None:
    unique_email = f"memory-{uuid4()}@example.com"

    with TestClient(app) as client:
        create_user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Memory User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Reduce stress and improve sleep",
                "focus_areas": "stress,sleep",
            },
        )
        assert create_user_response.status_code == 200
        user_id = create_user_response.json()["id"]

        check_in_response = client.post(
            "/api/v1/check-ins",
            json={
                "user_id": user_id,
                "mood_score": 4,
                "stress_score": 6,
                "energy_score": 5,
                "sleep_hours": 7,
                "notes": "A bit tired but doing okay",
            },
        )
        assert check_in_response.status_code == 200

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "Short reflection",
                "content": "Work was intense today but I handled it better than usual after work.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        session_response = client.post(
            "/api/v1/conversations/sessions",
            json={
                "user_id": user_id,
                "title": "Evening support",
                "status": "active",
            },
        )
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]

        message_response = client.post(
            "/api/v1/conversations/messages",
            json={
                "session_id": session_id,
                "role": "user",
                "content": "I feel mentally tired after work.",
                "message_type": "text",
            },
        )
        assert message_response.status_code == 200

        memory_response = client.get(
            f"/api/v1/memory-trends/memory-summary?user_id={user_id}"
        )
        assert memory_response.status_code == 200
        memory_payload = memory_response.json()
        assert memory_payload["user_id"] == user_id
        assert len(memory_payload["recent_memories"]) >= 3
        assert "helpful_before" in memory_payload
        assert "recurring_triggers" in memory_payload
        assert "preference_signals" in memory_payload
        assert "weekly_reflection_summary" in memory_payload
        assert "recent_journal_themes" in memory_payload
        assert memory_payload["preference_signals"]["support_style"] == "calm"
        assert any("memory_kind" in item for item in memory_payload["recent_memories"])

        trend_response = client.get(
            f"/api/v1/memory-trends/trend-summary?user_id={user_id}"
        )
        assert trend_response.status_code == 200
        trend_payload = trend_response.json()
        assert trend_payload["user_id"] == user_id
        assert trend_payload["total_check_ins"] == 1
        assert trend_payload["total_journal_entries"] == 1
        assert trend_payload["total_conversation_sessions"] == 1
        assert trend_payload["total_conversation_messages"] == 1
        assert "latest_snapshot_window_type" in trend_payload
        assert "latest_snapshot_created_at" in trend_payload
        assert "top_journal_themes" in trend_payload
        assert "recurring_trigger_count" in trend_payload
        assert "support_progress_summary" in trend_payload
        assert "recurring_patterns" in trend_payload
        assert "intervention_effectiveness" in trend_payload
        assert "trend_visualization" in trend_payload