from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from easy_connect.core.commands import find_askpass, write_askpass_helper
from easy_connect.core.models import AuthMethod, Connection, as_auth_method
from easy_connect.core.paths import is_windows, tmp_dir


class SshError(Exception):
    pass


def find_ssh() -> str:
    found = shutil.which("ssh")
    if found:
        return found
    if is_windows():
        candidate = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "OpenSSH" / "ssh.exe"
        if candidate.is_file():
            return str(candidate)
    raise SshError(
        "O cliente OpenSSH não foi encontrado no PATH. "
        "Instale o OpenSSH e tente de novo."
    )


def cleanup_tmp(max_age_seconds: int = 3600) -> None:
    folder = tmp_dir()
    if not folder.is_dir():
        return
    now = time.time()
    for item in folder.glob("ec-*"):
        try:
            if now - item.stat().st_mtime > max_age_seconds:
                item.unlink()
        except OSError:
            pass


def connect(connection: Connection, remote_args: list[str] | None = None) -> None:
    cleanup_tmp()
    ssh = find_ssh()
    key_file: Path | None = None
    secret_file: Path | None = None
    env = os.environ.copy()
    args = [ssh]
    args.extend(["-o", "StrictHostKeyChecking=accept-new"])
    timeout = connection.connect_timeout or connection.validation_timeout or 10
    args.extend(["-o", f"ConnectTimeout={timeout}"])
    args.extend(["-p", str(connection.port)])
    if connection.keepalive > 0:
        args.extend(["-o", f"ServerAliveInterval={connection.keepalive}"])
        args.extend(["-o", "ServerAliveCountMax=3"])
    if connection.compression:
        args.append("-C")
    if connection.agent_forwarding:
        args.extend(["-o", "ForwardAgent=yes"])
    if connection.jump_host.strip():
        args.extend(["-J", connection.jump_host.strip()])

    method = as_auth_method(connection.auth_method)
    if method == AuthMethod.password:
        args.extend(["-o", "PreferredAuthentications=password"])
        args.extend(["-o", "PubkeyAuthentication=no"])
        secret_file = _write_secret(connection.password)
        _apply_askpass(env, secret_file)
    elif method == AuthMethod.private_key:
        key_file = _resolve_key_file(connection)
        args.extend(["-i", str(key_file)])
        args.extend(["-o", "IdentitiesOnly=yes"])
        args.extend(["-o", "PreferredAuthentications=publickey"])
        args.extend(["-o", "PasswordAuthentication=no"])
        cert = _certificate_file(connection)
        if cert:
            args.extend(["-o", f"CertificateFile={cert}"])
        if connection.private_key_passphrase:
            secret_file = _write_secret(connection.private_key_passphrase)
            _apply_askpass(env, secret_file)
    else:
        args.extend(["-o", "PreferredAuthentications=publickey"])
        args.extend(["-o", "PasswordAuthentication=no"])
        if connection.agent_forwarding:
            args.extend(["-o", "ForwardAgent=yes"])

    target = f"{connection.username}@{connection.host}"
    args.append(target)
    extra = list(remote_args or [])
    remote = _remote_command(connection, extra)
    prefix = None
    if remote:
        args.extend(["-tt", remote])
        if connection.sudo_enabled and connection.sudo_password:
            prefix = connection.sudo_password

    try:
        _run_ssh(ssh, args, env, prefix)
    finally:
        _cleanup(secret_file)
        if key_file and connection.private_key_content:
            _cleanup(key_file)


def _join_remote_args(extra: list[str]) -> str:
    cleaned = [str(item) for item in extra if str(item) != ""]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    return shlex.join(cleaned)


def _sudo_login(connection: Connection) -> str:
    user = connection.sudo_user.strip() or "root"
    command = connection.sudo_command.strip() or "sudo -i"
    if connection.sudo_password and "-S" not in command.split():
        if command in {"sudo -i", "sudo -s", "sudo su", "sudo su -"}:
            command = f"sudo -S -p '' -u {shlex.quote(user)} -i"
        else:
            command = command.replace("sudo", "sudo -S -p ''", 1)
    elif "sudo" in command and "-u" not in command.split() and user != "root":
        command = command.replace("sudo", f"sudo -u {shlex.quote(user)}", 1)
    return command


def _sudo_script(connection: Connection, script: str) -> str:
    user = connection.sudo_user.strip() or "root"
    quoted = shlex.quote(script)
    if connection.sudo_password:
        return f"sudo -S -p '' -u {shlex.quote(user)} bash -c {quoted}"
    return f"sudo -u {shlex.quote(user)} bash -c {quoted}"


def _interactive_shell() -> str:
    return "exec ${SHELL:-/bin/bash} -il"


def _remote_command(connection: Connection, extra: list[str] | None = None) -> str | None:
    extra_cmd = _join_remote_args(extra or [])
    directory = connection.remote_directory.strip()
    if extra_cmd:
        script = extra_cmd
        if directory:
            script = f"cd {shlex.quote(directory)} && {extra_cmd}"
        if connection.sudo_enabled:
            return _sudo_script(connection, script)
        if directory:
            return f"cd {shlex.quote(directory)} && bash -c {shlex.quote(extra_cmd)}"
        return extra_cmd
    parts: list[str] = []
    if directory:
        parts.append(f"cd {shlex.quote(directory)}")
    if connection.sudo_enabled:
        parts.append(_sudo_login(connection))
    elif directory:
        parts.append(_interactive_shell())
    if not parts:
        return None
    return " && ".join(parts)


def _certificate_file(connection: Connection) -> str | None:
    path = connection.public_key_path.strip()
    if not path:
        return None
    expanded = Path(path).expanduser()
    if expanded.is_file() and expanded.name.endswith("-cert.pub"):
        return str(expanded)
    return None


def _run_ssh(ssh: str, args: list[str], env: dict[str, str], stdin_prefix: str | None) -> None:
    if not stdin_prefix:
        completed = subprocess.run(args, env=env, check=False)
        raise SystemExit(completed.returncode)
    process = subprocess.Popen(
        args,
        env=env,
        stdin=subprocess.PIPE,
        stdout=None,
        stderr=None,
    )
    if process.stdin is None:
        raise SshError("Não foi possível enviar a senha do sudo.")
    process.stdin.write((stdin_prefix + "\n").encode("utf-8", errors="replace"))
    process.stdin.flush()

    def pump() -> None:
        try:
            while True:
                chunk = sys.stdin.buffer.read(1)
                if not chunk:
                    break
                process.stdin.write(chunk)
                process.stdin.flush()
        except Exception:
            pass
        try:
            process.stdin.close()
        except Exception:
            pass

    thread = threading.Thread(target=pump, daemon=True)
    thread.start()
    code = process.wait()
    raise SystemExit(code)


def _apply_askpass(env: dict[str, str], secret_file: Path) -> None:
    write_askpass_helper()
    askpass = find_askpass()
    if not askpass:
        raise SshError(
            "Não foi possível preparar o helper de senha SSH. "
            "Instale o Easy Connect neste Python com pip install -e ."
        )
    env["EASY_CONNECT_ASKPASS_FILE"] = str(secret_file)
    env["SSH_ASKPASS_REQUIRE"] = "force"
    env["DISPLAY"] = env.get("DISPLAY") or ":0"
    env["SSH_ASKPASS"] = askpass


def _write_secret(secret: str) -> Path:
    folder = tmp_dir()
    folder.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=folder,
        prefix="ec-",
        suffix=".tmp",
        delete=False,
    )
    with handle:
        handle.write(secret)
    path = Path(handle.name)
    if not is_windows():
        os.chmod(path, 0o600)
    return path


def _resolve_key_file(connection: Connection) -> Path:
    if connection.private_key_path.strip():
        path = Path(connection.private_key_path).expanduser()
        if not path.is_file():
            raise SshError(f"Arquivo de chave privada não encontrado: {path}")
        return path
    if connection.private_key_content.strip():
        return _write_secret(connection.private_key_content)
    raise SshError("Nenhuma chave privada foi configurada para esta conexão.")


def _cleanup(path: Path | None) -> None:
    if path is None:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
