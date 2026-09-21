from __future__ import annotations

from pathlib import Path

from PIL import Image


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "src" / "easy_connect" / "resources" / "icon.png"
    if not source.is_file():
        source = root / "ico.png"
    if not source.is_file():
        raise SystemExit("Icone nao encontrado (ico.png).")
    dest = Path(__file__).resolve().parent / "easyconnect.ico"
    image = Image.open(source).convert("RGBA")
    image.save(
        dest,
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(dest)


if __name__ == "__main__":
    main()
