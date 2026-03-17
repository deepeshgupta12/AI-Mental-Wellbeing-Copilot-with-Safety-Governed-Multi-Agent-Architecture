from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_validation_handler_returns_consistent_shape() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/conversations/sessions",
            json={
                "user_id": "bad-id",
                "title": "Invalid request",
                "status": "active",
            },
        )

        assert response.status_code == 422
        payload = response.json()
        assert payload["detail"] == "Validation failed"
        assert "errors" in payload


def test_foreign_key_routes_return_404_instead_of_db_errors() -> None:
    missing_user_id = str(uuid4())
    missing_session_id = str(uuid4())

    with TestClient(app) as client:
        check_in_response = client.post(
            "/api/v1/check-ins",
            json={
                "user_id": missing_user_id,
                "mood_score": 5,
            },
        )
        assert check_in_response.status_code == 404
        assert check_in_response.json()["detail"] == "User not found"

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": missing_user_id,
                "content": "Test entry",
            },
        )
        assert journal_response.status_code == 404
        assert journal_response.json()["detail"] == "User not found"

        action_plan_response = client.post(
            "/api/v1/action-plans",
            json={
                "user_id": missing_user_id,
                "title": "Test plan",
            },
        )
        assert action_plan_response.status_code == 404
        assert action_plan_response.json()["detail"] == "User not found"

        message_response = client.post(
            "/api/v1/conversations/messages",
            json={
                "session_id": missing_session_id,
                "role": "user",
                "content": "Hello",
                "message_type": "text",
            },
        )
        assert message_response.status_code == 404
        assert message_response.json()["detail"] == "Conversation session not found"

        safety_flag_response = client.post(
            "/api/v1/safety-flags",
            json={
                "user_id": missing_user_id,
                "severity": "high",
                "flag_type": "self_harm",
                "summary": "Test",
            },
        )
        assert safety_flag_response.status_code == 404
        assert safety_flag_response.json()["detail"] == "User not found"