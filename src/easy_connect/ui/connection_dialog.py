from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.commands import is_valid_command, sanitize_command, suggest_command
from easy_connect.core.models import AuthMethod, Connection, as_auth_method
from easy_connect.core.session import AppSession
from easy_connect.core.validators import validate_connection
from easy_connect.ui.widgets import FilePicker


PRIVATE_KEY_FILTER = "Todos os arquivos (*);;PEM/KEY (*.pem *.key);;PPK (*.ppk)"
PUBLIC_KEY_FILTER = "Chave pública (*.pub);;Todos os arquivos (*)"


class FormError(ValueError):
    def __init__(self, message: str, tab: int = 0) -> None:
        super().__init__(message)
        self.tab = tab


class ReachabilityWorker(QThread):
    done = Signal(bool, str)

    def __init__(
        self,
        host: str,
        port: int,
        timeout: float,
        vpn_host: str,
        vpn_port: int,
    ) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self.vpn_host = vpn_host
        self.vpn_port = vpn_port

    def run(self) -> None:
        ok, message = validate_connection(
            self.host,
            self.port,
            self.timeout,
            vpn_host=self.vpn_host,
            vpn_port=self.vpn_port,
        )
        self.done.emit(ok, message)


class ConnectionDialog(QDialog):
    def __init__(self, session: AppSession, connection: Connection | None = None) -> None:
        super().__init__()
        self.session = session
        self.original = connection
        self.result_connection: Connection | None = None
        self._command_manual = connection is not None
        self._worker: ReachabilityWorker | None = None
        self.setWindowTitle("Editar conexão" if connection else "Nova conexão")
        self.setModal(True)
        self.setFixedSize(580, 540)
        self._build()
        if connection:
            self._fill(connection)
        else:
            timeout = session.payload.settings.default_validation_timeout
            self.timeout.setValue(timeout)

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("DialogTabs")
        self.tabs.addTab(self._tab_session(), "Sessão")
        self.tabs.addTab(self._tab_auth(), "Autenticação")
        self.tabs.addTab(self._tab_sudo(), "Sudo")
        root.addWidget(self.tabs, 1)

        self.status = QLabel("")
        self.status.setObjectName("Hint")
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        buttons = QHBoxLayout()
        test = QPushButton("Testar rede")
        test.clicked.connect(self._test_network)
        buttons.addWidget(test)
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar conexão")
        save.setObjectName("Primary")
        save.clicked.connect(self._save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        root.addLayout(buttons)
        self._sync_auth()
        self._sync_sudo()

    def _tab_session(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(10)
        hint = QLabel("Dados da sessão SSH, no mesmo espírito do WinSCP.")
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Nome amigável")
        self.host = QLineEdit()
        self.host.setPlaceholderText("1.100.0.2")
        self.host.textChanged.connect(self._on_host_changed)
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(22)
        self.port.setFixedWidth(90)
        host_row = QWidget()
        host_layout = QHBoxLayout(host_row)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(8)
        host_layout.addWidget(self.host, 1)
        host_layout.addWidget(QLabel("Porta"))
        host_layout.addWidget(self.port)
        self.username = QLineEdit()
        self.username.setPlaceholderText("ubuntu")
        self.jump = QLineEdit()
        self.jump.setPlaceholderText("usuario@jump-host (opcional)")
        self.remote_directory = QLineEdit()
        self.remote_directory.setPlaceholderText("/home/ubuntu/app")
        self.command = QLineEdit()
        self.command.setPlaceholderText("ssh-1-100-0-2")
        self.command.textEdited.connect(self._on_command_edited)
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(10)
        self.keepalive = QSpinBox()
        self.keepalive.setRange(0, 300)
        self.keepalive.setValue(30)
        self.compression = QCheckBox("Compressão SSH")
        form.addRow("Nome", self.name)
        form.addRow("Host / IP", host_row)
        form.addRow("Usuário", self.username)
        form.addRow("Jump host", self.jump)
        form.addRow("Diretório remoto", self.remote_directory)
        form.addRow("Comando", self.command)
        form.addRow("Timeout (s)", self.timeout)
        form.addRow("Keepalive (s)", self.keepalive)
        form.addRow("", self.compression)
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _tab_auth(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(10)
        hint = QLabel("Selecione arquivos de chave como no WinSCP. Nada disso é pedido no terminal.")
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        method_row = QHBoxLayout()
        self.auth = QComboBox()
        self.auth.addItem("Senha", AuthMethod.password.value)
        self.auth.addItem("Chave privada", AuthMethod.private_key.value)
        self.auth.addItem("ssh-agent", AuthMethod.agent.value)
        self.auth.currentIndexChanged.connect(self._sync_auth)
        method_row.addWidget(QLabel("Método"))
        method_row.addWidget(self.auth, 1)
        layout.addLayout(method_row)

        self.auth_stack = QStackedWidget()
        self.auth_stack.addWidget(self._auth_password_page())
        self.auth_stack.addWidget(self._auth_key_page())
        self.auth_stack.addWidget(self._auth_agent_page())
        layout.addWidget(self.auth_stack, 1)
        self.agent_forwarding = QCheckBox("Encaminhar agente SSH (ForwardAgent)")
        layout.addWidget(self.agent_forwarding)
        return page

    def _auth_password_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Senha SSH")
        layout.addWidget(QLabel("Senha"))
        layout.addWidget(self.password)
        note = QLabel("Fica no cofre e o comando global entra já autenticado.")
        note.setObjectName("Hint")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def _auth_key_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)
        self.private_key = FilePicker(
            "Arquivo da chave privada",
            "Selecionar chave privada",
            PRIVATE_KEY_FILTER,
        )
        self.private_key.path_changed.connect(lambda _path: self._suggest_public_key())
        self.public_key = FilePicker(
            "Arquivo da chave pública",
            "Selecionar chave pública",
            PUBLIC_KEY_FILTER,
        )
        self.key_passphrase = QLineEdit()
        self.key_passphrase.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_passphrase.setPlaceholderText("Passphrase da chave, se houver")
        self.stored_key_hint = QLabel("")
        self.stored_key_hint.setObjectName("Hint")
        self.stored_key_hint.setWordWrap(True)
        layout.addWidget(QLabel("Chave privada"))
        layout.addWidget(self.private_key)
        layout.addWidget(QLabel("Chave pública"))
        layout.addWidget(self.public_key)
        layout.addWidget(QLabel("Passphrase"))
        layout.addWidget(self.key_passphrase)
        layout.addWidget(self.stored_key_hint)
        layout.addStretch()
        return page

    def _auth_agent_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        note = QLabel(
            "Usa o ssh-agent do sistema (OpenSSH Agent ou Pageant). "
            "Nenhuma senha ou arquivo de chave precisa ser guardado aqui."
        )
        note.setObjectName("Hint")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def _tab_sudo(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(10)
        hint = QLabel(
            "Se ligado, o comando já cai com privilégio elevado. "
            "Útil quando o usuário SSH não é root."
        )
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.sudo_enabled = QCheckBox("Elevar com sudo após o login")
        self.sudo_enabled.toggled.connect(self._sync_sudo)
        layout.addWidget(self.sudo_enabled)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.sudo_user = QLineEdit()
        self.sudo_user.setPlaceholderText("root")
        self.sudo_user.setText("root")
        self.sudo_password = QLineEdit()
        self.sudo_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.sudo_password.setPlaceholderText("Senha do sudo, se o servidor pedir")
        self.sudo_command = QLineEdit()
        self.sudo_command.setText("sudo -i")
        self.sudo_command.setPlaceholderText("sudo -i")
        form.addRow("Usuário sudo", self.sudo_user)
        form.addRow("Senha sudo", self.sudo_password)
        form.addRow("Comando", self.sudo_command)
        layout.addLayout(form)
        extra = QLabel(
            "Deixe a senha em branco se o usuário tiver NOPASSWD. "
            "O comando padrão abre um login shell elevado."
        )
        extra.setObjectName("Hint")
        extra.setWordWrap(True)
        layout.addWidget(extra)
        layout.addStretch()
        self._sudo_fields = [self.sudo_user, self.sudo_password, self.sudo_command]
        return page

    def _fill(self, connection: Connection) -> None:
        self.name.setText(connection.name)
        self.host.setText(connection.host)
        self.port.setValue(connection.port)
        self.username.setText(connection.username)
        self.jump.setText(connection.jump_host)
        self.remote_directory.setText(connection.remote_directory)
        index = self.auth.findData(as_auth_method(connection.auth_method).value)
        if index >= 0:
            self.auth.setCurrentIndex(index)
        if connection.password:
            self.password.setPlaceholderText("Senha já salva. Deixe em branco para manter.")
        self.private_key.set_path(connection.private_key_path)
        self.public_key.set_path(connection.public_key_path)
        if connection.private_key_passphrase:
            self.key_passphrase.setPlaceholderText("Passphrase já salva. Deixe em branco para manter.")
        if connection.private_key_content and not connection.private_key_path:
            self.stored_key_hint.setText("Há uma chave privada no cofre. Selecione um arquivo para substituir.")
        self.agent_forwarding.setChecked(connection.agent_forwarding)
        self.command.setText(connection.command)
        self.timeout.setValue(connection.validation_timeout)
        self.keepalive.setValue(connection.keepalive)
        self.compression.setChecked(connection.compression)
        self.sudo_enabled.setChecked(connection.sudo_enabled)
        self.sudo_user.setText(connection.sudo_user or "root")
        if connection.sudo_password:
            self.sudo_password.setPlaceholderText("Senha sudo já salva. Deixe em branco para manter.")
        self.sudo_command.setText(connection.sudo_command or "sudo -i")
        self._sync_auth()
        self._sync_sudo()

    def _sync_auth(self) -> None:
        method = as_auth_method(self.auth.currentData() or AuthMethod.password)
        if method == AuthMethod.private_key:
            self.auth_stack.setCurrentIndex(1)
        elif method == AuthMethod.agent:
            self.auth_stack.setCurrentIndex(2)
        else:
            self.auth_stack.setCurrentIndex(0)

    def _sync_sudo(self) -> None:
        enabled = self.sudo_enabled.isChecked()
        for field in self._sudo_fields:
            field.setEnabled(enabled)

    def _suggest_public_key(self) -> None:
        if self.public_key.path():
            return
        private = self.private_key.path()
        if not private:
            return
        candidate = Path(private + ".pub")
        if candidate.is_file():
            self.public_key.set_path(str(candidate))

    def _on_host_changed(self, text: str) -> None:
        if self._command_manual:
            return
        self.command.setText(suggest_command(text))

    def _on_command_edited(self, text: str) -> None:
        self._command_manual = True
        cursor = self.command.cursorPosition()
        cleaned = sanitize_command(text)
        if cleaned != text:
            self.command.setText(cleaned)
            self.command.setCursorPosition(min(cursor, len(cleaned)))

    def _set_status(self, text: str, kind: str = "Hint") -> None:
        self.status.setObjectName(kind)
        self.status.setText(text)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def _test_network(self) -> None:
        host = self.host.text().strip()
        if not host:
            self.tabs.setCurrentIndex(0)
            self._set_status("Informe o host para testar.", "Error")
            return
        self._set_status("Checando rede...")
        settings = self.session.payload.settings
        self._worker = ReachabilityWorker(
            host,
            int(self.port.value()),
            float(self.timeout.value()),
            settings.vpn_check_host,
            settings.vpn_check_port,
        )
        self._worker.done.connect(self._on_test_done)
        self._worker.start()

    def _on_test_done(self, ok: bool, message: str) -> None:
        self._set_status("Host alcançável." if ok else message, "Success" if ok else "Error")

    def _save(self) -> None:
        try:
            connection = self._build_connection()
        except FormError as exc:
            self.tabs.setCurrentIndex(exc.tab)
            self._set_status(str(exc), "Error")
            return
        self.result_connection = connection
        self.accept()

    def _build_connection(self) -> Connection:
        name = self.name.text().strip()
        host = self.host.text().strip()
        username = self.username.text().strip()
        command = sanitize_command(self.command.text())
        if not name:
            raise FormError("Informe um nome para a conexão.", 0)
        if not host:
            raise FormError("Informe o host ou IP.", 0)
        if not username:
            raise FormError("Informe o usuário SSH.", 0)
        if not is_valid_command(command):
            raise FormError("Comando inválido. Use letras, números, hífen ou underline.", 0)
        ignore_id = self.original.id if self.original else None
        if self.session.command_taken(command, ignore_id=ignore_id):
            raise FormError(
                f"O comando {command} já está em uso. Escolha outro, por exemplo {command}-deploy.",
                0,
            )
        method = as_auth_method(self.auth.currentData() or AuthMethod.password)
        password = self.password.text()
        passphrase = self.key_passphrase.text()
        sudo_password = self.sudo_password.text()
        if self.original:
            if method == AuthMethod.password and not password:
                password = self.original.password
            if method == AuthMethod.private_key and not passphrase:
                passphrase = self.original.private_key_passphrase
            if self.sudo_enabled.isChecked() and not sudo_password:
                sudo_password = self.original.sudo_password
        if method == AuthMethod.password and not password:
            raise FormError("Informe a senha SSH. Ela não será pedida no terminal.", 1)
        private_path = self.private_key.path()
        public_path = self.public_key.path()
        stored_key = self.original.private_key_content if self.original else ""
        if method == AuthMethod.private_key and not private_path and not stored_key:
            raise FormError("Selecione o arquivo da chave privada.", 1)
        if public_path and not Path(public_path).expanduser().is_file():
            raise FormError("Arquivo da chave pública não encontrado.", 1)
        if private_path and not Path(private_path).expanduser().is_file():
            raise FormError("Arquivo da chave privada não encontrado.", 1)
        base = self.original.model_copy() if self.original else Connection(
            name=name,
            host=host,
            username=username,
            command=command,
        )
        base.name = name
        base.host = host
        base.port = int(self.port.value())
        base.username = username
        base.auth_method = method
        base.password = password if method == AuthMethod.password else ""
        base.private_key_path = private_path if method == AuthMethod.private_key else ""
        if method == AuthMethod.private_key and private_path:
            base.private_key_content = ""
        elif method != AuthMethod.private_key:
            base.private_key_content = ""
        base.private_key_passphrase = passphrase if method == AuthMethod.private_key else ""
        base.public_key_path = public_path if method == AuthMethod.private_key else ""
        base.agent_forwarding = self.agent_forwarding.isChecked()
        base.jump_host = self.jump.text().strip()
        base.remote_directory = self.remote_directory.text().strip()
        base.command = command
        base.validation_timeout = int(self.timeout.value())
        base.connect_timeout = int(self.timeout.value())
        base.keepalive = int(self.keepalive.value())
        base.compression = self.compression.isChecked()
        base.sudo_enabled = self.sudo_enabled.isChecked()
        base.sudo_user = self.sudo_user.text().strip() or "root"
        base.sudo_password = sudo_password if base.sudo_enabled else ""
        base.sudo_command = self.sudo_command.text().strip() or "sudo -i"
        return base
