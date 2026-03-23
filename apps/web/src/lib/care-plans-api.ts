import { apiRequest } from "@/lib/api-client";
import type {
  AdminCarePlanOverview,
  CarePlan,
  CarePlanAdvancePayload,
  CarePlanCreatePayload,
  CarePlanEvent,
  CarePlanEventCreatePayload,
  CarePlanLifecyclePayload,
  CarePlanSummary,
  CarePlanUpdatePayload,
} from "@/types/care-plans";

export function listCarePlans(params: {
  userId?: string | null;
  organizationId?: string | null;
  status?: string | null;
  preferredLanguage?: string | null;
  programKey?: string | null;
}): Promise<CarePlan[]> {
  const search = new URLSearchParams();

  if (params.userId) search.set("user_id", params.userId);
  if (params.organizationId) search.set("organization_id", params.organizationId);
  if (params.status) search.set("status", params.status);
  if (params.preferredLanguage) search.set("preferred_language", params.preferredLanguage);
  if (params.programKey) search.set("program_key", params.programKey);

  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<CarePlan[]>(`/api/v1/care-plans${suffix}`);
}

export function createCarePlan(payload: CarePlanCreatePayload): Promise<CarePlan> {
  return apiRequest<CarePlan>("/api/v1/care-plans", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCarePlan(
  carePlanId: string,
  payload: CarePlanUpdatePayload,
): Promise<CarePlan> {
  return apiRequest<CarePlan>(`/api/v1/care-plans/${carePlanId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function createCarePlanEvent(
  carePlanId: string,
  payload: CarePlanEventCreatePayload,
): Promise<CarePlanEvent> {
  return apiRequest<CarePlanEvent>(`/api/v1/care-plans/${carePlanId}/events`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function advanceCarePlan(
  carePlanId: string,
  payload: CarePlanAdvancePayload,
): Promise<CarePlan> {
  return apiRequest<CarePlan>(`/api/v1/care-plans/${carePlanId}/advance`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function lifecycleCarePlan(
  carePlanId: string,
  payload: CarePlanLifecyclePayload,
): Promise<CarePlan> {
  return apiRequest<CarePlan>(`/api/v1/care-plans/${carePlanId}/lifecycle`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCarePlanUserSummary(userId: string): Promise<CarePlanSummary> {
  return apiRequest<CarePlanSummary>(
    `/api/v1/care-plans/summary?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getAdminCarePlanOverview(
  organizationId?: string | null,
): Promise<AdminCarePlanOverview> {
  const suffix = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminCarePlanOverview>(`/api/v1/admin/care-plans/overview${suffix}`);
}

export function getAdminCarePlans(params?: {
  organizationId?: string | null;
  status?: string | null;
  preferredLanguage?: string | null;
  programKey?: string | null;
  attentionState?: string | null;
  limit?: number;
}): Promise<CarePlan[]> {
  const search = new URLSearchParams();
  if (params?.organizationId) search.set("organization_id", params.organizationId);
  if (params?.status) search.set("status", params.status);
  if (params?.preferredLanguage) search.set("preferred_language", params.preferredLanguage);
  if (params?.programKey) search.set("program_key", params.programKey);
  if (params?.attentionState) search.set("attention_state", params.attentionState);
  if (params?.limit) search.set("limit", String(params.limit));
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<CarePlan[]>(`/api/v1/admin/care-plans${suffix}`);
}

export function getAdminCarePlanEvents(params?: {
  carePlanId?: string | null;
  limit?: number;
}): Promise<CarePlanEvent[]> {
  const search = new URLSearchParams();
  if (params?.carePlanId) search.set("care_plan_id", params.carePlanId);
  if (params?.limit) search.set("limit", String(params.limit));
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<CarePlanEvent[]>(`/api/v1/admin/care-plan-events${suffix}`);
}