import { apiRequest } from "@/lib/api-client";
import type {
  AdminCarePlanOverview,
  CarePlan,
  CarePlanEvent,
  CarePlanUserSummary,
} from "@/types/care-plans";

export function listCarePlans(params?: {
  userId?: string | null;
  organizationId?: string | null;
}): Promise<CarePlan[]> {
  const search = new URLSearchParams();
  if (params?.userId) search.set("user_id", params.userId);
  if (params?.organizationId) search.set("organization_id", params.organizationId);
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<CarePlan[]>(`/api/v1/care-plans${suffix}`);
}

export function getCarePlan(carePlanId: string): Promise<CarePlan> {
  return apiRequest<CarePlan>(`/api/v1/care-plans/${carePlanId}`);
}

export function getCarePlanUserSummary(userId: string): Promise<CarePlanUserSummary> {
  return apiRequest<CarePlanUserSummary>(`/api/v1/care-plans/summary?user_id=${encodeURIComponent(userId)}`);
}

export function createCarePlan(payload: Record<string, unknown>): Promise<CarePlan> {
  return apiRequest<CarePlan>("/api/v1/care-plans", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCarePlan(
  carePlanId: string,
  payload: Record<string, unknown>,
): Promise<CarePlan> {
  return apiRequest<CarePlan>(`/api/v1/care-plans/${carePlanId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function listCarePlanEvents(carePlanId: string): Promise<CarePlanEvent[]> {
  return apiRequest<CarePlanEvent[]>(`/api/v1/care-plans/${carePlanId}/events`);
}

export function createCarePlanEvent(
  carePlanId: string,
  payload: Record<string, unknown>,
): Promise<CarePlanEvent> {
  return apiRequest<CarePlanEvent>(`/api/v1/care-plans/${carePlanId}/events`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function advanceCarePlan(
  carePlanId: string,
  payload: Record<string, unknown>,
): Promise<CarePlan> {
  return apiRequest<CarePlan>(`/api/v1/care-plans/${carePlanId}/advance`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAdminCarePlanOverview(
  organizationId?: string | null,
): Promise<AdminCarePlanOverview> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminCarePlanOverview>(`/api/v1/admin/care-plans/overview${query}`);
}

export function getAdminCarePlans(
  organizationId?: string | null,
): Promise<CarePlan[]> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<CarePlan[]>(`/api/v1/admin/care-plans${query}`);
}

export function getAdminCarePlanEvents(
  carePlanId?: string | null,
): Promise<CarePlanEvent[]> {
  const query = carePlanId ? `?care_plan_id=${encodeURIComponent(carePlanId)}` : "";
  return apiRequest<CarePlanEvent[]>(`/api/v1/admin/care-plan-events${query}`);
}