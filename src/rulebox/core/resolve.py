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


def is_floating(entity: Entity | None, props: dict[str, set[str]]) -> bool:
    return has_prop(entity, props, "FLOAT")


def same_layer(
    first: Entity | None, second: Entity | None, props: dict[str, set[str]]
) -> bool:
    """浮物件与普通物件分处两层；只有同层才会碰撞和结算。"""
    return is_floating(first, props) == is_floating(second, props)


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
    """同层恰好两个 TELE 格时，把这一步「走进」其中一个格子的物件换到另一个格子。

    传送也遵守浮层：普通物件不会触发浮传送门，反之亦然。
    按移动后的实际位置判定，所以只结算一次：到目的地不再连锁；
    原地不动的住户、词块和 TELE 自身都不传。
    """
    for entity in moved:
        if entity.is_word or has_prop(entity, props, "TELE"):
            continue
        sites: list[tuple[int, int]] = []
        for row, col, portal in world.find(
            lambda candidate: has_prop(candidate, props, "TELE")
            and same_layer(candidate, entity, props)
        ):
            if (row, col) not in sites:
                sites.append((row, col))
        if len(sites) != 2:
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


def has_defeat_touch(world: World, props: dict[str, set[str]]) -> bool:
    """「你」与带 DEFEAT 的物件同格且同层时判负。"""
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        for you in cell:
            if not has_prop(you, props, "YOU"):
                continue
            if any(
                has_prop(other, props, "DEFEAT") and same_layer(you, other, props)
                for other in cell
            ):
                return True
    return False


def _shut_victims(world: World, props: dict[str, set[str]]) -> list[tuple[int, int, Entity]]:
    """同层同格的 OPEN 与 SHUT 物件互相抵消；不同层互不影响。"""
    victims: list[tuple[int, int, Entity]] = []
    seen: set[int] = set()
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        for floating in (False, True):
            layer = [entity for entity in cell if is_floating(entity, props) == floating]
            opens = [entity for entity in layer if has_prop(entity, props, "OPEN")]
            shuts = [entity for entity in layer if has_prop(entity, props, "SHUT")]
            if not opens or not shuts:
                continue
            involved = opens + shuts
            for entity in involved:
                if id(entity) in seen:
                    continue
                if any(other is not entity for other in involved):
                    seen.add(id(entity))
                    victims.append((row, col, entity))
    return victims


def _sink_victims(world: World, props: dict[str, set[str]]) -> list[tuple[int, int, Entity]]:
    """同层水摧毁不带 FLOAT 的物件；词块和水自身不受影响，浮物件可安全穿过。"""
    victims: list[tuple[int, int, Entity]] = []
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        for water in cell:
            if not _is_water(water):
                continue
            victims += [
                (row, col, entity)
                for entity in cell
                if not _is_water(entity)
                and not entity.is_word
                and same_layer(water, entity, props)
                and not has_prop(entity, props, "FLOAT")
            ]
    return victims


def _melt_victims(world: World, props: dict[str, set[str]]) -> list[tuple[int, int, Entity]]:
    """同层 HOT 与 MELT 接触时融化；不同层互不影响。"""
    victims: list[tuple[int, int, Entity]] = []
    for row, col in _cells(world):
        cell = world.entities_at(row, col)
        for hot in cell:
            if not has_prop(hot, props, "HOT"):
                continue
            victims += [
                (row, col, entity)
                for entity in cell
                if same_layer(hot, entity, props)
                and has_prop(entity, props, "MELT")
                and not has_prop(entity, props, "HOT")
            ]
    return victims


def _is_water(entity: Entity) -> bool:
    return entity.id == WATER_ID


def _cells(world: World) -> list[tuple[int, int]]:
    return [(row, col) for row in range(world.height) for col in range(world.width)]
