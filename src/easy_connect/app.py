from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from easy_connect import __version__, app_title
from easy_connect.core.paths import ensure_app_dirs
from easy_connect.core.session import AppSession
from easy_connect.core.vault import Vault
from easy_connect.ui.disabled_connection_dialog import DENIED_EXIT, run_disabled_prompt
from easy_connect.ui.login_window import LoginWindow
from easy_connect.ui.main_window import MainWindow
from easy_connect.ui.rules_dialog import run_rule_prompt
from easy_connect.ui.setup_window import SetupWindow
from easy_connect.i18n import load_language
from easy_connect.ui.locale import adopt_session_language, apply_locale
from easy_connect.ui.styles import apply_app_icon, apply_theme


def _startup_flags() -> tuple[list[str], bool, str | None, str | None, list[str]]:
    unlock_only = False
    disabled_command = None
    rule_command = None
    rule_remote: list[str] = []
    qt_args = [sys.argv[0]]
    index = 1
    while index < len(sys.argv):
        item = sys.argv[index]
        if item == "--unlock":
            unlock_only = True
            index += 1
            continue
        if item == "--disabled-connection" and index + 1 < len(sys.argv):
            disabled_command = sys.argv[index + 1]
            index += 2
            continue
        if item == "--rule-prompt" and index + 1 < len(sys.argv):
            rule_command = sys.argv[index + 1]
            index += 2
            if index < len(sys.argv) and sys.argv[index] == "--":
                index += 1
            rule_remote = sys.argv[index:]
            break
        qt_args.append(item)
        index += 1
    return qt_args, unlock_only, disabled_command, rule_command, rule_remote


def main() -> None:
    ensure_app_dirs()
    load_language()
    qt_args, unlock_only, disabled_command, rule_command, rule_remote = _startup_flags()
    app = QApplication(qt_args)
    app.setApplicationName("Easy Connect")
    app.setApplicationDisplayName(app_title())
    app.setApplicationVersion(__version__)
    app.setOrganizationName("EasyConnect")
    apply_app_icon(app)
    apply_locale(app)
    apply_theme(app, "dark")
    resumed = AppSession.resume()
    if resumed is not None:
        adopt_session_language(resumed)
        apply_locale(app)
        apply_theme(app, resumed.payload.settings.theme)
        if disabled_command:
            sys.exit(run_disabled_prompt(resumed, disabled_command))
        if rule_command:
            sys.exit(run_rule_prompt(resumed, rule_command, rule_remote))
        if unlock_only:
            sys.exit(0)
        _show_main(app, resumed)
        sys.exit(app.exec())
    if Vault().exists():
        _show_login(
            app,
            unlock_only=unlock_only,
            disabled_command=disabled_command,
            rule_command=rule_command,
            rule_remote=rule_remote,
        )
    elif disabled_command or rule_command:
        sys.exit(DENIED_EXIT)
    else:
        _show_setup(app)
    sys.exit(app.exec())


def _show_setup(app: QApplication) -> None:
    window = SetupWindow()
    window.created.connect(lambda session: _show_main(app, session, window))
    window.show()
    app._window = window


def _show_login(
    app: QApplication,
    unlock_only: bool = False,
    disabled_command: str | None = None,
    rule_command: str | None = None,
    rule_remote: list[str] | None = None,
) -> None:
    window = LoginWindow()
    if disabled_command:
        window.unlocked.connect(
            lambda session: _finish_disabled_prompt(app, session, window, disabled_command)
        )
    elif rule_command:
        remote = list(rule_remote or [])
        window.unlocked.connect(
            lambda session: _finish_rule_prompt(app, session, window, rule_command, remote)
        )
    elif unlock_only:
        window.unlocked.connect(lambda _session: _finish_unlock(app, window))
    else:
        window.unlocked.connect(lambda session: _show_main(app, session, window))
    window.show()
    app._window = window


def _finish_disabled_prompt(app: QApplication, session: AppSession, window, command: str) -> None:
    window.close()
    app.exit(run_disabled_prompt(session, command))


def _finish_rule_prompt(
    app: QApplication,
    session: AppSession,
    window,
    command: str,
    remote: list[str],
) -> None:
    window.close()
    app.exit(run_rule_prompt(session, command, remote))


def _finish_unlock(app: QApplication, window) -> None:
    window.close()
    app.quit()


def _show_main(app: QApplication, session: AppSession, previous=None) -> None:
    adopt_session_language(session)
    apply_locale(app)
    apply_theme(app, session.payload.settings.theme)
    window = MainWindow(session)
    window.locked.connect(lambda: _show_login(app))
    window.show()
    app._window = window
    if previous is not None:
        previous.close()


if __name__ == "__main__":
    main()
