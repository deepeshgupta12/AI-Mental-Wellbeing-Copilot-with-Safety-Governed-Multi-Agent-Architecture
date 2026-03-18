from __future__ import annotations

from mental_wellbeing_api.orchestration.runtime import append_execution_event, append_handoff
from mental_wellbeing_api.orchestration.state import AgentRuntimeState
from mental_wellbeing_api.prompts.registry import load_prompt
from mental_wellbeing_api.services.llm_service import LLMService


def run_sleep_recovery_agent(state: AgentRuntimeState) -> AgentRuntimeState:
    llm = LLMService()
    system_prompt = load_prompt(
        "agents/sleep_recovery.txt",
        """
You are a non-clinical wellbeing assistant focused on sleep and recovery support.
Offer calm, practical, non-medical suggestions that help the user wind down and recover.
Keep it concise and realistic.
""",
    )

    user_prompt = (
        f"User input:\n{state['user_input']}\n\n"
        f"Structured summary:\n{state.get('structured_input', '')}\n\n"
        f"Session context:\n{state.get('session_context', '')}\n\n"
        "Write a brief response focused on sleep recovery and one or two practical wind-down suggestions."
    )
    specialist_response = llm.generate_text(state["provider"], system_prompt, user_prompt)

    state = {
        **state,
        "reflective_response": specialist_response,
        "specialist_response": specialist_response,
        "coping_recommendations": [
            "Reduce stimulation for the next 20 minutes.",
            "Choose one predictable wind-down cue tonight.",
        ],
        "journaling_insights": [
            "Track what tends to happen in the hour before sleep feels hardest.",
        ],
        "follow_up_suggestions": [
            "Tell me whether the issue is falling asleep, waking up, or restless sleep.",
        ],
    }
    state = append_execution_event(
        state,
        node_name="sleep_recovery",
        metadata={"response_length": len(specialist_response)},
    )
    state = append_handoff(
        state,
        from_agent="sleep_recovery",
        to_agent="response_composer",
        reason="sleep recovery draft prepared",
    )
    return state