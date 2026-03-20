from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StoredArtifactResponse(BaseModel):
    id: str
    scope_type: str
    scope_id: str
    artifact_kind: str
    file_name: str
    content_type: str
    storage_provider: str
    bucket_name: str | None = None
    object_key: str
    storage_uri: str
    local_path: str | None = None
    byte_size: int
    checksum_sha256: str
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RuntimeStorageSummaryResponse(BaseModel):
    provider: str
    local_root: str | None = None
    bucket_name: str | None = None
    region: str | None = None
    endpoint_url: str | None = None
    audit_artifact_prefix: str
    safety_artifact_prefix: str
    attachment_prefix: str
    stage_remote_writes_locally: bool
    artifact_base_uri: str
    write_mode: str


class RuntimeSecretsSummaryResponse(BaseModel):
    backend: str
    namespace: str | None = None
    prefix: str | None = None
    configured_keys: list[str] = Field(default_factory=list)
    missing_keys: list[str] = Field(default_factory=list)
    redacted: bool = True


class RuntimeQueueSummaryResponse(BaseModel):
    scheduler_backend: str
    temporal_enabled: bool
    temporal_namespace: str
    temporal_task_queue: str
    max_attempts: int
    dead_letter_enabled: bool
    max_inflight: int
    visibility_timeout_seconds: int
    enforce_idempotency: bool


class RuntimeFileHandlingSummaryResponse(BaseModel):
    max_attachment_bytes: int
    allowed_attachment_content_types: list[str] = Field(default_factory=list)
    sanitize_filenames: bool = True
    quarantine_prefix: str


class RuntimeCloudSummaryResponse(BaseModel):
    deployment_profile: str
    config_source: str
    object_storage_mode: str
    public_base_url: str | None = None


class InfrastructureRuntimeSummaryResponse(BaseModel):
    deployment_name: str
    organization_id: str | None = None
    storage: RuntimeStorageSummaryResponse
    secrets: RuntimeSecretsSummaryResponse
    queue: RuntimeQueueSummaryResponse
    file_handling: RuntimeFileHandlingSummaryResponse
    cloud: RuntimeCloudSummaryResponse