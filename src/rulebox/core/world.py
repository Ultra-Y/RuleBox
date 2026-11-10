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


Grid = list[list[list[Entity]]]


class World:
    def __init__(self, level: Level):
        self.name = level.name
        self.width = level.width
        self.height = level.height
        self.cells: Grid = [
            [[] if entity is None else [entity] for entity in row]
            for row in level.cells
        ]
        self._history: list[Grid] = []

    # ---------- 查询与修改 ----------

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def entities_at(self, row: int, col: int) -> tuple[Entity, ...]:
        """返回一格里的所有实体，顺序为底层到顶层。"""
        if not self.in_bounds(row, col):
            raise IndexError(f"坐标越界：({row}, {col})")
        return tuple(self.cells[row][col])

    def get(self, row: int, col: int) -> Entity | None:
        """返回格子最上层实体；空格返回 None。"""
        entities = self.entities_at(row, col)
        return entities[-1] if entities else None

    def set(self, row: int, col: int, entity: Entity | None) -> None:
        """替换整格内容；需要保留底层实体时使用 add/remove。"""
        if not self.in_bounds(row, col):
            raise IndexError(f"坐标越界：({row}, {col})")
        self.cells[row][col] = [] if entity is None else [entity]

    def add(self, row: int, col: int, entity: Entity) -> None:
        if not self.in_bounds(row, col):
            raise IndexError(f"坐标越界：({row}, {col})")
        self.cells[row][col].append(entity)

    def remove(self, row: int, col: int, entity: Entity) -> None:
        if not self.in_bounds(row, col):
            raise IndexError(f"坐标越界：({row}, {col})")
        self.cells[row][col].remove(entity)

    def find(self, predicate: Callable[[Entity], bool]) -> list[tuple[int, int, Entity]]:
        found: list[tuple[int, int, Entity]] = []
        for row in range(self.height):
            for col in range(self.width):
                for entity in self.cells[row][col]:
                    if predicate(entity):
                        found.append((row, col, entity))
        return found

    # ---------- 快照与撤销 ----------

    def snapshot(self) -> None:
        """在一步操作之前调用，之后就能 undo 回来。"""
        self._history.append([[cell[:] for cell in row] for row in self.cells])

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
                entity = self.get(row, col)
                if entity is None:
                    chars.append(".")
                elif entity.is_word:
                    chars.append(entity.text)
                else:
                    chars.append(_ASCII.get(entity.id, "?"))
            lines.append("".join(chars))
        return "\n".join(lines)
