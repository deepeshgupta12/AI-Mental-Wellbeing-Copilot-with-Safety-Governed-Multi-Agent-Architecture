from __future__ import annotations

from copy import deepcopy
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.db.base import Base
from mental_wellbeing_api.models.enterprise_setting import EnterpriseSetting


class EnterpriseSettingsService:
    SETTING_KEY = "settings_bundle"

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()

    async def ensure_settings_table(self) -> None:
        conn = await self.session.connection()
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn,
                tables=[EnterpriseSetting.__table__],
                checkfirst=True,
            )
        )

    def _default_deployment_payload(self) -> dict[str, Any]:
        default_provider = "openai" if self.settings.openai_api_key else "mock"
        low_risk_provider = "ollama" if self.settings.ollama_default_model else default_provider

        return {
            "deployment": {
                "name": self.settings.deployment_name,
                "app_env": self.settings.app_env,
                "auth_mode": self.settings.auth_mode,
                "auth_requires_token": self.settings.auth_requires_token,
                "temporal_enabled": self.settings.temporal_enabled,
                "scheduler_backend": self.settings.scheduler_backend,
            },
            "governance": {
                "escalation_policy": {
                    "high_risk_requires_human_review": True,
                    "crisis_requires_immediate_escalation": True,
                    "default_escalation_channel": "human_reviewer",
                    "reviewer_role": "reviewer",
                },
                "model_provider_policy": {
                    "default_provider": default_provider,
                    "low_risk_provider": low_risk_provider,
                    "medium_risk_provider": default_provider,
                    "high_risk_provider": "openai" if self.settings.openai_api_key else default_provider,
                    "final_response_provider": "openai" if self.settings.openai_api_key else default_provider,
                    "openai_model": self.settings.openai_model,
                    "ollama_model": self.settings.ollama_default_model,
                },
                "managed_config": {
                    "allow_runtime_policy_edits": True,
                    "allow_prompt_registry_edits": True,
                    "allow_routing_rule_edits": True,
                },
            },
        }

    def _default_organization_payload(self, organization_id: str) -> dict[str, Any]:
        return {
            "organization_id": organization_id,
            "governance": {
                "escalation_policy_overrides": {},
                "model_provider_policy_overrides": {},
                "feature_flags": {},
            },
        }

    def _normalize_deployment_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = deepcopy(payload)
        normalized.setdefault("deployment", {})
        normalized.setdefault("governance", {})
        normalized["deployment"].setdefault("name", self.settings.deployment_name)
        normalized["deployment"].setdefault("app_env", self.settings.app_env)
        normalized["deployment"].setdefault("auth_mode", self.settings.auth_mode)
        normalized["deployment"].setdefault(
            "auth_requires_token",
            self.settings.auth_requires_token,
        )
        normalized["deployment"].setdefault("temporal_enabled", self.settings.temporal_enabled)
        normalized["deployment"].setdefault("scheduler_backend", self.settings.scheduler_backend)

        governance = normalized["governance"]
        governance.setdefault("escalation_policy", {})
        governance.setdefault("model_provider_policy", {})
        governance.setdefault("managed_config", {})
        return normalized

    def _normalize_organization_payload(
        self,
        organization_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = deepcopy(payload)
        normalized["organization_id"] = organization_id
        normalized.setdefault("governance", {})
        governance = normalized["governance"]
        governance.setdefault("escalation_policy_overrides", {})
        governance.setdefault("model_provider_policy_overrides", {})
        governance.setdefault("feature_flags", {})
        return normalized

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in override.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged

    async def _get_setting(
        self,
        *,
        scope_type: str,
        scope_id: str,
    ) -> EnterpriseSetting | None:
        await self.ensure_settings_table()
        return await self.session.scalar(
            select(EnterpriseSetting).where(
                EnterpriseSetting.scope_type == scope_type,
                EnterpriseSetting.scope_id == scope_id,
                EnterpriseSetting.setting_key == self.SETTING_KEY,
                EnterpriseSetting.is_active.is_(True),
            )
        )

    async def _get_or_bootstrap_setting(
        self,
        *,
        scope_type: str,
        scope_id: str,
        actor: str = "system",
    ) -> EnterpriseSetting:
        existing = await self._get_setting(scope_type=scope_type, scope_id=scope_id)
        if existing is not None:
            return existing

        if scope_type == "deployment":
            payload = self._default_deployment_payload()
        elif scope_type == "organization":
            payload = self._default_organization_payload(scope_id)
        else:
            raise ValueError("Unsupported settings scope")

        row = EnterpriseSetting(
            scope_type=scope_type,
            scope_id=scope_id,
            setting_key=self.SETTING_KEY,
            payload_json=payload,
            is_active=True,
            created_by=actor,
            updated_by=actor,
            change_note="Bootstrap Pack 2 governance settings",
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def get_deployment_settings(self) -> EnterpriseSetting:
        return await self._get_or_bootstrap_setting(
            scope_type="deployment",
            scope_id=self.settings.deployment_name,
        )

    async def get_organization_settings(self, organization_id: str) -> EnterpriseSetting:
        return await self._get_or_bootstrap_setting(
            scope_type="organization",
            scope_id=organization_id,
        )

    async def update_deployment_settings(
        self,
        *,
        payload: dict[str, Any],
        actor: str,
        change_note: str | None = None,
    ) -> EnterpriseSetting:
        row = await self.get_deployment_settings()
        row.payload_json = self._normalize_deployment_payload(payload)
        row.updated_by = actor
        row.change_note = change_note
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def update_organization_settings(
        self,
        *,
        organization_id: str,
        payload: dict[str, Any],
        actor: str,
        change_note: str | None = None,
    ) -> EnterpriseSetting:
        row = await self.get_organization_settings(organization_id)
        row.payload_json = self._normalize_organization_payload(organization_id, payload)
        row.updated_by = actor
        row.change_note = change_note
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def resolve_settings(
        self,
        *,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        deployment_row = await self.get_deployment_settings()
        deployment_payload = deepcopy(deployment_row.payload_json)

        organization_payload: dict[str, Any] | None = None
        effective = deepcopy(deployment_payload)

        if organization_id:
            organization_row = await self.get_organization_settings(organization_id)
            organization_payload = deepcopy(organization_row.payload_json)

            organization_governance = organization_payload.get("governance", {})
            escalation_overrides = organization_governance.get("escalation_policy_overrides", {})
            provider_overrides = organization_governance.get("model_provider_policy_overrides", {})
            feature_flags = organization_governance.get("feature_flags", {})

            effective.setdefault("governance", {})
            effective["governance"].setdefault("escalation_policy", {})
            effective["governance"].setdefault("model_provider_policy", {})
            effective["governance"].setdefault("feature_flags", {})

            if isinstance(escalation_overrides, dict):
                effective["governance"]["escalation_policy"] = self._deep_merge(
                    effective["governance"]["escalation_policy"],
                    escalation_overrides,
                )
            if isinstance(provider_overrides, dict):
                effective["governance"]["model_provider_policy"] = self._deep_merge(
                    effective["governance"]["model_provider_policy"],
                    provider_overrides,
                )
            if isinstance(feature_flags, dict):
                effective["governance"]["feature_flags"] = self._deep_merge(
                    effective["governance"]["feature_flags"],
                    feature_flags,
                )

        return {
            "deployment_name": self.settings.deployment_name,
            "organization_id": organization_id,
            "deployment_settings": deployment_payload,
            "organization_settings": organization_payload,
            "effective_settings": effective,
        }