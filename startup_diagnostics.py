"""Safe startup diagnostics; never records license keys or tokens."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


def configure_startup_logging(base_dir: Path) -> Path:
    log_path = base_dir / "logs" / "startup.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )
    logging.info("application_version=HUMANEX BOT v5.0")
    entry_point = Path(sys.executable).resolve() if getattr(sys, "frozen", False) else Path(__file__).resolve().parent / "humanexbot_v5.py"
    logging.info("active_entry_point=%s", entry_point)
    logging.info("build_mode=%s", "packaged" if getattr(sys, "frozen", False) else "source")
    logging.info("logo_asset_path=%s", os.environ.get("HUMANEX_LOGO_PATH", "resource_path/assets/humanex_bot_v5.svg"))
    return log_path


def log_startup_status(license_configured: bool, activation_initialized: bool) -> None:
    logging.info("license_initialization=%s", "configured" if license_configured else "missing")
    logging.info("activation_window_initialization=%s", "ready" if activation_initialized else "failed")
