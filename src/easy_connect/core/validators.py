from __future__ import annotations

import socket
import time


def check_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "ok"
    except socket.timeout:
        return False, f"Tempo esgotado ao conectar em {host}:{port}."
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
            return False, (
                "Não foi possível validar a VPN "
                f"({vpn_host}:{vpn_port}). Conecte-se à VPN e tente de novo."
            )
    ok, error = check_tcp(host, port, timeout)
    if not ok:
        return False, (
            "Não foi possível alcançar a VM. "
            "Conecte-se à VPN e tente de novo."
        )
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
                print("Rede disponível. Conectando...", flush=True)
            return
        print(message, flush=True)
        print(
            f"Tentativa {attempt}. Conecte-se à VPN. "
            f"Tentando de novo em {int(interval)}s... (Ctrl+C para cancelar)",
            flush=True,
        )
        time.sleep(interval)
        attempt += 1
