from pathlib import Path

import pygame

from rulebox.core.game import Game
from rulebox.core.level import load_level
from rulebox.ui.app import _handle_key

LEVEL = Path(__file__).resolve().parents[1] / "content" / "levels" / "01-first-step.txt"

MOVES = {
    pygame.K_UP: (-1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_RIGHT: (0, 1),
}


def new_game() -> Game:
    return Game(load_level(LEVEL))


def test_r_resets_after_move():
    game = new_game()
    game.move(0, 1)
    assert game.moves == 1

    assert _handle_key(game, pygame.K_r, "r", MOVES) is True
    assert game.moves == 0
    assert game.world.get(2, 3).id == "baba"


def test_z_undoes_move():
    game = new_game()
    game.move(0, 1)
    assert game.world.get(2, 4).id == "baba"

    assert _handle_key(game, pygame.K_z, "z", MOVES) is True
    assert game.moves == 0
    assert game.world.get(2, 3).id == "baba"


def test_escape_returns_false():
    game = new_game()
    assert _handle_key(game, pygame.K_ESCAPE, "\x1b", MOVES) is False


def test_uppercase_unicode_fallback():
    game = new_game()
    game.move(0, 1)

    # 某些键盘布局下 key 可能对不上，但 unicode 仍然是 R
    assert _handle_key(game, 0, "R", MOVES) is True
    assert game.moves == 0


def test_arrow_moves_baba():
    game = new_game()
    assert _handle_key(game, pygame.K_RIGHT, "", MOVES) is True
    assert game.world.get(2, 4).id == "baba"
