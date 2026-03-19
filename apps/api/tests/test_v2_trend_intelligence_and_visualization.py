from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_trend_intelligence_surfaces_user_and_admin_trends() -> None:
    unique_email = f"trend-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Trend User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Understand progress over time",
                "focus_areas": "stress,sleep,routine",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        journal_response_1 = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "After work reflection",
                "content": "I felt overwhelmed after work and a short walk helped me reset.",
                "entry_type": "freeform",
            },
        )
        assert journal_response_1.status_code == 200

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

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel overwhelmed after work and need support that helps me see patterns.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        runtime_payload = runtime_response.json()

        assert "trend_summary" in runtime_payload
        assert "support_progress_summary" in runtime_payload
        assert "recurring_patterns" in runtime_payload
        assert "intervention_effectiveness" in runtime_payload

        trend_response = client.get(f"/api/v1/memory-trends/trend-summary?user_id={user_id}")
        assert trend_response.status_code == 200
        trend_payload = trend_response.json()

        assert trend_payload["user_id"] == user_id
        assert "support_progress_summary" in trend_payload
        assert "recurring_patterns" in trend_payload
        assert "intervention_effectiveness" in trend_payload
        assert "trend_visualization" in trend_payload

        admin_response = client.get("/api/v1/admin/trend-overview")
        assert admin_response.status_code == 200
        admin_payload = admin_response.json()

        assert "total_users_with_snapshots" in admin_payload
        assert "recent_snapshot_count" in admin_payload
        assert "weekly_reflection_snapshot_count" in admin_payload
        assert "top_recurring_patterns" in admin_payload
        assert "intervention_effectiveness_summary" in admin_payload
        assert "recent_support_progress_summaries" in admin_payload