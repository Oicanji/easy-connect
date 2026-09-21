from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from easy_connect.core.commands import invoke_command
from easy_connect.core.models import Connection
from easy_connect.core.paths import is_windows, tmp_dir
from easy_connect.llm.actions import action_prompt


TOOL_COMMANDS = {
    "claude": ("claude",),
    "cursor": ("cursor", "agent"),
    "antigravity": ("antigravity", "agy"),
    "codex": ("codex",),
}


def powershell_exe() -> str:
    return str(
        Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / "System32"
        / "WindowsPowerShell"
        / "v1.0"
        / "powershell.exe"
    )


def open_connected_terminal(command: str) -> None:
    invoke = invoke_command(command)
    if is_windows():
        quoted = invoke.replace("'", "''")
        script = f"& '{quoted}'"
        wt = shutil.which("wt.exe") or shutil.which("wt")
        if wt:
            subprocess.Popen(
                [wt, "new-tab", "--title", command, powershell_exe(), "-NoExit", "-Command", script],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return
        subprocess.Popen(
            [powershell_exe(), "-NoExit", "-Command", script],
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
        return
    shell = f"{command}; exec $SHELL"
    for candidate in (
        ["gnome-terminal", "--", "bash", "-lc", shell],
        ["konsole", "-e", "bash", "-lc", shell],
        ["xfce4-terminal", "-e", f"bash -lc '{shell}'"],
        ["xterm", "-e", "bash", "-lc", shell],
    ):
        if shutil.which(candidate[0]):
            subprocess.Popen(candidate)
            return
    raise FileNotFoundError("Nenhum terminal foi encontrado.")


def launch_assistant(tool: str, action_id: str, connection: Connection) -> str:
    prompt = action_prompt(action_id, connection)
    binary = _which_tool(tool)
    tmp_dir().mkdir(parents=True, exist_ok=True)
    prompt_file = tmp_dir() / f"prompt-{tool}-{action_id}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    if binary is None:
        return (
            "O prompt foi copiado. Não encontrei o aplicativo no PATH. "
            "Cole no chat do assistente."
        )
    if is_windows():
        prompt_path = str(prompt_file).replace("'", "''")
        binary_path = binary.replace("'", "''")
        script = (
            f"$p = Get-Content -Raw -Encoding UTF8 '{prompt_path}'; "
            f"& '{binary_path}' $p"
        )
        wt = shutil.which("wt.exe") or shutil.which("wt")
        if wt:
            subprocess.Popen(
                [wt, "new-tab", "--title", tool, powershell_exe(), "-NoExit", "-Command", script],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            subprocess.Popen(
                [powershell_exe(), "-NoExit", "-Command", script],
                creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
            )
    else:
        subprocess.Popen([binary, prompt], start_new_session=True)
    return "O prompt foi copiado e o assistente foi aberto."


def _which_tool(tool: str) -> str | None:
    for name in TOOL_COMMANDS.get(tool, ()):
        found = shutil.which(name)
        if found:
            return found
    extra: list[Path] = []
    local = os.environ.get("LOCALAPPDATA") or ""
    home = Path.home()
    if tool == "cursor":
        extra.extend(
            [
                Path(local) / "Programs" / "cursor" / "Cursor.exe",
                home / "AppData" / "Local" / "Programs" / "cursor" / "Cursor.exe",
            ]
        )
    if tool == "antigravity":
        extra.extend(
            [
                Path(local) / "Programs" / "Antigravity" / "Antigravity.exe",
                home / "AppData" / "Local" / "Programs" / "Antigravity" / "Antigravity.exe",
            ]
        )
    for path in extra:
        if path.is_file():
            return str(path)
    return None
