"""生成 RuleBox 的精灵文件、素材表与动画 GIF。

主角和物件美术都来自作者提供的 64×64 像素图：
- 主角：`tools/source/baba-{front,side,back}.png`
- 物件：`tools/source/ai/<id>.png`（第 0 帧）
- 动画：`tools/source/anim/<id>_<frame>.png`（第 1..n 帧）

本脚本只负责选帧、写盘和合成素材表/GIF，不参与绘制。

    python tools/generate_sprites.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rulebox.ui.sprites import ANIMATIONS  # noqa: E402

SPRITE_DIR = ROOT / "assets" / "sprites"
DOCS = ROOT / "docs"
SOURCE = ROOT / "tools" / "source"
AI_DIR = SOURCE / "ai"
ANIM_DIR = SOURCE / "anim"
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


def _pulse(image: Image.Image) -> Image.Image:
    """第 2 帧做一次很轻的亮度呼吸，保持像素和轮廓不动。"""
    rgb = ImageEnhance.Brightness(image.convert("RGB")).enhance(1.08)
    return Image.merge("RGBA", (*rgb.split(), image.getchannel("A")))


BABA_SOURCES = {"front": "front", "up": "back", "back": "back", "side": "side"}


def baba_sprite(view: str, frame: int = 0) -> Image.Image:
    source = BABA_SOURCES.get(view, "front")
    image = Image.open(SOURCE / f"baba-{source}.png").convert("RGBA")
    return _pulse(image) if frame else image


def _wall_tile() -> Image.Image:
    """把墙的立体边框裁掉，让相邻墙格能接上（不再看到每格的边线）。"""
    image = Image.open(AI_DIR / "wall.png").convert("RGBA")
    image = image.crop((4, 4, 60, 60))
    return image.resize((64, 64), Image.Resampling.LANCZOS)


def render(name: str, frame: int = 0) -> Image.Image:
    if name == "baba":
        return baba_sprite("front", frame)
    if name == "baba-up":
        return baba_sprite("back", frame)
    if name == "baba-side":
        return baba_sprite("side", frame)
    if name == "wall":
        return _wall_tile()
    if frame == 0:
        return Image.open(AI_DIR / f"{name}.png").convert("RGBA")
    return Image.open(ANIM_DIR / f"{name}_{frame}.png").convert("RGBA")


def frame_numbers(name: str) -> tuple[int, ...]:
    if name not in ANIMATIONS:
        return (0,)
    return tuple(sorted(set(ANIMATIONS[name][1])))


def frame_at(name: str, step: int) -> int:
    """素材表/GIF 里第 step 步该画哪一帧。"""
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
        sprite = render(name, frame).resize((cell - 8, cell - 8), Image.NEAREST)
        x = (index % columns) * cell + 4
        y = (index // columns) * cell + 4
        sheet.alpha_composite(sprite, (x, y))
    return sheet


def build_views_sheet() -> Image.Image:
    """三视角 × 两帧的展示图（docs/sprites_views.png）。"""
    cell = 120
    sheet = Image.new("RGBA", (6 * cell, cell), (24, 26, 34, 255))
    index = 0
    for view in ("front", "back", "side"):
        for frame in (0, 1):
            sprite = baba_sprite(view, frame).resize((cell - 16, cell - 16), Image.NEAREST)
            sheet.alpha_composite(sprite, (index * cell + 8, 8))
            index += 1
    return sheet


def main() -> None:
    SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    for name in SPRITES:
        for frame in frame_numbers(name):
            suffix = "" if frame == 0 else f"-{frame}"
            render(name, frame).save(SPRITE_DIR / f"{name}{suffix}.png")

    for view, suffix in (("up", "up"), ("side", "side")):
        for frame in (0, 1):
            image = baba_sprite(view, frame)
            name = f"baba-{suffix}" + ("" if frame == 0 else f"-{frame}")
            image.save(SPRITE_DIR / f"{name}.png")

    build_sheet(0).save(DOCS / "sprites.png")
    build_views_sheet().save(DOCS / "sprites_views.png")

    frames = [build_sheet(step) for step in range(12)]
    frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64) for frame in frames]
    frames[0].save(
        DOCS / "sprites_anim.gif",
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
        optimize=False,
    )
    print("generated", len(SPRITES), "sprites,", len(ANIMATIONS), "animated")


if __name__ == "__main__":
    main()
