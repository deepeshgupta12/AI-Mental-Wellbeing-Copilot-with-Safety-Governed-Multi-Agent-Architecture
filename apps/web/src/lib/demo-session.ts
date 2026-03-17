const CURRENT_USER_ID_KEY = "mwc_current_user_id";
const CURRENT_USER_EMAIL_KEY = "mwc_current_user_email";
const CURRENT_USER_NAME_KEY = "mwc_current_user_name";
const CURRENT_CONVERSATION_SESSION_ID_KEY = "mwc_current_conversation_session_id";

export function setCurrentUserSession(params: {
  userId: string;
  email: string;
  displayName?: string | null;
}) {
  localStorage.setItem(CURRENT_USER_ID_KEY, params.userId);
  localStorage.setItem(CURRENT_USER_EMAIL_KEY, params.email);
  localStorage.setItem(CURRENT_USER_NAME_KEY, params.displayName ?? "");
}

export function getCurrentUserId(): string | null {
  return localStorage.getItem(CURRENT_USER_ID_KEY);
}

export function getCurrentUserEmail(): string | null {
  return localStorage.getItem(CURRENT_USER_EMAIL_KEY);
}

export function getCurrentUserDisplayName(): string | null {
  return localStorage.getItem(CURRENT_USER_NAME_KEY);
}

export function clearCurrentUserSession() {
  localStorage.removeItem(CURRENT_USER_ID_KEY);
  localStorage.removeItem(CURRENT_USER_EMAIL_KEY);
  localStorage.removeItem(CURRENT_USER_NAME_KEY);
  localStorage.removeItem(CURRENT_CONVERSATION_SESSION_ID_KEY);
}

export function setCurrentConversationSessionId(sessionId: string) {
  localStorage.setItem(CURRENT_CONVERSATION_SESSION_ID_KEY, sessionId);
}

export function getCurrentConversationSessionId(): string | null {
  return localStorage.getItem(CURRENT_CONVERSATION_SESSION_ID_KEY);
}

export function clearCurrentConversationSessionId() {
  localStorage.removeItem(CURRENT_CONVERSATION_SESSION_ID_KEY);
}