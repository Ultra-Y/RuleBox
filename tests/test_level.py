from pathlib import Path

import pytest

from rulebox.core.level import LevelFormatError, load_level, parse_level

LEVEL = Path(__file__).resolve().parents[1] / "content" / "levels" / "01-first-step.txt"
LEVEL3 = Path(__file__).resolve().parents[1] / "content" / "levels" / "03-blocked-road.txt"


def test_load_first_level():
    level = load_level(LEVEL)
    assert (level.width, level.height) == (11, 7)
    assert level.entity_at(2, 3).id == "baba"
    assert level.entity_at(5, 9).id == "flag"
    assert level.entity_at(0, 0).id == "wall"
    assert level.entity_at(1, 1) is None


def test_word_entity():
    level = load_level(LEVEL)
    person = level.entity_at(3, 7)
    assert person is not None
    assert person.is_word and person.text == "人"
    assert level.entity_at(3, 8).text == "是"
    assert level.entity_at(3, 9).text == "你"


def test_unknown_symbol():
    text = (
        "name bad\n"
        "size 3 3\n"
        "legend\n"
        "  # wall\n"
        "  . empty\n"
        "grid\n"
        "  ###\n"
        "  #?#\n"
        "  ###\n"
    )
    with pytest.raises(LevelFormatError) as exc:
        parse_level(text, source="bad.txt")
    assert "bad.txt" in str(exc.value)
    assert "?" in str(exc.value)


def test_wrong_width():
    text = (
        "name bad\n"
        "size 3 3\n"
        "legend\n"
        "  # wall\n"
        "  . empty\n"
        "grid\n"
        "  ##\n"
        "  ###\n"
        "  ###\n"
    )
    with pytest.raises(LevelFormatError):
        parse_level(text)


def test_missing_size():
    text = "name bad\nlegend\n  # wall\ngrid\n  #\n"
    with pytest.raises(LevelFormatError):
        parse_level(text)


def test_blocked_road_level_layout():
    level = load_level(LEVEL3)
    assert (level.width, level.height) == (11, 8)
    assert level.entity_at(4, 2).id == "baba"
    assert level.entity_at(4, 5) is None
    assert level.entity_at(5, 5).id == "box"
    assert level.entity_at(6, 9).id == "flag"
