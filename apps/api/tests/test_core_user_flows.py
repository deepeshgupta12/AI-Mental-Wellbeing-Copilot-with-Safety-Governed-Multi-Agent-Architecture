from __future__ import annotations

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_core_user_flows() -> None:
    with TestClient(app) as client:
        create_user_response = client.post(
            "/api/v1/users",
            json={
                "email": "alex@example.com",
                "display_name": "Alex",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Sleep better and reduce overwhelm",
                "focus_areas": "stress,sleep",
            },
        )
        assert create_user_response.status_code == 200
        user_payload = create_user_response.json()
        user_id = user_payload["id"]

        check_in_response = client.post(
            "/api/v1/check-ins",
            json={
                "user_id": user_id,
                "mood_score": 3,
                "stress_score": 7,
                "energy_score": 4,
                "sleep_hours": 6,
                "notes": "Feeling low energy after work",
            },
        )
        assert check_in_response.status_code == 200

        journal_response = client.post(
            "/api/v1/journal-entries",
            json={
                "user_id": user_id,
                "title": "Evening reflection",
                "content": "Today felt heavy but manageable.",
                "entry_type": "freeform",
            },
        )
        assert journal_response.status_code == 200

        session_response = client.post(
            "/api/v1/conversations/sessions",
            json={
                "user_id": user_id,
                "title": "Stress conversation",
                "status": "active",
            },
        )
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]

        message_response = client.post(
            "/api/v1/conversations/messages",
            json={
                "session_id": session_id,
                "role": "user",
                "content": "I feel stressed every evening.",
                "message_type": "text",
            },
        )
        assert message_response.status_code == 200

        action_plan_response = client.post(
            "/api/v1/action-plans",
            json={
                "user_id": user_id,
                "title": "Evening reset",
                "description": "Take a short walk and journal",
                "timeframe": "today",
            },
        )
        assert action_plan_response.status_code == 200

        list_check_ins_response = client.get(f"/api/v1/check-ins?user_id={user_id}")
        assert list_check_ins_response.status_code == 200
        assert len(list_check_ins_response.json()) == 1

        list_journal_response = client.get(f"/api/v1/journal-entries?user_id={user_id}")
        assert list_journal_response.status_code == 200
        assert len(list_journal_response.json()) == 1

        list_sessions_response = client.get(f"/api/v1/conversations/sessions?user_id={user_id}")
        assert list_sessions_response.status_code == 200
        assert len(list_sessions_response.json()) == 1

        list_messages_response = client.get(f"/api/v1/conversations/messages?session_id={session_id}")
        assert list_messages_response.status_code == 200
        assert len(list_messages_response.json()) == 1

        list_action_plans_response = client.get(f"/api/v1/action-plans?user_id={user_id}")
        assert list_action_plans_response.status_code == 200
        assert len(list_action_plans_response.json()) == 1

        get_user_response = client.get(f"/api/v1/users/{user_id}")
        assert get_user_response.status_code == 200
        assert get_user_response.json()["email"] == "alex@example.com"