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


def test_v4_pack4_enterprise_analytics_surfaces_are_available() -> None:
    with TestClient(app) as client:
        admin_bootstrap = _bootstrap_session(
            client,
            email="pack4-admin@example.com",
            organization_name="Pack 4 Org",
            organization_slug="pack-4-org",
            role_name="platform_admin",
        )
        _bootstrap_session(
            client,
            email="pack4-member@example.com",
            organization_name="Pack 4 Org",
            organization_slug="pack-4-org",
            role_name="member",
        )

        token = admin_bootstrap["access_token"]
        organization_id = admin_bootstrap["organization"]["id"]

        overview_response = client.get(
            "/api/v1/admin/enterprise-analytics/overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert overview_response.status_code == 200
        overview_payload = overview_response.json()

        assert overview_payload["total_organizations"] >= 1
        assert overview_payload["total_memberships"] >= 2
        assert overview_payload["total_auth_sessions"] >= 2
        assert len(overview_payload["organizations"]) >= 1

        orgs_response = client.get(
            "/api/v1/admin/enterprise-analytics/organizations",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert orgs_response.status_code == 200
        orgs_payload = orgs_response.json()
        assert len(orgs_payload) >= 1

        detail_response = client.get(
            f"/api/v1/admin/enterprise-analytics/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()

        assert detail_payload["organization"]["id"] == organization_id
        assert "effective_settings" in detail_payload
        assert "infrastructure_summary" in detail_payload
        assert isinstance(detail_payload["recent_auth_sessions"], list)


def test_v4_pack5_integration_surfaces_are_available_and_secret_safe() -> None:
    with TestClient(app) as client:
        bootstrap = _bootstrap_session(
            client,
            email="pack5-admin@example.com",
            organization_name="Pack 5 Org",
            organization_slug="pack-5-org",
            role_name="platform_admin",
        )
        token = bootstrap["access_token"]
        organization_id = bootstrap["organization"]["id"]

        overview_response = client.get(
            f"/api/v1/admin/integrations/overview?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert overview_response.status_code == 200
        overview_payload = overview_response.json()

        assert overview_payload["deployment_name"]
        assert overview_payload["organization_id"] == organization_id
        assert overview_payload["storage_provider"] in {"local", "s3"}
        assert overview_payload["secret_backend"] in {
            "env",
            "aws_secrets_manager",
            "vault",
            "doppler",
            "1password",
        }
        assert overview_payload["redacted"] is True
        assert "secret_value" not in str(overview_payload).lower()
        assert len(overview_payload["integration_endpoints"]) >= 1

        runtime_feed_response = client.get(
            f"/api/v1/admin/integrations/runtime-feed?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert runtime_feed_response.status_code == 200
        runtime_feed_payload = runtime_feed_response.json()

        assert runtime_feed_payload["deployment_name"]
        assert runtime_feed_payload["organization_id"] == organization_id
        assert runtime_feed_payload["redacted"] is True
        assert "counts" in runtime_feed_payload
        assert "capabilities" in runtime_feed_payload
        assert "endpoints" in runtime_feed_payload
        assert "secret_value" not in str(runtime_feed_payload).lower()