"use client";

import { VideoFormat } from "./VideoInput";

interface Props {
  formats: VideoFormat[];
  title: string;
}

const PLATFORM_QUALITY_COLORS: Record<string, string> = {
  "2160P": "bg-purple-600",
  "1440P": "bg-violet-600",
  "高清 1080P": "bg-blue-600",
  "1080P HD": "bg-blue-600",
  "1080P": "bg-blue-500",
  "标清 720P": "bg-cyan-600",
  "720P HD": "bg-cyan-600",
  "720P": "bg-cyan-500",
  "流畅 360P": "bg-gray-500",
  "480P": "bg-green-600",
  "360P": "bg-gray-500",
};

function qualityColor(quality: string): string {
  return PLATFORM_QUALITY_COLORS[quality] || "bg-gray-600";
}

function formatFileSize(bytes?: number): string {
  if (!bytes) return "";
  const mb = bytes / (1024 * 1024);
  if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
  return `${mb.toFixed(1)} MB`;
}

function buildDownloadUrl(videoUrl: string, title: string, ext: string): string {
  const encoded = encodeURIComponent(videoUrl);
  const filename = encodeURIComponent(`${title}.${ext}`);
  return `/api/download?url=${encoded}&filename=${filename}`;
}

export default function FormatList({ formats, title }: Props) {
  if (formats.length === 0) return null;

  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
        选择下载格式
      </h3>
      <div className="space-y-2">
        {formats.map((fmt) => (
          <div
            key={fmt.format_id}
            className="flex items-center justify-between gap-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl px-4 py-3 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span
                className={`${qualityColor(fmt.quality)} text-white text-xs font-bold px-2 py-1 rounded-md min-w-17.5 text-center`}
              >
                {fmt.quality}
              </span>
              <div className="flex flex-col">
                <span className="text-white text-sm font-medium uppercase">{fmt.ext}</span>
                {fmt.filesize && (
                  <span className="text-gray-500 text-xs">{formatFileSize(fmt.filesize)}</span>
                )}
              </div>
            </div>

            <a
              href={buildDownloadUrl(fmt.url, title, fmt.ext)}
              download
              className="flex items-center gap-2 bg-linear-to-r from-violet-600 to-blue-500 hover:from-violet-500 hover:to-blue-400 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-all duration-200 shadow"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
