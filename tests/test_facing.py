import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from rulebox.core.game import Game
from rulebox.core.level import load_level
from rulebox.ui.app import _handle_play, _move_game, _move_map

ROOT = Path(__file__).resolve().parents[1]
LEVEL = ROOT / "content" / "levels" / "01-first-step.txt"


class FakeApp:
    def __init__(self):
        self.game = Game(load_level(LEVEL))
        self.facing = "down"
        self.play_return = "menu"
        self.won = False

    def mark_win(self):
        self.won = True


def test_move_game_tracks_facing():
    app = FakeApp()

    _move_game(app, 0, -1)
    assert app.facing == "left"
    _move_game(app, 0, 1)
    assert app.facing == "right"
    _move_game(app, -1, 0)
    assert app.facing == "up"
    _move_game(app, 1, 0)
    assert app.facing == "down"


def test_play_key_updates_facing():
    import pygame

    app = FakeApp()
    moves = _move_map()

    _handle_play(app, pygame.K_LEFT, "", moves)
    assert app.facing == "left"
    _handle_play(app, pygame.K_UP, "", moves)
    assert app.facing == "up"


def test_reset_restores_front_facing():
    import pygame

    app = FakeApp()
    moves = _move_map()
    _handle_play(app, pygame.K_RIGHT, "", moves)
    assert app.facing == "right"

    _handle_play(app, pygame.K_r, "r", moves)
    assert app.facing == "down"
