from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QTextOption
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.models import Connection
from easy_connect.llm.actions import TOOLS
from easy_connect.i18n import t
from easy_connect.ui.widgets import paperclip_icon, send_icon, tool_pixmap


class PromptEdit(QPlainTextEdit):
    def __init__(self, on_submit, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_submit = on_submit
        self.setObjectName("PromptEdit")
        self.setPlaceholderText(t("prompt.placeholder"))
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.document().contentsChanged.connect(self._adjust_height)
        self._adjust_height()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.insertPlainText("\n")
                return
            self._on_submit()
            return
        super().keyPressEvent(event)

    def _adjust_height(self) -> None:
        doc = self.document()
        margins = self.contentsMargins()
        frame = int(self.frameWidth()) * 2
        height = int(doc.size().height()) + margins.top() + margins.bottom() + frame + 10
        self.setFixedHeight(max(40, min(height, 160)))


class AgentPromptDialog(QDialog):
    def __init__(self, tool: str, connection: Connection, parent=None) -> None:
        super().__init__(parent)
        self._tool = tool
        self._connection = connection
        self._attachments: list[str] = []
        label = dict(TOOLS).get(tool, tool)
        self.setObjectName("PromptDialog")
        self.setWindowTitle(label)
        self.setModal(True)
        self.setFixedSize(440, 340)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 16)
        root.setSpacing(0)

        meta = QLabel(f"{connection.username}@{connection.host}:{connection.port}")
        meta.setObjectName("PromptMeta")
        meta.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(meta)

        root.addSpacing(18)

        icon = QLabel()
        icon.setObjectName("PromptAgentIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icon.setFixedHeight(48)
        icon.setPixmap(tool_pixmap(tool, size=44))
        icon.setToolTip(label)
        root.addWidget(icon)

        root.addSpacing(6)

        agent_name = QLabel(label)
        agent_name.setObjectName("PromptAgentName")
        agent_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(agent_name)

        root.addStretch(1)

        composer = QFrame()
        composer.setObjectName("PromptComposer")
        composer_layout = QVBoxLayout(composer)
        composer_layout.setContentsMargins(10, 8, 10, 8)
        composer_layout.setSpacing(6)

        self.files_host = QWidget()
        self.files_layout = QHBoxLayout(self.files_host)
        self.files_layout.setContentsMargins(0, 0, 0, 0)
        self.files_layout.setSpacing(6)
        self.files_host.hide()
        composer_layout.addWidget(self.files_host)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        attach = QPushButton()
        attach.setObjectName("PromptAttach")
        attach.setIcon(paperclip_icon())
        attach.setToolTip(t("prompt.attach_tip"))
        attach.setFixedSize(34, 34)
        attach.setCursor(Qt.CursorShape.PointingHandCursor)
        attach.clicked.connect(self._attach)
        row.addWidget(attach, 0, Qt.AlignmentFlag.AlignBottom)

        self.editor = PromptEdit(self._submit, self)
        row.addWidget(self.editor, 1)

        send = QPushButton()
        send.setObjectName("Primary")
        send.setIcon(send_icon())
        send.setToolTip(t("prompt.send_tip"))
        send.setFixedSize(34, 34)
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.clicked.connect(self._submit)
        row.addWidget(send, 0, Qt.AlignmentFlag.AlignBottom)

        composer_layout.addLayout(row)
        root.addWidget(composer)
        self.editor.setFocus()

    def prompt_text(self) -> str:
        return self.editor.toPlainText().strip()

    def attachments(self) -> list[str]:
        return list(self._attachments)

    def _attach(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, t("prompt.attach"), str(Path.home()))
        for path in paths:
            if path and path not in self._attachments:
                self._attachments.append(path)
        self._reload_files()

    def _remove(self, path: str) -> None:
        self._attachments = [item for item in self._attachments if item != path]
        self._reload_files()

    def _reload_files(self) -> None:
        while self.files_layout.count():
            item = self.files_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        if not self._attachments:
            self.files_host.hide()
            return
        self.files_host.show()
        for path in self._attachments:
            chip = QFrame()
            chip.setObjectName("PromptChip")
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(8, 2, 4, 2)
            chip_layout.setSpacing(4)
            name = QLabel(Path(path).name)
            name.setObjectName("PromptChipText")
            name.setToolTip(path)
            remove = QPushButton("x")
            remove.setObjectName("PromptChipRemove")
            remove.setFixedSize(18, 18)
            remove.setCursor(Qt.CursorShape.PointingHandCursor)
            remove.clicked.connect(lambda _checked=False, p=path: self._remove(p))
            chip_layout.addWidget(name)
            chip_layout.addWidget(remove)
            self.files_layout.addWidget(chip)
        self.files_layout.addStretch(1)

    def _submit(self) -> None:
        if not self.prompt_text() and not self._attachments:
            return
        self.accept()
