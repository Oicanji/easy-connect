from __future__ import annotations

import argparse
import subprocess
import sys
import time

from easy_connect.core import keyring_store
from easy_connect.core.models import RuleAction
from easy_connect.core.paths import gui_disabled_connection_args, gui_rule_prompt_args, gui_unlock_args
from easy_connect.core.rule_session import SESSION_ALLOW_CODE, remember_terminal, terminal_allows
from easy_connect.core.rules import decide, denial_text
from easy_connect.core.ssh import SshError, connect
from easy_connect.core.validators import wait_until_reachable
from easy_connect.core.vault import Vault, VaultNotFoundError
from easy_connect.i18n import load_language, t


def askpass_main() -> None:
    raise SystemExit(_askpass())


def main(argv: list[str] | None = None) -> int:
    load_language()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(prog="easy-connect-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    connect_parser = sub.add_parser("connect", help="Open a saved SSH connection")
    connect_parser.add_argument("--command", required=True)
    connect_parser.add_argument(
        "remote",
        nargs=argparse.REMAINDER,
        default=[],
        help="Command to run on the remote host after connecting",
    )
    sub.add_parser("askpass", help="Internal SSH askpass helper")
    args = parser.parse_args(argv)

    if args.cmd == "askpass":
        return _askpass()
    remote = [item for item in (args.remote or []) if item != "--"]
    return _connect(args.command, remote)


def _askpass() -> int:
    import os
    from pathlib import Path

    path = os.environ.get("EASY_CONNECT_ASKPASS_FILE", "")
    if not path:
        return 1
    secret_path = Path(path)
    if not secret_path.is_file():
        return 1
    sys.stdout.write(secret_path.read_text(encoding="utf-8"))
    sys.stdout.flush()
    return 0


def _ensure_key() -> bytes | None:
    key = keyring_store.load_key()
    if key is not None:
        return key
    print(t("cli.locked"), flush=True)
    try:
        completed = subprocess.run(gui_unlock_args(), check=False)
    except OSError as exc:
        print(t("cli.unlock_failed", error=exc), file=sys.stderr)
        return None
    if completed.returncode not in {0, None}:
        print(t("cli.login_cancelled"), file=sys.stderr)
        return None
    key = keyring_store.load_key()
    if key is None:
        print(t("cli.still_locked"), file=sys.stderr)
    return key


def _prompt_disabled(connection) -> bool:
    if connection.hide_disabled_prompt:
        return False
    print(t("cli.disabled_opening"), flush=True)
    try:
        completed = subprocess.run(
            gui_disabled_connection_args(connection.command),
            check=False,
        )
    except OSError as exc:
        print(t("cli.open_failed", error=exc), file=sys.stderr)
        return False
    return completed.returncode == 0


def _prompt_rules(command: str, remote: list[str]) -> int:
    try:
        completed = subprocess.run(gui_rule_prompt_args(command, remote), check=False)
    except OSError as exc:
        print(t("cli.permission_failed", error=exc), file=sys.stderr)
        return 1
    return completed.returncode


def _connect(command: str, remote: list[str] | None = None) -> int:
    print(t("cli.checking_network"), flush=True)
    key = _ensure_key()
    if key is None:
        return 2

    vault = Vault()
    try:
        payload = vault.load(key)
    except VaultNotFoundError:
        print(t("cli.vault_missing"), file=sys.stderr)
        return 2
    except Exception:
        print(t("cli.vault_unreadable"), file=sys.stderr)
        return 2

    connection = None
    for item in payload.connections:
        if item.command == command:
            connection = item
            break
    if connection is None:
        print(t("cli.connection_missing", command=command), file=sys.stderr)
        return 1

    if not connection.enabled:
        allowed = _prompt_disabled(connection)
        if not allowed:
            print(t("cli.denied"), file=sys.stderr)
            return 1
        try:
            payload = vault.load(key)
        except Exception:
            print(t("cli.denied"), file=sys.stderr)
            return 1
        connection = None
        for item in payload.connections:
            if item.command == command:
                connection = item
                break
        if connection is None or not connection.enabled:
            print(t("cli.denied"), file=sys.stderr)
            return 1

    if remote:
        action, rule_ids = decide(connection.rules, remote)
        if action == RuleAction.deny:
            print(denial_text(rule_ids), file=sys.stderr)
            return 1
        if action == RuleAction.prompt and not terminal_allows():
            answer = _prompt_rules(connection.command, remote)
            if answer == SESSION_ALLOW_CODE:
                remember_terminal()
            elif answer != 0:
                print(denial_text(rule_ids), file=sys.stderr)
                return 1

    timeout = connection.validation_timeout or payload.settings.default_validation_timeout
    try:
        while True:
            print(t("cli.checking_host", host=connection.host, port=connection.port), flush=True)
            wait_until_reachable(
                connection.host,
                connection.port,
                timeout,
                vpn_host=payload.settings.vpn_check_host,
                vpn_port=payload.settings.vpn_check_port,
            )
            print(t("cli.connecting"), flush=True)
            try:
                connect(connection, remote)
            except SshError as exc:
                print(str(exc), flush=True)
                print(t("cli.ssh_retry"), flush=True)
                time.sleep(3)
                continue
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                if code == 0:
                    return 0
                if remote and code != 255:
                    return code
                print(t("cli.vm_retry"), flush=True)
                time.sleep(3)
    except KeyboardInterrupt:
        print(t("cli.cancelled"), flush=True)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
