"""Pygame 游戏窗口：开始菜单、选关、游戏与 HUD。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from ..core.catalog import Progress, discover_levels, first_unfinished
from ..core.game import Game
from ..core.level import load_level
from ..core.rules import parse_rules
from .editor import Editor

WIDTH, HEIGHT = 980, 680
MARGIN, TOP, BOTTOM = 40, 100, 170

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
LOSE = (255, 150, 150)
SELECT_BG = (62, 72, 100)
MENU_OPTIONS = ("开始游戏", "选关", "关卡编辑器", "退出")


class _App:
    def __init__(self, entries, progress: Progress):
        self.entries = entries
        self.progress = progress
        self.screen = "menu"  # menu | select | play | editor
        self.menu_index = 0
        self.select_index = 0
        self.level_index: int | None = None
        self.game: Game | None = None
        self.editor: Editor | None = None
        self.layout: tuple[int, int, int] | None = None
        self.fonts: dict | None = None

    def start_index(self, index: int) -> None:
        if not (0 <= index < len(self.entries)):
            return
        self.level_index = index
        self._load(self.entries[index].path)

    def start_path(self, path: Path) -> None:
        path = Path(path)
        for index, entry in enumerate(self.entries):
            if entry.path.resolve() == path.resolve():
                self.start_index(index)
                return
        self.level_index = None
        self._load(path)

    def _load(self, path: Path) -> None:
        self.game = Game(load_level(path))
        try:
            import pygame

            pygame.key.stop_text_input()
        except Exception:
            pass
        world = self.game.world
        cell = min(
            (WIDTH - MARGIN * 2) // world.width,
            (HEIGHT - TOP - BOTTOM) // world.height,
            56,
        )
        grid_w, grid_h = cell * world.width, cell * world.height
        ox = (WIDTH - grid_w) // 2
        oy = TOP + (HEIGHT - TOP - BOTTOM - grid_h) // 2
        self.layout = (ox, oy, cell)
        self.fonts = {
            "object": _font(max(14, cell // 2)),
            "word": _font(max(12, cell // 3)),
        }
        self.screen = "play"

    def mark_win(self) -> None:
        if self.level_index is not None:
            self.progress.mark(self.entries[self.level_index].id)

    def next_level(self) -> None:
        if self.level_index is None:
            self.screen = "select"
            return
        index = self.level_index + 1
        if index < len(self.entries):
            self.start_index(index)
        else:
            self.select_index = self.level_index
            self.screen = "select"

    def open_select(self) -> None:
        self.select_index = self.level_index if self.level_index is not None else 0
        self.screen = "select"

    def open_editor(self) -> None:
        if self.editor is None:
            self.editor = Editor(
                on_changed=self.reload_entries,
                on_back=self.back_to_menu,
            )
        self.screen = "editor"
        try:
            import pygame

            pygame.key.start_text_input()
        except Exception:
            pass

    def back_to_menu(self) -> None:
        self.screen = "menu"
        try:
            import pygame

            pygame.key.stop_text_input()
        except Exception:
            pass

    def reload_entries(self) -> None:
        self.entries = discover_levels()


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    parsed = _parse_args(args)
    if parsed is None:
        return 0
    level_path, frames, shot, debug_keys, start_editor = parsed
    if level_path is not None and not level_path.exists():
        print(f"找不到关卡：{level_path}", file=sys.stderr)
        return 2

    entries = discover_levels()
    progress = Progress()

    try:
        import pygame  # noqa: F401
    except ImportError:
        if level_path is not None:
            print(Game(load_level(level_path)).world.to_ascii())
        else:
            for entry in entries:
                mark = "*" if progress.is_completed(entry.id) else " "
                print(f"[{mark}] {entry.display_name}")
        print("\n安装：pip install pygame")
        return 0

    return _run(
        entries, progress, level_path, frames, shot, debug_keys, start_editor
    )


def _parse_args(args: list[str]):
    level_path: Path | None = None
    frames = 0
    shot: Path | None = None
    debug_keys = False
    start_editor = False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print(
                "用法：python run.py [关卡文件] [--editor] [--frames N] "
                "[--shot 图片路径] [--debug-keys]"
            )
            return None
        if arg == "--frames":
            try:
                frames = int(args[i + 1])
            except (IndexError, ValueError):
                print("--frames 需要跟一个整数", file=sys.stderr)
                return None
            i += 2
            continue
        if arg == "--shot":
            if i + 1 >= len(args):
                print("--shot 需要跟一个图片路径", file=sys.stderr)
                return None
            shot = Path(args[i + 1])
            i += 2
            continue
        if arg == "--debug-keys":
            debug_keys = True
            i += 1
            continue
        if arg == "--editor":
            start_editor = True
            i += 1
            continue
        level_path = Path(arg)
        i += 1
    return level_path, frames, shot, debug_keys, start_editor


def _run(
    entries,
    progress: Progress,
    initial_level,
    frames: int,
    shot,
    debug_keys: bool,
    start_editor: bool = False,
) -> int:
    import pygame

    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    except pygame.error as exc:
        print(f"无法创建窗口：{exc}", file=sys.stderr)
        return 1

    try:
        pygame.key.stop_text_input()
    except AttributeError:
        pass
    _focus_window(pygame)
    pygame.key.set_repeat(0)
    clock = pygame.time.Clock()

    chrome = {
        "logo": _font(64),
        "title": _font(28),
        "menu": _font(24),
        "hint": _font(15),
        "rule": _font(18),
        "object": _font(22),
        "word": _font(14),
    }
    app = _App(entries, progress)
    if start_editor:
        app.open_editor()
    elif initial_level is not None:
        app.start_path(initial_level)
    else:
        app.screen = "menu"
    moves = _move_map()

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
                        f"focused={pygame.key.get_focused()} screen={app.screen}"
                    )
                if event.key in moves:
                    repeat_at = pygame.time.get_ticks() + 180
                if not _handle_event(app, event.key, event.unicode, moves):
                    running = False
            elif (
                event.type == pygame.TEXTINPUT
                and app.screen == "editor"
                and app.editor is not None
            ):
                app.editor.handle_text(event.text)
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and app.screen == "editor"
                and app.editor is not None
            ):
                app.editor.handle_click(event.pos, event.button)

        now = pygame.time.get_ticks()
        game = app.game
        if (
            running
            and app.screen == "play"
            and game is not None
            and not game.won
            and not game.lost
            and now >= repeat_at
        ):
            pressed = pygame.key.get_pressed()
            for key, (dr, dc) in moves.items():
                if pressed[key]:
                    _move_game(app, dr, dc)
                    repeat_at = now + 110
                    break

        _draw(screen, app, chrome)
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


def _move_map() -> dict[int, tuple[int, int]]:
    import pygame

    return {
        pygame.K_UP: (-1, 0),
        pygame.K_w: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_s: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_a: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_d: (0, 1),
    }


def _handle_event(app: _App, key: int, text: str, moves) -> bool:
    if app.screen == "menu":
        return _handle_menu(app, key)
    if app.screen == "select":
        return _handle_select(app, key)
    if app.screen == "editor":
        return _handle_editor(app, key, text)
    return _handle_play(app, key, text, moves)


def _handle_editor(app: _App, key: int, text: str) -> bool:
    import pygame

    if app.editor is None:
        app.screen = "menu"
        return True
    if app.editor.handle_key(key, text, pygame.key.get_mods()) == "back":
        app.back_to_menu()
    return True


def _handle_menu(app: _App, key: int) -> bool:
    import pygame

    if key in (pygame.K_UP, pygame.K_w):
        app.menu_index = (app.menu_index - 1) % len(MENU_OPTIONS)
    elif key in (pygame.K_DOWN, pygame.K_s):
        app.menu_index = (app.menu_index + 1) % len(MENU_OPTIONS)
    elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        if app.menu_index == 0:
            app.start_index(first_unfinished(app.entries, app.progress))
        elif app.menu_index == 1:
            app.open_select()
        elif app.menu_index == 2:
            app.open_editor()
        else:
            return False
    elif key == pygame.K_ESCAPE:
        return False
    return True


def _handle_select(app: _App, key: int) -> bool:
    import pygame

    if not app.entries:
        if key == pygame.K_ESCAPE:
            app.screen = "menu"
        return True
    if key in (pygame.K_UP, pygame.K_w):
        app.select_index = (app.select_index - 1) % len(app.entries)
    elif key in (pygame.K_DOWN, pygame.K_s):
        app.select_index = (app.select_index + 1) % len(app.entries)
    elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
        app.start_index(app.select_index)
    elif key == pygame.K_ESCAPE:
        app.screen = "menu"
    return True


def _handle_play(app: _App, key: int, text: str, moves) -> bool:
    import pygame

    game = app.game
    if game is None:
        app.screen = "menu"
        return True

    if key == pygame.K_ESCAPE:
        app.screen = "menu"
        return True
    if game.won and (
        key in (pygame.K_n, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
        or (text or "").lower() == "n"
    ):
        app.next_level()
        return True

    _handle_key(game, key, text, moves)
    if game.won:
        app.mark_win()
    return True


def _move_game(app: _App, dr: int, dc: int) -> None:
    if app.game is None:
        return
    if app.game.move(dr, dc).won:
        app.mark_win()


def _handle_key(game: Game, key: int, text: str, moves: dict[int, tuple[int, int]]) -> bool:
    """处理一次游戏内按键；返回 False 表示退出游戏。"""
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
    if key in moves and not game.won and not game.lost:
        dr, dc = moves[key]
        game.move(dr, dc)
    return True


def _font(size: int):
    import pygame

    path = pygame.font.match_font(
        "microsoftyahei,msyh,simhei,simsun,notosanscjksc,wenquanyimicrohei"
    )
    if path:
        return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def _draw(screen, app: _App, chrome) -> None:
    import pygame

    if app.screen == "menu":
        _draw_menu(screen, app, chrome)
    elif app.screen == "select":
        _draw_select(screen, app, chrome)
    elif app.screen == "editor" and app.editor is not None:
        app.editor.draw(screen, chrome)
    else:
        _draw_play(screen, app, chrome)

    if pygame.display.get_driver() != "dummy" and not pygame.key.get_focused():
        hint = chrome["rule"].render("点击窗口后使用键盘", True, (255, 210, 120))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 22)))


def _draw_menu(screen, app: _App, chrome) -> None:
    import pygame

    screen.fill(BG)
    logo = chrome["logo"].render("RuleBox", True, TITLE)
    screen.blit(logo, logo.get_rect(center=(WIDTH // 2, 150)))
    sub = chrome["title"].render("推得动箱子，也推得动规则", True, HINT)
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 215)))

    for index, option in enumerate(MENU_OPTIONS):
        color = TITLE if index == app.menu_index else HINT
        label = chrome["menu"].render(option, True, color)
        rect = label.get_rect(center=(WIDTH // 2, 340 + index * 58))
        if index == app.menu_index:
            pygame.draw.rect(screen, SELECT_BG, rect.inflate(150, 18), border_radius=10)
        screen.blit(label, rect)

    done = len(app.progress.completed)
    status = chrome["hint"].render(
        f"已完成 {done} / {len(app.entries)} 关", True, HINT
    )
    screen.blit(status, status.get_rect(center=(WIDTH // 2, 560)))
    tip = chrome["hint"].render("↑↓ 选择 · Enter 确认 · Esc 退出", True, HINT)
    screen.blit(tip, tip.get_rect(center=(WIDTH // 2, 620)))


def _draw_select(screen, app: _App, chrome) -> None:
    import pygame

    screen.fill(BG)
    title = chrome["title"].render("选关", True, TITLE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

    if not app.entries:
        empty = chrome["rule"].render("content/levels 下还没有关卡", True, HINT)
        screen.blit(empty, empty.get_rect(center=(WIDTH // 2, 300)))
    else:
        max_rows = 9
        start = max(0, min(app.select_index - 3, len(app.entries) - max_rows))
        start = max(0, start)
        for offset, entry in enumerate(app.entries[start : start + max_rows]):
            index = start + offset
            completed = app.progress.is_completed(entry.id)
            color = TITLE if index == app.select_index else (RULE_TEXT if completed else HINT)
            label = chrome["menu"].render(entry.display_name, True, color)
            rect = label.get_rect(center=(WIDTH // 2, 180 + offset * 46))
            if index == app.select_index:
                pygame.draw.rect(screen, SELECT_BG, rect.inflate(260, 14), border_radius=10)
            screen.blit(label, rect)

    tip = chrome["hint"].render("↑↓ 选择 · Enter 开始 · Esc 返回", True, HINT)
    screen.blit(tip, tip.get_rect(center=(WIDTH // 2, 620)))


def _draw_play(screen, app: _App, chrome) -> None:
    import pygame

    game = app.game
    if game is None or app.layout is None or app.fonts is None:
        return
    world = game.world
    ox, oy, cell = app.layout
    fonts = {**chrome, **app.fonts}
    screen.fill(BG)

    screen.blit(fonts["title"].render(_display_title(world.name), True, TITLE), (MARGIN, 24))
    moves_text = fonts["hint"].render(f"步数 {game.moves}", True, HINT)
    screen.blit(moves_text, (WIDTH - MARGIN - moves_text.get_width(), 34))

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

    hint = "方向键 / WASD 移动 · Z 撤销 · R 重开 · Esc 菜单"
    screen.blit(fonts["hint"].render(hint, True, HINT), (MARGIN, HEIGHT - 34))

    if game.won or game.lost:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 16, 170))
        screen.blit(overlay, (0, 0))

    if game.won:
        big = fonts["title"].render("过关！", True, WIN)
        screen.blit(big, big.get_rect(center=(WIDTH // 2, 300)))
        last = app.level_index is not None and app.level_index >= len(app.entries) - 1
        tail = "这是最后一关 · Esc 选关" if last else "Enter / N 下一关 · R 重来 · Esc 菜单"
        sub = fonts["rule"].render(f"用了 {game.moves} 步 · {tail}", True, (232, 232, 240))
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 345)))
    elif game.lost:
        big = fonts["title"].render("失败", True, LOSE)
        screen.blit(big, big.get_rect(center=(WIDTH // 2, 300)))
        sub = fonts["rule"].render("R 重开 · Esc 菜单", True, (232, 232, 240))
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 345)))


def _text_color(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = bg
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return TEXT_DARK if luminance > 140 else TEXT_LIGHT


def _display_title(text: str) -> str:
    return re.sub(r"^\s*\d+\s*", "", text).strip() or text


def _focus_window(pygame) -> None:
    """Windows 下尽量把游戏窗口提到前台，避免键盘事件都进终端。"""
    try:
        import ctypes

        hwnd = pygame.display.get_wm_info().get("window")
        if not hwnd:
            return
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, 5)
        user32.SetForegroundWindow(hwnd)
    except Exception:
        pass
