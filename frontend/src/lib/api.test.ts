import { describe, expect, it } from "vitest";

import { buildDownloadUrl } from "./api";

describe("buildDownloadUrl", () => {
  it("adds delogo post-process parameters when enabled", () => {
    const url = buildDownloadUrl("https://example.com/video.mp4", "video.mp4", {
      enabled: true,
      x: 20,
      y: 30,
      width: 600,
      height: 110,
    });
    const parsed = new URL(url, "https://local.test");

    expect(parsed.pathname).toBe("/api/download");
    expect(parsed.searchParams.get("postprocess")).toBe("delogo");
    expect(parsed.searchParams.get("wm_x")).toBe("20");
    expect(parsed.searchParams.get("wm_y")).toBe("30");
    expect(parsed.searchParams.get("wm_w")).toBe("600");
    expect(parsed.searchParams.get("wm_h")).toBe("110");
  });
});
