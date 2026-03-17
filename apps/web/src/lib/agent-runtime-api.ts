import { apiRequest } from "@/lib/api-client";
import type {
  AgentRuntimeSmokePayload,
  AgentRuntimeSmokeResponse,
  SafetyEvaluationResponse,
} from "@/types/api";

export function runAgentRuntimeSmoke(
  payload: AgentRuntimeSmokePayload,
): Promise<AgentRuntimeSmokeResponse> {
  return apiRequest<AgentRuntimeSmokeResponse>("/api/v1/agent-runtime/smoke", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function evaluateSafety(
  payload: AgentRuntimeSmokePayload,
): Promise<SafetyEvaluationResponse> {
  return apiRequest<SafetyEvaluationResponse>(
    "/api/v1/agent-runtime/safety-evaluate",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}