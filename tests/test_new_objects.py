from rulebox.core.game import Game
from rulebox.core.level import parse_level
from rulebox.core.rules import parse_rules

LEVEL = """\
name 新物件测试
size 13 6
legend
  # wall
  . empty
  d dog
  c cat
  f flower
  X word 狗
  Z word 猫
  Q word 花
  2 word 是
  1 word 你
  7 word 推
  9 word 赢
  5 word 停
grid
  #############
  #X21.Z27.Q29#
  #...........#
  #.d.c...f...#
  #...........#
  #############
"""


def make_game(*, cat_rule: str = "Z27") -> Game:
    return Game(parse_level(LEVEL.replace("Z27", cat_rule)))


def find(game: Game, object_id: str) -> list[tuple[int, int]]:
    return [
        (row, col)
        for row, col, entity in game.world.find(lambda entity: entity.id == object_id)
    ]


def test_new_nouns_parse_and_behave():
    game = make_game()
    rules = {rule.display() for rule in parse_rules(game.world)}

    assert "狗 是 你" in rules
    assert "猫 是 推" in rules
    assert "花 是 赢" in rules


def test_dog_pushes_cat_then_wins_on_flower():
    game = make_game()
    assert find(game, "dog") == [(3, 2)]
    assert find(game, "cat") == [(3, 4)]
    assert find(game, "flower") == [(3, 8)]

    # 狗向右一步，把猫从 (3,4) 推到 (3,5)。
    assert game.move(0, 1).moved
    assert find(game, "dog") == [(3, 3)]
    assert find(game, "cat") == [(3, 4)]
    assert game.move(0, 1).moved
    assert find(game, "cat") == [(3, 5)]

    # 绕过猫，从下面走到花上。
    for direction in ((1, 0), (0, 1), (0, 1), (0, 1), (0, 1), (-1, 0)):
        game.move(*direction)
        if game.won:
            break
    assert game.won


def test_unruled_cat_is_background():
    game = make_game(cat_rule="Z2.")

    assert game.move(0, 1).moved
    assert game.move(0, 1).moved
    # 猫没有规则，是背景：狗和猫可以同格。
    assert find(game, "dog") == [(3, 4)]
    assert find(game, "cat") == [(3, 4)]


def test_cat_with_stop_blocks_dog():
    game = make_game(cat_rule="Z25")

    assert game.move(0, 1).moved
    assert not game.move(0, 1).moved
    assert find(game, "dog") == [(3, 3)]


LAVA = """\
name 岩浆测试
size 15 5
legend
  # wall
  . empty
  @ baba
  ~ water
  l lava
  1 word 人
  2 word 是
  3 word 你
  W word 水
  ] word 融
  L word 岩浆
  [ word 热
grid
  ###############
  #.123.W2].L2[.#
  #.............#
  #.@..l........#
  ###############
stack
  4 6 ~
"""


def lava_game(*, hot: bool = True) -> Game:
    text = LAVA if hot else LAVA.replace("L2[", "L2.")
    return Game(parse_level(text))


def test_lava_melts_water_with_hot_rule():
    game = lava_game(hot=True)

    # 水叠在岩浆上：一步移动后接触结算，水被融化，岩浆留下。
    game.move(0, 1)
    assert find(game, "water") == []
    assert find(game, "lava") == [(3, 5)]


def test_lava_without_hot_rule_keeps_water():
    game = lava_game(hot=False)

    game.move(0, 1)
    assert find(game, "water") == [(3, 5)]
    assert find(game, "lava") == [(3, 5)]


def test_lava_noun_parses_as_object():
    game = lava_game(hot=False)
    rules = {rule.display() for rule in parse_rules(game.world)}

    assert "水 是 融" in rules
    assert "人 是 你" in rules
    assert "岩浆 是 热" not in rules

