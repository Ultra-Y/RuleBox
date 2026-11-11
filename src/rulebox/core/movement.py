"""移动、推箱与推词。

每一步的流程：
    快照 -> 解析规则 -> 找出所有「你」 -> 逐个尝试移动
    -> 传送 -> 接触结算 -> 变形 -> 失败则回滚
"""

from __future__ import annotations

from dataclasses import dataclass

from .entities import Entity
from .resolve import (
    apply_contacts,
    apply_teleports,
    apply_transforms,
    has_prop,
    is_obstacle,
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

    # 这一步真正移动过的物件，传送结算只认它们。
    trail: list[Entity] = []
    moved_any = False
    won = False
    for row, col in movers:
        result = _move_one(world, row, col, dr, dc, props, trail, can_win=True)
        if result.won:
            won = True
            break
        moved_any = moved_any or result.moved

    if not moved_any and not won:
        world.undo()
        return MoveResult(False)

    if not won:
        # 传送和接触结算都用回合开始时解析出的属性，和水/热/门是否被推动无关。
        apply_teleports(world, props, trail)
        apply_contacts(world, props)

    # 接触结算后统一变形；变形可能制造或消灭「你」，所以之后要重新解析再判负。
    apply_transforms(world, transforms)
    lost = False
    if not won:
        lost = not you_positions(world, property_map(parse_rules(world)))
    return MoveResult(True, won=won, lost=lost)


def _is_pushable(entity: Entity, props: dict[str, set[str]]) -> bool:
    return entity.is_word or has_prop(entity, props, "PUSH")


def _move_one(
    world: World,
    row: int,
    col: int,
    dr: int,
    dc: int,
    props: dict[str, set[str]],
    trail: list[Entity],
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
        _relocate(world, row, col, target_row, target_col, entity, trail)
        return MoveResult(True)

    # 停 + 推 的物件可以被推；只有“停但不可推”的物件才挡路。
    stop_blockers = [
        target
        for target in targets
        if has_prop(target, props, "STOP") and not _is_pushable(target, props)
    ]
    if stop_blockers:
        return MoveResult(False)

    # 门关着：只有带 OPEN 的移动方能进，进去后由接触结算把门毁掉。
    opener = has_prop(entity, props, "OPEN")
    if not opener and any(has_prop(target, props, "SHUT") for target in targets):
        return MoveResult(False)

    if any(has_prop(target, props, "WIN") for target in targets):
        if can_win:
            return MoveResult(True, won=True)
        return MoveResult(False)

    # 词块永远可推，且不参与属性判定。
    pushable = next(
        (target for target in targets if _is_pushable(target, props)),
        None,
    )
    if pushable is not None:
        pushed = _move_one(
            world, target_row, target_col, dr, dc, props, trail, can_win=False
        )
        if not pushed.moved:
            return MoveResult(False)
        _relocate(world, row, col, target_row, target_col, entity, trail)
        return MoveResult(True)

    # 推链里的非「你」物件不能进入占用格；「你」也不能与另一个「你」重叠。
    # 格子里只有水/热/传送门，或者门对 OPEN 移动方让路时，不算占用。
    if any(has_prop(target, props, "YOU") for target in targets):
        return MoveResult(False)
    occupied = any(is_obstacle(target, props, opener=opener) for target in targets)
    if occupied and not can_win:
        return MoveResult(False)

    _relocate(world, row, col, target_row, target_col, entity, trail)
    return MoveResult(True)


def _relocate(
    world: World,
    row: int,
    col: int,
    target_row: int,
    target_col: int,
    entity: Entity,
    trail: list[Entity],
) -> None:
    """只移动指定实体，保留来源格和目标格里的其他实体。"""
    world.remove(row, col, entity)
    world.add(target_row, target_col, entity)
    trail.append(entity)
