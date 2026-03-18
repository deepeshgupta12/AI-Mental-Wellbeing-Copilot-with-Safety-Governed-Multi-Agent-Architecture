from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.user import User, UserPreference, UserProfile


class PreferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_preference_signals(self, user_id: str) -> dict[str, str]:
        signals: dict[str, str] = {}

        profile = await self.session.scalar(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        if profile is not None:
            if profile.support_style:
                signals["support_style"] = profile.support_style
            if profile.preferred_support_mode:
                signals["preferred_support_mode"] = profile.preferred_support_mode
            if profile.timezone:
                signals["timezone"] = profile.timezone
            if profile.focus_areas:
                signals["focus_areas"] = profile.focus_areas
            if profile.wellbeing_goals:
                signals["wellbeing_goals"] = profile.wellbeing_goals

        preference_rows = list(
            (
                await self.session.scalars(
                    select(UserPreference)
                    .where(
                        UserPreference.user_id == user_id,
                        UserPreference.is_active.is_(True),
                    )
                    .order_by(desc(UserPreference.updated_at), desc(UserPreference.created_at))
                    .limit(20)
                )
            ).all()
        )

        for pref in preference_rows:
            value = pref.preference_value_json
            if isinstance(value, dict):
                if "value" in value and value["value"] is not None:
                    signals[pref.preference_key] = str(value["value"])
                elif "label" in value and value["label"] is not None:
                    signals[pref.preference_key] = str(value["label"])

        return signals

    async def user_exists(self, user_id: str) -> bool:
        user_exists = await self.session.scalar(select(User.id).where(User.id == user_id))
        return bool(user_exists)

    async def upsert_preference(
        self,
        *,
        user_id: str,
        preference_key: str,
        value: str,
        source: str = "system",
        confidence_score: float | None = None,
    ) -> None:
        existing = await self.session.scalar(
            select(UserPreference)
            .where(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key,
                UserPreference.is_active.is_(True),
            )
            .order_by(desc(UserPreference.updated_at), desc(UserPreference.created_at))
            .limit(1)
        )

        payload = {"value": value}

        if existing:
            existing.preference_value_json = payload
            existing.source = source
            existing.confidence_score = confidence_score
        else:
            self.session.add(
                UserPreference(
                    user_id=user_id,
                    preference_key=preference_key,
                    preference_value_json=payload,
                    source=source,
                    confidence_score=confidence_score,
                    is_active=True,
                )
            )

        profile = await self.session.scalar(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        if profile is not None:
            if preference_key == "support_style":
                profile.support_style = value
            if preference_key == "preferred_support_mode":
                profile.preferred_support_mode = value

            profile.preference_profile_json = {
                **(profile.preference_profile_json or {}),
                preference_key: value,
            }

        await self.session.commit()

    async def persist_learned_preferences(
        self,
        *,
        user_id: str,
        learned_preferences: dict[str, str] | None,
    ) -> None:
        if not learned_preferences:
            return

        for key, value in learned_preferences.items():
            if value:
                await self.upsert_preference(
                    user_id=user_id,
                    preference_key=key,
                    value=value,
                    source="preference_learning_agent",
                    confidence_score=0.72,
                )