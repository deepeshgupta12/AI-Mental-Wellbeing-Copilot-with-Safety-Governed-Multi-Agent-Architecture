from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_safety_review_resolution_flow() -> None:
    unique_email = f"review-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Review User",
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

        queue_response = client.get("/api/v1/safety-flags/queue")
        assert queue_response.status_code == 200
        queue_payload = queue_response.json()
        assert len(queue_payload) >= 1

        target_flag = next(item for item in queue_payload if item["user_id"] == user_id)
        flag_id = target_flag["id"]

        counts_response = client.get("/api/v1/safety-flags/dashboard-counts")
        assert counts_response.status_code == 200
        counts_payload = counts_response.json()
        assert counts_payload["total_flags"] >= 1
        assert counts_payload["open_flags"] >= 1
        assert counts_payload["review_needed_flags"] >= 1

        safety_events_response = client.get("/api/v1/admin/safety-events")
        assert safety_events_response.status_code == 200
        safety_events_payload = safety_events_response.json()
        target_event = next(item for item in safety_events_payload if item["user_id"] == user_id)

        review_response = client.post(
            f"/api/v1/admin/safety-events/{target_event['id']}/reviews",
            json={
                "reviewer_id": "reviewer-1",
                "review_status": "resolved",
                "reviewer_note": "Reviewed and escalated to human support flow.",
                "human_summary": "High-risk statement reviewed by human.",
                "decision_rationale": "Immediate support and escalation required.",
                "resolution_type": "human_escalation",
                "escalation_required": True,
                "escalation_status": "escalated",
                "review_payload_json": {"channel": "human_support"},
            },
        )
        assert review_response.status_code == 200
        review_payload = review_response.json()
        assert review_payload["review_status"] == "resolved"
        assert review_payload["escalation_required"] is True
        assert review_payload["escalation_status"] == "escalated"

        update_response = client.patch(
            f"/api/v1/safety-flags/{flag_id}",
            json={
                "needs_review": False,
                "is_resolved": True,
                "reviewer_note": "Reviewed and escalated to human support flow.",
            },
        )
        assert update_response.status_code == 200
        update_payload = update_response.json()
        assert update_payload["needs_review"] is False
        assert update_payload["is_resolved"] is True
        assert update_payload["reviewer_note"] == "Reviewed and escalated to human support flow."
        assert update_payload["reviewed_at"] is not None
        assert update_payload["resolved_at"] is not None

        final_counts_response = client.get("/api/v1/safety-flags/dashboard-counts")
        assert final_counts_response.status_code == 200
        final_counts_payload = final_counts_response.json()
        assert final_counts_payload["resolved_flags"] >= 1

        reviewer_dashboard_response = client.get("/api/v1/admin/reviewer-dashboard")
        assert reviewer_dashboard_response.status_code == 200
        reviewer_dashboard_payload = reviewer_dashboard_response.json()
        assert reviewer_dashboard_payload["total_events"] >= 1

        escalation_analytics_response = client.get("/api/v1/admin/escalation-analytics")
        assert escalation_analytics_response.status_code == 200
        escalation_analytics_payload = escalation_analytics_response.json()
        assert escalation_analytics_payload["total_events"] >= 1

        audit_timeline_response = client.get("/api/v1/admin/audit-timeline")
        assert audit_timeline_response.status_code == 200
        audit_timeline_payload = audit_timeline_response.json()
        assert len(audit_timeline_payload) >= 1