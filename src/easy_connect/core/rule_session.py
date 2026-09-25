from __future__ import annotations

import json
import os
from pathlib import Path

from easy_connect.core.paths import is_windows, tmp_dir


SESSION_ALLOW_CODE = 4

_SHELLS = {
    "powershell.exe",
    "pwsh.exe",
    "cmd.exe",
    "bash.exe",
    "bash",
    "sh",
    "dash",
    "zsh",
    "fish",
    "wsl.exe",
}
_WRAPPERS = {"cmd.exe", "bash.exe", "bash", "sh", "dash"}
_SKIP = {
    "python.exe",
    "pythonw.exe",
    "easy-connect-cli.exe",
    "easyconnect.exe",
    "conhost.exe",
    "openconsole.exe",
}


def terminal_allows() -> bool:
    pid = shell_pid()
    if pid <= 0 or not _alive(pid):
        return False
    sessions = _load()
    allowed = str(pid) in sessions
    _save({key: True for key in sessions if _alive(int(key))})
    return allowed


def remember_terminal() -> None:
    pid = shell_pid()
    if pid <= 0:
        return
    sessions = {key: True for key, _flag in _load().items() if _alive(int(key))}
    sessions[str(pid)] = True
    _save(sessions)


def shell_pid() -> int:
    chain = _ancestors(os.getpid())
    names = {pid: name for pid, name, _parent in chain}
    for pid, name, parent in chain:
        if pid == os.getpid() or _skipped(name):
            continue
        parent_name = names.get(parent, "")
        if name in _WRAPPERS and parent_name in _SHELLS:
            continue
        if name in _SHELLS:
            return pid
    if chain:
        return chain[-1][0]
    return os.getppid()


def _skipped(name: str) -> bool:
    lowered = name.lower()
    return lowered in _SKIP or lowered.startswith("python")


def _ancestors(start: int) -> list[tuple[int, str, int]]:
    if is_windows():
        return _windows_ancestors(start)
    return _linux_ancestors(start)


def _windows_ancestors(start: int) -> list[tuple[int, str, int]]:
    import ctypes
    from ctypes import wintypes

    class Entry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    kernel = ctypes.windll.kernel32
    snapshot = kernel.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == ctypes.c_void_p(-1).value or snapshot == -1:
        return []
    by_pid: dict[int, tuple[str, int]] = {}
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(Entry)
        if not kernel.Process32FirstW(snapshot, ctypes.byref(entry)):
            return []
        while True:
            by_pid[int(entry.th32ProcessID)] = (
                str(entry.szExeFile).lower(),
                int(entry.th32ParentProcessID),
            )
            if not kernel.Process32NextW(snapshot, ctypes.byref(entry)):
                break
    finally:
        kernel.CloseHandle(snapshot)

    chain: list[tuple[int, str, int]] = []
    pid = start
    seen: set[int] = set()
    while pid and pid not in seen and pid in by_pid:
        seen.add(pid)
        name, parent = by_pid[pid]
        chain.append((pid, name, parent))
        pid = parent
    return chain


def _linux_ancestors(start: int) -> list[tuple[int, str, int]]:
    chain: list[tuple[int, str, int]] = []
    pid = start
    seen: set[int] = set()
    while pid and pid not in seen:
        seen.add(pid)
        comm = Path(f"/proc/{pid}/comm")
        stat = Path(f"/proc/{pid}/stat")
        if not comm.is_file() or not stat.is_file():
            break
        name = comm.read_text(encoding="utf-8").strip().lower()
        text = stat.read_text(encoding="utf-8")
        marker = text.rfind(")")
        parent = int(text[marker + 2 :].split()[1]) if marker >= 0 else 0
        chain.append((pid, name, parent))
        pid = parent
    return chain


def _alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if is_windows():
        import ctypes

        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        kernel.CloseHandle(handle)
        return True
    return Path(f"/proc/{pid}").exists()


def _path() -> Path:
    return tmp_dir() / "rule-sessions.json"


def _load() -> dict[str, bool]:
    path = _path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    sessions = data.get("sessions") if isinstance(data, dict) else None
    if not isinstance(sessions, dict):
        return {}
    return {str(key): True for key in sessions}


def _save(sessions: dict[str, bool]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"sessions": sessions}, indent=2),
        encoding="utf-8",
    )
