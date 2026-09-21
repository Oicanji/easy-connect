from __future__ import annotations

import os
from base64 import b64decode, b64encode

from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

TIME_COST = 3
MEMORY_COST = 65536
PARALLELISM = 4
HASH_LEN = 32
SALT_LEN = 16
NONCE_LEN = 12


def new_salt() -> bytes:
    return os.urandom(SALT_LEN)


def derive_key(
    password: str,
    salt: bytes,
    time_cost: int = TIME_COST,
    memory_cost: int = MEMORY_COST,
    parallelism: int = PARALLELISM,
) -> bytes:
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=HASH_LEN,
        type=Type.ID,
    )


def encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(NONCE_LEN)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    return nonce, ciphertext


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    return AESGCM(key).decrypt(nonce, ciphertext, None)


def b64(data: bytes) -> str:
    return b64encode(data).decode("ascii")


def b64b(data: str) -> bytes:
    return b64decode(data.encode("ascii"))
