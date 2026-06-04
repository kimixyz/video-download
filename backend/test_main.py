import asyncio
import json
import os
import unittest

from main import unhandled_exception_handler


class ErrorHandlingTest(unittest.TestCase):
    def test_unhandled_errors_hide_internal_details_by_default(self):
        os.environ.pop("DEBUG_ERRORS", None)

        response = asyncio.run(unhandled_exception_handler(None, RuntimeError("secret token")))
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(payload["error"]["code"], "internal_error")
        self.assertEqual(payload["error"]["message"], "服务器内部错误")
        self.assertNotIn("details", payload["error"])


if __name__ == "__main__":
    unittest.main()
