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
from easy_connect.core.rules import ACTION_COLORS, action_label, dominant_action
from easy_connect.core.session import AppSession
from easy_connect.i18n import t
from easy_connect.llm.actions import ACTIONS, TOOLS, action_menu_label
from easy_connect.ui.agent_prompt_dialog import AgentPromptDialog
from easy_connect.ui.disabled_connection_dialog import DisabledConnectionDialog
from easy_connect.ui.icon_picker import card_icon
from easy_connect.ui.rules_dialog import RulesDialog
from easy_connect.ui.widgets import (
    CopyRow,
    close_icon,
    document_icon,
    duplicate_icon,
    pencil_icon,
    robot_icon,
    ToggleSwitch,
)


class RulesButton(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.button = QPushButton(t("list.rules"), self)
        self.button.setObjectName("RulesLink")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dot = QLabel(self)
        self.dot.setFixedSize(8, 8)
        self.dot.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._layout_children()

    def _layout_children(self) -> None:
        hint = self.button.sizeHint()
        self.setFixedSize(hint.width(), hint.height())
        self.button.setGeometry(0, 0, hint.width(), hint.height())
        self.dot.move(max(0, hint.width() - 14), 3)
        self.dot.raise_()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._layout_children()


class ConnectionCard(QFrame):
    edit_requested = Signal(str)
    duplicate_requested = Signal(str)
    export_requested = Signal(str)
    delete_requested = Signal(str)
    enabled_changed = Signal(str, bool)

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
        icon = QLabel()
        icon.setPixmap(card_icon(connection.icon))
        icon.setFixedSize(32, 32)
        icon.setStyleSheet("background: transparent;")
        top.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)
        name = QLabel(connection.name)
        name.setObjectName("Title")
        name.setStyleSheet("font-size: 16px;")
        connect = QPushButton(t("list.connect"))
        connect.setObjectName("Primary")
        connect.clicked.connect(self._connect)
        self.rules_button = RulesButton()
        self.rules_button.button.clicked.connect(self._edit_rules)
        self.rule_dot = self.rules_button.dot
        top.addWidget(name, 1)
        top.addWidget(self.rules_button, 0, Qt.AlignmentFlag.AlignVCenter)
        top.addWidget(connect, 0, Qt.AlignmentFlag.AlignVCenter)
        self._show_rule_dot()

        tools = QHBoxLayout()
        tools.setContentsMargins(0, 0, 0, 0)
        tools.setSpacing(8)
        target = QLabel(f"{connection.username}@{connection.host}:{connection.port}")
        target.setObjectName("Subtitle")
        agents = QToolButton()
        agents.setObjectName("Ghost")
        agents.setText(t("list.agents"))
        agents.setIcon(robot_icon())
        agents.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        agents.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        agents.setMenu(self._agents_menu())
        export = QPushButton(t("list.export"))
        export.setObjectName("Ghost")
        export.setIcon(document_icon())
        export.clicked.connect(lambda: self.export_requested.emit(self.connection_id))
        tools.addWidget(target, 1)
        tools.addWidget(agents, 0, Qt.AlignmentFlag.AlignVCenter)
        tools.addWidget(export, 0, Qt.AlignmentFlag.AlignVCenter)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 0, 0)
        footer.setSpacing(8)
        delete = QPushButton(t("list.delete"))
        delete.setObjectName("DangerGhost")
        delete.setIcon(close_icon())
        delete.clicked.connect(lambda: self.delete_requested.emit(self.connection_id))
        edit = QPushButton(t("list.edit"))
        edit.setObjectName("EditLink")
        edit.setIcon(pencil_icon())
        edit.clicked.connect(lambda: self.edit_requested.emit(self.connection_id))
        duplicate = QPushButton(t("list.duplicate"))
        duplicate.setObjectName("DuplicateLink")
        duplicate.setIcon(duplicate_icon("#8fd0c0"))
        duplicate.clicked.connect(lambda: self.duplicate_requested.emit(self.connection_id))
        self.enabled_label = QLabel()
        self.enabled_switch = ToggleSwitch(connection.enabled)
        self.enabled_switch.toggled.connect(self._on_enabled_toggled)
        self._show_enabled_state(connection.enabled)
        footer.addWidget(delete, 0, Qt.AlignmentFlag.AlignLeft)
        footer.addWidget(edit, 0, Qt.AlignmentFlag.AlignLeft)
        footer.addWidget(duplicate, 0, Qt.AlignmentFlag.AlignLeft)
        footer.addStretch()
        footer.addWidget(self.enabled_label, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        footer.addWidget(self.enabled_switch, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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
            for action_id, _action_label, _prompt in ACTIONS:
                item = submenu.addAction(action_menu_label(action_id))
                item.triggered.connect(
                    lambda _checked=False, t=tool_id, a=action_id: self._assist(t, a)
                )
        return menu

    def _show_enabled_state(self, enabled: bool) -> None:
        self.enabled_label.setText(t("list.enabled") if enabled else t("list.disabled"))
        self.enabled_label.setObjectName("Success" if enabled else "Hint")
        self.enabled_label.style().unpolish(self.enabled_label)
        self.enabled_label.style().polish(self.enabled_label)
        self.enabled_switch.setToolTip(
            t("list.disable_tip") if enabled else t("list.enable_tip")
        )

    def _on_enabled_toggled(self, checked: bool) -> None:
        self.connection.enabled = checked
        self._show_enabled_state(checked)
        self.enabled_changed.emit(self.connection_id, checked)

    def _show_rule_dot(self) -> None:
        action = dominant_action(self.connection.rules)
        color = ACTION_COLORS[action]
        self.rule_dot.setStyleSheet(
            f"background: {color}; border-radius: 4px;"
        )
        self.rule_dot.setToolTip(action_label(action))
        self.rules_button.button.setToolTip(action_label(action))

    def _edit_rules(self) -> None:
        dialog = RulesDialog(self.connection, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.connection.rules = dialog.rules()
        self.session.upsert(self.connection)
        self.session.save()
        self._show_rule_dot()

    def _connect(self) -> None:
        if not self.connection.enabled:
            dialog = DisabledConnectionDialog(self.connection, self)
            dialog.exec()
            if dialog.choice != "enable":
                if dialog.choice == "deny" and dialog.dont_show_again():
                    self.connection.hide_disabled_prompt = True
                    self.session.upsert(self.connection)
                    self.session.save()
                return
            self.enabled_switch.setChecked(True)
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
    enabled_changed = Signal(str, bool)

    def __init__(self, session: AppSession) -> None:
        super().__init__()
        self.session = session
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 20)
        root.setSpacing(12)

        header = QLabel(t("list.section"))
        header.setObjectName("Section")
        root.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(self.scroll, 1)

        self.add_button = QPushButton(t("list.add"))
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
            empty = QLabel(t("list.empty"))
            empty.setObjectName("Subtitle")
            empty.setWordWrap(True)
            layout.addWidget(empty)
        for connection in connections:
            card = ConnectionCard(connection, self.session)
            card.edit_requested.connect(self.edit_requested.emit)
            card.duplicate_requested.connect(self.duplicate_requested.emit)
            card.export_requested.connect(self.export_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)
            card.enabled_changed.connect(self.enabled_changed.emit)
            layout.addWidget(card)
        layout.addStretch()
        self.scroll.setWidget(container)
