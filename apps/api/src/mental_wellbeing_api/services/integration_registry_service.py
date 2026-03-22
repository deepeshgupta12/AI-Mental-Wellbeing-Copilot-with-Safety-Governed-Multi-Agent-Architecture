from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.audit_log import AuditLog
from mental_wellbeing_api.models.follow_up_event import FollowUpEvent
from mental_wellbeing_api.models.safety_event import SafetyEvent
from mental_wellbeing_api.models.stored_artifact import StoredArtifact
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService
from mental_wellbeing_api.services.infrastructure_governance_service import (
    InfrastructureGovernanceService,
)


class IntegrationRegistryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.enterprise_settings = EnterpriseSettingsService(session)
        self.infrastructure = InfrastructureGovernanceService(session)

    def _registry_items(self) -> list[dict[str, Any]]:
        return [
            {
                "integration_key": "enterprise_context_api",
                "display_name": "Enterprise Context API",
                "category": "auth_context",
                "status": "ready",
                "adapter_type": "internal_http",
                "description": "Provides authenticated enterprise/user/request context for internal and external orchestration layers.",
                "config_placeholders": [
                    {
                        "key": "base_url",
                        "label": "Base URL",
                        "required": True,
                        "secret": False,
                        "placeholder": "/api/v1/enterprise/context",
                    },
                    {
                        "key": "bearer_token",
                        "label": "Bearer Token",
                        "required": True,
                        "secret": True,
                        "placeholder": "integration-token",
                    },
                ],
                "health": {
                    "status": "healthy",
                    "sync_enabled": False,
                    "last_sync_at": None,
                    "last_error": None,
                },
                "audit_hooks": [
                    {
                        "action": "context_requested",
                        "event_type": "integration.context.requested",
                        "enabled": True,
                    }
                ],
            },
            {
                "integration_key": "enterprise_governance_feed",
                "display_name": "Enterprise Governance Feed",
                "category": "governance",
                "status": "ready",
                "adapter_type": "internal_http",
                "description": "Exports resolved governance settings, feature flags, escalation policy, and model routing posture.",
                "config_placeholders": [
                    {
                        "key": "organization_id",
                        "label": "Organization ID",
                        "required": False,
                        "secret": False,
                        "placeholder": "org-uuid",
                    }
                ],
                "health": {
                    "status": "healthy",
                    "sync_enabled": True,
                    "last_sync_at": None,
                    "last_error": None,
                },
                "audit_hooks": [
                    {
                        "action": "settings_exported",
                        "event_type": "integration.governance.exported",
                        "enabled": True,
                    }
                ],
            },
            {
                "integration_key": "artifact_manifest_export",
                "display_name": "Artifact Manifest Export",
                "category": "storage",
                "status": "ready",
                "adapter_type": "object_storage_manifest",
                "description": "Exposes audit, safety, and attachment manifests through stored artifact inventory endpoints.",
                "config_placeholders": [
                    {
                        "key": "scope_type",
                        "label": "Scope Type",
                        "required": False,
                        "secret": False,
                        "placeholder": "audit_log | safety_event | safety_review",
                    },
                    {
                        "key": "artifact_prefix",
                        "label": "Artifact Prefix",
                        "required": False,
                        "secret": False,
                        "placeholder": "audit-artifacts",
                    },
                ],
                "health": {
                    "status": "healthy",
                    "sync_enabled": True,
                    "last_sync_at": None,
                    "last_error": None,
                },
                "audit_hooks": [
                    {
                        "action": "artifact_list_requested",
                        "event_type": "integration.artifacts.listed",
                        "enabled": True,
                    },
                    {
                        "action": "artifact_drilldown_requested",
                        "event_type": "integration.artifacts.drilldown_requested",
                        "enabled": True,
                    },
                ],
            },
            {
                "integration_key": "enterprise_analytics_export",
                "display_name": "Enterprise Analytics Export",
                "category": "analytics",
                "status": "ready",
                "adapter_type": "internal_http",
                "description": "Provides org-aware operational KPIs, reviewer productivity, safety rollups, and activity trend feeds.",
                "config_placeholders": [
                    {
                        "key": "window_days",
                        "label": "Trend Window Days",
                        "required": False,
                        "secret": False,
                        "placeholder": "30",
                    },
                    {
                        "key": "organization_id",
                        "label": "Organization ID",
                        "required": False,
                        "secret": False,
                        "placeholder": "org-uuid",
                    },
                ],
                "health": {
                    "status": "healthy",
                    "sync_enabled": True,
                    "last_sync_at": None,
                    "last_error": None,
                },
                "audit_hooks": [
                    {
                        "action": "analytics_feed_requested",
                        "event_type": "integration.analytics.feed_requested",
                        "enabled": True,
                    }
                ],
            },
        ]

    def _endpoint_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "enterprise_context",
                "path": "/api/v1/enterprise/context",
                "method": "GET",
                "category": "auth_context",
            },
            {
                "name": "resolved_enterprise_settings",
                "path": "/api/v1/enterprise/settings/resolved",
                "method": "GET",
                "category": "governance",
            },
            {
                "name": "admin_infrastructure_summary",
                "path": "/api/v1/admin/settings/infrastructure/summary",
                "method": "GET",
                "category": "infrastructure",
            },
            {
                "name": "admin_stored_artifacts",
                "path": "/api/v1/admin/settings/infrastructure/artifacts",
                "method": "GET",
                "category": "storage",
            },
            {
                "name": "admin_enterprise_analytics_overview",
                "path": "/api/v1/admin/enterprise-analytics/overview",
                "method": "GET",
                "category": "analytics",
            },
            {
                "name": "admin_enterprise_organization_detail",
                "path": "/api/v1/admin/enterprise-analytics/organizations/{organization_id}",
                "method": "GET",
                "category": "analytics",
            },
            {
                "name": "admin_enterprise_reviewer_productivity",
                "path": "/api/v1/admin/enterprise-analytics/reviewer-productivity",
                "method": "GET",
                "category": "analytics",
            },
            {
                "name": "admin_integration_runtime_feed",
                "path": "/api/v1/admin/integrations/runtime-feed",
                "method": "GET",
                "category": "integrations",
            },
            {
                "name": "admin_integration_artifact_drilldown",
                "path": "/api/v1/admin/integrations/artifacts",
                "method": "GET",
                "category": "integrations",
            },
        ]

    async def _artifact_drilldown(self, *, limit: int = 20) -> list[dict[str, Any]]:
        rows = list(
            (
                await self.session.scalars(
                    select(StoredArtifact)
                    .order_by(desc(StoredArtifact.created_at))
                    .limit(limit)
                )
            ).all()
        )
        return [
            {
                "id": item.id,
                "scope_type": item.scope_type,
                "scope_id": item.scope_id,
                "artifact_kind": item.artifact_kind,
                "file_name": item.file_name,
                "storage_provider": item.storage_provider,
                "content_type": item.content_type,
                "storage_uri": item.storage_uri,
                "local_path": item.local_path,
                "byte_size": item.byte_size,
                "checksum_sha256": item.checksum_sha256,
                "created_at": item.created_at,
            }
            for item in rows
        ]

    async def build_overview(
        self,
        *,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        resolved = await self.enterprise_settings.resolve_settings(
            organization_id=organization_id
        )
        infra = await self.infrastructure.build_runtime_summary(
            organization_id=organization_id
        )
        effective = resolved.get("effective_settings", {})
        governance = effective.get("governance", {})
        provider_policy = governance.get("model_provider_policy", {})
        feature_flags = governance.get("feature_flags", {})

        integration_registry = self._registry_items()
        integration_endpoints = self._endpoint_catalog()

        return {
            "deployment_name": resolved["deployment_name"],
            "organization_id": organization_id,
            "auth_mode": effective.get("deployment", {}).get("auth_mode"),
            "storage_provider": infra["storage"]["provider"],
            "secret_backend": infra["secrets"]["backend"],
            "scheduler_backend": infra["queue"]["scheduler_backend"],
            "temporal_enabled": infra["queue"]["temporal_enabled"],
            "model_provider_policy": provider_policy
            if isinstance(provider_policy, dict)
            else {},
            "feature_flags": feature_flags if isinstance(feature_flags, dict) else {},
            "integration_endpoints": integration_endpoints,
            "integration_registry": integration_registry,
            "artifact_exports_enabled": True,
            "audit_exports_enabled": True,
            "safety_queue_enabled": True,
            "redacted": True,
        }

    async def build_runtime_feed(
        self,
        *,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        overview = await self.build_overview(organization_id=organization_id)

        total_artifacts = int(
            (await self.session.scalar(select(func.count(StoredArtifact.id)))) or 0
        )
        total_audit_logs = int(
            (await self.session.scalar(select(func.count(AuditLog.id)))) or 0
        )
        total_safety_events = int(
            (await self.session.scalar(select(func.count(SafetyEvent.id)))) or 0
        )
        total_follow_up_events = int(
            (await self.session.scalar(select(func.count(FollowUpEvent.id)))) or 0
        )

        artifact_rows = (
            await self.session.execute(
                select(
                    StoredArtifact.scope_type,
                    func.count(StoredArtifact.id).label("count"),
                )
                .group_by(StoredArtifact.scope_type)
                .order_by(desc("count"))
            )
        ).all()
        artifact_counts_by_scope = {
            str(row.scope_type): int(row.count or 0)
            for row in artifact_rows
            if row.scope_type
        }

        return {
            "generated_at": datetime.now(UTC),
            "deployment_name": overview["deployment_name"],
            "organization_id": organization_id,
            "capabilities": {
                "auth_context": True,
                "enterprise_governance": True,
                "storage_artifacts": True,
                "audit_logs": True,
                "safety_queue": True,
                "follow_up_events": True,
                "analytics_surfaces": True,
                "runtime_feed": True,
                "artifact_drilldown": True,
            },
            "counts": {
                "stored_artifacts": total_artifacts,
                "audit_logs": total_audit_logs,
                "safety_events": total_safety_events,
                "follow_up_events": total_follow_up_events,
            },
            "artifact_counts_by_scope": artifact_counts_by_scope,
            "model_routing": overview["model_provider_policy"],
            "endpoints": overview["integration_endpoints"],
            "integration_registry": overview["integration_registry"],
            "recent_artifacts": await self._artifact_drilldown(limit=12),
            "redacted": True,
        }

    async def list_artifact_drilldown(
        self,
        *,
        organization_id: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        return {
            "deployment_name": (await self.build_overview(organization_id=organization_id))[
                "deployment_name"
            ],
            "organization_id": organization_id,
            "artifacts": await self._artifact_drilldown(limit=limit),
            "redacted": True,
        }
