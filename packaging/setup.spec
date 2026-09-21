# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.building.api import EXE, PYZ
from PyInstaller.building.build_main import Analysis

SPECDIR = Path(SPECPATH)
ROOT = SPECDIR.parent
PAYLOAD = ROOT / "dist" / "EasyConnect"
ICON = SPECDIR / "easyconnect.ico"
ICON_PNG = ROOT / "src" / "easy_connect" / "resources" / "icon.png"
VERSION_INFO = SPECDIR / "file_version_info.txt"

datas = []
if PAYLOAD.is_dir():
    datas.append((str(PAYLOAD), "payload"))
if ICON.is_file():
    datas.append((str(ICON), "."))
if ICON_PNG.is_file():
    datas.append((str(ICON_PNG), "."))

a = Analysis(
    [str(SPECDIR / "windows_setup.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PySide6", "shiboken6"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="EasyConnect-Setup",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(ICON) if ICON.is_file() else None,
    version=str(VERSION_INFO) if VERSION_INFO.is_file() else None,
    uac_admin=True,
)
