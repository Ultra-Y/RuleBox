from pathlib import Path

import pytest

from rulebox.core.entities import make_object
from rulebox.core.level import load_level
from rulebox.core.world import World

LEVEL = Path(__file__).resolve().parents[1] / "content" / "levels" / "01-first-step.txt"


def make_world() -> World:
    return World(load_level(LEVEL))


def test_get_and_set():
    world = make_world()
    assert world.get(2, 3).id == "baba"

    world.set(2, 3, None)
    assert world.get(2, 3) is None

    world.set(2, 3, make_object("box"))
    assert world.get(2, 3).id == "box"


def test_snapshot_undo():
    world = make_world()
    before = world.get(2, 3).id

    world.snapshot()
    world.set(2, 3, None)
    assert world.get(2, 3) is None

    assert world.undo() is True
    assert world.get(2, 3).id == before


def test_undo_without_history():
    world = make_world()
    assert world.undo() is False


def test_out_of_bounds():
    world = make_world()
    with pytest.raises(IndexError):
        world.get(-1, 0)
    with pytest.raises(IndexError):
        world.get(0, world.width)


def test_find_and_ascii():
    world = make_world()
    people = world.find(lambda entity: entity.id == "baba")
    assert len(people) == 1
    assert (people[0][0], people[0][1]) == (2, 3)

    text = world.to_ascii()
    assert "@" in text and "F" in text and "#" in text
