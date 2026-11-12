"""普通水、浮层、热/融的接触结算。"""

import pygame

from rulebox.core.entities import make_object, make_word
from rulebox.core.game import Game
from rulebox.core.level import Level
from rulebox.core.movement import try_move
from rulebox.core.world import World
from rulebox.ui.app import _handle_key

MOVES = {
    pygame.K_UP: (-1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_RIGHT: (0, 1),
}


def rule(row: int, noun: str, prop: str) -> list[tuple[int, int, str]]:
    """把「名词 是 属性」放在第 row 行的前三格。"""
    return [(row, 0, noun), (row, 1, "是"), (row, 2, prop)]


def make_level(words=(), objects=(), width=8, height=6) -> Level:
    cells: list[list] = [[None] * width for _ in range(height)]
    for row, col, text in words:
        cells[row][col] = make_word(text)
    for row, col, object_id in objects:
        cells[row][col] = make_object(object_id)
    return Level("hazards", width, height, cells)


def make_world(words=(), objects=(), width=8, height=6) -> World:
    return World(make_level(words, objects, width, height))


def ids_at(world: World, row: int, col: int) -> list[str]:
    return [entity.id for entity in world.entities_at(row, col)]


# ---------- 水是普通物件 ----------


def test_water_is_plain_object():
    world = make_world(words=rule(0, "人", "你"), objects=[(4, 1, "baba"), (4, 2, "water")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert set(ids_at(world, 4, 2)) == {"water", "baba"}


def test_float_you_overlaps_water():
    words = rule(0, "人", "你") + rule(1, "人", "浮")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert set(ids_at(world, 4, 2)) == {"water", "baba"}


def test_float_object_leaves_water_intact():
    words = rule(0, "人", "你") + rule(1, "人", "浮")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])

    assert try_move(world, 0, 1).moved
    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 3).id == "baba"
    assert ids_at(world, 4, 2) == ["water"]


def test_water_can_be_pushed_by_rule():
    words = rule(0, "人", "你") + rule(1, "水", "推")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 2).id == "baba"
    assert ids_at(world, 4, 3) == ["water"]


def test_water_can_be_stopped_by_rule():
    words = rule(0, "人", "你") + rule(1, "水", "停")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])

    result = try_move(world, 0, 1)

    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert ids_at(world, 4, 2) == ["water"]


def test_water_can_be_melted_by_rule():
    words = rule(0, "人", "你") + rule(1, "火", "热") + rule(2, "水", "融")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])
    world.add(4, 2, make_object("fire"))

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert set(ids_at(world, 4, 2)) == {"fire", "baba"}


def test_word_pushed_into_water_is_blocked():
    words = rule(0, "人", "你") + [(4, 2, "墙")]
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 3, "water")])

    result = try_move(world, 0, 1)

    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert ids_at(world, 4, 2) == ["word:墙"]
    assert ids_at(world, 4, 3) == ["water"]


def test_stop_still_blocks_water_cell():
    words = rule(0, "人", "你") + rule(1, "墙", "停")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "wall")])
    world.add(4, 2, make_object("water"))

    result = try_move(world, 0, 1)

    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert not world.can_undo


# ---------- 沉 ----------


def test_sink_object_cancels_you():
    words = rule(0, "人", "你") + rule(1, "水", "沉")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == []


def test_sink_object_cancels_word_block():
    words = rule(0, "人", "你") + rule(1, "水", "沉")
    world = make_world(words=words, objects=[(4, 1, "baba")])
    world.set(4, 3, make_word("墙"))
    world.add(4, 3, make_object("water"))

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 3) == []
    assert world.get(4, 2).id == "baba"


def test_sink_object_alone_stays():
    words = rule(0, "人", "你") + rule(1, "水", "沉")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 3, "water")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 3) == ["water"]


def test_sink_cancels_across_float_layer():
    words = rule(0, "人", "你") + rule(1, "人", "浮") + rule(2, "水", "沉")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "water")])

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == []


# ---------- 失败、撤销、重置 ----------


DEFEAT_RULES = rule(0, "人", "你") + rule(1, "火", "败")


def test_game_tracks_defeat_and_reset_clears_it():
    game = Game(make_level(words=DEFEAT_RULES, objects=[(4, 1, "baba"), (4, 2, "fire")]))

    assert game.move(0, 1).lost
    assert game.lost and game.moves == 1

    assert not game.move(0, 1).moved
    assert set(ids_at(game.world, 4, 2)) == {"fire", "baba"}
    assert game.moves == 1

    game.reset()
    assert not game.lost
    assert game.moves == 0
    assert game.world.get(4, 1).id == "baba"


def test_undo_restores_defeated_you():
    world = make_world(words=DEFEAT_RULES, objects=[(4, 1, "baba"), (4, 2, "fire")])

    assert try_move(world, 0, 1).lost
    assert world.undo() is True
    assert world.get(4, 1).id == "baba"
    assert ids_at(world, 4, 2) == ["fire"]


def test_key_handler_blocks_moves_after_loss():
    game = Game(make_level(words=DEFEAT_RULES, objects=[(4, 1, "baba"), (4, 2, "fire")]))

    assert game.move(0, 1).lost

    assert _handle_key(game, pygame.K_RIGHT, "", MOVES) is True
    assert game.moves == 1
    assert set(ids_at(game.world, 4, 2)) == {"fire", "baba"}

    assert _handle_key(game, pygame.K_z, "z", MOVES) is True
    assert not game.lost
    assert game.moves == 0
    assert game.world.get(4, 1).id == "baba"

    assert game.move(0, 1).lost
    assert _handle_key(game, pygame.K_r, "r", MOVES) is True
    assert not game.lost
    assert game.world.get(4, 1).id == "baba"


# ---------- 热 / 融 ----------


MELT_BOX_PUSH = rule(0, "人", "你") + rule(1, "箱", "推") + rule(2, "火", "热") + rule(3, "箱", "融")


def test_fire_melts_pushed_box():
    world = make_world(
        words=MELT_BOX_PUSH,
        objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "fire")],
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 2).id == "baba"
    assert ids_at(world, 4, 3) == ["fire"]


def test_undo_restores_melted_box():
    world = make_world(
        words=MELT_BOX_PUSH,
        objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "fire")],
    )

    assert try_move(world, 0, 1).moved
    assert world.undo() is True
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 2).id == "box"
    assert world.get(4, 3).id == "fire"


def test_non_hazard_and_water_still_block_push():
    words = rule(0, "人", "你") + rule(1, "箱", "推")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "rock")])
    world.add(4, 3, make_object("water"))

    result = try_move(world, 0, 1)

    assert not result.moved
    assert world.get(4, 2).id == "box"
    assert ids_at(world, 4, 3) == ["rock", "water"]
    assert not world.can_undo


def test_fire_melts_you():
    words = rule(0, "人", "你") + rule(1, "人", "融") + rule(2, "火", "热")
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "fire")])

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert ids_at(world, 4, 2) == ["fire"]

    assert world.undo() is True
    assert world.get(4, 1).id == "baba"


def test_word_pushed_into_fire_survives():
    words = rule(0, "人", "你") + rule(1, "火", "热") + rule(2, "箱", "融") + [(4, 2, "箱")]
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 3, "fire")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert world.get(4, 2).id == "baba"
    assert ids_at(world, 4, 3) == ["fire", "word:箱"]


def test_hot_and_melt_object_does_not_self_destroy():
    words = (
        rule(0, "人", "你")
        + rule(1, "人", "热")
        + rule(2, "人", "融")
        + rule(3, "火", "热")
    )
    world = make_world(words=words, objects=[(4, 1, "baba"), (4, 2, "fire")])

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["fire", "baba"]


# ---------- 变形后的胜负判定 ----------


def test_transform_creates_new_you_prevents_loss():
    words = (
        rule(0, "人", "你")
        + rule(1, "石", "人")
        + rule(2, "人", "融")
        + rule(3, "火", "热")
    )
    world = make_world(
        words=words,
        objects=[(4, 1, "baba"), (4, 2, "fire"), (4, 3, "rock")],
    )

    result = try_move(world, 0, 1)

    assert result.moved and not result.lost
    assert ids_at(world, 4, 2) == ["fire"]
    assert world.get(4, 3).id == "baba"


def test_transform_removes_last_you_causes_loss():
    words = rule(0, "人", "你") + rule(1, "人", "石")
    world = make_world(words=words, objects=[(4, 1, "baba")])

    result = try_move(world, 0, 1)

    assert result.moved and result.lost
    assert world.get(4, 2).id == "rock"
