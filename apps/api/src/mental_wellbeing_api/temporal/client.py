from __future__ import annotations

from temporalio.client import Client

from mental_wellbeing_api.core.config import get_settings


async def get_temporal_client() -> Client:
    settings = get_settings()
    return await Client.connect(
        target_host=settings.temporal_host,
        namespace=settings.temporal_namespace,
    )