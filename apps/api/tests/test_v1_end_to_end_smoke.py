from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_v1_end_to_end_smoke() -> None:
    unique_email = f"v1-smoke-{uuid4()}@example.com"

    with TestClient(app) as client:
        root_response = client.get("/")
        assert root_response.status_code == 200

        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200

        dependencies_response = client.get("/api/v1/health/dependencies")
        assert dependencies_response.status_code == 200

        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "V1 Smoke User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Reduce overwhelm and improve consistency",
                "focus_areas": "stress,sleep",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        check_in_response = client.post(
            "/api/v1/check-ins",
            json={
                "user_id": user_id,
                "mood_score": 4,
                "stress_score": 6,
                "energy_score": 5,
                "sleep_hours": 7,
                "notes": "A little overwhelmed but stable",
            },
        )
        assert check_in_response.status_code == 200

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "Smoke reflection",
                "content": "Today felt manageable overall.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        conversation_session_response = client.post(
            "/api/v1/conversations/sessions",
            json={
                "user_id": user_id,
                "title": "Smoke conversation",
                "status": "active",
            },
        )
        assert conversation_session_response.status_code == 200
        session_id = conversation_session_response.json()["id"]

        conversation_message_response = client.post(
            "/api/v1/conversations/messages",
            json={
                "session_id": session_id,
                "role": "user",
                "content": "I feel tired after work.",
                "message_type": "text",
            },
        )
        assert conversation_message_response.status_code == 200

        action_plan_response = client.post(
            "/api/v1/action-plans",
            json={
                "user_id": user_id,
                "title": "Reset routine",
                "description": "Take a short walk and decompress",
                "timeframe": "today",
            },
        )
        assert action_plan_response.status_code == 200

        memory_response = client.get(
            f"/api/v1/memory-trends/memory-summary?user_id={user_id}"
        )
        assert memory_response.status_code == 200

        trend_response = client.get(
            f"/api/v1/memory-trends/trend-summary?user_id={user_id}"
        )
        assert trend_response.status_code == 200

        safety_eval_response = client.post(
            "/api/v1/agent-runtime/safety-evaluate",
            json={
                "user_input": "I feel stressed and mentally tired after work.",
                "provider": "mock",
            },
        )
        assert safety_eval_response.status_code == 200
        assert safety_eval_response.json()["risk_level"] == "low"

        high_risk_runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to end my life.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert high_risk_runtime_response.status_code == 200
        assert high_risk_runtime_response.json()["safety_override"] is True

        safety_flags_response = client.get(f"/api/v1/safety-flags?user_id={user_id}")
        assert safety_flags_response.status_code == 200
        assert len(safety_flags_response.json()) >= 1

        queue_response = client.get("/api/v1/safety-flags/queue")
        assert queue_response.status_code == 200

        counts_response = client.get("/api/v1/safety-flags/dashboard-counts")
        assert counts_response.status_code == 200