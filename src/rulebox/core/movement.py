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
    has_defeat_touch,
    has_prop,
    is_floating,
    is_obstacle,
    same_layer,
    spawn_destroyed,
    you_positions,
)
from .rules import parse_rules, property_map, ruled_nouns, spawn_map, transform_map
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
    spawns = spawn_map(rules)
    ruled = ruled_nouns(rules)
    movers = you_positions(world, props)
    if not movers:
        world.undo()
        return MoveResult(False)

    # 「移」物件只使用操作开始前记录的方向；本回合刚被推动不会立刻多走一步。
    auto_actors = _capture_auto(world, props, (dr, dc))

    # 这一步真正移动过的物件，传送结算只认它们。
    trail: list[Entity] = []
    moved_any = False
    won = False
    for row, col in movers:
        result = _move_one(
            world, row, col, dr, dc, props, ruled, trail, can_win=True
        )
        if result.won:
            won = True
            break
        moved_any = moved_any or result.moved

    if won:
        apply_transforms(world, transforms)
        return MoveResult(True, won=True)

    # 传送和接触结算都用回合开始时解析出的属性，和水/热/门是否被推动无关。
    apply_teleports(world, props, trail)

    auto_trail: list[Entity] = []
    auto_moved = _move_auto(
        world, auto_actors, props, ruled, auto_trail, skip=trail
    )
    apply_teleports(world, props, auto_trail)

    destroyed = apply_contacts(world, props)
    spawn_destroyed(world, destroyed, spawns)

    # 接触结算后统一变形；变形可能制造或消灭「你」，所以之后要重新解析再判负。
    apply_transforms(world, transforms)
    lost = has_defeat_touch(world, props) or not you_positions(
        world, property_map(parse_rules(world))
    )
    if not moved_any and not auto_moved:
        world.undo()
        return MoveResult(False)
    return MoveResult(True, lost=lost)


def try_wait(world: World) -> MoveResult:
    """不移动「你」，只让所有「移」物件沿上次方向走一格。"""
    world.snapshot()

    rules = parse_rules(world)
    props = property_map(rules)
    transforms = transform_map(rules)
    spawns = spawn_map(rules)
    ruled = ruled_nouns(rules)
    auto_actors = _capture_auto(world, props)
    if not auto_actors:
        world.undo()
        return MoveResult(False)

    trail: list[Entity] = []
    moved = _move_auto(world, auto_actors, props, ruled, trail)
    if not moved:
        world.undo()
        return MoveResult(False)

    apply_teleports(world, props, trail)
    destroyed = apply_contacts(world, props)
    spawn_destroyed(world, destroyed, spawns)
    apply_transforms(world, transforms)
    lost = has_defeat_touch(world, props) or not you_positions(
        world, property_map(parse_rules(world))
    )
    return MoveResult(True, lost=lost)


def _capture_auto(
    world: World,
    props: dict[str, set[str]],
    default_dir: tuple[int, int] | None = None,
) -> list[tuple[Entity, tuple[int, int]]]:
    """记录开始时所有「移」物件及其方向；没有历史方向时用本次按键方向。"""
    actors: list[tuple[Entity, tuple[int, int]]] = []
    for _row, _col, entity in world.find(lambda candidate: has_prop(candidate, props, "MOVE")):
        direction = world.get_move_dir(entity)
        if direction is None:
            direction = default_dir
        if direction is not None:
            actors.append((entity, direction))
    return actors


def _move_auto(
    world: World,
    actors: list[tuple[Entity, tuple[int, int]]],
    props: dict[str, set[str]],
    ruled: set[str],
    trail: list[Entity],
    *,
    skip: list[Entity] | None = None,
) -> bool:
    """让「移」物件按记录方向走一步；不会触发胜利，撞边/停时反向。"""
    moved = False
    for entity, (dr, dc) in actors:
        if any(candidate is entity for candidate in trail):
            continue
        if skip and any(candidate is entity for candidate in skip):
            continue
        locations = world.find(lambda candidate: candidate is entity)
        if len(locations) != 1:
            continue
        row, col = locations[0][0], locations[0][1]
        if not any(candidate is entity for candidate in world.entities_at(row, col)):
            continue
        result = _move_one(
            world,
            row,
            col,
            dr,
            dc,
            props,
            ruled,
            trail,
            can_win=False,
            auto=True,
            specific=entity,
        )
        if result.moved:
            moved = True
            continue
        if not _auto_should_bounce(world, entity, row, col, dr, dc, props):
            continue
        # 反方向也写入历史方向；即使反方向仍被挡住，下一次也朝反方向尝试。
        world.set_move_dir(entity, -dr, -dc)
        reverse = _move_one(
            world,
            row,
            col,
            -dr,
            -dc,
            props,
            ruled,
            trail,
            can_win=False,
            auto=True,
            specific=entity,
        )
        moved = moved or reverse.moved
    return moved


def _auto_should_bounce(
    world: World,
    entity: Entity,
    row: int,
    col: int,
    dr: int,
    dc: int,
    props: dict[str, set[str]],
) -> bool:
    """只有地图边缘和同层不可推的 STOP 会让「移」物件反向。"""
    target_row, target_col = row + dr, col + dc
    if not world.in_bounds(target_row, target_col):
        return True
    for target in world.entities_at(target_row, target_col):
        related = (
            same_layer(entity, target, props)
            or (
                target.is_word
                and (is_floating(entity, props) or is_floating(target, props))
            )
            or (is_floating(entity, props) and has_prop(target, props, "STOP"))
        )
        if not related:
            continue
        if has_prop(target, props, "STOP") and not _is_pushable(target, props):
            return True
    return False


def _is_pushable(entity: Entity, props: dict[str, set[str]]) -> bool:
    return entity.is_word or has_prop(entity, props, "PUSH")


def _move_one(
    world: World,
    row: int,
    col: int,
    dr: int,
    dc: int,
    props: dict[str, set[str]],
    ruled: set[str],
    trail: list[Entity],
    *,
    can_win: bool,
    auto: bool = False,
    specific: Entity | None = None,
) -> MoveResult:
    """移动一个实体；can_win 为 True 表示它是最外层的「你」。"""
    cell = world.entities_at(row, col)
    if specific is not None:
        entity = specific
    elif can_win:
        entity = next(
            (candidate for candidate in reversed(cell) if has_prop(candidate, props, "YOU")),
            None,
        )
    else:
        entity = world.get(row, col)
    if entity is None:
        return MoveResult(False)

    # 「你」自身带 WIN：操作它移动时直接胜利，不需要走进赢格。
    if can_win and has_prop(entity, props, "WIN"):
        return MoveResult(True, won=True)

    weak_mover = has_prop(entity, props, "WEAK")
    target_row, target_col = row + dr, col + dc
    if not world.in_bounds(target_row, target_col):
        return MoveResult(False)

    mover_floating = is_floating(entity, props)
    targets = [
        target
        for target in world.entities_at(target_row, target_col)
        if same_layer(entity, target, props)
        or (
            target.is_word
            and (mover_floating or is_floating(target, props))
        )
        or (mover_floating and has_prop(target, props, "STOP"))
    ]
    if not targets:
        _relocate(world, row, col, target_row, target_col, entity, trail)
        if can_win:
            _pull_behind(world, row, col, dr, dc, entity, props, trail)
        return MoveResult(True)

    # 停 + 推 的物件可以被推；只有“停但不可推”的物件才挡路。
    stop_blockers = [
        target
        for target in targets
        if has_prop(target, props, "STOP") and not _is_pushable(target, props)
    ]
    if stop_blockers:
        if not weak_mover:
            return MoveResult(False)

    # 关 + 推 的门和其他可推物件一样可以被推；
    # 只有“关但不可推”的门才挡住没有 OPEN 的移动方。
    opener = has_prop(entity, props, "OPEN")
    shut_blockers = [
        target
        for target in targets
        if has_prop(target, props, "SHUT") and not _is_pushable(target, props)
    ]
    if not opener and shut_blockers:
        return MoveResult(False)

    if any(has_prop(target, props, "WIN") for target in targets):
        if can_win:
            return MoveResult(True, won=True)
        if not auto:
            return MoveResult(False)

    # 带 OPEN 的移动方碰到 SHUT 时应抵消门，而不是把可推的门推走。
    pushable = next(
        (
            target
            for target in targets
            if _is_pushable(target, props)
            and not (opener and has_prop(target, props, "SHUT"))
        ),
        None,
    )
    if pushable is not None:
        pushed = _move_one(
            world, target_row, target_col, dr, dc, props, ruled, trail, can_win=False
        )
        if not pushed.moved:
            return MoveResult(False)
        _relocate(world, row, col, target_row, target_col, entity, trail)
        if can_win:
            _pull_behind(world, row, col, dr, dc, entity, props, trail)
        return MoveResult(True)

    # 推链里的非「你」物件不能进入占用格；「你」也不能与另一个「你」重叠。
    # 格子里只有水/热/传送门，或者门对 OPEN 移动方让路时，不算占用。
    if any(has_prop(target, props, "YOU") for target in targets):
        return MoveResult(False)
    occupied = any(
        is_obstacle(
            target, props, opener=opener, ruled=ruled, mover=entity
        )
        for target in targets
        if not (auto and has_prop(target, props, "WIN"))
    )
    if occupied and not can_win:
        if not (weak_mover and any(has_prop(target, props, "STOP") for target in targets)):
            return MoveResult(False)

    _relocate(world, row, col, target_row, target_col, entity, trail)
    if can_win:
        _pull_behind(world, row, col, dr, dc, entity, props, trail)
    return MoveResult(True)


def _pull_behind(
    world: World,
    row: int,
    col: int,
    dr: int,
    dc: int,
    mover: Entity,
    props: dict[str, set[str]],
    trail: list[Entity],
) -> None:
    """「你」移动后，把正后方同层的 PULL 物件拉进刚空出的格子。"""
    behind_row, behind_col = row - dr, col - dc
    if not world.in_bounds(behind_row, behind_col):
        return
    if world.entities_at(row, col):
        return
    behind = world.entities_at(behind_row, behind_col)
    target = next(
        (
            entity
            for entity in reversed(behind)
            if has_prop(entity, props, "PULL") and same_layer(mover, entity, props)
        ),
        None,
    )
    if target is None:
        return
    world.remove(behind_row, behind_col, target)
    world.add(row, col, target)
    world.set_move_dir(target, dr, dc)
    trail.append(target)


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
    world.set_move_dir(entity, target_row - row, target_col - col)
    trail.append(entity)
