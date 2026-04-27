const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

export interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
    details?: string;
  };
  detail?: string;
  message?: string;
}

function normalizeApiBaseUrl(value?: string): string {
  if (!value) {
    return "";
  }

  return value.replace(/\/$/, "");
}

export const apiBaseUrl = normalizeApiBaseUrl(rawApiBaseUrl);

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  if (!apiBaseUrl) {
    return normalizedPath;
  }

  return `${apiBaseUrl}${normalizedPath}`;
}

export function buildDownloadUrl(videoUrl: string, filename: string): string {
  const searchParams = new URLSearchParams({
    url: videoUrl,
    filename,
  });

  return `${buildApiUrl("/api/download")}?${searchParams.toString()}`;
}

export function extractApiErrorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== "object") {
    return fallback;
  }

  const data = payload as ApiErrorResponse;

  if (typeof data.error?.message === "string" && data.error.message.trim()) {
    return data.error.message;
  }

  if (typeof data.detail === "string" && data.detail.trim()) {
    return data.detail;
  }

  if (typeof data.message === "string" && data.message.trim()) {
    return data.message;
  }

  return fallback;
}