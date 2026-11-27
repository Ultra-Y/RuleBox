import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from rulebox.core.game import Game
from rulebox.core.level import load_level, parse_level
from rulebox.ui.app import (
    FLOOR_A,
    FLOOR_B,
    _handle_play,
    _move_map,
    entity_rect,
    floor_color,
    liquid_open_sides,
)

ROOT = Path(__file__).resolve().parents[1]
LEVEL = ROOT / "content" / "levels" / "01-first-step.txt"


class FakeApp:
    def __init__(self):
        self.game = Game(load_level(LEVEL))
        self.facing = "down"
        self.play_return = "menu"
        self.show_grid = False
        self.won = False

    def mark_win(self):
        self.won = True


def test_floor_color_toggles_checkerboard():
    assert floor_color(0, 0, True) == FLOOR_A
    assert floor_color(0, 1, True) == FLOOR_B
    # 关掉网格后不再用深浅交替，整张地图一个底色。
    assert floor_color(0, 0, False) == FLOOR_A
    assert floor_color(0, 1, False) == FLOOR_A


def test_objects_use_inset_rect():
    for object_id in ("water", "lava", "wall", "dog", "baba"):
        entity = SimpleNamespace(kind="object", id=object_id)
        rect = entity_rect(40, 50, 60, entity)
        assert rect.width < 60 and rect.height < 60
        assert rect.x > 40 and rect.y > 50

    word = SimpleNamespace(kind="word", id="word")
    assert entity_rect(40, 50, 60, word).width < 60


def test_g_toggles_grid():
    import pygame

    app = FakeApp()
    moves = _move_map()
    assert app.show_grid is False

    _handle_play(app, pygame.K_g, "g", moves)
    assert app.show_grid is True

    _handle_play(app, pygame.K_g, "g", moves)
    assert app.show_grid is False


WATER_LEVEL = """\
name 水边
size 6 3
legend
  # wall
  . empty
  ~ water
  ^ fire
grid
  ######
  #~~^.#
  ######
"""


def test_liquid_open_sides_follow_neighbors():
    world = Game(parse_level(WATER_LEVEL)).world

    # (1,1)：右边是水，其余是墙/火 → 上/右/下/左 = 开/连/开/开
    assert liquid_open_sides(world, 1, 1, "water") == (True, False, True, True)
    # (1,2)：左边是水，右边是火
    assert liquid_open_sides(world, 1, 2, "water") == (True, True, True, False)
