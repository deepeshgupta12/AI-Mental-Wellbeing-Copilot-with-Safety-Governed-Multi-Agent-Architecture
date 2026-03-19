from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_runtime_creates_and_lists_follow_up_plan() -> None:
    unique_email = f"followup-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Follow Up User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Stay consistent after support sessions",
                "focus_areas": "routine,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want a better routine and need something practical I can follow up on tomorrow.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        runtime_payload = runtime_response.json()

        generated_plan = runtime_payload["generated_follow_up_plan"]
        assert generated_plan is not None
        assert generated_plan["user_id"] == user_id
        assert generated_plan["plan_type"] == "plan"
        assert generated_plan["delivery_channel"] == "in_app"
        assert generated_plan["status"] == "planned"
        assert generated_plan["scheduled_for"] is not None
        assert generated_plan["scheduling_contract_json"]["contract_version"] == "v2-followup-basic"
        assert generated_plan["scheduling_contract_json"]["status"] == "planned_not_enqueued"

        list_response = client.get(f"/api/v1/follow-ups/plans?user_id={user_id}")
        assert list_response.status_code == 200
        list_payload = list_response.json()

        assert len(list_payload) >= 1
        assert list_payload[0]["id"] == generated_plan["id"]

        event_response = client.post(
            "/api/v1/follow-ups/events",
            json={
                "follow_up_plan_id": generated_plan["id"],
                "user_id": user_id,
                "event_type": "delivered",
                "outcome_status": "sent",
                "notes": "Reminder delivered in test.",
                "event_payload_json": {"channel": "in_app"},
            },
        )
        assert event_response.status_code == 200
        event_payload = event_response.json()

        assert event_payload["follow_up_plan_id"] == generated_plan["id"]
        assert event_payload["event_type"] == "delivered"
        assert event_payload["outcome_status"] == "sent"

        events_response = client.get(
            f"/api/v1/follow-ups/events?follow_up_plan_id={generated_plan['id']}"
        )
        assert events_response.status_code == 200
        events_payload = events_response.json()

        assert len(events_payload) >= 1
        assert events_payload[0]["follow_up_plan_id"] == generated_plan["id"]