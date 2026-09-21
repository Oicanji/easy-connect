from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.models import Connection, LlmTarget, as_llm_kind
from easy_connect.llm.templates import LlmKind, forget_export, remember_export, suggested_filename


class ExportDialog(QDialog):
    def __init__(self, connection: Connection, parent=None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Exportar instrução")
        self.setModal(True)
        self.setMinimumSize(480, 380)
        self.resize(520, 440)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        title = QLabel("Exportar instrução da LLM")
        title.setObjectName("Title")
        title.setStyleSheet("font-size: 18px;")
        hint = QLabel(
            "O texto é gerado com os dados desta conexão. "
            "Todos os arquivos da lista são atualizados sozinhos quando você editar a conexão."
        )
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        self.target = QComboBox()
        self.target.addItem("Claude", LlmTarget.claude.value)
        self.target.addItem("Cursor", LlmTarget.cursor.value)
        self.target.addItem("Antigravity", LlmTarget.antigravity.value)
        if connection.llm_exports:
            kind = as_llm_kind(connection.llm_exports[-1].kind).value
            index = self.target.findData(kind)
            if index >= 0:
                self.target.setCurrentIndex(index)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.target)

        files_label = QLabel("ARQUIVOS")
        files_label.setObjectName("Section")
        layout.addWidget(files_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.scroll, 1)
        self.files_host = QWidget()
        self.files_layout = QVBoxLayout(self.files_host)
        self.files_layout.setContentsMargins(0, 0, 4, 0)
        self.files_layout.setSpacing(6)
        self.scroll.setWidget(self.files_host)

        self.status = QLabel("")
        self.status.setObjectName("Hint")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        buttons = QHBoxLayout()
        add = QPushButton("Adicionar arquivo")
        add.setObjectName("Primary")
        add.clicked.connect(self._add)
        close = QPushButton("Fechar")
        close.clicked.connect(self.accept)
        buttons.addWidget(add)
        buttons.addStretch()
        buttons.addWidget(close)
        layout.addLayout(buttons)
        self._reload_files()

    def _reload_files(self) -> None:
        while self.files_layout.count():
            item = self.files_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        exports = list(self.connection.llm_exports)
        if not exports:
            empty = QLabel("Nenhum arquivo ainda. Adicione um para cada projeto.")
            empty.setObjectName("Hint")
            empty.setWordWrap(True)
            self.files_layout.addWidget(empty)
        for item in exports:
            self.files_layout.addWidget(self._file_row(item.path, item.kind))
        self.files_layout.addStretch()

    def _file_row(self, path: str, kind: str) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        label = QLabel(path)
        label.setObjectName("Hint")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        remove = QPushButton("-")
        remove.setObjectName("Danger")
        remove.setFixedSize(28, 28)
        remove.setStyleSheet("padding: 0px;")
        remove.clicked.connect(lambda: self._remove(path))
        layout.addWidget(label, 1)
        layout.addWidget(remove, 0, Qt.AlignmentFlag.AlignTop)
        row.setToolTip(kind)
        return row

    def _remove(self, path: str) -> None:
        forget_export(self.connection, path)
        self.status.setText("Arquivo removido da lista. O arquivo no disco não foi apagado.")
        self._reload_files()

    def _add(self) -> None:
        try:
            kind: LlmKind = self.target.currentData()
            if kind not in ("claude", "cursor", "antigravity"):
                kind = "cursor"
            suggested = suggested_filename(kind, self.connection)
            exports = list(self.connection.llm_exports)
            if exports:
                start = exports[-1].path
            else:
                start = str(Path.home() / Path(suggested).name)
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar instrução da LLM",
                start,
                "Markdown (*.md *.mdc);;Todos os arquivos (*.*)",
            )
            if not path:
                return
            output = remember_export(self.connection, kind, path)
            self.status.setObjectName("Success")
            self.status.setText(f"Instrução salva em {output}")
            self.status.style().unpolish(self.status)
            self.status.style().polish(self.status)
            self._reload_files()
        except Exception as exc:
            QMessageBox.critical(self, "Easy Connect", f"Não foi possível salvar a instrução:\n{exc}")
