from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip().replace("Z", "+00:00")
    item = datetime.fromisoformat(normalized)
    if item.tzinfo is None:
        return item.replace(tzinfo=UTC)
    return item


@dataclass(slots=True)
class CatalogField:
    key: str
    label: str
    required: bool = False
    secret: bool = False
    placeholder: str | None = None


@dataclass(slots=True)
class NormalizedSignalInput:
    signal_type: str
    source_item_id: str
    signal_at: datetime | None = None
    signal_start_at: datetime | None = None
    signal_end_at: datetime | None = None
    numeric_value: float | None = None
    text_value: str | None = None
    unit: str | None = None
    signal_payload_json: dict[str, Any] = field(default_factory=dict)


class BaseExternalProviderAdapter:
    integration_key: str
    provider_key: str
    display_name: str
    category: str
    adapter_type: str = "manual_ingest_contract"
    description: str = ""
    sync_supported: bool = True
    manual_ingest_supported: bool = True
    consent_required: bool = True

    def config_fields(self) -> list[CatalogField]:
        return []

    def registry_item(self) -> dict[str, Any]:
        return {
            "integration_key": self.integration_key,
            "provider_key": self.provider_key,
            "display_name": self.display_name,
            "category": self.category,
            "adapter_type": self.adapter_type,
            "description": self.description,
            "sync_supported": self.sync_supported,
            "manual_ingest_supported": self.manual_ingest_supported,
            "consent_required": self.consent_required,
            "config_fields": [asdict(field_item) for field_item in self.config_fields()],
        }

    def normalize_payload(self, payload_json: dict[str, Any]) -> list[NormalizedSignalInput]:
        raise NotImplementedError


class GoogleCalendarAdapter(BaseExternalProviderAdapter):
    integration_key = "calendar"
    provider_key = "google_calendar"
    display_name = "Google Calendar"
    category = "calendar"
    description = (
        "Manual or scheduled ingestion contract for calendar events such as meetings, "
        "therapy sessions, routines, or focus blocks."
    )

    def config_fields(self) -> list[CatalogField]:
        return [
            CatalogField("calendar_id", "Calendar ID", required=False, placeholder="primary"),
            CatalogField("account_label", "Account Label", required=False, placeholder="Work / Personal"),
        ]

    def normalize_payload(self, payload_json: dict[str, Any]) -> list[NormalizedSignalInput]:
        items = payload_json.get("events", [])
        if not isinstance(items, list):
            raise ValueError("Calendar payload must include an 'events' array.")

        normalized: list[NormalizedSignalInput] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            source_item_id = str(raw.get("id") or raw.get("event_id") or "")
            if not source_item_id:
                continue

            start_at = _parse_datetime(raw.get("start_at"))
            end_at = _parse_datetime(raw.get("end_at"))
            normalized.append(
                NormalizedSignalInput(
                    signal_type="calendar_event",
                    source_item_id=source_item_id,
                    signal_at=start_at,
                    signal_start_at=start_at,
                    signal_end_at=end_at,
                    text_value=str(raw.get("title") or raw.get("summary") or "calendar_event"),
                    signal_payload_json=raw,
                )
            )
        return normalized


class AppleRemindersAdapter(BaseExternalProviderAdapter):
    integration_key = "reminders"
    provider_key = "apple_reminders"
    display_name = "Apple Reminders"
    category = "reminders"
    description = (
        "Manual or scheduled ingestion contract for reminders, tasks, coping prompts, "
        "and recurring nudges."
    )

    def config_fields(self) -> list[CatalogField]:
        return [
            CatalogField("list_name", "List Name", required=False, placeholder="Wellbeing"),
            CatalogField("account_label", "Account Label", required=False, placeholder="iPhone"),
        ]

    def normalize_payload(self, payload_json: dict[str, Any]) -> list[NormalizedSignalInput]:
        items = payload_json.get("reminders", [])
        if not isinstance(items, list):
            raise ValueError("Reminders payload must include a 'reminders' array.")

        normalized: list[NormalizedSignalInput] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            source_item_id = str(raw.get("id") or raw.get("reminder_id") or "")
            if not source_item_id:
                continue

            due_at = _parse_datetime(raw.get("due_at"))
            completed = bool(raw.get("completed", False))
            normalized.append(
                NormalizedSignalInput(
                    signal_type="reminder_item",
                    source_item_id=source_item_id,
                    signal_at=due_at,
                    text_value=str(raw.get("title") or "reminder"),
                    numeric_value=1.0 if completed else 0.0,
                    unit="completed_flag",
                    signal_payload_json=raw,
                )
            )
        return normalized


class FitbitWearableAdapter(BaseExternalProviderAdapter):
    integration_key = "wearable"
    provider_key = "fitbit_wearable"
    display_name = "Fitbit Wearable"
    category = "wearable"
    description = (
        "Manual or scheduled ingestion contract for wearable signals such as steps, "
        "heart rate, stress, readiness, and activity samples."
    )

    def config_fields(self) -> list[CatalogField]:
        return [
            CatalogField("device_label", "Device Label", required=False, placeholder="Fitbit Charge"),
            CatalogField(
                "metric_mode",
                "Metric Mode",
                required=False,
                placeholder="steps / heart_rate / stress",
            ),
        ]

    def normalize_payload(self, payload_json: dict[str, Any]) -> list[NormalizedSignalInput]:
        items = payload_json.get("samples", [])
        if not isinstance(items, list):
            raise ValueError("Wearable payload must include a 'samples' array.")

        normalized: list[NormalizedSignalInput] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            source_item_id = str(raw.get("id") or raw.get("sample_id") or "")
            if not source_item_id:
                continue

            metric_type = str(raw.get("metric_type") or "wearable_metric")
            captured_at = _parse_datetime(raw.get("captured_at"))
            value = raw.get("value")
            numeric_value = float(value) if isinstance(value, (int, float)) else None

            normalized.append(
                NormalizedSignalInput(
                    signal_type=f"wearable_{metric_type}",
                    source_item_id=source_item_id,
                    signal_at=captured_at,
                    numeric_value=numeric_value,
                    text_value=str(raw.get("label") or metric_type),
                    unit=str(raw.get("unit")) if raw.get("unit") else None,
                    signal_payload_json=raw,
                )
            )
        return normalized


class OuraSleepAdapter(BaseExternalProviderAdapter):
    integration_key = "sleep"
    provider_key = "oura_sleep"
    display_name = "Oura Sleep"
    category = "sleep"
    description = (
        "Manual or scheduled ingestion contract for sleep sessions, duration, quality, "
        "and sleep score normalization."
    )

    def config_fields(self) -> list[CatalogField]:
        return [
            CatalogField("device_label", "Device Label", required=False, placeholder="Oura Ring"),
            CatalogField(
                "account_label",
                "Account Label",
                required=False,
                placeholder="Primary Sleep Source",
            ),
        ]

    def normalize_payload(self, payload_json: dict[str, Any]) -> list[NormalizedSignalInput]:
        items = payload_json.get("sessions", [])
        if not isinstance(items, list):
            raise ValueError("Sleep payload must include a 'sessions' array.")

        normalized: list[NormalizedSignalInput] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            source_item_id = str(raw.get("id") or raw.get("session_id") or "")
            if not source_item_id:
                continue

            start_at = _parse_datetime(raw.get("start_at"))
            end_at = _parse_datetime(raw.get("end_at"))
            duration = raw.get("duration_minutes")
            numeric_value = float(duration) if isinstance(duration, (int, float)) else None

            normalized.append(
                NormalizedSignalInput(
                    signal_type="sleep_session",
                    source_item_id=source_item_id,
                    signal_at=end_at or start_at,
                    signal_start_at=start_at,
                    signal_end_at=end_at,
                    numeric_value=numeric_value,
                    text_value=str(raw.get("sleep_score") or raw.get("quality") or "sleep"),
                    unit="minutes",
                    signal_payload_json=raw,
                )
            )
        return normalized


class ExternalProviderAdapterRegistry:
    def __init__(self) -> None:
        self._items: dict[str, BaseExternalProviderAdapter] = {
            item.provider_key: item
            for item in [
                GoogleCalendarAdapter(),
                AppleRemindersAdapter(),
                FitbitWearableAdapter(),
                OuraSleepAdapter(),
            ]
        }

    def all(self) -> list[BaseExternalProviderAdapter]:
        return list(self._items.values())

    def get(self, provider_key: str) -> BaseExternalProviderAdapter:
        item = self._items.get(provider_key)
        if item is None:
            raise ValueError(f"Unsupported provider: {provider_key}")
        return item