from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
POLICY_DIR = MODULE_ROOT / "policies"

SEARCH_DIRS = [
    MODULE_ROOT,
    MODULE_ROOT / "agents",
    REPO_ROOT / "prompts",
    REPO_ROOT / "prompts" / "agents",
]


@lru_cache
def load_prompt_registry() -> dict[str, str]:
    registry_path = POLICY_DIR / "prompt_registry.json"
    if not registry_path.exists():
        return {}

    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}

    prompt_map = payload.get("prompt_map", {})
    if isinstance(prompt_map, dict):
        return {str(k): str(v) for k, v in prompt_map.items()}
    return {}


@lru_cache
def load_runtime_policy() -> dict[str, Any]:
    policy_path = POLICY_DIR / "runtime_policy.yaml"
    if not policy_path.exists():
        return {}

    payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def load_prompt(relative_path: str, fallback: str) -> str:
    prompt_registry = load_prompt_registry()
    resolved_relative_path = prompt_registry.get(relative_path, relative_path)

    for base_dir in SEARCH_DIRS:
        candidate = base_dir / resolved_relative_path
        if candidate.exists():
            return candidate.read_text(encoding="utf-8").strip()

    return fallback.strip()