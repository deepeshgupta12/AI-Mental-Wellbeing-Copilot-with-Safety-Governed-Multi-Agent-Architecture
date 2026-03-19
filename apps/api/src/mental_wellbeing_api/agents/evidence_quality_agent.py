from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState


def run_evidence_quality_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    evidence = {
        "user_input": state.get("user_input"),
        "risk_level": state.get("risk_level"),
        "safety_flag_type": state.get("safety_flag_type"),
        "safety_summary": state.get("safety_summary"),
        "intent_label": state.get("intent_label"),
        "support_mode": state.get("support_mode"),
        "specialist_agent": state.get("specialist_agent"),
        "local_classifier_signals": state.get("local_classifier_signals", {}),
        "routing_contract": state.get("routing_contract", {}),
        "memory_hit_count": len(state.get("recalled_memory_items", [])),
    }

    quality = {
        "response_present": bool(state.get("specialist_response") or state.get("reflective_response")),
        "safety_override": bool(state.get("safety_override", False)),
        "requires_human_review": bool(state.get("requires_human_review", False)),
        "non_clinical_path": True,
        "reviewable": True,
    }

    state = {
        **state,
        "evidence_bundle": evidence,
        "quality_checks": quality,
    }
    state = append_execution_event(
        state,
        node_name="evidence_quality",
        metadata={
            "evidence_keys": list(evidence.keys()),
            "reviewable": True,
            "requires_human_review": bool(state.get("requires_human_review", False)),
        },
    )
    state = append_handoff(
        state,
        from_agent="evidence_quality",
        to_agent="human_summary_generator",
        reason="evidence bundle prepared for human-readable review summary",
    )
    return state