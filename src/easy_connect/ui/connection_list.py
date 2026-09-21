from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.integrations import launch_assistant, open_connected_terminal
from easy_connect.core.models import Connection
from easy_connect.core.session import AppSession
from easy_connect.llm.actions import ACTIONS, TOOLS, action_prompt
from easy_connect.ui.widgets import CopyRow, copy_to_clipboard


class ConnectionCard(QFrame):
    edit_requested = Signal(str)
    duplicate_requested = Signal(str)
    export_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self.setObjectName("ConnectionCard")
        self.connection = connection
        self.connection_id = connection.id
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()
        name = QLabel(connection.name)
        name.setObjectName("Title")
        name.setStyleSheet("font-size: 16px;")
        top.addWidget(name, 1)

        actions = QHBoxLayout()
        connect = QPushButton("Conectar")
        connect.setObjectName("Primary")
        connect.clicked.connect(self._connect)
        assist = QPushButton("Assistentes")
        assist.setObjectName("Ghost")
        assist.setMenu(self._assistants_menu())
        edit = QPushButton("Editar")
        edit.setObjectName("Ghost")
        edit.clicked.connect(lambda: self.edit_requested.emit(self.connection_id))
        duplicate = QPushButton("Duplicar")
        duplicate.setObjectName("Ghost")
        duplicate.clicked.connect(lambda: self.duplicate_requested.emit(self.connection_id))
        export = QPushButton("Exportar LLM")
        export.setObjectName("Ghost")
        export.clicked.connect(lambda: self.export_requested.emit(self.connection_id))
        delete = QPushButton("Excluir")
        delete.setObjectName("Danger")
        delete.clicked.connect(lambda: self.delete_requested.emit(self.connection_id))
        actions.addWidget(connect)
        actions.addWidget(assist)
        actions.addWidget(edit)
        actions.addWidget(duplicate)
        actions.addWidget(export)
        actions.addWidget(delete)
        actions.addStretch()

        target = CopyRow(f"{connection.username}@{connection.host}:{connection.port}")
        target.label.setObjectName("Subtitle")
        command = CopyRow(connection.command)

        layout.addLayout(top)
        layout.addLayout(actions)
        layout.addWidget(target)
        layout.addWidget(command)
        for item in connection.llm_exports:
            exported = CopyRow(item.path)
            exported.label.setWordWrap(True)
            layout.addWidget(exported)

    def _assistants_menu(self) -> QMenu:
        menu = QMenu(self)
        for tool_id, tool_label in TOOLS:
            submenu = menu.addMenu(tool_label)
            for action_id, action_label, _prompt in ACTIONS:
                action = submenu.addAction(action_label)
                action.triggered.connect(
                    lambda *_args, t=tool_id, a=action_id: self._assist(t, a)
                )
        return menu

    def _connect(self) -> None:
        try:
            open_connected_terminal(self.connection.command)
        except Exception as exc:
            QMessageBox.warning(self, "Easy Connect", str(exc))

    def _assist(self, tool: str, action_id: str) -> None:
        try:
            copy_to_clipboard(action_prompt(action_id, self.connection))
            message = launch_assistant(tool, action_id, self.connection)
            QMessageBox.information(self, "Easy Connect", message)
        except Exception as exc:
            QMessageBox.warning(self, "Easy Connect", str(exc))


class ConnectionList(QWidget):
    add_requested = Signal()
    edit_requested = Signal(str)
    duplicate_requested = Signal(str)
    export_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, session: AppSession) -> None:
        super().__init__()
        self.session = session
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 20)
        root.setSpacing(12)

        header = QLabel("CONEXÕES")
        header.setObjectName("Section")
        root.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(self.scroll, 1)

        self.add_button = QPushButton("Adicionar conexão")
        self.add_button.setObjectName("Primary")
        self.add_button.clicked.connect(self.add_requested.emit)
        root.addWidget(self.add_button)

        self.reload()

    def reload(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(10)
        connections = list(self.session.payload.connections)
        if not connections:
            empty = QLabel(
                "Nenhuma conexão ainda. Adicione a primeira para gerar um comando global no terminal."
            )
            empty.setObjectName("Subtitle")
            empty.setWordWrap(True)
            layout.addWidget(empty)
        for connection in connections:
            card = ConnectionCard(connection)
            card.edit_requested.connect(self.edit_requested.emit)
            card.duplicate_requested.connect(self.duplicate_requested.emit)
            card.export_requested.connect(self.export_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)
            layout.addWidget(card)
        layout.addStretch()
        self.scroll.setWidget(container)
