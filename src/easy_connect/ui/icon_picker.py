from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from easy_connect.i18n import t
from easy_connect.ui.connection_icons import catalog, icon_picture, icon_pixmap, resolve_icon


MAX_VISIBLE = 180
_PICKER_ICON = 40
_CARD_ICON = 32


class IconPicker(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._icons = catalog()
        self._selected = ""
        self._buttons: list[QPushButton] = []
        self._build()

    def icon(self) -> str:
        return self._selected

    def set_icon(self, icon_id: str) -> None:
        self._selected = icon_id if icon_id in {item[0] for item in self._icons} else ""
        self._sync_selection()
        self._show_current()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText(t("icon.search"))
        self.search.textChanged.connect(self._apply_filter)
        clear = QPushButton(t("icon.none"))
        clear.clicked.connect(self._clear)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(clear)

        current_row = QHBoxLayout()
        current_row.setSpacing(8)
        self.current_icon = QLabel()
        self.current_icon.setFixedSize(_CARD_ICON, _CARD_ICON)
        self.current_text = QLabel(t("icon.empty_selection"))
        self.current_text.setObjectName("Hint")
        current_row.addWidget(self.current_icon, 0, Qt.AlignmentFlag.AlignVCenter)
        current_row.addWidget(self.current_text, 1)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.grid_host)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root.addLayout(search_row)
        root.addLayout(current_row)
        root.addWidget(scroll, 1)
        self._apply_filter()

    def _choose(self, icon_id: str) -> None:
        self._selected = icon_id
        self._sync_selection()
        self._show_current()

    def _clear(self) -> None:
        self._selected = ""
        self._sync_selection()
        self._show_current()

    def _show_current(self) -> None:
        if self._selected:
            self.current_icon.setPixmap(icon_pixmap(self._selected, _CARD_ICON))
            self.current_text.setText(t("icon.selected"))
        else:
            self.current_icon.clear()
            self.current_text.setText(t("icon.empty_selection"))

    def _sync_selection(self) -> None:
        for button in self._buttons:
            button.setChecked(button.property("iconId") == self._selected)

    def _clear_grid(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._buttons.clear()

    def _apply_filter(self) -> None:
        terms = [part for part in self.search.text().strip().lower().split() if part]
        matched: list[tuple[str, str]] = []
        for icon_id, words in self._icons:
            haystack = f"{icon_id} {words}"
            if all(term in haystack for term in terms):
                matched.append((icon_id, words))
                if len(matched) >= MAX_VISIBLE:
                    break
        self._clear_grid()
        if not matched:
            empty = QLabel(t("icon.not_found"))
            empty.setObjectName("Hint")
            self.grid.addWidget(empty, 0, 0)
            return
        columns = 12
        for index, (icon_id, words) in enumerate(matched):
            button = QPushButton()
            button.setObjectName("IconChoice")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setIcon(icon_picture(icon_id, _PICKER_ICON))
            button.setIconSize(QSize(_PICKER_ICON, _PICKER_ICON))
            button.setToolTip(words.replace(" ", ", "))
            button.setFixedSize(72, 64)
            button.setProperty("iconId", icon_id)
            button.setChecked(icon_id == self._selected)
            button.clicked.connect(lambda _checked=False, chosen=icon_id: self._choose(chosen))
            self._buttons.append(button)
            self.grid.addWidget(button, index // columns, index % columns)


def card_icon(icon_id: str):
    return icon_pixmap(resolve_icon(icon_id), _CARD_ICON)
