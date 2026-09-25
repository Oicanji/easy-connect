from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from easy_connect.core.models import CommandRules, RuleAction
from easy_connect.core.rules import ACTION_COLORS, ACTIONS, RULES, action_label, rule_label
from easy_connect.i18n import t


class RulesPanel(QWidget):
    def __init__(self, rules: CommandRules | None = None, parent=None) -> None:
        super().__init__(parent)
        self._groups: dict[str, QButtonGroup] = {}
        self._boxes: dict[tuple[str, RuleAction], QCheckBox] = {}
        self._headers: dict[RuleAction, QLabel] = {}
        self._build()
        self.set_rules(rules or CommandRules())

    def rules(self) -> CommandRules:
        values: dict[str, RuleAction] = {}
        for rule_id, _label in RULES:
            chosen = RuleAction.allow
            for action, _action_label in ACTIONS:
                if self._boxes[(rule_id, action)].isChecked():
                    chosen = action
                    break
            values[rule_id] = chosen
        return CommandRules(**values)

    def set_rules(self, rules: CommandRules) -> None:
        for rule_id, _label in RULES:
            action = getattr(rules, rule_id)
            self._boxes[(rule_id, action)].setChecked(True)
        self._paint()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(0, 1)
        label_width = 0

        for column, (action, _label) in enumerate(ACTIONS, start=1):
            header = QWidget()
            header.setCursor(Qt.CursorShape.PointingHandCursor)
            header.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            header.setToolTip(t("rules.column_tip"))
            row = QHBoxLayout(header)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(
                f"background: {ACTION_COLORS[action]}; border-radius: 4px;"
            )
            caption = QLabel(action_label(action))
            caption.setWordWrap(False)
            caption.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            row.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(caption, 0, Qt.AlignmentFlag.AlignVCenter)
            header.mousePressEvent = lambda _event, chosen=action: self._select_column(chosen)
            self._headers[action] = caption
            width = header.sizeHint().width()
            header.setMinimumWidth(width)
            grid.setColumnMinimumWidth(column, width)
            grid.addWidget(header, 0, column, Qt.AlignmentFlag.AlignHCenter)

        for row_index, (rule_id, _label) in enumerate(RULES, start=1):
            name = QLabel(rule_label(rule_id))
            name.setWordWrap(False)
            label_width = max(label_width, name.sizeHint().width())
            grid.addWidget(name, row_index, 0, Qt.AlignmentFlag.AlignVCenter)
            group = QButtonGroup(self)
            group.setExclusive(True)
            self._groups[rule_id] = group
            for column, (action, _action_label) in enumerate(ACTIONS, start=1):
                box = QCheckBox()
                box.setToolTip(action_label(action))
                box.toggled.connect(lambda _checked=False: self._paint())
                group.addButton(box)
                self._boxes[(rule_id, action)] = box
                grid.addWidget(box, row_index, column, Qt.AlignmentFlag.AlignHCenter)

        grid.setColumnMinimumWidth(0, label_width)
        root.addLayout(grid)

    def _select_column(self, action: RuleAction) -> None:
        for rule_id, _label in RULES:
            self._boxes[(rule_id, action)].setChecked(True)
        self._paint()

    def _paint(self) -> None:
        current = self.rules()
        for (rule_id, action), box in self._boxes.items():
            color = ACTION_COLORS[action]
            if box.isChecked():
                box.setStyleSheet(
                    "QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; }"
                    f"QCheckBox::indicator:checked {{ background: {color}; border: 1px solid {color}; }}"
                )
            else:
                box.setStyleSheet(
                    "QCheckBox::indicator {"
                    " width: 16px; height: 16px; border-radius: 3px;"
                    " border: 1px solid #5c6570; background: transparent;"
                    "}"
                )
        for action, header in self._headers.items():
            color = ACTION_COLORS[action]
            filled = all(getattr(current, rule_id) == action for rule_id, _label in RULES)
            weight = "600" if filled else "400"
            header.setStyleSheet(
                f"color: {color}; font-weight: {weight}; background: transparent;"
            )
