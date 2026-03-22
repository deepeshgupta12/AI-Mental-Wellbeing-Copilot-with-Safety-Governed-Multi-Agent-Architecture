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


def test_v4_pack6_user_external_integrations_ingestion_and_status_surfaces_work() -> None:
    with TestClient(app) as client:
        member_bootstrap = _bootstrap_session(
            client,
            email="pack6-member@example.com",
            organization_name="Pack 6 Org",
            organization_slug="pack-6-org",
            role_name="member",
        )
        token = member_bootstrap["access_token"]

        catalog_response = client.get(
            "/api/v1/external-integrations/catalog",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert catalog_response.status_code == 200
        catalog_payload = catalog_response.json()
        assert len(catalog_payload) >= 4
        assert any(item["provider_key"] == "google_calendar" for item in catalog_payload)

        create_connection_response = client.post(
            "/api/v1/external-integrations/me/connections",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "integration_key": "calendar",
                "provider_key": "google_calendar",
                "consent_status": "active",
                "access_scope_json": {"read_calendar": True},
                "config_json": {"account_label": "Personal"},
                "metadata_json": {"source": "pack6-test"},
            },
        )
        assert create_connection_response.status_code == 200
        connection_payload = create_connection_response.json()
        connection_id = connection_payload["id"]
        assert connection_payload["consent_status"] == "active"
        assert connection_payload["provider_key"] == "google_calendar"

        queue_sync_response = client.post(
            f"/api/v1/external-integrations/me/connections/{connection_id}/sync",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_type": "manual_sync",
                "sync_window_days": 7,
                "request_payload_json": {"reason": "initial_seed"},
            },
        )
        assert queue_sync_response.status_code == 200
        queued_job_payload = queue_sync_response.json()
        assert queued_job_payload["status"] == "queued"

        ingest_response = client.post(
            f"/api/v1/external-integrations/me/connections/{connection_id}/ingest",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source_label": "calendar_seed",
                "payload_json": {
                    "events": [
                        {
                            "id": "evt-1",
                            "title": "Therapy Session",
                            "start_at": "2026-03-20T09:00:00+00:00",
                            "end_at": "2026-03-20T10:00:00+00:00",
                            "status": "confirmed",
                        },
                        {
                            "id": "evt-2",
                            "title": "Walk Break",
                            "start_at": "2026-03-21T18:00:00+00:00",
                            "end_at": "2026-03-21T18:30:00+00:00",
                            "status": "confirmed",
                        },
                    ]
                },
            },
        )
        assert ingest_response.status_code == 200
        ingest_payload = ingest_response.json()

        assert ingest_payload["normalized_signal_count"] == 2
        assert ingest_payload["job"]["status"] == "completed"
        assert ingest_payload["signal_type_breakdown"]["calendar_event"] == 2

        status_response = client.get(
            "/api/v1/external-integrations/me/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert status_response.status_code == 200
        status_payload = status_response.json()

        assert status_payload["user_id"] == member_bootstrap["user"]["id"]
        assert len(status_payload["connections"]) >= 1
        assert len(status_payload["recent_sync_jobs"]) >= 1
        assert status_payload["signal_breakdown_by_type"]["calendar_event"] >= 2

        signals_response = client.get(
            "/api/v1/external-integrations/me/signals?signal_type=calendar_event",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert signals_response.status_code == 200
        signals_payload = signals_response.json()
        assert len(signals_payload) >= 2
        assert all(item["signal_type"] == "calendar_event" for item in signals_payload)


def test_v4_pack6_admin_external_integrations_are_org_scoped_and_enterprise_safe() -> None:
    with TestClient(app) as client:
        admin_bootstrap = _bootstrap_session(
            client,
            email="pack6-admin@example.com",
            organization_name="Pack 6 Admin Org",
            organization_slug="pack-6-admin-org",
            role_name="platform_admin",
        )
        member_bootstrap = _bootstrap_session(
            client,
            email="pack6-member-boundary@example.com",
            organization_name="Pack 6 Admin Org",
            organization_slug="pack-6-admin-org",
            role_name="member",
        )

        admin_token = admin_bootstrap["access_token"]
        member_token = member_bootstrap["access_token"]
        organization_id = admin_bootstrap["organization"]["id"]

        disable_integrations_response = client.put(
            f"/api/v1/admin/settings/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "payload_json": {
                    "governance": {
                        "feature_flags": {
                            "external_integrations_enabled": False,
                        }
                    }
                },
                "change_note": "Disable external integrations for Pack 6 boundary test",
            },
        )
        assert disable_integrations_response.status_code == 200

        blocked_connection_response = client.post(
            "/api/v1/external-integrations/me/connections",
            headers={"Authorization": f"Bearer {member_token}"},
            json={
                "integration_key": "wearable",
                "provider_key": "fitbit_wearable",
                "consent_status": "active",
            },
        )
        assert blocked_connection_response.status_code == 403

        enable_integrations_response = client.put(
            f"/api/v1/admin/settings/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "payload_json": {
                    "governance": {
                        "feature_flags": {
                            "external_integrations_enabled": True,
                            "external_integrations_allowed_categories": [
                                "calendar",
                                "reminders",
                                "wearable",
                                "sleep",
                            ],
                            "external_integrations_allowed_providers": [
                                "google_calendar",
                                "apple_reminders",
                                "fitbit_wearable",
                                "oura_sleep",
                            ],
                        }
                    }
                },
                "change_note": "Enable external integrations for Pack 6 boundary test",
            },
        )
        assert enable_integrations_response.status_code == 200

        create_connection_response = client.post(
            "/api/v1/external-integrations/me/connections",
            headers={"Authorization": f"Bearer {member_token}"},
            json={
                "integration_key": "sleep",
                "provider_key": "oura_sleep",
                "consent_status": "active",
                "config_json": {"account_label": "Primary Sleep Source"},
            },
        )
        assert create_connection_response.status_code == 200
        connection_id = create_connection_response.json()["id"]

        ingest_response = client.post(
            f"/api/v1/external-integrations/me/connections/{connection_id}/ingest",
            headers={"Authorization": f"Bearer {member_token}"},
            json={
                "source_label": "sleep_seed",
                "payload_json": {
                    "sessions": [
                        {
                            "id": "sleep-1",
                            "start_at": "2026-03-20T22:00:00+00:00",
                            "end_at": "2026-03-21T05:30:00+00:00",
                            "duration_minutes": 450,
                            "sleep_score": 82,
                        }
                    ]
                },
            },
        )
        assert ingest_response.status_code == 200
        assert ingest_response.json()["normalized_signal_count"] == 1

        overview_response = client.get(
            f"/api/v1/admin/external-integrations/overview?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert overview_response.status_code == 200
        overview_payload = overview_response.json()

        assert overview_payload["organization_id"] == organization_id
        assert overview_payload["total_connections"] >= 1
        assert overview_payload["total_sync_jobs"] >= 1
        assert overview_payload["total_signals"] >= 1
        assert "oura_sleep" in overview_payload["connection_breakdown_by_provider"]
        assert "sleep_session" in overview_payload["signal_breakdown_by_type"]

        connections_response = client.get(
            f"/api/v1/admin/external-integrations/connections?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert connections_response.status_code == 200
        assert len(connections_response.json()) >= 1

        sync_jobs_response = client.get(
            f"/api/v1/admin/external-integrations/sync-jobs?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert sync_jobs_response.status_code == 200
        assert len(sync_jobs_response.json()) >= 1

        signals_response = client.get(
            f"/api/v1/admin/external-integrations/signals?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert signals_response.status_code == 200
        signals_payload = signals_response.json()
        assert len(signals_payload) >= 1
        assert any(item["signal_type"] == "sleep_session" for item in signals_payload)

        artifacts_response = client.get(
            "/api/v1/admin/settings/infrastructure/artifacts?scope_type=external_sync_job",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert artifacts_response.status_code == 200
        artifacts_payload = artifacts_response.json()
        assert len(artifacts_payload) >= 1
        assert any(item["artifact_kind"] == "ingest_payload_json" for item in artifacts_payload)