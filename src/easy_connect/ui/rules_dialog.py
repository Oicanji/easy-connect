from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from easy_connect.core.models import CommandRules, Connection, RuleAction
from easy_connect.core.rule_session import SESSION_ALLOW_CODE
from easy_connect.core.rules import decide, rule_label
from easy_connect.core.session import AppSession
from easy_connect.i18n import t
from easy_connect.ui.rules_panel import RulesPanel
from easy_connect.ui.styles import apply_app_icon


class RulesDialog(QDialog):
    def __init__(self, connection: Connection, parent=None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle(t("rules.window"))
        self.setModal(True)
        self.setMinimumWidth(1080)
        apply_app_icon(self)
        self._build()

    def rules(self) -> CommandRules:
        return self.panel.rules()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        title = QLabel(t("rules.title"))
        title.setObjectName("Title")
        title.setStyleSheet("font-size: 18px;")
        hint = QLabel(t("rules.hint"))
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        self.panel = RulesPanel(self.connection.rules)
        columns = QLabel(t("dialog.rules_columns"))
        columns.setObjectName("Hint")
        columns.setWordWrap(True)

        cancel = QPushButton(t("dialog.cancel"))
        cancel.clicked.connect(self.reject)
        save = QPushButton(t("rules.save"))
        save.setObjectName("Primary")
        save.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(save)

        root.addWidget(title)
        root.addWidget(hint)
        root.addWidget(self.panel)
        root.addWidget(columns)
        root.addLayout(buttons)


class RulePromptDialog(QDialog):
    def __init__(self, connection: Connection, remote: list[str], rule_ids: list[str]) -> None:
        super().__init__()
        self.choice = "deny"
        self.setWindowTitle("Easy Connect")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumWidth(640)
        apply_app_icon(self)
        self._build(connection, remote, rule_ids)

    def _build(self, connection: Connection, remote: list[str], rule_ids: list[str]) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 18)
        root.setSpacing(12)

        title = QLabel(t("prompt.title"))
        title.setObjectName("Title")
        title.setStyleSheet("font-size: 18px;")
        names = ", ".join(rule_label(rule_id) for rule_id in rule_ids)
        message = QLabel(t("prompt.message", name=connection.name, names=names))
        message.setObjectName("Subtitle")
        message.setWordWrap(True)
        command = QLabel(" ".join(remote))
        command.setObjectName("Hint")
        command.setWordWrap(True)
        command.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        deny = QPushButton(t("prompt.deny"))
        deny.clicked.connect(self.reject)
        allow_all = QPushButton(t("prompt.allow_session"))
        allow_all.clicked.connect(self._allow_session)
        allow = QPushButton(t("prompt.allow"))
        allow.setObjectName("Primary")
        allow.clicked.connect(self._allow)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(deny)
        buttons.addWidget(allow_all)
        buttons.addWidget(allow)

        root.addWidget(title)
        root.addWidget(message)
        root.addWidget(command)
        root.addLayout(buttons)

    def _allow(self) -> None:
        self.choice = "once"
        self.accept()

    def _allow_session(self) -> None:
        self.choice = "session"
        self.accept()


def run_rule_prompt(session: AppSession, command: str, remote: list[str]) -> int:
    connection = session.find_by_command(command)
    if connection is None:
        return 1
    action, rule_ids = decide(connection.rules, remote)
    if action == RuleAction.allow:
        return 0
    if action == RuleAction.deny:
        return 1
    dialog = RulePromptDialog(connection, remote, rule_ids)
    dialog.exec()
    if dialog.choice == "session":
        return SESSION_ALLOW_CODE
    if dialog.choice == "once":
        return 0
    return 1
