"""Pygame 游戏窗口：渲染、输入、HUD。"""

from __future__ import annotations

import sys
from pathlib import Path

from ..core.game import Game
from ..core.level import load_level
from ..core.rules import parse_rules

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LEVEL = ROOT / "content" / "levels" / "01-first-step.txt"

BG = (24, 26, 34)
FLOOR_A = (50, 54, 66)
FLOOR_B = (56, 60, 74)
GRID_LINE = (34, 36, 46)
TITLE = (236, 238, 245)
HINT = (150, 155, 170)
RULE_TEXT = (196, 202, 218)
TEXT_DARK = (26, 26, 32)
TEXT_LIGHT = (242, 242, 248)
WIN = (255, 226, 128)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    level_path, frames, shot, debug_keys = _parse_args(args)
    if level_path is None:
        return 0
    if not level_path.exists():
        print(f"找不到关卡：{level_path}", file=sys.stderr)
        return 2

    game = Game(load_level(level_path))

    try:
        import pygame  # noqa: F401
    except ImportError:
        print("没有安装 pygame，先用文本模式显示关卡：\n")
        print(game.world.to_ascii())
        print("\n安装：pip install pygame")
        return 0

    return _run(game, frames, shot, debug_keys)


def _parse_args(args: list[str]) -> tuple[Path | None, int, Path | None, bool]:
    level_path: Path | None = DEFAULT_LEVEL
    frames = 0
    shot: Path | None = None
    debug_keys = False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print(
                "用法：python run.py [关卡文件] [--frames N] [--shot 图片路径] [--debug-keys]"
            )
            return None, 0, None, False
        if arg == "--frames":
            try:
                frames = int(args[i + 1])
            except (IndexError, ValueError):
                print("--frames 需要跟一个整数", file=sys.stderr)
                return None, 0, None, False
            i += 2
            continue
        if arg == "--shot":
            if i + 1 >= len(args):
                print("--shot 需要跟一个图片路径", file=sys.stderr)
                return None, 0, None, False
            shot = Path(args[i + 1])
            i += 2
            continue
        if arg == "--debug-keys":
            debug_keys = True
            i += 1
            continue
        level_path = Path(arg)
        i += 1
    return level_path, frames, shot, debug_keys


def _run(game: Game, frames: int, shot: Path | None = None, debug_keys: bool = False) -> int:
    import pygame

    pygame.init()
    try:
        screen = pygame.display.set_mode((980, 680))
    except pygame.error as exc:
        print(f"无法创建窗口：{exc}", file=sys.stderr)
        return 1

    # 关掉文字输入，避免中文输入法吃掉 R / Z / Esc
    try:
        pygame.key.stop_text_input()
    except AttributeError:
        pass

    # 尽量把窗口提到前台，避免按键全进终端
    _focus_window(pygame)

    pygame.display.set_caption(f"RuleBox · {game.level.name}")
    pygame.key.set_repeat(0)  # 自己控制方向键的连发，Z/R 只触发一次
    clock = pygame.time.Clock()

    margin = 40
    top = 100
    bottom = 140
    width, height = 980, 680
    world = game.world
    cell = min(
        (width - margin * 2) // world.width,
        (height - top - bottom) // world.height,
        56,
    )
    grid_w, grid_h = cell * world.width, cell * world.height
    ox = (width - grid_w) // 2
    oy = top + (height - top - bottom - grid_h) // 2

    fonts = {
        "title": _font(26),
        "hint": _font(15),
        "rule": _font(16),
        "object": _font(max(14, cell // 2)),
        "word": _font(max(12, cell // 3)),
    }

    moves = {
        pygame.K_UP: (-1, 0),
        pygame.K_w: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_s: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_a: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_d: (0, 1),
    }

    running = True
    drawn = 0
    repeat_at = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if debug_keys:
                    print(
                        f"KEY key={event.key} unicode={event.unicode!r} "
                        f"focused={pygame.key.get_focused()}"
                    )
                if event.key in moves:
                    repeat_at = pygame.time.get_ticks() + 180
                if not _handle_key(game, event.key, event.unicode, moves):
                    running = False

        # 事件被输入法/焦点吞掉时的兜底：直接轮询 Esc
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False

        # 方向键按住时连续移动；Z/R 不在轮询里，避免连发
        now = pygame.time.get_ticks()
        if running and not game.won and now >= repeat_at:
            pressed = pygame.key.get_pressed()
            for key, (dr, dc) in moves.items():
                if pressed[key]:
                    game.move(dr, dc)
                    repeat_at = now + 110
                    break

        _draw(screen, game, (ox, oy), cell, fonts)
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


def _draw(screen, game: Game, origin, cell: int, fonts) -> None:
    import pygame

    world = game.world
    ox, oy = origin
    screen.fill(BG)

    screen.blit(fonts["title"].render(world.name, True, TITLE), (40, 24))
    moves_text = fonts["hint"].render(f"步数 {game.moves}", True, HINT)
    screen.blit(moves_text, (980 - 40 - moves_text.get_width(), 34))

    # 窗口没拿到焦点时，按键会全部进终端，这里给出明确提示
    if pygame.display.get_driver() != "dummy" and not pygame.key.get_focused():
        tip = fonts["rule"].render("点击窗口后使用键盘", True, (255, 210, 120))
        screen.blit(tip, tip.get_rect(center=(490, 84)))

    for row in range(world.height):
        for col in range(world.width):
            x, y = ox + col * cell, oy + row * cell
            floor = FLOOR_A if (row + col) % 2 == 0 else FLOOR_B
            pygame.draw.rect(screen, floor, (x, y, cell, cell))
            pygame.draw.rect(screen, GRID_LINE, (x, y, cell, cell), 1)

            for entity in world.entities_at(row, col):
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
                else:
                    font = fonts["word"] if entity.is_word else fonts["object"]
                    label = font.render(entity.text, True, _text_color(entity.color))
                    screen.blit(label, label.get_rect(center=rect.center))

    # 规则面板
    rules = parse_rules(world)
    panel_y = oy + world.height * cell + 18
    screen.blit(fonts["hint"].render("规则", True, HINT), (ox, panel_y))
    panel_y += 24
    if not rules:
        screen.blit(fonts["rule"].render("（没有生效的规则）", True, RULE_TEXT), (ox, panel_y))
    for rule in rules[:5]:
        screen.blit(fonts["rule"].render("· " + rule.display(), True, RULE_TEXT), (ox, panel_y))
        panel_y += 21
    if len(rules) > 5:
        screen.blit(fonts["hint"].render("…", True, HINT), (ox, panel_y))

    hint = "方向键 / WASD 移动 · Z 撤销 · R 重开 · Esc 退出"
    hint_surface = fonts["hint"].render(hint, True, HINT)
    screen.blit(hint_surface, (40, 680 - 34))

    if game.won:
        overlay = pygame.Surface((980, 680), pygame.SRCALPHA)
        overlay.fill((10, 10, 16, 170))
        screen.blit(overlay, (0, 0))
        big = fonts["title"].render("过关！", True, WIN)
        screen.blit(big, big.get_rect(center=(490, 300)))
        sub = fonts["rule"].render(
            f"用了 {game.moves} 步 · 按 R 重来", True, (232, 232, 240)
        )
        screen.blit(sub, sub.get_rect(center=(490, 345)))


def _text_color(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = bg
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return TEXT_DARK if luminance > 140 else TEXT_LIGHT


def _handle_key(game: Game, key: int, text: str, moves: dict[int, tuple[int, int]]) -> bool:
    """处理一次按键；返回 False 表示退出游戏。"""
    import pygame

    text = (text or "").lower()
    if key == pygame.K_ESCAPE:
        return False
    if key == pygame.K_r or text == "r":
        game.reset()
        return True
    if key == pygame.K_z or text == "z":
        game.undo()
        return True
    if key in moves and not game.won:
        dr, dc = moves[key]
        game.move(dr, dc)
    return True


def _focus_window(pygame) -> None:
    """Windows 下尽量把游戏窗口提到前台，避免键盘事件都进终端。"""
    try:
        import ctypes

        hwnd = pygame.display.get_wm_info().get("window")
        if not hwnd:
            return
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, 5)  # SW_SHOW
        user32.SetForegroundWindow(hwnd)
    except Exception:
        # 非 Windows 或没有权限就算了，不影响游戏
        pass
