import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from license_client import (
    DeviceIdentity,
    LicenseClient,
    LicenseConfigurationError,
    SecureActivationStore,
)


class _Response:
    def __init__(self, body):
        self.body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


class LicenseClientTests(unittest.TestCase):
    def test_uses_production_endpoint_and_form_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            identity = DeviceIdentity(Path(directory))
            client = LicenseClient(identity=identity)
            with patch("license_client.urllib.request.urlopen", return_value=_Response({"status": "valid"})) as opened:
                result = client.verify("  ABC-123  ")

        self.assertTrue(result.valid)
        request = opened.call_args.args[0]
        fields = request.data.decode("utf-8")
        self.assertIn("license_key=ABC-123", fields)
        self.assertIn("device_id=", fields)
        self.assertIn("hardware_id=", fields)
        self.assertIn("user_agent=", fields)
        self.assertTrue(client.api_url.startswith("https://"))

    def test_preserves_invalid_and_error_statuses(self):
        with patch("license_client.urllib.request.urlopen", return_value=_Response({"status": "invalid", "message": "Expired"})):
            invalid = LicenseClient().verify("KEY")
        with patch("license_client.urllib.request.urlopen", return_value=_Response({"status": "error", "message": "Unavailable"})):
            error = LicenseClient().verify("KEY")

        self.assertEqual((invalid.status, invalid.message), ("invalid", "Expired"))
        self.assertEqual((error.status, error.message), ("error", "Unavailable"))

    def test_rejects_non_https_endpoint(self):
        with self.assertRaises(LicenseConfigurationError):
            LicenseClient(api_url="http://localhost/check_license.php")

    def test_activation_store_round_trip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.dat"
            store = SecureActivationStore(path)
            store.save({"license_key": "KEY", "device_id": "DEVICE"})
            self.assertEqual(store.load()["license_key"], "KEY")
            tampered = bytearray(path.read_bytes())
            tampered[-3] = ord("A") if tampered[-3] != ord("A") else ord("B")
            path.write_bytes(tampered)
            self.assertIsNone(store.load())


if __name__ == "__main__":
    unittest.main()
