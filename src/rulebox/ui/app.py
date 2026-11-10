"""Pygame 关卡预览窗口（Day 1：只渲染，不处理移动）。"""

from __future__ import annotations

import sys
from pathlib import Path

from ..core.level import load_level
from ..core.world import World

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LEVEL = ROOT / "content" / "levels" / "01-first-step.txt"

BG = (24, 26, 34)
FLOOR_A = (50, 54, 66)
FLOOR_B = (56, 60, 74)
GRID_LINE = (34, 36, 46)
TITLE = (236, 238, 245)
HINT = (150, 155, 170)
TEXT_DARK = (26, 26, 32)
TEXT_LIGHT = (242, 242, 248)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    level_path, frames, shot = _parse_args(args)
    if level_path is None:
        return 0
    if not level_path.exists():
        print(f"找不到关卡：{level_path}", file=sys.stderr)
        return 2

    world = World(load_level(level_path))

    try:
        import pygame  # noqa: F401
    except ImportError:
        print("没有安装 pygame，先用文本模式显示关卡：\n")
        print(world.to_ascii())
        print("\n安装：pip install pygame")
        return 0

    return _run(world, frames, shot)


def _parse_args(args: list[str]) -> tuple[Path | None, int, Path | None]:
    level_path: Path | None = DEFAULT_LEVEL
    frames = 0
    shot: Path | None = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print("用法：python run.py [关卡文件] [--frames N] [--shot 图片路径]")
            return None, 0, None
        if arg == "--frames":
            try:
                frames = int(args[i + 1])
            except (IndexError, ValueError):
                print("--frames 需要跟一个整数", file=sys.stderr)
                return None, 0, None
            i += 2
            continue
        if arg == "--shot":
            if i + 1 >= len(args):
                print("--shot 需要跟一个图片路径", file=sys.stderr)
                return None, 0, None
            shot = Path(args[i + 1])
            i += 2
            continue
        level_path = Path(arg)
        i += 1
    return level_path, frames, shot


def _run(world: World, frames: int, shot: Path | None = None) -> int:
    import pygame

    pygame.init()
    try:
        screen = pygame.display.set_mode((980, 680))
    except pygame.error as exc:
        print(f"无法创建窗口：{exc}", file=sys.stderr)
        return 1

    pygame.display.set_caption(f"RuleBox · {world.name}")
    clock = pygame.time.Clock()

    margin = 40
    top = 92
    width, height = 980, 680
    cell = min(
        (width - margin * 2) // world.width,
        (height - top - margin) // world.height,
        56,
    )
    grid_w, grid_h = cell * world.width, cell * world.height
    ox = (width - grid_w) // 2
    oy = top + (height - top - margin - grid_h) // 2

    title_font = _font(26)
    hint_font = _font(15)
    object_font = _font(max(14, cell // 2))
    word_font = _font(max(12, cell // 3))

    running = True
    drawn = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        _draw(
            screen,
            world,
            (ox, oy),
            cell,
            title_font,
            hint_font,
            object_font,
            word_font,
        )
        pygame.display.flip()

        drawn += 1
        if shot is not None and drawn == 1:
            shot.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(shot))
            running = False
        if frames and drawn >= frames:
            running = False
        clock.tick(60)

    pygame.quit()
    return 0


def _font(size: int):
    import pygame

    path = pygame.font.match_font(
        "microsoftyahei,msyh,simhei,simsun,notosanscjksc,wenquanyimicrohei"
    )
    if path:
        return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def _draw(screen, world, origin, cell, title_font, hint_font, object_font, word_font):
    import pygame

    ox, oy = origin
    screen.fill(BG)
    screen.blit(title_font.render(world.name, True, TITLE), (ox, 28))
    screen.blit(hint_font.render("Day 1 预览 · Esc 退出", True, HINT), (ox, 62))

    for row in range(world.height):
        for col in range(world.width):
            x, y = ox + col * cell, oy + row * cell
            floor = FLOOR_A if (row + col) % 2 == 0 else FLOOR_B
            pygame.draw.rect(screen, floor, (x, y, cell, cell))
            pygame.draw.rect(screen, GRID_LINE, (x, y, cell, cell), 1)

            entity = world.get(row, col)
            if entity is None:
                continue

            inset = max(3, cell // 12)
            rect = pygame.Rect(x + inset, y + inset, cell - inset * 2, cell - inset * 2)
            radius = max(4, cell // 8)
            pygame.draw.rect(screen, entity.color, rect, border_radius=radius)
            pygame.draw.rect(screen, (18, 18, 24), rect, 1, border_radius=radius)

            if entity.id == "wall":
                inner = rect.inflate(-max(6, cell // 5), -max(6, cell // 5))
                pygame.draw.rect(
                    screen, (68, 72, 90), inner, 2, border_radius=max(2, radius - 2)
                )
                continue

            font = word_font if entity.is_word else object_font
            label = font.render(entity.text, True, _text_color(entity.color))
            screen.blit(label, label.get_rect(center=rect.center))


def _text_color(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = bg
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return TEXT_DARK if luminance > 140 else TEXT_LIGHT
