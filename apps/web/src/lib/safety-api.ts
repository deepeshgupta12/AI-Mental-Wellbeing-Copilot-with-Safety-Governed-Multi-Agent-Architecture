import { apiRequest } from "@/lib/api-client";
import type {
  CreateSafetyFlagPayload,
  SafetyDashboardCounts,
  SafetyFlag,
  SafetyQueueItem,
  UpdateSafetyFlagPayload,
} from "@/types/api";

export function createSafetyFlag(
  payload: CreateSafetyFlagPayload,
): Promise<SafetyFlag> {
  return apiRequest<SafetyFlag>("/api/v1/safety-flags", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listSafetyFlags(userId: string): Promise<SafetyFlag[]> {
  return apiRequest<SafetyFlag[]>(
    `/api/v1/safety-flags?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getSafetyQueue(): Promise<SafetyQueueItem[]> {
  return apiRequest<SafetyQueueItem[]>("/api/v1/safety-flags/queue");
}

export function getSafetyDashboardCounts(): Promise<SafetyDashboardCounts> {
  return apiRequest<SafetyDashboardCounts>(
    "/api/v1/safety-flags/dashboard-counts",
  );
}

export function updateSafetyFlag(
  flagId: string,
  payload: UpdateSafetyFlagPayload,
): Promise<SafetyFlag> {
  return apiRequest<SafetyFlag>(`/api/v1/safety-flags/${flagId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}