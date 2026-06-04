import unittest

from parser import _normalize_douyin_play_url, _parse_douyin_from_html


class DouyinParserTest(unittest.TestCase):
    def test_normalize_douyin_play_url_rewrites_watermark_variants(self):
        url = "https://aweme.snssdk.com/aweme/v1/playwm/?video_id=123&ratio=720p&watermark=1&logo=1"

        normalized = _normalize_douyin_play_url(url, ratio="1080p")

        self.assertIn("/play/", normalized)
        self.assertNotIn("/playwm/", normalized)
        self.assertNotIn("watermark=1", normalized)
        self.assertNotIn("logo=1", normalized)
        self.assertIn("ratio=1080p", normalized)

    def test_parse_douyin_from_html_builds_no_watermark_formats(self):
        html = """
        <html><body>
        <script>
        window._ROUTER_DATA = {
          "loaderData": {
            "page": {
              "videoInfoRes": {
                "item_list": [
                  {
                    "desc": "测试视频",
                    "author": {"nickname": "作者"},
                    "video": {
                      "play_addr": {
                        "url_list": [
                          "https://aweme.snssdk.com/aweme/v1/playwm/?video_id=123&watermark=1&ratio=720p"
                        ]
                      },
                      "cover": {"url_list": ["https://example.com/cover.jpg"]},
                      "duration": 12345
                    }
                  }
                ]
              }
            }
          }
        };
        </script>
        </body></html>
        """

        result = _parse_douyin_from_html(html)

        self.assertEqual(result.platform, "douyin")
        self.assertEqual(result.title, "测试视频")
        self.assertEqual(result.author, "作者")
        self.assertEqual(result.duration, 12)
        self.assertEqual(len(result.formats), 3)
        for fmt in result.formats:
            self.assertIn("/play/", fmt.url)
            self.assertNotIn("/playwm/", fmt.url)
            self.assertNotIn("watermark=1", fmt.url)


if __name__ == "__main__":
    unittest.main()
