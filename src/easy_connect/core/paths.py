from pathlib import Path
import os
import sys


APP_NAME = "EasyConnect"
LINUX_APP_NAME = "easy-connect"


def is_windows() -> bool:
    return sys.platform == "win32"


def app_data_dir() -> Path:
    if is_windows():
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / APP_NAME
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / LINUX_APP_NAME
    return Path.home() / ".local" / "share" / LINUX_APP_NAME


def vault_path() -> Path:
    return app_data_dir() / "vault.json"


def session_key_path() -> Path:
    return app_data_dir() / "session.key"


def tmp_dir() -> Path:
    return app_data_dir() / "tmp"


def windows_bin_dir() -> Path:
    return app_data_dir() / "bin"


def linux_bin_dir() -> Path:
    return Path.home() / ".local" / "bin"


def wrappers_dir() -> Path:
    if is_windows():
        return windows_bin_dir()
    return linux_bin_dir()


def askpass_script_path() -> Path:
    if is_windows():
        return app_data_dir() / "askpass_startup.py"
    return app_data_dir() / "askpass.sh"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def install_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(sys.executable).resolve().parent


def resource_base() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[1]


def python_path() -> str:
    return sys.executable


def cli_executable() -> str:
    if is_frozen():
        name = "easy-connect-cli.exe" if is_windows() else "easy-connect-cli"
        candidate = install_dir() / name
        if candidate.is_file():
            return str(candidate)
        return str(Path(sys.executable).resolve())
    return sys.executable


def gui_executable() -> str:
    if is_frozen():
        name = "EasyConnect.exe" if is_windows() else "EasyConnect"
        candidate = install_dir() / name
        if candidate.is_file():
            return str(candidate)
        return str(Path(sys.executable).resolve())
    return sys.executable


def gui_unlock_args() -> list[str]:
    if is_frozen():
        return [gui_executable(), "--unlock"]
    return [python_path(), "-m", "easy_connect.app", "--unlock"]


def gui_disabled_connection_args(command: str) -> list[str]:
    if is_frozen():
        return [gui_executable(), "--disabled-connection", command]
    return [python_path(), "-m", "easy_connect.app", "--disabled-connection", command]


def gui_rule_prompt_args(command: str, remote: list[str]) -> list[str]:
    if is_frozen():
        args = [gui_executable(), "--rule-prompt", command]
    else:
        args = [python_path(), "-m", "easy_connect.app", "--rule-prompt", command]
    if remote:
        args.append("--")
        args.extend(remote)
    return args


def package_search_path() -> Path:
    if is_frozen():
        return install_dir()
    return Path(__file__).resolve().parents[2]


def icon_path() -> Path | None:
    return resource_file("icon.png")


def resource_file(name: str) -> Path | None:
    candidates = [
        resource_base() / "easy_connect" / "resources" / name,
        resource_base() / "resources" / name,
        Path(__file__).resolve().parents[1] / "resources" / name,
        Path(__file__).resolve().parents[3] / "src" / "easy_connect" / "resources" / name,
    ]
    if is_frozen():
        candidates.insert(0, install_dir() / name)
        candidates.insert(0, install_dir() / "resources" / name)
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate
        except OSError:
            continue
    return None


def windows_documents_dir() -> Path:
    if is_windows():
        try:
            import ctypes
            from ctypes import wintypes

            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
            if buf.value:
                return Path(buf.value)
        except Exception:
            pass
    return Path.home() / "Documents"


def powershell_module_dirs() -> list[Path]:
    documents = windows_documents_dir()
    return [
        documents / "WindowsPowerShell" / "Modules" / "EasyConnect",
        documents / "PowerShell" / "Modules" / "EasyConnect",
    ]


def ensure_app_dirs() -> None:
    app_data_dir().mkdir(parents=True, exist_ok=True)
    tmp_dir().mkdir(parents=True, exist_ok=True)
    wrappers_dir().mkdir(parents=True, exist_ok=True)
