import { apiRequest } from "@/lib/api-client";
import type {
  AdminLocalizationOverview,
  LocalizationCatalog,
  LocalizationRuntimeCopy,
  UserLanguagePreference,
} from "@/types/localization";

export function getLocalizationCatalog(): Promise<LocalizationCatalog> {
  return apiRequest<LocalizationCatalog>("/api/v1/localization/catalog");
}

export function getLocalizationRuntimeCopy(language?: string | null): Promise<LocalizationRuntimeCopy> {
  const query = language ? `?language=${encodeURIComponent(language)}` : "";
  return apiRequest<LocalizationRuntimeCopy>(`/api/v1/localization/runtime-copy${query}`);
}

export function getUserLanguagePreference(userId: string): Promise<UserLanguagePreference> {
  return apiRequest<UserLanguagePreference>(`/api/v1/users/${userId}/language`);
}

export function updateUserLanguagePreference(
  userId: string,
  payload: {
    preferred_language: string;
    content_language?: string | null;
    fallback_language?: string | null;
  },
): Promise<UserLanguagePreference> {
  return apiRequest<UserLanguagePreference>(`/api/v1/users/${userId}/language`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function getAdminLocalizationOverview(
  organizationId?: string | null,
): Promise<AdminLocalizationOverview> {
  const query = organizationId ? `?organization_id=${encodeURIComponent(organizationId)}` : "";
  return apiRequest<AdminLocalizationOverview>(`/api/v1/admin/localization/overview${query}`);
}