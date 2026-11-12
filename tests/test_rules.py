from rulebox.core.entities import make_object, make_word
from rulebox.core.level import Level
from rulebox.core.resolve import you_positions
from rulebox.core.rules import (
    active_word_positions,
    blocked_transform_word_positions,
    effective_rules,
    locked_nouns,
    parse_rules,
    parse_sentence,
    property_map,
    transform_map,
)
from rulebox.core.world import World


def make_world(width=9, height=7, words=(), objects=()) -> World:
    cells: list[list] = [[None] * width for _ in range(height)]
    for row, col, text in words:
        cells[row][col] = make_word(text)
    for row, col, object_id in objects:
        cells[row][col] = make_object(object_id)
    return World(Level("test", width, height, cells))


def test_horizontal_rule():
    world = make_world(words=[(1, 1, "墙"), (1, 2, "是"), (1, 3, "停")])
    rules = parse_rules(world)
    assert len(rules) == 1
    assert rules[0].nouns == frozenset({"wall"})
    assert rules[0].props == frozenset({"STOP"})
    assert rules[0].display() == "墙 是 停"


def test_vertical_rule():
    world = make_world(words=[(1, 3, "人"), (2, 3, "是"), (3, 3, "你")])
    rules = parse_rules(world)
    assert len(rules) == 1
    assert rules[0].nouns == frozenset({"baba"})
    assert rules[0].props == frozenset({"YOU"})


def test_and_nouns():
    world = make_world(
        words=[(1, 1, "墙"), (1, 2, "和"), (1, 3, "箱"), (1, 4, "是"), (1, 5, "停")]
    )
    rules = parse_rules(world)
    assert len(rules) == 1
    assert rules[0].nouns == frozenset({"wall", "box"})
    assert rules[0].props == frozenset({"STOP"})


def test_and_properties():
    world = make_world(
        words=[(1, 1, "人"), (1, 2, "是"), (1, 3, "你"), (1, 4, "和"), (1, 5, "推")]
    )
    rules = parse_rules(world)
    assert len(rules) == 1
    assert rules[0].props == frozenset({"YOU", "PUSH"})


def test_not_property():
    world = make_world(
        words=[(1, 1, "墙"), (1, 2, "是"), (1, 3, "不"), (1, 4, "停")]
    )
    rules = parse_rules(world)
    assert len(rules) == 1
    assert rules[0].props == frozenset()
    assert rules[0].negated == frozenset({"STOP"})


def test_transform():
    world = make_world(words=[(1, 1, "石"), (1, 2, "是"), (1, 3, "箱")])
    rules = parse_rules(world)
    assert len(rules) == 1
    assert rules[0].transform == "box"


def test_self_rule_locks_transform():
    world = make_world(
        width=12,
        height=5,
        words=[
            (1, 1, "旗"),
            (1, 2, "是"),
            (1, 3, "旗"),
            (3, 1, "旗"),
            (3, 2, "是"),
            (3, 3, "人"),
        ],
    )
    rules = parse_rules(world)

    assert len(rules) == 2
    assert locked_nouns(rules) == {"flag"}
    assert transform_map(rules) == {"flag": "flag"}
    assert len(effective_rules(rules)) == 1
    assert blocked_transform_word_positions(world) == {(3, 1)}
    assert active_word_positions(world) == {(1, 1), (1, 2), (1, 3)}


def test_self_rule_does_not_block_properties():
    world = make_world(
        words=[
            (1, 1, "旗"),
            (1, 2, "是"),
            (1, 3, "旗"),
            (3, 1, "旗"),
            (3, 2, "是"),
            (3, 3, "赢"),
        ]
    )
    rules = parse_rules(world)

    assert property_map(rules)["flag"] == {"WIN"}
    assert transform_map(rules) == {"flag": "flag"}
    assert len(effective_rules(rules)) == 2


def test_overlapping_transform_and_property_sentences():
    world = make_world(
        words=[
            (1, 1, "旗"),
            (1, 2, "是"),
            (1, 3, "箱"),
            (1, 4, "是"),
            (1, 5, "开"),
        ]
    )
    rules = parse_rules(world)

    assert {rule.display() for rule in rules} == {"旗 是 箱", "箱 是 开"}
    assert transform_map(rules) == {"flag": "box"}
    assert property_map(rules)["box"] == {"OPEN"}
    assert active_word_positions(world) == {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)}


def test_suffix_sentence_after_extra_noun():
    world = make_world(words=[(1, 1, "人"), (1, 2, "旗"), (1, 3, "是"), (1, 4, "开")])
    rules = parse_rules(world)

    assert [rule.display() for rule in rules] == ["旗 是 开"]
    assert active_word_positions(world) == {(1, 2), (1, 3), (1, 4)}


def test_prefix_sentence_before_trailing_word():
    world = make_world(words=[(1, 1, "旗"), (1, 2, "是"), (1, 3, "开"), (1, 4, "关")])
    rules = parse_rules(world)

    assert [rule.display() for rule in rules] == ["旗 是 开"]
    assert property_map(rules)["flag"] == {"OPEN"}
    assert active_word_positions(world) == {(1, 1), (1, 2), (1, 3)}


def test_incomplete_sentence_ignored():
    assert parse_sentence(["墙", "是"]) is None
    assert parse_sentence(["墙", "是", "你", "和"]) is None
    world = make_world(words=[(1, 1, "墙"), (1, 2, "是")])
    assert parse_rules(world) == []


def test_negation_cancels_positive():
    world = make_world(
        words=[
            (1, 1, "墙"),
            (1, 2, "是"),
            (1, 3, "停"),
            (2, 1, "墙"),
            (2, 2, "是"),
            (2, 3, "不"),
            (2, 4, "停"),
        ]
    )
    props = property_map(parse_rules(world))
    assert "STOP" not in props.get("wall", set())


def test_you_positions():
    world = make_world(
        words=[(0, 1, "人"), (0, 2, "是"), (0, 3, "你")],
        objects=[(4, 4, "baba")],
    )
    props = property_map(parse_rules(world))
    assert you_positions(world, props) == [(4, 4)]


def test_adjacent_sentences_in_one_row():
    world = make_world(
        words=[
            (1, 1, "墙"),
            (1, 2, "是"),
            (1, 3, "停"),
            (1, 4, "人"),
            (1, 5, "是"),
            (1, 6, "你"),
        ]
    )
    rules = parse_rules(world)
    assert len(rules) == 2
    assert {rule.display() for rule in rules} == {"墙 是 停", "人 是 你"}


def test_adjacent_sentences_in_one_column():
    world = make_world(
        words=[
            (1, 1, "墙"),
            (2, 1, "是"),
            (3, 1, "停"),
            (4, 1, "人"),
            (5, 1, "是"),
            (6, 1, "你"),
        ]
    )
    rules = parse_rules(world)
    assert len(rules) == 2
    assert {rule.display() for rule in rules} == {"墙 是 停", "人 是 你"}


def test_active_word_positions_marks_rule_tiles():
    world = make_world(
        words=[(1, 1, "墙"), (1, 2, "是"), (1, 3, "停"), (1, 5, "人")]
    )
    assert active_word_positions(world) == {(1, 1), (1, 2), (1, 3)}


def test_active_word_positions_marks_adjacent_sentences():
    world = make_world(
        words=[
            (1, 1, "墙"),
            (1, 2, "是"),
            (1, 3, "停"),
            (1, 4, "人"),
            (1, 5, "是"),
            (1, 6, "你"),
        ]
    )
    assert active_word_positions(world) == {
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
    }


def test_active_word_positions_vertical():
    world = make_world(
        words=[(1, 1, "墙"), (2, 1, "是"), (3, 1, "停"), (5, 1, "人")]
    )
    assert active_word_positions(world) == {(1, 1), (2, 1), (3, 1)}


def test_active_word_positions_empty_for_incomplete():
    world = make_world(words=[(1, 1, "墙"), (1, 2, "是")])
    assert active_word_positions(world) == set()


def test_you_positions_scans_overlapped_entities():
    world = make_world(objects=[(4, 4, "rock")])
    world.add(4, 4, make_object("baba"))
    props = {"baba": {"YOU"}}
    assert you_positions(world, props) == [(4, 4)]
