from __future__ import annotations

from easy_connect.core.commands import invoke_command
from easy_connect.core.models import Connection
from easy_connect.core.paths import is_windows


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
)


def action_prompt(action_id: str, connection: Connection) -> str:
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
    for item_id, _label, template in ACTIONS:
        if item_id == action_id:
            return prefix + template.format(command=command)
    return prefix + f"Inspect the VM with `{command}`."
