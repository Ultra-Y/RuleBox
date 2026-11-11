"""关卡编辑器：可调尺寸、调色板、试玩、保存、重命名、删除、分享码。"""

from __future__ import annotations

from pathlib import Path

from ..core.catalog import CUSTOM_DIR, USER_ROOT
from ..core.entities import make_object, make_word
from ..core.level import Level, parse_level
from ..core.rules import active_word_positions, blocked_transform_word_positions
from ..core.world import World
from ..core.level_builder import (
    BY_SYMBOL,
    PALETTE,
    blank_cells,
    build_level_text,
    cells_from_text,
    safe_level_path,
    share_decode,
    share_encode,
)
from .sprites import draw_object

EXPORTS_DIR = USER_ROOT / "exports"

BG = (24, 26, 34)
PANEL = (36, 40, 52)
FLOOR_A = (50, 54, 66)
FLOOR_B = (56, 60, 74)
GRID_LINE = (34, 36, 46)
TITLE = (236, 238, 245)
HINT = (150, 155, 170)
SELECT_BG = (62, 72, 100)
ACCENT = (255, 210, 120)
TEXT_DARK = (26, 26, 32)
TEXT_LIGHT = (242, 242, 248)

GRID_X, GRID_Y = 40, 110
MAX_GRID_W, MAX_GRID_H = 520, 360
PALETTE_X, PALETTE_Y = 40, 478
PALETTE_COLS = 10
PALETTE_TILE = 38
PALETTE_GAP = 4


class Editor:
    def __init__(self, on_changed=None, on_back=None, on_playtest=None, on_open=None):
        self.width = 11
        self.height = 8
        self.cells = blank_cells(self.width, self.height)
        self.name = "自制关卡"
        self.current_path: Path | None = None
        self.selected_symbol = "@"
        self.name_active = False
        self._undo_stack: list[tuple] = []
        self._redo_stack: list[tuple] = []
        self.message = "左键放置 · 右键擦除 · Ctrl+S 保存"
        self.on_changed = on_changed
        self.on_back = on_back
        self.on_playtest = on_playtest
        self.on_open = on_open
        try:
            import pygame

            pygame.scrap.init()
        except Exception:
            pass

    # ---------- 历史 ----------

    def _snapshot(self) -> tuple:
        return (self.width, self.height, tuple(tuple(row) for row in self.cells))

    def _push_undo(self) -> None:
        self._undo_stack.append(self._snapshot())
        del self._undo_stack[:-60]
        self._redo_stack.clear()

    def _restore(self, snapshot: tuple) -> None:
        self.width, self.height, cells = snapshot
        self.cells = [list(row) for row in cells]

    def undo(self) -> None:
        if not self._undo_stack:
            self.message = "没有可撤销的操作"
            return
        self._redo_stack.append(self._snapshot())
        self._restore(self._undo_stack.pop())
        self.message = "已撤销"

    def redo(self) -> None:
        if not self._redo_stack:
            self.message = "没有可重做的操作"
            return
        self._undo_stack.append(self._snapshot())
        self._restore(self._redo_stack.pop())
        self.message = "已重做"

    # ---------- 文件 ----------

    def build_text(self) -> str:
        text = build_level_text(self.name, self.cells)
        parse_level(text, source="<editor>")
        return text

    def save(self) -> None:
        try:
            text = self.build_text()
            path = safe_level_path(CUSTOM_DIR, self.name, self.current_path)
            path.write_text(text, encoding="utf-8")
        except Exception as exc:
            self.message = f"保存失败：{exc}"
            return
        self.current_path = path
        self.message = f"已保存：{path.name}"
        if self.on_changed:
            self.on_changed()

    def load_path(self, path: Path) -> None:
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8")
            name, cells = cells_from_text(text)
        except Exception as exc:
            self.message = f"打开失败：{exc}"
            return
        self.name = name
        self.cells = cells
        self.height = len(cells)
        self.width = len(cells[0]) if cells else 0
        self.current_path = path
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.message = f"已打开：{path.name}"

    def rename(self) -> None:
        if self.current_path is None:
            self.message = "先保存，再重命名"
            return
        try:
            target = safe_level_path(CUSTOM_DIR, self.name, self.current_path)
            if target != self.current_path:
                self.current_path.rename(target)
                self.current_path = target
        except Exception as exc:
            self.message = f"重命名失败：{exc}"
            return
        self.message = f"已重命名：{self.current_path.name}"
        if self.on_changed:
            self.on_changed()

    def delete(self) -> None:
        if self.current_path is None:
            self.message = "还没有保存过的自制关卡"
            return
        try:
            self.current_path.unlink(missing_ok=True)
        except Exception as exc:
            self.message = f"删除失败：{exc}"
            return
        self.message = f"已删除：{self.current_path.name}"
        self.current_path = None
        if self.on_changed:
            self.on_changed()

    def playtest(self) -> None:
        try:
            text = self.build_text()
        except Exception as exc:
            self.message = f"试玩失败：{exc}"
            return
        if self.on_playtest and self.on_playtest(text):
            return
        self.message = "试玩启动失败"

    def open_custom(self) -> None:
        if self.on_open:
            self.on_open()

    def export(self) -> None:
        try:
            text = self.build_text()
            path = safe_level_path(EXPORTS_DIR, self.name)
            path.write_text(text, encoding="utf-8")
            code = share_encode(text)
            path.with_suffix(".code").write_text(code, encoding="utf-8")
        except Exception as exc:
            self.message = f"导出失败：{exc}"
            return
        copied = _clipboard_set(code)
        tail = "，分享码已复制" if copied else "（剪贴板不可用，见 .code）"
        self.message = f"已导出 {path.name}{tail}"

    def import_share(self) -> None:
        code = _clipboard_get()
        if not code:
            files = sorted(EXPORTS_DIR.glob("*.code"))
            if files:
                code = files[-1].read_text(encoding="utf-8")
        if not code:
            self.message = "剪贴板里没有分享码"
            return
        try:
            text = share_decode(code)
            path = safe_level_path(CUSTOM_DIR, "导入关卡")
            path.write_text(text, encoding="utf-8")
        except ValueError as exc:
            self.message = f"导入失败：{exc}"
            return
        self.load_path(path)
        self.message = f"已导入：{path.name}"
        if self.on_changed:
            self.on_changed()

    def clear(self) -> None:
        self._push_undo()
        self.cells = blank_cells(self.width, self.height)
        self.current_path = None
        self.message = "已清空，保留当前尺寸"

    def resize(self, width: int, height: int) -> None:
        width = max(5, min(20, width))
        height = max(5, min(20, height))
        if (width, height) == (self.width, self.height):
            return
        self._push_undo()
        old = self.cells
        self.width, self.height = width, height
        self.cells = blank_cells(width, height)
        for row in range(1, min(len(old), height) - 1):
            for col in range(1, min(len(old[row]), width) - 1):
                self.cells[row][col] = old[row][col]
        self.message = f"尺寸：{width}×{height}"

    # ---------- 输入 ----------

    def handle_text(self, text: str) -> None:
        if self.name_active and text and len(self.name) < 24:
            self.name += text

    def handle_key(self, key: int, text: str, mods: int) -> str | None:
        import pygame

        if self.name_active:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.name_active = False
            elif key == pygame.K_ESCAPE:
                self.name_active = False
            elif key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            return None

        if key == pygame.K_ESCAPE:
            return "back"
        ctrl = mods & pygame.KMOD_CTRL
        if ctrl and key == pygame.K_s:
            self.save()
        elif ctrl and key == pygame.K_e:
            self.export()
        elif ctrl and key == pygame.K_i:
            self.import_share()
        elif ctrl and key == pygame.K_z:
            if mods & pygame.KMOD_SHIFT:
                self.redo()
            else:
                self.undo()
        elif ctrl and key == pygame.K_y:
            self.redo()
        return None

    def handle_click(self, pos: tuple[int, int], button: int) -> None:
        if self._name_rect().collidepoint(pos):
            self.name_active = True
            return
        self.name_active = False

        for _label, rect, action in self._size_buttons():
            if rect.collidepoint(pos):
                action()
                return
        for _label, rect, action in self._history_buttons():
            if rect.collidepoint(pos):
                action()
                return
        for _label, rect, action in self._buttons():
            if rect.collidepoint(pos):
                action()
                return

        index = self._palette_index_at(pos)
        if index is not None:
            self.selected_symbol = PALETTE[index].symbol
            return

        cell = self._grid_cell_at(pos)
        if cell is not None:
            row, col = cell
            symbol = self.selected_symbol if button == 1 else "."
            if self.cells[row][col] != symbol:
                self._push_undo()
                self.cells[row][col] = symbol

    # ---------- 布局 ----------

    def _name_rect(self):
        import pygame

        return pygame.Rect(590, 110, 340, 38)

    def _size_buttons(self):
        import pygame

        specs = [
            ("宽−", pygame.Rect(590, 160, 80, 32), lambda: self.resize(self.width - 1, self.height)),
            ("宽＋", pygame.Rect(675, 160, 80, 32), lambda: self.resize(self.width + 1, self.height)),
            ("高−", pygame.Rect(760, 160, 80, 32), lambda: self.resize(self.width, self.height - 1)),
            ("高＋", pygame.Rect(845, 160, 85, 32), lambda: self.resize(self.width, self.height + 1)),
        ]
        return specs

    def _history_buttons(self):
        import pygame

        return [
            ("撤销", pygame.Rect(590, 205, 160, 34), self.undo),
            ("重做", pygame.Rect(760, 205, 170, 34), self.redo),
        ]

    def _buttons(self):
        import pygame

        specs = [
            ("保存", pygame.Rect(590, 250, 160, 40), self.save),
            ("试玩", pygame.Rect(760, 250, 170, 40), self.playtest),
            ("打开", pygame.Rect(590, 296, 160, 40), self.open_custom),
            ("重命名", pygame.Rect(760, 296, 170, 40), self.rename),
            ("删除", pygame.Rect(590, 342, 160, 40), self.delete),
            ("导出码", pygame.Rect(760, 342, 170, 40), self.export),
            ("导入码", pygame.Rect(590, 388, 160, 40), self.import_share),
            ("清空", pygame.Rect(760, 388, 170, 40), self.clear),
            ("返回菜单", pygame.Rect(590, 434, 340, 40), self.on_back or (lambda: None)),
        ]
        return specs

    def _grid_layout(self) -> tuple[int, int, int]:
        cell = min(MAX_GRID_W // max(1, self.width), MAX_GRID_H // max(1, self.height), 44)
        cell = max(12, cell)
        return GRID_X, GRID_Y, cell

    def _active_word_positions(self) -> set[tuple[int, int]]:
        cells = [[_entity(symbol) for symbol in row] for row in self.cells]
        try:
            return active_word_positions(World(Level("editor", self.width, self.height, cells)))
        except Exception:
            return set()

    def _blocked_word_positions(self) -> set[tuple[int, int]]:
        cells = [[_entity(symbol) for symbol in row] for row in self.cells]
        try:
            return blocked_transform_word_positions(
                World(Level("editor", self.width, self.height, cells))
            )
        except Exception:
            return set()

    def _palette_rect(self, index: int):
        import pygame

        row, col = divmod(index, PALETTE_COLS)
        x = PALETTE_X + col * (PALETTE_TILE + PALETTE_GAP)
        y = PALETTE_Y + row * (PALETTE_TILE + PALETTE_GAP)
        return pygame.Rect(x, y, PALETTE_TILE, PALETTE_TILE)

    def _palette_index_at(self, pos):
        import pygame

        point = pygame.Rect(pos[0], pos[1], 1, 1)
        for index in range(len(PALETTE)):
            if self._palette_rect(index).contains(point):
                return index
        return None

    def _grid_cell_at(self, pos):
        x0, y0, cell = self._grid_layout()
        x, y = pos
        if not (x0 <= x < x0 + self.width * cell):
            return None
        if not (y0 <= y < y0 + self.height * cell):
            return None
        return (y - y0) // cell, (x - x0) // cell

    # ---------- 绘制 ----------

    def draw(self, screen, chrome) -> None:
        import pygame

        screen.fill(BG)
        screen.blit(chrome["title"].render("关卡编辑器", True, TITLE), (40, 24))
        size = chrome["hint"].render(f"画布：{self.width}×{self.height}", True, HINT)
        screen.blit(size, (40, 66))

        name_rect = self._name_rect()
        pygame.draw.rect(screen, PANEL, name_rect, border_radius=6)
        border = ACCENT if self.name_active else GRID_LINE
        pygame.draw.rect(screen, border, name_rect, 2, border_radius=6)
        name_label = chrome["rule"].render(f"关卡名：{self.name}", True, TITLE)
        screen.set_clip(name_rect.inflate(-12, -8))
        screen.blit(name_label, (name_rect.x + 8, name_rect.y + 8))
        screen.set_clip(None)

        for label, rect, _action in self._size_buttons():
            pygame.draw.rect(screen, PANEL, rect, border_radius=5)
            text = chrome["hint"].render(label, True, TITLE)
            screen.blit(text, text.get_rect(center=rect.center))

        for label, rect, _action in self._history_buttons():
            pygame.draw.rect(screen, PANEL, rect, border_radius=5)
            text = chrome["hint"].render(label, True, TITLE)
            screen.blit(text, text.get_rect(center=rect.center))

        gx, gy, cell = self._grid_layout()
        active_words = self._active_word_positions()
        blocked_words = self._blocked_word_positions()
        for row in range(self.height):
            for col in range(self.width):
                x = gx + col * cell
                y = gy + row * cell
                floor = FLOOR_A if (row + col) % 2 == 0 else FLOOR_B
                pygame.draw.rect(screen, floor, (x, y, cell, cell))
                pygame.draw.rect(screen, GRID_LINE, (x, y, cell, cell), 1)
                entity = _entity(self.cells[row][col])
                if entity is not None:
                    color = entity.color
                    if entity.is_word and (row, col) not in active_words:
                        color = _dim_color(color)
                    _draw_entity(screen, entity, x, y, cell, chrome, color)
                    if entity.is_word and (row, col) in blocked_words:
                        inset = max(2, cell // 12)
                        _draw_cross(
                            screen,
                            pygame.Rect(
                                x + inset,
                                y + inset,
                                cell - inset * 2,
                                cell - inset * 2,
                            ),
                        )

        for index, item in enumerate(PALETTE):
            rect = self._palette_rect(index)
            entity = _entity(item.symbol)
            if entity is not None and not entity.is_word:
                pygame.draw.rect(screen, PANEL, rect, border_radius=4)
                if draw_object(screen, entity, rect.inflate(-4, -4)):
                    if item.symbol == self.selected_symbol:
                        pygame.draw.rect(screen, ACCENT, rect, 3, border_radius=4)
                    continue
            color = entity.color if entity is not None else PANEL
            pygame.draw.rect(screen, color, rect, border_radius=4)
            label = chrome["hint"].render(item.label, True, _text_color(color))
            screen.blit(label, label.get_rect(center=rect.center))
            if item.symbol == self.selected_symbol:
                pygame.draw.rect(screen, ACCENT, rect, 3, border_radius=4)

        for label, rect, _action in self._buttons():
            pygame.draw.rect(screen, SELECT_BG, rect, border_radius=6)
            text = chrome["rule"].render(label, True, TITLE)
            screen.blit(text, text.get_rect(center=rect.center))

        y = 492
        for line in _wrap(self.message, chrome["hint"], 340):
            screen.blit(chrome["hint"].render(line, True, HINT), (590, y))
            y += 20

        hint = chrome["hint"].render(
            "左键放置 · 右键擦除 · Ctrl+S 保存 · Ctrl+Z 撤销 · Ctrl+Y 重做 · Esc 返回",
            True,
            HINT,
        )
        screen.blit(hint, (40, 640))


def _entity(symbol: str):
    item = BY_SYMBOL.get(symbol)
    if item is None or item.kind == "empty":
        return None
    if item.kind == "word":
        return make_word(item.value)
    return make_object(item.value)


def _draw_entity(screen, entity, x: int, y: int, cell: int, chrome, color=None) -> None:
    import pygame

    inset = max(2, cell // 12)
    rect = pygame.Rect(x + inset, y + inset, cell - inset * 2, cell - inset * 2)
    if draw_object(screen, entity, rect):
        return
    if color is None:
        color = entity.color
    radius = max(3, cell // 8)
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, (18, 18, 24), rect, 1, border_radius=radius)
    if entity.id == "wall":
        inner = rect.inflate(-max(4, cell // 5), -max(4, cell // 5))
        pygame.draw.rect(screen, (68, 72, 90), inner, 2, border_radius=max(2, radius - 2))
        return
    font = chrome["word"] if entity.is_word else chrome["object"]
    label = font.render(entity.text, True, _text_color(color))
    screen.blit(label, label.get_rect(center=rect.center))


def _text_color(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = bg
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return TEXT_DARK if luminance > 140 else TEXT_LIGHT


def _dim_color(color: tuple[int, int, int], factor: float = 0.48) -> tuple[int, int, int]:
    return tuple(max(0, int(channel * factor)) for channel in color)


def _draw_cross(screen, rect, color=(238, 82, 82)) -> None:
    import pygame

    inset = max(4, rect.width // 5)
    pygame.draw.line(
        screen,
        color,
        (rect.left + inset, rect.top + inset),
        (rect.right - inset, rect.bottom - inset),
        3,
    )
    pygame.draw.line(
        screen,
        color,
        (rect.right - inset, rect.top + inset),
        (rect.left + inset, rect.bottom - inset),
        3,
    )


def _wrap(text: str, font, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and font.size(candidate)[0] > width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:3]


def _clipboard_get() -> str:
    try:
        import pygame

        data = pygame.scrap.get(pygame.SCRAP_TEXT)
        if isinstance(data, bytes):
            return data.replace(b"\x00", b"").decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return ""


def _clipboard_set(text: str) -> bool:
    try:
        import pygame

        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
        return True
    except Exception:
        return False
