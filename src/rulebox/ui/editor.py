"""关卡编辑器：调色板、放置、保存、分享码导入导出。"""

from __future__ import annotations

from pathlib import Path

from ..core.catalog import LEVELS_DIR, ROOT
from ..core.entities import make_object, make_word
from ..core.level import parse_level
from ..core.level_builder import (
    BY_SYMBOL,
    PALETTE,
    blank_cells,
    build_level_text,
    save_level_text,
    share_decode,
    share_encode,
)

EXPORTS_DIR = ROOT / "exports"

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

GRID_X, GRID_Y, CELL = 40, 110, 44
GRID_COLS, GRID_ROWS = 11, 8
PALETTE_X, PALETTE_Y = 40, 478
PALETTE_COLS = 10
PALETTE_TILE = 38
PALETTE_GAP = 4


class Editor:
    def __init__(self, on_changed=None, on_back=None):
        self.cells = blank_cells(GRID_COLS, GRID_ROWS)
        self.name = "自制关卡"
        self.selected_symbol = "@"
        self.name_active = False
        self.message = "左键放置 · 右键擦除 · Ctrl+S 保存"
        self.on_changed = on_changed
        self.on_back = on_back
        try:
            import pygame

            pygame.scrap.init()
        except Exception:
            pass

    # ---------- 操作 ----------

    def build_text(self) -> str:
        text = build_level_text(self.name, self.cells)
        parse_level(text, source="<editor>")
        return text

    def save(self) -> None:
        try:
            text = self.build_text()
            path = save_level_text(text, LEVELS_DIR, "custom")
        except Exception as exc:
            self.message = f"保存失败：{exc}"
            return
        self.message = f"已保存到关卡库：{path.name}"
        if self.on_changed:
            self.on_changed()

    def export(self) -> None:
        try:
            text = self.build_text()
            path = save_level_text(text, EXPORTS_DIR, "export")
            code = share_encode(text)
            path.with_suffix(".code").write_text(code, encoding="utf-8")
        except Exception as exc:
            self.message = f"导出失败：{exc}"
            return
        copied = _clipboard_set(code)
        tail = "，分享码已复制" if copied else "（剪贴板不可用，见 .code 文件）"
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
            path = save_level_text(text, LEVELS_DIR, "imported")
        except ValueError as exc:
            self.message = f"导入失败：{exc}"
            return
        self.message = f"已导入到关卡库：{path.name}"
        if self.on_changed:
            self.on_changed()

    def clear(self) -> None:
        self.cells = blank_cells(GRID_COLS, GRID_ROWS)
        self.message = "已清空，保留边框"

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
        return None

    def handle_click(self, pos: tuple[int, int], button: int) -> None:
        import pygame

        if self._name_rect().collidepoint(pos):
            self.name_active = True
            return
        self.name_active = False

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
            self.cells[row][col] = self.selected_symbol if button == 1 else "."

    # ---------- 布局 ----------

    def _name_rect(self):
        import pygame

        return pygame.Rect(590, 110, 340, 38)

    def _buttons(self):
        import pygame

        rows = [
            ("保存到关卡库", self.save),
            ("导出分享码", self.export),
            ("导入分享码", self.import_share),
            ("清空", self.clear),
        ]
        result = []
        for index, (label, action) in enumerate(rows):
            result.append((label, pygame.Rect(590, 170 + index * 50, 340, 40), action))
        result.append(
            ("返回菜单", pygame.Rect(590, 370, 340, 40), self.on_back or (lambda: None))
        )
        return result

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
        x, y = pos
        if not (GRID_X <= x < GRID_X + GRID_COLS * CELL):
            return None
        if not (GRID_Y <= y < GRID_Y + GRID_ROWS * CELL):
            return None
        return (y - GRID_Y) // CELL, (x - GRID_X) // CELL

    # ---------- 绘制 ----------

    def draw(self, screen, chrome) -> None:
        import pygame

        screen.fill(BG)
        title = chrome["title"].render("关卡编辑器", True, TITLE)
        screen.blit(title, (40, 24))

        name_rect = self._name_rect()
        pygame.draw.rect(screen, PANEL, name_rect, border_radius=6)
        border = ACCENT if self.name_active else GRID_LINE
        pygame.draw.rect(screen, border, name_rect, 2, border_radius=6)
        name_label = chrome["rule"].render(f"关卡名：{self.name}", True, TITLE)
        screen.set_clip(name_rect.inflate(-12, -8))
        screen.blit(name_label, (name_rect.x + 8, name_rect.y + 8))
        screen.set_clip(None)

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = GRID_X + col * CELL
                y = GRID_Y + row * CELL
                floor = FLOOR_A if (row + col) % 2 == 0 else FLOOR_B
                pygame.draw.rect(screen, floor, (x, y, CELL, CELL))
                pygame.draw.rect(screen, GRID_LINE, (x, y, CELL, CELL), 1)
                entity = _entity(self.cells[row][col])
                if entity is not None:
                    _draw_entity(screen, entity, x, y, CELL, chrome)

        for index, item in enumerate(PALETTE):
            rect = self._palette_rect(index)
            entity = _entity(item.symbol)
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

        y = 440
        for line in _wrap(self.message, chrome["hint"], 340):
            screen.blit(chrome["hint"].render(line, True, HINT), (590, y))
            y += 20

        hint = chrome["hint"].render(
            "左键放置 · 右键擦除 · Ctrl+S 保存 · Ctrl+E 导出 · Esc 返回", True, HINT
        )
        screen.blit(hint, (40, 640))


def _entity(symbol: str):
    item = BY_SYMBOL.get(symbol)
    if item is None or item.kind == "empty":
        return None
    if item.kind == "word":
        return make_word(item.value)
    return make_object(item.value)


def _draw_entity(screen, entity, x: int, y: int, cell: int, chrome) -> None:
    import pygame

    inset = max(3, cell // 12)
    rect = pygame.Rect(x + inset, y + inset, cell - inset * 2, cell - inset * 2)
    radius = max(4, cell // 8)
    pygame.draw.rect(screen, entity.color, rect, border_radius=radius)
    pygame.draw.rect(screen, (18, 18, 24), rect, 1, border_radius=radius)
    if entity.id == "wall":
        inner = rect.inflate(-max(6, cell // 5), -max(6, cell // 5))
        pygame.draw.rect(screen, (68, 72, 90), inner, 2, border_radius=max(2, radius - 2))
        return
    font = chrome["word"] if entity.is_word else chrome["object"]
    label = font.render(entity.text, True, _text_color(entity.color))
    screen.blit(label, label.get_rect(center=rect.center))


def _text_color(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = bg
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return TEXT_DARK if luminance > 140 else TEXT_LIGHT


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
    return lines[:4]


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
