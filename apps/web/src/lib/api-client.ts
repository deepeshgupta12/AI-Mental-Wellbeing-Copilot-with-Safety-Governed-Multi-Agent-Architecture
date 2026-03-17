import { env } from "@/config/env";

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

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { timeoutMs = 10000, headers, body, ...rest } = options;

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...rest,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      body,
      signal: controller.signal,
    });

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