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

export type UserLanguagePreference = {
  user_id: string;
  preferred_language: string;
  content_language: string;
  fallback_language: string;
  supported_languages: string[];
};

export type LocalizationRuntimeCopy = {
  language: string;
  normalized_language: string;
  copy: Record<string, unknown>;
};

export type AdminLocalizationOverview = {
  default_language: string;
  supported_languages: string[];
  user_language_breakdown: Record<string, number>;
  care_plan_language_breakdown: Record<string, number>;
};