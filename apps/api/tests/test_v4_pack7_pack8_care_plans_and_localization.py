from __future__ import annotations

from uuid import uuid4

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


def test_v4_pack7_care_plans_user_and_admin_surfaces_work() -> None:
    unique_suffix = uuid4().hex[:10]

    with TestClient(app) as client:
        admin_bootstrap = _bootstrap_session(
            client,
            email=f"pack78-admin-{unique_suffix}@example.com",
            organization_name="Pack 78 Org",
            organization_slug=f"pack-78-org-{unique_suffix}",
            role_name="platform_admin",
        )
        admin_token = admin_bootstrap["access_token"]
        organization_id = admin_bootstrap["organization"]["id"]

        user_response = client.post(
            "/api/v1/users",
            json={
                "email": f"pack78-user-{unique_suffix}@example.com",
                "display_name": "Pack 78 User",
                "timezone": "Asia/Kolkata",
                "support_style": "direct",
                "wellbeing_goals": "Build steady habits",
                "focus_areas": "routine,stress",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        create_plan_response = client.post(
            "/api/v1/care-plans",
            json={
                "user_id": user_id,
                "organization_id": organization_id,
                "source_agent": "habit_care_plan",
                "program_key": "habit_rebuild_program",
                "title": "Habit Rebuild Program",
                "description": "A recurring care plan for building consistency.",
                "preferred_language": "hi",
                "timezone": "Asia/Kolkata",
                "cadence_json": {"every_n_days": 3},
                "sequence_json": {
                    "steps": [
                        {"key": "stabilize", "order": 1},
                        {"key": "practice", "order": 2},
                        {"key": "review", "order": 3},
                    ]
                },
            },
        )
        assert create_plan_response.status_code == 200
        care_plan_payload = create_plan_response.json()
        care_plan_id = care_plan_payload["id"]

        assert care_plan_payload["user_id"] == user_id
        assert care_plan_payload["organization_id"] == organization_id
        assert care_plan_payload["program_key"] == "habit_rebuild_program"
        assert care_plan_payload["preferred_language"] == "hi"
        assert care_plan_payload["status"] == "active"
        assert care_plan_payload["current_step_key"] == "stabilize"

        list_response = client.get(f"/api/v1/care-plans?user_id={user_id}")
        assert list_response.status_code == 200
        list_payload = list_response.json()
        assert len(list_payload) >= 1
        assert any(item["id"] == care_plan_id for item in list_payload)

        event_response = client.post(
            f"/api/v1/care-plans/{care_plan_id}/events",
            json={
                "user_id": user_id,
                "event_type": "check_in",
                "event_status": "completed",
                "step_key": "stabilize",
                "adherence_score": 1.0,
                "notes": "User completed the first check-in.",
            },
        )
        assert event_response.status_code == 200
        event_payload = event_response.json()
        assert event_payload["care_plan_id"] == care_plan_id
        assert event_payload["event_type"] == "check_in"
        assert event_payload["adherence_score"] == 1.0

        advance_response = client.post(
            f"/api/v1/care-plans/{care_plan_id}/advance",
            json={
                "notes": "Advance to next step",
            },
        )
        assert advance_response.status_code == 200
        advance_payload = advance_response.json()
        assert advance_payload["id"] == care_plan_id
        assert advance_payload["current_step_key"] == "practice"
        assert advance_payload["progress_json"]["completed_step_count"] >= 1
        assert advance_payload["adherence_json"]["check_in_count"] >= 1

        summary_response = client.get(f"/api/v1/care-plans/summary?user_id={user_id}")
        assert summary_response.status_code == 200
        summary_payload = summary_response.json()
        assert summary_payload["user_id"] == user_id
        assert summary_payload["total_care_plans"] >= 1
        assert summary_payload["active_care_plans"] >= 1
        assert "habit_rebuild_program" in summary_payload["by_program_key"]

        admin_overview_response = client.get(
            f"/api/v1/admin/care-plans/overview?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_overview_response.status_code == 200
        admin_overview_payload = admin_overview_response.json()

        assert admin_overview_payload["total_care_plans"] >= 1
        assert admin_overview_payload["active_care_plans"] >= 1
        assert "habit_rebuild_program" in admin_overview_payload["program_breakdown"]
        assert "hi" in admin_overview_payload["language_breakdown"]
        assert isinstance(admin_overview_payload["recent_events"], list)

        admin_care_plans_response = client.get(
            f"/api/v1/admin/care-plans?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_care_plans_response.status_code == 200
        admin_care_plans_payload = admin_care_plans_response.json()
        assert len(admin_care_plans_payload) >= 1
        assert any(item["id"] == care_plan_id for item in admin_care_plans_payload)

        admin_events_response = client.get(
            "/api/v1/admin/care-plan-events",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_events_response.status_code == 200
        admin_events_payload = admin_events_response.json()
        assert len(admin_events_payload) >= 1
        assert any(item["care_plan_id"] == care_plan_id for item in admin_events_payload)


def test_v4_pack8_localization_catalog_preferences_and_admin_overview_work() -> None:
    unique_suffix = uuid4().hex[:10]

    with TestClient(app) as client:
        admin_bootstrap = _bootstrap_session(
            client,
            email=f"pack78-admin-localization-{unique_suffix}@example.com",
            organization_name="Pack 78 Local Org",
            organization_slug=f"pack-78-local-org-{unique_suffix}",
            role_name="platform_admin",
        )
        admin_token = admin_bootstrap["access_token"]
        organization_id = admin_bootstrap["organization"]["id"]

        user_response = client.post(
            "/api/v1/users",
            json={
                "email": f"pack78-local-user-{unique_suffix}@example.com",
                "display_name": "Localized User",
                "timezone": "Asia/Kolkata",
                "support_style": "reflective",
                "wellbeing_goals": "Feel supported in my language",
                "focus_areas": "stress,clarity",
            },
        )
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        catalog_response = client.get("/api/v1/localization/catalog")
        assert catalog_response.status_code == 200
        catalog_payload = catalog_response.json()

        assert catalog_payload["default_language"] == "en"
        assert len(catalog_payload["supported_languages"]) >= 3
        assert any(item["language_code"] == "hi" for item in catalog_payload["supported_languages"])
        assert any(
            item["language_code"] == "hinglish"
            for item in catalog_payload["supported_languages"]
        )

        runtime_copy_response = client.get("/api/v1/localization/runtime-copy?language=hi")
        assert runtime_copy_response.status_code == 200
        runtime_copy_payload = runtime_copy_response.json()

        assert runtime_copy_payload["language"] == "hi"
        assert runtime_copy_payload["normalized_language"] == "hi"
        assert "crisis_open" in runtime_copy_payload["copy"]
        assert "care_plan_step_complete" in runtime_copy_payload["copy"]

        set_language_response = client.put(
            f"/api/v1/users/{user_id}/language",
            json={
                "preferred_language": "hinglish",
                "content_language": "hinglish",
                "fallback_language": "en",
            },
        )
        assert set_language_response.status_code == 200
        set_language_payload = set_language_response.json()
        assert set_language_payload["user_id"] == user_id
        assert set_language_payload["preferred_language"] == "hinglish"
        assert set_language_payload["content_language"] == "hinglish"
        assert set_language_payload["fallback_language"] == "en"

        get_language_response = client.get(f"/api/v1/users/{user_id}/language")
        assert get_language_response.status_code == 200
        get_language_payload = get_language_response.json()
        assert get_language_payload["preferred_language"] == "hinglish"
        assert get_language_payload["content_language"] == "hinglish"

        admin_localization_response = client.get(
            f"/api/v1/admin/localization/overview?organization_id={organization_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_localization_response.status_code == 200
        admin_localization_payload = admin_localization_response.json()

        assert admin_localization_payload["organization_id"] == organization_id
        assert admin_localization_payload["default_language"] == "en"
        assert "hinglish" in admin_localization_payload["supported_language_codes"]
        assert "hi" in admin_localization_payload["supported_language_codes"]
        assert isinstance(admin_localization_payload["language_preference_breakdown"], dict)
        assert isinstance(admin_localization_payload["content_language_breakdown"], dict)
        assert isinstance(admin_localization_payload["fallback_language_breakdown"], dict)