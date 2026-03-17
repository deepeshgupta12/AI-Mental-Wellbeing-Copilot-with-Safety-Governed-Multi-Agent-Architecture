from __future__ import annotations

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[4] / "prompts"


def load_prompt(relative_path: str, fallback: str) -> str:
    path = PROMPTS_DIR / relative_path
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return fallback.strip()