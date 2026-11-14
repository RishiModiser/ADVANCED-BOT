import unittest

from script_utils import validate_rpa_script_data


class ValidateRpaScriptTests(unittest.TestCase):
    def test_accepts_single_step_and_step_lists(self):
        validate_rpa_script_data({"type": "navigate", "url": "https://example.com"})
        validate_rpa_script_data([{"type": "wait", "duration": 1000}])
        validate_rpa_script_data({"steps": [{"type": "closePage"}]})

    def test_rejects_invalid_shapes(self):
        invalid_values = (
            None,
            "not a script",
            {"steps": {}},
            {"steps": [{"url": "https://example.com"}]},
            {"steps": ["navigate"]},
        )
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_rpa_script_data(value)


if __name__ == "__main__":
    unittest.main()
