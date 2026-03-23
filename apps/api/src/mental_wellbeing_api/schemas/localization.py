from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LocalizationLanguageItemResponse(BaseModel):
    language_code: str
    display_name: str
    native_name: str
    is_rtl: bool = False
    enabled: bool = True


class LocalizationCatalogResponse(BaseModel):
    default_language: str = "en"
    supported_languages: list[LocalizationLanguageItemResponse] = Field(default_factory=list)
    safety_copy_keys: list[str] = Field(default_factory=list)
    localized_ui_sections: list[str] = Field(default_factory=list)


class UserLanguagePreferenceResponse(BaseModel):
    user_id: str
    preferred_language: str
    content_language: str
    fallback_language: str
    supported_languages: list[str] = Field(default_factory=list)


class UserLanguagePreferenceUpdateRequest(BaseModel):
    preferred_language: str
    content_language: str | None = None
    fallback_language: str | None = None


class LocalizationRuntimeCopyResponse(BaseModel):
    language: str
    normalized_language: str
    copy: dict[str, Any] = Field(default_factory=dict)


class AdminLocalizationOverviewResponse(BaseModel):
    organization_id: str | None = None
    default_language: str = "en"
    supported_language_codes: list[str] = Field(default_factory=list)
    language_preference_breakdown: dict[str, int] = Field(default_factory=dict)
    content_language_breakdown: dict[str, int] = Field(default_factory=dict)
    fallback_language_breakdown: dict[str, int] = Field(default_factory=dict)
    care_plan_language_breakdown: dict[str, int] = Field(default_factory=dict)