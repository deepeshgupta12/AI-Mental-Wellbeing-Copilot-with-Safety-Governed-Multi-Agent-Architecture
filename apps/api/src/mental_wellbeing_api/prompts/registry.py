from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
POLICY_DIR = MODULE_ROOT / "policies"

PROMPT_REGISTRY_PATH = POLICY_DIR / "prompt_registry.json"
RUNTIME_POLICY_PATH = POLICY_DIR / "runtime_policy.yaml"
ROUTING_RULES_PATH = POLICY_DIR / "routing_rules.json"

SEARCH_DIRS = [
    MODULE_ROOT,
    MODULE_ROOT / "agents",
    REPO_ROOT / "prompts",
    REPO_ROOT / "prompts" / "agents",
]


def reset_registry_caches() -> None:
    load_prompt_registry.cache_clear()
    load_prompt_registry_document.cache_clear()
    load_runtime_policy.cache_clear()
    load_routing_rules.cache_clear()


@lru_cache
def load_prompt_registry_document() -> dict[str, Any]:
    if not PROMPT_REGISTRY_PATH.exists():
        return {"prompt_map": {}}

    payload = json.loads(PROMPT_REGISTRY_PATH.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"prompt_map": {}}


@lru_cache
def load_prompt_registry() -> dict[str, str]:
    payload = load_prompt_registry_document()
    prompt_map = payload.get("prompt_map", {})
    if isinstance(prompt_map, dict):
        return {str(k): str(v) for k, v in prompt_map.items()}
    return {}


@lru_cache
def load_runtime_policy() -> dict[str, Any]:
    if not RUNTIME_POLICY_PATH.exists():
        return {}

    payload = yaml.safe_load(RUNTIME_POLICY_PATH.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


@lru_cache
def load_routing_rules() -> dict[str, Any]:
    if not ROUTING_RULES_PATH.exists():
        return {}

    payload = json.loads(ROUTING_RULES_PATH.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_prompt(relative_path: str, fallback: str) -> str:
    prompt_registry = load_prompt_registry()
    resolved_relative_path = prompt_registry.get(relative_path, relative_path)

    for base_dir in SEARCH_DIRS:
        candidate = base_dir / resolved_relative_path
        if candidate.exists():
            return candidate.read_text(encoding="utf-8").strip()

    return fallback.strip()