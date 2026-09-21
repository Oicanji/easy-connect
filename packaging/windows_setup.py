from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import winreg
from pathlib import Path


APP_NAME = "Easy Connect"
APP_VERSION = "0.0.4"
PUBLISHER = "Easy Connect"
EXE_NAME = "EasyConnect.exe"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\EasyConnect"

BG = "#16181d"
SIDE = "#10141a"
CARD = "#1e232b"
BORDER = "#2c3440"
TEXT = "#e6e8ec"
MUTED = "#9aa3ae"
ACCENT = "#2f9e8f"
ACCENT_HOVER = "#3cb5a5"
ACCENT_TEXT = "#08110f"
INPUT = "#12151a"
DANGER = "#e07a7f"
BTN = "#242b34"
BTN_HOVER = "#2c3440"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def payload_dir() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / "payload"
    return Path(__file__).resolve().parents[1] / "dist" / "EasyConnect"


def bundled_file(*parts: str) -> Path | None:
    names = [Path(*parts)]
    filename = parts[-1] if parts else ""
    bases: list[Path] = []
    if is_frozen():
        meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        bases.append(meipass)
        bases.append(meipass / "payload" / "_internal" / "easy_connect" / "resources")
    else:
        root = Path(__file__).resolve().parents[1]
        bases.append(root)
        bases.append(root / "packaging")
        bases.append(root / "src" / "easy_connect" / "resources")
    seen: set[Path] = set()
    for base in bases:
        for name in (*names, Path(filename) if filename else None):
            if name is None:
                continue
            path = base / name
            if path in seen:
                continue
            seen.add(path)
            if path.is_file():
                return path
    return None


def user_install_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "Programs" / "EasyConnect"


def program_files_dir() -> Path:
    base = os.environ.get("ProgramFiles") or r"C:\Program Files"
    return Path(base) / "EasyConnect"


def default_install_dir() -> Path:
    return program_files_dir()


def special_folder(csidl: int) -> Path:
    from ctypes import wintypes

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
    return Path(buf.value)


def desktop_dir() -> Path:
    return special_folder(0x19 if is_admin() else 0)


def start_menu_dir() -> Path:
    return special_folder(0x17 if is_admin() else 2) / APP_NAME


def uninstall_root():
    return winreg.HKEY_LOCAL_MACHINE if is_admin() else winreg.HKEY_CURRENT_USER


def powershell() -> str:
    return str(
        Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / "System32"
        / "WindowsPowerShell"
        / "v1.0"
        / "powershell.exe"
    )


def quote_ps(value: str) -> str:
    return value.replace("'", "''")


def create_shortcut(link: Path, target: Path, workdir: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    script = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{quote_ps(str(link))}'); "
        f"$s.TargetPath = '{quote_ps(str(target))}'; "
        f"$s.WorkingDirectory = '{quote_ps(str(workdir))}'; "
        f"$s.IconLocation = '{quote_ps(str(target))},0'; "
        f"$s.Save()"
    )
    subprocess.run(
        [powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def estimated_size_kb(install_dir: Path) -> int:
    total = 0
    for path in install_dir.rglob("*"):
        if path.is_file():
            total += path.stat().st_size
    return max(int(total / 1024), 1)


def write_uninstall_registry(install_dir: Path) -> None:
    key = winreg.CreateKey(uninstall_root(), UNINSTALL_KEY)
    uninstall = install_dir / "uninstall.cmd"
    winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
    winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
    winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
    winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(install_dir / EXE_NAME))
    winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstall))
    winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, estimated_size_kb(install_dir))
    winreg.CloseKey(key)
    if is_admin():
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
        except OSError:
            pass


def write_uninstaller(install_dir: Path, desktop_link: Path, start_link: Path) -> None:
    uninstall_ps1 = install_dir / "uninstall.ps1"
    uninstall_cmd = install_dir / "uninstall.cmd"
    hive = "HKLM" if is_admin() else "HKCU"
    elevate = ""
    if is_admin():
        elevate = (
            "net session >nul 2>&1\r\n"
            "if %errorLevel% neq 0 (\r\n"
            f'  "{powershell()}" -NoProfile -ExecutionPolicy Bypass -Command '
            "\"Start-Process -FilePath '%~f0' -Verb RunAs\"\r\n"
            "  exit /b\r\n"
            ")\r\n"
        )
    ps = (
        f'$ErrorActionPreference = "SilentlyContinue"\n'
        f'Remove-Item -LiteralPath "{desktop_link}" -Force\n'
        f'Remove-Item -LiteralPath "{start_link}" -Force\n'
        f'Remove-Item -LiteralPath "{start_menu_dir()}" -Recurse -Force\n'
        f'Remove-Item -Path "{hive}:\\{UNINSTALL_KEY}" -Recurse -Force\n'
        f'Start-Sleep -Seconds 1\n'
        f'Remove-Item -LiteralPath "{install_dir}" -Recurse -Force\n'
    )
    uninstall_ps1.write_text(ps, encoding="utf-8")
    uninstall_cmd.write_text(
        "@echo off\r\n"
        + elevate
        + f'"{powershell()}" -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"\r\n',
        encoding="utf-8",
    )


def copy_payload(source: Path, dest: Path, progress) -> None:
    if dest.exists():
        try:
            shutil.rmtree(dest)
        except OSError as exc:
            raise RuntimeError(
                "Não foi possível substituir os arquivos. Feche o Easy Connect e tente novamente."
            ) from exc
    files = [path for path in source.rglob("*") if path.is_file()]
    total = max(len(files), 1)
    for index, path in enumerate(files, start=1):
        relative = path.relative_to(source)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        progress(index, total)


def install(dest: Path, desktop: bool, progress, status) -> Path:
    source = payload_dir()
    if not source.is_dir():
        raise FileNotFoundError("Pacote do Easy Connect não encontrado.")
    status("Copiando arquivos...")
    copy_payload(source, dest, progress)
    exe = dest / EXE_NAME
    if not exe.is_file():
        raise FileNotFoundError("EasyConnect.exe não foi copiado.")
    start_dir = start_menu_dir()
    start_link = start_dir / f"{APP_NAME}.lnk"
    desktop_link = desktop_dir() / f"{APP_NAME}.lnk"
    status("Criando atalhos...")
    create_shortcut(start_link, exe, dest)
    if desktop:
        create_shortcut(desktop_link, exe, dest)
    elif desktop_link.is_file():
        desktop_link.unlink()
    status("Registrando desinstalação...")
    write_uninstaller(dest, desktop_link, start_link)
    write_uninstall_registry(dest)
    status("Instalação concluída.")
    return exe


def relaunch_as_admin(extra_args: list[str] | None = None) -> bool:
    args = extra_args if extra_args is not None else sys.argv[1:]
    if is_frozen():
        executable = sys.executable
        params = subprocess.list2cmdline(args)
    else:
        executable = sys.executable
        params = subprocess.list2cmdline([str(Path(__file__).resolve()), *args])
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    return int(rc) > 32


def enable_dark_titlebar(window) -> None:
    window.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    if not hwnd:
        hwnd = window.winfo_id()
    value = ctypes.c_int(1)
    for attr in (20, 19):
        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
            )
        except Exception:
            pass


def parse_resume() -> tuple[Path | None, bool, bool]:
    dest = None
    desktop = True
    auto = False
    args = sys.argv[1:]
    index = 0
    while index < len(args):
        current = args[index]
        if current == "--resume":
            auto = True
        elif current == "--dir" and index + 1 < len(args):
            dest = Path(args[index + 1])
            index += 1
        elif current == "--desktop" and index + 1 < len(args):
            desktop = args[index + 1] != "0"
            index += 1
        index += 1
    return dest, desktop, auto


def run_gui() -> int:
    import tkinter as tk
    from tkinter import filedialog

    resume_dir, resume_desktop, auto_install = parse_resume()

    root = tk.Tk()
    root.title(f"Instalar {APP_NAME}")
    root.configure(bg=BG)
    width, height = 760, 500
    x = max((root.winfo_screenwidth() - width) // 2, 0)
    y = max((root.winfo_screenheight() - height) // 2, 0)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)
    ico = bundled_file("easyconnect.ico")
    if ico is not None:
        try:
            root.iconbitmap(default=str(ico))
        except tk.TclError:
            pass
    enable_dark_titlebar(root)

    dest_var = tk.StringVar(value=str(resume_dir or default_install_dir()))
    desktop_var = tk.BooleanVar(value=resume_desktop)
    status_var = tk.StringVar(value="")
    progress_var = tk.DoubleVar(value=0)
    installed_exe: list[Path] = []

    shell = tk.Frame(root, bg=BG)
    shell.pack(fill="both", expand=True)

    side = tk.Frame(shell, bg=SIDE, width=240)
    side.pack(side="left", fill="y")
    side.pack_propagate(False)
    side_inner = tk.Frame(side, bg=SIDE)
    side_inner.pack(fill="both", expand=True, padx=28, pady=32)

    logo_path = bundled_file("icon.png")
    if logo_path is not None:
        try:
            logo = tk.PhotoImage(file=str(logo_path))
            biggest = max(logo.width(), logo.height())
            factor = max(1, (biggest + 71) // 72)
            if factor > 1:
                logo = logo.subsample(factor, factor)
            root._logo = logo
            tk.Label(side_inner, image=logo, bg=SIDE).pack(anchor="w")
        except tk.TclError:
            pass

    tk.Label(
        side_inner,
        text=APP_NAME,
        bg=SIDE,
        fg=TEXT,
        font=("Segoe UI", 16, "bold"),
        justify="left",
    ).pack(anchor="w", pady=(18, 2))
    tk.Label(
        side_inner,
        text=f"Versão {APP_VERSION}",
        bg=SIDE,
        fg=MUTED,
        font=("Segoe UI", 10),
    ).pack(anchor="w")
    tk.Frame(side_inner, bg=BORDER, height=1).pack(fill="x", pady=22)
    tk.Label(
        side_inner,
        text="Instalador para Windows",
        bg=SIDE,
        fg=MUTED,
        font=("Segoe UI", 9),
        wraplength=180,
        justify="left",
    ).pack(anchor="w")

    badge = tk.Label(
        side_inner,
        text="Administrador" if is_admin() else "Usuário atual",
        bg="#1a3d38" if is_admin() else "#2a2320",
        fg=ACCENT if is_admin() else "#d7b56d",
        font=("Segoe UI", 8, "bold"),
        padx=8,
        pady=4,
    )
    badge.pack(anchor="w", pady=(18, 0))

    main = tk.Frame(shell, bg=BG)
    main.pack(side="left", fill="both", expand=True)
    content = tk.Frame(main, bg=BG)
    content.pack(fill="both", expand=True, padx=36, pady=32)

    pages = tk.Frame(content, bg=BG)
    pages.pack(fill="both", expand=True)
    setup_page = tk.Frame(pages, bg=BG)
    done_page = tk.Frame(pages, bg=BG)
    for page in (setup_page, done_page):
        page.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Label(
        setup_page,
        text="Instalar o Easy Connect",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        justify="left",
    ).pack(fill="x")
    tk.Label(
        setup_page,
        text=(
            "O aplicativo será instalado neste computador, com atalho no menu Iniciar. "
            "Com permissão de administrador, a pasta padrão é Program Files."
        ),
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10),
        wraplength=430,
        justify="left",
        anchor="w",
    ).pack(fill="x", pady=(8, 22))

    tk.Label(
        setup_page,
        text="PASTA DE INSTALAÇÃO",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 8, "bold"),
        anchor="w",
    ).pack(fill="x")

    path_row = tk.Frame(setup_page, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    path_row.pack(fill="x", pady=(6, 0))
    entry = tk.Entry(
        path_row,
        textvariable=dest_var,
        bg=CARD,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        font=("Segoe UI", 10),
        bd=0,
    )
    entry.pack(side="left", fill="x", expand=True, padx=12, ipady=10)

    def browse() -> None:
        chosen = filedialog.askdirectory(initialdir=dest_var.get() or str(default_install_dir()))
        if chosen:
            dest_var.set(chosen)

    browse_btn = tk.Button(
        path_row,
        text="Procurar",
        command=browse,
        bg=BTN,
        fg=TEXT,
        activebackground=BTN_HOVER,
        activeforeground=TEXT,
        relief="flat",
        bd=0,
        font=("Segoe UI", 9),
        cursor="hand2",
        padx=12,
        pady=8,
    )
    browse_btn.pack(side="right", padx=(0, 6), pady=6)

    desktop_box = tk.Checkbutton(
        setup_page,
        text="Criar atalho na área de trabalho",
        variable=desktop_var,
        bg=BG,
        fg=TEXT,
        activebackground=BG,
        activeforeground=TEXT,
        selectcolor=INPUT,
        highlightthickness=0,
        font=("Segoe UI", 10),
        anchor="w",
    )
    desktop_box.pack(fill="x", pady=(16, 0))

    admin_hint = tk.Label(
        setup_page,
        text="",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9),
        wraplength=430,
        justify="left",
        anchor="w",
    )
    admin_hint.pack(fill="x", pady=(8, 0))

    spacer = tk.Frame(setup_page, bg=BG)
    spacer.pack(fill="both", expand=True)

    bar_wrap = tk.Frame(setup_page, bg=INPUT, height=8)
    bar_wrap.pack(fill="x", pady=(8, 0))
    bar_wrap.pack_propagate(False)
    bar_fill = tk.Frame(bar_wrap, bg=ACCENT, width=0)
    bar_fill.place(x=0, y=0, relheight=1, width=0)

    status_label = tk.Label(
        setup_page,
        textvariable=status_var,
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9),
        wraplength=430,
        justify="left",
        anchor="w",
    )
    status_label.pack(fill="x", pady=(8, 0))

    tk.Label(
        done_page,
        text="Instalação concluída",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        justify="left",
    ).pack(fill="x")
    tk.Label(
        done_page,
        text="O Easy Connect está pronto para uso. Você pode abrir o aplicativo agora ou fechar o instalador.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10),
        wraplength=430,
        justify="left",
        anchor="w",
    ).pack(fill="x", pady=(8, 0))

    footer = tk.Frame(main, bg=BG)
    footer.pack(fill="x", padx=36, pady=(0, 28))
    tk.Frame(footer, bg=BORDER, height=1).pack(fill="x", pady=(0, 16))
    footer_right = tk.Frame(footer, bg=BG)
    footer_right.pack(side="right")

    def set_progress(pct: float) -> None:
        progress_var.set(pct)
        bar_wrap.update_idletasks()
        width_px = bar_wrap.winfo_width()
        bar_fill.place(width=max(int(width_px * min(max(pct, 0), 100) / 100), 0))

    def set_busy(busy: bool) -> None:
        state = "disabled" if busy else "normal"
        entry.configure(state=state)
        browse_btn.configure(state=state)
        desktop_box.configure(state=state)
        install_btn.configure(state=state)
        elevate_btn.configure(state=state)

    def refresh_hint(*_args) -> None:
        if is_admin():
            admin_hint.configure(
                text="Instalando com permissão de administrador. Atalhos e registro valem para todos os usuários."
            )
            elevate_btn.pack_forget()
        else:
            admin_hint.configure(
                text="Sem elevação, a instalação fica só no seu usuário. Use administrador para instalar em Program Files."
            )
            elevate_btn.pack(side="left")

    def on_cancel() -> None:
        root.destroy()

    def on_elevate() -> None:
        args = [
            "--resume",
            "--dir",
            dest_var.get().strip() or str(program_files_dir()),
            "--desktop",
            "1" if desktop_var.get() else "0",
        ]
        if dest_var.get().strip() == str(user_install_dir()):
            args = ["--resume", "--dir", str(program_files_dir()), "--desktop", "1" if desktop_var.get() else "0"]
        if relaunch_as_admin(args):
            root.destroy()
        else:
            status_var.set("A permissão de administrador foi recusada.")
            status_label.configure(fg=DANGER)

    def on_install() -> None:
        dest = Path(dest_var.get().strip() or str(default_install_dir()))
        if not is_admin() and _needs_admin(dest):
            if relaunch_as_admin(
                [
                    "--resume",
                    "--dir",
                    str(dest),
                    "--desktop",
                    "1" if desktop_var.get() else "0",
                ]
            ):
                root.destroy()
                return
            status_var.set("Esta pasta exige permissão de administrador.")
            status_label.configure(fg=DANGER)
            return
        set_busy(True)
        status_label.configure(fg=MUTED)
        try:
            def progress(done: int, total: int) -> None:
                set_progress(done / total * 100)
                root.update_idletasks()

            def status(text: str) -> None:
                status_var.set(text)
                root.update_idletasks()

            exe = install(dest, desktop_var.get(), progress, status)
            installed_exe.append(exe)
            set_progress(100)
            setup_page.lower()
            done_page.lift()
            install_btn.pack_forget()
            elevate_btn.pack_forget()
            close_btn.pack_forget()
            launch_btn.pack(side="right")
            close_btn.pack(side="right", padx=(0, 8))
            close_btn.configure(text="Fechar")
        except Exception as exc:
            status_var.set(str(exc))
            status_label.configure(fg=DANGER)
            set_busy(False)

    def on_launch() -> None:
        if installed_exe:
            subprocess.Popen([str(installed_exe[0])], cwd=str(installed_exe[0].parent))
        root.destroy()

    close_btn = tk.Button(
        footer_right,
        text="Cancelar",
        command=on_cancel,
        bg=BTN,
        fg=TEXT,
        activebackground=BTN_HOVER,
        activeforeground=TEXT,
        relief="flat",
        bd=0,
        font=("Segoe UI", 10),
        cursor="hand2",
        padx=16,
        pady=8,
        width=10,
    )

    install_btn = tk.Button(
        footer_right,
        text="Instalar",
        command=on_install,
        bg=ACCENT,
        fg=ACCENT_TEXT,
        activebackground=ACCENT_HOVER,
        activeforeground=ACCENT_TEXT,
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
        padx=18,
        pady=8,
        width=12,
    )
    install_btn.pack(side="right")
    close_btn.pack(side="right", padx=(0, 8))

    launch_btn = tk.Button(
        footer_right,
        text="Abrir aplicativo",
        command=on_launch,
        bg=ACCENT,
        fg=ACCENT_TEXT,
        activebackground=ACCENT_HOVER,
        activeforeground=ACCENT_TEXT,
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
        padx=18,
        pady=8,
    )

    elevate_btn = tk.Button(
        footer,
        text="Usar administrador",
        command=on_elevate,
        bg=BG,
        fg=ACCENT,
        activebackground=BG,
        activeforeground=ACCENT_HOVER,
        relief="flat",
        bd=0,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
    )

    def _hover(widget, bg, hover) -> None:
        widget.bind("<Enter>", lambda _e: widget.configure(bg=hover))
        widget.bind("<Leave>", lambda _e: widget.configure(bg=bg))

    _hover(install_btn, ACCENT, ACCENT_HOVER)
    _hover(close_btn, BTN, BTN_HOVER)
    _hover(browse_btn, BTN, BTN_HOVER)
    _hover(launch_btn, ACCENT, ACCENT_HOVER)

    refresh_hint()
    setup_page.lift()
    if auto_install and is_admin():
        root.after(200, on_install)
    root.mainloop()
    return 0


def _needs_admin(dest: Path) -> bool:
    try:
        dest.mkdir(parents=True, exist_ok=True)
        probe = dest / ".easyconnect_write_test"
        probe.write_bytes(b"ok")
        probe.unlink(missing_ok=True)
        return False
    except OSError:
        return True


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in {"--uninstall", "/uninstall"}:
        return 0
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
