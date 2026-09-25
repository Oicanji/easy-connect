from __future__ import annotations

import re
from pathlib import Path

from easy_connect.core.models import CommandRules, RuleAction
from easy_connect.core.paths import resource_base
from easy_connect.i18n import t


RULES: tuple[tuple[str, str], ...] = (
    ("read", "Comandos de leitura"),
    ("write", "Comandos de escrita"),
    ("delete", "Comandos de exclusão"),
    ("database_read", "Banco de dados ler"),
    ("database_write", "Banco de dados editar"),
    ("database_delete", "Banco de dados apagar"),
    ("credentials", "Buscar por credenciais"),
)

ACTIONS: tuple[tuple[RuleAction, str], ...] = (
    (RuleAction.allow, "Permitir"),
    (RuleAction.prompt, "Perguntar"),
    (RuleAction.deny, "Bloquear"),
)

ACTION_COLORS = {
    RuleAction.allow: "#3cba6a",
    RuleAction.prompt: "#e0b322",
    RuleAction.deny: "#e04b4b",
}

def rules_keywords_dir() -> Path:
    packaged = Path(__file__).resolve().parents[1] / "resources" / "rules"
    if packaged.is_dir():
        return packaged
    base = resource_base()
    for candidate in (
        base / "easy_connect" / "resources" / "rules",
        base / "resources" / "rules",
    ):
        if candidate.is_dir():
            return candidate
    return packaged


def load_keywords(rule_id: str) -> frozenset[str]:
    path = rules_keywords_dir() / f"{rule_id}.txt"
    if not path.is_file():
        return frozenset()
    words: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        word = line.split("#", 1)[0].strip().lower()
        if word:
            words.add(word)
    return frozenset(words)


def load_all_keywords() -> dict[str, frozenset[str]]:
    return {rule_id: load_keywords(rule_id) for rule_id, _label in RULES}


_SEVERITY = {
    RuleAction.allow: 0,
    RuleAction.prompt: 1,
    RuleAction.deny: 2,
}

def denial_text(rule_ids: list[str]) -> str:
    message = t("rules.denied")
    if not rule_ids:
        return message
    names = ", ".join(rule_label(rule_id) for rule_id in rule_ids)
    return t("rules.denied_with", message=message, names=names)


def rule_label(rule_id: str) -> str:
    for key, _label in RULES:
        if key == rule_id:
            return t(f"rules.{rule_id}")
    return rule_id


def action_label(action: RuleAction) -> str:
    return t(f"rules.action.{action.value}")


def dominant_action(rules: CommandRules) -> RuleAction:
    counts = {action: 0 for action, _label in ACTIONS}
    for rule_id, _label in RULES:
        counts[getattr(rules, rule_id)] += 1
    return max(counts, key=lambda action: (counts[action], _SEVERITY[action]))


def matched_rules(remote: list[str]) -> list[str]:
    tokens = set(re.findall(r"[a-z0-9_]+", " ".join(remote).lower()))
    if not tokens:
        return []
    keywords = load_all_keywords()
    found: list[str] = []
    for rule_id, _label in RULES:
        if tokens & keywords[rule_id]:
            found.append(rule_id)
    return found


def decide(rules: CommandRules, remote: list[str]) -> tuple[RuleAction, list[str]]:
    hits = matched_rules(remote)
    if not hits:
        return RuleAction.allow, []
    action = max((getattr(rules, rule_id) for rule_id in hits), key=lambda item: _SEVERITY[item])
    if action == RuleAction.allow:
        return RuleAction.allow, []
    blocking = [rule_id for rule_id in hits if getattr(rules, rule_id) == action]
    return action, blocking
