from __future__ import annotations

import socket
import time

from easy_connect.i18n import t


def check_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "ok"
    except socket.timeout:
        return False, t("net.timeout", host=host, port=port)
    except OSError as exc:
        return False, str(exc)


def validate_connection(
    host: str,
    port: int,
    timeout: float,
    vpn_host: str = "",
    vpn_port: int = 443,
) -> tuple[bool, str]:
    if vpn_host.strip():
        ok, error = check_tcp(vpn_host.strip(), vpn_port, timeout)
        if not ok:
            return False, t("net.vpn", host=vpn_host, port=vpn_port)
    ok, error = check_tcp(host, port, timeout)
    if not ok:
        return False, t("net.vm")
    return True, "ok"


def wait_until_reachable(
    host: str,
    port: int,
    timeout: float,
    vpn_host: str = "",
    vpn_port: int = 443,
    interval: float = 3,
) -> None:
    attempt = 1
    while True:
        ok, message = validate_connection(
            host,
            port,
            timeout,
            vpn_host=vpn_host,
            vpn_port=vpn_port,
        )
        if ok:
            if attempt > 1:
                print(t("net.ready"), flush=True)
            return
        print(message, flush=True)
        print(
            t("net.retry", attempt=attempt, seconds=int(interval)),
            flush=True,
        )
        time.sleep(interval)
        attempt += 1
