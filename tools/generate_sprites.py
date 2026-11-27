"""用 `assets/sprites/` 里的 16×16 PNG 生成 docs 的素材表和动画 GIF。

素材本身由 `assets/sprites/` 直接维护，本脚本只做合成：
- `docs/sprites.png`：5 列素材表（每一帧按 ANIMATIONS 取）；
- `docs/sprites_views.png`：主角正/背/侧 × 两帧；
- `docs/sprites_anim.gif`：素材表的 12 步动画。

    python tools/generate_sprites.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rulebox.ui.sprites import ANIMATIONS  # noqa: E402

SPRITE_DIR = ROOT / "assets" / "sprites"
DOCS = ROOT / "docs"
GIF_STEP_MS = 110

SPRITES = [
    "baba",
    "wall",
    "box",
    "flag",
    "water",
    "fire",
    "rock",
    "door",
    "key",
    "portal",
    "dog",
    "cat",
    "flower",
    "tree",
    "fish",
    "lava",
]


def sprite_image(name: str, frame: int = 0) -> Image.Image:
    suffix = "" if frame == 0 else f"-{frame}"
    return Image.open(SPRITE_DIR / f"{name}{suffix}.png").convert("RGBA")


def frame_numbers(name: str) -> tuple[int, ...]:
    if name not in ANIMATIONS:
        return (0,)
    return tuple(sorted(set(ANIMATIONS[name][1])))


def frame_at(name: str, step: int) -> int:
    if name not in ANIMATIONS:
        return 0
    period, pattern = ANIMATIONS[name]
    return pattern[(step * GIF_STEP_MS // period) % len(pattern)]


def build_sheet(step: int, cell: int = 72) -> Image.Image:
    columns = 5
    rows = (len(SPRITES) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell, rows * cell), (24, 26, 34, 255))
    for index, name in enumerate(SPRITES):
        frame = frame_at(name, step)
        sprite = sprite_image(name, frame).resize((cell - 8, cell - 8), Image.Resampling.NEAREST)
        sheet.alpha_composite(sprite, ((index % columns) * cell + 4, (index // columns) * cell + 4))
    return sheet


def build_views_sheet() -> Image.Image:
    cell = 120
    sheet = Image.new("RGBA", (6 * cell, cell), (24, 26, 34, 255))
    index = 0
    for name in ("baba", "baba-up", "baba-side"):
        for frame in (0, 1):
            sprite = sprite_image(name, frame).resize((cell - 16, cell - 16), Image.Resampling.NEAREST)
            sheet.alpha_composite(sprite, (index * cell + 8, 8))
            index += 1
    return sheet


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)

    for name in SPRITES:
        for frame in frame_numbers(name):
            assert (SPRITE_DIR / (f"{name}.png" if frame == 0 else f"{name}-{frame}.png")).exists()

    build_sheet(0).save(DOCS / "sprites.png")
    build_views_sheet().save(DOCS / "sprites_views.png")

    frames = [build_sheet(step) for step in range(12)]
    frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64) for frame in frames]
    frames[0].save(
        DOCS / "sprites_anim.gif",
        save_all=True,
        append_images=frames[1:],
        duration=GIF_STEP_MS,
        loop=0,
        optimize=False,
    )
    print("built sheets for", len(SPRITES), "sprites,", len(ANIMATIONS), "animated")


if __name__ == "__main__":
    main()
