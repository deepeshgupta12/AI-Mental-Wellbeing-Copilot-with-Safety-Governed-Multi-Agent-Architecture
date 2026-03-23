from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_wellbeing_api.models.care_plan import CarePlan
from mental_wellbeing_api.models.user import UserPreference


class LocalizationService:
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = {
        "en": {
            "display_name": "English",
            "native_name": "English",
            "is_rtl": False,
        },
        "hi": {
            "display_name": "Hindi",
            "native_name": "हिन्दी",
            "is_rtl": False,
        },
        "hinglish": {
            "display_name": "Hinglish",
            "native_name": "Hinglish",
            "is_rtl": False,
        },
    }

    RUNTIME_COPY: dict[str, dict[str, str]] = {
        "en": {
            "crisis_open": "I'm glad you reached out.",
            "crisis_immediate": "If you may be in immediate danger or might act on these thoughts, contact local emergency services now.",
            "crisis_support": "If possible, reach out to a trusted person and ask them to stay with you right now.",
            "crisis_follow_up": "If you're not in immediate danger, tell me whether you want help taking the next safe step right now.",
            "care_plan_title_default": "Continue your care plan",
            "care_plan_step_complete": "Step completed",
        },
        "hi": {
            "crisis_open": "मुझे खुशी है कि आपने संपर्क किया।",
            "crisis_immediate": "अगर आपको लगता है कि आप तुरंत खतरे में हैं या इन विचारों पर अमल कर सकते हैं, तो अभी अपनी स्थानीय आपातकालीन सेवा से संपर्क करें।",
            "crisis_support": "अगर संभव हो, किसी भरोसेमंद व्यक्ति से तुरंत संपर्क करें और उनसे अपने साथ रहने के लिए कहें।",
            "crisis_follow_up": "अगर तत्काल खतरा नहीं है, तो बताइए क्या आप अभी अगला सुरक्षित कदम लेने में मदद चाहते हैं।",
            "care_plan_title_default": "अपना केयर प्लान जारी रखें",
            "care_plan_step_complete": "चरण पूरा हुआ",
        },
        "hinglish": {
            "crisis_open": "Accha hua aapne reach out kiya.",
            "crisis_immediate": "Agar aapko lag raha hai ki turant danger hai ya aap in thoughts par act kar sakte hain, to abhi local emergency services se contact kariye.",
            "crisis_support": "Agar possible ho to kisi trusted person ko abhi call ya message karke apne saath rehne ko bolo.",
            "crisis_follow_up": "Agar immediate danger nahi hai, to batao kya main abhi next safe step lene mein help karun.",
            "care_plan_title_default": "Apna care plan continue karo",
            "care_plan_step_complete": "Step complete hua",
        },
    }

    def __init__(self, session: AsyncSession | None) -> None:
        self.session = session

    def normalize_language(self, language: str | None) -> str:
        value = (language or self.DEFAULT_LANGUAGE).strip().lower()
        if value in self.SUPPORTED_LANGUAGES:
            return value
        if value.startswith("hi"):
            return "hi"
        if value in {"en-in", "en-us", "en-gb"}:
            return "en"
        return self.DEFAULT_LANGUAGE

    def catalog(self) -> dict[str, Any]:
        return {
            "default_language": self.DEFAULT_LANGUAGE,
            "supported_languages": [
                {
                    "language_code": code,
                    "display_name": meta["display_name"],
                    "native_name": meta["native_name"],
                    "is_rtl": bool(meta["is_rtl"]),
                    "enabled": True,
                }
                for code, meta in self.SUPPORTED_LANGUAGES.items()
            ],
            "safety_copy_keys": sorted(self.RUNTIME_COPY["en"].keys()),
            "localized_ui_sections": [
                "onboarding",
                "chat",
                "care_plans",
                "admin_localization",
            ],
        }

    def runtime_copy(self, language: str | None) -> dict[str, Any]:
        normalized = self.normalize_language(language)
        return {
            "language": language or self.DEFAULT_LANGUAGE,
            "normalized_language": normalized,
            "copy": self.RUNTIME_COPY.get(normalized, self.RUNTIME_COPY[self.DEFAULT_LANGUAGE]),
        }

    async def get_user_language_preference(self, user_id: str) -> dict[str, Any]:
        if self.session is None:
            raise ValueError("Database session is required")

        rows = list(
            (
                await self.session.scalars(
                    select(UserPreference)
                    .where(
                        UserPreference.user_id == user_id,
                        UserPreference.preference_key.in_(
                            [
                                "preferred_language",
                                "content_language",
                                "fallback_language",
                            ]
                        ),
                        UserPreference.is_active.is_(True),
                    )
                    .order_by(desc(UserPreference.created_at))
                )
            ).all()
        )

        latest_by_key: dict[str, UserPreference] = {}
        for row in rows:
            if row.preference_key not in latest_by_key:
                latest_by_key[row.preference_key] = row

        preferred = self.normalize_language(
            (
                latest_by_key.get("preferred_language")
                or UserPreference(
                    preference_value_json={"value": self.DEFAULT_LANGUAGE},
                    user_id=user_id,
                    preference_key="preferred_language",
                )
            ).preference_value_json.get("value")  # type: ignore[arg-type]
        )
        content = self.normalize_language(
            (
                latest_by_key.get("content_language")
                or UserPreference(
                    preference_value_json={"value": preferred},
                    user_id=user_id,
                    preference_key="content_language",
                )
            ).preference_value_json.get("value")  # type: ignore[arg-type]
        )
        fallback = self.normalize_language(
            (
                latest_by_key.get("fallback_language")
                or UserPreference(
                    preference_value_json={"value": self.DEFAULT_LANGUAGE},
                    user_id=user_id,
                    preference_key="fallback_language",
                )
            ).preference_value_json.get("value")  # type: ignore[arg-type]
        )

        return {
            "user_id": user_id,
            "preferred_language": preferred,
            "content_language": content,
            "fallback_language": fallback,
            "supported_languages": sorted(self.SUPPORTED_LANGUAGES.keys()),
        }

    async def upsert_user_language_preference(
        self,
        *,
        user_id: str,
        preferred_language: str,
        content_language: str | None,
        fallback_language: str | None,
    ) -> dict[str, Any]:
        if self.session is None:
            raise ValueError("Database session is required")

        normalized_preferred = self.normalize_language(preferred_language)
        normalized_content = self.normalize_language(content_language or normalized_preferred)
        normalized_fallback = self.normalize_language(fallback_language or self.DEFAULT_LANGUAGE)

        keys = {
            "preferred_language": normalized_preferred,
            "content_language": normalized_content,
            "fallback_language": normalized_fallback,
        }

        for preference_key, value in keys.items():
            row = UserPreference(
                user_id=user_id,
                preference_key=preference_key,
                preference_value_json={"value": value},
                source="user",
                confidence_score=1.0,
                is_active=True,
            )
            self.session.add(row)

        await self.session.commit()
        return await self.get_user_language_preference(user_id)

    def localize_text(self, key: str, language: str | None, fallback_text: str) -> str:
        normalized = self.normalize_language(language)
        return self.RUNTIME_COPY.get(normalized, {}).get(key, fallback_text)

    async def build_admin_overview(self, organization_id: str | None = None) -> dict[str, Any]:
        if self.session is None:
            raise ValueError("Database session is required")

        preference_rows = list(
            (
                await self.session.scalars(
                    select(UserPreference)
                    .where(
                        UserPreference.preference_key.in_(
                            [
                                "preferred_language",
                                "content_language",
                                "fallback_language",
                            ]
                        ),
                        UserPreference.is_active.is_(True),
                    )
                    .order_by(desc(UserPreference.created_at))
                    .limit(3000)
                )
            ).all()
        )

        latest_by_user_and_key: dict[tuple[str, str], UserPreference] = {}
        for row in preference_rows:
            compound_key = (str(row.user_id), str(row.preference_key))
            if compound_key not in latest_by_user_and_key:
                latest_by_user_and_key[compound_key] = row

        preferred_counter = Counter()
        content_counter = Counter()
        fallback_counter = Counter()

        for (_user_id, preference_key), row in latest_by_user_and_key.items():
            value = self.normalize_language((row.preference_value_json or {}).get("value"))
            if preference_key == "preferred_language":
                preferred_counter[value] += 1
            elif preference_key == "content_language":
                content_counter[value] += 1
            elif preference_key == "fallback_language":
                fallback_counter[value] += 1

        care_plan_stmt = select(CarePlan)
        if organization_id:
            care_plan_stmt = care_plan_stmt.where(CarePlan.organization_id == organization_id)
        care_plans = list((await self.session.scalars(care_plan_stmt.limit(1000))).all())

        care_plan_counter = Counter(
            self.normalize_language(item.preferred_language) for item in care_plans
        )

        return {
            "organization_id": organization_id,
            "default_language": self.DEFAULT_LANGUAGE,
            "supported_language_codes": sorted(self.SUPPORTED_LANGUAGES.keys()),
            "language_preference_breakdown": dict(preferred_counter),
            "content_language_breakdown": dict(content_counter),
            "fallback_language_breakdown": dict(fallback_counter),
            "care_plan_language_breakdown": dict(care_plan_counter),
        }