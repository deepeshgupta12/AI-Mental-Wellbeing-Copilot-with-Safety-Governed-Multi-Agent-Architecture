export type LocalizationLanguageItem = {
  language_code: string;
  display_name: string;
  native_name: string;
  is_rtl: boolean;
  enabled: boolean;
};

export type LocalizationCatalog = {
  default_language: string;
  supported_languages: LocalizationLanguageItem[];
  safety_copy_keys: string[];
  localized_ui_sections: string[];
};

export type LocalizationRuntimeCopy = {
  language: string;
  normalized_language: string;
  copy: Record<string, string>;
};

export type UserLanguagePreference = {
  user_id: string;
  preferred_language: string;
  content_language: string;
  fallback_language: string;
  supported_languages: string[];
};

export type UpdateUserLanguagePreferencePayload = {
  preferred_language: string;
  content_language?: string | null;
  fallback_language?: string | null;
};

export type AdminLocalizationOverview = {
  organization_id?: string | null;
  default_language: string;
  supported_language_codes: string[];
  language_preference_breakdown: Record<string, number>;
  content_language_breakdown: Record<string, number>;
  fallback_language_breakdown: Record<string, number>;
  care_plan_language_breakdown: Record<string, number>;
  recent_preference_adoption_7d: Record<string, number>;
  recent_preference_adoption_30d: Record<string, number>;
  fallback_usage_count: number;
  top_preferred_language: string | null;
  top_care_plan_language: string | null;
  alignment_alerts: string[];
  fallback_gap_alerts: string[];
};