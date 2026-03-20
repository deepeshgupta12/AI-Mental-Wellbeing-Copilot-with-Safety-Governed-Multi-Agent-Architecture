from __future__ import annotations

from typing import Any

from mental_wellbeing_api.core.config import get_settings


class SecretManagerService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _presence_map(self) -> dict[str, bool]:
        return {
            "OPENAI_API_KEY": bool(self.settings.openai_api_key),
            "AUTH_SESSION_SECRET": bool(self.settings.auth_session_secret),
            "STORAGE_ACCESS_KEY_ID": bool(self.settings.storage_access_key_id),
            "STORAGE_SECRET_ACCESS_KEY": bool(self.settings.storage_secret_access_key),
        }

    def build_runtime_summary(
        self,
        *,
        deployment_secrets_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        configured = self._presence_map()

        requested_keys: list[str] = []
        if deployment_secrets_payload:
            raw = deployment_secrets_payload.get("managed_secret_keys", [])
            if isinstance(raw, list):
                requested_keys = [str(item) for item in raw]

        if not requested_keys:
            requested_keys = list(configured.keys())

        configured_keys = [key for key in requested_keys if configured.get(key, False)]
        missing_keys = [key for key in requested_keys if not configured.get(key, False)]

        return {
            "backend": deployment_secrets_payload.get("backend", self.settings.secret_backend)
            if deployment_secrets_payload
            else self.settings.secret_backend,
            "namespace": deployment_secrets_payload.get("namespace", self.settings.managed_secret_namespace)
            if deployment_secrets_payload
            else self.settings.managed_secret_namespace,
            "prefix": deployment_secrets_payload.get("prefix", self.settings.managed_secret_prefix or None)
            if deployment_secrets_payload
            else (self.settings.managed_secret_prefix or None),
            "configured_keys": configured_keys,
            "missing_keys": missing_keys,
            "redacted": True,
        }