export interface VideoFormat {
  format_id: string;
  quality: string;
  ext: string;
  url: string;
  filesize?: number;
  vcodec?: string;
  acodec?: string;
}

export interface ParseResult {
  title: string;
  thumbnail?: string;
  author?: string;
  platform: string;
  duration?: number;
  formats: VideoFormat[];
}

const INVALID_PARSE_RESULT_MESSAGE = "解析服务返回的数据格式异常";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function optionalString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value : undefined;
}

function optionalNumber(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function parseVideoFormat(value: unknown): VideoFormat {
  if (!isRecord(value)) {
    throw new Error(INVALID_PARSE_RESULT_MESSAGE);
  }

  const formatId = optionalString(value.format_id);
  const quality = optionalString(value.quality);
  const ext = optionalString(value.ext);
  const url = optionalString(value.url);

  if (!formatId || !quality || !ext || !url) {
    throw new Error(INVALID_PARSE_RESULT_MESSAGE);
  }

  return {
    format_id: formatId,
    quality,
    ext,
    url,
    filesize: optionalNumber(value.filesize),
    vcodec: optionalString(value.vcodec),
    acodec: optionalString(value.acodec),
  };
}

export function parseParseResult(value: unknown): ParseResult {
  if (!isRecord(value)) {
    throw new Error(INVALID_PARSE_RESULT_MESSAGE);
  }

  const title = optionalString(value.title);
  const platform = optionalString(value.platform);

  if (!title || !platform || !Array.isArray(value.formats)) {
    throw new Error(INVALID_PARSE_RESULT_MESSAGE);
  }

  return {
    title,
    thumbnail: optionalString(value.thumbnail),
    author: optionalString(value.author),
    platform,
    duration: optionalNumber(value.duration),
    formats: value.formats.map(parseVideoFormat),
  };
}
