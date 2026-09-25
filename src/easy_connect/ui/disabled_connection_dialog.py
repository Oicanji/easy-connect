from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from easy_connect.core.models import Connection
from easy_connect.core.session import AppSession
from easy_connect.i18n import t
from easy_connect.ui.styles import apply_app_icon

DENIED_EXIT = 3


class DisabledConnectionDialog(QDialog):
    def __init__(self, connection: Connection, parent=None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.choice = "cancel"
        self.setWindowTitle("Easy Connect")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        apply_app_icon(self)
        self.setMinimumWidth(420)
        self._build()

    def dont_show_again(self) -> bool:
        return self.again.isChecked()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 18)
        root.setSpacing(14)

        title = QLabel(t("disabled.title"))
        title.setObjectName("Title")
        title.setStyleSheet("font-size: 18px;")
        message = QLabel(
            t("disabled.message", name=self.connection.name, command=self.connection.command)
        )
        message.setObjectName("Subtitle")
        message.setWordWrap(True)

        self.again = QCheckBox(t("disabled.again"))
        self.again.setChecked(True)

        deny = QPushButton(t("disabled.ok"))
        deny.clicked.connect(self._deny)
        enable = QPushButton(t("disabled.enable"))
        enable.setObjectName("Primary")
        enable.clicked.connect(self._enable)
        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addStretch()
        buttons.addWidget(deny)
        buttons.addWidget(enable)

        root.addWidget(title)
        root.addWidget(message)
        root.addWidget(self.again)
        root.addLayout(buttons)

    def _deny(self) -> None:
        self.choice = "deny"
        self.accept()

    def _enable(self) -> None:
        self.choice = "enable"
        self.accept()

    def reject(self) -> None:
        self.choice = "cancel"
        super().reject()


def run_disabled_prompt(session: AppSession, command: str) -> int:
    connection = session.find_by_command(command)
    if connection is None:
        return 1
    if connection.enabled:
        return 0
    dialog = DisabledConnectionDialog(connection)
    dialog.exec()
    if dialog.choice == "enable":
        connection.enabled = True
        connection.hide_disabled_prompt = False
        session.upsert(connection)
        session.save()
        return 0
    if dialog.choice == "deny" and dialog.dont_show_again():
        connection.hide_disabled_prompt = True
        session.upsert(connection)
        session.save()
    return DENIED_EXIT
