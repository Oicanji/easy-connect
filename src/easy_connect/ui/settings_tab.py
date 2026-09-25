from __future__ import annotations

from PySide6.QtCore import Signal
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
from easy_connect.i18n import set_language, t
from easy_connect.llm.actions import TOOLS
from easy_connect.ui.locale import apply_locale, fill_language_combo
from easy_connect.ui.styles import apply_theme
from easy_connect.ui.widgets import CopyButton, FilePicker


class SettingsTab(QWidget):
    language_changed = Signal()
    def __init__(self, session: AppSession) -> None:
        super().__init__()
        self.session = session
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 20)
        root.setSpacing(12)

        title = QLabel(t("settings.section"))
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
        self.vpn_host.setPlaceholderText(t("settings.vpn_placeholder"))
        self.vpn_port = QSpinBox()
        self.vpn_port.setRange(1, 65535)
        self.vpn_port.setValue(session.payload.settings.vpn_check_port)
        self.theme = QComboBox()
        self.theme.addItem(t("settings.theme.dark"), "dark")
        self.theme.addItem(t("settings.theme.light"), "light")
        index = self.theme.findData(session.payload.settings.theme)
        if index >= 0:
            self.theme.setCurrentIndex(index)
        self.language = QComboBox()
        fill_language_combo(self.language, session.payload.settings.language)

        form.addRow(t("settings.commands_dir"), self._with_copy(self.wrappers))
        form.addRow(t("settings.python"), self._with_copy(self.python))
        form.addRow(t("settings.timeout"), self.timeout)
        form.addRow(t("settings.vpn_host"), self.vpn_host)
        form.addRow(t("settings.vpn_port"), self.vpn_port)
        form.addRow(t("settings.theme"), self.theme)
        form.addRow(t("settings.language"), self.language)
        root.addLayout(form)

        agents = QLabel(t("settings.agents"))
        agents.setObjectName("Section")
        root.addWidget(agents)

        agent_form = QFormLayout()
        saved_paths = session.payload.settings.agent_paths
        self._agent_pickers: dict[str, FilePicker] = {}
        for tool_id, tool_label in TOOLS:
            picker = FilePicker(
                t("settings.agent_placeholder"),
                t("settings.agent_caption", label=tool_label),
                directory=True,
            )
            picker.set_path(str(saved_paths.get(tool_id) or ""))
            self._agent_pickers[tool_id] = picker
            agent_form.addRow(tool_label, picker)
        root.addLayout(agent_form)

        agent_hint = QLabel(t("settings.agent_hint"))
        agent_hint.setObjectName("Hint")
        agent_hint.setWordWrap(True)
        root.addWidget(agent_hint)

        hint = QLabel(t("settings.path_hint"))
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        root.addWidget(hint)

        buttons = QHBoxLayout()
        save = QPushButton(t("settings.save"))
        save.setObjectName("Primary")
        save.clicked.connect(self._save)
        reinstall = QPushButton(t("settings.reinstall"))
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
        previous_language = settings.language
        settings.default_validation_timeout = int(self.timeout.value())
        settings.vpn_check_host = self.vpn_host.text().strip()
        settings.vpn_check_port = int(self.vpn_port.value())
        settings.theme = self.theme.currentData()
        settings.language = str(self.language.currentData() or "pt")
        set_language(settings.language)
        settings.agent_paths = {
            tool_id: picker.path() for tool_id, picker in self._agent_pickers.items()
        }
        self.session.save()
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            apply_locale(app)
            apply_theme(app, settings.theme)
        QMessageBox.information(self, "Easy Connect", t("settings.saved"))
        if settings.language != previous_language:
            self.language_changed.emit()

    def _reinstall(self) -> None:
        commands = [item.command for item in self.session.payload.connections]
        reinstall_wrappers(commands)
        self.session.payload.settings.path_installed = True
        self.session.save()
        QMessageBox.information(self, "Easy Connect", path_notice())
