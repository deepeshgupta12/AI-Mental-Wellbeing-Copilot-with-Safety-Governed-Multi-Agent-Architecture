const CURRENT_USER_ID_KEY = "mwc_current_user_id";
const CURRENT_USER_EMAIL_KEY = "mwc_current_user_email";
const CURRENT_USER_NAME_KEY = "mwc_current_user_name";
const CURRENT_CONVERSATION_SESSION_ID_KEY = "mwc_current_conversation_session_id";
const PENDING_AUTH_EMAIL_KEY = "mwc_pending_auth_email";
const PENDING_AUTH_NAME_KEY = "mwc_pending_auth_name";
const MEMBER_ACCESS_TOKEN_KEY = "mwc_member_access_token";
const MEMBER_ACCESS_TOKEN_EXPIRES_AT_KEY = "mwc_member_access_token_expires_at";
const ADMIN_ACCESS_TOKEN_KEY = "mwc_admin_access_token";
const ADMIN_ACCESS_TOKEN_EXPIRES_AT_KEY = "mwc_admin_access_token_expires_at";

export type DemoAuthScope = "member" | "admin";

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
  clearPendingAuthIdentity();
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

export function setPendingAuthIdentity(params: {
  email: string;
  displayName?: string | null;
}) {
  safeSet(PENDING_AUTH_EMAIL_KEY, params.email);
  safeSet(PENDING_AUTH_NAME_KEY, params.displayName ?? "");
}

export function getPendingAuthEmail(): string | null {
  return safeGet(PENDING_AUTH_EMAIL_KEY);
}

export function getPendingAuthDisplayName(): string | null {
  return safeGet(PENDING_AUTH_NAME_KEY);
}

export function clearPendingAuthIdentity() {
  safeRemove(PENDING_AUTH_EMAIL_KEY);
  safeRemove(PENDING_AUTH_NAME_KEY);
}

export function clearCurrentUserSession() {
  safeRemove(CURRENT_USER_ID_KEY);
  safeRemove(CURRENT_USER_EMAIL_KEY);
  safeRemove(CURRENT_USER_NAME_KEY);
  safeRemove(CURRENT_CONVERSATION_SESSION_ID_KEY);
  clearPendingAuthIdentity();
  clearStoredAccessToken("member");
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

function getAccessTokenStorageKeys(scope: DemoAuthScope): {
  tokenKey: string;
  expiresAtKey: string;
} {
  return scope === "admin"
    ? {
        tokenKey: ADMIN_ACCESS_TOKEN_KEY,
        expiresAtKey: ADMIN_ACCESS_TOKEN_EXPIRES_AT_KEY,
      }
    : {
        tokenKey: MEMBER_ACCESS_TOKEN_KEY,
        expiresAtKey: MEMBER_ACCESS_TOKEN_EXPIRES_AT_KEY,
      };
}

export function setStoredAccessToken(params: {
  scope: DemoAuthScope;
  accessToken: string;
  expiresAt?: string | null;
}) {
  const { tokenKey, expiresAtKey } = getAccessTokenStorageKeys(params.scope);
  safeSet(tokenKey, params.accessToken);

  if (params.expiresAt) {
    safeSet(expiresAtKey, params.expiresAt);
  } else {
    safeRemove(expiresAtKey);
  }
}

export function getStoredAccessToken(scope: DemoAuthScope): string | null {
  const { tokenKey } = getAccessTokenStorageKeys(scope);
  return safeGet(tokenKey);
}

export function getStoredAccessTokenExpiry(scope: DemoAuthScope): string | null {
  const { expiresAtKey } = getAccessTokenStorageKeys(scope);
  return safeGet(expiresAtKey);
}

export function clearStoredAccessToken(scope: DemoAuthScope) {
  const { tokenKey, expiresAtKey } = getAccessTokenStorageKeys(scope);
  safeRemove(tokenKey);
  safeRemove(expiresAtKey);
}

export function isStoredAccessTokenValid(scope: DemoAuthScope): boolean {
  const token = getStoredAccessToken(scope);
  if (!token) return false;

  const expiresAt = getStoredAccessTokenExpiry(scope);
  if (!expiresAt) return true;

  const expiryMs = Date.parse(expiresAt);
  if (Number.isNaN(expiryMs)) return true;

  return expiryMs - Date.now() > 30_000;
}