import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from license_client import (
    DeviceIdentity,
    LicenseClient,
    PRODUCTION_API_URL,
    SecureActivationStore,
)


class _Response:
    def __init__(self, value):
        self.value = json.dumps(value).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.value


class LicenseClientTests(unittest.TestCase):
    def test_defaults_to_production_https_endpoint(self):
        client = LicenseClient(identity=DeviceIdentity(Path(tempfile.mkdtemp())))
        self.assertEqual(client.api_url, PRODUCTION_API_URL)

    @patch("license_client.urllib.request.urlopen")
    def test_sends_php_form_fields_and_accepts_valid_status(self, urlopen):
        urlopen.return_value = _Response({"status": "valid", "message": "ok", "expires_at": "2030-01-01"})
        with tempfile.TemporaryDirectory() as directory:
            client = LicenseClient(identity=DeviceIdentity(Path(directory)))
            result = client.verify("  ABC-123  ")
        self.assertTrue(result.valid)
        request = urlopen.call_args.args[0]
        self.assertIn(b"license_key=ABC-123", request.data)
        self.assertIn(b"device_id=", request.data)
        self.assertIn(b"hardware_id=", request.data)
        self.assertEqual(request.headers["Content-type"], "application/x-www-form-urlencoded")

    @patch("license_client.urllib.request.urlopen")
    def test_invalid_and_error_statuses_remain_distinct(self, urlopen):
        with tempfile.TemporaryDirectory() as directory:
            client = LicenseClient(identity=DeviceIdentity(Path(directory)))
            urlopen.return_value = _Response({"status": "invalid", "message": "Device limit exceeded."})
            invalid = client.verify("ABC")
            urlopen.return_value = _Response({"status": "error", "message": "Try again later."})
            error = client.verify("ABC")
        self.assertEqual(invalid.status, "invalid")
        self.assertFalse(invalid.valid)
        self.assertEqual(error.status, "error")
        self.assertFalse(error.valid)

    def test_activation_store_round_trip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.dat"
            store = SecureActivationStore(path)
            store.save({"license_key": "ABC", "device_id": "device"})
            self.assertEqual(store.load()["license_key"], "ABC")
            path.write_bytes(path.read_bytes()[:-1] + b"x")
            self.assertIsNone(store.load())


if __name__ == "__main__":
    unittest.main()
