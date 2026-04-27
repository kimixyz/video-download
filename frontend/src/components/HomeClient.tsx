"use client";

import { useState } from "react";
import VideoInput, { ParseResult } from "@/components/VideoInput";
import VideoResult from "@/components/VideoResult";

export default function HomeClient() {
  const [result, setResult] = useState<ParseResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleResult = (data: ParseResult) => {
    setResult(data);
    setError("");
  };

  return (
    <>
      <VideoInput
        onResult={handleResult}
        onError={setError}
        onLoading={setLoading}
      />

      {error && (
        <div className="mt-4 flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm">
          <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

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

      {result && !loading && <VideoResult result={result} />}
    </>
  );
}