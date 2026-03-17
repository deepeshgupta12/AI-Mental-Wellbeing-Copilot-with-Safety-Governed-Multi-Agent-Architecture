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