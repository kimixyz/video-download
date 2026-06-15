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
      <div className="p-5">
        <div className="mb-4 inline-grid grid-cols-3 rounded-xl border border-white/10 bg-white/5 p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${
                activeTab === tab.id
                  ? "bg-linear-to-r from-violet-600 to-blue-500 text-white shadow"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-4 sm:flex-row">
          <div className="relative w-full shrink-0 overflow-hidden rounded-xl border border-white/10 bg-black sm:w-56">
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
                  className="object-cover"
                  unoptimized
                />
              </div>
            ) : activeTab === "title" ? (
              <div className="flex aspect-video w-full items-center justify-center px-4 text-center text-sm font-semibold leading-snug text-white">
                <span className="line-clamp-3">{result.title}</span>
              </div>
            ) : (
              <div className="flex aspect-video w-full items-center justify-center text-sm text-gray-500">
                暂无预览
              </div>
            )}

            {activeTab !== "title" && duration && (
              <span className="absolute bottom-2 right-2 rounded bg-black/70 px-1.5 py-0.5 text-xs font-semibold text-white">
                {duration}
              </span>
            )}
          </div>

          <div className="min-w-0 flex-1">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="bg-linear-to-r from-violet-600 to-blue-500 text-white text-xs font-semibold px-2 py-0.5 rounded-full">
                {platformLabel}
              </span>
              {previewFormat && (
                <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 text-xs font-medium text-gray-400">
                  {previewFormat.quality}
                </span>
              )}
              {previewFormat?.filesize && (
                <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 text-xs font-medium text-gray-400">
                  {(previewFormat.filesize / (1024 * 1024)).toFixed(2)} MB
                </span>
              )}
            </div>
            <h2 className="line-clamp-2 text-base font-semibold leading-snug text-white">
              {result.title}
            </h2>
            {result.author && (
              <p className="mt-1 truncate text-sm text-gray-500">{result.author}</p>
            )}
            {previewFormat && (
              <button
                type="button"
                onClick={() => navigator.clipboard.writeText(previewFormat.url)}
                className="mt-3 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-gray-200 transition-colors hover:bg-white/10 hover:text-white"
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
