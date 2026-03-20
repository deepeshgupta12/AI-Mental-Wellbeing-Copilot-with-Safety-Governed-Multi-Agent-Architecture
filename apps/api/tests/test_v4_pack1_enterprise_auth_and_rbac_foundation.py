from __future__ import annotations

from fastapi.testclient import TestClient

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.main import app


def _reset_settings() -> None:
    get_settings.cache_clear()


def test_v4_pack1_dev_session_bootstrap_returns_enterprise_context() -> None:
    _reset_settings()

    with TestClient(app) as client:
        bootstrap_response = client.post(
            "/api/v1/auth/dev-session",
            json={
                "email": "pack1-admin@example.com",
                "display_name": "Pack 1 Admin",
                "organization_name": "Pack 1 Org",
                "organization_slug": "pack-1-org",
                "role_name": "platform_admin",
            },
        )
        assert bootstrap_response.status_code == 200
        bootstrap_payload = bootstrap_response.json()

        assert bootstrap_payload["access_token"]
        assert bootstrap_payload["user"]["email"] == "pack1-admin@example.com"
        assert bootstrap_payload["organization"]["slug"] == "pack-1-org"
        assert bootstrap_payload["membership"]["role"]["name"] == "platform_admin"
        assert "admin:read" in bootstrap_payload["permissions"]
        assert "enterprise:read" in bootstrap_payload["permissions"]

        token = bootstrap_payload["access_token"]

        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        me_payload = me_response.json()

        assert me_payload["is_authenticated"] is True
        assert me_payload["role_name"] == "platform_admin"
        assert me_payload["organization"]["slug"] == "pack-1-org"
        assert "admin:write" in me_payload["permissions"]


def test_v4_pack1_admin_routes_are_protected_in_token_required_mode(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_MODE", "token_required")
    _reset_settings()

    with TestClient(app) as client:
        unauthorized_response = client.get("/api/v1/admin/ops-overview")
        assert unauthorized_response.status_code == 401

        bootstrap_response = client.post(
            "/api/v1/auth/dev-session",
            json={
                "email": "pack1-protected@example.com",
                "display_name": "Protected Admin",
                "organization_name": "Protected Org",
                "organization_slug": "protected-org",
                "role_name": "platform_admin",
            },
        )
        assert bootstrap_response.status_code == 200
        token = bootstrap_response.json()["access_token"]

        authorized_response = client.get(
            "/api/v1/admin/ops-overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert authorized_response.status_code == 200

    monkeypatch.delenv("AUTH_MODE", raising=False)
    _reset_settings()


def test_v4_pack1_enterprise_context_and_memberships_are_resolved_from_session() -> None:
    _reset_settings()

    with TestClient(app) as client:
        bootstrap_response = client.post(
            "/api/v1/auth/dev-session",
            json={
                "email": "pack1-member@example.com",
                "display_name": "Pack 1 Member",
                "organization_name": "Member Org",
                "organization_slug": "member-org",
                "role_name": "member",
            },
        )
        assert bootstrap_response.status_code == 200
        bootstrap_payload = bootstrap_response.json()
        token = bootstrap_payload["access_token"]
        organization_id = bootstrap_payload["organization"]["id"]

        context_response = client.get(
            "/api/v1/enterprise/context",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert context_response.status_code == 200
        context_payload = context_response.json()

        assert context_payload["organization_id"] == organization_id
        assert context_payload["role_name"] == "member"
        assert "enterprise:read" in context_payload["permissions"]
        assert "admin:read" not in context_payload["permissions"]

        memberships_response = client.get(
            f"/api/v1/enterprise/organizations/{organization_id}/memberships",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert memberships_response.status_code == 200
        memberships_payload = memberships_response.json()

        assert len(memberships_payload) >= 1
        assert memberships_payload[0]["organization"]["id"] == organization_id
        assert memberships_payload[0]["role"]["name"] == "member"