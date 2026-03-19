import { apiRequest } from "@/lib/api-client";
import type { SupportTrack } from "@/types/api";

export function listSupportTracks(): Promise<SupportTrack[]> {
  return apiRequest<SupportTrack[]>("/api/v1/support-tracks");
}