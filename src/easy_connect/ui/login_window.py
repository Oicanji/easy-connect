from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from easy_connect import __version__, app_title
from easy_connect.core.session import AppSession
from easy_connect.core.vault import Vault, VaultError, WrongPasswordError
from easy_connect.ui.styles import apply_app_icon


class LoginWindow(QWidget):
    unlocked = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(app_title())
        apply_app_icon(self)
        self.setFixedSize(440, 360)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 36, 36, 36)
        root.setSpacing(12)

        title = QLabel("Desbloquear")
        title.setObjectName("Title")
        version = QLabel(f"v{__version__}")
        version.setObjectName("Subtitle")
        subtitle = QLabel("Digite a senha mestre para abrir o Easy Connect e as sessões salvas.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Senha mestre")
        self.password.returnPressed.connect(self._submit)

        self.error = QLabel("")
        self.error.setObjectName("Error")
        self.error.setWordWrap(True)

        submit = QPushButton("Entrar")
        submit.setObjectName("Primary")
        submit.clicked.connect(self._submit)

        root.addWidget(title)
        root.addWidget(version)
        root.addWidget(subtitle)
        root.addSpacing(8)
        root.addWidget(self.password)
        root.addWidget(self.error)
        root.addStretch()
        root.addWidget(submit)

    def _submit(self) -> None:
        password = self.password.text()
        if not password:
            self.error.setText("Informe a senha mestre.")
            return
        try:
            vault = Vault()
            key = vault.unlock(password)
            payload = vault.load(key)
            session = AppSession(key, payload, vault)
            session.persist_unlock()
            self.unlocked.emit(session)
        except WrongPasswordError:
            self.error.setText("Senha incorreta.")
        except VaultError as exc:
            self.error.setText(str(exc))
