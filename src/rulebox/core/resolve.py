"""属性查询：谁是「你」、谁可推、谁挡路，以及传送与开关/水/热的接触结算。

处理 YOU / PUSH / STOP / WIN / FLOAT / HOT / MELT / OPEN / SHUT / TELE。
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


def is_obstacle(
    entity: Entity, props: dict[str, set[str]], *, opener: bool = False
) -> bool:
    """对正在进入该格的移动方来说，这个实体是否算「占用」。

    水/热不占地；传送门本身不占地（进来的人由传送结算处理）；
    SHUT 只对带 OPEN 的移动方让路。
    """
    if is_hazard(entity, props) or has_prop(entity, props, "TELE"):
        return False
    return not (opener and has_prop(entity, props, "SHUT"))


def apply_teleports(
    world: World, props: dict[str, set[str]], moved: list[Entity]
) -> None:
    """恰好两个 TELE 格时，把这一步「走进」其中一个格子的物件换到另一个格子。

    按移动后的实际位置判定，所以只结算一次：到目的地不再连锁；
    原地不动的住户、词块和 TELE 自身都不传。
    """
    sites: list[tuple[int, int]] = []
    for row, col, _entity in world.find(lambda entity: has_prop(entity, props, "TELE")):
        if (row, col) not in sites:
            sites.append((row, col))
    if len(sites) != 2:
        return

    for entity in moved:
        if entity.is_word or has_prop(entity, props, "TELE"):
            continue
        for index, site in enumerate(sites):
            if not any(other is entity for other in world.entities_at(*site)):
                continue
            dest = sites[1 - index]
            world.remove(site[0], site[1], entity)
            world.add(dest[0], dest[1], entity)
            break


def apply_contacts(world: World, props: dict[str, set[str]]) -> None:
    """接触结算：先开/关，再水，最后热/融。毁灭结果由调用方在变形后统一判定。"""
    for row, col, entity in _shut_victims(world, props):
        world.remove(row, col, entity)
    for row, col, entity in _sink_victims(world, props):
        world.remove(row, col, entity)
    for row, col, entity in _melt_victims(world, props):
        world.remove(row, col, entity)


def _shut_victims(world: World, props: dict[str, set[str]]) -> list[tuple[int, int, Entity]]:
    """带 OPEN 的格子里，摧毁同格的 SHUT 物件；自身也是 OPEN 的不自我摧毁。"""
    victims: list[tuple[int, int, Entity]] = []
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        if not any(has_prop(entity, props, "OPEN") for entity in cell):
            continue
        victims += [
            (row, col, entity)
            for entity in cell
            if has_prop(entity, props, "SHUT") and not has_prop(entity, props, "OPEN")
        ]
    return victims


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
