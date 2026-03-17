import { env } from "@/config/env";

type RequestOptions = RequestInit & {
  timeoutMs?: number;
};

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { timeoutMs = 10000, headers, ...rest } = options;

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...rest,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(
        `API request failed: ${response.status} ${response.statusText} - ${text}`,
      );
    }

    return (await response.json()) as T;
  } finally {
    window.clearTimeout(timeoutId);
  }
}