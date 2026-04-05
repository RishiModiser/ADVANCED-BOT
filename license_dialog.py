#!/usr/bin/env python3
"""
License Key Entry Dialog
Shown at bot startup. Requires a valid license key to proceed.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QApplication, QMessageBox,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

from license_database import validate_key


_STYLE = """
QDialog {
    background-color: #1a1a2e;
}
QLabel#title {
    color: #e94560;
    font-size: 22px;
    font-weight: bold;
}
QLabel#subtitle {
    color: #a0a0c0;
    font-size: 11px;
}
QLabel#info {
    color: #c0c0e0;
    font-size: 12px;
}
QLineEdit#key_input {
    background-color: #16213e;
    color: #e0e0ff;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 15px;
    letter-spacing: 2px;
    font-family: Consolas, monospace;
}
QLineEdit#key_input:focus {
    border: 2px solid #e94560;
}
QPushButton#activate_btn {
    background-color: #e94560;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#activate_btn:hover {
    background-color: #c73652;
}
QPushButton#activate_btn:pressed {
    background-color: #a02840;
}
QPushButton#cancel_btn {
    background-color: transparent;
    color: #606080;
    border: 1px solid #404060;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
}
QPushButton#cancel_btn:hover {
    color: #a0a0c0;
    border-color: #606080;
}
QFrame#separator {
    background-color: #0f3460;
}
QLabel#error_label {
    color: #e94560;
    font-size: 11px;
}
QLabel#success_label {
    color: #4ecca3;
    font-size: 11px;
}
"""


class LicenseDialog(QDialog):
    """Full-screen modal dialog that asks the user for a license key."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Activate HUMANEX")
        self.setFixedSize(520, 360)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setStyleSheet(_STYLE)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 36, 48, 36)
        root.setSpacing(0)

        # ── Brand header ──────────────────────────────────────────────
        title = QLabel("HUMANEX v5")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("License Activation Required")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        root.addWidget(title)
        root.addSpacing(4)
        root.addWidget(subtitle)
        root.addSpacing(24)

        # ── Separator ─────────────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFixedHeight(1)
        root.addWidget(sep)
        root.addSpacing(20)

        # ── Info text ─────────────────────────────────────────────────
        info = QLabel("Enter your license key to continue:")
        info.setObjectName("info")
        root.addWidget(info)
        root.addSpacing(8)

        # ── Key input ─────────────────────────────────────────────────
        self.key_input = QLineEdit()
        self.key_input.setObjectName("key_input")
        self.key_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX-XXXXX")
        self.key_input.setMaxLength(29)
        self.key_input.textChanged.connect(self._auto_format)
        root.addWidget(self.key_input)
        root.addSpacing(6)

        # ── Status label ──────────────────────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setObjectName("error_label")
        root.addWidget(self.status_label)
        root.addSpacing(20)

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.cancel_btn = QPushButton("Exit")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)

        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setObjectName("activate_btn")
        self.activate_btn.setDefault(True)
        self.activate_btn.clicked.connect(self._on_activate)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.activate_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _auto_format(self, text: str):
        """Auto-insert dashes as the user types."""
        # Strip everything except alphanumerics
        clean = "".join(c for c in text.upper() if c.isalnum())
        # Insert dashes every 5 chars
        groups = [clean[i : i + 5] for i in range(0, len(clean), 5)][:5]
        formatted = "-".join(groups)

        # Block signal to avoid recursion
        self.key_input.blockSignals(True)
        self.key_input.setText(formatted)
        # Move cursor to end
        self.key_input.setCursorPosition(len(formatted))
        self.key_input.blockSignals(False)

        self.status_label.setText("")

    def _on_activate(self):
        key = self.key_input.text().strip().upper()
        if not key:
            self._show_error("Please enter a license key.")
            return
        if len(key) != 29:
            self._show_error("Key must be in format XXXXX-XXXXX-XXXXX-XXXXX-XXXXX.")
            return

        self.activate_btn.setEnabled(False)
        self.activate_btn.setText("Validating…")
        QApplication.processEvents()

        valid, message = validate_key(key)

        self.activate_btn.setEnabled(True)
        self.activate_btn.setText("Activate")

        if valid:
            self.status_label.setObjectName("success_label")
            self.status_label.setStyleSheet("color: #4ecca3; font-size: 11px;")
            self.status_label.setText(f"✔  {message}")
            QApplication.processEvents()
            import time
            time.sleep(0.6)
            self.accept()
        else:
            self._show_error(f"✘  {message}")

    def _show_error(self, msg: str):
        self.status_label.setStyleSheet("color: #e94560; font-size: 11px;")
        self.status_label.setText(msg)


def run_license_check() -> bool:
    """
    Show the license dialog and return True if the user successfully activated.
    Must be called after QApplication has been created.
    """
    dlg = LicenseDialog()
    return dlg.exec() == QDialog.Accepted
