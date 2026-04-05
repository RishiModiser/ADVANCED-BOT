#!/usr/bin/env python3
"""
Admin Panel – License Key Database Management
Run standalone:  python admin_panel.py

Features:
  • Admin login (password-protected)
  • Generate / add / edit / delete license keys
  • View & filter login activity (IP, OS, hostname, timestamp)
  • Dashboard statistics
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QGroupBox, QSpinBox, QCheckBox,
    QComboBox, QMessageBox, QFrame, QTextEdit, QSizePolicy,
    QAbstractItemView, QStatusBar,
)
from PySide6.QtCore import Qt, QTimer, QSortFilterProxyModel
from PySide6.QtGui import QFont, QColor, QBrush, QIcon

import license_database as db

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
_APP_STYLE = """
QMainWindow, QDialog {
    background-color: #f0f2f5;
}
QTabWidget::pane {
    border: 1px solid #d0d0d8;
    background: white;
    border-radius: 4px;
}
QTabBar::tab {
    background: #e0e2e8;
    color: #404060;
    padding: 8px 18px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: white;
    color: #1a1a2e;
    font-weight: bold;
    border-bottom: 2px solid #e94560;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #d0d0d8;
    border-radius: 6px;
    margin-top: 10px;
    padding: 12px;
    background: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #1a1a2e;
}
QTableWidget {
    background: white;
    gridline-color: #e8e8f0;
    border: 1px solid #d0d0d8;
    border-radius: 4px;
    font-size: 12px;
}
QTableWidget::item:selected {
    background-color: #d0e8ff;
    color: #1a1a2e;
}
QHeaderView::section {
    background-color: #1a1a2e;
    color: white;
    padding: 6px 8px;
    font-weight: bold;
    font-size: 12px;
    border: none;
}
QPushButton {
    border-radius: 5px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#btn_primary {
    background: #e94560;
    color: white;
    border: none;
}
QPushButton#btn_primary:hover { background: #c73652; }
QPushButton#btn_secondary {
    background: #0f3460;
    color: white;
    border: none;
}
QPushButton#btn_secondary:hover { background: #0a2444; }
QPushButton#btn_success {
    background: #27ae60;
    color: white;
    border: none;
}
QPushButton#btn_success:hover { background: #1e8449; }
QPushButton#btn_warning {
    background: #e67e22;
    color: white;
    border: none;
}
QPushButton#btn_warning:hover { background: #ca6f1e; }
QPushButton#btn_danger {
    background: #c0392b;
    color: white;
    border: none;
}
QPushButton#btn_danger:hover { background: #a93226; }
QPushButton#btn_neutral {
    background: #bdc3c7;
    color: #2c3e50;
    border: none;
}
QPushButton#btn_neutral:hover { background: #99a3a4; }
QLineEdit, QSpinBox, QComboBox {
    border: 1px solid #c0c0d0;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 13px;
    background: white;
}
QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #e94560;
}
QLabel#stat_number {
    font-size: 28px;
    font-weight: bold;
    color: #e94560;
}
QLabel#stat_title {
    font-size: 12px;
    color: #808090;
}
QStatusBar {
    background: #1a1a2e;
    color: #a0a0c0;
    font-size: 12px;
}
"""

_LOGIN_STYLE = """
QDialog {
    background-color: #1a1a2e;
}
QLabel#brand {
    color: #e94560;
    font-size: 26px;
    font-weight: bold;
}
QLabel#tagline {
    color: #606080;
    font-size: 12px;
}
QLabel#field_lbl {
    color: #c0c0e0;
    font-size: 13px;
}
QLineEdit {
    background: #16213e;
    color: #e0e0ff;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 9px 12px;
    font-size: 14px;
}
QLineEdit:focus { border-color: #e94560; }
QPushButton#login_btn {
    background: #e94560;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 11px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#login_btn:hover { background: #c73652; }
QLabel#err_lbl { color: #e94560; font-size: 12px; }
"""


# ---------------------------------------------------------------------------
# Login Dialog
# ---------------------------------------------------------------------------

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Login")
        self.setFixedSize(400, 320)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setStyleSheet(_LOGIN_STYLE)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(48, 36, 48, 36)
        lay.setSpacing(0)

        brand = QLabel("⚙  Admin Panel")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignCenter)
        tagline = QLabel("License Key Management System")
        tagline.setObjectName("tagline")
        tagline.setAlignment(Qt.AlignCenter)

        lay.addWidget(brand)
        lay.addSpacing(4)
        lay.addWidget(tagline)
        lay.addSpacing(28)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("admin")
        user_lbl = QLabel("Username:")
        user_lbl.setObjectName("field_lbl")

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setPlaceholderText("••••••••")
        pass_lbl = QLabel("Password:")
        pass_lbl.setObjectName("field_lbl")

        form.addRow(user_lbl, self.user_edit)
        form.addRow(pass_lbl, self.pass_edit)
        lay.addLayout(form)
        lay.addSpacing(8)

        self.err_lbl = QLabel("")
        self.err_lbl.setObjectName("err_lbl")
        self.err_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.err_lbl)
        lay.addSpacing(14)

        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.clicked.connect(self._on_login)
        self.pass_edit.returnPressed.connect(self._on_login)
        lay.addWidget(self.login_btn)

    def _on_login(self):
        user = self.user_edit.text().strip()
        pwd = self.pass_edit.text()
        if not user or not pwd:
            self.err_lbl.setText("Username and password are required.")
            return
        if db.admin_login(user, pwd):
            self._username = user
            self.accept()
        else:
            self.err_lbl.setText("Invalid credentials.")
            self.pass_edit.clear()

    def get_username(self) -> str:
        return getattr(self, "_username", "")


# ---------------------------------------------------------------------------
# Key Edit/Add Dialog
# ---------------------------------------------------------------------------

class KeyEditDialog(QDialog):
    """Dialog for adding a new key or editing an existing one."""

    def __init__(self, parent=None, key_data: Optional[dict] = None):
        super().__init__(parent)
        self._is_edit = key_data is not None
        self._key_data = key_data or {}
        self.setWindowTitle("Edit License Key" if self._is_edit else "Add License Key")
        self.setFixedSize(460, 400)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        # Key value
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Auto-generated if empty")
        self.key_edit.setMaxLength(29)
        if self._is_edit:
            self.key_edit.setText(self._key_data.get("key", ""))
            self.key_edit.setReadOnly(True)
            self.key_edit.setStyleSheet("background: #f0f0f0; color: #808080;")
        form.addRow("License Key:", self.key_edit)

        # User name
        self.user_edit = QLineEdit()
        self.user_edit.setText(self._key_data.get("user_name", ""))
        form.addRow("User Name:", self.user_edit)

        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setText(self._key_data.get("email", ""))
        form.addRow("Email:", self.email_edit)

        # Expiry days
        self.expiry_spin = QSpinBox()
        self.expiry_spin.setRange(0, 3650)
        self.expiry_spin.setSuffix("  days  (0 = never)")
        self.expiry_spin.setValue(365)
        form.addRow("Expires in:", self.expiry_spin)

        # Max uses
        self.max_uses_spin = QSpinBox()
        self.max_uses_spin.setRange(1, 99999)
        self.max_uses_spin.setValue(int(self._key_data.get("max_uses", 1)))
        form.addRow("Max Uses:", self.max_uses_spin)

        # Active checkbox
        self.active_check = QCheckBox("Key is active")
        self.active_check.setChecked(bool(self._key_data.get("is_active", 1)))
        form.addRow("Status:", self.active_check)

        # Notes
        self.notes_edit = QLineEdit()
        self.notes_edit.setText(self._key_data.get("notes", ""))
        form.addRow("Notes:", self.notes_edit)

        lay.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("btn_neutral")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save" if self._is_edit else "Add Key")
        save.setObjectName("btn_primary")
        save.clicked.connect(self._on_save)
        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(save)
        lay.addLayout(btn_row)

    def _on_save(self):
        user = self.user_edit.text().strip()
        email = self.email_edit.text().strip()
        expiry = self.expiry_spin.value()
        max_uses = self.max_uses_spin.value()
        is_active = self.active_check.isChecked()
        notes = self.notes_edit.text().strip()
        key_text = self.key_edit.text().strip().upper()

        if self._is_edit:
            ok = db.update_key(
                self._key_data["key"],
                user_name=user,
                email=email,
                expires_days=expiry if expiry > 0 else None,
                max_uses=max_uses,
                is_active=is_active,
                notes=notes,
            )
            if ok:
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update key.")
        else:
            if key_text:
                ok = db.add_key(
                    key_text,
                    user_name=user,
                    email=email,
                    expires_days=expiry if expiry > 0 else None,
                    max_uses=max_uses,
                    notes=notes,
                )
                if not ok:
                    QMessageBox.warning(self, "Duplicate", "That key already exists.")
                    return
            else:
                db.generate_key(
                    user_name=user,
                    email=email,
                    expires_days=expiry if expiry > 0 else None,
                    max_uses=max_uses,
                    notes=notes,
                )
            self.accept()


# ---------------------------------------------------------------------------
# Change Password Dialog
# ---------------------------------------------------------------------------

class ChangePasswordDialog(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self._username = username
        self.setWindowTitle("Change Admin Password")
        self.setFixedSize(380, 240)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        form = QFormLayout()

        self.old_edit = QLineEdit()
        self.old_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Current Password:", self.old_edit)

        self.new_edit = QLineEdit()
        self.new_edit.setEchoMode(QLineEdit.Password)
        form.addRow("New Password:", self.new_edit)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Confirm New:", self.confirm_edit)

        lay.addLayout(form)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet("color: red; font-size: 12px;")
        lay.addWidget(self.err_lbl)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("btn_neutral")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Change Password")
        save.setObjectName("btn_primary")
        save.clicked.connect(self._on_save)
        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(save)
        lay.addLayout(btn_row)

    def _on_save(self):
        old = self.old_edit.text()
        new = self.new_edit.text()
        confirm = self.confirm_edit.text()

        if not old or not new or not confirm:
            self.err_lbl.setText("All fields are required.")
            return
        if new != confirm:
            self.err_lbl.setText("New passwords do not match.")
            return
        if len(new) < 6:
            self.err_lbl.setText("Password must be at least 6 characters.")
            return
        if not db.admin_login(self._username, old):
            self.err_lbl.setText("Current password is incorrect.")
            return
        db.admin_change_password(self._username, new)
        QMessageBox.information(self, "Success", "Password changed successfully.")
        self.accept()


# ---------------------------------------------------------------------------
# Keys Tab
# ---------------------------------------------------------------------------

_KEY_COLS = ["ID", "Key", "User", "Email", "Uses", "Max", "Created", "Expires", "Active", "Notes"]
_KEY_FIELDS = ["id", "key", "user_name", "email", "uses_count", "max_uses",
               "created_at", "expires_at", "is_active", "notes"]


class KeysTab(QWidget):
    def __init__(self, status_bar: QStatusBar, parent=None):
        super().__init__(parent)
        self._status = status_bar
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search keys, users, emails…")
        self.search_edit.textChanged.connect(self._apply_filter)

        btn_gen = QPushButton("⊕  Generate Key")
        btn_gen.setObjectName("btn_success")
        btn_gen.clicked.connect(self._on_generate)

        btn_add = QPushButton("＋  Add Key")
        btn_add.setObjectName("btn_secondary")
        btn_add.clicked.connect(self._on_add)

        btn_edit = QPushButton("✎  Edit")
        btn_edit.setObjectName("btn_warning")
        btn_edit.clicked.connect(self._on_edit)

        btn_del = QPushButton("✕  Delete")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._on_delete)

        btn_refresh = QPushButton("↺  Refresh")
        btn_refresh.setObjectName("btn_neutral")
        btn_refresh.clicked.connect(self.refresh)

        toolbar.addWidget(self.search_edit, 1)
        toolbar.addWidget(btn_gen)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_del)
        toolbar.addWidget(btn_refresh)
        lay.addLayout(toolbar)

        # Table
        self.table = QTableWidget(0, len(_KEY_COLS))
        self.table.setHorizontalHeaderLabels(_KEY_COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self._on_edit)
        lay.addWidget(self.table, 1)

        # Default column widths
        self.table.setColumnWidth(0, 40)   # ID
        self.table.setColumnWidth(1, 200)  # Key
        self.table.setColumnWidth(2, 120)  # User
        self.table.setColumnWidth(3, 150)  # Email
        self.table.setColumnWidth(4, 45)   # Uses
        self.table.setColumnWidth(5, 45)   # Max
        self.table.setColumnWidth(6, 130)  # Created
        self.table.setColumnWidth(7, 130)  # Expires
        self.table.setColumnWidth(8, 50)   # Active

        self._all_rows: list = []

    def refresh(self):
        self._all_rows = db.get_all_keys()
        self._apply_filter(self.search_edit.text())
        self._status.showMessage(f"Keys loaded: {len(self._all_rows)}", 3000)

    def _apply_filter(self, text: str):
        text = text.lower()
        rows = [r for r in self._all_rows
                if not text or any(text in str(v).lower() for v in r.values())]
        self._populate(rows)

    def _populate(self, rows: list):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, field in enumerate(_KEY_FIELDS):
                val = row.get(field, "")
                if field == "is_active":
                    val = "✔ Yes" if val else "✘ No"
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if field == "is_active":
                    item.setForeground(QBrush(QColor("#27ae60" if row.get("is_active") else "#c0392b")))
                self.table.setItem(r_idx, c_idx, item)
        self.table.setSortingEnabled(True)

    def _selected_key(self) -> Optional[str]:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 1)
        return item.text() if item else None

    def _on_generate(self):
        dlg = KeyEditDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh()
            self._status.showMessage("Key generated.", 3000)

    def _on_add(self):
        dlg = KeyEditDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh()
            self._status.showMessage("Key added.", 3000)

    def _on_edit(self):
        key = self._selected_key()
        if not key:
            QMessageBox.information(self, "No Selection", "Please select a key to edit.")
            return
        data = db.get_key(key)
        if not data:
            return
        dlg = KeyEditDialog(self, key_data=data)
        if dlg.exec() == QDialog.Accepted:
            self.refresh()
            self._status.showMessage("Key updated.", 3000)

    def _on_delete(self):
        key = self._selected_key()
        if not key:
            QMessageBox.information(self, "No Selection", "Please select a key to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete license key:\n{key}\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            db.delete_key(key)
            self.refresh()
            self._status.showMessage("Key deleted.", 3000)


# ---------------------------------------------------------------------------
# Activity Tab
# ---------------------------------------------------------------------------

_LOG_COLS = ["ID", "License Key", "IP Address", "Hostname", "OS", "Login Time", "Success", "Notes"]
_LOG_FIELDS = ["id", "license_key", "ip_address", "hostname", "os_info", "login_time", "success", "notes"]


class ActivityTab(QWidget):
    def __init__(self, status_bar: QStatusBar, parent=None):
        super().__init__(parent)
        self._status = status_bar
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter by key, IP, OS, hostname…")
        self.search_edit.textChanged.connect(self._apply_filter)

        btn_refresh = QPushButton("↺  Refresh")
        btn_refresh.setObjectName("btn_neutral")
        btn_refresh.clicked.connect(self.refresh)

        toolbar.addWidget(self.search_edit, 1)
        toolbar.addWidget(btn_refresh)
        lay.addLayout(toolbar)

        self.table = QTableWidget(0, len(_LOG_COLS))
        self.table.setHorizontalHeaderLabels(_LOG_COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        lay.addWidget(self.table, 1)

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 200)
        self.table.setColumnWidth(5, 140)
        self.table.setColumnWidth(6, 60)

        self._all_rows: list = []

    def refresh(self):
        self._all_rows = db.get_login_logs(limit=1000)
        self._apply_filter(self.search_edit.text())
        self._status.showMessage(f"Activity log loaded: {len(self._all_rows)} entries", 3000)

    def _apply_filter(self, text: str):
        text = text.lower()
        rows = [r for r in self._all_rows
                if not text or any(text in str(v).lower() for v in r.values())]
        self._populate(rows)

    def _populate(self, rows: list):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, field in enumerate(_LOG_FIELDS):
                val = row.get(field, "")
                if field == "success":
                    val = "✔ Yes" if val else "✘ No"
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if field == "success":
                    item.setForeground(QBrush(QColor("#27ae60" if row.get("success") else "#c0392b")))
                self.table.setItem(r_idx, c_idx, item)
        self.table.setSortingEnabled(True)


# ---------------------------------------------------------------------------
# Dashboard Tab
# ---------------------------------------------------------------------------

class DashboardTab(QWidget):
    def __init__(self, status_bar: QStatusBar, parent=None):
        super().__init__(parent)
        self._status = status_bar
        self._build_ui()
        self.refresh()

        # Auto-refresh every 30 s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(30_000)

    def _stat_card(self, title: str, value: str) -> QGroupBox:
        box = QGroupBox()
        box.setFixedHeight(100)
        inner = QVBoxLayout(box)
        num = QLabel(value)
        num.setObjectName("stat_number")
        num.setAlignment(Qt.AlignCenter)
        lbl = QLabel(title)
        lbl.setObjectName("stat_title")
        lbl.setAlignment(Qt.AlignCenter)
        inner.addWidget(num)
        inner.addWidget(lbl)
        return box, num  # type: ignore

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(16)

        # Stat cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self._card_total_keys, self._num_total_keys = self._stat_card("Total Keys", "0")
        self._card_active_keys, self._num_active_keys = self._stat_card("Active Keys", "0")
        self._card_total_logins, self._num_total_logins = self._stat_card("Total Logins", "0")
        self._card_success_logins, self._num_success_logins = self._stat_card("Successful Logins", "0")
        self._card_unique_ips, self._num_unique_ips = self._stat_card("Unique IPs", "0")

        for card in [self._card_total_keys, self._card_active_keys,
                     self._card_total_logins, self._card_success_logins,
                     self._card_unique_ips]:
            cards_row.addWidget(card, 1)
        lay.addLayout(cards_row)

        # OS breakdown
        os_box = QGroupBox("Operating System Breakdown (successful logins)")
        os_lay = QVBoxLayout(os_box)
        self.os_table = QTableWidget(0, 2)
        self.os_table.setHorizontalHeaderLabels(["OS Info", "Count"])
        self.os_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.os_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.os_table.verticalHeader().setVisible(False)
        self.os_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.os_table.setFixedHeight(200)
        os_lay.addWidget(self.os_table)

        btn_refresh = QPushButton("↺  Refresh Stats")
        btn_refresh.setObjectName("btn_neutral")
        btn_refresh.clicked.connect(self.refresh)

        lay.addWidget(os_box)
        lay.addWidget(btn_refresh, 0, Qt.AlignRight)
        lay.addStretch()

    def refresh(self):
        stats = db.get_stats()

        self._num_total_keys.setText(str(stats["total_keys"]))
        self._num_active_keys.setText(str(stats["active_keys"]))
        self._num_total_logins.setText(str(stats["total_logins"]))
        self._num_success_logins.setText(str(stats["successful_logins"]))
        self._num_unique_ips.setText(str(stats["unique_ips"]))

        os_data = stats["os_breakdown"]
        self.os_table.setRowCount(len(os_data))
        for i, row in enumerate(os_data):
            self.os_table.setItem(i, 0, QTableWidgetItem(row["os_info"]))
            self.os_table.setItem(i, 1, QTableWidgetItem(str(row["cnt"])))

        self._status.showMessage("Dashboard refreshed.", 3000)


# ---------------------------------------------------------------------------
# Main Admin Window
# ---------------------------------------------------------------------------

class AdminWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()
        self._username = username
        self.setWindowTitle(f"Admin Panel  —  License Key Database  |  {username}")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(_APP_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet("background-color: #1a1a2e;")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 0, 20, 0)

        title_lbl = QLabel("⚙  License Key Admin Panel")
        title_lbl.setStyleSheet("color: #e94560; font-size: 16px; font-weight: bold;")

        user_lbl = QLabel(f"Logged in as: {self._username}")
        user_lbl.setStyleSheet("color: #808090; font-size: 12px;")

        btn_chpwd = QPushButton("Change Password")
        btn_chpwd.setStyleSheet(
            "background: transparent; color: #a0a0c0; border: 1px solid #404060;"
            "border-radius: 4px; padding: 4px 10px; font-size: 12px;"
        )
        btn_chpwd.clicked.connect(self._on_change_password)

        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet(
            "background: #e94560; color: white; border: none;"
            "border-radius: 4px; padding: 4px 14px; font-size: 12px; font-weight: bold;"
        )
        btn_logout.clicked.connect(self.close)

        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        h_lay.addWidget(user_lbl)
        h_lay.addSpacing(16)
        h_lay.addWidget(btn_chpwd)
        h_lay.addSpacing(8)
        h_lay.addWidget(btn_logout)
        root.addWidget(header)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        # Tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        self._dashboard_tab = DashboardTab(self._status)
        self._keys_tab = KeysTab(self._status)
        self._activity_tab = ActivityTab(self._status)

        tabs.addTab(self._dashboard_tab, "📊  Dashboard")
        tabs.addTab(self._keys_tab, "🔑  License Keys")
        tabs.addTab(self._activity_tab, "📋  Login Activity")

        root.addWidget(tabs, 1)

    def _on_change_password(self):
        dlg = ChangePasswordDialog(self._username, self)
        dlg.exec()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(_APP_STYLE)

    # Ensure DB is ready
    db.init_database()

    # Login
    login = LoginDialog()
    if login.exec() != QDialog.Accepted:
        sys.exit(0)

    window = AdminWindow(login.get_username())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
