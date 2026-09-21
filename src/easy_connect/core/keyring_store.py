from __future__ import annotations

import os
import time
from pathlib import Path

from easy_connect.core.crypto import b64, b64b
from easy_connect.core.paths import ensure_app_dirs, is_windows, session_key_path

SERVICE = "EasyConnect"
USERNAME = "vault-key"
SEPARATOR = "|"


def current_boot_id() -> str:
    if is_windows():
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetTickCount64.restype = ctypes.c_uint64
        elapsed = kernel32.GetTickCount64() / 1000.0
        return str(int((time.time() - elapsed) // 5))
    try:
        for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines():
            if line.startswith("btime "):
                return line.split()[1]
    except OSError:
        pass
    return "unknown"


def _pack(key: bytes) -> str:
    return f"{b64(key)}{SEPARATOR}{current_boot_id()}"


def _unpack(raw: str | None) -> bytes | None:
    if not raw:
        return None
    encoded, sep, boot = raw.partition(SEPARATOR)
    if not sep or boot != current_boot_id():
        clear_key()
        return None
    try:
        return b64b(encoded)
    except Exception:
        clear_key()
        return None


def save_key(key: bytes) -> None:
    encoded = _pack(key)
    if _save_keyring(encoded):
        _clear_file_fallback()
        return
    _write_file_fallback(encoded)


def load_key() -> bytes | None:
    packed = _load_keyring()
    if packed:
        return _unpack(packed)
    return _unpack(_read_file_fallback_text())


def clear_key() -> None:
    _clear_keyring()
    _clear_file_fallback()


def _save_keyring(encoded: str) -> bool:
    try:
        import keyring

        keyring.set_password(SERVICE, USERNAME, encoded)
        return True
    except Exception:
        return False


def _load_keyring() -> str | None:
    try:
        import keyring

        return keyring.get_password(SERVICE, USERNAME)
    except Exception:
        return None


def _clear_keyring() -> None:
    try:
        import keyring

        keyring.delete_password(SERVICE, USERNAME)
    except Exception:
        pass


def _write_file_fallback(encoded: str) -> None:
    ensure_app_dirs()
    path = session_key_path()
    path.write_text(encoded, encoding="ascii")
    _restrict(path)


def _read_file_fallback_text() -> str | None:
    path = session_key_path()
    if not path.is_file():
        return None
    return path.read_text(encoding="ascii").strip()


def _clear_file_fallback() -> None:
    path = session_key_path()
    if path.is_file():
        path.unlink()


def _restrict(path: Path) -> None:
    if is_windows():
        return
    os.chmod(path, 0o600)
