"""一局游戏的状态：世界、步数、胜负、撤销。"""

from __future__ import annotations

from .level import Level
from .movement import MoveResult, try_move
from .world import World


class Game:
    def __init__(self, level: Level):
        self.level = level
        self.reset()

    def reset(self) -> None:
        self.world = World(self.level)
        self.moves = 0
        self.won = False
        self.lost = False

    def move(self, dr: int, dc: int) -> MoveResult:
        if self.won or self.lost:
            return MoveResult(False)
        result = try_move(self.world, dr, dc)
        if result.moved:
            self.moves += 1
        if result.won:
            self.won = True
        if result.lost:
            self.lost = True
        return result

    def undo(self) -> bool:
        if not self.world.undo():
            return False
        self.moves = max(0, self.moves - 1)
        self.won = False
        self.lost = False
        return True
