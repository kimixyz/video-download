import unittest

from parser import _normalize_bilibili_url


class BilibiliNormalizeTest(unittest.TestCase):
    def test_mobile_host_rewritten_to_www(self):
        # m.bilibili.com falls through to yt-dlp's generic extractor (→ HTTP 412);
        # it must be rewritten to the www host the BiliBili extractor matches.
        url = "https://m.bilibili.com/video/BV1dQEF6GEtm?p=1&share_source=copy"
        self.assertEqual(
            _normalize_bilibili_url(url),
            "https://www.bilibili.com/video/BV1dQEF6GEtm",
        )

    def test_av_id_preserved(self):
        url = "https://www.bilibili.com/video/av170001"
        self.assertEqual(
            _normalize_bilibili_url(url),
            "https://www.bilibili.com/video/av170001",
        )

    def test_url_without_id_returned_unchanged(self):
        url = "https://www.bilibili.com/some/other/page"
        self.assertEqual(_normalize_bilibili_url(url), url)


if __name__ == "__main__":
    unittest.main()
