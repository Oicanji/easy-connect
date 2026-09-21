# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis

SPECDIR = Path(os.path.abspath(SPECPATH))
ROOT = SPECDIR.parent
SRC = ROOT / "src"
ICON = SPECDIR / "easyconnect.ico"
VERSION_INFO = SPECDIR / "file_version_info.txt"
ICON_PNG = ROOT / "src" / "easy_connect" / "resources" / "icon.png"

datas = []
if ICON_PNG.is_file():
    datas.append((str(ICON_PNG), "easy_connect/resources"))

hiddenimports = [
    "keyring.backends.Windows",
    "keyring.backends.fail",
    "keyring.backends.null",
    "keyring.backends.libsecret",
    "argon2",
    "argon2.low_level",
    "cryptography",
    "cryptography.hazmat.primitives.ciphers.aead",
    "pydantic",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

pathex = [str(SRC), str(ROOT)]
icon_file = str(ICON) if ICON.is_file() else None

gui_a = Analysis(
    [str(SPECDIR / "entry_gui.py")],
    pathex=pathex,
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
cli_a = Analysis(
    [str(SPECDIR / "entry_cli.py")],
    pathex=pathex,
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
ask_a = Analysis(
    [str(SPECDIR / "entry_askpass.py")],
    pathex=pathex,
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

gui_pyz = PYZ(gui_a.pure)
cli_pyz = PYZ(cli_a.pure)
ask_pyz = PYZ(ask_a.pure)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name="EasyConnect",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=icon_file,
    version=str(VERSION_INFO) if VERSION_INFO.is_file() else None,
)
cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    [],
    exclude_binaries=True,
    name="easy-connect-cli",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon=icon_file,
    version=str(VERSION_INFO) if VERSION_INFO.is_file() else None,
)
ask_exe = EXE(
    ask_pyz,
    ask_a.scripts,
    [],
    exclude_binaries=True,
    name="easy-connect-askpass",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icon_file,
    version=str(VERSION_INFO) if VERSION_INFO.is_file() else None,
)

coll = COLLECT(
    gui_exe,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    cli_exe,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
    ask_exe,
    ask_a.binaries,
    ask_a.zipfiles,
    ask_a.datas,
    strip=False,
    upx=False,
    name="EasyConnect",
)
