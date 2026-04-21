"use client";

import { useState } from "react";
import VideoInput, { ParseResult } from "@/components/VideoInput";
import VideoResult from "@/components/VideoResult";
import PlatformBadges from "@/components/PlatformBadges";
import FAQ from "@/components/FAQ";

export default function Home() {
  const [result, setResult] = useState<ParseResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleResult = (data: ParseResult) => {
    setResult(data);
    setError("");
  };

  return (
    <div className="min-h-screen bg-[#0f0f1a] text-white flex flex-col">
      {/* header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-linear-to-br from-violet-600 to-blue-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <span className="font-bold text-lg">视频解析下载</span>
        </div>
        <span className="text-xs text-gray-500">仅供个人学习使用</span>
      </header>

      {/* hero */}
      <section className="relative flex flex-col items-center justify-center py-20 px-4 overflow-hidden">
        {/* background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-150 h-150 rounded-full bg-violet-900/30 blur-3xl" />
          <div className="absolute top-20 left-1/4 w-75 h-75 rounded-full bg-blue-900/20 blur-3xl" />
        </div>

        <div className="relative z-10 text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-4 bg-linear-to-r from-violet-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
            在线视频解析下载
          </h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            支持抖音、B站、YouTube、TikTok 等 10+ 平台，去水印极速下载
          </p>
        </div>

        <div className="relative z-10 w-full max-w-2xl">
          <VideoInput
            onResult={handleResult}
            onError={setError}
            onLoading={setLoading}
          />

          {/* error */}
          {error && (
            <div className="mt-4 flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm">
              <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          )}

          {/* loading skeleton */}
          {loading && !result && (
            <div className="mt-6 w-full bg-white/5 border border-white/10 rounded-2xl p-5 animate-pulse">
              <div className="flex gap-4">
                <div className="w-32 h-20 bg-white/10 rounded-lg shrink-0" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-white/10 rounded w-1/3" />
                  <div className="h-4 bg-white/10 rounded w-3/4" />
                  <div className="h-4 bg-white/10 rounded w-1/2" />
                </div>
              </div>
            </div>
          )}

          {/* result */}
          {result && !loading && <VideoResult result={result} />}
        </div>
      </section>

      {/* platform badges */}
      <PlatformBadges />

      {/* divider */}
      <div className="border-t border-white/10 mx-6" />

      {/* FAQ */}
      <FAQ />

      {/* footer */}
      <footer className="mt-auto border-t border-white/10 py-6 px-4 text-center text-gray-600 text-sm">
        视频归相关网站及作者所有，本站不存储任何视频，仅供个人学习使用
      </footer>
    </div>
  );
}
