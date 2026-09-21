from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from easy_connect import __version__, app_title
from easy_connect.core.paths import ensure_app_dirs, is_windows
from easy_connect.core.session import AppSession
from easy_connect.core.vault import Vault
from easy_connect.ui.login_window import LoginWindow
from easy_connect.ui.main_window import MainWindow
from easy_connect.ui.setup_window import SetupWindow
from easy_connect.ui.styles import apply_app_icon, apply_theme


def main() -> None:
    ensure_app_dirs()
    unlock_only = "--unlock" in sys.argv
    qt_args = [item for item in sys.argv if item != "--unlock"]
    app = QApplication(qt_args)
    app.setApplicationName("Easy Connect")
    app.setApplicationDisplayName(app_title())
    app.setApplicationVersion(__version__)
    app.setOrganizationName("EasyConnect")
    apply_app_icon(app)
    family = "Segoe UI" if is_windows() else "Sans Serif"
    app.setFont(QFont(family, 10))
    apply_theme(app, "dark")
    resumed = AppSession.resume()
    if resumed is not None:
        apply_theme(app, resumed.payload.settings.theme)
        if unlock_only:
            sys.exit(0)
        _show_main(app, resumed)
        sys.exit(app.exec())
    if Vault().exists():
        _show_login(app, unlock_only=unlock_only)
    else:
        _show_setup(app)
    sys.exit(app.exec())


def _show_setup(app: QApplication) -> None:
    window = SetupWindow()
    window.created.connect(lambda session: _show_main(app, session, window))
    window.show()
    app._window = window


def _show_login(app: QApplication, unlock_only: bool = False) -> None:
    window = LoginWindow()
    if unlock_only:
        window.unlocked.connect(lambda _session: _finish_unlock(app, window))
    else:
        window.unlocked.connect(lambda session: _show_main(app, session, window))
    window.show()
    app._window = window


def _finish_unlock(app: QApplication, window) -> None:
    window.close()
    app.quit()


def _show_main(app: QApplication, session: AppSession, previous=None) -> None:
    apply_theme(app, session.payload.settings.theme)
    window = MainWindow(session)
    window.locked.connect(lambda: _show_login(app))
    window.show()
    app._window = window
    if previous is not None:
        previous.close()


if __name__ == "__main__":
    main()
