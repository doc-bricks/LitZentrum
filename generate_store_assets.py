from __future__ import annotations

from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_ICON = PROJECT_ROOT / "LitZentrum.ico"
STORE_ASSETS_DIR = PROJECT_ROOT / "store_assets"


def _render_centered_wide_icon(icon: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    target_height = size[1]
    scaled = icon.resize((target_height, target_height), Image.LANCZOS)
    x = (size[0] - target_height) // 2
    canvas.paste(scaled, (x, 0), scaled)
    return canvas


def generate_store_assets() -> list[Path]:
    STORE_ASSETS_DIR.mkdir(exist_ok=True)

    icon = Image.open(SOURCE_ICON).convert("RGBA")
    targets = {
        "Square44x44Logo.png": icon.resize((44, 44), Image.LANCZOS),
        "Square150x150Logo.png": icon.resize((150, 150), Image.LANCZOS),
        "Square310x310Logo.png": icon.resize((310, 310), Image.LANCZOS),
        "Wide310x150Logo.png": _render_centered_wide_icon(icon, (310, 150)),
        "StoreLogo.png": icon.resize((50, 50), Image.LANCZOS),
    }

    written: list[Path] = []
    for name, image in targets.items():
        target = STORE_ASSETS_DIR / name
        image.save(target)
        written.append(target)
    return written


if __name__ == "__main__":
    for path in generate_store_assets():
        print(path)
