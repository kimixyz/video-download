const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

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