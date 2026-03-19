from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_v3_high_risk_session_is_reviewable_in_admin_queue() -> None:
    unique_email = f"v3-reviewable-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "V3 Reviewable User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Stay safe",
                "focus_areas": "safety,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to kill myself tonight.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        runtime_payload = runtime_response.json()

        assert runtime_payload["risk_level"] == "high"
        assert runtime_payload["safety_override"] is True
        assert runtime_payload["requires_human_review"] is True
        assert runtime_payload["review_recommended"] is True
        assert runtime_payload["decision_path_label"] == "crisis_escalation"
        assert runtime_payload["human_summary"] is not None
        assert runtime_payload["evidence_bundle"]
        assert runtime_payload["audit_snapshot"]

        safety_events_response = client.get("/api/v1/admin/safety-events")
        assert safety_events_response.status_code == 200
        safety_events_payload = safety_events_response.json()

        matching = [item for item in safety_events_payload if item["user_id"] == user_id]
        assert len(matching) >= 1
        assert matching[0]["queue_status"] in {"queued", "in_review", "resolved"}

        detail_response = client.get(f"/api/v1/admin/safety-events/{matching[0]['id']}")
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert detail_payload["event"]["user_id"] == user_id


def test_v3_admin_review_creation_writes_audit_timeline() -> None:
    unique_email = f"v3-audit-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "V3 Audit User",
                "timezone": "Asia/Kolkata",
                "support_style": "calm",
                "wellbeing_goals": "Stay safe",
                "focus_areas": "safety,stress",
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

        safety_events_response = client.get("/api/v1/admin/safety-events")
        assert safety_events_response.status_code == 200
        safety_event = next(item for item in safety_events_response.json() if item["user_id"] == user_id)

        review_response = client.post(
            f"/api/v1/admin/safety-events/{safety_event['id']}/reviews",
            json={
                "reviewer_id": "reviewer-v3",
                "review_status": "resolved",
                "reviewer_note": "Resolved through human safety escalation.",
                "human_summary": "Reviewer confirmed immediate support path.",
                "decision_rationale": "High-risk content required escalation.",
                "resolution_type": "human_escalation",
                "escalation_required": True,
                "escalation_status": "escalated",
                "review_payload_json": {"source": "admin_queue"},
            },
        )
        assert review_response.status_code == 200
        review_payload = review_response.json()
        assert review_payload["review_status"] == "resolved"

        dashboard_response = client.get("/api/v1/admin/reviewer-dashboard")
        assert dashboard_response.status_code == 200
        dashboard_payload = dashboard_response.json()
        assert dashboard_payload["total_events"] >= 1

        analytics_response = client.get("/api/v1/admin/escalation-analytics")
        assert analytics_response.status_code == 200
        analytics_payload = analytics_response.json()
        assert analytics_payload["total_events"] >= 1

        audit_timeline_response = client.get("/api/v1/admin/audit-timeline")
        assert audit_timeline_response.status_code == 200
        audit_payload = audit_timeline_response.json()
        assert len(audit_payload) >= 1
        assert any(item["event_type"] == "safety_review_created" for item in audit_payload)