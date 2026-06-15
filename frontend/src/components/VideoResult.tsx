"use client";

import Image from "next/image";
import { useState } from "react";
import FormatList from "./FormatList";
import { buildDownloadUrl } from "@/lib/api";
import { getPlatformLabel } from "@/lib/videoRules";
import type { ParseResult } from "@/lib/parseResult";

interface Props {
  result: ParseResult;
}

type PreviewTab = "video" | "image" | "title";

function formatDuration(seconds?: number): string {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function VideoResult({ result }: Props) {
  const [activeTab, setActiveTab] = useState<PreviewTab>("video");
  const platformLabel = getPlatformLabel(result.platform);
  const duration = formatDuration(result.duration);
  const previewFormat = result.formats[0];
  const previewVideoUrl = previewFormat
    ? buildDownloadUrl(previewFormat.url, `${result.title}.${previewFormat.ext}`)
    : "";
  const tabs: Array<{ id: PreviewTab; label: string }> = [
    { id: "video", label: "视频" },
    { id: "image", label: "图片" },
    { id: "title", label: "标题" },
  ];

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
      <div className="bg-white/95 text-gray-900">
        <div className="grid grid-cols-3 border-b border-gray-200 px-4 pt-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`relative py-3 text-center text-base font-semibold transition-colors ${
                activeTab === tab.id ? "text-emerald-500" : "text-gray-500 hover:text-gray-800"
              }`}
            >
              {tab.label}
              {activeTab === tab.id && (
                <span className="absolute inset-x-4 bottom-0 h-0.5 rounded-full bg-emerald-500" />
              )}
            </button>
          ))}
        </div>

        <div className="relative bg-black">
          {activeTab === "video" && previewFormat ? (
            <video
              className="aspect-video w-full bg-black object-contain"
              controls
              playsInline
              poster={result.thumbnail}
              preload="metadata"
              src={previewVideoUrl}
            />
          ) : activeTab === "image" && result.thumbnail ? (
            <div className="relative aspect-video w-full">
              <Image
                src={result.thumbnail}
                alt={result.title}
                fill
                className="object-contain"
                unoptimized
              />
            </div>
          ) : activeTab === "title" ? (
            <div className="flex min-h-72 flex-col justify-center gap-3 bg-white px-5 py-8">
              <span className="w-fit rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-600">
                {platformLabel}
              </span>
              <h2 className="text-xl font-semibold leading-snug text-gray-900">
                {result.title}
              </h2>
              {result.author && (
                <p className="text-sm text-gray-500">{result.author}</p>
              )}
            </div>
          ) : (
            <div className="flex aspect-video w-full items-center justify-center bg-gray-100 text-sm text-gray-500">
              暂无预览
            </div>
          )}

          {activeTab !== "title" && duration && (
            <span className="absolute bottom-3 right-3 rounded bg-black/65 px-2 py-1 text-sm font-semibold text-white">
              {duration}
            </span>
          )}
        </div>

        <div className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <div className="mb-1 flex items-center gap-2">
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-600">
                {platformLabel}
              </span>
              {previewFormat && (
                <span className="rounded border border-gray-200 px-2 py-0.5 text-xs font-medium text-gray-500">
                  清晰度：{previewFormat.quality}
                </span>
              )}
              {previewFormat?.filesize && (
                <span className="rounded border border-gray-200 px-2 py-0.5 text-xs font-medium text-gray-500">
                  体积：{(previewFormat.filesize / (1024 * 1024)).toFixed(2)}MB
                </span>
              )}
            </div>
            <h2 className="line-clamp-2 text-base font-semibold leading-snug text-gray-900">
              {result.title}
            </h2>
            {result.author && (
              <p className="mt-1 truncate text-sm text-gray-500">{result.author}</p>
            )}
          </div>
          <div className="flex gap-2">
            {previewFormat && (
              <button
                type="button"
                onClick={() => navigator.clipboard.writeText(previewFormat.url)}
                className="rounded-lg border border-emerald-500 px-4 py-2 text-sm font-semibold text-emerald-600 transition-colors hover:bg-emerald-50"
              >
                复制链接
              </button>
            )}
          </div>
        </div>
      </div>

      {/* divider */}
      <div className="border-t border-white/10 mx-5" />

      {/* format list */}
      <div className="p-5">
        <FormatList formats={result.formats} title={result.title} />
      </div>
    </div>
  );
}
