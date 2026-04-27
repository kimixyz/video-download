"use client";

import { useState } from "react";
import { buildApiUrl, extractApiErrorMessage } from "@/lib/api";
import { extractShareUrl } from "@/lib/videoRules";

interface Props {
  onResult: (data: ParseResult) => void;
  onError: (msg: string) => void;
  onLoading: (loading: boolean) => void;
}

export interface ParseResult {
  title: string;
  thumbnail?: string;
  author?: string;
  platform: string;
  duration?: number;
  formats: VideoFormat[];
}

export interface VideoFormat {
  format_id: string;
  quality: string;
  ext: string;
  url: string;
  filesize?: number;
  vcodec?: string;
  acodec?: string;
}

export default function VideoInput({ onResult, onError, onLoading }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleParse = async () => {
    const trimmed = url.trim();
    if (!trimmed) {
      onError("请输入视频链接");
      return;
    }

    const extracted = extractShareUrl(trimmed);
    if (extracted !== trimmed) {
      setUrl(extracted);
    }

    setLoading(true);
    onLoading(true);
    onError("");

    try {
      const res = await fetch(buildApiUrl("/api/parse"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: extracted }),
      });

      const contentType = res.headers.get("content-type") || "";
      const isJsonResponse = contentType.includes("application/json");
      const payload = isJsonResponse ? await res.json() : await res.text();

      if (!res.ok) {
        throw new Error(
          isJsonResponse
            ? extractApiErrorMessage(payload, "解析失败，请稍后重试")
            : "解析服务返回了非 JSON 响应，请检查前端环境变量 NEXT_PUBLIC_API_BASE_URL 是否已配置并重新部署 Vercel",
        );
      }

      if (!isJsonResponse) {
        throw new Error("解析服务返回了 HTML 页面，通常表示前端还在请求错误地址。请确认 NEXT_PUBLIC_API_BASE_URL 已在 Vercel 生效并重新部署");
      }

      onResult(payload as ParseResult);
    } catch (err) {
      onError(
        err instanceof Error ? err.message : "网络错误，请检查后端服务是否运行",
      );
    } finally {
      setLoading(false);
      onLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleParse();
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(extractShareUrl(text));
      }
    } catch {
      // clipboard access denied, ignore
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="relative flex items-center gap-1.5 sm:gap-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-1.5 sm:p-2 shadow-2xl">
        {/* paste icon */}
        <button
          onClick={handlePaste}
          className="shrink-0 p-1.5 sm:p-2 text-gray-400 hover:text-white transition-colors"
          title="粘贴链接"
        >
          <svg
            className="w-4 h-4 sm:w-5 sm:h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </button>

        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="粘贴抖音、B站、YouTube 等视频链接..."
          className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-sm sm:text-base py-1.5 sm:py-2 min-w-0"
          disabled={loading}
          autoComplete="off"
        />

        {url && (
          <button
            onClick={() => setUrl("")}
            className="shrink-0 p-1.5 sm:p-2 text-gray-500 hover:text-white transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}

        <button
          onClick={handleParse}
          disabled={loading}
          className="shrink-0 flex items-center gap-2 bg-linear-to-r from-violet-600 to-blue-500 hover:from-violet-500 hover:to-blue-400 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold px-3 py-2.5 sm:px-6 sm:py-3 rounded-lg sm:rounded-xl transition-all duration-200 shadow-lg"
        >
          {loading ? (
            <>
              <svg
                className="w-4 h-4 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              <span className="hidden sm:inline">解析中</span>
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"
                />
              </svg>
              <span className="hidden sm:inline">解析</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
