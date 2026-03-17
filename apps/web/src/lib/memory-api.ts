import { apiRequest } from "@/lib/api-client";
import type { MemorySummary, TrendSummary } from "@/types/api";

export function getMemorySummary(userId: string): Promise<MemorySummary> {
  return apiRequest<MemorySummary>(
    `/api/v1/memory-trends/memory-summary?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getTrendSummary(userId: string): Promise<TrendSummary> {
  return apiRequest<TrendSummary>(
    `/api/v1/memory-trends/trend-summary?user_id=${encodeURIComponent(userId)}`,
  );
}