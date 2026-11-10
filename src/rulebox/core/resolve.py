"""属性查询：谁是「你」、谁可推、谁挡路，以及水/热的接触结算。

处理 YOU / PUSH / STOP / WIN / FLOAT / HOT / MELT；
开关、传送待后续实现。
"""

from __future__ import annotations

from .entities import Entity, make_object
from .world import World

WATER_ID = "water"


def has_prop(entity: Entity | None, props: dict[str, set[str]], prop: str) -> bool:
    """物件是否拥有某个属性。词块不参与属性系统。"""
    return (
        entity is not None
        and entity.kind == "object"
        and prop in props.get(entity.id, ())
    )


def you_positions(world: World, props: dict[str, set[str]]) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for row in range(world.height):
        for col in range(world.width):
            entities = world.entities_at(row, col)
            if any(has_prop(entity, props, "YOU") for entity in entities):
                found.append((row, col))
    return found


def apply_transforms(world: World, transforms: dict[str, str]) -> None:
    """按回合开始时的物件身份统一变形一次，词块不参与。"""
    pending = [
        (row, col, entity, transforms[entity.id])
        for row, col, entity in world.find(
            lambda entity: entity.kind == "object" and entity.id in transforms
        )
    ]
    for row, col, entity, target_id in pending:
        if target_id != entity.id:
            world.replace(row, col, entity, make_object(target_id))


def is_hazard(entity: Entity, props: dict[str, set[str]]) -> bool:
    """水与带 HOT 的物件：本身不挡路，同格来客交给接触结算。"""
    return _is_water(entity) or has_prop(entity, props, "HOT")


def apply_contacts(world: World, props: dict[str, set[str]]) -> bool:
    """接触结算：先水，再热/融。返回场上是否已没有「你」。"""
    for row, col, entity in _sink_victims(world, props):
        world.remove(row, col, entity)
    for row, col, entity in _melt_victims(world, props):
        world.remove(row, col, entity)
    return not you_positions(world, props)


def _sink_victims(world: World, props: dict[str, set[str]]) -> list[tuple[int, int, Entity]]:
    """水摧毁同格不带 FLOAT 的物件；词块和水自身不受影响。"""
    victims: list[tuple[int, int, Entity]] = []
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        if not any(_is_water(entity) for entity in cell):
            continue
        victims += [
            (row, col, entity)
            for entity in cell
            if not _is_water(entity) and not entity.is_word
            and not has_prop(entity, props, "FLOAT")
        ]
    return victims


def _melt_victims(world: World, props: dict[str, set[str]]) -> list[tuple[int, int, Entity]]:
    """有 HOT 物件的格子里，摧毁同时带 MELT 的物件；自身也是 HOT 的不自我摧毁。"""
    victims: list[tuple[int, int, Entity]] = []
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        if not any(has_prop(entity, props, "HOT") for entity in cell):
            continue
        victims += [
            (row, col, entity)
            for entity in cell
            if has_prop(entity, props, "MELT") and not has_prop(entity, props, "HOT")
        ]
    return victims


def _is_water(entity: Entity) -> bool:
    return entity.id == WATER_ID


def _cells(world: World) -> list[tuple[int, int]]:
    return [(row, col) for row in range(world.height) for col in range(world.width)]
