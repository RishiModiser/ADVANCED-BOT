"""Modern Humanex Bot activation dialog."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from license_client import LicenseClient, LicenseConfigurationError, LicenseResult, SecureActivationStore


class _VerificationWorker(QObject):
    finished = Signal(object)

    def __init__(self, client: LicenseClient, key: str) -> None:
        super().__init__()
        self.client = client
        self.key = key

    @Slot()
    def run(self) -> None:
        try:
            result = self.client.verify(self.key)
        except Exception:
            result = LicenseResult("error", False, "License verification failed. Please retry.")
        self.finished.emit(result)


class ActivationDialog(QDialog):
    """Block startup until the existing PHP license service authorizes a key."""

    def __init__(
        self,
        parent=None,
        logo_path: Optional[Path] = None,
        icon_path: Optional[Path] = None,
        license_config_path: Optional[Path] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("HumanexBot v5.0 - Activation Required")
        self.setWindowIcon(QIcon(str(icon_path))) if icon_path and icon_path.exists() else None
        self.setModal(True)
        self.setFixedSize(460, 430)
        self._thread: Optional[QThread] = None
        self._worker: Optional[_VerificationWorker] = None
        self._store = SecureActivationStore()
        self._client: Optional[LicenseClient] = None
        self._build_ui(logo_path)
        try:
            self._client = LicenseClient(config_path=license_config_path)
        except LicenseConfigurationError as exc:
            self._set_error(str(exc))
            self._set_busy(False)
            return
        saved = self._client.saved_activation(self._store)
        if saved:
            self._set_busy(True, "Verifying saved activation...")
            self._start_verification(str(saved["license_key"]))

    def _build_ui(self, logo_path: Optional[Path]) -> None:
        self.setStyleSheet(
            """
            QDialog { background: #0b110d; color: #f2fff4; }
            QLabel#eyebrow { color: #8ca593; font-size: 11px; letter-spacing: 1px; }
            QLabel#title { color: #effff1; font-size: 24px; font-weight: 700; }
            QLabel#status { color: #a7b8aa; font-size: 12px; }
            QLineEdit {
                background: #121b15; color: #f2fff4; border: 1px solid #395542;
                border-radius: 10px; padding: 13px; font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #35d86a; }
            QPushButton {
                background: #25c85b; color: #07110a; border: 0; border-radius: 10px;
                padding: 12px 18px; font-weight: 700; min-width: 100px;
            }
            QPushButton:hover { background: #35df70; }
            QPushButton:pressed { background: #1aa64a; }
            QPushButton:disabled { background: #304337; color: #718276; }
            QPushButton#toggle { background: transparent; color: #69e88a; min-width: 65px; padding: 4px; }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(38, 28, 38, 30)
        layout.setSpacing(14)
        if logo_path and logo_path.exists():
            logo = QLabel()
            logo.setPixmap(QPixmap(str(logo_path)).scaled(84, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)
        eyebrow = QLabel("HUMANEXBOT  •  VERSION 5.0")
        eyebrow.setObjectName("eyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)
        layout.addWidget(eyebrow)
        title = QLabel("Activate your application")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.status_label = QLabel("Enter your license key to continue.")
        self.status_label.setObjectName("status")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        field_row = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your license key")
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.textChanged.connect(self._update_button)
        self.key_input.returnPressed.connect(self._activate)
        field_row.addWidget(self.key_input)
        self.toggle_button = QPushButton("Show")
        self.toggle_button.setObjectName("toggle")
        self.toggle_button.clicked.connect(self._toggle_key)
        field_row.addWidget(self.toggle_button)
        layout.addLayout(field_row)
        self.activate_button = QPushButton("Activate")
        self.activate_button.clicked.connect(self._activate)
        layout.addWidget(self.activate_button)
        layout.addStretch(1)
        self._update_button()

    def _toggle_key(self) -> None:
        visible = self.key_input.echoMode() == QLineEdit.Normal
        self.key_input.setEchoMode(QLineEdit.Password if visible else QLineEdit.Normal)
        self.toggle_button.setText("Show" if visible else "Hide")

    def _update_button(self) -> None:
        self.activate_button.setEnabled(bool(self.key_input.text().strip()) and self._thread is None)

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self.key_input.setEnabled(not busy)
        self.toggle_button.setEnabled(not busy)
        self.activate_button.setEnabled(
            not busy and self._client is not None and bool(self.key_input.text().strip())
        )
        if message:
            self._set_status(message, error=False)

    def _set_status(self, message: str, error: bool) -> None:
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #ff7d7d;" if error else "")

    def _set_error(self, message: str) -> None:
        self._set_status(message, error=True)

    def _activate(self) -> None:
        if self._client is None or self._thread is not None:
            return
        key = self.key_input.text().strip()
        if not key:
            self._set_error("Enter a license key.")
            return
        self._set_busy(True, "Connecting to license server...")
        self._start_verification(key)

    def _start_verification(self, key: str) -> None:
        if self._client is None:
            return
        self._thread = QThread(self)
        self._worker = _VerificationWorker(self._client, key)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._verification_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._verification_thread_finished)
        self._thread.start()

    @Slot(object)
    def _verification_finished(self, result: LicenseResult) -> None:
        if result.status == "valid":
            self._store.save({
                "license_key": self._worker.key if self._worker else "",
                "device_id": self._client.identity.device_id if self._client else "",
                "expires_at": result.expires_at,
            })
            self._set_status(result.message, error=False)
            self.accept()
        elif result.status == "invalid":
            self._store.clear()
            self._set_error(result.message)
            self._set_busy(False)
        else:
            self._set_error(result.message)
            self._set_busy(False)

    @Slot()
    def _verification_thread_finished(self) -> None:
        if self._thread:
            self._thread.deleteLater()
        self._thread = None
        self._worker = None
        if self.isVisible():
            self._update_button()
