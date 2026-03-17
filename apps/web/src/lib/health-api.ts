import { apiRequest } from "@/lib/api-client";
import type {
  HealthDependenciesResponse,
  HealthResponse,
} from "@/types/api";

export async function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/api/v1/health");
}

export async function getHealthDependencies(): Promise<HealthDependenciesResponse> {
  return apiRequest<HealthDependenciesResponse>("/api/v1/health/dependencies");
}