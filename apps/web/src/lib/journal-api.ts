import { apiRequest } from "@/lib/api-client";
import type { CreateJournalEntryPayload, JournalEntry } from "@/types/api";

export function createJournalEntry(
  payload: CreateJournalEntryPayload,
): Promise<JournalEntry> {
  return apiRequest<JournalEntry>("/api/v1/journal-entries", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listJournalEntries(userId: string): Promise<JournalEntry[]> {
  return apiRequest<JournalEntry[]>(
    `/api/v1/journal-entries?user_id=${encodeURIComponent(userId)}`,
  );
}