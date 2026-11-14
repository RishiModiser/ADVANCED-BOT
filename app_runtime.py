"""Runtime paths and browser provisioning helpers for HumanexBot."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable

APP_NAME = "HumanexBot"
SUPPORTED_BROWSERS = ("chromium", "firefox")


def resource_path(*parts: str) -> Path:
    """Resolve read-only resources from source or a PyInstaller bundle."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return root.joinpath(*parts)


def app_data_path(*parts: str) -> Path:
    """Return a writable per-user application-data path."""
    if platform.system() == "Windows":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif platform.system() == "Darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    root = root / APP_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root.joinpath(*parts)


def browser_root() -> Path:
    """Return the bundled or user-managed Playwright browser directory."""
    bundled = resource_path("playwright-browsers")
    if bundled.exists():
        return bundled
    return app_data_path("playwright-browsers")


def configure_browser_environment() -> Path:
    """Point Playwright at the application-managed browser directory."""
    root = browser_root()
    root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(root))
    return root


def browser_installation_status() -> Dict[str, bool]:
    """Check executable availability for all supported Playwright browsers."""
    configure_browser_environment()
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return {name: False for name in SUPPORTED_BROWSERS}

    playwright = None
    try:
        import asyncio

        async def inspect() -> Dict[str, bool]:
            instance = await async_playwright().start()
            try:
                return {
                    name: bool(Path(getattr(instance, name).executable_path).exists())
                    for name in SUPPORTED_BROWSERS
                }
            finally:
                await instance.stop()

        return asyncio.run(inspect())
    except Exception:
        return {name: False for name in SUPPORTED_BROWSERS}


def install_missing_browsers(
    browsers: Iterable[str] = SUPPORTED_BROWSERS,
) -> subprocess.CompletedProcess[str]:
    """Install missing browsers through the bundled or source Playwright CLI."""
    configure_browser_environment()
    requested = [name for name in browsers if name in SUPPORTED_BROWSERS]
    if getattr(sys, "frozen", False):
        from playwright._impl._driver import compute_driver_executable

        command = [*compute_driver_executable(), "install", *requested]
    else:
        command = [sys.executable, "-m", "playwright", "install", *requested]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def layout_mode(width: int, height: int) -> str:
    """Select the default responsive UI mode from available screen dimensions."""
    shortest = min(width, height)
    if shortest < 600 or width < 800:
        return "mobile"
    if shortest < 900 or width < 1200:
        return "tablet"
    return "desktop"


class SingleInstance:
    """Windows-friendly lock file used to prevent duplicate GUI instances."""

    def __init__(self) -> None:
        self.path = app_data_path("instance.lock")
        self._handle = None
        self._owns_lock = False

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                self._handle = self.path.open("x", encoding="ascii")
                self._handle.write(str(os.getpid()))
                self._handle.flush()
                self._owns_lock = True
                return True
            except FileExistsError:
                if not self._remove_stale_lock():
                    return False
        return False

    def _remove_stale_lock(self) -> bool:
        try:
            pid = int(self.path.read_text(encoding="ascii").strip())
        except (FileNotFoundError, OSError, ValueError):
            pid = None
        if pid and _process_is_running(pid):
            return False
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            return False
        return True

    def release(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None
        if self._owns_lock:
            self._owns_lock = False
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass


def _process_is_running(pid: int) -> bool:
    if pid <= 0 or pid == os.getpid():
        return pid == os.getpid()
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True
