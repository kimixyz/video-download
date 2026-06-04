import { describe, expect, it } from "vitest";

import { parseParseResult } from "./parseResult";

describe("parseParseResult", () => {
  it("accepts a valid parse response", () => {
    const result = parseParseResult({
      title: "测试视频",
      thumbnail: "https://example.com/a.jpg",
      author: "作者",
      platform: "douyin",
      duration: 12,
      formats: [
        {
          format_id: "1080",
          quality: "1080P",
          ext: "mp4",
          url: "https://example.com/video.mp4",
          filesize: 1024,
        },
      ],
    });

    expect(result.title).toBe("测试视频");
    expect(result.formats[0]?.url).toBe("https://example.com/video.mp4");
  });

  it("rejects responses without a formats array", () => {
    expect(() =>
      parseParseResult({
        title: "缺少格式",
        platform: "douyin",
      }),
    ).toThrow("解析服务返回的数据格式异常");
  });

  it("rejects formats without a downloadable url", () => {
    expect(() =>
      parseParseResult({
        title: "坏格式",
        platform: "douyin",
        formats: [{ format_id: "bad", quality: "1080P", ext: "mp4" }],
      }),
    ).toThrow("解析服务返回的数据格式异常");
  });
});
