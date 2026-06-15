"use client";

import { useState } from "react";
import { buildDownloadUrl } from "@/lib/api";
import type { VideoFormat } from "@/lib/parseResult";

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

export default function FormatList({ formats, title }: Props) {
  const [delogoEnabled, setDelogoEnabled] = useState(false);
  const [box, setBox] = useState({ x: 20, y: 20, width: 600, height: 110 });

  if (formats.length === 0) return null;

  const updateBox = (key: keyof typeof box, value: string) => {
    const next = Number.parseInt(value, 10);
    setBox((current) => ({
      ...current,
      [key]: Number.isFinite(next) ? Math.max(0, next) : 0,
    }));
  };

  const delogoOptions = {
    enabled: delogoEnabled,
    ...box,
  };

  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
        选择下载格式
      </h3>
      <div className="mb-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
        <label className="flex items-center justify-between gap-3">
          <span className="flex flex-col">
            <span className="text-sm font-medium text-white">FFmpeg 后处理修补水印</span>
            <span className="text-xs text-gray-400">
              适合左上角这类固定水印，会重新编码视频，下载更慢
            </span>
          </span>
          <input
            type="checkbox"
            checked={delogoEnabled}
            onChange={(event) => setDelogoEnabled(event.target.checked)}
            className="h-5 w-5 accent-blue-500"
          />
        </label>

        {delogoEnabled && (
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              ["x", "X"],
              ["y", "Y"],
              ["width", "宽"],
              ["height", "高"],
            ].map(([key, label]) => (
              <label key={key} className="flex flex-col gap-1 text-xs text-gray-400">
                {label}
                <input
                  type="number"
                  min={key === "width" || key === "height" ? 8 : 0}
                  value={box[key as keyof typeof box]}
                  onChange={(event) => updateBox(key as keyof typeof box, event.target.value)}
                  className="w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none focus:border-blue-400"
                />
              </label>
            ))}
          </div>
        )}
      </div>
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
              href={buildDownloadUrl(fmt.url, `${title}.${fmt.ext}`, delogoOptions)}
              download
              className="flex items-center gap-2 bg-linear-to-r from-violet-600 to-blue-500 hover:from-violet-500 hover:to-blue-400 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-all duration-200 shadow"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              {delogoEnabled ? "处理下载" : "下载"}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
