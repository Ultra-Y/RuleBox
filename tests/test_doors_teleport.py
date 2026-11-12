"""开/关（OPEN/SHUT）与传（TELE）的结算。"""

from rulebox.core.entities import make_object, make_word
from rulebox.core.level import Level
from rulebox.core.movement import try_move
from rulebox.core.world import World


def rule(row: int, noun: str, prop: str) -> list[tuple[int, int, str]]:
    """把「名词 是 属性」放在第 row 行的前三格。"""
    return [(row, 0, noun), (row, 1, "是"), (row, 2, prop)]


def rule2(row: int, noun: str, prop_a: str, prop_b: str) -> list[tuple[int, int, str]]:
    """把「名词 是 属性甲 和 属性乙」放在第 row 行的前五格。"""
    return rule(row, noun, prop_a) + [(row, 3, "和"), (row, 4, prop_b)]


def make_world(words=(), objects=(), width=9, height=6) -> World:
    cells: list[list] = [[None] * width for _ in range(height)]
    for row, col, text in words:
        cells[row][col] = make_word(text)
    for row, col, object_id in objects:
        cells[row][col] = make_object(object_id)
    return World(Level("doors-teleport", width, height, cells))


def ids_at(world: World, row: int, col: int) -> list[str]:
    return [entity.id for entity in world.entities_at(row, col)]


def count(world: World, object_id: str) -> int:
    return len(world.find(lambda entity: entity.id == object_id))


# ---------- 开 / 关 ----------


DOOR_RULES = rule(0, "人", "你") + rule(1, "门", "关")


def test_shut_blocks_you_without_open():
    world = make_world(words=DOOR_RULES, objects=[(4, 1, "baba"), (4, 2, "door")])

    result = try_move(world, 0, 1)

    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert ids_at(world, 4, 2) == ["door"]
    assert not world.can_undo


def test_open_you_and_shut_cancel_each_other():
    words = DOOR_RULES + rule(2, "人", "开")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "door")])

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == []


def test_pushed_open_key_and_shut_cancel_each_other():
    words = rule(0, "人", "你") + rule2(1, "钥", "推", "开") + rule(2, "门", "关")
    world = make_world(
        words=words, objects=[(4, 1, "baba"), (4, 2, "key"), (4, 3, "door")]
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 2).id == "baba"
    assert ids_at(world, 4, 3) == []


def test_pushed_box_without_open_stops_at_shut():
    words = rule(0, "人", "你") + rule(1, "箱", "推") + rule(2, "门", "关")
    world = make_world(
        words=words, objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "door")]
    )

    result = try_move(world, 0, 1)

    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 2).id == "box"
    assert world.get(4, 3).id == "door"
    assert not world.can_undo


def test_open_key_cancels_with_open_shut_door():
    words = (
        rule(0, "人", "你")
        + rule2(1, "钥", "推", "开")
        + rule2(2, "门", "开", "关")
    )
    world = make_world(
        words=words, objects=[(4, 1, "baba"), (4, 2, "key"), (4, 3, "door")]
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 3) == []


def test_open_you_cancels_pushable_shut():
    words = rule(0, "人", "你") + rule(1, "人", "开") + rule2(2, "门", "关", "推")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "door")])

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == []
    assert ids_at(world, 4, 3) == []


def test_word_does_not_open_shut():
    words = DOOR_RULES + [(4, 2, "墙")]
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 3, "door")])

    result = try_move(world, 0, 1)

    assert not result.moved
    assert ids_at(world, 4, 2) == ["word:墙"]
    assert not world.can_undo


def test_undo_restores_destroyed_door():
    words = DOOR_RULES + rule(2, "人", "开")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "door")])

    assert try_move(world, 0, 1).moved
    assert world.undo() is True
    assert world.get(4, 1).id == "baba"
    assert ids_at(world, 4, 2) == ["door"]


def test_stop_still_blocks_open_you():
    words = DOOR_RULES + rule(2, "人", "开") + rule(3, "墙", "停")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "wall")])
    world.add(4, 2, make_object("door"))

    result = try_move(world, 0, 1)

    assert not result.moved
    assert ids_at(world, 4, 2) == ["wall", "door"]
    assert not world.can_undo


def test_shut_hides_win_from_you_without_open():
    words = DOOR_RULES + rule(2, "旗", "赢")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "door")])
    world.add(4, 2, make_object("flag"))

    result = try_move(world, 0, 1)

    assert not result.moved and not result.won
    assert world.get(4, 1).id == "baba"
    assert not world.can_undo


def test_open_you_wins_through_shut():
    words = DOOR_RULES + rule(2, "人", "开") + rule(3, "旗", "赢")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "door")])
    world.add(4, 2, make_object("flag"))

    result = try_move(world, 0, 1)

    # 胜利会短路接触结算，所以门此时仍然在场，只是不再挡路。
    assert result.won
    assert ids_at(world, 4, 2) == ["door", "flag"]


def test_door_without_shut_is_plain_overlap():
    world = make_world(words=rule(0, "人", "你"), objects=[(4, 1, "baba"), (4, 2, "door")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["door", "baba"]


# ---------- 传 ----------


TELE_RULES = rule(0, "人", "你") + rule(1, "传送", "传")


def test_two_teleport_sites_move_you():
    world = make_world(
        words=TELE_RULES,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal")],
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["portal"]
    assert ids_at(world, 4, 5) == ["portal", "baba"]
    assert count(world, "baba") == 1


def test_single_teleport_site_does_not_move_you():
    world = make_world(words=TELE_RULES, objects=[(4, 1, "baba"), (4, 2, "portal")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["portal", "baba"]


def test_three_teleport_sites_do_not_move_you():
    world = make_world(
        words=TELE_RULES,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal"), (5, 5, "portal")],
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["portal", "baba"]
    assert ids_at(world, 4, 5) == ["portal"]


def test_teleport_into_water_drowns_you():
    words = rule(0, "人", "你") + rule(1, "传送", "传")
    world = make_world(
        words=words,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal")],
    )
    world.add(4, 5, make_object("water"))

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == ["portal"]
    assert ids_at(world, 4, 5) == ["water"]


def test_float_portal_does_not_teleport_nonfloat_you():
    words = rule(0, "人", "你") + rule2(1, "传送", "传", "浮")
    world = make_world(
        words=words,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal")],
    )
    world.add(4, 5, make_object("water"))

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["portal", "baba"]
    assert ids_at(world, 4, 5) == ["portal", "water"]


def test_undo_restores_teleported_you():
    world = make_world(
        words=TELE_RULES,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal")],
    )

    assert try_move(world, 0, 1).moved
    assert world.undo() is True
    assert world.get(4, 1).id == "baba"
    assert ids_at(world, 4, 2) == ["portal"]
    assert ids_at(world, 4, 5) == ["portal"]


def test_pushed_box_is_teleported():
    words = rule(0, "人", "你") + rule(1, "箱", "推") + rule(2, "传送", "传")
    world = make_world(
        words=words,
        objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "portal"), (4, 5, "portal")],
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 2).id == "baba"
    assert ids_at(world, 4, 3) == ["portal"]
    assert ids_at(world, 4, 5) == ["portal", "box"]


def test_word_is_not_teleported():
    words = TELE_RULES + [(4, 2, "墙")]
    world = make_world(
        words=words, objects=[(4, 1, "baba"), (4, 3, "portal"), (4, 5, "portal")]
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 2).id == "baba"
    assert ids_at(world, 4, 3) == ["portal", "word:墙"]


def test_open_you_teleports_into_shut_and_breaks_it():
    """传送先于开/关结算：传进门后面的 OPEN「你」与门互相抵消。"""
    words = (
        rule(0, "人", "你")
        + rule(1, "人", "开")
        + rule(2, "传送", "传")
        + rule(3, "门", "关")
    )
    world = make_world(
        words=words,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal")],
    )
    world.add(4, 5, make_object("door"))

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == ["portal"]
    assert ids_at(world, 4, 5) == ["portal"]


def test_teleport_resolves_only_once_per_step():
    """只有「进入」传送格的物件会被传；目的地的住户留下，来的「你」也不会被弹回去。"""
    world = make_world(
        words=TELE_RULES,
        objects=[(4, 1, "baba"), (4, 2, "portal"), (4, 5, "portal")],
    )
    world.add(4, 5, make_object("rock"))

    assert try_move(world, 0, 1).moved
    assert ids_at(world, 4, 2) == ["portal"]
    assert ids_at(world, 4, 5) == ["portal", "rock", "baba"]

    assert try_move(world, 0, 1).moved
    assert ids_at(world, 4, 6) == ["baba"]
    assert ids_at(world, 4, 5) == ["portal", "rock"]
