from __future__ import annotations

from fastapi import APIRouter

from mental_wellbeing_api.services.support_track_service import SupportTrackService

router = APIRouter(prefix="/support-tracks", tags=["support-tracks"])


@router.get("")
async def list_support_tracks() -> list[dict]:
    return SupportTrackService().list_tracks()