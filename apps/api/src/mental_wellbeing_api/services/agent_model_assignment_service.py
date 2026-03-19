from __future__ import annotations

from typing import Any

from mental_wellbeing_api.prompts.registry import load_runtime_policy


class AgentModelAssignmentService:
    def __init__(self) -> None:
        self.policy = load_runtime_policy()

    def resolve(self, *, provider: str, agent_name: str | None) -> dict[str, Any]:
        normalized_provider = (provider or "").strip().lower() or "mock"
        assignments = self.policy.get("models", {}).get("agent_assignments", {})

        # Never override explicit mock mode with agent-level provider assignments.
        if normalized_provider == "mock":
            return {"provider": "mock", "model": None}

        if not agent_name:
            return {"provider": normalized_provider, "model": None}

        config = assignments.get(agent_name, {})
        assigned_provider = str(config.get("provider") or normalized_provider).strip().lower()
        assigned_model = config.get("model")

        return {
            "provider": assigned_provider or normalized_provider,
            "model": assigned_model,
        }