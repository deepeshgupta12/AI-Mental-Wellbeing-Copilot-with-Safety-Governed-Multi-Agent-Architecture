from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def _bootstrap_admin(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/dev-session",
        json={
            "email": f"pack3-admin-{uuid4()}@example.com",
            "display_name": "Pack 3 Admin",
            "organization_name": "Pack 3 Org",
            "organization_slug": f"pack-3-org-{uuid4().hex[:8]}",
            "role_name": "platform_admin",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_v4_pack3_infrastructure_summary_is_available_and_secret_safe() -> None:
    with TestClient(app) as client:
        bootstrap = _bootstrap_admin(client)
        token = bootstrap["access_token"]

        response = client.get(
            "/api/v1/admin/settings/infrastructure/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        payload = response.json()

        assert payload["deployment_name"]
        assert payload["storage"]["provider"] in {"local", "s3"}
        assert payload["secrets"]["backend"] in {
            "env",
            "aws_secrets_manager",
            "vault",
            "doppler",
            "1password",
        }
        assert payload["secrets"]["redacted"] is True
        assert "secret_value" not in str(payload).lower()
        assert payload["queue"]["max_attempts"] >= 1
        assert payload["file_handling"]["max_attachment_bytes"] > 0


def test_v4_pack3_org_overrides_are_reflected_in_infrastructure_summary() -> None:
    with TestClient(app) as client:
        bootstrap = _bootstrap_admin(client)
        token = bootstrap["access_token"]
        organization_id = bootstrap["organization"]["id"]

        update_response = client.put(
            f"/api/v1/admin/settings/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "payload_json": {
                    "governance": {
                        "storage_policy_overrides": {
                            "audit_artifact_prefix": "org-audit-prefix",
                        },
                        "queue_hardening_overrides": {
                            "max_attempts": 9,
                            "max_inflight": 25,
                        },
                        "file_handling_overrides": {
                            "max_attachment_bytes": 2048,
                        },
                    }
                },
                "change_note": "Pack 3 org override test",
            },
        )
        assert update_response.status_code == 200

        summary_response = client.get(
            f"/api/v1/admin/settings/infrastructure/summary?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert summary_response.status_code == 200
        summary_payload = summary_response.json()

        assert summary_payload["organization_id"] == organization_id
        assert summary_payload["storage"]["audit_artifact_prefix"] == "org-audit-prefix"
        assert summary_payload["queue"]["max_attempts"] == 9
        assert summary_payload["queue"]["max_inflight"] == 25
        assert summary_payload["file_handling"]["max_attachment_bytes"] == 2048


def test_v4_pack3_high_risk_runtime_writes_stored_artifact_manifests() -> None:
    unique_email = f"pack3-user-{uuid4()}@example.com"

    with TestClient(app) as client:
        bootstrap = _bootstrap_admin(client)
        token = bootstrap["access_token"]

        user_response = client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "display_name": "Pack 3 User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Stabilize mood",
                "focus_areas": "stress,safety",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        runtime_response = client.post(
            "/api/v1/agent-runtime/smoke",
            json={
                "user_input": "I want to hurt myself tonight and I do not feel safe.",
                "provider": "mock",
                "user_id": user_id,
            },
        )
        assert runtime_response.status_code == 200

        artifacts_response = client.get(
            "/api/v1/admin/settings/infrastructure/artifacts?scope_type=safety_event",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert artifacts_response.status_code == 200
        artifacts_payload = artifacts_response.json()

        assert len(artifacts_payload) >= 1
        assert any(item["artifact_kind"] in {"evidence_json", "event_payload_json"} for item in artifacts_payload)
        assert any(item["storage_uri"] for item in artifacts_payload)

        audit_artifacts_response = client.get(
            "/api/v1/admin/settings/infrastructure/artifacts?scope_type=audit_log",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert audit_artifacts_response.status_code == 200
        audit_artifacts_payload = audit_artifacts_response.json()

        assert len(audit_artifacts_payload) >= 1
        assert any(item["artifact_kind"] == "audit_snapshot" for item in audit_artifacts_payload)