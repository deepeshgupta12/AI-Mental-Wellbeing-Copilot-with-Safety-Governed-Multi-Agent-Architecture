from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.db.base import Base
from mental_wellbeing_api.models.external_integration_connection import (
    ExternalIntegrationConnection,
)
from mental_wellbeing_api.models.external_signal import ExternalSignal
from mental_wellbeing_api.models.external_sync_job import ExternalSyncJob
from mental_wellbeing_api.services.audit_log_service import AuditLogService
from mental_wellbeing_api.services.enterprise_settings_service import EnterpriseSettingsService
from mental_wellbeing_api.services.external_provider_adapters import (
    ExternalProviderAdapterRegistry,
)
from mental_wellbeing_api.services.storage_service import StorageService


class ExternalIntegrationsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.audit = AuditLogService(session)
        self.storage = StorageService(session)
        self.enterprise_settings = EnterpriseSettingsService(session)
        self.registry = ExternalProviderAdapterRegistry()

    async def ensure_tables(self) -> None:
        conn = await self.session.connection()
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn,
                tables=[
                    ExternalIntegrationConnection.__table__,
                    ExternalSyncJob.__table__,
                    ExternalSignal.__table__,
                ],
                checkfirst=True,
            )
        )

    async def _boundary_policy(self, organization_id: str | None) -> dict[str, Any]:
        resolved = await self.enterprise_settings.resolve_settings(organization_id=organization_id)
        effective = resolved.get("effective_settings", {})
        governance = effective.get("governance", {})
        feature_flags = governance.get("feature_flags", {}) if isinstance(governance, dict) else {}

        enabled = bool(feature_flags.get("external_integrations_enabled", True))
        allowed_categories = feature_flags.get(
            "external_integrations_allowed_categories",
            ["calendar", "reminders", "wearable", "sleep"],
        )
        allowed_providers = feature_flags.get(
            "external_integrations_allowed_providers",
            [
                "google_calendar",
                "apple_reminders",
                "fitbit_wearable",
                "oura_sleep",
            ],
        )
        max_signals_per_ingest = int(
            feature_flags.get("external_integrations_max_signals_per_ingest", 250)
        )

        return {
            "enabled": enabled,
            "allowed_categories": allowed_categories if isinstance(allowed_categories, list) else [],
            "allowed_providers": allowed_providers if isinstance(allowed_providers, list) else [],
            "max_signals_per_ingest": max_signals_per_ingest,
            "audit_required": True,
            "organization_id": organization_id,
        }

    async def _validate_adapter_for_org(
        self,
        *,
        organization_id: str | None,
        provider_key: str,
    ) -> tuple[dict[str, Any], Any]:
        policy = await self._boundary_policy(organization_id)
        if not policy["enabled"]:
            raise PermissionError("External integrations are disabled for this organization.")

        adapter = self.registry.get(provider_key)
        if adapter.category not in set(policy["allowed_categories"]):
            raise PermissionError(f"Category not allowed for this organization: {adapter.category}")
        if adapter.provider_key not in set(policy["allowed_providers"]):
            raise PermissionError(f"Provider not allowed for this organization: {adapter.provider_key}")

        return policy, adapter

    async def catalog(self, organization_id: str | None = None) -> list[dict[str, Any]]:
        policy = await self._boundary_policy(organization_id)
        allowed_categories = set(policy["allowed_categories"])
        allowed_providers = set(policy["allowed_providers"])

        items: list[dict[str, Any]] = []
        for adapter in self.registry.all():
            entry = adapter.registry_item()
            entry["enabled"] = (
                bool(policy["enabled"])
                and adapter.category in allowed_categories
                and adapter.provider_key in allowed_providers
            )
            items.append(entry)
        return items

    async def list_connections(
        self,
        *,
        organization_id: str | None = None,
        user_id: str | None = None,
    ) -> list[ExternalIntegrationConnection]:
        await self.ensure_tables()

        stmt = (
            select(ExternalIntegrationConnection)
            .order_by(desc(ExternalIntegrationConnection.updated_at))
            .limit(200)
        )
        if organization_id:
            stmt = stmt.where(ExternalIntegrationConnection.organization_id == organization_id)
        if user_id:
            stmt = stmt.where(ExternalIntegrationConnection.user_id == user_id)

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def list_sync_jobs(
        self,
        *,
        organization_id: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
    ) -> list[ExternalSyncJob]:
        await self.ensure_tables()

        stmt = select(ExternalSyncJob).order_by(desc(ExternalSyncJob.created_at)).limit(limit)
        if organization_id:
            stmt = stmt.where(ExternalSyncJob.organization_id == organization_id)
        if user_id:
            stmt = stmt.where(ExternalSyncJob.user_id == user_id)

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def list_signals(
        self,
        *,
        organization_id: str | None = None,
        user_id: str | None = None,
        signal_type: str | None = None,
        limit: int = 100,
    ) -> list[ExternalSignal]:
        await self.ensure_tables()

        stmt = select(ExternalSignal).order_by(desc(ExternalSignal.created_at)).limit(limit)
        if organization_id:
            stmt = stmt.where(ExternalSignal.organization_id == organization_id)
        if user_id:
            stmt = stmt.where(ExternalSignal.user_id == user_id)
        if signal_type:
            stmt = stmt.where(ExternalSignal.signal_type == signal_type)

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_user_status(
        self,
        *,
        user_id: str,
        organization_id: str | None,
    ) -> dict[str, Any]:
        connections = await self.list_connections(user_id=user_id, organization_id=organization_id)
        recent_sync_jobs = await self.list_sync_jobs(
            user_id=user_id,
            organization_id=organization_id,
            limit=20,
        )
        recent_signals = await self.list_signals(
            user_id=user_id,
            organization_id=organization_id,
            limit=20,
        )
        signal_breakdown = Counter(item.signal_type for item in recent_signals if item.signal_type)

        return {
            "user_id": user_id,
            "organization_id": organization_id,
            "boundary_policy": await self._boundary_policy(organization_id),
            "catalog": await self.catalog(organization_id),
            "connections": connections,
            "recent_sync_jobs": recent_sync_jobs,
            "recent_signals": recent_signals,
            "signal_breakdown_by_type": dict(signal_breakdown),
        }

    async def upsert_connection(
        self,
        *,
        user_id: str,
        organization_id: str | None,
        payload: dict[str, Any],
        actor: str,
    ) -> ExternalIntegrationConnection:
        await self.ensure_tables()

        integration_key = str(payload.get("integration_key") or "")
        provider_key = str(payload.get("provider_key") or "")
        consent_status = str(payload.get("consent_status") or "active")

        if not integration_key:
            raise ValueError("integration_key is required")
        if not provider_key:
            raise ValueError("provider_key is required")

        _, adapter = await self._validate_adapter_for_org(
            organization_id=organization_id,
            provider_key=provider_key,
        )

        if integration_key != adapter.integration_key:
            raise ValueError(
                f"integration_key '{integration_key}' does not match provider contract '{adapter.integration_key}'"
            )

        item = await self.session.scalar(
            select(ExternalIntegrationConnection).where(
                ExternalIntegrationConnection.user_id == user_id,
                ExternalIntegrationConnection.integration_key == integration_key,
                ExternalIntegrationConnection.provider_key == provider_key,
            )
        )

        now = datetime.now(UTC)
        if item is None:
            item = ExternalIntegrationConnection(
                user_id=user_id,
                organization_id=organization_id,
                integration_key=integration_key,
                provider_key=provider_key,
                category=adapter.category,
                connection_status="active" if consent_status == "active" else "disabled",
                consent_status=consent_status,
                access_scope_json=payload.get("access_scope_json"),
                config_json=payload.get("config_json"),
                metadata_json=payload.get("metadata_json"),
                consented_at=now if consent_status == "active" else None,
                revoked_at=now if consent_status == "revoked" else None,
            )
            self.session.add(item)
        else:
            item.organization_id = organization_id
            item.category = adapter.category
            item.connection_status = "active" if consent_status == "active" else "disabled"
            item.consent_status = consent_status
            item.access_scope_json = payload.get("access_scope_json")
            item.config_json = payload.get("config_json")
            item.metadata_json = payload.get("metadata_json")
            if consent_status == "active":
                item.consented_at = item.consented_at or now
                item.revoked_at = None
            if consent_status == "revoked":
                item.revoked_at = now

        await self.session.commit()
        await self.session.refresh(item)

        await self.audit.create_log(
            event_type="external_integration_connection_upserted",
            entity_type="external_integration_connection",
            entity_id=item.id,
            title=f"External integration connection updated: {item.provider_key}",
            details=f"Consent status: {item.consent_status}",
            actor_type="user",
            actor_id=actor,
            user_id=item.user_id,
            event_payload_json={
                "organization_id": item.organization_id,
                "integration_key": item.integration_key,
                "provider_key": item.provider_key,
                "category": item.category,
                "consent_status": item.consent_status,
            },
        )

        return item

    async def create_sync_job(
        self,
        *,
        connection_id: str,
        user_id: str,
        organization_id: str | None,
        job_type: str,
        requested_by: str,
        sync_window_days: int | None,
        request_payload_json: dict[str, Any] | None,
    ) -> ExternalSyncJob:
        await self.ensure_tables()

        connection = await self.session.get(ExternalIntegrationConnection, connection_id)
        if connection is None:
            raise ValueError("External integration connection not found")
        if connection.user_id != user_id:
            raise PermissionError("Connection does not belong to the authenticated user")

        _, _ = await self._validate_adapter_for_org(
            organization_id=organization_id,
            provider_key=connection.provider_key,
        )

        now = datetime.now(UTC)
        window_start = now - timedelta(days=sync_window_days or 7)

        job = ExternalSyncJob(
            connection_id=connection.id,
            user_id=connection.user_id,
            organization_id=connection.organization_id,
            integration_key=connection.integration_key,
            provider_key=connection.provider_key,
            job_type=job_type,
            status="queued",
            requested_by=requested_by,
            scheduled_at=now,
            sync_window_start=window_start,
            sync_window_end=now,
            request_payload_json=request_payload_json or {},
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)

        await self.audit.create_log(
            event_type="external_sync_job_queued",
            entity_type="external_sync_job",
            entity_id=job.id,
            title=f"External sync job queued: {job.provider_key}",
            details=f"Job type: {job.job_type}",
            actor_type="user",
            actor_id=requested_by,
            user_id=job.user_id,
            event_payload_json={
                "organization_id": job.organization_id,
                "integration_key": job.integration_key,
                "provider_key": job.provider_key,
                "job_type": job.job_type,
            },
        )

        return job

    async def ingest_payload(
        self,
        *,
        connection_id: str,
        user_id: str,
        organization_id: str | None,
        payload_json: dict[str, Any],
        source_label: str,
        actor: str,
    ) -> dict[str, Any]:
        await self.ensure_tables()

        connection = await self.session.get(ExternalIntegrationConnection, connection_id)
        if connection is None:
            raise ValueError("External integration connection not found")
        if connection.user_id != user_id:
            raise PermissionError("Connection does not belong to the authenticated user")
        if connection.consent_status != "active":
            raise PermissionError("Consent must be active before ingestion can proceed")

        policy, adapter = await self._validate_adapter_for_org(
            organization_id=organization_id,
            provider_key=connection.provider_key,
        )

        job = ExternalSyncJob(
            connection_id=connection.id,
            user_id=connection.user_id,
            organization_id=connection.organization_id,
            integration_key=connection.integration_key,
            provider_key=connection.provider_key,
            job_type="manual_ingest",
            status="running",
            requested_by=actor,
            started_at=datetime.now(UTC),
            request_payload_json={
                "source_label": source_label,
                "payload_preview_keys": sorted(payload_json.keys()),
            },
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)

        try:
            normalized = adapter.normalize_payload(payload_json)
            if len(normalized) > int(policy["max_signals_per_ingest"]):
                raise ValueError(
                    f"Payload exceeds max_signals_per_ingest={policy['max_signals_per_ingest']}"
                )

            breakdown = Counter()
            for item in normalized:
                existing = await self.session.scalar(
                    select(ExternalSignal).where(
                        ExternalSignal.connection_id == connection.id,
                        ExternalSignal.signal_type == item.signal_type,
                        ExternalSignal.source_item_id == item.source_item_id,
                    )
                )

                if existing is None:
                    signal = ExternalSignal(
                        connection_id=connection.id,
                        user_id=connection.user_id,
                        organization_id=connection.organization_id,
                        integration_key=connection.integration_key,
                        provider_key=connection.provider_key,
                        signal_type=item.signal_type,
                        source_item_id=item.source_item_id,
                        signal_at=item.signal_at,
                        signal_start_at=item.signal_start_at,
                        signal_end_at=item.signal_end_at,
                        numeric_value=item.numeric_value,
                        text_value=item.text_value,
                        unit=item.unit,
                        signal_payload_json=item.signal_payload_json,
                    )
                    self.session.add(signal)
                else:
                    existing.signal_at = item.signal_at
                    existing.signal_start_at = item.signal_start_at
                    existing.signal_end_at = item.signal_end_at
                    existing.numeric_value = item.numeric_value
                    existing.text_value = item.text_value
                    existing.unit = item.unit
                    existing.signal_payload_json = item.signal_payload_json

                breakdown[item.signal_type] += 1

            connection.last_synced_at = datetime.now(UTC)
            connection.last_sync_status = "completed"
            connection.last_error = None

            job.status = "completed"
            job.finished_at = datetime.now(UTC)
            job.signal_count = len(normalized)
            job.result_payload_json = {
                "source_label": source_label,
                "normalized_signal_count": len(normalized),
                "signal_type_breakdown": dict(breakdown),
            }

            await self.session.commit()
            await self.session.refresh(connection)
            await self.session.refresh(job)

            await self.storage.persist_json_artifact(
                scope_type="external_sync_job",
                scope_id=job.id,
                artifact_kind="ingest_payload_json",
                file_name=f"external-ingest-{job.id}.json",
                payload=payload_json,
                metadata_json={
                    "organization_id": connection.organization_id,
                    "integration_key": connection.integration_key,
                    "provider_key": connection.provider_key,
                    "source_label": source_label,
                },
            )

            await self.audit.create_log(
                event_type="external_integration_payload_ingested",
                entity_type="external_sync_job",
                entity_id=job.id,
                title=f"External payload ingested: {connection.provider_key}",
                details=f"{len(normalized)} normalized signals created or updated",
                actor_type="user",
                actor_id=actor,
                user_id=connection.user_id,
                event_payload_json={
                    "organization_id": connection.organization_id,
                    "integration_key": connection.integration_key,
                    "provider_key": connection.provider_key,
                    "source_label": source_label,
                    "normalized_signal_count": len(normalized),
                    "signal_type_breakdown": dict(breakdown),
                },
            )

            return {
                "connection": connection,
                "job": job,
                "normalized_signal_count": len(normalized),
                "signal_type_breakdown": dict(breakdown),
            }
        except Exception as exc:
            connection.last_synced_at = datetime.now(UTC)
            connection.last_sync_status = "failed"
            connection.last_error = str(exc)

            job.status = "failed"
            job.finished_at = datetime.now(UTC)
            job.error_message = str(exc)
            job.result_payload_json = {
                "source_label": source_label,
                "status": "failed",
            }

            await self.session.commit()
            await self.session.refresh(connection)
            await self.session.refresh(job)

            await self.audit.create_log(
                event_type="external_integration_payload_failed",
                entity_type="external_sync_job",
                entity_id=job.id,
                title=f"External payload ingest failed: {connection.provider_key}",
                details=str(exc),
                actor_type="user",
                actor_id=actor,
                user_id=connection.user_id,
                event_payload_json={
                    "organization_id": connection.organization_id,
                    "integration_key": connection.integration_key,
                    "provider_key": connection.provider_key,
                    "source_label": source_label,
                    "error": str(exc),
                },
            )
            raise

    async def build_admin_overview(
        self,
        *,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        await self.ensure_tables()

        boundary_policy = await self._boundary_policy(organization_id)
        catalog = await self.catalog(organization_id)

        connection_stmt = select(func.count(ExternalIntegrationConnection.id))
        active_stmt = select(func.count(ExternalIntegrationConnection.id)).where(
            ExternalIntegrationConnection.connection_status == "active"
        )
        consented_stmt = select(func.count(ExternalIntegrationConnection.id)).where(
            ExternalIntegrationConnection.consent_status == "active"
        )
        job_stmt = select(func.count(ExternalSyncJob.id))
        queued_job_stmt = select(func.count(ExternalSyncJob.id)).where(
            ExternalSyncJob.status == "queued"
        )
        failed_job_stmt = select(func.count(ExternalSyncJob.id)).where(
            ExternalSyncJob.status == "failed"
        )
        signal_stmt = select(func.count(ExternalSignal.id))

        if organization_id:
            connection_stmt = connection_stmt.where(
                ExternalIntegrationConnection.organization_id == organization_id
            )
            active_stmt = active_stmt.where(
                ExternalIntegrationConnection.organization_id == organization_id
            )
            consented_stmt = consented_stmt.where(
                ExternalIntegrationConnection.organization_id == organization_id
            )
            job_stmt = job_stmt.where(ExternalSyncJob.organization_id == organization_id)
            queued_job_stmt = queued_job_stmt.where(
                ExternalSyncJob.organization_id == organization_id
            )
            failed_job_stmt = failed_job_stmt.where(
                ExternalSyncJob.organization_id == organization_id
            )
            signal_stmt = signal_stmt.where(ExternalSignal.organization_id == organization_id)

        provider_rows_stmt = (
            select(
                ExternalIntegrationConnection.provider_key,
                func.count(ExternalIntegrationConnection.id).label("count"),
            )
            .group_by(ExternalIntegrationConnection.provider_key)
            .order_by(desc("count"))
        )
        signal_rows_stmt = (
            select(
                ExternalSignal.signal_type,
                func.count(ExternalSignal.id).label("count"),
            )
            .group_by(ExternalSignal.signal_type)
            .order_by(desc("count"))
        )

        if organization_id:
            provider_rows_stmt = provider_rows_stmt.where(
                ExternalIntegrationConnection.organization_id == organization_id
            )
            signal_rows_stmt = signal_rows_stmt.where(
                ExternalSignal.organization_id == organization_id
            )

        provider_rows = (await self.session.execute(provider_rows_stmt)).all()
        signal_rows = (await self.session.execute(signal_rows_stmt)).all()

        recent_sync_jobs = await self.list_sync_jobs(
            organization_id=organization_id,
            limit=15,
        )

        return {
            "deployment_name": "local",
            "organization_id": organization_id,
            "boundary_policy": boundary_policy,
            "catalog": catalog,
            "total_connections": int((await self.session.scalar(connection_stmt)) or 0),
            "active_connections": int((await self.session.scalar(active_stmt)) or 0),
            "consented_connections": int((await self.session.scalar(consented_stmt)) or 0),
            "total_sync_jobs": int((await self.session.scalar(job_stmt)) or 0),
            "queued_sync_jobs": int((await self.session.scalar(queued_job_stmt)) or 0),
            "failed_sync_jobs": int((await self.session.scalar(failed_job_stmt)) or 0),
            "total_signals": int((await self.session.scalar(signal_stmt)) or 0),
            "connection_breakdown_by_provider": {
                str(row.provider_key): int(row.count or 0)
                for row in provider_rows
                if row.provider_key
            },
            "signal_breakdown_by_type": {
                str(row.signal_type): int(row.count or 0)
                for row in signal_rows
                if row.signal_type
            },
            "recent_sync_jobs": recent_sync_jobs,
        }