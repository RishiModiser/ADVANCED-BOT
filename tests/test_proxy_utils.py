import unittest

from proxy_utils import parse_proxy


class ParseProxyTests(unittest.TestCase):
    def test_parses_at_format(self):
        self.assertEqual(
            parse_proxy("alice:secret@example.com:8080"),
            {
                "server": "http://example.com:8080",
                "username": "alice",
                "password": "secret",
            },
        )

    def test_parses_colon_format(self):
        self.assertEqual(
            parse_proxy("example.com:8080:alice:secret")["username"],
            "alice",
        )

    def test_rejects_empty_or_malformed_input(self):
        for value in ("", "example.com:8080", "alice@example.com:8080"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_proxy(value)


if __name__ == "__main__":
    unittest.main()
