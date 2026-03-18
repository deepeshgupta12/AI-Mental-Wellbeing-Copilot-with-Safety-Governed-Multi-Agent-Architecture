const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!rawApiBaseUrl) {
  throw new Error("NEXT_PUBLIC_API_BASE_URL is not set");
}

export const env = {
  apiBaseUrl: rawApiBaseUrl.replace(/\/+$/, ""),
};