export type ExternalIntegrationCatalogField = {
  key: string;
  label: string;
  required: boolean;
  secret: boolean;
  placeholder?: string | null;
};

export type ExternalIntegrationCatalogItem = {
  integration_key: string;
  provider_key: string;
  display_name: string;
  category: string;
  adapter_type: string;
  description: string;
  sync_supported: boolean;
  manual_ingest_supported: boolean;
  consent_required: boolean;
  enabled: boolean;
  config_fields: ExternalIntegrationCatalogField[];
};

export type ExternalIntegrationConnection = {
  id: string;
  user_id: string;
  organization_id?: string | null;
  integration_key: string;
  provider_key: string;
  category: string;
  connection_status: string;
  consent_status: string;
  access_scope_json?: Record<string, unknown> | null;
  config_json?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
  consented_at?: string | null;
  revoked_at?: string | null;
  last_synced_at?: string | null;
  last_sync_status?: string | null;
  last_error?: string | null;
  created_at: string;
  updated_at: string;
};

export type ExternalSyncJob = {
  id: string;
  connection_id: string;
  user_id: string;
  organization_id?: string | null;
  integration_key: string;
  provider_key: string;
  job_type: string;
  status: string;
  requested_by?: string | null;
  scheduled_at?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  sync_window_start?: string | null;
  sync_window_end?: string | null;
  signal_count: number;
  cursor_json?: Record<string, unknown> | null;
  request_payload_json?: Record<string, unknown> | null;
  result_payload_json?: Record<string, unknown> | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
};

export type ExternalSignal = {
  id: string;
  connection_id: string;
  user_id: string;
  organization_id?: string | null;
  integration_key: string;
  provider_key: string;
  signal_type: string;
  source_item_id: string;
  signal_at?: string | null;
  signal_start_at?: string | null;
  signal_end_at?: string | null;
  numeric_value?: number | null;
  text_value?: string | null;
  unit?: string | null;
  signal_payload_json?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type UserExternalIntegrationStatus = {
  user_id: string;
  organization_id?: string | null;
  boundary_policy: Record<string, unknown>;
  catalog: ExternalIntegrationCatalogItem[];
  connections: ExternalIntegrationConnection[];
  recent_sync_jobs: ExternalSyncJob[];
  recent_signals: ExternalSignal[];
  signal_breakdown_by_type: Record<string, number>;
};

export type AdminExternalIntegrationOverview = {
  deployment_name: string;
  organization_id?: string | null;
  boundary_policy: Record<string, unknown>;
  catalog: ExternalIntegrationCatalogItem[];
  total_connections: number;
  active_connections: number;
  consented_connections: number;
  total_sync_jobs: number;
  queued_sync_jobs: number;
  failed_sync_jobs: number;
  total_signals: number;
  connection_breakdown_by_provider: Record<string, number>;
  signal_breakdown_by_type: Record<string, number>;
  recent_sync_jobs: ExternalSyncJob[];
};

export type ExternalIntegrationConnectionUpsertPayload = {
  integration_key: string;
  provider_key: string;
  consent_status?: string;
  access_scope_json?: Record<string, unknown> | null;
  config_json?: Record<string, unknown> | null;
  metadata_json?: Record<string, unknown> | null;
};

export type ExternalIntegrationSyncPayload = {
  job_type?: string;
  sync_window_days?: number | null;
  request_payload_json?: Record<string, unknown> | null;
};

export type ExternalIntegrationIngestPayload = {
  source_label?: string;
  payload_json: Record<string, unknown>;
};

export type ExternalIntegrationIngestResponse = {
  connection: ExternalIntegrationConnection;
  job: ExternalSyncJob;
  normalized_signal_count: number;
  signal_type_breakdown: Record<string, number>;
};