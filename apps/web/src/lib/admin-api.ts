import { apiRequest } from "@/lib/api-client";
import type {
  AdminAnalyticsOverview,
  AdminAuditItem,
  AdminAuditLog,
  AdminConfigAudit,
  AdminConfigDiff,
  AdminConfigVersion,
  AdminEnterpriseAnalyticsOverview,
  AdminEnterpriseOrganizationDetail,
  AdminEscalationAnalytics,
  AdminIntegrationArtifactDrilldown,
  AdminFlaggedSession,
  AdminFlaggedSessionDetail,
  AdminIntegrationOverview,
  AdminIntegrationRuntimeFeed,
  AdminOrganizationSummary,
  AdminReviewerProductivityOverview,
  AdminInterventionLog,
  AdminInterventionOverview,
  AdminOpsOverview,
  AdminPolicyConfig,
  AdminReviewerDashboard,
  AdminRoutingRulesResponse,
  AdminSafetyEvent,
  AdminSafetyEventDetail,
  AdminSafetyReview,
  AdminSafetyReviewCreatePayload,
  AdminTraceExecutionDetail,
  AdminTraceExecutionSummary,
  AdminTraceItem,
  EnterpriseSetting,
  ResolvedEnterpriseSettings,
} from "@/types/api";

export type AdminInfrastructureSummary = {
  deployment_name: string;
  organization_id?: string | null;
  storage: {
    provider: string;
    local_root?: string | null;
    bucket_name?: string | null;
    region?: string | null;
    endpoint_url?: string | null;
    audit_artifact_prefix: string;
    safety_artifact_prefix: string;
    attachment_prefix: string;
    stage_remote_writes_locally: boolean;
    artifact_base_uri: string;
    write_mode: string;
  };
  secrets: {
    backend: string;
    namespace?: string | null;
    prefix?: string | null;
    configured_keys: string[];
    missing_keys: string[];
    redacted: boolean;
  };
  queue: {
    scheduler_backend: string;
    temporal_enabled: boolean;
    temporal_namespace: string;
    temporal_task_queue: string;
    max_attempts: number;
    dead_letter_enabled: boolean;
    max_inflight: number;
    visibility_timeout_seconds: number;
    enforce_idempotency: boolean;
  };
  file_handling: {
    max_attachment_bytes: number;
    allowed_attachment_content_types: string[];
    sanitize_filenames: boolean;
    quarantine_prefix: string;
  };
  cloud: {
    deployment_profile: string;
    config_source: string;
    object_storage_mode: string;
    public_base_url?: string | null;
  };
};

export type StoredArtifact = {
  id: string;
  scope_type: string;
  scope_id: string;
  artifact_kind: string;
  file_name: string;
  content_type: string;
  storage_provider: string;
  bucket_name?: string | null;
  object_key: string;
  storage_uri: string;
  local_path?: string | null;
  byte_size: number;
  checksum_sha256: string;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
};

export function getAdminFlaggedSessions(): Promise<AdminFlaggedSession[]> {
  return apiRequest<AdminFlaggedSession[]>("/api/v1/admin/flagged-sessions");
}

export function getAdminFlaggedSessionDetail(flagId: string): Promise<AdminFlaggedSessionDetail> {
  return apiRequest<AdminFlaggedSessionDetail>(`/api/v1/admin/flagged-sessions/${flagId}`);
}

export function getAdminAuditTrail(): Promise<AdminAuditItem[]> {
  return apiRequest<AdminAuditItem[]>("/api/v1/admin/audit-trail");
}

export function getAdminPolicyConfig(): Promise<AdminPolicyConfig> {
  return apiRequest<AdminPolicyConfig>("/api/v1/admin/policy-config");
}

export function getAdminAgentTraces(): Promise<AdminTraceItem[]> {
  return apiRequest<AdminTraceItem[]>("/api/v1/admin/agent-traces");
}

export function getAdminAgentTraceExecutions(): Promise<AdminTraceExecutionSummary[]> {
  return apiRequest<AdminTraceExecutionSummary[]>("/api/v1/admin/agent-trace-executions");
}

export function getAdminAgentTraceExecutionDetail(
  traceName: string,
): Promise<AdminTraceExecutionDetail> {
  return apiRequest<AdminTraceExecutionDetail>(
    `/api/v1/admin/agent-trace-executions/${encodeURIComponent(traceName)}`,
  );
}

export function getAdminInterventionLogs(): Promise<AdminInterventionLog[]> {
  return apiRequest<AdminInterventionLog[]>("/api/v1/admin/intervention-logs");
}

export function getAdminInterventionOverview(): Promise<AdminInterventionOverview> {
  return apiRequest<AdminInterventionOverview>("/api/v1/admin/intervention-overview");
}

export function getAdminRoutingRules(): Promise<AdminRoutingRulesResponse> {
  return apiRequest<AdminRoutingRulesResponse>("/api/v1/admin/routing-rules");
}

export function updateAdminRoutingRules(
  payloadJson: Record<string, unknown>,
  changeNote?: string | null,
): Promise<AdminConfigVersion> {
  return apiRequest<AdminConfigVersion>("/api/v1/admin/routing-rules", {
    method: "PUT",
    body: JSON.stringify({
      payload_json: payloadJson,
      change_note: changeNote ?? null,
      actor: "admin-ui",
    }),
  });
}

export function getAdminRuntimePolicyVersions(): Promise<AdminConfigVersion[]> {
  return apiRequest<AdminConfigVersion[]>("/api/v1/admin/runtime-policy/versions");
}

export function getAdminPromptRegistryVersions(): Promise<AdminConfigVersion[]> {
  return apiRequest<AdminConfigVersion[]>("/api/v1/admin/prompt-registry/versions");
}

export function updateAdminRuntimePolicy(
  payloadJson: Record<string, unknown>,
  changeNote?: string | null,
): Promise<AdminConfigVersion> {
  return apiRequest<AdminConfigVersion>("/api/v1/admin/runtime-policy", {
    method: "PUT",
    body: JSON.stringify({
      payload_json: payloadJson,
      change_note: changeNote ?? null,
      actor: "admin-ui",
    }),
  });
}

export function updateAdminPromptRegistry(
  payloadJson: Record<string, unknown>,
  changeNote?: string | null,
): Promise<AdminConfigVersion> {
  return apiRequest<AdminConfigVersion>("/api/v1/admin/prompt-registry", {
    method: "PUT",
    body: JSON.stringify({
      payload_json: payloadJson,
      change_note: changeNote ?? null,
      actor: "admin-ui",
    }),
  });
}

export function getAdminConfigAudit(configKey?: string): Promise<AdminConfigAudit[]> {
  const query = configKey ? `?config_key=${encodeURIComponent(configKey)}` : "";
  return apiRequest<AdminConfigAudit[]>(`/api/v1/admin/config-audit${query}`);
}

export function getAdminConfigDiff(
  configKey: string,
  fromVersionId: string,
  toVersionId: string,
): Promise<AdminConfigDiff> {
  const params = new URLSearchParams({
    config_key: configKey,
    from_version_id: fromVersionId,
    to_version_id: toVersionId,
  });
  return apiRequest<AdminConfigDiff>(`/api/v1/admin/config-diff?${params.toString()}`);
}

export function getAdminOpsOverview(): Promise<AdminOpsOverview> {
  return apiRequest<AdminOpsOverview>("/api/v1/admin/ops-overview");
}

export function getAdminAnalyticsOverview(): Promise<AdminAnalyticsOverview> {
  return apiRequest<AdminAnalyticsOverview>("/api/v1/admin/analytics/overview");
}

export function getAdminSafetyEvents(params?: {
  queueStatus?: string;
  riskLevel?: string;
}): Promise<AdminSafetyEvent[]> {
  const search = new URLSearchParams();
  if (params?.queueStatus) search.set("queue_status", params.queueStatus);
  if (params?.riskLevel) search.set("risk_level", params.riskLevel);
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<AdminSafetyEvent[]>(`/api/v1/admin/safety-events${suffix}`);
}

export function getAdminSafetyEventDetail(
  safetyEventId: string,
): Promise<AdminSafetyEventDetail> {
  return apiRequest<AdminSafetyEventDetail>(`/api/v1/admin/safety-events/${safetyEventId}`);
}

export function getAdminSafetyEventReviews(
  safetyEventId: string,
): Promise<AdminSafetyReview[]> {
  return apiRequest<AdminSafetyReview[]>(
    `/api/v1/admin/safety-events/${safetyEventId}/reviews`,
  );
}

export function createAdminSafetyEventReview(
  safetyEventId: string,
  payload: AdminSafetyReviewCreatePayload,
): Promise<AdminSafetyReview> {
  return apiRequest<AdminSafetyReview>(
    `/api/v1/admin/safety-events/${safetyEventId}/reviews`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getAdminReviewerDashboard(): Promise<AdminReviewerDashboard> {
  return apiRequest<AdminReviewerDashboard>("/api/v1/admin/reviewer-dashboard");
}

export function getAdminEscalationAnalytics(): Promise<AdminEscalationAnalytics> {
  return apiRequest<AdminEscalationAnalytics>("/api/v1/admin/escalation-analytics");
}

export function getAdminAuditTimeline(): Promise<AdminAuditLog[]> {
  return apiRequest<AdminAuditLog[]>("/api/v1/admin/audit-timeline");
}

export function getAdminDeploymentSettings(): Promise<EnterpriseSetting> {
  return apiRequest<EnterpriseSetting>("/api/v1/admin/settings/deployment/current");
}

export function updateAdminDeploymentSettings(
  payloadJson: Record<string, unknown>,
  changeNote?: string | null,
): Promise<EnterpriseSetting> {
  return apiRequest<EnterpriseSetting>("/api/v1/admin/settings/deployment/current", {
    method: "PUT",
    body: JSON.stringify({
      payload_json: payloadJson,
      change_note: changeNote ?? null,
    }),
  });
}

export function getAdminOrganizationSettings(organizationId: string): Promise<EnterpriseSetting> {
  return apiRequest<EnterpriseSetting>(`/api/v1/admin/settings/organizations/${organizationId}`);
}

export function updateAdminOrganizationSettings(
  organizationId: string,
  payloadJson: Record<string, unknown>,
  changeNote?: string | null,
): Promise<EnterpriseSetting> {
  return apiRequest<EnterpriseSetting>(`/api/v1/admin/settings/organizations/${organizationId}`, {
    method: "PUT",
    body: JSON.stringify({
      payload_json: payloadJson,
      change_note: changeNote ?? null,
    }),
  });
}

export function getAdminResolvedEnterpriseSettings(
  organizationId?: string | null,
): Promise<ResolvedEnterpriseSettings> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<ResolvedEnterpriseSettings>(`/api/v1/admin/settings/resolved${query}`);
}

export function getAdminInfrastructureSummary(
  organizationId?: string | null,
): Promise<AdminInfrastructureSummary> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminInfrastructureSummary>(
    `/api/v1/admin/settings/infrastructure/summary${query}`,
  );
}

export function getAdminStoredArtifacts(params?: {
  limit?: number;
  scopeType?: string;
  scopeId?: string;
  artifactKind?: string;
}): Promise<StoredArtifact[]> {
  const search = new URLSearchParams();
  if (params?.limit) search.set("limit", String(params.limit));
  if (params?.scopeType) search.set("scope_type", params.scopeType);
  if (params?.scopeId) search.set("scope_id", params.scopeId);
  if (params?.artifactKind) search.set("artifact_kind", params.artifactKind);

  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<StoredArtifact[]>(`/api/v1/admin/settings/infrastructure/artifacts${suffix}`);
}

export function getAdminEnterpriseAnalyticsOverview(
  organizationId?: string | null,
  days = 30,
): Promise<AdminEnterpriseAnalyticsOverview> {
  const search = new URLSearchParams();
  if (organizationId) search.set("organization_id", organizationId);
  search.set("days", String(days));
  return apiRequest<AdminEnterpriseAnalyticsOverview>(
    `/api/v1/admin/enterprise-analytics/overview?${search.toString()}`,
  );
}

export function getAdminEnterpriseOrganizations(): Promise<AdminOrganizationSummary[]> {
  return apiRequest<AdminOrganizationSummary[]>("/api/v1/admin/enterprise-analytics/organizations");
}

export function getAdminEnterpriseOrganizationDetail(
  organizationId: string,
  days = 30,
): Promise<AdminEnterpriseOrganizationDetail> {
  return apiRequest<AdminEnterpriseOrganizationDetail>(
    `/api/v1/admin/enterprise-analytics/organizations/${organizationId}?days=${days}`,
  );
}

export function getAdminReviewerProductivityOverview(
  organizationId: string,
  days = 30,
): Promise<AdminReviewerProductivityOverview> {
  const search = new URLSearchParams({ organization_id: organizationId, days: String(days) });
  return apiRequest<AdminReviewerProductivityOverview>(
    `/api/v1/admin/enterprise-analytics/reviewer-productivity?${search.toString()}`,
  );
}

export function getAdminIntegrationOverview(
  organizationId?: string | null,
): Promise<AdminIntegrationOverview> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminIntegrationOverview>(`/api/v1/admin/integrations/overview${query}`);
}

export function getAdminIntegrationRuntimeFeed(
  organizationId?: string | null,
): Promise<AdminIntegrationRuntimeFeed> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminIntegrationRuntimeFeed>(`/api/v1/admin/integrations/runtime-feed${query}`);
}

export function getAdminIntegrationArtifactDrilldown(params?: {
  organizationId?: string | null;
  limit?: number;
}): Promise<AdminIntegrationArtifactDrilldown> {
  const search = new URLSearchParams();
  if (params?.organizationId) search.set("organization_id", params.organizationId);
  if (params?.limit) search.set("limit", String(params.limit));
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<AdminIntegrationArtifactDrilldown>(
    `/api/v1/admin/integrations/artifacts${suffix}`,
  );
}
