from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def test_admin_intelligence_and_observability_surfaces_are_available() -> None:
    unique_email = f"admin-v210-{uuid4()}@example.com"

    with TestClient(app) as client:
        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Admin V210 User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Understand patterns and continuity",
                "focus_areas": "stress,sleep,routine",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I feel overwhelmed after work and want help that I can revisit tomorrow.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200

        traces_response = client.get("/api/v1/admin/agent-traces")
        assert traces_response.status_code == 200
        assert isinstance(traces_response.json(), list)

        grouped_response = client.get("/api/v1/admin/agent-trace-executions")
        assert grouped_response.status_code == 200
        grouped_payload = grouped_response.json()
        assert isinstance(grouped_payload, list)
        assert len(grouped_payload) >= 1

        detail_response = client.get(
            f"/api/v1/admin/agent-trace-executions/{grouped_payload[0]['trace_name']}"
        )
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert "events" in detail_payload

        intervention_logs_response = client.get("/api/v1/admin/intervention-logs")
        assert intervention_logs_response.status_code == 200

        intervention_overview_response = client.get("/api/v1/admin/intervention-overview")
        assert intervention_overview_response.status_code == 200
        assert "total_logs" in intervention_overview_response.json()

        routing_rules_response = client.get("/api/v1/admin/routing-rules")
        assert routing_rules_response.status_code == 200
        assert "active_version" in routing_rules_response.json()

        prompt_versions_response = client.get("/api/v1/admin/prompt-registry/versions")
        assert prompt_versions_response.status_code == 200

        policy_versions_response = client.get("/api/v1/admin/runtime-policy/versions")
        assert policy_versions_response.status_code == 200

        config_audit_response = client.get("/api/v1/admin/config-audit")
        assert config_audit_response.status_code == 200

        ops_overview_response = client.get("/api/v1/admin/ops-overview")
        assert ops_overview_response.status_code == 200
        ops_payload = ops_overview_response.json()
        assert "total_traces" in ops_payload
        assert "intervention_overview" in ops_payload

        analytics_overview_response = client.get("/api/v1/admin/analytics/overview")
        assert analytics_overview_response.status_code == 200
        analytics_payload = analytics_overview_response.json()
        assert "specialist_agent_breakdown" in analytics_payload
        assert "support_strategy_breakdown" in analytics_payload