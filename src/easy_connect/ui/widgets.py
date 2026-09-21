from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, Signal
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


def _paint_icon(size: int, draw) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    draw(painter, size)
    painter.end()
    return QIcon(pixmap)


def copy_icon(color: str = "#6b7380") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(QPen(QColor(color), 1.3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRect(6, 2, 9, 10), 2, 2)
        painter.drawRoundedRect(QRect(2, 6, 9, 10), 2, 2)

    return _paint_icon(18, draw)


def plus_icon(color: str = "#c5ced6") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(QPen(QColor(color), 1.6))
        mid = size // 2
        painter.drawLine(mid, 4, mid, size - 4)
        painter.drawLine(4, mid, size - 4, mid)

    return _paint_icon(18, draw)


def robot_icon(color: str = "#c5ced6") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        pen = QPen(QColor(color), 1.4)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRect(3, 6, 12, 10), 3, 3)
        painter.drawLine(9, 3, 9, 6)
        painter.drawEllipse(QPoint(9, 3), 1, 1)
        painter.setBrush(QColor(color))
        painter.drawEllipse(QPoint(6, 10), 1, 1)
        painter.drawEllipse(QPoint(12, 10), 1, 1)

    return _paint_icon(18, draw)


def document_icon(color: str = "#c5ced6") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(QPen(QColor(color), 1.3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRect(4, 2, 10, 14), 2, 2)
        painter.drawLine(7, 6, 13, 6)
        painter.drawLine(7, 9, 13, 9)
        painter.drawLine(7, 12, 11, 12)

    return _paint_icon(18, draw)


def close_icon(color: str = "#e07a7f") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(QPen(QColor(color), 1.6))
        painter.drawLine(5, 5, size - 5, size - 5)
        painter.drawLine(size - 5, 5, 5, size - 5)

    return _paint_icon(18, draw)


def pencil_icon(color: str = "#6cb6ff") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(QPen(QColor(color), 1.5))
        painter.drawLine(4, size - 5, size - 6, 5)
        painter.drawLine(size - 6, 5, size - 4, 7)
        painter.drawLine(4, size - 5, 6, size - 3)

    return _paint_icon(18, draw)


def paperclip_icon(color: str = "#9aa3ae") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(QPen(QColor(color), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(QRect(5, 3, 8, 8), 40 * 16, 200 * 16)
        painter.drawLine(7, 10, 7, 14)
        painter.drawArc(QRect(5, 11, 8, 6), -40 * 16, -200 * 16)

    return _paint_icon(18, draw)


def send_icon(color: str = "#08110f") -> QIcon:
    def draw(painter: QPainter, size: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        mid = size // 2
        painter.drawPolygon(
            [
                QPoint(4, 3),
                QPoint(size - 3, mid),
                QPoint(4, size - 3),
                QPoint(6, mid),
            ]
        )

    return _paint_icon(18, draw)


TOOL_ICON_FILES = {
    "claude": "claude_code.png",
    "cursor": "cursor.png",
    "antigravity": "antigravity.png",
    "codex": "codex.png",
}


def tool_pixmap(tool: str, size: int = 40) -> QPixmap:
    from easy_connect.core.paths import resource_file

    name = TOOL_ICON_FILES.get(tool)
    if name:
        path = resource_file(name)
        if path is not None:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                return pixmap.scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
    return tool_icon(tool, size=size).pixmap(size, size)


def tool_icon(tool: str, size: int = 28, color: str = "#2f9e8f") -> QIcon:
    from easy_connect.core.paths import resource_file

    name = TOOL_ICON_FILES.get(tool)
    if name:
        path = resource_file(name)
        if path is not None:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                return QIcon(scaled)

    label = {
        "claude": "C",
        "cursor": "A",
        "antigravity": "G",
        "codex": "X",
    }.get(tool, "?")

    def draw(painter: QPainter, icon_size: int) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        painter.drawEllipse(1, 1, icon_size - 2, icon_size - 2)
        painter.setPen(QColor("#08110f"))
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(max(10, icon_size // 2))
        painter.setFont(font)
        painter.drawText(QRect(0, 0, icon_size, icon_size), Qt.AlignmentFlag.AlignCenter, label)

    return _paint_icon(size, draw)


def copy_to_clipboard(text: str) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is not None:
        clipboard.setText(text)


class CopyButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = text
        self.setObjectName("InlineCopy")
        self.setIcon(copy_icon())
        self.setToolTip("Copiar")
        self.setFlat(True)
        self.setFixedSize(18, 18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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
        layout.setSpacing(4)
        self.label = QLabel(text)
        self.label.setObjectName("Hint")
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setWordWrap(False)
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        self.button = CopyButton(text)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignVCenter)


class FilePicker(QWidget):
    path_changed = Signal(str)

    def __init__(
        self,
        placeholder: str,
        caption: str,
        file_filter: str = "",
        parent: QWidget | None = None,
        directory: bool = False,
    ) -> None:
        super().__init__(parent)
        self._caption = caption
        self._filter = file_filter
        self._directory = directory
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
        start = self._start_path()
        if self._directory:
            chosen = QFileDialog.getExistingDirectory(self, self._caption, start)
        else:
            chosen, _ = QFileDialog.getOpenFileName(self, self._caption, start, self._filter)
        if chosen:
            self.edit.setText(chosen)
            self._emit_path()

    def _start_path(self) -> str:
        current = self.path()
        if current:
            path = Path(current)
            if path.is_file():
                return str(path.parent)
            if path.exists():
                return str(path)
        if self._directory:
            programs = Path(os.environ.get("LOCALAPPDATA") or "") / "Programs"
            if programs.is_dir():
                return str(programs)
            return str(Path.home())
        ssh = Path.home() / ".ssh"
        if ssh.exists():
            return str(ssh)
        return str(Path.home())
