import unittest

from video_rules import detect_platform, extract_share_url, referer_for_url


class VideoRulesTest(unittest.TestCase):
    def test_extract_share_url_removes_share_text_and_trailing_punctuation(self):
        text = "复制这条消息 https://v.douyin.com/example/，打开看看"

        self.assertEqual(extract_share_url(text), "https://v.douyin.com/example/")

    def test_detect_platform_supports_shared_rules(self):
        self.assertEqual(detect_platform("https://www.bilibili.com/video/BV123"), "bilibili")

    def test_referer_falls_back_to_url_for_unknown_platforms(self):
        url = "https://example.com/video"

        self.assertEqual(referer_for_url(url), url)


if __name__ == "__main__":
    unittest.main()
