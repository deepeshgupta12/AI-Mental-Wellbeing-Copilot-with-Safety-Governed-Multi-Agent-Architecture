import { apiRequest } from "@/lib/api-client";
import type {
  AdminExternalIntegrationOverview,
  ExternalIntegrationCatalogItem,
  ExternalIntegrationConnection,
  ExternalIntegrationConnectionUpsertPayload,
  ExternalIntegrationIngestPayload,
  ExternalIntegrationIngestResponse,
  ExternalSignal,
  ExternalSyncJob,
  ExternalIntegrationSyncPayload,
  UserExternalIntegrationStatus,
} from "@/types/external-integrations";

export function getAdminExternalIntegrationsOverview(
  organizationId?: string | null,
): Promise<AdminExternalIntegrationOverview> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminExternalIntegrationOverview>(
    `/api/v1/admin/external-integrations/overview${query}`,
  );
}

export function getAdminExternalIntegrationConnections(
  organizationId?: string | null,
): Promise<ExternalIntegrationConnection[]> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<ExternalIntegrationConnection[]>(
    `/api/v1/admin/external-integrations/connections${query}`,
  );
}

export function getAdminExternalIntegrationSyncJobs(
  organizationId?: string | null,
): Promise<ExternalSyncJob[]> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<ExternalSyncJob[]>(`/api/v1/admin/external-integrations/sync-jobs${query}`);
}

export function getAdminExternalIntegrationSignals(
  organizationId?: string | null,
): Promise<ExternalSignal[]> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<ExternalSignal[]>(`/api/v1/admin/external-integrations/signals${query}`);
}

export function getExternalIntegrationCatalog(): Promise<ExternalIntegrationCatalogItem[]> {
  return apiRequest<ExternalIntegrationCatalogItem[]>("/api/v1/external-integrations/catalog");
}

export function getMyExternalIntegrationStatus(): Promise<UserExternalIntegrationStatus> {
  return apiRequest<UserExternalIntegrationStatus>("/api/v1/external-integrations/me/status");
}

export function getMyExternalIntegrationConnections(): Promise<ExternalIntegrationConnection[]> {
  return apiRequest<ExternalIntegrationConnection[]>("/api/v1/external-integrations/me/connections");
}

export function upsertMyExternalIntegrationConnection(
  payload: ExternalIntegrationConnectionUpsertPayload,
): Promise<ExternalIntegrationConnection> {
  return apiRequest<ExternalIntegrationConnection>("/api/v1/external-integrations/me/connections", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function queueMyExternalIntegrationSync(
  connectionId: string,
  payload: ExternalIntegrationSyncPayload,
): Promise<ExternalSyncJob> {
  return apiRequest<ExternalSyncJob>(
    `/api/v1/external-integrations/me/connections/${connectionId}/sync`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function ingestMyExternalIntegrationPayload(
  connectionId: string,
  payload: ExternalIntegrationIngestPayload,
): Promise<ExternalIntegrationIngestResponse> {
  return apiRequest<ExternalIntegrationIngestResponse>(
    `/api/v1/external-integrations/me/connections/${connectionId}/ingest`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getMyExternalSignals(signalType?: string | null): Promise<ExternalSignal[]> {
  const query = signalType ? `?signal_type=${encodeURIComponent(signalType)}` : "";
  return apiRequest<ExternalSignal[]>(`/api/v1/external-integrations/me/signals${query}`);
}