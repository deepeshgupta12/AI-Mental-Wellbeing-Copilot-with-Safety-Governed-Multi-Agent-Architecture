import { apiRequest } from "@/lib/api-client";
import type { CheckIn, CreateCheckInPayload } from "@/types/api";

export function createCheckIn(payload: CreateCheckInPayload): Promise<CheckIn> {
  return apiRequest<CheckIn>("/api/v1/check-ins", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listCheckIns(userId: string): Promise<CheckIn[]> {
  return apiRequest<CheckIn[]>(
    `/api/v1/check-ins?user_id=${encodeURIComponent(userId)}`,
  );
}