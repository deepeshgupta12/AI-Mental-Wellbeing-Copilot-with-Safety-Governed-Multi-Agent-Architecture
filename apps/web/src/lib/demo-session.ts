const CURRENT_USER_ID_KEY = "mwc_current_user_id";
const CURRENT_USER_EMAIL_KEY = "mwc_current_user_email";
const CURRENT_USER_NAME_KEY = "mwc_current_user_name";
const CURRENT_CONVERSATION_SESSION_ID_KEY = "mwc_current_conversation_session_id";

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function safeGet(key: string): string | null {
  if (!canUseStorage()) return null;

  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function safeSet(key: string, value: string): void {
  if (!canUseStorage()) return;

  try {
    window.localStorage.setItem(key, value);
  } catch {
    // ignore storage failures in demo mode
  }
}

function safeRemove(key: string): void {
  if (!canUseStorage()) return;

  try {
    window.localStorage.removeItem(key);
  } catch {
    // ignore storage failures in demo mode
  }
}

export function setCurrentUserSession(params: {
  userId: string;
  email: string;
  displayName?: string | null;
}) {
  safeSet(CURRENT_USER_ID_KEY, params.userId);
  safeSet(CURRENT_USER_EMAIL_KEY, params.email);
  safeSet(CURRENT_USER_NAME_KEY, params.displayName ?? "");
}

export function getCurrentUserId(): string | null {
  return safeGet(CURRENT_USER_ID_KEY);
}

export function getCurrentUserEmail(): string | null {
  return safeGet(CURRENT_USER_EMAIL_KEY);
}

export function getCurrentUserDisplayName(): string | null {
  return safeGet(CURRENT_USER_NAME_KEY);
}

export function clearCurrentUserSession() {
  safeRemove(CURRENT_USER_ID_KEY);
  safeRemove(CURRENT_USER_EMAIL_KEY);
  safeRemove(CURRENT_USER_NAME_KEY);
  safeRemove(CURRENT_CONVERSATION_SESSION_ID_KEY);
}

export function setCurrentConversationSessionId(sessionId: string) {
  safeSet(CURRENT_CONVERSATION_SESSION_ID_KEY, sessionId);
}

export function getCurrentConversationSessionId(): string | null {
  return safeGet(CURRENT_CONVERSATION_SESSION_ID_KEY);
}

export function clearCurrentConversationSessionId() {
  safeRemove(CURRENT_CONVERSATION_SESSION_ID_KEY);
}