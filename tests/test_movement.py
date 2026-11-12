from pathlib import Path

from rulebox.core.entities import make_object, make_word
from rulebox.core.game import Game
from rulebox.core.level import Level, load_level
from rulebox.core.movement import try_move
from rulebox.core.world import World

ROOT = Path(__file__).resolve().parents[1]
LEVEL1 = ROOT / "content" / "levels" / "01-first-step.txt"
LEVEL2 = ROOT / "content" / "levels" / "02-move-aside.txt"


def make_world(width=6, height=7, words=(), objects=()) -> World:
    cells: list[list] = [[None] * width for _ in range(height)]
    for row, col, text in words:
        cells[row][col] = make_word(text)
    for row, col, object_id in objects:
        cells[row][col] = make_object(object_id)
    return World(Level("test", width, height, cells))


def test_move_into_empty():
    game = Game(load_level(LEVEL1))
    result = game.move(0, 1)
    assert result.moved and not result.won
    assert game.world.get(2, 4).id == "baba"
    assert game.moves == 1


def test_wall_blocks():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "墙"),
            (1, 1, "是"),
            (1, 2, "停"),
        ],
        objects=[(4, 1, "baba"), (4, 0, "wall")],
    )

    result = try_move(world, 0, -1)
    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 0).id == "wall"
    assert not world.can_undo


def test_push_box():
    game = Game(load_level(LEVEL2))
    game.move(0, 1)
    game.move(0, 1)

    result = game.move(0, 1)
    assert result.moved
    assert game.world.get(4, 5).id == "baba"
    assert game.world.get(4, 6).id == "box"


def test_stop_and_push_object_is_pushable():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "箱"),
            (1, 1, "是"),
            (1, 2, "停"),
            (1, 3, "和"),
            (1, 4, "推"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "box")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 2).id == "baba"
    assert world.get(4, 3).id == "box"


def test_pushable_shut_door_is_pushed_like_other_objects():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "门"),
            (1, 1, "是"),
            (1, 2, "关"),
            (1, 3, "和"),
            (1, 4, "推"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "door")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 2).id == "baba"
    assert world.get(4, 3).id == "door"


def test_shut_door_without_push_still_blocks():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "门"),
            (1, 1, "是"),
            (1, 2, "关"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "door")],
    )

    result = try_move(world, 0, 1)
    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 2).id == "door"


def test_defeat_touch_loses():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "火"),
            (1, 1, "是"),
            (1, 2, "败"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "fire")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert result.lost
    assert not result.won


def test_you_with_win_wins_directly():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (0, 3, "和"),
            (0, 4, "赢"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "wall")],
    )

    result = try_move(world, 0, 1)
    assert result.moved and result.won
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 2).id == "wall"


def test_float_you_passes_nonfloat_wall():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "人"),
            (1, 1, "是"),
            (1, 2, "浮"),
            (2, 0, "墙"),
            (2, 1, "是"),
            (2, 2, "停"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "wall")],
    )

    result = try_move(world, 0, 1)
    assert result.moved and not result.lost
    assert {entity.id for entity in world.entities_at(4, 2)} == {"baba", "wall"}


def test_nonfloat_you_passes_float_wall():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "墙"),
            (1, 1, "是"),
            (1, 2, "停"),
            (1, 3, "和"),
            (1, 4, "浮"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "wall")],
    )

    result = try_move(world, 0, 1)
    assert result.moved and not result.lost
    assert {entity.id for entity in world.entities_at(4, 2)} == {"baba", "wall"}


def test_float_you_does_not_push_nonfloat_box():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "人"),
            (1, 1, "是"),
            (1, 2, "浮"),
            (2, 0, "箱"),
            (2, 1, "是"),
            (2, 2, "推"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "box")],
    )

    result = try_move(world, 0, 1)
    assert result.moved and not result.lost
    assert {entity.id for entity in world.entities_at(4, 2)} == {"baba", "box"}


def test_float_you_ignores_nonfloat_win():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "人"),
            (1, 1, "是"),
            (1, 2, "浮"),
            (2, 0, "旗"),
            (2, 1, "是"),
            (2, 2, "赢"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "flag")],
    )

    result = try_move(world, 0, 1)
    assert result.moved and not result.won and not result.lost


def test_float_you_wins_on_float_win():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "人"),
            (1, 1, "是"),
            (1, 2, "浮"),
            (2, 0, "旗"),
            (2, 1, "是"),
            (2, 2, "赢"),
            (2, 3, "和"),
            (2, 4, "浮"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "flag")],
    )

    result = try_move(world, 0, 1)
    assert result.won


def test_push_chain_blocked_by_wall():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "箱"),
            (1, 1, "是"),
            (1, 2, "推"),
            (2, 0, "墙"),
            (2, 1, "是"),
            (2, 2, "停"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "wall")],
    )
    result = try_move(world, 0, 1)
    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 2).id == "box"


def test_cannot_push_into_win():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "箱"),
            (1, 1, "是"),
            (1, 2, "推"),
            (2, 0, "旗"),
            (2, 1, "是"),
            (2, 2, "赢"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "flag")],
    )
    result = try_move(world, 0, 1)
    assert not result.moved
    assert world.get(4, 2).id == "box"


def test_word_is_pushable():
    world = make_world(
        words=[(0, 0, "人"), (0, 1, "是"), (0, 2, "你")],
        objects=[(4, 1, "baba")],
    )
    world.set(4, 2, make_word("墙"))
    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 2).id == "baba"
    assert world.get(4, 3).text == "墙"


def test_win_when_touching_flag():
    game = Game(load_level(LEVEL1))
    for _ in range(3):
        game.move(0, 1)
    for _ in range(3):
        game.move(1, 0)
    game.move(0, 1)
    game.move(0, 1)

    result = game.move(0, 1)
    assert result.won
    assert game.won


def test_level2_is_solvable():
    game = Game(load_level(LEVEL2))
    for _ in range(3):
        game.move(0, 1)  # 走到箱子左侧并把它推开
    for _ in range(2):
        game.move(1, 0)  # 从缺口下到最下面一行
    for _ in range(3):
        game.move(0, 1)
    result = game.move(0, 1)  # 最后一格是旗子

    assert result.won
    assert game.won


def test_undo_restores_position():
    game = Game(load_level(LEVEL1))
    game.move(0, 1)
    assert game.moves == 1

    assert game.undo() is True
    assert game.world.get(2, 3).id == "baba"
    assert game.moves == 0


def test_no_you_means_no_move():
    world = make_world(objects=[(4, 1, "baba")])
    result = try_move(world, 0, 1)
    assert not result.moved
    assert not world.can_undo


def test_you_can_pass_through_object_without_stop():
    world = make_world(
        words=[(0, 0, "人"), (0, 1, "是"), (0, 2, "你")],
        objects=[(4, 1, "baba"), (4, 2, "wall")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert [entity.id for entity in world.entities_at(4, 2)] == ["wall", "baba"]

    result = try_move(world, 0, 1)
    assert result.moved
    assert [entity.id for entity in world.entities_at(4, 2)] == ["wall"]
    assert world.get(4, 3).id == "baba"


def test_non_you_cannot_enter_occupied_cell():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "箱"),
            (1, 1, "是"),
            (1, 2, "推"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "box"), (4, 3, "rock")],
    )

    result = try_move(world, 0, 1)
    assert not result.moved
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 2).id == "box"
    assert world.get(4, 3).id == "rock"
    assert not world.can_undo


def test_undo_restores_overlapped_entities():
    world = make_world(
        words=[(0, 0, "人"), (0, 1, "是"), (0, 2, "你")],
        objects=[(4, 1, "baba"), (4, 2, "rock")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.undo() is True
    assert [entity.id for entity in world.entities_at(4, 1)] == ["baba"]
    assert [entity.id for entity in world.entities_at(4, 2)] == ["rock"]


def test_transform_after_move_and_words_unchanged():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "石"),
            (1, 1, "是"),
            (1, 2, "箱"),
        ],
        objects=[(4, 1, "baba"), (4, 4, "rock")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 4).id == "box"
    assert world.get(1, 0).is_word
    assert world.get(1, 0).text == "石"


def test_transform_preserves_overlap_order():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "石"),
            (1, 1, "是"),
            (1, 2, "箱"),
        ],
        objects=[(4, 1, "baba"), (4, 2, "rock")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert [entity.id for entity in world.entities_at(4, 2)] == ["box", "baba"]


def test_transformed_box_can_be_pushed():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "石"),
            (1, 1, "是"),
            (1, 2, "箱"),
            (2, 0, "箱"),
            (2, 1, "是"),
            (2, 2, "推"),
        ],
        objects=[(4, 1, "baba"), (4, 3, "rock")],
    )

    assert try_move(world, 0, 1).moved
    assert world.get(4, 3).id == "box"

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 3).id == "baba"
    assert world.get(4, 4).id == "box"


def test_failed_move_does_not_transform():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "石"),
            (1, 1, "是"),
            (1, 2, "箱"),
        ],
        objects=[(4, 0, "baba"), (4, 2, "rock")],
    )

    result = try_move(world, 0, -1)
    assert not result.moved
    assert world.get(4, 2).id == "rock"
    assert not world.can_undo


def test_undo_restores_transformed_entity():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "石"),
            (1, 1, "是"),
            (1, 2, "箱"),
        ],
        objects=[(4, 1, "baba"), (4, 4, "rock")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 4).id == "box"

    assert world.undo() is True
    assert world.get(4, 1).id == "baba"
    assert world.get(4, 4).id == "rock"


def test_transform_rules_apply_once():
    world = make_world(
        words=[
            (0, 0, "人"),
            (0, 1, "是"),
            (0, 2, "你"),
            (1, 0, "石"),
            (1, 1, "是"),
            (1, 2, "箱"),
            (2, 0, "箱"),
            (2, 1, "是"),
            (2, 2, "石"),
        ],
        objects=[(4, 0, "baba"), (4, 2, "rock"), (4, 4, "box")],
    )

    result = try_move(world, 0, 1)
    assert result.moved
    assert world.get(4, 2).id == "box"
    assert world.get(4, 4).id == "rock"
