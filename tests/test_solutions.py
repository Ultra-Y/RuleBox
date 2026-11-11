from pathlib import Path

import pytest

from rulebox.core.game import Game
from rulebox.core.level import load_level

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ROOT / "content" / "levels"
SOLUTIONS = ROOT / "solutions"
MOVES = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1),
}


def solution_cases():
    cases = []
    for solution in sorted(SOLUTIONS.glob("*.txt")):
        number = solution.stem.split("-", 1)[0]
        matches = sorted(LEVELS.glob(f"{number}-*.txt"))
        assert len(matches) == 1, f"{solution.name} 找不到唯一关卡"
        moves = "".join(solution.read_text(encoding="utf-8").split())
        cases.append((matches[0], moves))
    return cases


@pytest.mark.parametrize("level_path,moves", solution_cases())
def test_solution_reaches_win(level_path: Path, moves: str):
    game = Game(load_level(level_path))
    for index, char in enumerate(moves):
        assert char in MOVES, f"{level_path.name} 第 {index + 1} 步方向非法：{char}"
        assert not game.won, f"{level_path.name} 提前胜利"
        assert not game.lost, f"{level_path.name} 第 {index + 1} 步前已失败"
        game.move(*MOVES[char])
        if game.won:
            break

    assert game.won, f"{level_path.name} 解法未通关：{moves}"
