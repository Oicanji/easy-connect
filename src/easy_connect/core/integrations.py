from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from easy_connect.core.commands import _ps_quote, invoke_command
from easy_connect.core.models import Connection
from easy_connect.core.paths import is_windows, tmp_dir, wrappers_dir
from easy_connect.i18n import t
from easy_connect.llm.actions import action_prompt


TOOL_CLIS = {
    "claude": {
        "names": ("claude",),
        "flags": (),
        "cli_files": ("claude.exe", "claude.cmd", "claude"),
        "install_win": "npm install -g @anthropic-ai/claude-code",
        "install_unix": "curl -fsSL https://claude.ai/install.sh | bash",
    },
    "cursor": {
        "names": ("agent", "cursor-agent"),
        "flags": (),
        "cli_files": (
            "agent.cmd",
            "agent.exe",
            "cursor-agent.cmd",
            "cursor-agent.exe",
            "agent",
        ),
        "install_win": "irm 'https://cursor.com/install?win32=true' | iex",
        "install_unix": "curl https://cursor.com/install -fsS | bash",
    },
    "antigravity": {
        "names": ("agy",),
        "flags": ("--prompt-interactive",),
        "cli_files": ("agy.exe", "agy.cmd", "agy.ps1", "agy"),
        "install_win": "irm https://antigravity.google/cli/install.ps1 | iex",
        "install_unix": "curl -fsSL https://antigravity.google/cli/install.sh | bash",
    },
    "codex": {
        "names": ("codex",),
        "flags": (),
        "cli_files": ("codex.exe", "codex.cmd", "codex.ps1", "codex"),
        "install_win": "irm https://chatgpt.com/codex/install.ps1 | iex",
        "install_unix": "curl -fsSL https://chatgpt.com/codex/install.sh | sh",
    },
}

TOOL_LABELS = {
    "claude": "Claude Code",
    "cursor": "Cursor",
    "antigravity": "Antigravity",
    "codex": "Codex",
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
    raise FileNotFoundError(t("term.missing"))


def launch_assistant(
    tool: str,
    action_id: str,
    connection: Connection,
    configured_path: str = "",
    custom_prompt: str = "",
    attachments: list[str] | None = None,
) -> str:
    spec = TOOL_CLIS.get(tool)
    if spec is None:
        return t("agent.missing")
    prompt = action_prompt(
        action_id,
        connection,
        custom_text=custom_prompt,
        attachments=attachments,
    )
    tmp_dir().mkdir(parents=True, exist_ok=True)
    prompt_file = tmp_dir() / f"prompt-{tool}-{action_id}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    cli = _resolve_cli(tool, configured_path)
    flags = tuple(spec["flags"])
    if is_windows():
        _start_windows_agent(tool, flags, cli, prompt_file, ensure_cli=True)
        return ""
    if cli is None:
        label = TOOL_LABELS.get(tool, tool)
        return t("agent.cli_missing", label=label)
    _start_unix_agent(flags, cli, prompt_file)
    return ""


def _start_windows_agent(
    tool: str,
    flags: tuple[str, ...],
    cli: str | None,
    prompt_file: Path,
    ensure_cli: bool = False,
) -> None:
    script = tmp_dir() / f"launch-{tool}.ps1"
    spec = TOOL_CLIS[tool]
    flag_list = ", ".join(_ps_quote(flag) for flag in flags)
    extra_paths = ", ".join(_ps_quote(str(path)) for path in _known_cli_paths(tool))
    names = ", ".join(_ps_quote(name) for name in spec["names"])
    cli_literal = _ps_quote(cli) if cli else "$null"
    lines = [
        "$ErrorActionPreference = 'Continue'",
        "[Console]::OutputEncoding = [Text.UTF8Encoding]::new()",
        "function Refresh-Path {",
        "  $machine = [Environment]::GetEnvironmentVariable('Path','Machine')",
        "  $user = [Environment]::GetEnvironmentVariable('Path','User')",
        f"  $bin = {_ps_quote(str(wrappers_dir()))}",
        "  $agentDir = Join-Path $env:LOCALAPPDATA 'cursor-agent'",
        "  $agyDir = Join-Path $env:LOCALAPPDATA 'agy\\bin'",
        "  $localBin = Join-Path $env:USERPROFILE '.local\\bin'",
        "  $codexDir = Join-Path $env:LOCALAPPDATA 'Programs\\codex'",
        "  $env:Path = \"$agentDir;$agyDir;$localBin;$codexDir;$bin;$user;$machine;$env:Path\"",
        "}",
        "function Find-Cli {",
        f"  $names = @({names})",
        f"  $extra = @({extra_paths})",
        "  foreach ($item in $extra) { if ($item -and (Test-Path -LiteralPath $item)) { return $item } }",
        "  foreach ($name in $names) {",
        "    $found = Get-Command $name -ErrorAction SilentlyContinue",
        "    if ($found) { return $found.Source }",
        "  }",
        "  return $null",
        "}",
        "Refresh-Path",
        f"$prompt = Get-Content -LiteralPath {_ps_quote(str(prompt_file))} -Raw -Encoding UTF8",
        "$prompt = [regex]::Replace([string]$prompt, '\\s+', ' ').Trim()",
        f"$exe = {cli_literal}",
        "if (-not $exe) { $exe = Find-Cli }",
        "if ($exe -and $exe.ToLower().EndsWith('.cmd')) {",
        "  $ps1 = [IO.Path]::ChangeExtension($exe, '.ps1')",
        "  $alt = Join-Path (Split-Path -Parent $exe) 'cursor-agent.ps1'",
        "  if (Test-Path -LiteralPath $ps1) { $exe = $ps1 }",
        "  elseif (Test-Path -LiteralPath $alt) { $exe = $alt }",
        "}",
    ]
    if ensure_cli:
        lines.extend(
            [
                "if (-not $exe) {",
                f"  Write-Host {_ps_quote(t('agent.installing', label=TOOL_LABELS.get(tool, tool)))}",
                f"  {spec['install_win']}",
                "  Refresh-Path",
                "  $exe = Find-Cli",
                "}",
            ]
        )
    lines.extend(
        [
            "if (-not $exe) {",
            f"  Write-Host {_ps_quote(t('agent.start_failed'))}",
            f"  Read-Host {_ps_quote(t('agent.press_enter'))}",
            "  exit 1",
            "}",
            f"$flags = @({flag_list})" if flag_list else "$flags = @()",
            "& $exe @flags $prompt",
            "if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { Read-Host "
            + _ps_quote(t("agent.press_enter"))
            + " }",
        ]
    )
    script.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    subprocess.Popen(
        [
            powershell_exe(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
        ],
        cwd=str(Path.home()),
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )


def _start_unix_agent(
    flags: tuple[str, ...],
    cli: str,
    prompt_file: Path,
) -> None:
    extra = " ".join(_sh_quote(flag) for flag in flags)
    quoted = _sh_quote(cli)
    run = f'{quoted} {extra} "$(cat {_sh_quote(str(prompt_file))})"'.strip()
    shell = (
        f'export PATH="{wrappers_dir()}:$HOME/.local/bin:$PATH"; '
        f"{run}; exec $SHELL"
    )
    for candidate in (
        ["gnome-terminal", "--", "bash", "-lc", shell],
        ["konsole", "-e", "bash", "-lc", shell],
        ["xfce4-terminal", "-e", f"bash -lc {_sh_quote(shell)}"],
        ["xterm", "-e", "bash", "-lc", shell],
    ):
        if shutil.which(candidate[0]):
            subprocess.Popen(candidate)
            return
    subprocess.Popen(["bash", "-lc", run], start_new_session=True)


def _resolve_cli(tool: str, configured_path: str = "") -> str | None:
    configured = _from_configured(tool, configured_path)
    if configured is not None:
        return configured
    for candidate in _known_cli_paths(tool):
        resolved = _as_cli(tool, candidate)
        if resolved is not None:
            return str(resolved)
    for name in TOOL_CLIS[tool]["names"]:
        found = shutil.which(name)
        if not found:
            continue
        resolved = _as_cli(tool, Path(found))
        if resolved is not None:
            return str(resolved)
    return None


def _from_configured(tool: str, configured_path: str) -> str | None:
    if not configured_path.strip():
        return None
    raw = Path(configured_path.strip()).expanduser()
    if not raw.exists():
        return None
    if raw.is_file():
        resolved = _as_cli(tool, raw)
        if resolved is not None:
            return str(resolved)
        return None
    hit = _find_named(raw, TOOL_CLIS[tool]["cli_files"])
    if hit is not None:
        resolved = _as_cli(tool, hit)
        if resolved is not None:
            return str(resolved)
    return None


def _as_cli(tool: str, path: Path) -> Path | None:
    if not path.is_file():
        return None
    name = path.name.lower()
    if name in {
        "cursor.exe",
        "cursor.cmd",
        "cursor",
        "antigravity.exe",
        "antigravity ide.exe",
        "antigravity-ide.exe",
        "antigravity-ide.cmd",
        "chatgpt.exe",
    }:
        return None
    if name.endswith(".cmd"):
        ps1 = path.with_suffix(".ps1")
        sibling = path.parent / "cursor-agent.ps1"
        if ps1.is_file():
            return ps1
        if tool == "cursor" and sibling.is_file():
            return sibling
    return path


def _find_named(root: Path, names: tuple[str, ...]) -> Path | None:
    wanted = {name.lower() for name in names}
    folders = (
        root,
        root / "bin",
        root / "resources" / "app" / "bin",
        root / "agy" / "bin",
    )
    for folder in folders:
        if not folder.is_dir():
            continue
        try:
            entries = list(folder.iterdir())
        except OSError:
            continue
        for item in entries:
            if item.is_file() and item.name.lower() in wanted:
                return item
    return None


def _known_cli_paths(tool: str) -> list[Path]:
    local = Path(os.environ.get("LOCALAPPDATA") or "")
    roaming = Path(os.environ.get("APPDATA") or "")
    home = Path.home()
    if tool == "cursor":
        return [
            local / "cursor-agent" / "agent.ps1",
            local / "cursor-agent" / "cursor-agent.ps1",
            local / "cursor-agent" / "agent.cmd",
            local / "cursor-agent" / "cursor-agent.cmd",
            home / ".local" / "bin" / "agent.exe",
            home / ".local" / "bin" / "agent",
        ]
    if tool == "claude":
        return [
            home / ".local" / "bin" / "claude.exe",
            home / ".local" / "bin" / "claude",
            roaming / "npm" / "claude.cmd",
            local / "npm" / "claude.cmd",
        ]
    if tool == "codex":
        return [
            home / ".local" / "bin" / "codex.exe",
            home / ".local" / "bin" / "codex",
            roaming / "npm" / "codex.cmd",
            roaming / "npm" / "codex.ps1",
            local / "Programs" / "codex" / "codex.exe",
            local / "codex" / "codex.exe",
        ]
    if tool == "antigravity":
        return [
            local / "agy" / "bin" / "agy.exe",
            local / "agy" / "bin" / "agy.cmd",
            local / "agy" / "agy.exe",
            home / ".local" / "bin" / "agy",
            home / ".local" / "bin" / "agy.exe",
        ]
    return []


def _sh_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"
