"""生成 RuleBox 的 16×16 像素精灵与待机动画帧。

配色取自 DawnBringer 16 色板（DB16，像素画常用的公开调色板），形状全部自绘；
统一的简单可爱风格：1px 深色描边、圆角/圆形轮廓、少量细节。
动画帧的周期/序列统一由 `src/rulebox/ui/sprites.py` 的 ANIMATIONS 定义，这里只负责画。

需要 Pillow；素材已提交到 assets/sprites/，运行时不需要 Pillow。

    python tools/generate_sprites.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rulebox.ui.sprites import ANIMATIONS  # noqa: E402

SPRITE_DIR = ROOT / "assets" / "sprites"
DOCS = ROOT / "docs"
GIF_STEP_MS = 110

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


def _baba_sword(draw, x: int, frame: int) -> None:
    """竖持的大剑：钢刃 + 金护手 + 酒红剑柄。"""
    draw.polygon([(x+4,2),(x+7,9),(x+7,38),(x+1,38),(x+1,9)], fill=C["steel"])
    draw.rectangle((x+5,4,x+5,37), fill=C["cream"])
    draw.rectangle((x+2,10,x+3,37), fill=C["beige"])
    draw.rectangle((x-1,38,x+9,42), fill=C["amber"])
    draw.rectangle((x-1,38,x+9,39), fill=C["cream"])
    draw.rectangle((x+3,42,x+5,48), fill=C["wine"])
    draw.rectangle((x+2,48,x+6,49), fill=C["lemon"])
    if frame == 1:
        draw.point((x+6, 10), fill=C["cream"])


def _baba_body(draw, facing: str) -> None:
    """三视角共用：金靴、红裤腿、金护胫、黑内衬、金胸甲、腰带、护肩、手臂。"""
    # 金靴
    draw.rounded_rectangle((18, 56, 30, 62), radius=2, fill=C["amber"])
    draw.rounded_rectangle((34, 56, 46, 62), radius=2, fill=C["amber"])
    draw.rectangle((18, 61, 30, 62), fill=C["clay"])
    draw.rectangle((34, 61, 46, 62), fill=C["clay"])
    draw.rectangle((18, 56, 30, 57), fill=C["cream"])
    draw.rectangle((34, 56, 46, 57), fill=C["cream"])
    # 红裤腿 + 金护胫
    draw.rectangle((22, 44, 29, 56), fill=C["wine"])
    draw.rectangle((35, 44, 42, 56), fill=C["wine"])
    draw.rectangle((22, 50, 29, 56), fill=C["amber"])
    draw.rectangle((35, 50, 42, 56), fill=C["amber"])
    draw.rectangle((23, 51, 24, 55), fill=C["cream"])
    draw.rectangle((36, 51, 37, 55), fill=C["cream"])
    # 黑色内衬
    draw.rounded_rectangle((21, 24, 43, 44), radius=3, fill=C["charcoal"])
    # 金色胸甲
    draw.rounded_rectangle((24, 26, 40, 38), radius=3, fill=C["amber"])
    draw.rectangle((25, 27, 26, 37), fill=C["cream"])
    draw.rectangle((38, 27, 39, 37), fill=C["clay"])
    draw.rectangle((24, 35, 40, 36), fill=C["clay"])
    # 腰带
    draw.rectangle((21, 39, 43, 43), fill=C["clay"])
    draw.rectangle((30, 39, 34, 43), fill=C["beige"])
    # 护肩
    draw.rounded_rectangle((11, 21, 23, 33), radius=4, fill=C["amber"])
    draw.rounded_rectangle((41, 21, 53, 33), radius=4, fill=C["amber"])
    draw.rectangle((12, 29, 22, 32), fill=C["clay"])
    draw.rectangle((42, 29, 52, 32), fill=C["clay"])
    draw.rectangle((13, 22, 21, 23), fill=C["cream"])
    draw.rectangle((43, 22, 51, 23), fill=C["cream"])
    # 手臂 + 金护腕
    if facing == "side":
        draw.rectangle((38, 32, 46, 42), fill=C["charcoal"])
        draw.rectangle((38, 37, 46, 44), fill=C["amber"])
        draw.rectangle((38, 44, 46, 47), fill=C["charcoal"])
    else:
        draw.rectangle((12, 32, 20, 42), fill=C["charcoal"])
        draw.rectangle((44, 32, 52, 42), fill=C["charcoal"])
        draw.rectangle((12, 37, 20, 44), fill=C["amber"])
        draw.rectangle((44, 37, 52, 44), fill=C["amber"])
        draw.rectangle((12, 44, 20, 47), fill=C["charcoal"])
        draw.rectangle((44, 44, 52, 47), fill=C["charcoal"])
    # 脖子
    draw.rectangle((28, 20, 36, 25), fill=C["charcoal"])


def _baba_head_front(draw, frame: int) -> None:
    glow = C["lemon"] if frame == 0 else C["amber"]
    # 金色头盔 + 盔顶冠脊
    draw.rounded_rectangle((23, 5, 41, 22), radius=6, fill=C["amber"])
    draw.rectangle((25, 6, 39, 9), fill=C["cream"])
    draw.polygon([(29, 0), (35, 0), (38, 6), (26, 6)], fill=C["amber"])
    draw.polygon([(30, 1), (34, 1), (36, 5), (28, 5)], fill=C["cream"])
    # 面甲 + 发光眼
    draw.rounded_rectangle((26, 11, 38, 21), radius=3, fill=C["charcoal"])
    draw.polygon([(27, 13), (31, 12), (31, 15), (27, 17)], fill=glow)
    draw.polygon([(37, 13), (33, 12), (33, 15), (37, 17)], fill=glow)
    draw.rectangle((28, 13, 29, 15), fill=C["amber"])
    draw.rectangle((35, 13, 36, 15), fill=C["amber"])
    # 白发 + 颈甲
    draw.rectangle((21, 13, 22, 24), fill=C["cream"])
    draw.rectangle((42, 13, 43, 24), fill=C["cream"])
    draw.point((20, 17), fill=C["cream"])
    draw.point((44, 17), fill=C["cream"])
    draw.rectangle((26, 21, 38, 23), fill=C["clay"])


def _baba_head_back(draw, frame: int) -> None:
    draw.rounded_rectangle((23, 5, 41, 22), radius=6, fill=C["amber"])
    draw.polygon([(29, 0), (35, 0), (38, 6), (26, 6)], fill=C["amber"])
    draw.polygon([(30, 1), (34, 1), (36, 5), (28, 5)], fill=C["cream"])
    draw.rounded_rectangle((23, 8, 41, 23), radius=3, fill=C["cream"])
    shift = 0 if frame == 0 else 1
    draw.rectangle((27 + shift, 9, 28 + shift, 23), fill=C["steel"])
    draw.rectangle((36 + shift, 9, 37 + shift, 23), fill=C["steel"])
    draw.rectangle((24, 21, 40, 23), fill=C["beige"])


def _baba_head_side(draw, frame: int) -> None:
    glow = C["lemon"] if frame == 0 else C["amber"]
    draw.rounded_rectangle((23, 5, 41, 22), radius=6, fill=C["amber"])
    draw.polygon([(29, 0), (35, 0), (38, 6), (26, 6)], fill=C["amber"])
    draw.polygon([(30, 1), (34, 1), (36, 5), (28, 5)], fill=C["cream"])
    # 侧面面甲 + 发光眼
    draw.rounded_rectangle((30, 11, 41, 21), radius=3, fill=C["charcoal"])
    draw.polygon([(38, 12), (41, 13), (41, 16), (38, 17)], fill=glow)
    draw.rectangle((39, 13, 40, 15), fill=C["amber"])
    # 白发在后
    draw.rectangle((21, 12, 23, 24), fill=C["cream"])
    draw.point((20, 16), fill=C["cream"])


def _baba_view(facing: str, frame: int) -> Image.Image:
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _baba_sword(draw, 46 if facing == "side" else 4, frame)
    _baba_body(draw, facing)
    heads = {"down": _baba_head_front, "up": _baba_head_back, "side": _baba_head_side}
    heads[facing](draw, frame)
    return add_outline(image)


def draw_baba(frame: int = 0) -> Image.Image:
    """主角正面（朝下）。"""
    return _baba_view("down", frame)


def draw_baba_up(frame: int = 0) -> Image.Image:
    """主角背面（朝上）。"""
    return _baba_view("up", frame)


def draw_baba_side(frame: int = 0) -> Image.Image:
    """主角侧面（朝右）；朝左时由渲染层水平翻转。"""
    return _baba_view("side", frame)


def draw_dog(frame: int = 0) -> Image.Image:
    """柴犬：橘色毛、白色里白、立耳、卷尾；第 2 帧卷尾上移。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    tan, white = C["amber"], C["cream"]
    lift = 0 if frame == 0 else 1
    draw.ellipse((10, 3 - lift, 14, 7 - lift), fill=tan)
    draw.ellipse((11, 4 - lift, 13, 6 - lift), fill=(0, 0, 0, 0))
    draw.rectangle((12, 5 - lift, 14, 8 - lift), fill=tan)
    for x in (4, 7, 10, 13):
        draw.rectangle((x, 10, x + 1, 12), fill=tan)
        draw.rectangle((x, 13, x + 1, 13), fill=white)
    draw.rounded_rectangle((4, 6, 13, 10), radius=2, fill=tan)
    draw.rectangle((4, 8, 6, 10), fill=white)
    draw.rectangle((7, 9, 12, 10), fill=white)
    draw.rounded_rectangle((1, 2, 7, 9), radius=2, fill=tan)
    draw.rectangle((1, 5, 4, 8), fill=white)
    draw.rectangle((1, 5, 2, 5), fill=C["ink"])
    draw.polygon([(2, 2), (4, 2), (3, 0)], fill=tan)
    draw.polygon([(5, 2), (7, 2), (6, 0)], fill=tan)
    draw.point((3, 1), fill=white)
    draw.point((6, 1), fill=white)
    draw.rectangle((3, 4, 4, 4), fill=C["ink"])
    draw.point((3, 4), fill=white)
    draw.point((3, 3), fill=white)
    draw.point((5, 3), fill=white)
    return add_outline(image)


def draw_cat(frame: int = 0) -> Image.Image:
    """灰猫：圆脑袋、尖耳朵、胡须；第 2 帧尾巴上移。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    tail_y = 0 if frame == 0 else 1
    draw.rectangle((12, 10 - tail_y, 14, 11 - tail_y), fill=C["charcoal"])
    draw.rectangle((13, 7 - tail_y, 14, 10 - tail_y), fill=C["charcoal"])
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


def draw_flower(frame: int = 0) -> Image.Image:
    """四瓣小花 + 黄芯，第 2 帧轻摆。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    dx = 1 if frame else 0
    draw.rectangle((7, 9, 8, 15), fill=C["moss"])
    draw.ellipse((3, 11, 6, 13), fill=C["leaf"])
    draw.ellipse((9, 10, 12, 12), fill=C["leaf"])
    draw.ellipse((6 + dx, 1, 9 + dx, 4), fill=C["crimson"])
    draw.ellipse((2 + dx, 4, 5 + dx, 7), fill=C["crimson"])
    draw.ellipse((10 + dx, 4, 13 + dx, 7), fill=C["crimson"])
    draw.ellipse((6 + dx, 8, 9 + dx, 11), fill=C["crimson"])
    draw.ellipse((6 + dx, 4, 9 + dx, 7), fill=C["lemon"])
    draw.point((7 + dx, 5), fill=C["cream"])
    return add_outline(image)


def draw_tree(frame: int = 0) -> Image.Image:
    """圆树冠 + 树干，第 2 帧轻轻摆动。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    dx = 1 if frame else 0
    draw.rectangle((6, 9, 9, 15), fill=C["clay"])
    draw.rectangle((6, 9, 6, 15), fill=C["amber"])
    draw.ellipse((2 + dx, 1, 13 + dx, 10), fill=C["moss"])
    draw.ellipse((4 + dx, 2, 9 + dx, 6), fill=C["leaf"])
    draw.point((6 + dx, 3), fill=C["cream"])
    return add_outline(image)


def draw_fish(frame: int = 0) -> Image.Image:
    """圆鱼：第 2 帧摆尾。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    if frame == 0:
        draw.polygon([(11, 8), (15, 4), (15, 12)], fill=C["midnight"])
    else:
        draw.polygon([(11, 8), (14, 5), (14, 11)], fill=C["midnight"])
    draw.polygon([(5, 5), (7, 2), (9, 5)], fill=C["midnight"])
    draw.ellipse((1, 5, 11, 11), fill=C["cornflower"])
    draw.ellipse((3, 8, 10, 11), fill=C["aqua"])
    draw.rectangle((6, 6, 6, 10), fill=C["aqua"])
    draw.rectangle((3, 6, 4, 7), fill=C["ink"])
    draw.point((3, 6), fill=C["cream"])
    draw.point((9, 5), fill=C["cream"])
    return add_outline(image)


def draw_wall(frame: int = 0) -> Image.Image:
    """简单的大块砖墙。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 15, 15), fill=C["ink"])
    for x0, y0, x1, y1 in ((0, 0, 6, 6), (8, 0, 14, 6), (0, 8, 6, 14), (8, 8, 14, 14)):
        draw.rounded_rectangle((x0, y0, x1, y1), radius=1, fill=C["stone"])
        draw.line((x0 + 1, y0 + 1, x1 - 1, y0 + 1), fill=C["steel"])
        draw.line((x0 + 1, y1 - 1, x1 - 1, y1 - 1), fill=C["charcoal"])
    return image


def draw_box(frame: int = 0) -> Image.Image:
    """简单木箱：浅色箱盖 + 交叉木条。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((2, 2, 13, 13), radius=2, fill=C["clay"])
    draw.rounded_rectangle((2, 2, 13, 4), radius=2, fill=C["amber"])
    draw.rectangle((4, 5, 11, 12), fill=C["amber"])
    draw.line((4, 5, 11, 12), fill=C["clay"], width=2)
    draw.line((11, 5, 4, 12), fill=C["clay"], width=2)
    draw.point((3, 3), fill=C["cream"])
    draw.point((12, 3), fill=C["cream"])
    return add_outline(image)


def draw_flag(frame: int = 0) -> Image.Image:
    """旗杆 + 飘动的小旗。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 14, 7, 15), fill=C["steel"])
    draw.rectangle((4, 1, 5, 14), fill=C["steel"])
    draw.line((4, 1, 4, 13), fill=C["cream"])
    if frame == 0:
        draw.polygon([(6, 2), (15, 4), (6, 7)], fill=C["leaf"])
        draw.polygon([(6, 5), (12, 5), (6, 7)], fill=C["moss"])
    else:
        draw.polygon([(6, 2), (13, 3), (15, 5), (12, 6), (6, 7)], fill=C["leaf"])
        draw.polygon([(6, 5), (11, 5), (13, 6), (6, 7)], fill=C["moss"])
    return add_outline(image)


def draw_water(frame: int = 0) -> Image.Image:
    """铺满格子的水：浅青底 + 三排错动的蓝色水波，4 帧循环。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    shift = frame * 2
    draw.rectangle((0, 0, 15, 15), fill=C["aqua"])
    for y, width, phase in ((2, 5, 0), (7, 6, 3), (12, 5, 5)):
        offset = (shift + phase) % 8
        for x in range(16):
            if (x + offset) % 8 < width:
                draw.point((x, y), fill=C["cornflower"])
                draw.point((x, y + 1), fill=C["cornflower"])
    for x, y in ((3, 5), (11, 1), (8, 10), (14, 14), (5, 15)):
        draw.point((x, y), fill=C["cream"])
    return image


def draw_lava(frame: int = 0) -> Image.Image:
    """铺满格子的岩浆：亮橙底 + 红色岩浆纹 + 气泡，3 帧翻动。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    shift = frame * 2
    draw.rectangle((0, 0, 15, 15), fill=C["amber"])
    for y, width, phase in ((3, 4, 1), (8, 5, 4), (13, 4, 6)):
        offset = (shift + phase) % 8
        for x in range(16):
            if (x + offset) % 8 < width:
                draw.point((x, y), fill=C["crimson"])
                draw.point((x, y + 1), fill=C["crimson"])
    for x, y in ((4, 5), (11, 2), (8, 11), (14, 7)):
        draw.point((x, y), fill=C["cream"])
    for x, y in ((2, 12), (9, 6)):
        draw.point((x, y), fill=C["wine"])
    return image


def draw_fire(frame: int = 0) -> Image.Image:
    """圆润的三层火苗，第 2 帧火尖偏移。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    tip = 0 if frame == 0 else 1
    draw.polygon(
        [(8, 1 + tip), (11, 4), (12, 8), (11, 12), (8, 14), (5, 12), (4, 8), (5, 4)],
        fill=C["crimson"],
    )
    draw.polygon([(8, 4), (10, 7), (10, 10), (8, 12), (6, 10), (6, 7)], fill=C["amber"])
    draw.polygon([(8, 7), (9, 9), (8, 11), (7, 9)], fill=C["lemon"])
    return add_outline(image)


def draw_rock(frame: int = 0) -> Image.Image:
    """圆滚滚的石头，一点高光。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 5, 13, 14), fill=C["stone"])
    draw.ellipse((4, 6, 8, 9), fill=C["steel"])
    draw.point((5, 7), fill=C["cream"])
    return add_outline(image)


def draw_door(frame: int = 0) -> Image.Image:
    """简单木门：一块门板 + 圆把手。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 2, 12, 15), radius=2, fill=C["clay"])
    draw.rounded_rectangle((5, 4, 10, 13), radius=1, fill=C["amber"])
    draw.ellipse((8, 8, 9, 9), fill=C["lemon"])
    draw.point((8, 8), fill=C["cream"])
    return add_outline(image)


def draw_key(frame: int = 0) -> Image.Image:
    """小钥匙。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 1, 11, 8), outline=C["lemon"], width=2)
    draw.rectangle((7, 7, 8, 15), fill=C["lemon"])
    draw.rectangle((8, 11, 10, 12), fill=C["lemon"])
    draw.rectangle((8, 13, 9, 14), fill=C["lemon"])
    draw.line((5, 3, 6, 3), fill=C["cream"])
    draw.rectangle((7, 8, 7, 13), fill=C["cream"])
    return add_outline(image)


def draw_portal(frame: int = 0) -> Image.Image:
    """简单的传送门圆环 + 两点闪光。"""
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((1, 1, 14, 14), fill=C["wine"])
    draw.ellipse((3, 3, 12, 12), fill=C["cornflower"])
    draw.ellipse((6, 6, 9, 9), fill=C["cream"])
    sparks = ((2, 7), (13, 8)) if frame == 0 else ((3, 6), (12, 9))
    for x, y in sparks:
        draw.point((x, y), fill=C["cream"])
    return add_outline(image)


SPRITES = {
    "baba": draw_baba,
    "wall": draw_wall,
    "box": draw_box,
    "flag": draw_flag,
    "water": draw_water,
    "lava": draw_lava,
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


def frame_numbers(name: str) -> tuple[int, ...]:
    if name not in ANIMATIONS:
        return (0,)
    return tuple(sorted(set(ANIMATIONS[name][1])))


def render(name: str, frame: int) -> Image.Image:
    return SPRITES[name](frame)


def frame_at(name: str, step: int) -> int:
    """素材表/GIF 里第 step 步该画哪一帧。"""
    if name not in ANIMATIONS:
        return 0
    period, pattern = ANIMATIONS[name]
    ticks = step * GIF_STEP_MS
    return pattern[(ticks // period) % len(pattern)]


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


# 主角的额外朝向：只写文件，不参与 16 格素材表。
EXTRA_VIEWS = {
    "baba-up": draw_baba_up,
    "baba-side": draw_baba_side,
}


def build_views_sheet() -> Image.Image:
    """三视角 × 两帧的展示图（docs/sprites_views.png）。"""
    cell = 120
    sheet = Image.new("RGBA", (6 * cell, cell), (24, 26, 34, 255))
    index = 0
    for name, func in (("baba", draw_baba), ("baba-up", draw_baba_up), ("baba-side", draw_baba_side)):
        for frame in (0, 1):
            sprite = func(frame).resize((cell - 16, cell - 16), Image.NEAREST)
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

    for name, func in EXTRA_VIEWS.items():
        for frame in (0, 1):
            suffix = "" if frame == 0 else f"-{frame}"
            func(frame).save(SPRITE_DIR / f"{name}{suffix}.png")

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
