from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.core.config import get_settings
from mental_wellbeing_api.db.base import Base
from mental_wellbeing_api.models.stored_artifact import StoredArtifact


class StorageService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()

    async def ensure_artifact_table(self) -> None:
        conn = await self.session.connection()
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn,
                tables=[StoredArtifact.__table__],
                checkfirst=True,
            )
        )

    def _safe_segment(self, value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
        normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
        return normalized or "artifact"

    def _prefix_for_scope(self, scope_type: str) -> str:
        if scope_type == "audit_log":
            return self.settings.storage_audit_artifact_prefix
        if scope_type in {"safety_event", "safety_review"}:
            return self.settings.storage_safety_artifact_prefix
        return self.settings.storage_attachment_prefix

    def _build_object_key(
        self,
        *,
        scope_type: str,
        scope_id: str,
        artifact_kind: str,
        file_name: str,
    ) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        prefix = self._prefix_for_scope(scope_type)
        return "/".join(
            [
                self._safe_segment(prefix),
                self._safe_segment(scope_type),
                self._safe_segment(scope_id),
                f"{timestamp}-{self._safe_segment(artifact_kind)}-{self._safe_segment(file_name)}",
            ]
        )

    def _build_storage_uri(self, provider: str, object_key: str, local_path: str | None) -> str:
        if provider == "local":
            return f"file://{local_path}" if local_path else f"file://{object_key}"

        bucket = self.settings.storage_artifact_bucket.strip()
        if bucket:
            return f"s3://{bucket}/{object_key}"
        return f"s3://unconfigured/{object_key}"

    async def persist_json_artifact(
        self,
        *,
        scope_type: str,
        scope_id: str,
        artifact_kind: str,
        payload: dict[str, Any],
        file_name: str,
        metadata_json: dict[str, Any] | None = None,
    ) -> StoredArtifact:
        await self.ensure_artifact_table()

        provider = (self.settings.storage_provider or "local").strip().lower()
        safe_file_name = self._safe_segment(file_name)
        object_key = self._build_object_key(
            scope_type=scope_type,
            scope_id=scope_id,
            artifact_kind=artifact_kind,
            file_name=safe_file_name,
        )

        payload_bytes = json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            default=str,
        ).encode("utf-8")
        checksum = hashlib.sha256(payload_bytes).hexdigest()

        local_path: str | None = None
        if provider == "local" or self.settings.storage_stage_remote_writes_locally:
            root = self.settings.storage_local_root_path
            target_path = root / object_key
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(payload_bytes)
            local_path = str(target_path)

        row = StoredArtifact(
            scope_type=scope_type,
            scope_id=scope_id,
            artifact_kind=artifact_kind,
            file_name=safe_file_name,
            content_type="application/json",
            storage_provider=provider,
            bucket_name=self.settings.storage_artifact_bucket.strip() or None,
            object_key=object_key,
            storage_uri=self._build_storage_uri(provider, object_key, local_path),
            local_path=local_path,
            byte_size=len(payload_bytes),
            checksum_sha256=checksum,
            metadata_json=metadata_json or {},
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def list_artifacts(
        self,
        *,
        limit: int = 50,
        scope_type: str | None = None,
        scope_id: str | None = None,
        artifact_kind: str | None = None,
    ) -> list[StoredArtifact]:
        await self.ensure_artifact_table()

        stmt = select(StoredArtifact).order_by(desc(StoredArtifact.created_at)).limit(limit)

        if scope_type:
            stmt = stmt.where(StoredArtifact.scope_type == scope_type)
        if scope_id:
            stmt = stmt.where(StoredArtifact.scope_id == scope_id)
        if artifact_kind:
            stmt = stmt.where(StoredArtifact.artifact_kind == artifact_kind)

        result = await self.session.scalars(stmt)
        return list(result.all())