import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // In local development, proxy to the uvicorn backend at :8000.
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: "http://localhost:8000/api/:path*",
        },
      ];
    }
    // In production (Vercel), route /api/* to the Python serverless function.
    // The function receives the original path so FastAPI routing works correctly.
    return [
      {
        source: "/api/:path*",
        destination: "/api/index",
      },
    unction receives the original path so FastAPI routing works correctly.
    return [
      {
        source: "/api/:path*",
        destination: "/api/index",
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
