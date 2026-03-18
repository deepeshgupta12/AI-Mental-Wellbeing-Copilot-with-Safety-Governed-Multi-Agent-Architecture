from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_memory_retrieval_ranks_and_returns_contextual_hits() -> None:
    unique_email = f"retrieval-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Retrieval User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Reduce overwhelm",
                "focus_areas": "stress,burnout",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "Overwhelm pattern",
                "content": "I get overwhelmed after work and a short walk helped me reset.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel overwhelmed after work.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["preference_signals"]["support_style"] == "direct"
        assert len(payload["memory_hits"]) >= 1
        assert any("overwhelmed" in item["content"].lower() for item in payload["memory_hits"])
        assert "session_context" in payload
        assert payload["session_context"]