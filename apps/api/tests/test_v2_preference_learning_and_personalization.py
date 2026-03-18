from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_preference_learning_updates_profile_and_response_style() -> None:
    unique_email = f"prefs-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Preference User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Be more consistent",
                "focus_areas": "routine,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want a better routine and more consistency with self-care habits.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        runtime_payload = runtime_response.json()

        assert runtime_payload["support_mode"] == "plan"
        assert runtime_payload["specialist_agent"] == "habit_care_plan"
        assert runtime_payload["preference_signals"]["preferred_support_mode"] == "plan"
        assert runtime_payload["preference_signals"]["support_style"] == "direct"
        assert "Let's make this concrete." in runtime_payload["final_response"]

        get_user_response = client.get(f"/api/v1/users/{user_id}")
        assert get_user_response.status_code == 200
        profile_payload = get_user_response.json()["profile"]

        assert profile_payload["support_style"] == "direct"
        assert profile_payload["preferred_support_mode"] == "plan"


def test_preference_aware_memory_ranking_preserves_helpful_before() -> None:
    unique_email = f"prefs-memory-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Memory Preference User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Reduce overwhelm",
                "focus_areas": "stress,routine",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "Reset note",
                "content": "After work, a short walk helped before and made things feel more manageable.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel overwhelmed after work and need something practical.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["preference_signals"]["support_style"] == "direct"
        assert len(payload["what_helped_before"]) >= 1
        assert any("helped" in item.lower() for item in payload["what_helped_before"])
        assert len(payload["memory_hits"]) >= 1