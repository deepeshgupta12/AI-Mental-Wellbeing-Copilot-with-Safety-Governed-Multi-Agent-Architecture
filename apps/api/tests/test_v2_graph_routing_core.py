from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_medium_risk_routes_to_distress_stabilization_with_traceable_handoffs() -> None:
    unique_email = f"routing-medium-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Routing Medium User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Reduce panic and overwhelm",
                "focus_areas": "stress,safety",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I think I am having a panic attack and I can't breathe.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["risk_level"] == "medium"
        assert payload["support_strategy"] == "distress_stabilization"
        assert payload["specialist_agent"] == "distress_stabilization"
        assert "distress_stabilization" in payload["execution_path"]
        assert any(
            item["to_agent"] == "distress_stabilization"
            for item in payload["handoff_history"]
        )


def test_low_risk_behavioral_activation_path_is_traceable() -> None:
    unique_email = f"routing-ba-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Routing BA User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Get unstuck after work",
                "focus_areas": "stress,motivation",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel stuck, exhausted, and can't start anything after work.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["risk_level"] == "low"
        assert payload["support_strategy"] == "behavioral_activation"
        assert payload["specialist_agent"] == "behavioral_activation"
        assert payload["routing_contract"]["contract_name"] == "v2-routing-core"
        assert "behavioral_activation" in payload["execution_path"]
        assert payload["execution_summary"] is not None