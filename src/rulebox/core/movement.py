"""移动、推箱与推词。

每一步的流程：
    快照 -> 解析规则 -> 找出所有「你」 -> 逐个尝试移动 -> 失败则回滚
"""

from __future__ import annotations

from dataclasses import dataclass

from .entities import Entity
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
    """移动一个实体；can_win 为 True 表示它是最外层的「你」。"""
    entity = world.get(row, col)
    if entity is None:
        return MoveResult(False)

    target_row, target_col = row + dr, col + dc
    if not world.in_bounds(target_row, target_col):
        return MoveResult(False)

    targets = world.entities_at(target_row, target_col)
    if not targets:
        _relocate(world, row, col, target_row, target_col, entity)
        return MoveResult(True)

    if any(has_prop(target, props, "STOP") for target in targets):
        return MoveResult(False)

    if any(has_prop(target, props, "WIN") for target in targets):
        if can_win:
            return MoveResult(True, won=True)
        return MoveResult(False)

    # 词块永远可推，且不参与属性判定。
    pushable = next(
        (
            target
            for target in targets
            if target.is_word or has_prop(target, props, "PUSH")
        ),
        None,
    )
    if pushable is not None:
        pushed = _move_one(world, target_row, target_col, dr, dc, props, can_win=False)
        if not pushed.moved:
            return MoveResult(False)
        _relocate(world, row, col, target_row, target_col, entity)
        return MoveResult(True)

    # 推链里的非「你」物件不能进入占用格；「你」也不能与另一个「你」重叠。
    if not can_win or any(has_prop(target, props, "YOU") for target in targets):
        return MoveResult(False)

    _relocate(world, row, col, target_row, target_col, entity)
    return MoveResult(True)


def _relocate(
    world: World,
    row: int,
    col: int,
    target_row: int,
    target_col: int,
    entity: Entity,
) -> None:
    """只移动指定实体，保留来源格和目标格里的其他实体。"""
    world.remove(row, col, entity)
    world.add(target_row, target_col, entity)
