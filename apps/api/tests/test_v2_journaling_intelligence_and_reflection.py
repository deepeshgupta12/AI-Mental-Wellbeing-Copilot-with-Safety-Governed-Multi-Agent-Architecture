from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_journaling_intelligence_enriches_entry_and_weekly_reflection() -> None:
    unique_email = f"journal-v2-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Journal V2 User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Understand patterns better",
                "focus_areas": "journaling,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        journal_response_1 = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "After work entry",
                "content": "I felt overwhelmed after work. A short walk helped me reset.",
                "entry_type": "freeform",
            },
        )
        assert journal_response_1.status_code == 200
        journal_payload_1 = journal_response_1.json()
        assert journal_payload_1["summary"] is not None
        assert journal_payload_1["emotional_tone"] is not None
        assert journal_payload_1["structured_insights_json"] is not None
        assert "detected_themes" in journal_payload_1["structured_insights_json"]

        journal_response_2 = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "Night reflection",
                "content": "Before sleep I keep replaying work conversations and feeling heavy.",
                "entry_type": "freeform",
            },
        )
        assert journal_response_2.status_code == 200

        memory_response = client.get(
            f"/api/v1/memory-trends/memory-summary?user_id={user_id}"
        )
        assert memory_response.status_code == 200
        memory_payload = memory_response.json()

        assert memory_payload["user_id"] == user_id
        assert memory_payload["weekly_reflection_summary"] is not None
        assert len(memory_payload["recent_journal_themes"]) >= 1
        assert len(memory_payload["recurring_triggers"]) >= 1

        trend_response = client.get(
            f"/api/v1/memory-trends/trend-summary?user_id={user_id}"
        )
        assert trend_response.status_code == 200
        trend_payload = trend_response.json()

        assert trend_payload["latest_snapshot_window_type"] == "weekly_reflection"
        assert trend_payload["latest_snapshot_created_at"] is not None
        assert len(trend_payload["top_journal_themes"]) >= 1
        assert trend_payload["recurring_trigger_count"] >= 1