"""Client and local state for the Humanex Bot PHP license service."""

from __future__ import annotations

import base64
import binascii
import ctypes
import hashlib
import hmac
import json
import os
import platform
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from app_runtime import app_data_path

PRODUCTION_API_URL = "https://adsenseloadingmethod.com/license_system/check_license.php"
PRODUCT_NAME = "HUMANEX BOT v5.0"
USER_AGENT = f"{PRODUCT_NAME} license client"


@dataclass(frozen=True)
class LicenseResult:
    status: str
    valid: bool
    message: str
    expires_at: Optional[str] = None


class LicenseConfigurationError(RuntimeError):
    """Raised when an unsafe or malformed activation endpoint is configured."""


class SecureActivationStore:
    """Persist activation data outside the installation directory.

    Windows uses DPAPI.  The non-Windows fallback is intentionally limited to
    development platforms and authenticates the payload with a machine-bound
    key; the production Windows build never uses it.
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or app_data_path("activation.dat")

    def save(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
        encoded = self._protect(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(encoded)

    def load(self) -> Optional[Dict[str, Any]]:
        try:
            payload = self._unprotect(self.path.read_bytes())
            value = json.loads(payload.decode("utf-8"))
        except (FileNotFoundError, OSError, ValueError, UnicodeDecodeError, binascii.Error):
            return None
        return value if isinstance(value, dict) else None

    def clear(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    @staticmethod
    def _protect(payload: bytes) -> bytes:
        if os.name == "nt":
            return b"DPAPI1" + _dpapi_protect(payload)
        key = _machine_secret()
        mac = hashlib.sha256(key + payload).digest()
        return b"LOCAL1" + base64.urlsafe_b64encode(mac + payload)

    @staticmethod
    def _unprotect(value: bytes) -> bytes:
        if value.startswith(b"DPAPI1") and os.name == "nt":
            return _dpapi_unprotect(value[6:])
        if value.startswith(b"LOCAL1"):
            decoded = base64.urlsafe_b64decode(value[6:])
            if len(decoded) < 32:
                raise ValueError("Activation data is truncated")
            mac, payload = decoded[:32], decoded[32:]
            expected_mac = hashlib.sha256(_machine_secret() + payload).digest()
            if not hmac.compare_digest(expected_mac, mac):
                raise ValueError("Activation data integrity check failed")
            return payload
        raise ValueError("Unknown activation data format")


class DeviceIdentity:
    """Create stable, privacy-preserving identifiers for the PHP API."""

    def __init__(self, directory: Optional[Path] = None) -> None:
        self.directory = directory or app_data_path()
        self.device_path = self.directory / "device_id"

    @property
    def device_id(self) -> str:
        try:
            value = self.device_path.read_text(encoding="ascii").strip()
            if value:
                return value
        except (FileNotFoundError, OSError, UnicodeDecodeError):
            pass
        value = hashlib.sha256(
            f"{PRODUCT_NAME}|{self.hardware_id}|{socket.gethostname()}".encode("utf-8")
        ).hexdigest()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.device_path.write_text(value, encoding="ascii")
        return value

    @property
    def hardware_id(self) -> str:
        raw = _windows_machine_guid() or _linux_machine_id() or str(uuid.getnode())
        return hashlib.sha256(f"{PRODUCT_NAME}|{raw}".encode("utf-8")).hexdigest()


class LicenseClient:
    """Form-encoded client for the existing PHP check_license.php endpoint."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        config_path: Optional[Path] = None,
        timeout: int = 15,
        identity: Optional[DeviceIdentity] = None,
    ) -> None:
        configured_url = api_url or os.environ.get("HUMANEX_LICENSE_API_URL") or ""
        if not configured_url and config_path:
            configured_url = self._load_configured_url(config_path)
        self.api_url = (configured_url or PRODUCTION_API_URL).strip()
        parsed = urllib.parse.urlparse(self.api_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise LicenseConfigurationError("The license service endpoint must use HTTPS.")
        self.timeout = max(1, int(timeout))
        self.identity = identity or DeviceIdentity()

    @staticmethod
    def _load_configured_url(config_path: Path) -> str:
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return ""
        except (OSError, json.JSONDecodeError) as exc:
            raise LicenseConfigurationError("License configuration could not be read.") from exc
        value = data.get("api_url") if isinstance(data, dict) else None
        if value is not None and not isinstance(value, str):
            raise LicenseConfigurationError("License configuration contains an invalid endpoint.")
        return value or ""

    def verify(self, license_key: str) -> LicenseResult:
        key = license_key.strip()
        if not key:
            return LicenseResult("invalid", False, "Enter a license key.")
        fields = {
            "license_key": key,
            "device_id": self.identity.device_id,
            "user_agent": USER_AGENT,
            "hardware_id": self.identity.hardware_id,
        }
        request = urllib.request.Request(
            self.api_url,
            data=urllib.parse.urlencode(fields).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=ssl.create_default_context()) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return LicenseResult("error", False, f"License server unavailable (HTTP {exc.code}).")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            reason = getattr(exc, "reason", None)
            return LicenseResult("error", False, f"Unable to contact the license server: {reason or exc}.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return LicenseResult("error", False, "License server returned an invalid response.")

        if not isinstance(body, dict):
            return LicenseResult("error", False, "License server returned an invalid response.")
        status = str(body.get("status", "")).strip().lower()
        if status not in {"valid", "invalid", "error"}:
            return LicenseResult("error", False, "License server returned an invalid status.")
        message = str(body.get("message") or _default_message(status))
        expires = body.get("expires_at") or body.get("expires")
        return LicenseResult(status, status == "valid", message, str(expires) if expires else None)

    def saved_activation(self, store: Optional[SecureActivationStore] = None) -> Optional[Dict[str, Any]]:
        activation = (store or SecureActivationStore()).load()
        if not activation or not isinstance(activation.get("license_key"), str):
            return None
        if activation.get("device_id") != self.identity.device_id:
            return None
        return activation


def _default_message(status: str) -> str:
    return {
        "valid": "License activated successfully.",
        "invalid": "Invalid license key.",
        "error": "License server error.",
    }[status]


def _machine_secret() -> bytes:
    return hashlib.sha256(
        f"{platform.node()}|{uuid.getnode()}|{PRODUCT_NAME}".encode("utf-8")
    ).digest()


def _windows_machine_guid() -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
            return str(winreg.QueryValueEx(key, "MachineGuid")[0])
    except (OSError, ImportError):
        return ""


def _linux_machine_id() -> str:
    for path in (Path("/etc/machine-id"), Path("/var/lib/dbus/machine-id")):
        try:
            value = path.read_text(encoding="ascii").strip()
        except (OSError, UnicodeDecodeError):
            continue
        if value:
            return value
    return ""


if os.name == "nt":
    class _Blob(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    def _dpapi_protect(payload: bytes) -> bytes:
        crypt = ctypes.windll.crypt32.CryptProtectData
        local_free = ctypes.windll.kernel32.LocalFree
        source = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        blob_in = _Blob(len(payload), source)
        blob_out = _Blob()
        if not crypt(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            raise OSError("Windows data protection failed")
        try:
            return ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            local_free(blob_out.pbData)

    def _dpapi_unprotect(payload: bytes) -> bytes:
        crypt = ctypes.windll.crypt32.CryptUnprotectData
        local_free = ctypes.windll.kernel32.LocalFree
        source = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        blob_in = _Blob(len(payload), source)
        blob_out = _Blob()
        if not crypt(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            raise OSError("Windows data protection failed")
        try:
            return ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            local_free(blob_out.pbData)
