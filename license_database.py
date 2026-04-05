#!/usr/bin/env python3
"""
License Key Database Manager
Handles key storage, generation, CRUD operations, and login activity tracking.
"""

import os
import sqlite3
import secrets
import string
import hashlib
import platform
import socket
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Database location: beside this file so it travels with the bot
_DB_PATH = Path(__file__).parent / "license_keys.db"

# Default admin user.  A random password is generated on first install and
# printed to the console once – the admin must note it and change it via the
# admin panel.  The plaintext is never stored anywhere.
_DEFAULT_ADMIN_USER = "admin"


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


def _utcnow_str() -> str:
    """Return the current UTC time as an ISO string without tzinfo suffix."""
    return _utcnow().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """Return (hex_hash, hex_salt) using PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_bytes(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return dk.hex(), salt.hex()


def _verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """Verify a plaintext password against stored hash+salt."""
    salt = bytes.fromhex(stored_salt)
    dk, _ = _hash_password(password, salt)
    return secrets.compare_digest(dk, stored_hash)


def _generate_license_key() -> str:
    """Generate a strong license key in format XXXXX-XXXXX-XXXXX-XXXXX-XXXXX."""
    alphabet = string.ascii_uppercase + string.digits
    # Remove ambiguous chars: O, 0, I, 1
    alphabet = alphabet.translate(str.maketrans("", "", "O0I1"))
    groups = ["".join(secrets.choice(alphabet) for _ in range(5)) for _ in range(5)]
    return "-".join(groups)


def _get_client_info() -> Dict[str, str]:
    """Collect local machine info for the login log."""
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"

    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "127.0.0.1"

    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    return {"ip": ip, "hostname": hostname, "os_info": os_info}


# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------

def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Return a connection with row_factory set to sqlite3.Row."""
    path = str(db_path or _DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database(db_path: Optional[Path] = None) -> None:
    """Create tables and seed default admin account if needed."""
    conn = get_connection(db_path)
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                pass_hash   TEXT    NOT NULL,
                pass_salt   TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                last_login  TEXT
            );

            CREATE TABLE IF NOT EXISTS license_keys (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                key         TEXT    NOT NULL UNIQUE,
                user_name   TEXT    NOT NULL DEFAULT '',
                email       TEXT    NOT NULL DEFAULT '',
                max_uses    INTEGER NOT NULL DEFAULT 1,
                uses_count  INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                expires_at  TEXT,
                is_active   INTEGER NOT NULL DEFAULT 1,
                notes       TEXT    NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS login_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT    NOT NULL,
                ip_address  TEXT    NOT NULL DEFAULT '',
                hostname    TEXT    NOT NULL DEFAULT '',
                os_info     TEXT    NOT NULL DEFAULT '',
                login_time  TEXT    NOT NULL DEFAULT (datetime('now')),
                success     INTEGER NOT NULL DEFAULT 1,
                notes       TEXT    NOT NULL DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_keys_key         ON license_keys(key);
            CREATE INDEX IF NOT EXISTS idx_logs_key         ON login_logs(license_key);
            CREATE INDEX IF NOT EXISTS idx_logs_login_time  ON login_logs(login_time);
        """)

        # Seed default admin if table is empty – generate a random password
        row = conn.execute("SELECT COUNT(*) FROM admin_users").fetchone()
        if row[0] == 0:
            # Generate a cryptographically random 16-character password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            initial_password = "".join(secrets.choice(alphabet) for _ in range(16))
            ph, ps = _hash_password(initial_password)
            conn.execute(
                "INSERT INTO admin_users (username, pass_hash, pass_salt) VALUES (?, ?, ?)",
                (_DEFAULT_ADMIN_USER, ph, ps),
            )
            print("\n" + "=" * 60)
            print("  ADMIN PANEL – INITIAL CREDENTIALS")
            print("=" * 60)
            print(f"  Username : {_DEFAULT_ADMIN_USER}")
            print(f"  Password : {initial_password}")
            print("  ⚠  Change this password after your first login!")
            print("=" * 60 + "\n")
    conn.close()


# ---------------------------------------------------------------------------
# Admin authentication
# ---------------------------------------------------------------------------

def admin_login(username: str, password: str, db_path: Optional[Path] = None) -> bool:
    """Return True if credentials are valid."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT pass_hash, pass_salt FROM admin_users WHERE username = ?",
            (username,),
        ).fetchone()
        if row is None:
            return False
        ok = _verify_password(password, row["pass_hash"], row["pass_salt"])
        if ok:
            conn.execute(
                "UPDATE admin_users SET last_login = datetime('now') WHERE username = ?",
                (username,),
            )
            conn.commit()
        return ok
    finally:
        conn.close()


def admin_change_password(username: str, new_password: str, db_path: Optional[Path] = None) -> bool:
    """Change admin password. Returns True on success."""
    conn = get_connection(db_path)
    try:
        ph, ps = _hash_password(new_password)
        cur = conn.execute(
            "UPDATE admin_users SET pass_hash = ?, pass_salt = ? WHERE username = ?",
            (ph, ps, username),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# License key CRUD
# ---------------------------------------------------------------------------

def generate_key(
    user_name: str = "",
    email: str = "",
    expires_days: Optional[int] = 365,
    max_uses: int = 1,
    notes: str = "",
    db_path: Optional[Path] = None,
) -> str:
    """Generate a new license key, persist it, and return the key string."""
    key = _generate_license_key()
    expires_at = None
    if expires_days is not None:
        expires_at = (_utcnow() + timedelta(days=expires_days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    conn = get_connection(db_path)
    try:
        conn.execute(
            """INSERT INTO license_keys
                   (key, user_name, email, max_uses, expires_at, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (key, user_name, email, max_uses, expires_at, notes),
        )
        conn.commit()
    finally:
        conn.close()
    return key


def add_key(
    key: str,
    user_name: str = "",
    email: str = "",
    expires_days: Optional[int] = 365,
    max_uses: int = 1,
    notes: str = "",
    db_path: Optional[Path] = None,
) -> bool:
    """Insert an externally supplied key. Returns True on success."""
    expires_at = None
    if expires_days is not None:
        expires_at = (_utcnow() + timedelta(days=expires_days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    conn = get_connection(db_path)
    try:
        conn.execute(
            """INSERT INTO license_keys
                   (key, user_name, email, max_uses, expires_at, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (key, user_name, email, max_uses, expires_at, notes),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_all_keys(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return all license keys as a list of dicts."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM license_keys ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_key(key: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Return a single key record or None."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM license_keys WHERE key = ?", (key,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_key(
    key: str,
    user_name: Optional[str] = None,
    email: Optional[str] = None,
    expires_days: Optional[int] = None,
    max_uses: Optional[int] = None,
    is_active: Optional[bool] = None,
    notes: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> bool:
    """Update mutable fields of a license key. Returns True if a row was changed."""
    fields: List[str] = []
    params: List[Any] = []

    if user_name is not None:
        fields.append("user_name = ?")
        params.append(user_name)
    if email is not None:
        fields.append("email = ?")
        params.append(email)
    if expires_days is not None:
        expires_at = (_utcnow() + timedelta(days=expires_days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        fields.append("expires_at = ?")
        params.append(expires_at)
    if max_uses is not None:
        fields.append("max_uses = ?")
        params.append(max_uses)
    if is_active is not None:
        fields.append("is_active = ?")
        params.append(1 if is_active else 0)
    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)

    if not fields:
        return False

    params.append(key)
    # Safe: `fields` is built exclusively from the controlled strings above,
    # never from user input, so f-string interpolation here cannot be injected.
    sql = f"UPDATE license_keys SET {', '.join(fields)} WHERE key = ?"
    conn = get_connection(db_path)
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_key(key: str, db_path: Optional[Path] = None) -> bool:
    """Delete a license key record. Returns True if deleted."""
    conn = get_connection(db_path)
    try:
        cur = conn.execute("DELETE FROM license_keys WHERE key = ?", (key,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# License validation (used by the bot at startup)
# ---------------------------------------------------------------------------

def validate_key(key: str, db_path: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Validate a license key.

    Returns (is_valid, message).
    Side-effect: logs the attempt and increments uses_count on success.
    """
    client = _get_client_info()

    def _log(success: bool, notes: str = "") -> None:
        conn2 = get_connection(db_path)
        try:
            conn2.execute(
                """INSERT INTO login_logs
                       (license_key, ip_address, hostname, os_info, success, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (key, client["ip"], client["hostname"], client["os_info"], 1 if success else 0, notes),
            )
            conn2.commit()
        finally:
            conn2.close()

    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM license_keys WHERE key = ?", (key,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        _log(False, "Key not found")
        return False, "Invalid license key."

    record = dict(row)

    if not record["is_active"]:
        _log(False, "Key disabled")
        return False, "This license key has been disabled."

    if record["expires_at"]:
        try:
            exp = datetime.strptime(record["expires_at"], "%Y-%m-%d %H:%M:%S")
            if _utcnow().replace(tzinfo=None) > exp:
                _log(False, "Key expired")
                return False, f"License expired on {exp.strftime('%Y-%m-%d')}."
        except ValueError:
            pass

    if record["max_uses"] > 0 and record["uses_count"] >= record["max_uses"]:
        _log(False, "Max uses reached")
        return False, "License key has reached its maximum number of uses."

    # Increment use counter and log success
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE license_keys SET uses_count = uses_count + 1 WHERE key = ?",
            (key,),
        )
        conn.commit()
    finally:
        conn.close()

    _log(True)
    user = record["user_name"] or "User"
    exp_str = ""
    if record["expires_at"]:
        try:
            exp = datetime.strptime(record["expires_at"], "%Y-%m-%d %H:%M:%S")
            exp_str = f" (expires {exp.strftime('%Y-%m-%d')})"
        except ValueError:
            pass
    return True, f"Welcome, {user}!{exp_str}"


# ---------------------------------------------------------------------------
# Login log queries
# ---------------------------------------------------------------------------

def get_login_logs(
    limit: int = 500,
    key_filter: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Return recent login log entries, newest first."""
    conn = get_connection(db_path)
    try:
        if key_filter:
            rows = conn.execute(
                "SELECT * FROM login_logs WHERE license_key = ? ORDER BY login_time DESC LIMIT ?",
                (key_filter, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM login_logs ORDER BY login_time DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_stats(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Return summary statistics for the dashboard."""
    conn = get_connection(db_path)
    try:
        total_keys = conn.execute("SELECT COUNT(*) FROM license_keys").fetchone()[0]
        active_keys = conn.execute(
            "SELECT COUNT(*) FROM license_keys WHERE is_active = 1"
        ).fetchone()[0]
        total_logins = conn.execute("SELECT COUNT(*) FROM login_logs").fetchone()[0]
        successful_logins = conn.execute(
            "SELECT COUNT(*) FROM login_logs WHERE success = 1"
        ).fetchone()[0]
        unique_ips = conn.execute(
            "SELECT COUNT(DISTINCT ip_address) FROM login_logs WHERE success = 1"
        ).fetchone()[0]
        unique_os = conn.execute(
            "SELECT os_info, COUNT(*) AS cnt FROM login_logs WHERE success = 1 "
            "GROUP BY os_info ORDER BY cnt DESC"
        ).fetchall()
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "total_logins": total_logins,
            "successful_logins": successful_logins,
            "unique_ips": unique_ips,
            "os_breakdown": [dict(r) for r in unique_os],
        }
    finally:
        conn.close()


# Initialise DB when module is imported (safe to call multiple times)
init_database()
