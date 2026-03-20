from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService
from mental_wellbeing_api.services.secret_manager_service import SecretManagerService
from mental_wellbeing_api.services.storage_service import StorageService


class InfrastructureGovernanceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.enterprise_settings = EnterpriseSettingsService(session)
        self.storage = StorageService(session)
        self.secrets = SecretManagerService()

    async def build_runtime_summary(
        self,
        *,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        resolved = await self.enterprise_settings.resolve_settings(organization_id=organization_id)
        effective = resolved.get("effective_settings", {})

        deployment = effective.get("deployment", {})
        storage_cfg = deployment.get("storage", {})
        secrets_cfg = deployment.get("secrets", {})
        queue_cfg = deployment.get("queue_hardening", {})
        file_cfg = deployment.get("file_handling", {})
        cloud_cfg = deployment.get("cloud", {})

        provider = str(storage_cfg.get("provider", self.settings.storage_provider)).lower()
        local_root = str(storage_cfg.get("local_root", str(self.settings.storage_local_root_path)))
        bucket_name = storage_cfg.get("bucket_name") or self.settings.storage_artifact_bucket or None

        if provider == "local":
            artifact_base_uri = f"file://{local_root}"
            write_mode = "local_filesystem"
        else:
            artifact_base_uri = (
                f"s3://{bucket_name}" if bucket_name else "s3://unconfigured"
            )
            write_mode = "remote_manifest_with_local_staging" if self.settings.storage_stage_remote_writes_locally else "remote_manifest_only"

        return {
            "deployment_name": resolved["deployment_name"],
            "organization_id": resolved["organization_id"],
            "storage": {
                "provider": provider,
                "local_root": local_root,
                "bucket_name": bucket_name,
                "region": storage_cfg.get("region") or self.settings.storage_region or None,
                "endpoint_url": storage_cfg.get("endpoint_url") or self.settings.storage_endpoint_url or None,
                "audit_artifact_prefix": storage_cfg.get(
                    "audit_artifact_prefix",
                    self.settings.storage_audit_artifact_prefix,
                ),
                "safety_artifact_prefix": storage_cfg.get(
                    "safety_artifact_prefix",
                    self.settings.storage_safety_artifact_prefix,
                ),
                "attachment_prefix": storage_cfg.get(
                    "attachment_prefix",
                    self.settings.storage_attachment_prefix,
                ),
                "stage_remote_writes_locally": bool(
                    storage_cfg.get(
                        "stage_remote_writes_locally",
                        self.settings.storage_stage_remote_writes_locally,
                    )
                ),
                "artifact_base_uri": artifact_base_uri,
                "write_mode": write_mode,
            },
            "secrets": self.secrets.build_runtime_summary(
                deployment_secrets_payload=secrets_cfg if isinstance(secrets_cfg, dict) else None,
            ),
            "queue": {
                "scheduler_backend": deployment.get("scheduler_backend", self.settings.scheduler_backend),
                "temporal_enabled": bool(
                    deployment.get("temporal_enabled", self.settings.temporal_enabled)
                ),
                "temporal_namespace": queue_cfg.get(
                    "temporal_namespace",
                    self.settings.temporal_namespace,
                ),
                "temporal_task_queue": queue_cfg.get(
                    "temporal_task_queue",
                    self.settings.temporal_task_queue,
                ),
                "max_attempts": int(
                    queue_cfg.get("max_attempts", self.settings.queue_max_attempts)
                ),
                "dead_letter_enabled": bool(
                    queue_cfg.get(
                        "dead_letter_enabled",
                        self.settings.queue_dead_letter_enabled,
                    )
                ),
                "max_inflight": int(
                    queue_cfg.get("max_inflight", self.settings.queue_max_inflight)
                ),
                "visibility_timeout_seconds": int(
                    queue_cfg.get(
                        "visibility_timeout_seconds",
                        self.settings.queue_visibility_timeout_seconds,
                    )
                ),
                "enforce_idempotency": bool(
                    queue_cfg.get(
                        "enforce_idempotency",
                        self.settings.queue_enforce_idempotency,
                    )
                ),
            },
            "file_handling": {
                "max_attachment_bytes": int(
                    file_cfg.get(
                        "max_attachment_bytes",
                        self.settings.file_max_attachment_bytes,
                    )
                ),
                "allowed_attachment_content_types": file_cfg.get(
                    "allowed_attachment_content_types",
                    self.settings.file_allowed_attachment_content_types_list,
                ),
                "sanitize_filenames": bool(file_cfg.get("sanitize_filenames", True)),
                "quarantine_prefix": file_cfg.get(
                    "quarantine_prefix",
                    self.settings.file_quarantine_prefix,
                ),
            },
            "cloud": {
                "deployment_profile": cloud_cfg.get(
                    "deployment_profile",
                    self.settings.cloud_deployment_profile,
                ),
                "config_source": cloud_cfg.get(
                    "config_source",
                    self.settings.cloud_config_source,
                ),
                "object_storage_mode": cloud_cfg.get(
                    "object_storage_mode",
                    provider,
                ),
                "public_base_url": self.settings.storage_public_base_url,
            },
        }

    async def list_recent_artifacts(
        self,
        *,
        limit: int = 50,
        scope_type: str | None = None,
        scope_id: str | None = None,
        artifact_kind: str | None = None,
    ):
        return await self.storage.list_artifacts(
            limit=limit,
            scope_type=scope_type,
            scope_id=scope_id,
            artifact_kind=artifact_kind,
        )