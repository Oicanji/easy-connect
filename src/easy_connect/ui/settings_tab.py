from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.commands import path_notice, python_display, reinstall_wrappers, wrappers_dir
from easy_connect.core.session import AppSession
from easy_connect.llm.actions import TOOLS
from easy_connect.ui.styles import apply_theme
from easy_connect.ui.widgets import CopyButton, FilePicker


class SettingsTab(QWidget):
    def __init__(self, session: AppSession) -> None:
        super().__init__()
        self.session = session
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 20)
        root.setSpacing(12)

        title = QLabel("CONFIGURAÇÕES")
        title.setObjectName("Section")
        root.addWidget(title)

        form = QFormLayout()
        self.wrappers = QLineEdit(str(wrappers_dir()))
        self.wrappers.setReadOnly(True)
        self.python = QLineEdit(python_display())
        self.python.setReadOnly(True)
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(session.payload.settings.default_validation_timeout)
        self.vpn_host = QLineEdit(session.payload.settings.vpn_check_host)
        self.vpn_host.setPlaceholderText("Host opcional para validar VPN")
        self.vpn_port = QSpinBox()
        self.vpn_port.setRange(1, 65535)
        self.vpn_port.setValue(session.payload.settings.vpn_check_port)
        self.theme = QComboBox()
        self.theme.addItem("Escuro", "dark")
        self.theme.addItem("Claro", "light")
        index = self.theme.findData(session.payload.settings.theme)
        if index >= 0:
            self.theme.setCurrentIndex(index)

        form.addRow("Pasta dos comandos", self._with_copy(self.wrappers))
        form.addRow("Python dos wrappers", self._with_copy(self.python))
        form.addRow("Timeout padrão (s)", self.timeout)
        form.addRow("Host de checagem VPN", self.vpn_host)
        form.addRow("Porta VPN", self.vpn_port)
        form.addRow("Tema", self.theme)
        root.addLayout(form)

        agents = QLabel("AGENTES")
        agents.setObjectName("Section")
        root.addWidget(agents)

        agent_form = QFormLayout()
        saved_paths = session.payload.settings.agent_paths
        self._agent_pickers: dict[str, FilePicker] = {}
        for tool_id, tool_label in TOOLS:
            picker = FilePicker(
                "Pasta de instalação",
                f"Selecionar pasta do {tool_label}",
                directory=True,
            )
            picker.set_path(str(saved_paths.get(tool_id) or ""))
            self._agent_pickers[tool_id] = picker
            agent_form.addRow(tool_label, picker)
        root.addLayout(agent_form)

        agent_hint = QLabel(
            "Se o Easy Connect não achar o CLI no PATH, selecione a pasta onde o "
            "programa está instalado. O prompt continua copiado para colar no chat."
        )
        agent_hint.setObjectName("Hint")
        agent_hint.setWordWrap(True)
        root.addWidget(agent_hint)

        hint = QLabel(
            "Terminais já abertos não veem um PATH novo. Feche e abra o terminal "
            "depois de instalar o primeiro comando."
        )
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        root.addWidget(hint)

        buttons = QHBoxLayout()
        save = QPushButton("Salvar configurações")
        save.setObjectName("Primary")
        save.clicked.connect(self._save)
        reinstall = QPushButton("Reinstalar comandos no PATH")
        reinstall.clicked.connect(self._reinstall)
        buttons.addWidget(save)
        buttons.addWidget(reinstall)
        buttons.addStretch()
        root.addLayout(buttons)

        credit = QLabel("Ignacio Sepúlveda")
        credit.setObjectName("Credit")
        link = QLabel('<a href="https://github.com/Oicanji/easy-connect">github.com/Oicanji/easy-connect</a>')
        link.setObjectName("Credit")
        link.setOpenExternalLinks(True)
        root.addWidget(credit)
        root.addWidget(link)
        root.addStretch()

    def _with_copy(self, field: QLineEdit) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(field, 1)
        layout.addWidget(CopyButton(field.text()))
        return row

    def _save(self) -> None:
        settings = self.session.payload.settings
        settings.default_validation_timeout = int(self.timeout.value())
        settings.vpn_check_host = self.vpn_host.text().strip()
        settings.vpn_check_port = int(self.vpn_port.value())
        settings.theme = self.theme.currentData()
        settings.agent_paths = {
            tool_id: picker.path() for tool_id, picker in self._agent_pickers.items()
        }
        self.session.save()
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            apply_theme(app, settings.theme)
        QMessageBox.information(self, "Easy Connect", "Configurações salvas.")

    def _reinstall(self) -> None:
        commands = [item.command for item in self.session.payload.connections]
        reinstall_wrappers(commands)
        self.session.payload.settings.path_installed = True
        self.session.save()
        QMessageBox.information(self, "Easy Connect", path_notice())
