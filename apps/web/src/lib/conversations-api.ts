import { apiRequest } from "@/lib/api-client";
import type {
  ConversationMessage,
  ConversationSession,
  CreateConversationMessagePayload,
  CreateConversationSessionPayload,
} from "@/types/api";

export function createConversationSession(
  payload: CreateConversationSessionPayload,
): Promise<ConversationSession> {
  return apiRequest<ConversationSession>("/api/v1/conversations/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listConversationSessions(
  userId: string,
): Promise<ConversationSession[]> {
  return apiRequest<ConversationSession[]>(
    `/api/v1/conversations/sessions?user_id=${encodeURIComponent(userId)}`,
  );
}

export function createConversationMessage(
  payload: CreateConversationMessagePayload,
): Promise<ConversationMessage> {
  return apiRequest<ConversationMessage>("/api/v1/conversations/messages", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listConversationMessages(
  sessionId: string,
): Promise<ConversationMessage[]> {
  return apiRequest<ConversationMessage[]>(
    `/api/v1/conversations/messages?session_id=${encodeURIComponent(sessionId)}`,
  );
}