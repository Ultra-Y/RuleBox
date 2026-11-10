"""移动、推箱与推词。

每一步的流程：
    快照 -> 解析规则 -> 找出所有「你」 -> 逐个尝试移动
    -> 接触结算 -> 变形 -> 失败则回滚
"""

from __future__ import annotations

from dataclasses import dataclass

from .entities import Entity
from .resolve import (
    apply_contacts,
    apply_transforms,
    has_prop,
    is_hazard,
    you_positions,
)
from .rules import parse_rules, property_map, transform_map
from .world import World

MAX_PUSH_DEPTH = 10


@dataclass
class MoveResult:
    moved: bool
    won: bool = False
    lost: bool = False


def try_move(world: World, dr: int, dc: int) -> MoveResult:
    """尝试让所有「你」朝 (dr, dc) 走一步。"""
    world.snapshot()

    rules = parse_rules(world)
    props = property_map(rules)
    transforms = transform_map(rules)
    movers = you_positions(world, props)
    if not movers:
        world.undo()
        return MoveResult(False)

    moved_any = False
    won = False
    for row, col in movers:
        result = _move_one(world, row, col, dr, dc, props, can_win=True)
        if result.won:
            won = True
            break
        moved_any = moved_any or result.moved

    if not moved_any and not won:
        world.undo()
        return MoveResult(False)

    lost = False
    if not won:
        # 接触结算用回合开始时解析出的属性，和水/热是否被推动无关。
        lost = apply_contacts(world, props)

    # 接触结算后统一变形；下一步和 UI 会重新解析变形后的属性。
    apply_transforms(world, transforms)
    return MoveResult(True, won=won, lost=lost)


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
    # 格子里只有水/热时不算占用：推进去由接触结算决定生死。
    if any(has_prop(target, props, "YOU") for target in targets):
        return MoveResult(False)
    occupied = any(not is_hazard(target, props) for target in targets)
    if occupied and not can_win:
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
