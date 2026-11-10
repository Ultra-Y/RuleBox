"""世界状态：网格、取放、快照与撤销。

Day 1 只负责"状态"，不负责"规则"。
"""

from __future__ import annotations

from collections.abc import Callable

from .entities import Entity
from .level import Level

_ASCII = {
    "baba": "@",
    "wall": "#",
    "box": "$",
    "flag": "F",
    "water": "~",
    "fire": "^",
    "rock": "o",
    "door": "D",
    "key": "k",
    "portal": "P",
}


class World:
    def __init__(self, level: Level):
        self.name = level.name
        self.width = level.width
        self.height = level.height
        self.cells: list[list[Entity | None]] = [row[:] for row in level.cells]
        self._history: list[list[list[Entity | None]]] = []

    # ---------- 查询与修改 ----------

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def get(self, row: int, col: int) -> Entity | None:
        if not self.in_bounds(row, col):
            raise IndexError(f"坐标越界：({row}, {col})")
        return self.cells[row][col]

    def set(self, row: int, col: int, entity: Entity | None) -> None:
        if not self.in_bounds(row, col):
            raise IndexError(f"坐标越界：({row}, {col})")
        self.cells[row][col] = entity

    def find(self, predicate: Callable[[Entity], bool]) -> list[tuple[int, int, Entity]]:
        found: list[tuple[int, int, Entity]] = []
        for row in range(self.height):
            for col in range(self.width):
                entity = self.cells[row][col]
                if entity is not None and predicate(entity):
                    found.append((row, col, entity))
        return found

    # ---------- 快照与撤销 ----------

    def snapshot(self) -> None:
        """在一步操作之前调用，之后就能 undo 回来。"""
        self._history.append([row[:] for row in self.cells])

    def undo(self) -> bool:
        if not self._history:
            return False
        self.cells = self._history.pop()
        return True

    @property
    def can_undo(self) -> bool:
        return bool(self._history)

    # ---------- 调试用 ----------

    def to_ascii(self) -> str:
        lines: list[str] = []
        for row in range(self.height):
            chars: list[str] = []
            for col in range(self.width):
                entity = self.cells[row][col]
                if entity is None:
                    chars.append(".")
                elif entity.is_word:
                    chars.append(entity.text)
                else:
                    chars.append(_ASCII.get(entity.id, "?"))
            lines.append("".join(chars))
        return "\n".join(lines)
