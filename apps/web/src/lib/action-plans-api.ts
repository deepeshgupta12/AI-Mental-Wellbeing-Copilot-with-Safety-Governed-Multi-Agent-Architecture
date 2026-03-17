import { apiRequest } from "@/lib/api-client";
import type { ActionPlan, CreateActionPlanPayload } from "@/types/api";

export function createActionPlan(
  payload: CreateActionPlanPayload,
): Promise<ActionPlan> {
  return apiRequest<ActionPlan>("/api/v1/action-plans", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listActionPlans(userId: string): Promise<ActionPlan[]> {
  return apiRequest<ActionPlan[]>(
    `/api/v1/action-plans?user_id=${encodeURIComponent(userId)}`,
  );
}