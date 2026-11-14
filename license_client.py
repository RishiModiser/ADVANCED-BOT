"""License API client for the Humanex Bot activation gate."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class LicenseResult:
    valid: bool
    message: str
    expires_at: Optional[str] = None


class LicenseConfigurationError(RuntimeError):
    """Raised when the activation API has not been configured."""


class LicenseClient:
    """Small, dependency-free client for the existing PHP license API."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        config_path: Optional[Path] = None,
        timeout: int = 15,
    ) -> None:
        configured_url = api_url or os.environ.get("HUMANEX_LICENSE_API_URL", "")
        if not configured_url and config_path:
            configured_url = self._load_configured_url(config_path)
        self.api_url = configured_url.strip()
        self.timeout = timeout
        if not self.api_url:
            raise LicenseConfigurationError(
                "License API is not configured. Set HUMANEX_LICENSE_API_URL "
                "to the PHP license verification endpoint."
            )

    @staticmethod
    def _load_configured_url(config_path: Path) -> str:
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return ""
        except (OSError, json.JSONDecodeError) as exc:
            raise LicenseConfigurationError(
                f"License configuration could not be read: {exc}."
            ) from exc
        if not isinstance(data, dict) or not isinstance(data.get("api_url"), str):
            raise LicenseConfigurationError(
                f"License configuration must define a string api_url: {config_path}"
            )
        return data["api_url"]

    def verify(self, license_key: str) -> LicenseResult:
        key = license_key.strip()
        if not key:
            return LicenseResult(False, "Enter a license key.")

        payload = json.dumps({"license_key": key, "product": "HUMANEX BOT v5.0"}).encode("utf-8")
        request = urllib.request.Request(
            self.api_url,
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return LicenseResult(False, f"License API returned HTTP {exc.code}.")
        except (urllib.error.URLError, TimeoutError) as exc:
            return LicenseResult(False, f"Unable to contact the license API: {exc.reason if hasattr(exc, 'reason') else exc}.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return LicenseResult(False, "License API returned invalid JSON.")
        except OSError as exc:
            return LicenseResult(False, f"License API connection failed: {exc}.")

        if not isinstance(body, dict):
            return LicenseResult(False, "License API returned an invalid response.")

        valid = body.get("valid", body.get("success", False)) is True
        status = str(body.get("status", "")).strip().lower()
        if status in {"invalid", "blocked", "expired", "revoked", "denied"}:
            valid = False
        message = str(body.get("message") or ("License activated." if valid else "License is invalid, expired, revoked, or blocked."))
        expires_at = body.get("expires_at") or body.get("expires")
        return LicenseResult(valid, message, str(expires_at) if expires_at else None)
