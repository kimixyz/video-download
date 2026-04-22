import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // In local development, proxy to the uvicorn backend at :8000.
    // In production (Vercel), vercel.json handles /api/* routing.
    if (process.env.NODE_ENV !== "development") {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "**" },
    ],
  },
};

export default nextConfig;
