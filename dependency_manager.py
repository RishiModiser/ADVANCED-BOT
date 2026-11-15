"""Non-blocking system requirement detection and installation helpers."""

from __future__ import annotations

import importlib
import importlib.metadata
import os
import platform
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout

from app_runtime import SUPPORTED_BROWSERS, app_data_path, browser_installation_status, install_missing_browsers


REQUIRED_PACKAGES = ("PySide6", "playwright", "python-dateutil", "aiohttp", "cryptography")


@dataclass(frozen=True)
class RequirementStatus:
    name: str
    status: str
    detail: str = ""


def package_status() -> list[RequirementStatus]:
    result = []
    for requirement in REQUIRED_PACKAGES:
        module_name = {"python-dateutil": "dateutil"}.get(requirement, requirement)
        try:
            version = importlib.metadata.version(requirement)
            importlib.import_module(module_name)
            result.append(RequirementStatus(requirement, "Installed", version))
        except (ImportError, importlib.metadata.PackageNotFoundError):
            result.append(RequirementStatus(requirement, "Missing"))
    return result


def runtime_status() -> RequirementStatus:
    if getattr(sys, "frozen", False):
        return RequirementStatus("Python Runtime", "Bundled", sys.version.split()[0])
    return RequirementStatus("Python Runtime", "Available", sys.version.split()[0])


def vcredist_status() -> RequirementStatus:
    if platform.system() != "Windows":
        return RequirementStatus("Microsoft Visual C++ Runtime", "Not applicable")
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    installed = any((system_root / "System32" / name).exists() for name in ("vcruntime140.dll", "msvcp140.dll"))
    return RequirementStatus("Microsoft Visual C++ Runtime", "Installed" if installed else "Missing")


class _InstallWorker(QObject):
    finished = Signal(bool, str)
    progress = Signal(int)

    def __init__(self, action: Callable[[], tuple[bool, str]]) -> None:
        super().__init__()
        self.action = action

    @Slot()
    def run(self) -> None:
        try:
            self.progress.emit(10)
            success, message = self.action()
            self.progress.emit(100 if success else 0)
            self.finished.emit(success, message)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            self.finished.emit(False, str(exc))


class SystemRequirementsPanel(QGroupBox):
    """Compact panel that fits the existing Control page without redesigning it."""

    def __init__(self, parent=None) -> None:
        super().__init__("System Requirements & Downloads", parent)
        self._threads: list[QThread] = []
        self._workers: list[_InstallWorker] = []
        self._rows: dict[str, tuple[QLabel, QPushButton]] = {}
        layout = QVBoxLayout(self)
        self._add_row(layout, "Chromium Browser", self._browser_action("chromium"))
        self._add_row(layout, "Firefox Browser", self._browser_action("firefox"))
        runtime = runtime_status()
        self._add_row(layout, "Python Runtime", None, runtime)
        self._add_row(layout, "Required Libraries", self._install_libraries,
                      self._library_summary())
        for package in package_status():
            self._add_row(
                layout,
                f"Library: {package.name}",
                lambda name=package.name: self._install_package(name),
                package,
            )
        self._add_row(layout, "Microsoft Visual C++ Runtime", self._vc_action(),
                      vcredist_status())
        self.refresh()

    def _add_row(self, layout: QVBoxLayout, name: str, action: Optional[Callable[[], tuple[bool, str]]],
                 status: Optional[RequirementStatus] = None) -> None:
        row = QHBoxLayout()
        label = QLabel(name)
        state = QLabel()
        button = QPushButton("View Details" if action is None else "Install / Repair")
        button.setEnabled(action is not None)
        if action is not None:
            button.clicked.connect(lambda: self._start_action(action, state, button))
        row.addWidget(label)
        row.addStretch()
        row.addWidget(state)
        row.addWidget(button)
        layout.addLayout(row)
        self._rows[name] = (state, button)
        if status:
            state.setText(self._format(status))

    @staticmethod
    def _format(status: RequirementStatus) -> str:
        return f"{status.status}{' (' + status.detail + ')' if status.detail else ''}"

    def _library_summary(self) -> RequirementStatus:
        missing = [item.name for item in package_status() if item.status == "Missing"]
        return RequirementStatus("Required Libraries", f"{len(missing)} Missing" if missing else "Installed")

    def _browser_action(self, browser: str) -> Callable[[], tuple[bool, str]]:
        return lambda: self._install_browser(browser)

    def _install_browser(self, browser: str) -> tuple[bool, str]:
        result = install_missing_browsers((browser,))
        ok = result.returncode == 0 and browser_installation_status().get(browser, False)
        return ok, f"{browser.title()} {'ready' if ok else 'installation failed'}"

    def _install_libraries(self) -> tuple[bool, str]:
        missing = [item.name for item in package_status() if item.status == "Missing"]
        if not missing:
            return True, "All required libraries are installed."
        flags = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}
        result = subprocess.run([sys.executable, "-m", "pip", "install", *missing],
                                capture_output=True, text=True, check=False, **flags)
        return result.returncode == 0, (result.stderr or result.stdout or "Library installation finished.").strip()

    def _install_package(self, package: str) -> tuple[bool, str]:
        flags = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package],
            capture_output=True,
            text=True,
            check=False,
            **flags,
        )
        try:
            version = importlib.metadata.version(package)
            importlib.import_module({"python-dateutil": "dateutil"}.get(package, package))
            return result.returncode == 0, f"{package} {version} is available."
        except (ImportError, importlib.metadata.PackageNotFoundError):
            return False, (result.stderr or f"{package} could not be verified.").strip()

    def _vc_action(self) -> Callable[[], tuple[bool, str]]:
        return self._install_vcredist

    def _install_vcredist(self) -> tuple[bool, str]:
        if platform.system() != "Windows":
            return True, "Not applicable on this operating system."
        if vcredist_status().status == "Installed":
            return True, "Microsoft Visual C++ Runtime is already installed."
        target = app_data_path("downloads") / "vc_redist.x64.exe"
        target.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve("https://aka.ms/vs/17/release/vc_redist.x64.exe", target)
        if target.stat().st_size < 1_000_000 or target.read_bytes()[:2] != b"MZ":
            target.unlink(missing_ok=True)
            return False, "Downloaded Visual C++ installer failed verification."
        result = subprocess.run(
            [str(target), "/install", "/quiet", "/norestart"],
            capture_output=True,
            text=True,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return (
            result.returncode in (0, 1638, 3010) and vcredist_status().status == "Installed",
            "Microsoft Visual C++ Runtime installation completed."
            if result.returncode in (0, 1638, 3010)
            else (result.stderr or "Microsoft Visual C++ Runtime installation failed."),
        )

    def _start_action(self, action: Callable[[], tuple[bool, str]], state: QLabel, button: QPushButton) -> None:
        if any(thread.isRunning() for thread in self._threads):
            return
        button.setEnabled(False)
        thread = QThread(self)
        worker = _InstallWorker(action)
        worker.moveToThread(thread)
        worker.progress.connect(lambda value: state.setText(f"Working ({value}%)"))
        worker.finished.connect(lambda ok, message: self._action_finished(ok, message, state, button, thread, worker))
        thread.started.connect(worker.run)
        self._threads.append(thread)
        self._workers.append(worker)
        thread.start()

    def _action_finished(self, ok: bool, message: str, state: QLabel, button: QPushButton,
                         thread: QThread, worker: _InstallWorker) -> None:
        state.setText("Installed" if ok else f"Failed: {message[:80]}")
        button.setEnabled(True)
        thread.quit()
        thread.deleteLater()
        if thread in self._threads:
            self._threads.remove(thread)
        if worker in self._workers:
            self._workers.remove(worker)
        self.refresh()

    def refresh(self) -> None:
        browsers = browser_installation_status()
        for browser in SUPPORTED_BROWSERS:
            state, button = self._rows[browser.title() + " Browser"]
            state.setText("Installed" if browsers.get(browser, False) else "Missing")
            button.setText("Repair" if browsers.get(browser, False) else "Install")
        state, _ = self._rows["Required Libraries"]
        state.setText(self._format(self._library_summary()))
