from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from easy_connect import __version__, app_title
from easy_connect.core.session import AppSession
from easy_connect.core.vault import Vault, VaultError
from easy_connect.i18n import set_language, t
from easy_connect.ui.locale import apply_locale, fill_language_combo
from easy_connect.ui.styles import apply_app_icon


class SetupWindow(QWidget):
    created = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(app_title())
        apply_app_icon(self)
        self.setFixedSize(440, 520)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 36, 36, 36)
        root.setSpacing(12)

        title = QLabel("Easy Connect")
        title.setObjectName("Title")
        version = QLabel(f"v{__version__}")
        version.setObjectName("Subtitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("Subtitle")
        self.subtitle.setWordWrap(True)

        language_row = QHBoxLayout()
        self.language_label = QLabel()
        self.language = QComboBox()
        fill_language_combo(self.language)
        self.language.currentIndexChanged.connect(self._on_language)
        language_row.addWidget(self.language_label)
        language_row.addWidget(self.language, 1)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.returnPressed.connect(self._submit)

        self.error = QLabel("")
        self.error.setObjectName("Error")
        self.error.setWordWrap(True)

        self.submit = QPushButton()
        self.submit.setObjectName("Primary")
        self.submit.clicked.connect(self._submit)

        root.addWidget(title)
        root.addWidget(version)
        root.addWidget(self.subtitle)
        root.addLayout(language_row)
        root.addSpacing(8)
        root.addWidget(self.password)
        root.addWidget(self.confirm)
        root.addWidget(self.error)
        root.addStretch()
        root.addWidget(self.submit)
        self._apply_texts()

    def _apply_texts(self) -> None:
        self.subtitle.setText(t("setup.subtitle"))
        self.language_label.setText(t("login.language"))
        self.password.setPlaceholderText(t("setup.password"))
        self.confirm.setPlaceholderText(t("setup.confirm"))
        self.submit.setText(t("setup.submit"))

    def _on_language(self) -> None:
        set_language(str(self.language.currentData() or "pt"))
        app = QApplication.instance()
        if app is not None:
            apply_locale(app)
        self._apply_texts()

    def _submit(self) -> None:
        password = self.password.text()
        confirm = self.confirm.text()
        if password != confirm:
            self.error.setText(t("setup.mismatch"))
            return
        try:
            vault = Vault()
            key = vault.create(password)
            payload = vault.load(key)
            session = AppSession(key, payload, vault)
            session.persist_unlock()
            self.created.emit(session)
        except VaultError as exc:
            self.error.setText(str(exc))
            QMessageBox.warning(self, "Easy Connect", str(exc))
