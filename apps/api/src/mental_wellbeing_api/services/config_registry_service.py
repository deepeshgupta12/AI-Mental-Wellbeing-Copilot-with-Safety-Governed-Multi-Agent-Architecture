from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.admin_config_audit import AdminConfigAudit
from mental_wellbeing_api.models.admin_config_version import AdminConfigVersion
from mental_wellbeing_api.prompts.registry import (
    PROMPT_REGISTRY_PATH,
    ROUTING_RULES_PATH,
    RUNTIME_POLICY_PATH,
    load_prompt_registry_document,
    load_routing_rules,
    load_runtime_policy,
    reset_registry_caches,
)


class ConfigRegistryService:
    VALID_KEYS = {"runtime_policy", "prompt_registry", "routing_rules"}

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._path_map: dict[str, Path] = {
            "runtime_policy": RUNTIME_POLICY_PATH,
            "prompt_registry": PROMPT_REGISTRY_PATH,
            "routing_rules": ROUTING_RULES_PATH,
        }

    def _read_live_payload(self, config_key: str) -> dict[str, Any]:
        if config_key == "runtime_policy":
            return deepcopy(load_runtime_policy())
        if config_key == "prompt_registry":
            return deepcopy(load_prompt_registry_document())
        if config_key == "routing_rules":
            return deepcopy(load_routing_rules())
        raise ValueError("Unsupported config key")

    def _write_live_payload(self, config_key: str, payload: dict[str, Any]) -> None:
        path = self._path_map[config_key]
        path.parent.mkdir(parents=True, exist_ok=True)

        if config_key == "runtime_policy":
            path.write_text(
                yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
        else:
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        reset_registry_caches()

    def _normalize_payload(self, config_key: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a JSON object")

        normalized = deepcopy(payload)

        if config_key == "prompt_registry":
            normalized.setdefault("version", "v2-10.0.0")
            normalized.setdefault("prompt_map", {})
            if not isinstance(normalized["prompt_map"], dict):
                raise ValueError("prompt_registry.prompt_map must be an object")

        if config_key == "routing_rules":
            normalized.setdefault("version", "v2-10.0.0")
            normalized.setdefault("intent_router", {})
            normalized.setdefault("support_mode_router", {})

        if config_key == "runtime_policy":
            normalized.setdefault("service", {})
            normalized.setdefault("routing", {})
            normalized.setdefault("response", {})
            normalized.setdefault("admin", {})

        return normalized

    def _diff_payloads(self, before: Any, after: Any, path: str = "") -> tuple[dict[str, Any], list[str]]:
        changed_keys: list[str] = []

        if isinstance(before, dict) and isinstance(after, dict):
            diff: dict[str, Any] = {}
            for key in sorted(set(before.keys()) | set(after.keys())):
                child_path = f"{path}.{key}" if path else str(key)
                if key not in before:
                    diff[key] = {"before": None, "after": after[key]}
                    changed_keys.append(child_path)
                elif key not in after:
                    diff[key] = {"before": before[key], "after": None}
                    changed_keys.append(child_path)
                elif before[key] != after[key]:
                    child_diff, child_keys = self._diff_payloads(before[key], after[key], child_path)
                    diff[key] = child_diff
                    changed_keys.extend(child_keys)
            return diff, changed_keys

        if before != after:
            return {"before": before, "after": after}, [path or "root"]

        return {}, []

    async def _bootstrap_if_needed(self, config_key: str) -> None:
        existing = await self.session.scalar(
            select(AdminConfigVersion.id)
            .where(
                AdminConfigVersion.config_key == config_key,
                AdminConfigVersion.is_active.is_(True),
            )
            .limit(1)
        )
        if existing:
            return

        payload = self._normalize_payload(config_key, self._read_live_payload(config_key))
        row = AdminConfigVersion(
            config_key=config_key,
            version_number=1,
            payload_json=payload,
            change_note="Bootstrap from live policy file",
            is_active=True,
            created_by="system",
        )
        self.session.add(row)
        await self.session.commit()

    async def get_active(self, config_key: str) -> AdminConfigVersion:
        if config_key not in self.VALID_KEYS:
            raise ValueError("Unsupported config key")

        await self._bootstrap_if_needed(config_key)
        item = await self.session.scalar(
            select(AdminConfigVersion)
            .where(
                AdminConfigVersion.config_key == config_key,
                AdminConfigVersion.is_active.is_(True),
            )
            .order_by(desc(AdminConfigVersion.version_number))
            .limit(1)
        )
        if item is None:
            raise ValueError("Active config version not found")
        return item

    async def list_versions(self, config_key: str, limit: int = 20) -> list[AdminConfigVersion]:
        if config_key not in self.VALID_KEYS:
            raise ValueError("Unsupported config key")

        await self._bootstrap_if_needed(config_key)
        result = await self.session.scalars(
            select(AdminConfigVersion)
            .where(AdminConfigVersion.config_key == config_key)
            .order_by(desc(AdminConfigVersion.version_number), desc(AdminConfigVersion.created_at))
            .limit(limit)
        )
        return list(result.all())

    async def update_config(
        self,
        *,
        config_key: str,
        payload: dict[str, Any],
        change_note: str | None = None,
        actor: str | None = "admin",
    ) -> AdminConfigVersion:
        if config_key not in self.VALID_KEYS:
            raise ValueError("Unsupported config key")

        await self._bootstrap_if_needed(config_key)
        active = await self.get_active(config_key)
        normalized = self._normalize_payload(config_key, payload)

        diff_json, changed_keys = self._diff_payloads(active.payload_json, normalized)
        if not changed_keys:
            return active

        next_version_number = int(
            (
                await self.session.scalar(
                    select(func.max(AdminConfigVersion.version_number)).where(
                        AdminConfigVersion.config_key == config_key
                    )
                )
            )
            or 0
        ) + 1

        await self.session.execute(
            update(AdminConfigVersion)
            .where(
                AdminConfigVersion.config_key == config_key,
                AdminConfigVersion.is_active.is_(True),
            )
            .values(is_active=False)
        )

        new_version = AdminConfigVersion(
            config_key=config_key,
            version_number=next_version_number,
            payload_json=normalized,
            change_note=change_note,
            is_active=True,
            created_by=actor,
        )
        self.session.add(new_version)
        await self.session.flush()

        audit = AdminConfigAudit(
            config_key=config_key,
            from_version_id=active.id,
            to_version_id=new_version.id,
            changed_keys_json=changed_keys,
            diff_json=diff_json,
            actor=actor,
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(new_version)

        self._write_live_payload(config_key, normalized)
        return new_version

    async def list_audits(self, config_key: str | None = None, limit: int = 50) -> list[AdminConfigAudit]:
        stmt = select(AdminConfigAudit).order_by(desc(AdminConfigAudit.created_at)).limit(limit)
        if config_key:
            stmt = stmt.where(AdminConfigAudit.config_key == config_key)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_diff(
        self,
        *,
        config_key: str,
        from_version_id: str,
        to_version_id: str,
    ) -> dict[str, Any]:
        from_row = await self.session.get(AdminConfigVersion, from_version_id)
        to_row = await self.session.get(AdminConfigVersion, to_version_id)

        if from_row is None or to_row is None:
            raise ValueError("Version not found")
        if from_row.config_key != config_key or to_row.config_key != config_key:
            raise ValueError("Config key mismatch")

        diff_json, changed_keys = self._diff_payloads(from_row.payload_json, to_row.payload_json)
        return {
            "config_key": config_key,
            "from_version_id": from_row.id,
            "to_version_id": to_row.id,
            "from_version_number": from_row.version_number,
            "to_version_number": to_row.version_number,
            "changed_keys": changed_keys,
            "diff_json": diff_json,
        }