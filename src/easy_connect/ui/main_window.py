from __future__ import annotations

from uuid import uuid4

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from easy_connect import __version__, app_title
from easy_connect.core.commands import (
    install_wrapper,
    next_available_command,
    remove_wrapper,
)
from easy_connect.core.models import Connection
from easy_connect.core.session import AppSession
from easy_connect.llm.templates import rewrite_exported_instruction
from easy_connect.ui.connection_dialog import ConnectionDialog
from easy_connect.ui.connection_list import ConnectionList
from easy_connect.ui.export_dialog import ExportDialog
from easy_connect.ui.settings_tab import SettingsTab
from easy_connect.ui.styles import apply_app_icon


class MainWindow(QMainWindow):
    locked = Signal()

    def __init__(self, session: AppSession) -> None:
        super().__init__()
        self.session = session
        self.setWindowTitle(app_title())
        apply_app_icon(self)
        self.resize(980, 680)
        self._build()
        QShortcut(QKeySequence("Ctrl+L"), self, self._lock)
        QShortcut(QKeySequence("Ctrl+N"), self, self._add)

    def _build(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 12)
        title = QLabel("Easy Connect")
        title.setObjectName("Title")
        version = QLabel(f"v{__version__}")
        version.setObjectName("Subtitle")
        subtitle = QLabel("Acesso automatizado e seguro às VMs, com regras e integrações LLM")
        subtitle.setObjectName("Subtitle")
        titles = QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(title)
        titles.addWidget(version)
        titles.addWidget(subtitle)
        header_layout.addLayout(titles, 1)
        lock = QPushButton("Bloquear")
        lock.clicked.connect(self._lock)
        header_layout.addWidget(lock, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.list_tab = ConnectionList(self.session)
        self.list_tab.add_requested.connect(self._add)
        self.list_tab.edit_requested.connect(self._edit)
        self.list_tab.duplicate_requested.connect(self._duplicate)
        self.list_tab.export_requested.connect(self._export)
        self.list_tab.delete_requested.connect(self._delete)
        self.settings_tab = SettingsTab(self.session)
        self.tabs.addTab(self.list_tab, "Conexões")
        self.tabs.addTab(self.settings_tab, "Configurações")
        layout.addWidget(self.tabs, 1)
        credit = QLabel("Ignacio Sepúlveda")
        credit.setObjectName("Credit")
        credit.setAlignment(Qt.AlignmentFlag.AlignRight)
        credit.setContentsMargins(24, 4, 24, 14)
        layout.addWidget(credit)
        self.setCentralWidget(container)

    def _add(self) -> None:
        dialog = ConnectionDialog(self.session)
        if dialog.exec() and dialog.result_connection:
            self._persist(dialog.result_connection, previous_command=None)

    def _edit(self, connection_id: str) -> None:
        connection = self.session.find_by_id(connection_id)
        if connection is None:
            return
        previous = connection.command
        dialog = ConnectionDialog(self.session, connection)
        if dialog.exec() and dialog.result_connection:
            self._persist(dialog.result_connection, previous_command=previous)

    def _duplicate(self, connection_id: str) -> None:
        connection = self.session.find_by_id(connection_id)
        if connection is None:
            return
        copy = connection.model_copy(deep=True)
        copy.id = uuid4().hex
        copy.name = f"{connection.name} (cópia)"
        copy.llm_exports = []
        def taken(command: str) -> bool:
            return self.session.command_taken(command)
        copy.command = next_available_command(connection.command, taken)
        dialog = ConnectionDialog(self.session, copy)
        if dialog.exec() and dialog.result_connection:
            self._persist(dialog.result_connection, previous_command=None)

    def _export(self, connection_id: str) -> None:
        connection = self.session.find_by_id(connection_id)
        if connection is None:
            return
        dialog = ExportDialog(connection, self)
        dialog.exec()
        self.session.save()
        self.list_tab.reload()
        count = len(connection.llm_exports)
        if count:
            self.statusBar().showMessage(
                f"{count} arquivo(s) de instrução vinculados.",
                5000,
            )

    def _delete(self, connection_id: str) -> None:
        connection = self.session.find_by_id(connection_id)
        if connection is None:
            return
        answer = QMessageBox.question(
            self,
            "Excluir conexão",
            f"Excluir '{connection.name}' e o comando {connection.command}?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.session.remove(connection_id)
        remove_wrapper(connection.command)
        self.session.save()
        self.list_tab.reload()
        self.statusBar().showMessage("Conexão excluída.", 4000)

    def _persist(self, connection: Connection, previous_command: str | None) -> None:
        if previous_command and previous_command != connection.command:
            remove_wrapper(previous_command)
        self.session.upsert(connection)
        install_wrapper(connection.command)
        self.session.payload.settings.path_installed = True
        self.session.save()
        rewritten = self._rewrite_instruction(connection)
        self.list_tab.reload()
        message = f"Comando {connection.command} pronto."
        if rewritten:
            message = f"Comando {connection.command} pronto. Instruções da LLM atualizadas."
        self.statusBar().showMessage(message, 5000)

    def _rewrite_instruction(self, connection: Connection) -> bool:
        try:
            return bool(rewrite_exported_instruction(connection))
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Easy Connect",
                f"A conexão foi salva, mas a instrução da LLM não pôde ser atualizada:\n{exc}",
            )
            return False

    def _lock(self) -> None:
        self.session.lock()
        self.locked.emit()
        self.close()
