from __future__ import annotations

from easy_connect.i18n.catalog import CATALOG

LANGUAGES: tuple[tuple[str, str], ...] = (
    ("pt", "Português"),
    ("en", "English"),
    ("es", "Español"),
    ("de", "Deutsch"),
    ("zh", "中文"),
)

_current = "pt"
_loaded = False


def language_codes() -> tuple[str, ...]:
    return tuple(code for code, _label in LANGUAGES)


def normalize_language(code: str | None) -> str:
    text = str(code or "").strip().lower().replace("_", "-")
    if text in language_codes():
        return text
    primary = text.split("-", 1)[0]
    if primary in language_codes():
        return primary
    return "pt"


def language_path():
    from easy_connect.core.paths import app_data_dir

    return app_data_dir() / "language.txt"


def get_language() -> str:
    return _current


def load_language() -> str:
    global _current, _loaded
    _loaded = True
    path = language_path()
    if path.is_file():
        _current = normalize_language(path.read_text(encoding="utf-8"))
    else:
        _current = "pt"
    return _current


def language_file_exists() -> bool:
    return language_path().is_file()


def set_language(code: str) -> str:
    global _current, _loaded
    _loaded = True
    _current = normalize_language(code)
    from easy_connect.core.paths import ensure_app_dirs

    ensure_app_dirs()
    language_path().write_text(_current + "\n", encoding="utf-8")
    return _current


def t(key: str, **kwargs) -> str:
    if not _loaded:
        load_language()
    catalog = CATALOG.get(_current) or CATALOG["pt"]
    text = catalog.get(key)
    if text is None:
        text = CATALOG["pt"].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
