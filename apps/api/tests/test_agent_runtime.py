from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_agent_runtime_smoke() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/agent-runtime/smoke",
        json={
            "user_input": "I feel overwhelmed and tired after work every day.",
            "provider": "mock",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "mock"
    assert "structured_input" in payload
    assert "reflective_response" in payload
    assert "final_response" in payload
    assert "memory_hits" in payload
    assert "preference_signals" in payload
    assert "what_helped_before" in payload
    assert "execution_path" in payload
    assert "node_trace" in payload
    assert "handoff_history" in payload
    assert "routing_contract" in payload
    assert "trend_summary" in payload
    assert "support_progress_summary" in payload
    assert "recurring_patterns" in payload
    assert "intervention_effectiveness" in payload


def test_agent_runtime_returns_memory_hits_and_preferences_for_known_user() -> None:
    unique_email = f"runtime-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Runtime User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Reduce stress and sleep better",
                "focus_areas": "stress,sleep",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "After work reflection",
                "content": "I feel overwhelmed after work and a short walk helped a little.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel overwhelmed after work again.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["status"] == "ok"
        assert payload["support_strategy"] is not None
        assert payload["intent_label"] is not None
        assert payload["specialist_agent"] is not None
        assert payload["preference_signals"]["support_style"] in {"reflective", "direct", "calm"}
        assert len(payload["memory_hits"]) >= 1
        assert len(payload["execution_path"]) >= 4
        assert len(payload["node_trace"]) >= 4
        assert len(payload["handoff_history"]) >= 3
        assert payload["memory_hits"][0]["memory_kind"] in {
            "episodic",
            "helpful_strategy",
            "preference",
            "semantic",
        }
        assert "trend_summary" in payload
        assert "support_progress_summary" in payload
        assert "recurring_patterns" in payload
        assert "intervention_effectiveness" in payload