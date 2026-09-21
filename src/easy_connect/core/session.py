from __future__ import annotations

from datetime import datetime, timezone

from easy_connect.core import keyring_store
from easy_connect.core.models import Connection, VaultPayload
from easy_connect.core.vault import Vault


class AppSession:
    def __init__(self, key: bytes, payload: VaultPayload, vault: Vault | None = None) -> None:
        self.key = key
        self.payload = payload
        self.vault = vault or Vault()

    def save(self) -> None:
        self.vault.save(self.key, self.payload)

    def persist_unlock(self) -> None:
        keyring_store.save_key(self.key)

    def lock(self) -> None:
        keyring_store.clear_key()

    @classmethod
    def resume(cls) -> AppSession | None:
        key = keyring_store.load_key()
        if key is None:
            return None
        vault = Vault()
        try:
            payload = vault.load(key)
        except Exception:
            keyring_store.clear_key()
            return None
        return cls(key, payload, vault)

    def find_by_id(self, connection_id: str) -> Connection | None:
        for item in self.payload.connections:
            if item.id == connection_id:
                return item
        return None

    def find_by_command(self, command: str) -> Connection | None:
        for item in self.payload.connections:
            if item.command == command:
                return item
        return None

    def upsert(self, connection: Connection) -> None:
        connection.updated_at = datetime.now(timezone.utc).isoformat()
        items = self.payload.connections
        for index, item in enumerate(items):
            if item.id == connection.id:
                items[index] = connection
                return
        items.append(connection)

    def remove(self, connection_id: str) -> Connection | None:
        items = self.payload.connections
        for index, item in enumerate(items):
            if item.id == connection_id:
                return items.pop(index)
        return None

    def command_taken(self, command: str, ignore_id: str | None = None) -> bool:
        for item in self.payload.connections:
            if item.command == command and item.id != ignore_id:
                return True
        return False
