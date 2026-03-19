import { apiRequest } from "@/lib/api-client";
import type {
  AdminAnalyticsOverview,
  AdminAuditItem,
  AdminConfigAudit,
  AdminConfigDiff,
  AdminConfigVersion,
  AdminFlaggedSession,
  AdminFlaggedSessionDetail,
  AdminInterventionLog,
  AdminInterventionOverview,
  AdminOpsOverview,
  AdminPolicyConfig,
  AdminRoutingRulesResponse,
  AdminTraceExecutionDetail,
  AdminTraceExecutionSummary,
  AdminTraceItem,
} from "@/types/api";

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

export function getAdminAgentTraceExecutionDetail(traceName: string): Promise<AdminTraceExecutionDetail> {
  return apiRequest<AdminTraceExecutionDetail>(`/api/v1/admin/agent-trace-executions/${encodeURIComponent(traceName)}`);
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

export function updateAdminRoutingRules(payloadJson: Record<string, unknown>, changeNote?: string | null): Promise<AdminConfigVersion> {
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

export function updateAdminRuntimePolicy(payloadJson: Record<string, unknown>, changeNote?: string | null): Promise<AdminConfigVersion> {
  return apiRequest<AdminConfigVersion>("/api/v1/admin/runtime-policy", {
    method: "PUT",
    body: JSON.stringify({
      payload_json: payloadJson,
      change_note: changeNote ?? null,
      actor: "admin-ui",
    }),
  });
}

export function updateAdminPromptRegistry(payloadJson: Record<string, unknown>, changeNote?: string | null): Promise<AdminConfigVersion> {
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

export function getAdminConfigDiff(configKey: string, fromVersionId: string, toVersionId: string): Promise<AdminConfigDiff> {
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