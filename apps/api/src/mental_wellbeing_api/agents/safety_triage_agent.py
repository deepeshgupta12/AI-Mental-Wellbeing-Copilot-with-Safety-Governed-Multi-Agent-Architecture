from __future__ import annotations

from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_safety_triage_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    return state