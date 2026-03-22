import { env } from "@/config/env";
import {
  clearStoredAccessToken,
  type DemoAuthScope,
  getCurrentUserDisplayName,
  getCurrentUserEmail,
  getPendingAuthDisplayName,
  getPendingAuthEmail,
  getStoredAccessToken,
  isStoredAccessTokenValid,
  setCurrentUserSession,
  setStoredAccessToken,
} from "@/lib/demo-session";

export class ApiError extends Error {
  status: number;
  statusText: string;
  body: unknown;

  constructor(params: {
    message: string;
    status: number;
    statusText: string;
    body: unknown;
  }) {
    super(params.message);
    this.name = "ApiError";
    this.status = params.status;
    this.statusText = params.statusText;
    this.body = params.body;
  }
}

type RequestOptions = RequestInit & {
  timeoutMs?: number;
};

type DevSessionBootstrapResponse = {
  access_token: string;
  expires_at?: string | null;
  user: {
    id: string;
    email: string;
    profile?: {
      display_name?: string | null;
    } | null;
  };
};

const DEFAULT_DEMO_ORG_NAME = "Aether Demo Org";
const DEFAULT_DEMO_ORG_SLUG = "aether-demo-org";
const DEFAULT_MEMBER_EMAIL = "demo-member@example.com";
const DEFAULT_MEMBER_NAME = "Aether Demo Member";
const DEFAULT_ADMIN_EMAIL = "demo-admin@example.com";
const DEFAULT_ADMIN_NAME = "Aether Demo Admin";

let memberBootstrapPromise: Promise<string | null> | null = null;
let adminBootstrapPromise: Promise<string | null> | null = null;

async function parseErrorBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

function isProtectedPath(path: string): boolean {
  return path.startsWith("/api/v1/admin/") || path.startsWith("/api/v1/external-integrations/");
}

function getScopeForPath(path: string): DemoAuthScope {
  return path.startsWith("/api/v1/admin/") ? "admin" : "member";
}

function getDefaultIdentity(scope: DemoAuthScope): { email: string; displayName: string } {
  return scope === "admin"
    ? { email: DEFAULT_ADMIN_EMAIL, displayName: DEFAULT_ADMIN_NAME }
    : { email: DEFAULT_MEMBER_EMAIL, displayName: DEFAULT_MEMBER_NAME };
}

function getPreferredIdentity(scope: DemoAuthScope): { email: string; displayName: string } {
  const defaultIdentity = getDefaultIdentity(scope);

  if (scope === "admin") {
    return defaultIdentity;
  }

  const email = getCurrentUserEmail() ?? getPendingAuthEmail() ?? defaultIdentity.email;
  const displayName =
    getCurrentUserDisplayName() ?? getPendingAuthDisplayName() ?? defaultIdentity.displayName;

  return {
    email,
    displayName: displayName || defaultIdentity.displayName,
  };
}

async function bootstrapDevSession(scope: DemoAuthScope): Promise<string | null> {
  const existingToken = getStoredAccessToken(scope);
  if (existingToken && isStoredAccessTokenValid(scope)) {
    return existingToken;
  }

  const inFlightPromise = scope === "admin" ? adminBootstrapPromise : memberBootstrapPromise;
  if (inFlightPromise) {
    return inFlightPromise;
  }

  const bootstrapPromise = (async () => {
    const identity = getPreferredIdentity(scope);
    const roleName = scope === "admin" ? "platform_admin" : "member";

    const response = await fetch(`${env.apiBaseUrl}/api/v1/auth/dev-session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: identity.email,
        display_name: identity.displayName,
        organization_name: DEFAULT_DEMO_ORG_NAME,
        organization_slug: DEFAULT_DEMO_ORG_SLUG,
        role_name: roleName,
      }),
    });

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as DevSessionBootstrapResponse;

    if (!payload.access_token) {
      return null;
    }

    setStoredAccessToken({
      scope,
      accessToken: payload.access_token,
      expiresAt: payload.expires_at ?? null,
    });

    if (scope === "member") {
      setCurrentUserSession({
        userId: payload.user.id,
        email: payload.user.email,
        displayName: payload.user.profile?.display_name ?? identity.displayName,
      });
    }

    return payload.access_token;
  })();

  if (scope === "admin") {
    adminBootstrapPromise = bootstrapPromise;
  } else {
    memberBootstrapPromise = bootstrapPromise;
  }

  try {
    return await bootstrapPromise;
  } finally {
    if (scope === "admin") {
      adminBootstrapPromise = null;
    } else {
      memberBootstrapPromise = null;
    }
  }
}

async function getAccessTokenForPath(path: string): Promise<string | null> {
  const scope = getScopeForPath(path);

  if (isStoredAccessTokenValid(scope)) {
    return getStoredAccessToken(scope);
  }

  return bootstrapDevSession(scope);
}

function buildRequestHeaders(
  body: BodyInit | null | undefined,
  headers: HeadersInit | undefined,
  accessToken: string | null,
): HeadersInit {
  return {
    ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...headers,
  };
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { timeoutMs = 10000, headers, body, ...rest } = options;

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const protectedPath = isProtectedPath(path);
    const initialAccessToken = protectedPath ? await getAccessTokenForPath(path) : null;

    let response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...rest,
      headers: buildRequestHeaders(body, headers, initialAccessToken),
      body,
      signal: controller.signal,
    });

    if (response.status === 401 && protectedPath) {
      const scope = getScopeForPath(path);
      clearStoredAccessToken(scope);
      const refreshedAccessToken = await bootstrapDevSession(scope);

      if (refreshedAccessToken) {
        response = await fetch(`${env.apiBaseUrl}${path}`, {
          ...rest,
          headers: buildRequestHeaders(body, headers, refreshedAccessToken),
          body,
          signal: controller.signal,
        });
      }
    }

    if (!response.ok) {
      const errorBody = await parseErrorBody(response);

      throw new ApiError({
        message: `API request failed: ${response.status} ${response.statusText}`,
        status: response.status,
        statusText: response.statusText,
        body: errorBody,
      });
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request timed out while calling the API.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const body = error.body;

    if (
      body &&
      typeof body === "object" &&
      "detail" in body &&
      typeof (body as { detail?: unknown }).detail === "string"
    ) {
      return (body as { detail: string }).detail;
    }

    return `${error.status} ${error.statusText}`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong while calling the API.";
}