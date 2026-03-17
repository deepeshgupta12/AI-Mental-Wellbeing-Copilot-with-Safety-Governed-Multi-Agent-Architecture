from __future__ import annotations

from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

SEARCH_DIRS = [
    MODULE_ROOT,
    MODULE_ROOT / "agents",
    REPO_ROOT / "prompts",
    REPO_ROOT / "prompts" / "agents",
]


def load_prompt(relative_path: str, fallback: str) -> str:
    for base_dir in SEARCH_DIRS:
        candidate = base_dir / relative_path
        if candidate.exists():
            return candidate.read_text(encoding="utf-8").strip()
    return fallback.strip()