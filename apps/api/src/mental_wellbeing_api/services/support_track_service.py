from __future__ import annotations


class SupportTrackService:
    def list_tracks(self) -> list[dict]:
        return [
            {
                "id": "stress_overwhelm",
                "title": "Stress & Overwhelm",
                "description": "Support for pressure, burnout, and overload.",
                "suggested_prompt": "I feel overwhelmed after work and need help slowing things down.",
            },
            {
                "id": "sleep_recovery",
                "title": "Sleep & Recovery",
                "description": "Support for rest, sleep disruption, and reset routines.",
                "suggested_prompt": "My sleep has been off and I want help recovering better.",
            },
            {
                "id": "journaling_reflection",
                "title": "Reflection & Journaling",
                "description": "Support to process emotions and reflect on patterns.",
                "suggested_prompt": "Help me reflect on what I wrote in my journal today.",
            },
            {
                "id": "social_support",
                "title": "Connection & Support",
                "description": "Support for loneliness, reaching out, and social grounding.",
                "suggested_prompt": "I feel lonely and need help figuring out who to reach out to.",
            },
            {
                "id": "habit_support",
                "title": "Habit & Care Planning",
                "description": "Support for routines, consistency, and small next steps.",
                "suggested_prompt": "I want a better routine and something practical I can sustain.",
            },
        ]