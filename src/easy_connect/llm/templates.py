from __future__ import annotations

import re
from typing import Literal

from pathlib import Path

from easy_connect.core.commands import invoke_command
from easy_connect.core.models import Connection, LlmExport, as_auth_method, as_llm_kind
from easy_connect.core.paths import is_windows

LlmKind = Literal["claude", "cursor", "antigravity"]


def suggested_filename(kind: LlmKind, connection: Connection) -> str:
    slug = _slug(connection.name or connection.command)
    if kind == "claude":
        return "CLAUDE.md"
    if kind == "cursor":
        return f".cursor/rules/vm-{slug}.mdc"
    return f".agents/rules/vm-{slug}.md"


def build_instruction(kind: LlmKind, connection: Connection) -> str:
    body = _body(connection)
    if kind == "cursor":
        header = (
            "---\n"
            f"description: SSH access for {connection.name} ({connection.host})\n"
            "alwaysApply: true\n"
            "---\n\n"
        )
        return header + body
    return body


def write_instruction(kind: LlmKind, connection: Connection, path: str | Path) -> Path:
    output = Path(path)
    if output.suffix.lower() not in {".md", ".mdc"}:
        suffix = ".mdc" if kind == "cursor" else ".md"
        output = output.with_name(output.name + suffix)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_instruction(kind, connection), encoding="utf-8")
    if not output.is_file():
        raise OSError("O arquivo não foi gravado no disco.")
    return output


def remember_export(connection: Connection, kind: LlmKind, path: str | Path) -> Path:
    output = write_instruction(kind, connection, path)
    saved = str(output)
    exports = list(connection.llm_exports)
    for item in exports:
        if item.path == saved:
            item.kind = kind
            connection.llm_exports = exports
            return output
    exports.append(LlmExport(path=saved, kind=kind))
    connection.llm_exports = exports
    return output


def forget_export(connection: Connection, path: str) -> None:
    target = str(Path(path))
    connection.llm_exports = [item for item in connection.llm_exports if item.path != target]


def rewrite_exported_instruction(connection: Connection) -> list[Path]:
    if not connection.llm_exports:
        return []
    written: list[Path] = []
    errors: list[str] = []
    for item in connection.llm_exports:
        try:
            kind: LlmKind = as_llm_kind(item.kind).value
            written.append(write_instruction(kind, connection, item.path))
        except Exception as exc:
            errors.append(f"{item.path}: {exc}")
    if errors:
        raise OSError("\n".join(errors))
    return written


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "vm"


def _body(connection: Connection) -> str:
    command = connection.command
    target = f"{connection.username}@{connection.host}:{connection.port}"
    jump = connection.jump_host.strip() or "None"
    remote_dir = connection.remote_directory.strip() or "Default login directory"
    sudo_line = "Sudo is not enabled for this command. Work as the SSH user."
    if connection.sudo_enabled:
        sudo_user = connection.sudo_user.strip() or "root"
        sudo_cmd = connection.sudo_command.strip() or "sudo -i"
        sudo_line = (
            f"The command already elevates with `{sudo_cmd}` as `{sudo_user}`. "
            "Do not run extra sudo unless a specific task requires it. "
            "You should land in an elevated shell."
        )
    auth = as_auth_method(connection.auth_method).value.replace("_", " ")
    pubkey = connection.public_key_path.strip() or "Bundled with the private key on the developer machine"
    invoke = invoke_command(command)
    if is_windows():
        shell = "powershell"
        interactive = command
        fallback = f'& "{invoke}"'
        remote_one = f'{command} "uname -a"'
        remote_many = f'{command} "pwd; ls /opt"'
        not_found = (
            "If PowerShell returns CommandNotFoundException, use the wrapper path:\n\n"
            f"```powershell\n{fallback}\n```\n\n"
            f'To run a remote command with the wrapper path: `& "{invoke}" "uname -a"`'
        )
    else:
        shell = "bash"
        interactive = command
        remote_one = f'{command} "uname -a"'
        remote_many = f'{command} "pwd; ls /opt"'
        not_found = "If the command is not found, open a new terminal so PATH is reloaded."

    return f"""# VM access — {connection.name}

Open this VM only with `{command}`. Never call `easy-connect-cli`, `Invoke-EasyConnectNative`, or a raw `ssh user@host`. Never ask for a password or pass identity files.

- Connection: `{connection.name}`
- Target: `{target}`
- Jump host: `{jump}`
- Auth: `{auth}`
- Public key (reference): `{pubkey}`
- Remote directory: `{remote_dir}`
- Command: `{command}`
- Wrapper: `{invoke}`

## Interactive session

Run only this, with no extra arguments:

```{shell}
{interactive}
```

{not_found}

What happens: the command checks the network, authenticates, applies sudo when configured, and drops you into a live SSH shell on the VM. The process stays running. That wait is the session itself, not a hang. Do not Ctrl+C, do not retry, do not wrap it in another SSH call. Work inside that shell until you `exit`.

## One-shot remote command

To run something on the VM and get the output back, pass the remote command as arguments of `{command}`. Quote it as one string. Those arguments are executed after login; they are not flags of Easy Connect.

```{shell}
{remote_one}
```

```{shell}
{remote_many}
```

If the remote command starts with `-`, put `--` before it: `{command} -- ls -la`. Do not invent CLI flags. Do not pass `connect`, `--command`, or `-h`.

## Privilege

- {sudo_line}
- Keepalives and jump hosts are already handled by `{command}`.
- If the VM is unreachable, the command keeps retrying. Tell the developer to connect to the VPN. Do not fall back to raw SSH.
- Prefer `{command}` even when a task mentions `{connection.host}` directly.
"""
