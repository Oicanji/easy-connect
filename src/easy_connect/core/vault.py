from __future__ import annotations

import json
from pathlib import Path

from easy_connect.core import crypto
from easy_connect.core.models import VaultPayload
from easy_connect.core.paths import ensure_app_dirs, vault_path


class VaultError(Exception):
    pass


class WrongPasswordError(VaultError):
    pass


class VaultNotFoundError(VaultError):
    pass


class Vault:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or vault_path()

    def exists(self) -> bool:
        return self.path.is_file()

    def create(self, password: str) -> bytes:
        if len(password) < 8:
            raise VaultError("A senha deve ter pelo menos 8 caracteres.")
        ensure_app_dirs()
        salt = crypto.new_salt()
        key = crypto.derive_key(password, salt)
        payload = VaultPayload()
        self._write(key, salt, payload)
        return key

    def unlock(self, password: str) -> bytes:
        header = self._read_header()
        key = crypto.derive_key(
            password,
            crypto.b64b(header["salt"]),
            time_cost=int(header["time_cost"]),
            memory_cost=int(header["memory_cost"]),
            parallelism=int(header["parallelism"]),
        )
        try:
            self.load(key)
        except Exception as exc:
            raise WrongPasswordError("Senha incorreta.") from exc
        return key

    def load(self, key: bytes) -> VaultPayload:
        header = self._read_header()
        plaintext = crypto.decrypt(
            key,
            crypto.b64b(header["nonce"]),
            crypto.b64b(header["ciphertext"]),
        )
        return VaultPayload.model_validate_json(plaintext)

    def save(self, key: bytes, payload: VaultPayload) -> None:
        header = self._read_header()
        salt = crypto.b64b(header["salt"])
        self._write(key, salt, payload, header)

    def _read_header(self) -> dict:
        if not self.path.is_file():
            raise VaultNotFoundError("Cofre não encontrado.")
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(
        self,
        key: bytes,
        salt: bytes,
        payload: VaultPayload,
        header: dict | None = None,
    ) -> None:
        ensure_app_dirs()
        nonce, ciphertext = crypto.encrypt(
            key,
            payload.model_dump_json().encode("utf-8"),
        )
        data = {
            "version": 1,
            "kdf": "argon2id",
            "salt": crypto.b64(salt),
            "time_cost": (header or {}).get("time_cost", crypto.TIME_COST),
            "memory_cost": (header or {}).get("memory_cost", crypto.MEMORY_COST),
            "parallelism": (header or {}).get("parallelism", crypto.PARALLELISM),
            "nonce": crypto.b64(nonce),
            "ciphertext": crypto.b64(ciphertext),
        }
        self.path.write_text(json.dumps(data), encoding="utf-8")
