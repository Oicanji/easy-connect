from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuthMethod(str, Enum):
    password = "password"
    private_key = "private_key"
    agent = "agent"


class LlmTarget(str, Enum):
    claude = "claude"
    cursor = "cursor"
    antigravity = "antigravity"


def as_auth_method(value: AuthMethod | str) -> AuthMethod:
    if isinstance(value, AuthMethod):
        return value
    return AuthMethod(str(value))


def as_llm_kind(value: LlmTarget | str | None) -> LlmTarget:
    if isinstance(value, LlmTarget):
        return value
    text = str(value or "").strip()
    for item in LlmTarget:
        if item.value == text:
            return item
    return LlmTarget.cursor


class LlmExport(BaseModel):
    path: str
    kind: str = "cursor"


class Connection(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    host: str
    port: int = 22
    username: str
    auth_method: AuthMethod = AuthMethod.password
    password: str = ""
    private_key_path: str = ""
    private_key_content: str = ""
    private_key_passphrase: str = ""
    jump_host: str = ""
    command: str
    validation_timeout: int = 10
    connect_timeout: int = 10
    keepalive: int = 30
    compression: bool = False
    agent_forwarding: bool = False
    remote_directory: str = ""
    public_key_path: str = ""
    sudo_enabled: bool = False
    sudo_user: str = "root"
    sudo_password: str = ""
    sudo_command: str = "sudo -i"
    os_info: str = ""
    has_docker: bool = False
    docker_container: str = ""
    notes: str = ""
    llm_exports: list[LlmExport] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @model_validator(mode="before")
    @classmethod
    def _migrate_llm_export(cls, data):
        if not isinstance(data, dict):
            return data
        exports = list(data.get("llm_exports") or [])
        old_path = str(data.pop("llm_export_path", "") or "").strip()
        old_kind = str(data.pop("llm_export_kind", "") or "").strip()
        if old_path:
            known = set()
            for item in exports:
                if isinstance(item, dict):
                    known.add(str(item.get("path") or "").strip())
                else:
                    known.add(str(getattr(item, "path", "")).strip())
            if old_path not in known:
                exports.append({"path": old_path, "kind": old_kind or "cursor"})
        data["llm_exports"] = exports
        return data


class AppSettings(BaseModel):
    default_validation_timeout: int = 10
    vpn_check_host: str = ""
    vpn_check_port: int = 443
    theme: str = "dark"
    path_installed: bool = False


class VaultPayload(BaseModel):
    connections: list[Connection] = Field(default_factory=list)
    settings: AppSettings = Field(default_factory=AppSettings)
