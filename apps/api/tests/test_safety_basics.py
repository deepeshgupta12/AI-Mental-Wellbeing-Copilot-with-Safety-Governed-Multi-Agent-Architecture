from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_safety_evaluation_endpoint_low_risk() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/agent-runtime/safety-evaluate",
            json={
                "user_input": "I feel stressed and mentally tired after work.",
                "provider": "mock",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["risk_level"] == "low"
        assert payload["safety_override"] is False
        assert payload["requires_human_review"] is False
        assert payload["escalation_recommended"] is False


def test_safety_evaluation_endpoint_high_risk() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/agent-runtime/safety-evaluate",
            json={
                "user_input": "I want to kill myself tonight.",
                "provider": "mock",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["risk_level"] == "high"
        assert payload["safety_override"] is True
        assert payload["safety_flag_type"] == "self_harm"
        assert payload["requires_human_review"] is True
        assert payload["escalation_recommended"] is True
        assert payload["queue_status"] == "queued"


def test_agent_runtime_high_risk_creates_safety_flag() -> None:
    unique_email = f"safety-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Safety User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Feel safer and more stable",
                "focus_areas": "stress,safety",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to end my life.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        runtime_payload = runtime_response.json()
        assert runtime_payload["risk_level"] == "high"
        assert runtime_payload["safety_override"] is True
        assert runtime_payload["safety_flag_type"] == "self_harm"
        assert runtime_payload["requires_human_review"] is True
        assert runtime_payload["review_recommended"] is True
        assert runtime_payload["decision_path_label"] == "crisis_escalation"
        assert runtime_payload["human_summary"] is not None
        assert runtime_payload["evidence_bundle"]
        assert runtime_payload["audit_snapshot"]

        flags_response = client.get(f"/api/v1/safety-flags?user_id={user_id}")
        assert flags_response.status_code == 200
        flags_payload = flags_response.json()
        assert len(flags_payload) == 1
        assert flags_payload[0]["flag_type"] == "self_harm"
        assert flags_payload[0]["severity"] == "high"

        safety_events_response = client.get("/api/v1/admin/safety-events")
        assert safety_events_response.status_code == 200
        safety_events_payload = safety_events_response.json()
        assert any(item["user_id"] == user_id for item in safety_events_payload)