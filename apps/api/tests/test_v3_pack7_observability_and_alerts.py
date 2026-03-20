from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def _create_user(client: TestClient, *, email_prefix: str, display_name: str) -> str:
    response = client.post(
        "/api/v1/users",
        json={
            "email": f"{email_prefix}-{uuid4()}@example.com",
            "display_name": display_name,
            "timezone": "Asia/Kolkata",
            "support_style": "calm",
            "wellbeing_goals": "Stay safe and supported",
            "focus_areas": "safety,stress",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_v3_pack7_high_risk_runtime_creates_alertable_trace_and_safety_temporal_contract() -> None:
    with TestClient(app) as client:
        user_id = _create_user(
            client,
            email_prefix="pack7-alertable",
            display_name="Pack7 Alertable User",
        )

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to kill myself tonight.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200
        payload = runtime_response.json()

        assert payload["risk_level"] == "high"
        assert payload["safety_override"] is True
        assert payload["requires_human_review"] is True
        assert payload["decision_path_label"] == "crisis_escalation"
        assert payload["alertable_safety_trace"] is True
        assert payload["safety_temporal_contract"]["workflow_name"] == "safety_escalation_workflow"
        assert payload["safety_temporal_contract"]["trace_id"] is not None
        assert payload["safety_temporal_contract"]["user_id"] == user_id
        assert payload["safety_temporal_contract"]["status"] in {
            "ready_for_dispatch",
            "contract_only_not_enqueued",
        }

        grouped_response = client.get("/api/v1/admin/agent-trace-executions")
        assert grouped_response.status_code == 200
        grouped_payload = grouped_response.json()
        matching_execution = next(item for item in grouped_payload if item["user_id"] == user_id)

        detail_response = client.get(
            f"/api/v1/admin/agent-trace-executions/{matching_execution['trace_name']}"
        )
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()

        assert detail_payload["event_count"] >= 1
        assert any(
            bool(event["input_payload_json"].get("alertable_safety_trace"))
            for event in detail_payload["events"]
            if event.get("input_payload_json")
        )
        assert any(
            event["input_payload_json"].get("decision_path_label") == "crisis_escalation"
            for event in detail_payload["events"]
            if event.get("input_payload_json")
        )


def test_v3_pack7_ops_and_analytics_expose_safety_flow_metrics() -> None:
    with TestClient(app) as client:
        user_id = _create_user(
            client,
            email_prefix="pack7-metrics",
            display_name="Pack7 Metrics User",
        )

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to end my life.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200

        ops_response = client.get("/api/v1/admin/ops-overview")
        assert ops_response.status_code == 200
        ops_payload = ops_response.json()

        assert "safety_flow_overview" in ops_payload
        assert ops_payload["safety_flow_overview"]["total_safety_events"] >= 1
        assert ops_payload["safety_flow_overview"]["high_risk_safety_events"] >= 1
        assert ops_payload["safety_flow_overview"]["alertable_trace_count"] >= 1
        assert ops_payload["safety_flow_overview"]["immutable_audit_log_count"] >= 1
        assert "crisis_escalation" in ops_payload["safety_flow_overview"]["decision_path_breakdown"]

        analytics_response = client.get("/api/v1/admin/analytics/overview")
        assert analytics_response.status_code == 200
        analytics_payload = analytics_response.json()

        assert "safety_flow_overview" in analytics_payload
        assert analytics_payload["safety_flow_overview"]["total_safety_events"] >= 1
        assert analytics_payload["safety_flow_overview"]["alertable_trace_count"] >= 1
        assert analytics_payload["safety_flow_overview"]["temporal_safety_contract_status_breakdown"]

        audit_timeline_response = client.get("/api/v1/admin/audit-timeline")
        assert audit_timeline_response.status_code == 200
        audit_payload = audit_timeline_response.json()

        assert len(audit_payload) >= 1
        assert all("is_immutable" in item for item in audit_payload)
        assert any(item["is_immutable"] is True for item in audit_payload)


def test_v3_pack7_policy_version_history_and_audit_diff_are_available() -> None:
    marker = f"pack7-marker-{uuid4()}"

    with TestClient(app) as client:
        config_response = client.get("/api/v1/admin/policy-config")
        assert config_response.status_code == 200
        current_policy = config_response.json()["runtime_policy"]

        updated_policy = deepcopy(current_policy)
        updated_policy.setdefault("service", {})
        updated_policy["service"]["pack7_test_marker"] = marker

        update_response = client.put(
            "/api/v1/admin/runtime-policy",
            json={
                "payload_json": updated_policy,
                "change_note": "Pack7 policy history validation",
                "actor": "pack7-test",
            },
        )
        assert update_response.status_code == 200
        update_payload = update_response.json()
        assert update_payload["config_key"] == "runtime_policy"
        assert update_payload["is_active"] is True

        versions_response = client.get("/api/v1/admin/runtime-policy/versions")
        assert versions_response.status_code == 200
        versions_payload = versions_response.json()
        assert len(versions_payload) >= 2
        assert any(
            item.get("payload_json", {}).get("service", {}).get("pack7_test_marker") == marker
            for item in versions_payload
        )

        config_audit_response = client.get("/api/v1/admin/config-audit?config_key=runtime_policy")
        assert config_audit_response.status_code == 200
        audit_payload = config_audit_response.json()
        assert len(audit_payload) >= 1

        latest_audit = audit_payload[0]
        if latest_audit.get("from_version_id"):
            diff_response = client.get(
                "/api/v1/admin/config-diff",
                params={
                    "config_key": "runtime_policy",
                    "from_version_id": latest_audit["from_version_id"],
                    "to_version_id": latest_audit["to_version_id"],
                },
            )
            assert diff_response.status_code == 200
            diff_payload = diff_response.json()
            assert "changed_keys" in diff_payload
            assert len(diff_payload["changed_keys"]) >= 1

        restore_response = client.put(
            "/api/v1/admin/runtime-policy",
            json={
                "payload_json": current_policy,
                "change_note": "Pack7 policy history test restore",
                "actor": "pack7-test",
            },
        )
        assert restore_response.status_code == 200


def test_v3_pack7_admin_endpoints_support_pack6_web_safety_surfaces() -> None:
    with TestClient(app) as client:
        user_id = _create_user(
            client,
            email_prefix="pack7-websurfaces",
            display_name="Pack7 Web Surface User",
        )

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to kill myself tonight.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200

        safety_events_response = client.get("/api/v1/admin/safety-events")
        assert safety_events_response.status_code == 200
        safety_events_payload = safety_events_response.json()
        matching_event = next(item for item in safety_events_payload if item["user_id"] == user_id)

        assert matching_event["queue_status"] in {"queued", "in_review", "resolved"}
        assert matching_event["risk_level"] == "high"

        detail_response = client.get(f"/api/v1/admin/safety-events/{matching_event['id']}")
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()

        assert detail_payload["event"]["user_id"] == user_id
        assert detail_payload["event"]["evidence_json"]["decision_path_label"] == "crisis_escalation"
        assert detail_payload["event"]["evidence_json"]["human_summary"] is not None
        assert detail_payload["event"]["event_payload_json"]["safety_temporal_contract"]

        reviewer_dashboard_response = client.get("/api/v1/admin/reviewer-dashboard")
        assert reviewer_dashboard_response.status_code == 200
        reviewer_payload = reviewer_dashboard_response.json()
        assert reviewer_payload["total_events"] >= 1
        assert reviewer_payload["queued_events"] >= 1

        escalation_analytics_response = client.get("/api/v1/admin/escalation-analytics")
        assert escalation_analytics_response.status_code == 200
        escalation_payload = escalation_analytics_response.json()
        assert escalation_payload["total_events"] >= 1
        assert escalation_payload["high_risk_events"] >= 1