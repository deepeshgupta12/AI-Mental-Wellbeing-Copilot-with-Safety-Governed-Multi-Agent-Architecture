from __future__ import annotations

from typing import Any

from mental_wellbeing_api.prompts.registry import load_runtime_policy


class AgentModelAssignmentService:
    def __init__(self) -> None:
        self.policy = load_runtime_policy()

    def resolve(
        self,
        *,
        provider: str,
        agent_name: str | None,
        risk_level: str | None = None,
        final_stage: bool = False,
    ) -> dict[str, Any]:
        normalized_provider = (provider or "").strip().lower() or "mock"
        assignments = self.policy.get("models", {}).get("agent_assignments", {})
        gating = self.policy.get("models", {}).get("risk_tier_gating", {})

        if normalized_provider == "mock":
            return {"provider": "mock", "model": None}

        if not agent_name:
            return {"provider": normalized_provider, "model": None}

        config = assignments.get(agent_name, {})
        assigned_provider = str(config.get("provider") or normalized_provider).strip().lower()
        assigned_model = config.get("model")

        effective_risk = (risk_level or "").lower()

        if effective_risk == "high":
            high_risk_provider = gating.get("high_risk_provider")
            high_risk_model = gating.get("high_risk_model")
            if high_risk_provider:
                assigned_provider = str(high_risk_provider).strip().lower()
            if high_risk_model:
                assigned_model = high_risk_model

        if final_stage:
            final_provider = gating.get("final_response_provider")
            final_model = gating.get("final_response_model")
            if final_provider:
                assigned_provider = str(final_provider).strip().lower()
            if final_model:
                assigned_model = final_model

        return {
            "provider": assigned_provider or normalized_provider,
            "model": assigned_model,
        }