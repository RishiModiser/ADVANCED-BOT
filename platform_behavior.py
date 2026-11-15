"""Playwright device profiles for the Traffic Behaviour Platform.

The bot UI selects one profile for a task; this module owns the device details so
the desktop application does not grow device-specific dashboard layouts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class DeviceProfile:
    key: str
    label: str
    viewport: Dict[str, int]
    user_agent: str
    is_mobile: bool
    has_touch: bool
    device_scale_factor: float
    orientations: tuple[str, ...]

    def context_options(self, orientation: str = "portrait") -> Dict[str, object]:
        if orientation not in self.orientations:
            raise ValueError(f"Unsupported {self.label} orientation: {orientation}")
        viewport = dict(self.viewport)
        if orientation == "landscape":
            viewport["width"], viewport["height"] = viewport["height"], viewport["width"]
        return {
            "viewport": viewport,
            "user_agent": self.user_agent,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch,
            "device_scale_factor": self.device_scale_factor,
        }


DEVICE_PROFILES = {
    "desktop": DeviceProfile(
        "desktop",
        "Desktop Behaviour",
        {"width": 1366, "height": 768},
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        False,
        False,
        1.0,
        ("landscape",),
    ),
    "android": DeviceProfile(
        "android",
        "Android Behaviour",
        {"width": 412, "height": 915},
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        True,
        True,
        2.625,
        ("portrait", "landscape"),
    ),
    "tablet": DeviceProfile(
        "tablet",
        "Tablet Behaviour",
        {"width": 820, "height": 1180},
        "Mozilla/5.0 (Linux; Android 13; SM-X700) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        True,
        True,
        2.0,
        ("portrait", "landscape"),
    ),
}


def get_device_profile(mode: Optional[str]) -> DeviceProfile:
    """Return a validated profile, accepting legacy Windows/Desktop names."""
    key = (mode or "desktop").strip().lower()
    aliases = {"windows": "desktop", "desktop behaviour": "desktop",
               "android behaviour": "android", "tablet behaviour": "tablet"}
    key = aliases.get(key, key)
    try:
        return DEVICE_PROFILES[key]
    except KeyError as exc:
        raise ValueError(f"Unknown device behaviour mode: {mode}") from exc


def profile_choices() -> tuple[tuple[str, str], ...]:
    return tuple((profile.key, profile.label) for profile in DEVICE_PROFILES.values())
