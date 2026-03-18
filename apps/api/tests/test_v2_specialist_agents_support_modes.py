from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_sleep_recovery_specialist_path() -> None:
    unique_email = f"sleep-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Sleep User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Sleep better",
                "focus_areas": "sleep,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "My sleep has been terrible and I keep waking up at night.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["intent_label"] == "sleep_recovery"
        assert payload["specialist_agent"] == "sleep_recovery"
        assert payload["support_mode"] == "recover"
        assert "sleep_recovery" in payload["execution_path"]


def test_social_support_specialist_path() -> None:
    unique_email = f"social-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Social User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Feel less alone",
                "focus_areas": "loneliness,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel lonely and isolated and I do not know who to talk to.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["intent_label"] == "social_support"
        assert payload["specialist_agent"] == "social_support"
        assert payload["support_mode"] == "connect"
        assert "social_support" in payload["execution_path"]


def test_cbt_reframing_specialist_path() -> None:
    unique_email = f"cbt-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "CBT User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Challenge harsh thoughts",
                "focus_areas": "stress,self-talk",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I always ruin everything and I feel like a failure.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["intent_label"] == "cognitive_reframing"
        assert payload["specialist_agent"] == "cbt_reframing"
        assert payload["support_mode"] == "reframe"
        assert "cbt_reframing" in payload["execution_path"]


def test_journaling_insight_specialist_path() -> None:
    unique_email = f"journal-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Journal User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Reflect better",
                "focus_areas": "journaling,clarity",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want help reflecting on what I wrote in my journal today.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["intent_label"] == "journaling_insight"
        assert payload["specialist_agent"] == "journaling_insight"
        assert payload["support_mode"] == "reflect"
        assert "journaling_insight" in payload["execution_path"]


def test_habit_care_plan_specialist_path() -> None:
    unique_email = f"habit-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Habit User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Build consistency",
                "focus_areas": "habits,routine",
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
        payload = runtime_response.json()

        assert payload["intent_label"] == "habit_support"
        assert payload["specialist_agent"] == "habit_care_plan"
        assert payload["support_mode"] == "plan"
        assert "habit_care_plan" in payload["execution_path"]