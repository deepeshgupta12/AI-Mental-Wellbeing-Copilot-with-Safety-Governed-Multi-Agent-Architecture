from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_runtime_creates_lists_completes_and_cancels_follow_up_plan() -> None:
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

        assert runtime_payload["follow_up_required"] is True
        assert runtime_payload["follow_up_plan_id"] == generated_plan["id"]
        assert runtime_payload["follow_up_contract"]
        assert runtime_payload["temporal_contract"]
        assert runtime_payload["scheduler_backend"] is not None
        assert runtime_payload["follow_up_contract"]["contract_version"] == "v2-followup-basic"
        assert runtime_payload["follow_up_contract"]["status"] == "planned_not_enqueued"
        assert runtime_payload["scheduler_backend"] in {
            "local-contract",
            "local_contract",
            "placeholder",
        }

        assert runtime_payload["temporal_contract"]["workflow_name"] is not None
        assert runtime_payload["temporal_contract"]["task_queue"] is not None
        assert runtime_payload["temporal_contract"]["idempotency_key"] is not None
        assert len(runtime_payload["follow_up_event_ids"]) >= 1

        get_plan_response = client.get(f"/api/v1/follow-ups/plans/{generated_plan['id']}")
        assert get_plan_response.status_code == 200
        assert get_plan_response.json()["id"] == generated_plan["id"]

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

        complete_response = client.post(
            f"/api/v1/follow-ups/plans/{generated_plan['id']}/complete",
            json={
                "notes": "User completed the follow up.",
                "outcome_status": "completed",
            },
        )
        assert complete_response.status_code == 200
        complete_payload = complete_response.json()
        assert complete_payload["status"] == "completed"

        cancel_plan_response = client.post(
            "/api/v1/follow-ups/plans",
            json={
                "user_id": user_id,
                "source_agent": "habit_care_plan",
                "plan_type": "plan",
                "title": "Second follow up",
                "description": "Cancel this one in test.",
                "delivery_channel": "in_app",
                "timezone": "Asia/Kolkata",
                "metadata_json": {
                    "support_mode": "plan",
                    "support_strategy": "habit_care_plan",
                    "specialist_agent": "habit_care_plan",
                },
            },
        )
        assert cancel_plan_response.status_code == 200
        cancel_plan_id = cancel_plan_response.json()["id"]

        cancel_response = client.post(
            f"/api/v1/follow-ups/plans/{cancel_plan_id}/cancel",
            json={
                "notes": "User cancelled the follow up.",
                "outcome_status": "cancelled",
            },
        )
        assert cancel_response.status_code == 200
        cancel_payload = cancel_response.json()
        assert cancel_payload["status"] == "cancelled"

        admin_overview_response = client.get("/api/v1/admin/follow-up-overview")
        assert admin_overview_response.status_code == 200
        admin_overview_payload = admin_overview_response.json()

        assert "total_follow_up_plans" in admin_overview_payload
        assert "active_scheduled_plans" in admin_overview_payload
        assert "completed_plans" in admin_overview_payload
        assert "cancelled_plans" in admin_overview_payload
        assert "overdue_plans" in admin_overview_payload
        assert "failed_follow_up_events" in admin_overview_payload
        assert "delivery_channel_breakdown" in admin_overview_payload
        assert "scheduler_backend_breakdown" in admin_overview_payload
        assert "upcoming_due_follow_ups" in admin_overview_payload
        assert "recent_completion_outcomes" in admin_overview_payload
        assert admin_overview_payload["total_follow_up_plans"] >= 2
        assert "in_app" in admin_overview_payload["delivery_channel_breakdown"]

        admin_plans_response = client.get("/api/v1/admin/follow-up-plans")
        assert admin_plans_response.status_code == 200
        admin_plans_payload = admin_plans_response.json()

        assert len(admin_plans_payload) >= 1
        assert any(item["id"] == generated_plan["id"] for item in admin_plans_payload)

        admin_events_response = client.get("/api/v1/admin/follow-up-events")
        assert admin_events_response.status_code == 200
        admin_events_payload = admin_events_response.json()

        assert len(admin_events_payload) >= 1
        assert any(item["follow_up_plan_id"] == generated_plan["id"] for item in admin_events_payload)