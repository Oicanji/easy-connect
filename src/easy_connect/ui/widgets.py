from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


def copy_icon() -> QIcon:
    pixmap = QPixmap(18, 18)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#9aa3ae"), 1.4))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(QRect(6, 2, 9, 11), 2, 2)
    painter.setBrush(QColor("#16181d"))
    painter.drawRoundedRect(QRect(2, 6, 9, 11), 2, 2)
    painter.end()
    return QIcon(pixmap)


def copy_to_clipboard(text: str) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is not None:
        clipboard.setText(text)


class CopyButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = text
        self.setObjectName("Copy")
        self.setIcon(copy_icon())
        self.setToolTip("Copiar")
        self.setFixedSize(30, 30)
        self.clicked.connect(self._copy)

    def set_value(self, text: str) -> None:
        self._value = text

    def _copy(self) -> None:
        copy_to_clipboard(self._value)


class CopyRow(QWidget):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.label = QLabel(text)
        self.label.setObjectName("Hint")
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.button = CopyButton(text)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.button, 0)


class FilePicker(QWidget):
    path_changed = Signal(str)

    def __init__(
        self,
        placeholder: str,
        caption: str,
        file_filter: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._caption = caption
        self._filter = file_filter
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.editingFinished.connect(self._emit_path)
        browse = QPushButton("...")
        browse.setFixedWidth(40)
        browse.clicked.connect(self._browse)
        layout.addWidget(self.edit, 1)
        layout.addWidget(browse)

    def path(self) -> str:
        return self.edit.text().strip()

    def set_path(self, value: str) -> None:
        self.edit.setText(value)

    def _emit_path(self) -> None:
        self.path_changed.emit(self.path())

    def _browse(self) -> None:
        start = self.path() or str(Path.home() / ".ssh")
        if not Path(start).exists():
            start = str(Path.home())
        chosen, _ = QFileDialog.getOpenFileName(self, self._caption, start, self._filter)
        if chosen:
            self.edit.setText(chosen)
            self._emit_path()
