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
                "storage": {
                    "provider": self.settings.storage_provider,
                    "local_root": str(self.settings.storage_local_root_path),
                    "bucket_name": self.settings.storage_artifact_bucket or None,
                    "region": self.settings.storage_region or None,
                    "endpoint_url": self.settings.storage_endpoint_url or None,
                    "audit_artifact_prefix": self.settings.storage_audit_artifact_prefix,
                    "safety_artifact_prefix": self.settings.storage_safety_artifact_prefix,
                    "attachment_prefix": self.settings.storage_attachment_prefix,
                    "stage_remote_writes_locally": self.settings.storage_stage_remote_writes_locally,
                },
                "secrets": {
                    "backend": self.settings.secret_backend,
                    "namespace": self.settings.managed_secret_namespace,
                    "prefix": self.settings.managed_secret_prefix or None,
                    "managed_secret_keys": [
                        "OPENAI_API_KEY",
                        "AUTH_SESSION_SECRET",
                        "STORAGE_ACCESS_KEY_ID",
                        "STORAGE_SECRET_ACCESS_KEY",
                    ],
                },
                "queue_hardening": {
                    "max_attempts": self.settings.queue_max_attempts,
                    "dead_letter_enabled": self.settings.queue_dead_letter_enabled,
                    "max_inflight": self.settings.queue_max_inflight,
                    "visibility_timeout_seconds": self.settings.queue_visibility_timeout_seconds,
                    "enforce_idempotency": self.settings.queue_enforce_idempotency,
                    "temporal_namespace": self.settings.temporal_namespace,
                    "temporal_task_queue": self.settings.temporal_task_queue,
                },
                "file_handling": {
                    "max_attachment_bytes": self.settings.file_max_attachment_bytes,
                    "allowed_attachment_content_types": self.settings.file_allowed_attachment_content_types_list,
                    "sanitize_filenames": True,
                    "quarantine_prefix": self.settings.file_quarantine_prefix,
                },
                "cloud": {
                    "deployment_profile": self.settings.cloud_deployment_profile,
                    "config_source": self.settings.cloud_config_source,
                    "object_storage_mode": self.settings.storage_provider,
                },
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
                    "allow_enterprise_settings_edits": True,
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
                "storage_policy_overrides": {},
                "queue_hardening_overrides": {},
                "file_handling_overrides": {},
            },
        }

    def _normalize_deployment_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = deepcopy(payload)
        normalized.setdefault("deployment", {})
        normalized.setdefault("governance", {})

        deployment = normalized["deployment"]
        deployment.setdefault("name", self.settings.deployment_name)
        deployment.setdefault("app_env", self.settings.app_env)
        deployment.setdefault("auth_mode", self.settings.auth_mode)
        deployment.setdefault("auth_requires_token", self.settings.auth_requires_token)
        deployment.setdefault("temporal_enabled", self.settings.temporal_enabled)
        deployment.setdefault("scheduler_backend", self.settings.scheduler_backend)
        deployment.setdefault("storage", {})
        deployment.setdefault("secrets", {})
        deployment.setdefault("queue_hardening", {})
        deployment.setdefault("file_handling", {})
        deployment.setdefault("cloud", {})

        deployment["storage"].setdefault("provider", self.settings.storage_provider)
        deployment["storage"].setdefault("local_root", str(self.settings.storage_local_root_path))
        deployment["storage"].setdefault("bucket_name", self.settings.storage_artifact_bucket or None)
        deployment["storage"].setdefault("region", self.settings.storage_region or None)
        deployment["storage"].setdefault("endpoint_url", self.settings.storage_endpoint_url or None)
        deployment["storage"].setdefault("audit_artifact_prefix", self.settings.storage_audit_artifact_prefix)
        deployment["storage"].setdefault("safety_artifact_prefix", self.settings.storage_safety_artifact_prefix)
        deployment["storage"].setdefault("attachment_prefix", self.settings.storage_attachment_prefix)
        deployment["storage"].setdefault(
            "stage_remote_writes_locally",
            self.settings.storage_stage_remote_writes_locally,
        )

        deployment["secrets"].setdefault("backend", self.settings.secret_backend)
        deployment["secrets"].setdefault("namespace", self.settings.managed_secret_namespace)
        deployment["secrets"].setdefault("prefix", self.settings.managed_secret_prefix or None)
        deployment["secrets"].setdefault(
            "managed_secret_keys",
            [
                "OPENAI_API_KEY",
                "AUTH_SESSION_SECRET",
                "STORAGE_ACCESS_KEY_ID",
                "STORAGE_SECRET_ACCESS_KEY",
            ],
        )

        deployment["queue_hardening"].setdefault("max_attempts", self.settings.queue_max_attempts)
        deployment["queue_hardening"].setdefault(
            "dead_letter_enabled",
            self.settings.queue_dead_letter_enabled,
        )
        deployment["queue_hardening"].setdefault("max_inflight", self.settings.queue_max_inflight)
        deployment["queue_hardening"].setdefault(
            "visibility_timeout_seconds",
            self.settings.queue_visibility_timeout_seconds,
        )
        deployment["queue_hardening"].setdefault(
            "enforce_idempotency",
            self.settings.queue_enforce_idempotency,
        )
        deployment["queue_hardening"].setdefault(
            "temporal_namespace",
            self.settings.temporal_namespace,
        )
        deployment["queue_hardening"].setdefault(
            "temporal_task_queue",
            self.settings.temporal_task_queue,
        )

        deployment["file_handling"].setdefault(
            "max_attachment_bytes",
            self.settings.file_max_attachment_bytes,
        )
        deployment["file_handling"].setdefault(
            "allowed_attachment_content_types",
            self.settings.file_allowed_attachment_content_types_list,
        )
        deployment["file_handling"].setdefault("sanitize_filenames", True)
        deployment["file_handling"].setdefault(
            "quarantine_prefix",
            self.settings.file_quarantine_prefix,
        )

        deployment["cloud"].setdefault("deployment_profile", self.settings.cloud_deployment_profile)
        deployment["cloud"].setdefault("config_source", self.settings.cloud_config_source)
        deployment["cloud"].setdefault("object_storage_mode", self.settings.storage_provider)

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
        governance.setdefault("storage_policy_overrides", {})
        governance.setdefault("queue_hardening_overrides", {})
        governance.setdefault("file_handling_overrides", {})
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
            change_note="Bootstrap Pack 2/3 governance settings",
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

        effective.setdefault("deployment", {})
        effective["deployment"].setdefault("storage", {})
        effective["deployment"].setdefault("secrets", {})
        effective["deployment"].setdefault("queue_hardening", {})
        effective["deployment"].setdefault("file_handling", {})
        effective["deployment"].setdefault("cloud", {})

        if organization_id:
            organization_row = await self.get_organization_settings(organization_id)
            organization_payload = deepcopy(organization_row.payload_json)

            organization_governance = organization_payload.get("governance", {})
            escalation_overrides = organization_governance.get("escalation_policy_overrides", {})
            provider_overrides = organization_governance.get("model_provider_policy_overrides", {})
            feature_flags = organization_governance.get("feature_flags", {})
            storage_overrides = organization_governance.get("storage_policy_overrides", {})
            queue_overrides = organization_governance.get("queue_hardening_overrides", {})
            file_overrides = organization_governance.get("file_handling_overrides", {})

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
            if isinstance(storage_overrides, dict):
                effective["deployment"]["storage"] = self._deep_merge(
                    effective["deployment"]["storage"],
                    storage_overrides,
                )
            if isinstance(queue_overrides, dict):
                effective["deployment"]["queue_hardening"] = self._deep_merge(
                    effective["deployment"]["queue_hardening"],
                    queue_overrides,
                )
            if isinstance(file_overrides, dict):
                effective["deployment"]["file_handling"] = self._deep_merge(
                    effective["deployment"]["file_handling"],
                    file_overrides,
                )

        return {
            "deployment_name": self.settings.deployment_name,
            "organization_id": organization_id,
            "deployment_settings": deployment_payload,
            "organization_settings": organization_payload,
            "effective_settings": effective,
        }