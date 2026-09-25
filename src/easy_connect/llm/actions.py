from __future__ import annotations

from easy_connect.core.commands import invoke_command
from easy_connect.core.models import Connection
from easy_connect.core.paths import is_windows
from easy_connect.i18n import t


TOOLS = (
    ("claude", "Claude Code"),
    ("cursor", "Cursor"),
    ("antigravity", "Antigravity"),
    ("codex", "Codex"),
)

ACTIONS = (
    (
        "structure",
        "Conectar e rastrear estrutura e especificações da VM",
        (
            "After you are in the shell, inspect the operating system, kernel, hostname, CPU, memory, disks, "
            "network interfaces, installed packages that identify the stack, important directories "
            "(/opt, /var/www, /home, /srv), systemd services, and summarize the VM structure and specifications "
            "in a clear report."
        ),
    ),
    (
        "resources",
        "Análise de uso e recursos da VM",
        (
            "Measure current resource usage: CPU, RAM, swap, disk space, disk I/O, top processes, load average, "
            "and network. Point out saturation, leftover logs, and what could be cleaned or scaled."
        ),
    ),
    (
        "projects",
        "Quais projetos estão sendo executados na VM",
        (
            "Discover which projects and services are running: systemd units, docker/compose, screen/tmux, "
            "listening ports, process trees, git repos, and common app directories. List each project with "
            "path, how it is started, and whether it looks healthy."
        ),
    ),
    (
        "docker_logs",
        "Pode buscar e baixar no meu downloads o log completo de hoje do docker/ou similar",
        (
            "Find today's complete logs for Docker containers, docker compose services, or similar "
            "container/runtime logs on the VM. Prefer full logs for the current day. Download or copy "
            "those log files into the local Downloads folder on this machine (the developer's PC). "
            "If Docker is absent, look for equivalent logs (podman, journalctl for container units, "
            "app log directories). Report what you saved and where."
        ),
    ),
    (
        "custom",
        "Escreva aqui...",
        "",
    ),
)


def action_menu_label(action_id: str) -> str:
    return t(f"agents.action.{action_id}")


def action_prompt(
    action_id: str,
    connection: Connection,
    custom_text: str = "",
    attachments: list[str] | None = None,
) -> str:
    command = connection.command
    target = f"{connection.name} ({connection.username}@{connection.host}:{connection.port})"
    prefix = (
        f"Start immediately. Do not ask what to do and do not wait for a follow-up. "
        f"The VM is {target}. Connect only with `{command}`"
    )
    if is_windows():
        wrapper = invoke_command(command)
        if wrapper and wrapper != command:
            prefix += f"; if that command is not found, run `{wrapper}`"
    prefix += ". Do not use raw ssh and do not ask for passwords. "
    body = ""
    if action_id == "custom":
        body = (custom_text or "").strip()
        if not body:
            body = "Inspect the VM and wait for further instructions only if something blocks you."
    else:
        for item_id, _label, template in ACTIONS:
            if item_id == action_id:
                body = template.format(command=command)
                break
        if not body:
            body = f"Inspect the VM with `{command}`."
    prompt = prefix + body
    files = [path.strip() for path in (attachments or []) if path.strip()]
    if files:
        listed = "\n".join(f"- `{path}`" for path in files)
        prompt += (
            " Local files attached by the developer (read them from this machine when useful):\n"
            f"{listed}"
        )
    return prompt
