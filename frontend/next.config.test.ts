import { afterEach, describe, expect, it } from "vitest";

import nextConfig from "./next.config";

const originalApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

afterEach(() => {
  if (originalApiBaseUrl === undefined) {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
  } else {
    process.env.NEXT_PUBLIC_API_BASE_URL = originalApiBaseUrl;
  }
  delete process.env.API_PROXY_TARGET;
});

describe("next rewrites", () => {
  it("proxies api requests to the local backend when no public api base url is configured", async () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;

    const rewrites = await nextConfig.rewrites?.();

    expect(rewrites).toEqual([
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ]);
  });

  it("does not proxy api requests when a public api base url is configured", async () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "https://backend.example.com";

    const rewrites = await nextConfig.rewrites?.();

    expect(rewrites).toEqual([]);
  });
});
