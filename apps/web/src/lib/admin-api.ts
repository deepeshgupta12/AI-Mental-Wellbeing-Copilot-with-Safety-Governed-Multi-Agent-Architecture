import { apiRequest } from "@/lib/api-client";
import type {
  AdminAuditItem,
  AdminFlaggedSession,
  AdminPolicyConfig,
  AdminSessionLog,
} from "@/types/api";

export function getAdminFlaggedSessions(): Promise<AdminFlaggedSession[]> {
  return apiRequest<AdminFlaggedSession[]>("/api/v1/admin/flagged-sessions");
}

export function getAdminSessionLogs(): Promise<AdminSessionLog[]> {
  return apiRequest<AdminSessionLog[]>("/api/v1/admin/session-logs");
}

export function getAdminAuditTrail(): Promise<AdminAuditItem[]> {
  return apiRequest<AdminAuditItem[]>("/api/v1/admin/audit-trail");
}

export function getAdminPolicyConfig(): Promise<AdminPolicyConfig> {
  return apiRequest<AdminPolicyConfig>("/api/v1/admin/policy-config");
}