from __future__ import annotations

from PySide6.QtWidgets import QApplication

DARK_QSS = """
QWidget {
    background-color: #16181d;
    color: #e6e8ec;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #16181d;
}
QLabel {
    background: transparent;
}
QLabel#Title {
    font-size: 22px;
    font-weight: 600;
    color: #f2f4f7;
}
QLabel#Subtitle {
    color: #9aa3ae;
    font-size: 13px;
}
QLabel#Hint {
    color: #8b949e;
    font-size: 12px;
}
QLabel#Section {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #7d8a96;
}
QLabel#Error {
    color: #e07a7f;
}
QLabel#Success {
    color: #6bcb8b;
}
QFrame#Card {
    background-color: #1e232b;
    border: 1px solid #2c3440;
    border-radius: 12px;
}
QFrame#ConnectionCard {
    background-color: #1e232b;
    border: 1px solid #2c3440;
    border-radius: 10px;
}
QFrame#ConnectionCard:hover {
    border: 1px solid #3a4656;
}
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {
    background-color: #12151a;
    border: 1px solid #323b47;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #2f9e8f;
    selection-color: #08110f;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1px solid #2f9e8f;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e232b;
    border: 1px solid #323b47;
    selection-background-color: #2f9e8f;
    selection-color: #08110f;
}
QPushButton {
    background-color: #242b34;
    color: #e6e8ec;
    border: 1px solid #323b47;
    border-radius: 8px;
    padding: 8px 14px;
}
QPushButton:hover {
    background-color: #2c3440;
}
QPushButton:pressed {
    background-color: #1a1f26;
}
QPushButton:disabled {
    color: #6b7380;
    background-color: #1a1f26;
}
QPushButton#Primary {
    background-color: #2f9e8f;
    color: #08110f;
    border: none;
    font-weight: 600;
}
QPushButton#Primary:hover {
    background-color: #3cb5a5;
}
QPushButton#Primary:disabled {
    background-color: #1f4f48;
    color: #8aa8a3;
}
QPushButton#Danger {
    background-color: transparent;
    color: #e07a7f;
    border: 1px solid #5a3236;
}
QPushButton#Danger:hover {
    background-color: #3a2225;
}
QPushButton#Ghost {
    background: transparent;
    border: none;
    color: #9aa3ae;
    padding: 4px 8px;
}
QPushButton#Ghost:hover {
    color: #e6e8ec;
    background-color: #242b34;
}
QPushButton#InlineCopy {
    background: transparent;
    border: none;
    padding: 0;
    min-width: 18px;
    max-width: 18px;
    min-height: 18px;
}
QPushButton#InlineCopy:hover {
    background: transparent;
    border: none;
}
QPushButton#Plus {
    background: transparent;
    color: #c5ced6;
    border: 1px solid #323b47;
    border-radius: 8px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    padding: 0;
}
QPushButton#Plus:hover {
    background-color: #242b34;
    border: 1px solid #3a4656;
}
QPushButton#EditLink {
    background: transparent;
    border: 1px solid #355a7a;
    border-radius: 8px;
    color: #6cb6ff;
    padding: 6px 10px;
}
QPushButton#EditLink:hover {
    background-color: #1b2836;
    color: #8cc6ff;
    border: 1px solid #4a7aa0;
}
QPushButton#DangerGhost {
    background: transparent;
    border: 1px solid #5a3236;
    border-radius: 8px;
    color: #e07a7f;
    padding: 6px 10px;
}
QPushButton#DangerGhost:hover {
    background-color: #3a2225;
    border: 1px solid #7a4448;
}
QToolButton#Ghost {
    background: transparent;
    border: none;
    color: #9aa3ae;
    padding: 4px 8px;
}
QToolButton#Ghost:hover {
    color: #e6e8ec;
    background-color: #242b34;
}
QToolButton#Ghost::menu-indicator {
    image: none;
}
QLabel#Credit {
    color: #5c6570;
    font-size: 11px;
    background: transparent;
}
QLabel#PromptMeta {
    color: #6b7380;
    font-size: 10px;
    background: transparent;
}
QLabel#PromptAgentName {
    color: #9aa3ae;
    font-size: 12px;
    background: transparent;
}
QLabel#PromptAgentIcon {
    background: transparent;
}
QFrame#PromptComposer {
    background-color: #1e232b;
    border: 1px solid #2c3440;
    border-radius: 14px;
}
QPlainTextEdit#PromptEdit {
    background-color: transparent;
    border: none;
    padding: 6px 4px;
    font-size: 13px;
}
QPlainTextEdit#PromptEdit:focus {
    border: none;
}
QPushButton#PromptAttach {
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 0;
}
QPushButton#PromptAttach:hover {
    background-color: #242b34;
}
QFrame#PromptChip {
    background-color: #242b34;
    border: 1px solid #323b47;
    border-radius: 8px;
}
QLabel#PromptChipText {
    color: #c5ced6;
    font-size: 11px;
    background: transparent;
}
QPushButton#PromptChipRemove {
    background: transparent;
    border: none;
    color: #8b949e;
    padding: 0;
    font-size: 11px;
}
QPushButton#PromptChipRemove:hover {
    color: #e07a7f;
    background: transparent;
}
QMenu {
    background-color: #1e232b;
    color: #e6e8ec;
    border: 1px solid #323b47;
    padding: 6px;
    border-radius: 8px;
}
QMenu::item {
    padding: 8px 18px;
    border-radius: 6px;
    min-width: 280px;
}
QMenu::item:selected {
    background-color: #2f9e8f;
    color: #08110f;
}
QMenu::separator {
    height: 1px;
    background: #323b47;
    margin: 4px 8px;
}
QMenu::right-arrow {
    width: 10px;
    height: 10px;
    margin-right: 8px;
}
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #8b949e;
    padding: 10px 18px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #e6e8ec;
    border-bottom: 2px solid #2f9e8f;
}
QTabBar::tab:hover {
    color: #e6e8ec;
}
QTabWidget#DialogTabs::pane {
    border: 1px solid #2c3440;
    border-radius: 10px;
    background-color: #1e232b;
    top: -1px;
}
QTabWidget#DialogTabs QTabBar::tab {
    padding: 9px 16px;
    margin-right: 2px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px;
}
QScrollBar::handle:vertical {
    background: #323b47;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QCheckBox {
    spacing: 8px;
    background: transparent;
}
QGroupBox {
    border: 1px solid #2c3440;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #9aa3ae;
}
QStatusBar {
    background: #12151a;
    color: #8b949e;
}
"""

LIGHT_QSS = """
QWidget {
    background-color: #f4f6f8;
    color: #1c232c;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #f4f6f8;
}
QLabel {
    background: transparent;
}
QLabel#Title {
    font-size: 22px;
    font-weight: 600;
    color: #15202b;
}
QLabel#Subtitle {
    color: #5b6773;
    font-size: 13px;
}
QLabel#Hint {
    color: #6b7682;
    font-size: 12px;
}
QLabel#Section {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #6b7682;
}
QLabel#Error {
    color: #c2474d;
}
QLabel#Success {
    color: #2f8a55;
}
QFrame#Card, QFrame#ConnectionCard {
    background-color: #ffffff;
    border: 1px solid #d5dde5;
    border-radius: 12px;
}
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #2f9e8f;
    selection-color: #08110f;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1px solid #2f9e8f;
}
QPushButton {
    background-color: #ffffff;
    color: #1c232c;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    padding: 8px 14px;
}
QPushButton:hover {
    background-color: #eef2f5;
}
QPushButton#Primary {
    background-color: #2f9e8f;
    color: #08110f;
    border: none;
    font-weight: 600;
}
QPushButton#Danger {
    background-color: transparent;
    color: #c2474d;
    border: 1px solid #efc4c6;
}
QPushButton#Ghost {
    background: transparent;
    border: none;
    color: #5b6773;
}
QPushButton#InlineCopy {
    background: transparent;
    border: none;
    padding: 0;
    min-width: 18px;
    max-width: 18px;
}
QPushButton#Plus {
    background: transparent;
    border: 1px solid #d5dde5;
    border-radius: 8px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    padding: 0;
}
QPushButton#EditLink {
    background: transparent;
    border: 1px solid #b7d3ef;
    border-radius: 8px;
    color: #2f7fd6;
    padding: 6px 10px;
}
QPushButton#DangerGhost {
    background: transparent;
    border: 1px solid #efc4c6;
    border-radius: 8px;
    color: #c2474d;
    padding: 6px 10px;
}
QToolButton#Ghost {
    background: transparent;
    border: none;
    color: #5b6773;
}
QLabel#Credit {
    color: #8a94a0;
    font-size: 11px;
    background: transparent;
}
QLabel#PromptMeta {
    color: #8a94a0;
    font-size: 10px;
    background: transparent;
}
QLabel#PromptAgentName {
    color: #5b6773;
    font-size: 12px;
    background: transparent;
}
QLabel#PromptAgentIcon {
    background: transparent;
}
QFrame#PromptComposer {
    background-color: #ffffff;
    border: 1px solid #d5dde5;
    border-radius: 14px;
}
QPlainTextEdit#PromptEdit {
    background-color: transparent;
    border: none;
    padding: 6px 4px;
    font-size: 13px;
}
QPlainTextEdit#PromptEdit:focus {
    border: none;
}
QPushButton#PromptAttach {
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 0;
}
QPushButton#PromptAttach:hover {
    background-color: #eef2f5;
}
QFrame#PromptChip {
    background-color: #eef2f5;
    border: 1px solid #d5dde5;
    border-radius: 8px;
}
QLabel#PromptChipText {
    color: #5b6773;
    font-size: 11px;
    background: transparent;
}
QPushButton#PromptChipRemove {
    background: transparent;
    border: none;
    color: #8a94a0;
    padding: 0;
    font-size: 11px;
}
QPushButton#PromptChipRemove:hover {
    color: #c2474d;
    background: transparent;
}
QMenu {
    background-color: #ffffff;
    color: #1c232c;
    border: 1px solid #d5dde5;
    padding: 6px;
    border-radius: 8px;
}
QMenu::item {
    padding: 8px 18px;
    border-radius: 6px;
    min-width: 280px;
}
QMenu::item:selected {
    background-color: #2f9e8f;
    color: #08110f;
}
QTabBar::tab {
    background: transparent;
    color: #6b7682;
    padding: 10px 18px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #15202b;
    border-bottom: 2px solid #2f9e8f;
}
QTabWidget#DialogTabs::pane {
    border: 1px solid #d5dde5;
    border-radius: 10px;
    background-color: #ffffff;
}
QGroupBox {
    border: 1px solid #d5dde5;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
}
QStatusBar {
    background: #eef2f5;
    color: #5b6773;
}
"""


def apply_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(LIGHT_QSS if theme == "light" else DARK_QSS)


def apply_app_icon(target) -> None:
    from PySide6.QtGui import QIcon

    from easy_connect.core.paths import icon_path

    path = icon_path()
    if path is None:
        return
    target.setWindowIcon(QIcon(str(path)))
