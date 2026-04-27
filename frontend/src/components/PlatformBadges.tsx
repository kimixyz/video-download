import type { ReactNode } from "react";

import { videoPlatforms } from "@/lib/videoRules";

const PLATFORM_BADGE_STYLES: Record<string, { color: string; textColor: string; icon: ReactNode }> = {
  douyin: {
    color: "from-gray-900 to-black",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.34 6.34 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V9.05a8.16 8.16 0 004.77 1.52V7.12a4.85 4.85 0 01-1-.43z" />
      </svg>
    ),
  },
  xigua: {
    color: "from-orange-500 to-red-500",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <path
          d="M12.2 2.7c5 0 9.1 3.9 9.1 8.8 0 3.8-2.4 6.9-5.9 8.2-.8.3-1.3 1-1.5 1.8-.2 1-.9 1.6-1.9 1.6h-1.3c-1 0-1.8-.7-2-1.7-.2-.9-.8-1.6-1.6-2-2.9-1.3-4.8-4.1-4.8-7.3 0-5.1 4.4-9.4 9.9-9.4z"
          fill="#ff1f3d"
        />
        <path
          d="M10.45 9.35c0-.35.39-.57.69-.4l4.12 2.36c.31.18.31.63 0 .81l-4.12 2.36c-.3.17-.69-.05-.69-.4v-4.73z"
          fill="white"
        />
      </svg>
    ),
  },
  toutiao: {
    color: "from-red-500 to-red-600",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <rect x="2.8" y="4.1" width="18.4" height="15.8" rx="2.8" fill="white" />
        <g transform="rotate(-2.8 12 12)">
          <rect x="3.3" y="6.1" width="17.4" height="11.8" rx="1.5" fill="#ff3445" />
          <text
            x="12"
            y="14.45"
            textAnchor="middle"
            fontSize="6.7"
            fontWeight="700"
            fill="white"
            fontFamily="PingFang SC, Microsoft YaHei, Noto Sans SC, sans-serif"
          >
            头条
          </text>
        </g>
      </svg>
    ),
  },
  bilibili: {
    color: "from-blue-400 to-cyan-400",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L9.653 4.44c.071.071.134.142.187.213h4.267a.836.836 0 0 1 .16-.213l2.853-2.747c.267-.249.573-.373.92-.373.347 0 .662.151.929.4.267.249.391.551.391.907 0 .355-.124.657-.373.906zM5.333 7.24c-.746.018-1.373.276-1.88.773-.506.498-.769 1.13-.786 1.894v7.52c.017.764.28 1.395.786 1.893.507.498 1.134.756 1.88.773h13.334c.746-.017 1.373-.275 1.88-.773.506-.498.769-1.129.786-1.893v-7.52c-.017-.765-.28-1.396-.786-1.894-.507-.497-1.134-.755-1.88-.773zM8 11.107c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c0-.373.129-.689.386-.947.258-.257.574-.386.947-.386zm8 0c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c.017-.391.15-.711.4-.96.249-.249.56-.373.933-.373z" />
      </svg>
    ),
  },
  xiaohongshu: {
    color: "from-red-400 to-rose-500",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-4-4 1.41-1.41L11 14.17l6.59-6.59L19 9l-8 8z" />
      </svg>
    ),
  },
  kuaishou: {
    color: "from-orange-400 to-yellow-400",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M8 5v14l11-7z" />
      </svg>
    ),
  },
  weibo: {
    color: "from-red-500 to-orange-400",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <ellipse cx="11" cy="13" rx="7.5" ry="5" stroke="white" strokeWidth="1.8" />
        <circle cx="11" cy="13" r="2.1" fill="white" />
        <circle cx="11" cy="13" r="0.9" fill="currentColor" />
        <path
          d="M14.8 5.3c1.7.1 3 .7 4 1.8s1.5 2.5 1.5 4.1"
          stroke="white"
          strokeWidth="1.8"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M14.2 7.8c1 .1 1.9.5 2.5 1.1.6.7.9 1.5 1 2.5"
          stroke="white"
          strokeWidth="1.8"
          strokeLinecap="round"
          fill="none"
        />
        <circle cx="14.3" cy="8.3" r="1.2" fill="white" />
      </svg>
    ),
  },
  youtube: {
    color: "from-red-600 to-red-700",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
      </svg>
    ),
  },
  tiktok: {
    color: "from-gray-900 to-gray-800",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.34 6.34 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V9.05a8.16 8.16 0 004.77 1.52V7.12a4.85 4.85 0 01-1-.43z" />
      </svg>
    ),
  },
  twitter: {
    color: "from-gray-950 to-black",
    textColor: "text-white",
    icon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
      </svg>
    ),
  },
};

export default function PlatformBadges() {
  return (
    <section className="py-12 px-4">
      <h2 className="text-center text-xl font-semibold text-gray-300 mb-8">
        支持 {videoPlatforms.length}+ 主流平台
      </h2>
      <div className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto">
        {videoPlatforms.map((platform) => {
          const style = PLATFORM_BADGE_STYLES[platform.id];
          return (
            <div
              key={platform.id}
              className={`flex items-center gap-2 px-4 py-2 rounded-full bg-linear-to-r ${style.color} ${style.textColor} text-sm font-medium shadow-lg`}
            >
              {style.icon}
              {platform.displayName}
            </div>
          );
        })}
      </div>
    </section>
  );
}
