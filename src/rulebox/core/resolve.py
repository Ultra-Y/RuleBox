"""属性查询：谁是「你」、谁可推、谁挡路。

Day 2 只处理 YOU / PUSH / STOP / WIN；
水、热、开关、传送在 Day 3 的接触结算里处理。
"""

from __future__ import annotations

from .entities import Entity
from .world import World


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
