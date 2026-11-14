import unittest

from app_runtime import SUPPORTED_BROWSERS, layout_mode


class RuntimeTests(unittest.TestCase):
    def test_supported_browsers_exclude_webkit(self):
        self.assertEqual(SUPPORTED_BROWSERS, ("chromium", "firefox"))

    def test_layout_mode_breakpoints(self):
        self.assertEqual(layout_mode(1920, 1080), "desktop")
        self.assertEqual(layout_mode(1024, 768), "tablet")
        self.assertEqual(layout_mode(390, 844), "mobile")


if __name__ == "__main__":
    unittest.main()
