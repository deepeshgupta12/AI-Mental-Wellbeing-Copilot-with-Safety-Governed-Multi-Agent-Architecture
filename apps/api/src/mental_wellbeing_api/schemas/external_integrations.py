from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExternalIntegrationCatalogFieldResponse(BaseModel):
    key: str
    label: str
    required: bool = False
    secret: bool = False
    placeholder: str | None = None


class ExternalIntegrationCatalogItemResponse(BaseModel):
    integration_key: str
    provider_key: str
    display_name: str
    category: str
    adapter_type: str
    description: str
    sync_supported: bool = True
    manual_ingest_supported: bool = True
    consent_required: bool = True
    enabled: bool = True
    config_fields: list[ExternalIntegrationCatalogFieldResponse] = Field(default_factory=list)


class ExternalIntegrationConnectionResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str | None
    integration_key: str
    provider_key: str
    category: str
    connection_status: str
    consent_status: str
    access_scope_json: dict | None = None
    config_json: dict | None = None
    metadata_json: dict | None = None
    consented_at: datetime | None = None
    revoked_at: datetime | None = None
    last_synced_at: datetime | None = None
    last_sync_status: str | None = None
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExternalSyncJobResponse(BaseModel):
    id: str
    connection_id: str
    user_id: str
    organization_id: str | None
    integration_key: str
    provider_key: str
    job_type: str
    status: str
    requested_by: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    sync_window_start: datetime | None = None
    sync_window_end: datetime | None = None
    signal_count: int = 0
    cursor_json: dict | None = None
    request_payload_json: dict | None = None
    result_payload_json: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExternalSignalResponse(BaseModel):
    id: str
    connection_id: str
    user_id: str
    organization_id: str | None
    integration_key: str
    provider_key: str
    signal_type: str
    source_item_id: str
    signal_at: datetime | None = None
    signal_start_at: datetime | None = None
    signal_end_at: datetime | None = None
    numeric_value: float | None = None
    text_value: str | None = None
    unit: str | None = None
    signal_payload_json: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExternalIntegrationConnectionUpsertRequest(BaseModel):
    integration_key: str
    provider_key: str
    consent_status: str = "active"
    access_scope_json: dict[str, Any] | None = None
    config_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class ExternalIntegrationSyncRequest(BaseModel):
    job_type: str = "manual_sync"
    sync_window_days: int | None = Field(default=7, ge=1, le=90)
    request_payload_json: dict[str, Any] | None = None


class ExternalIntegrationIngestRequest(BaseModel):
    source_label: str = "manual_ingest"
    payload_json: dict[str, Any]


class ExternalIntegrationIngestResponse(BaseModel):
    connection: ExternalIntegrationConnectionResponse
    job: ExternalSyncJobResponse
    normalized_signal_count: int
    signal_type_breakdown: dict[str, int] = Field(default_factory=dict)


class UserExternalIntegrationStatusResponse(BaseModel):
    user_id: str
    organization_id: str | None = None
    boundary_policy: dict[str, Any] = Field(default_factory=dict)
    catalog: list[ExternalIntegrationCatalogItemResponse] = Field(default_factory=list)
    connections: list[ExternalIntegrationConnectionResponse] = Field(default_factory=list)
    recent_sync_jobs: list[ExternalSyncJobResponse] = Field(default_factory=list)
    recent_signals: list[ExternalSignalResponse] = Field(default_factory=list)
    signal_breakdown_by_type: dict[str, int] = Field(default_factory=dict)


class AdminExternalIntegrationOverviewResponse(BaseModel):
    deployment_name: str
    organization_id: str | None = None
    boundary_policy: dict[str, Any] = Field(default_factory=dict)
    catalog: list[ExternalIntegrationCatalogItemResponse] = Field(default_factory=list)
    total_connections: int = 0
    active_connections: int = 0
    consented_connections: int = 0
    total_sync_jobs: int = 0
    queued_sync_jobs: int = 0
    failed_sync_jobs: int = 0
    total_signals: int = 0
    connection_breakdown_by_provider: dict[str, int] = Field(default_factory=dict)
    signal_breakdown_by_type: dict[str, int] = Field(default_factory=dict)
    recent_sync_jobs: list[ExternalSyncJobResponse] = Field(default_factory=list)