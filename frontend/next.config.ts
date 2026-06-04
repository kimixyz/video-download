import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname, ".."),
  },
  experimental: {
    externalDir: true,
  },
  async rewrites() {
    // When a public API base URL is configured, the browser calls that backend directly.
    // Otherwise, keep /api/* usable for local dev and local production smoke tests.
    if (process.env.NEXT_PUBLIC_API_BASE_URL) {
      return [];
    }

    const apiProxyTarget = process.env.API_PROXY_TARGET || "http://localhost:8000";

    return [
      {
        source: "/api/:path*",
        destination: `${apiProxyTarget.replace(/\/$/, "")}/api/:path*`,
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
