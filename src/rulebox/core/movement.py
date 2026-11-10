"""移动、推箱与推词。

每一步的流程：
    快照 -> 解析规则 -> 找出所有「你」 -> 逐个尝试移动 -> 失败则回滚
"""

from __future__ import annotations

from dataclasses import dataclass

from .resolve import has_prop, you_positions
from .rules import parse_rules, property_map
from .world import World

MAX_PUSH_DEPTH = 10


@dataclass
class MoveResult:
    moved: bool
    won: bool = False


def try_move(world: World, dr: int, dc: int) -> MoveResult:
    """尝试让所有「你」朝 (dr, dc) 走一步。"""
    world.snapshot()

    props = property_map(parse_rules(world))
    movers = you_positions(world, props)
    if not movers:
        world.undo()
        return MoveResult(False)

    moved_any = False
    for row, col in movers:
        result = _move_one(world, row, col, dr, dc, props, can_win=True)
        if result.won:
            return MoveResult(True, won=True)
        moved_any = moved_any or result.moved

    if not moved_any:
        world.undo()
        return MoveResult(False)

    return MoveResult(True)


def _move_one(
    world: World,
    row: int,
    col: int,
    dr: int,
    dc: int,
    props: dict[str, set[str]],
    *,
    can_win: bool,
) -> MoveResult:
    entity = world.get(row, col)
    if entity is None:
        return MoveResult(False)

    target_row, target_col = row + dr, col + dc
    if not world.in_bounds(target_row, target_col):
        return MoveResult(False)

    target = world.get(target_row, target_col)

    if target is None:
        world.set(target_row, target_col, entity)
        world.set(row, col, None)
        return MoveResult(True)

    # 词块永远可推，且不参与属性判定
    if target.is_word:
        pushed = _move_one(world, target_row, target_col, dr, dc, props, can_win=False)
        if not pushed.moved:
            return MoveResult(False)
        world.set(target_row, target_col, entity)
        world.set(row, col, None)
        return MoveResult(True)

    if has_prop(target, props, "WIN"):
        if can_win:
            return MoveResult(True, won=True)
        return MoveResult(False)

    if has_prop(target, props, "STOP"):
        return MoveResult(False)

    if has_prop(target, props, "PUSH"):
        pushed = _move_one(world, target_row, target_col, dr, dc, props, can_win=False)
        if not pushed.moved:
            return MoveResult(False)
        world.set(target_row, target_col, entity)
        world.set(row, col, None)
        return MoveResult(True)

    return MoveResult(False)
