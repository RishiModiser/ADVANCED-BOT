"""Mandatory Humanex Bot activation dialog."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout

from license_client import LicenseClient, LicenseConfigurationError


class ActivationDialog(QDialog):
    """Block application startup until the configured license API authorizes a key."""

    def __init__(
        self,
        parent=None,
        logo_path: Optional[Path] = None,
        license_config_path: Optional[Path] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("HUMANEX BOT v5.0 - Activation Required")
        self.setModal(True)
        self.setMinimumWidth(480)
        self._client: Optional[LicenseClient] = None
        self._result_message = ""
        self._build_ui(logo_path)
        try:
            self._client = LicenseClient(config_path=license_config_path)
        except LicenseConfigurationError as exc:
            self._result_message = str(exc)
            self._set_error(self._result_message)
            self.key_input.setEnabled(False)
            self.activate_button.setEnabled(False)

    def _build_ui(self, logo_path: Optional[Path]) -> None:
        self.setStyleSheet(
            """
            QDialog { background: #050805; color: #ffffff; }
            QLabel { color: #ffffff; }
            QLineEdit { background: #111611; color: #ffffff; border: 1px solid #35ff55; padding: 10px; }
            QPushButton { background: #19d63b; color: #000000; padding: 9px 18px; font-weight: bold; }
            QPushButton:disabled { background: #555555; color: #aaaaaa; }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        if logo_path and logo_path.exists():
            logo = QLabel()
            logo.setPixmap(QPixmap(str(logo_path)).scaledToWidth(220, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)
        heading = QLabel("HUMANEX BOT v5.0")
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet("font-size: 24px; font-weight: bold; color: #35ff55;")
        layout.addWidget(heading)
        self.status_label = QLabel("Activation is required before the dashboard can open.")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your license key")
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.returnPressed.connect(self._activate)
        layout.addWidget(self.key_input)
        self.activate_button = QDialogButtonBox(QDialogButtonBox.Ok)
        self.activate_button.button(QDialogButtonBox.Ok).setText("Activate")
        self.activate_button.accepted.connect(self._activate)
        layout.addWidget(self.activate_button)

    def _set_error(self, message: str) -> None:
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #ff6b6b;")

    def _activate(self) -> None:
        if self._client is None:
            return
        self.activate_button.setEnabled(False)
        result = self._client.verify(self.key_input.text())
        if result.valid:
            self._result_message = result.message
            self.accept()
            return
        self._result_message = result.message
        self._set_error(result.message)
        self.activate_button.setEnabled(True)
