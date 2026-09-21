from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from easy_connect import __version__
from easy_connect.core.paths import (
    askpass_script_path,
    cli_executable,
    ensure_app_dirs,
    is_frozen,
    is_windows,
    linux_bin_dir,
    package_search_path,
    powershell_module_dirs,
    python_path,
    wrappers_dir,
)


COMMAND_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def suggest_command(host: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", host.strip()).strip("-").lower()
    if not slug:
        slug = "host"
    return f"ssh-{slug}"


def sanitize_command(command: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", command.strip()).strip("-")
    return cleaned.lower()


def is_valid_command(command: str) -> bool:
    return bool(COMMAND_RE.match(command))


def next_available_command(base: str, is_taken) -> str:
    if not is_taken(base):
        return base
    index = 2
    while is_taken(f"{base}-{index}"):
        index += 1
    return f"{base}-{index}"


def wrapper_path(command: str) -> Path:
    if is_windows():
        return wrappers_dir() / f"{command}.cmd"
    return wrappers_dir() / command


def install_wrapper(command: str) -> Path:
    ensure_app_dirs()
    write_askpass_helper()
    path = wrapper_path(command)
    python = cli_executable()
    search = str(package_search_path())
    if is_windows():
        path.write_text(_cmd_wrapper(command, python, search), encoding="utf-8")
        _ps1_wrapper_path(command).write_text(
            _ps1_wrapper(command, python, search),
            encoding="utf-8",
        )
    else:
        if is_frozen():
            content = (
                "#!/bin/sh\n"
                f'exec "{python}" connect --command {command} "$@"\n'
            )
        else:
            content = (
                "#!/bin/sh\n"
                f'export PYTHONPATH="{search}"\n'
                f'exec "{python}" -m easy_connect.cli connect --command {command} "$@"\n'
            )
        path.write_text(content, encoding="utf-8")
        os.chmod(path, 0o755)
    ensure_user_path()
    refresh_powershell_module()
    return path


def remove_wrapper(command: str) -> None:
    path = wrapper_path(command)
    if path.is_file():
        path.unlink()
    if is_windows():
        ps1 = _ps1_wrapper_path(command)
        if ps1.is_file():
            ps1.unlink()
    refresh_powershell_module()


def list_wrappers() -> list[str]:
    folder = wrappers_dir()
    if not folder.is_dir():
        return []
    names = []
    for item in folder.iterdir():
        if is_windows() and item.suffix.lower() == ".cmd":
            names.append(item.stem)
        elif not is_windows() and item.is_file() and item.name.startswith("ssh-"):
            names.append(item.name)
    return sorted(names)


def ensure_user_path() -> bool:
    if is_windows():
        return _ensure_windows_path()
    return _ensure_linux_path()


def path_notice() -> str:
    folder = str(wrappers_dir())
    if is_windows():
        return (
            f"O comando foi instalado em {folder}. "
            "No PowerShell do Cursor, o módulo EasyConnect também é registrado. "
            "Se o comando curto falhar, use o caminho completo do .cmd."
        )
    return (
        f"O comando foi instalado em {folder}. "
        "Se o terminal não reconhecer o comando, feche e abra o terminal "
        "ou execute: source ~/.profile"
    )


def write_askpass_helper() -> None:
    path = askpass_script_path()
    python = python_path()
    search = str(package_search_path())
    if is_windows():
        content = (
            "import os\n"
            "import sys\n"
            "path = os.environ.get('EASY_CONNECT_ASKPASS_FILE')\n"
            "if path and os.path.isfile(path):\n"
            "    with open(path, 'r', encoding='utf-8') as handle:\n"
            "        sys.stdout.write(handle.read())\n"
            "        sys.stdout.flush()\n"
            "os._exit(0)\n"
        )
        path.write_text(content, encoding="utf-8")
        return
    content = (
        "#!/bin/sh\n"
        f'export PYTHONPATH="{search}"\n'
        f'exec "{python}" -m easy_connect.cli askpass\n'
    )
    path.write_text(content, encoding="utf-8")
    os.chmod(path, 0o755)


def _ensure_windows_path() -> bool:
    import winreg

    folder = str(wrappers_dir())
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Environment",
        0,
        winreg.KEY_READ | winreg.KEY_WRITE,
    )
    try:
        current, _ = winreg.QueryValueEx(key, "Path")
    except FileNotFoundError:
        current = ""
    parts = [part for part in current.split(";") if part]
    if folder not in parts:
        parts.append(folder)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
        _broadcast_path_change()
        winreg.CloseKey(key)
        return True
    winreg.CloseKey(key)
    return False


def _broadcast_path_change() -> None:
    import ctypes

    hwnd_broadcast = 0xFFFF
    wm_settingchange = 0x001A
    smto_abortifhung = 0x0002
    result = ctypes.c_ulong()
    ctypes.windll.user32.SendMessageTimeoutW(
        hwnd_broadcast,
        wm_settingchange,
        0,
        "Environment",
        smto_abortifhung,
        5000,
        ctypes.byref(result),
    )


def _ensure_linux_path() -> bool:
    bin_dir = linux_bin_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)
    current = os.environ.get("PATH", "")
    if str(bin_dir) in current.split(":"):
        return False
    marker = "# Easy Connect"
    line = 'export PATH="$HOME/.local/bin:$PATH"'
    profile = Path.home() / ".profile"
    existing = profile.read_text(encoding="utf-8") if profile.is_file() else ""
    if marker in existing or line in existing:
        return False
    addition = f"\n{marker}\n{line}\n"
    with profile.open("a", encoding="utf-8") as handle:
        handle.write(addition)
    return True


def python_display() -> str:
    return python_path()


def find_askpass() -> str | None:
    folder = Path(cli_executable()).parent
    names = ("easy-connect-askpass.exe", "easy-connect-askpass")
    for name in names:
        candidate = folder / name
        if candidate.is_file():
            return str(candidate)
    which = shutil.which("easy-connect-askpass")
    if which:
        return which
    script = askpass_script_path()
    if script.is_file() and not is_windows():
        return str(script)
    return None


def reinstall_wrappers(commands: list[str]) -> None:
    for command in commands:
        install_wrapper(command)
    refresh_powershell_module()


def invoke_command(command: str) -> str:
    if is_windows():
        return str(wrapper_path(command))
    return command


def refresh_powershell_module() -> None:
    if not is_windows():
        return
    names = list_wrappers()
    python = cli_executable()
    search = str(package_search_path())
    psm1 = _powershell_module_script(names, python, search)
    psd1 = _powershell_manifest(names)
    for folder in powershell_module_dirs():
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "EasyConnect.psm1").write_text(psm1, encoding="utf-8")
        (folder / "EasyConnect.psd1").write_text(psd1, encoding="utf-8")


def _ps1_wrapper_path(command: str) -> Path:
    return wrappers_dir() / f"{command}.ps1"


def _cmd_wrapper(command: str, python: str, search: str) -> str:
    if is_frozen():
        return (
            "@echo off\r\n"
            f'"{python}" connect --command {command} %*\r\n'
        )
    return (
        "@echo off\r\n"
        f'set "PYTHONPATH={search}"\r\n'
        f'"{python}" -m easy_connect.cli connect --command {command} %*\r\n'
    )


def _ps1_wrapper(command: str, python: str, search: str) -> str:
    if is_frozen():
        return (
            f"& {_ps_quote(python)} connect --command {command} @args\r\n"
            "if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\r\n"
        )
    return (
        f"$env:PYTHONPATH = {_ps_quote(search)}\r\n"
        f"& {_ps_quote(python)} -m easy_connect.cli connect --command {command} @args\r\n"
        "if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\r\n"
    )


def _powershell_module_script(names: list[str], python: str, search: str) -> str:
    if is_frozen():
        invoke = (
            "    & $script:EasyConnectPython connect --command $CommandName @Rest"
        )
        path_line = "$script:EasyConnectPythonPath = ''"
    else:
        invoke = (
            "    $env:PYTHONPATH = $script:EasyConnectPythonPath\n"
            "    & $script:EasyConnectPython -m easy_connect.cli connect --command $CommandName @Rest"
        )
        path_line = f"$script:EasyConnectPythonPath = {_ps_quote(search)}"
    lines = [
        f"$script:EasyConnectPython = {_ps_quote(python)}",
        path_line,
        "function Invoke-EasyConnectNative {",
        "    param(",
        "        [Parameter(Mandatory = $true)][string]$CommandName,",
        "        [Parameter(ValueFromRemainingArguments = $true)][object[]]$Rest",
        "    )",
        invoke,
        "}",
        "",
    ]
    for name in names:
        lines.extend(
            [
                f"function {name} {{",
                "    param([Parameter(ValueFromRemainingArguments = $true)][object[]]$Rest)",
                f"    Invoke-EasyConnectNative -CommandName {_ps_quote(name)} @Rest",
                "}",
                "",
            ]
        )
    if names:
        exported = ", ".join(_ps_quote(name) for name in names)
        lines.append(f"Export-ModuleMember -Function {exported}")
    return "\n".join(lines) + "\n"


def _powershell_manifest(names: list[str]) -> str:
    exported = ", ".join(_ps_quote(name) for name in names) or ""
    functions = f"@({exported})" if names else "@()"
    return (
        "@{\n"
        "    RootModule = 'EasyConnect.psm1'\n"
        f"    ModuleVersion = '{__version__}'\n"
        "    GUID = 'b3d7c1a4-8e2f-4c9a-9b11-6e2c0e000001'\n"
        "    Author = 'Easy Connect'\n"
        f"    FunctionsToExport = {functions}\n"
        "    CmdletsToExport = @()\n"
        "    VariablesToExport = @()\n"
        "    AliasesToExport = @()\n"
        "}\n"
    )


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"
