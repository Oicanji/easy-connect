from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
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
from easy_connect.ui.styles import apply_app_icon


class SetupWindow(QWidget):
    created = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(app_title())
        apply_app_icon(self)
        self.setFixedSize(440, 460)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 36, 36, 36)
        root.setSpacing(12)

        title = QLabel("Easy Connect")
        title.setObjectName("Title")
        version = QLabel(f"v{__version__}")
        version.setObjectName("Subtitle")
        subtitle = QLabel(
            "Defina uma senha mestre. Ela protege o aplicativo e as sessões SSH salvas. "
            "Se esquecer, não há recuperação."
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Senha mestre (mínimo 8 caracteres)")

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.setPlaceholderText("Confirmar senha")
        self.confirm.returnPressed.connect(self._submit)

        self.error = QLabel("")
        self.error.setObjectName("Error")
        self.error.setWordWrap(True)

        submit = QPushButton("Criar cofre e continuar")
        submit.setObjectName("Primary")
        submit.clicked.connect(self._submit)

        root.addWidget(title)
        root.addWidget(version)
        root.addWidget(subtitle)
        root.addSpacing(8)
        root.addWidget(self.password)
        root.addWidget(self.confirm)
        root.addWidget(self.error)
        root.addStretch()
        root.addWidget(submit)

    def _submit(self) -> None:
        password = self.password.text()
        confirm = self.confirm.text()
        if password != confirm:
            self.error.setText("As senhas não coincidem.")
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
