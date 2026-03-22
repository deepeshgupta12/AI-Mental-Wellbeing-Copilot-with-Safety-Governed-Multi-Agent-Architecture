from __future__ import annotations

from fastapi.testclient import TestClient

from mental_wellbeing_api.main import app


def _bootstrap_session(
    client: TestClient,
    *,
    email: str,
    organization_name: str,
    organization_slug: str,
    role_name: str,
) -> dict:
    response = client.post(
        "/api/v1/auth/dev-session",
        json={
            "email": email,
            "display_name": email.split("@")[0],
            "organization_name": organization_name,
            "organization_slug": organization_slug,
            "role_name": role_name,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_v4_pack2_deployment_settings_are_bootstrapped_and_updateable() -> None:
    with TestClient(app) as client:
        bootstrap = _bootstrap_session(
            client,
            email="pack2-admin@example.com",
            organization_name="Pack 2 Org",
            organization_slug="pack-2-org",
            role_name="platform_admin",
        )
        token = bootstrap["access_token"]

        current_response = client.get(
            "/api/v1/admin/settings/deployment/current",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert current_response.status_code == 200
        current_payload = current_response.json()

        assert current_payload["scope_type"] == "deployment"
        assert current_payload["payload_json"]["deployment"]["name"]

        updated_payload = current_payload["payload_json"]
        updated_payload["governance"]["escalation_policy"]["default_escalation_channel"] = "deployment_review_team"
        updated_payload["governance"]["model_provider_policy"]["low_risk_provider"] = "openai"

        update_response = client.put(
            "/api/v1/admin/settings/deployment/current",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "payload_json": updated_payload,
                "change_note": "Pack 2 deployment governance test update",
            },
        )
        assert update_response.status_code == 200
        update_json = update_response.json()

        assert (
            update_json["payload_json"]["governance"]["escalation_policy"]["default_escalation_channel"]
            == "deployment_review_team"
        )
        assert (
            update_json["payload_json"]["governance"]["model_provider_policy"]["low_risk_provider"]
            == "openai"
        )

        resolved_response = client.get(
            "/api/v1/admin/settings/resolved",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resolved_response.status_code == 200
        resolved_payload = resolved_response.json()

        assert (
            resolved_payload["effective_settings"]["governance"]["escalation_policy"]["default_escalation_channel"]
            == "deployment_review_team"
        )
        assert (
            resolved_payload["effective_settings"]["governance"]["model_provider_policy"]["low_risk_provider"]
            == "openai"
        )


def test_v4_pack2_org_overrides_are_reflected_in_enterprise_resolved_settings() -> None:
    with TestClient(app) as client:
        admin_bootstrap = _bootstrap_session(
            client,
            email="pack2-org-admin@example.com",
            organization_name="Pack 2 Member Org",
            organization_slug="pack-2-member-org",
            role_name="platform_admin",
        )
        member_bootstrap = _bootstrap_session(
            client,
            email="pack2-member@example.com",
            organization_name="Pack 2 Member Org",
            organization_slug="pack-2-member-org",
            role_name="member",
        )

        admin_token = admin_bootstrap["access_token"]
        member_token = member_bootstrap["access_token"]
        organization_id = admin_bootstrap["organization"]["id"]

        update_response = client.put(
            f"/api/v1/admin/settings/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "payload_json": {
                    "governance": {
                        "escalation_policy_overrides": {
                            "default_escalation_channel": "org_review_team",
                        },
                        "model_provider_policy_overrides": {
                            "high_risk_provider": "openai",
                            "final_response_provider": "openai",
                        },
                        "feature_flags": {
                            "allow_self_serve_escalation": True,
                        },
                    }
                },
                "change_note": "Pack 2 org governance override test update",
            },
        )
        assert update_response.status_code == 200

        resolved_response = client.get(
            "/api/v1/enterprise/settings/resolved",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resolved_response.status_code == 200
        resolved_payload = resolved_response.json()

        assert resolved_payload["organization_id"] == organization_id
        assert (
            resolved_payload["effective_settings"]["governance"]["escalation_policy"]["default_escalation_channel"]
            == "org_review_team"
        )
        assert (
            resolved_payload["effective_settings"]["governance"]["model_provider_policy"]["high_risk_provider"]
            == "openai"
        )
        assert (
            resolved_payload["effective_settings"]["governance"]["feature_flags"]["allow_self_serve_escalation"]
            is True
        )


def test_v4_pack2_member_cannot_write_admin_settings() -> None:
    with TestClient(app) as client:
        member_bootstrap = _bootstrap_session(
            client,
            email="pack2-readonly@example.com",
            organization_name="Pack 2 Readonly Org",
            organization_slug="pack-2-readonly-org",
            role_name="member",
        )
        token = member_bootstrap["access_token"]

        update_response = client.put(
            "/api/v1/admin/settings/deployment/current",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "payload_json": {
                    "deployment": {
                        "name": "local",
                    },
                    "governance": {
                        "escalation_policy": {},
                        "model_provider_policy": {},
                        "managed_config": {},
                    },
                },
                "change_note": "Should be forbidden for member",
            },
        )
        assert update_response.status_code == 403