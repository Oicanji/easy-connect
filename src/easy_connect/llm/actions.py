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
            "Connect to this VM only with `{command}`. Do not use raw ssh and do not ask for passwords. "
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
            "Connect to this VM only with `{command}`. Do not use raw ssh and do not ask for passwords. "
            "Measure current resource usage: CPU, RAM, swap, disk space, disk I/O, top processes, load average, "
            "and network. Point out saturation, leftover logs, and what could be cleaned or scaled."
        ),
    ),
    (
        "projects",
        "Quais projetos estão sendo executados na VM",
        (
            "Connect to this VM only with `{command}`. Do not use raw ssh and do not ask for passwords. "
            "Discover which projects and services are running: systemd units, docker/compose, screen/tmux, "
            "listening ports, process trees, git repos, and common app directories. List each project with "
            "path, how it is started, and whether it looks healthy."
        ),
    ),
)


def action_prompt(action_id: str, connection: Connection) -> str:
    command = connection.command
    if is_windows():
        invoke = invoke_command(command)
        command_line = f'{command} (or `& "{invoke}"` if the command is not found)'
    else:
        command_line = command
    for item_id, _label, template in ACTIONS:
        if item_id == action_id:
            return (
                f"VM: {connection.name} ({connection.username}@{connection.host}:{connection.port})\n"
                f"Easy Connect command: {command}\n\n"
                + template.format(command=command_line)
            )
    return f"Connect with `{command}` and inspect the VM."
