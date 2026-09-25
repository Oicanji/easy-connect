from __future__ import annotations

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QComboBox

from easy_connect.core.paths import is_windows
from easy_connect.i18n import LANGUAGES, get_language, language_file_exists, set_language

_QT_LOCALES = {
    "pt": "pt_BR",
    "en": "en",
    "es": "es",
    "de": "de",
    "zh": "zh_CN",
}


def fill_language_combo(box: QComboBox, current: str | None = None) -> None:
    box.blockSignals(True)
    box.clear()
    for code, label in LANGUAGES:
        box.addItem(label, code)
    index = box.findData(current or get_language())
    if index >= 0:
        box.setCurrentIndex(index)
    box.blockSignals(False)


def apply_locale(app: QApplication) -> None:
    code = get_language()
    locale = QLocale(_QT_LOCALES.get(code, "pt_BR"))
    QLocale.setDefault(locale)
    previous = getattr(app, "_qt_translator", None)
    if previous is not None:
        app.removeTranslator(previous)
    translator = QTranslator(app)
    translations = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if code != "en":
        translator.load(locale, "qtbase", "_", translations)
    app.installTranslator(translator)
    app._qt_translator = translator
    if code == "zh" and is_windows():
        family = "Microsoft YaHei UI"
    elif is_windows():
        family = "Segoe UI"
    else:
        family = "Sans Serif"
    app.setFont(QFont(family, 10))


def adopt_session_language(session) -> None:
    settings = session.payload.settings
    if language_file_exists():
        code = get_language()
        if settings.language != code:
            settings.language = code
            session.save()
        return
    set_language(settings.language)
