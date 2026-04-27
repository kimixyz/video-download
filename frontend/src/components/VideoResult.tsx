"use client";

import Image from "next/image";
import { ParseResult } from "./VideoInput";
import FormatList from "./FormatList";
import { getPlatformLabel } from "@/lib/videoRules";

interface Props {
  result: ParseResult;
}

function formatDuration(seconds?: number): string {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function VideoResult({ result }: Props) {
  const platformLabel = getPlatformLabel(result.platform);
  const duration = formatDuration(result.duration);

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
      {/* thumbnail + info */}
      <div className="flex gap-4 p-5">
        {result.thumbnail ? (
          <div className="shrink-0 w-32 h-20 rounded-lg overflow-hidden relative bg-gray-800">
            <Image
              src={result.thumbnail}
              alt={result.title}
              fill
              className="object-cover"
              unoptimized
            />
            {duration && (
              <span className="absolute bottom-1 right-1 bg-black/70 text-white text-xs px-1.5 py-0.5 rounded">
                {duration}
              </span>
            )}
          </div>
        ) : (
          <div className="shrink-0 w-32 h-20 rounded-lg bg-gray-800 flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-linear-to-r from-violet-600 to-blue-500 text-white text-xs font-semibold px-2 py-0.5 rounded-full">
              {platformLabel}
            </span>
          </div>
          <h2 className="text-white font-semibold text-base leading-snug line-clamp-2 mb-1">
            {result.title}
          </h2>
          {result.author && (
            <p className="text-gray-500 text-sm truncate">
              <span className="text-gray-400">{result.author}</span>
            </p>
          )}
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
