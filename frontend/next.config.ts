import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV === "development") {
      // Local dev: proxy to uvicorn at :8000
      return [
        {
          source: "/api/:path*",
          destination: "http://localhost:8000/api/:path*",
        },
      ];
    }
    // Production (Vercel): rewrite /api/* to the Python serverless function
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
