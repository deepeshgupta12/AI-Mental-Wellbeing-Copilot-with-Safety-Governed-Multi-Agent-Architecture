from __future__ import annotations

from pydantic import BaseModel


class SafetyEvaluationResponse(BaseModel):
    risk_level: str
    safety_flag_type: str | None = None
    safety_summary: str | None = None
    safety_override: bool
    requires_human_review: bool = False
    escalation_recommended: bool = False
    queue_status: str | None = None
    review_priority: str | None = None


class SafetyService:
    HIGH_RISK_PATTERNS = [
        ("self_harm", ["kill myself", "end my life", "suicide", "want to die", "hurt myself"]),
        ("harm_to_others", ["kill someone", "hurt someone", "harm others"]),
        ("acute_hopelessness", ["no reason to live", "everyone is better off without me"]),
    ]

    MEDIUM_RISK_PATTERNS = [
        ("panic_distress", ["panic attack", "can't breathe", "losing control"]),
        ("severe_distress", ["i am not safe", "i might do something bad", "breaking down"]),
    ]

    def evaluate_text(self, text: str) -> SafetyEvaluationResponse:
        normalized = text.lower().strip()

        for flag_type, patterns in self.HIGH_RISK_PATTERNS:
            if any(pattern in normalized for pattern in patterns):
                return SafetyEvaluationResponse(
                    risk_level="high",
                    safety_flag_type=flag_type,
                    safety_summary=f"High-risk language detected: {flag_type}",
                    safety_override=True,
                    requires_human_review=True,
                    escalation_recommended=True,
                    queue_status="queued",
                    review_priority="urgent",
                )

        for flag_type, patterns in self.MEDIUM_RISK_PATTERNS:
            if any(pattern in normalized for pattern in patterns):
                return SafetyEvaluationResponse(
                    risk_level="medium",
                    safety_flag_type=flag_type,
                    safety_summary=f"Elevated-risk language detected: {flag_type}",
                    safety_override=False,
                    requires_human_review=True,
                    escalation_recommended=False,
                    queue_status="queued",
                    review_priority="high",
                )

        return SafetyEvaluationResponse(
            risk_level="low",
            safety_flag_type=None,
            safety_summary=None,
            safety_override=False,
            requires_human_review=False,
            escalation_recommended=False,
            queue_status=None,
            review_priority="normal",
        )