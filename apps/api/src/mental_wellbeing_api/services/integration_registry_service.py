from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
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
            "integration_endpoints": [
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
                    "name": "admin_integration_runtime_feed",
                    "path": "/api/v1/admin/integrations/runtime-feed",
                    "method": "GET",
                    "category": "integrations",
                },
            ],
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
            },
            "counts": {
                "stored_artifacts": total_artifacts,
                "audit_logs": total_audit_logs,
                "safety_events": total_safety_events,
                "follow_up_events": total_follow_up_events,
            },
            "model_routing": overview["model_provider_policy"],
            "endpoints": overview["integration_endpoints"],
            "redacted": True,
        }