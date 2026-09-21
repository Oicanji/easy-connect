from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.integrations import launch_assistant, open_connected_terminal
from easy_connect.core.models import Connection
from easy_connect.core.session import AppSession
from easy_connect.llm.actions import ACTIONS, TOOLS
from easy_connect.ui.agent_prompt_dialog import AgentPromptDialog
from easy_connect.ui.widgets import (
    CopyRow,
    close_icon,
    document_icon,
    pencil_icon,
    plus_icon,
    robot_icon,
)


class ConnectionCard(QFrame):
    edit_requested = Signal(str)
    duplicate_requested = Signal(str)
    export_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, connection: Connection, session: AppSession) -> None:
        super().__init__()
        self.setObjectName("ConnectionCard")
        self.connection = connection
        self.session = session
        self.connection_id = connection.id
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        name = QLabel(connection.name)
        name.setObjectName("Title")
        name.setStyleSheet("font-size: 16px;")
        duplicate = QPushButton()
        duplicate.setObjectName("Plus")
        duplicate.setIcon(plus_icon())
        duplicate.setToolTip("Duplicar")
        duplicate.clicked.connect(lambda: self.duplicate_requested.emit(self.connection_id))
        connect = QPushButton("Conectar")
        connect.setObjectName("Primary")
        connect.clicked.connect(self._connect)
        top.addWidget(name, 1)
        top.addWidget(duplicate, 0, Qt.AlignmentFlag.AlignVCenter)
        top.addWidget(connect, 0, Qt.AlignmentFlag.AlignVCenter)

        tools = QHBoxLayout()
        tools.setContentsMargins(0, 0, 0, 0)
        tools.setSpacing(8)
        target = QLabel(f"{connection.username}@{connection.host}:{connection.port}")
        target.setObjectName("Subtitle")
        agents = QToolButton()
        agents.setObjectName("Ghost")
        agents.setText(" Agentes")
        agents.setIcon(robot_icon())
        agents.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        agents.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        agents.setMenu(self._agents_menu())
        export = QPushButton(" Exportar regra")
        export.setObjectName("Ghost")
        export.setIcon(document_icon())
        export.clicked.connect(lambda: self.export_requested.emit(self.connection_id))
        tools.addWidget(target, 1)
        tools.addWidget(agents, 0, Qt.AlignmentFlag.AlignVCenter)
        tools.addWidget(export, 0, Qt.AlignmentFlag.AlignVCenter)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 0, 0)
        footer.setSpacing(8)
        delete = QPushButton(" Excluir")
        delete.setObjectName("DangerGhost")
        delete.setIcon(close_icon())
        delete.clicked.connect(lambda: self.delete_requested.emit(self.connection_id))
        edit = QPushButton(" Editar")
        edit.setObjectName("EditLink")
        edit.setIcon(pencil_icon())
        edit.clicked.connect(lambda: self.edit_requested.emit(self.connection_id))
        footer.addWidget(delete, 0, Qt.AlignmentFlag.AlignLeft)
        footer.addWidget(edit, 0, Qt.AlignmentFlag.AlignLeft)
        footer.addStretch()

        layout.addLayout(top)
        layout.addLayout(tools)
        command = CopyRow(connection.command)
        layout.addWidget(command)
        for item in connection.llm_exports:
            exported = CopyRow(item.path)
            layout.addWidget(exported)
        layout.addLayout(footer)

    def _agents_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.setObjectName("AgentsMenu")
        for tool_id, tool_label in TOOLS:
            submenu = menu.addMenu(tool_label)
            submenu.setObjectName("AgentsMenu")
            for action_id, action_label, _prompt in ACTIONS:
                item = submenu.addAction(action_label)
                item.triggered.connect(
                    lambda _checked=False, t=tool_id, a=action_id: self._assist(t, a)
                )
        return menu

    def _connect(self) -> None:
        try:
            open_connected_terminal(self.connection.command)
        except Exception as exc:
            QMessageBox.warning(self, "Easy Connect", str(exc))

    def _assist(
        self,
        tool: str,
        action_id: str,
        custom_prompt: str = "",
        attachments: list[str] | None = None,
    ) -> None:
        try:
            if action_id == "custom" and not custom_prompt and not attachments:
                dialog = AgentPromptDialog(tool, self.connection, self)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                custom_prompt = dialog.prompt_text()
                attachments = dialog.attachments()
            configured = str(self.session.payload.settings.agent_paths.get(tool) or "")
            message = launch_assistant(
                tool,
                action_id,
                self.connection,
                configured,
                custom_prompt=custom_prompt,
                attachments=attachments,
            )
            if message:
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
        layout.setSpacing(8)
        connections = list(self.session.payload.connections)
        if not connections:
            empty = QLabel(
                "Nenhuma conexão ainda. Adicione a primeira para gerar um comando global no terminal."
            )
            empty.setObjectName("Subtitle")
            empty.setWordWrap(True)
            layout.addWidget(empty)
        for connection in connections:
            card = ConnectionCard(connection, self.session)
            card.edit_requested.connect(self.edit_requested.emit)
            card.duplicate_requested.connect(self.duplicate_requested.emit)
            card.export_requested.connect(self.export_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)
            layout.addWidget(card)
        layout.addStretch()
        self.scroll.setWidget(container)
