import asyncio
import json
import os
import unittest

from main import unhandled_exception_handler
from main import _validated_delogo_filter


class ErrorHandlingTest(unittest.TestCase):
    def test_unhandled_errors_hide_internal_details_by_default(self):
        os.environ.pop("DEBUG_ERRORS", None)

        response = asyncio.run(unhandled_exception_handler(None, RuntimeError("secret token")))
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(payload["error"]["code"], "internal_error")
        self.assertEqual(payload["error"]["message"], "服务器内部错误")
        self.assertNotIn("details", payload["error"])


class DelogoFilterTest(unittest.TestCase):
    def test_validated_delogo_filter_builds_ffmpeg_expression(self):
        self.assertEqual(
            _validated_delogo_filter(20, 30, 600, 110),
            "delogo=x=20:y=30:w=600:h=110:show=0",
        )

    def test_validated_delogo_filter_rejects_tiny_box(self):
        with self.assertRaises(Exception):
            _validated_delogo_filter(0, 0, 7, 100)


if __name__ == "__main__":
    unittest.main()
