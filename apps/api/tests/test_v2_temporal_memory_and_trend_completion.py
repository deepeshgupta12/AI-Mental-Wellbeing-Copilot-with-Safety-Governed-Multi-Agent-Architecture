from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_v2_temporal_memory_and_trend_closure() -> None:
    unique_email = f"v2-closure-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "V2 Closure User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Improve routine and track patterns",
                "focus_areas": "stress,sleep,routine",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "After work pattern",
                "content": "I feel overwhelmed after work and a short walk helped before.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel overwhelmed after work and want something practical tomorrow.",
                "provider": "mock",
                "user_id": user_id,
                "support_track": "stress_overwhelm",
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["follow_up_required"] is True
        assert payload["generated_follow_up_plan"] is not None
        assert payload["scheduler_backend"] is not None
        assert payload["temporal_contract"]
        assert payload["follow_up_contract"]

        trend_response = client.get(f"/api/v1/memory-trends/trend-summary?user_id={user_id}")
        assert trend_response.status_code == 200
        trend_payload = trend_response.json()

        assert "trend_series" in trend_payload
        assert "mood_series" in trend_payload["trend_series"]
        assert "trigger_frequency" in trend_payload["trend_series"]

        tracks_response = client.get("/api/v1/support-tracks")
        assert tracks_response.status_code == 200
        assert len(tracks_response.json()) >= 3