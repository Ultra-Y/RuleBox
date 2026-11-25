"""生成 RuleBox 的 16×16 像素精灵。

配色取自 DawnBringer 16 色板（DB16，像素画常用的公开调色板），形状全部自绘；
统一 1px 深色描边，从左上受光。需要 Pillow；素材已提交到 assets/sprites/，
运行时不需要 Pillow。

    python tools/generate_sprites.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPRITE_DIR = ROOT / "assets" / "sprites"
DOCS = ROOT / "docs"

# DawnBringer 16（DB16）
C = {
    "ink": (20, 12, 28, 255),
    "wine": (68, 36, 52, 255),
    "midnight": (48, 52, 109, 255),
    "charcoal": (78, 74, 78, 255),
    "clay": (133, 76, 48, 255),
    "moss": (52, 101, 36, 255),
    "crimson": (208, 70, 72, 255),
    "stone": (117, 113, 97, 255),
    "cornflower": (89, 125, 206, 255),
    "amber": (210, 125, 44, 255),
    "steel": (133, 149, 161, 255),
    "leaf": (109, 170, 44, 255),
    "beige": (210, 170, 153, 255),
    "aqua": (109, 194, 202, 255),
    "lemon": (218, 212, 94, 255),
    "cream": (222, 238, 214, 255),
}


def canvas() -> Image.Image:
    return Image.new("RGBA", (16, 16), (0, 0, 0, 0))


def add_outline(image: Image.Image, color: tuple = C["ink"]) -> Image.Image:
    """给不透明区域补一圈 1px 描边（画在透明像素上，不覆盖原图）。"""
    pixels = image.load()
    width, height = image.size
    edge: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if pixels[x, y][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and pixels[nx, ny][3] != 0:
                    edge.append((x, y))
                    break
    for x, y in edge:
        pixels[x, y] = color
    return image


def draw_baba() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 13, 5, 15), radius=1, fill=C["amber"])
    draw.rounded_rectangle((10, 13, 12, 15), radius=1, fill=C["amber"])
    draw.rectangle((1, 8, 1, 11), fill=C["beige"])
    draw.rectangle((14, 8, 14, 11), fill=C["beige"])
    draw.ellipse((2, 2, 13, 13), fill=C["beige"])
    draw.arc((3, 3, 12, 12), start=175, end=285, fill=C["cream"], width=1)
    draw.rectangle((5, 6, 6, 7), fill=C["ink"])
    draw.rectangle((9, 6, 10, 7), fill=C["ink"])
    draw.point((5, 6), fill=C["cream"])
    draw.point((9, 6), fill=C["cream"])
    draw.rectangle((7, 10, 8, 10), fill=C["wine"])
    draw.point((6, 9), fill=C["crimson"])
    draw.point((9, 9), fill=C["crimson"])
    return add_outline(image)


def draw_dog() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((12, 3, 13, 6), fill=C["clay"])
    draw.rectangle((13, 2, 14, 4), fill=C["clay"])
    draw.rectangle((3, 11, 4, 15), fill=C["clay"])
    draw.rectangle((5, 11, 6, 15), fill=C["clay"])
    draw.rectangle((9, 11, 10, 15), fill=C["clay"])
    draw.rectangle((11, 11, 12, 15), fill=C["clay"])
    draw.rounded_rectangle((3, 6, 12, 12), radius=2, fill=C["clay"])
    draw.rectangle((4, 9, 11, 10), fill=C["beige"])
    draw.rounded_rectangle((1, 2, 6, 9), radius=2, fill=C["clay"])
    draw.rectangle((1, 5, 4, 8), fill=C["beige"])
    draw.polygon([(2, 1), (5, 1), (4, 4)], fill=C["amber"])
    draw.rectangle((4, 4, 5, 5), fill=C["ink"])
    draw.point((4, 4), fill=C["cream"])
    draw.point((1, 5), fill=C["ink"])
    draw.point((2, 8), fill=C["crimson"])
    draw.rectangle((5, 8, 6, 9), fill=C["crimson"])
    return add_outline(image)


def draw_cat() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((12, 10, 14, 11), fill=C["charcoal"])
    draw.rectangle((13, 7, 14, 10), fill=C["charcoal"])
    draw.rounded_rectangle((4, 8, 12, 14), radius=3, fill=C["charcoal"])
    draw.rounded_rectangle((3, 4, 12, 10), radius=3, fill=C["charcoal"])
    draw.polygon([(3, 5), (5, 4), (3, 1)], fill=C["charcoal"])
    draw.polygon([(12, 5), (10, 4), (12, 1)], fill=C["charcoal"])
    draw.point((4, 3), fill=C["crimson"])
    draw.point((11, 3), fill=C["crimson"])
    draw.rectangle((5, 6, 6, 7), fill=C["ink"])
    draw.rectangle((9, 6, 10, 7), fill=C["ink"])
    draw.point((5, 6), fill=C["lemon"])
    draw.point((9, 6), fill=C["lemon"])
    draw.point((7, 8), fill=C["crimson"])
    draw.point((8, 8), fill=C["crimson"])
    draw.line((0, 8, 2, 8), fill=C["steel"])
    draw.line((13, 8, 15, 8), fill=C["steel"])
    draw.rectangle((6, 9, 7, 9), fill=C["beige"])
    draw.rectangle((9, 9, 10, 9), fill=C["beige"])
    return add_outline(image)


def draw_flower() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((7, 9, 8, 15), fill=C["moss"])
    draw.ellipse((3, 11, 6, 13), fill=C["leaf"])
    draw.ellipse((9, 10, 12, 12), fill=C["leaf"])
    draw.ellipse((6, 1, 9, 4), fill=C["crimson"])
    draw.ellipse((2, 4, 5, 7), fill=C["crimson"])
    draw.ellipse((10, 4, 13, 7), fill=C["crimson"])
    draw.ellipse((6, 8, 9, 11), fill=C["crimson"])
    draw.ellipse((6, 4, 9, 7), fill=C["lemon"])
    draw.point((7, 5), fill=C["cream"])
    return add_outline(image)


def draw_tree() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((6, 9, 9, 15), fill=C["clay"])
    draw.rectangle((6, 9, 6, 15), fill=C["amber"])
    draw.ellipse((2, 1, 13, 9), fill=C["moss"])
    draw.ellipse((4, 2, 8, 5), fill=C["leaf"])
    draw.ellipse((9, 4, 12, 6), fill=C["leaf"])
    draw.ellipse((3, 6, 5, 8), fill=C["leaf"])
    return add_outline(image)


def draw_fish() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.polygon([(11, 8), (15, 4), (15, 12)], fill=C["midnight"])
    draw.polygon([(5, 5), (7, 2), (9, 5)], fill=C["midnight"])
    draw.ellipse((1, 5, 11, 11), fill=C["cornflower"])
    draw.ellipse((3, 8, 10, 11), fill=C["aqua"])
    draw.rectangle((6, 6, 6, 10), fill=C["aqua"])
    draw.rectangle((3, 6, 4, 7), fill=C["ink"])
    draw.point((3, 6), fill=C["cream"])
    draw.point((9, 5), fill=C["cream"])
    return add_outline(image)


def draw_wall() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 15, 15), fill=C["ink"])
    courses = (
        (1, ((1, 6), (8, 14))),
        (5, ((1, 3), (5, 10), (12, 14))),
        (9, ((1, 6), (8, 14))),
        (13, ((1, 3), (5, 10), (12, 14))),
    )
    for y, bricks in courses:
        for x0, x1 in bricks:
            draw.rectangle((x0, y, x1, y + 2), fill=C["stone"])
            draw.line((x0, y, x1, y), fill=C["steel"])
            draw.line((x0, y + 2, x1, y + 2), fill=C["charcoal"])
    return image


def draw_box() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((2, 2, 13, 14), radius=2, fill=C["clay"])
    draw.rounded_rectangle((2, 2, 13, 5), radius=2, fill=C["amber"])
    draw.rectangle((4, 6, 11, 12), fill=C["amber"])
    draw.line((4, 6, 11, 12), fill=C["clay"], width=2)
    draw.line((11, 6, 4, 12), fill=C["clay"], width=2)
    draw.rectangle((3, 3, 3, 3), fill=C["cream"])
    draw.rectangle((12, 3, 12, 3), fill=C["cream"])
    draw.rectangle((3, 13, 3, 13), fill=C["cream"])
    draw.rectangle((12, 13, 12, 13), fill=C["cream"])
    return add_outline(image)


def draw_flag() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 14, 7, 15), fill=C["steel"])
    draw.rectangle((4, 1, 5, 14), fill=C["steel"])
    draw.line((4, 1, 4, 13), fill=C["cream"])
    draw.polygon([(6, 2), (15, 4), (6, 7)], fill=C["leaf"])
    draw.polygon([(6, 5), (12, 5), (6, 7)], fill=C["moss"])
    return add_outline(image)


def draw_water() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((1, 5, 14, 13), fill=C["cornflower"])
    draw.rectangle((1, 7, 14, 7), fill=C["aqua"])
    draw.rectangle((1, 10, 14, 10), fill=C["aqua"])
    draw.rectangle((1, 12, 14, 13), fill=C["midnight"])
    for x in (2, 6, 10):
        draw.rectangle((x, 5, x + 1, 5), fill=C["cream"])
    for x in (4, 8, 12):
        draw.rectangle((x, 8, x, 8), fill=C["cream"])
    return add_outline(image)


def draw_fire() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [(8, 1), (10, 4), (12, 5), (13, 9), (11, 13), (8, 15), (5, 13), (3, 9), (4, 5), (6, 4)],
        fill=C["crimson"],
    )
    draw.polygon([(8, 4), (10, 7), (11, 10), (8, 13), (5, 10), (6, 7)], fill=C["amber"])
    draw.polygon([(8, 8), (9, 10), (8, 12), (7, 10)], fill=C["lemon"])
    draw.point((8, 9), fill=C["cream"])
    return add_outline(image)


def draw_rock() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [(3, 14), (2, 10), (4, 5), (8, 3), (12, 5), (14, 9), (12, 13), (6, 15)],
        fill=C["stone"],
    )
    draw.polygon([(5, 5), (8, 4), (10, 6), (7, 8)], fill=C["steel"])
    draw.polygon([(9, 9), (13, 8), (12, 12), (9, 13)], fill=C["charcoal"])
    draw.point((8, 5), fill=C["cream"])
    return add_outline(image)


def draw_door() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 1, 12, 15), radius=1, fill=C["clay"])
    draw.rectangle((5, 3, 10, 7), fill=C["amber"])
    draw.rectangle((5, 9, 10, 13), fill=C["amber"])
    draw.line((4, 2, 4, 14), fill=C["beige"])
    draw.rectangle((9, 8, 10, 9), fill=C["lemon"])
    draw.point((9, 8), fill=C["cream"])
    return add_outline(image)


def draw_key() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 1, 11, 8), outline=C["lemon"], width=2)
    draw.rectangle((7, 7, 8, 15), fill=C["lemon"])
    draw.rectangle((8, 11, 10, 12), fill=C["lemon"])
    draw.rectangle((8, 13, 9, 14), fill=C["lemon"])
    draw.line((5, 3, 6, 3), fill=C["cream"])
    draw.rectangle((7, 8, 7, 13), fill=C["cream"])
    return add_outline(image)


def draw_portal() -> Image.Image:
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((1, 1, 14, 14), fill=C["wine"])
    draw.ellipse((3, 3, 12, 12), fill=C["cornflower"])
    draw.ellipse((6, 6, 9, 9), fill=C["cream"])
    draw.point((2, 7), fill=C["cream"])
    draw.point((13, 8), fill=C["cream"])
    draw.point((7, 1), fill=C["cream"])
    draw.point((8, 14), fill=C["cream"])
    return add_outline(image)


SPRITES = {
    "baba": draw_baba,
    "wall": draw_wall,
    "box": draw_box,
    "flag": draw_flag,
    "water": draw_water,
    "fire": draw_fire,
    "rock": draw_rock,
    "door": draw_door,
    "key": draw_key,
    "portal": draw_portal,
    "dog": draw_dog,
    "cat": draw_cat,
    "flower": draw_flower,
    "tree": draw_tree,
    "fish": draw_fish,
}


def main() -> None:
    SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    for name, painter in SPRITES.items():
        painter().save(SPRITE_DIR / f"{name}.png")

    columns = 5
    rows = (len(SPRITES) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * 72, rows * 72), (24, 26, 34, 255))
    for index, name in enumerate(SPRITES):
        sprite = Image.open(SPRITE_DIR / f"{name}.png").resize((64, 64), Image.NEAREST)
        x = (index % columns) * 72 + 4
        y = (index // columns) * 72 + 4
        sheet.alpha_composite(sprite, (x, y))
    sheet.save(DOCS / "sprites.png")
    print("generated", len(SPRITES), "sprites")


if __name__ == "__main__":
    main()
