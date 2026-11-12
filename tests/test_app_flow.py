import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from rulebox.core.catalog import Progress, discover_levels
from rulebox.ui.app import _App, _handle_menu, _handle_official, _handle_select


def new_app(tmp_path) -> _App:
    pygame.init()
    pygame.font.init()
    entries = discover_levels()
    progress = Progress(tmp_path / "progress.json")
    return _App(entries, progress)


def test_menu_starts_first_level(tmp_path):
    app = new_app(tmp_path)
    app.screen = "menu"
    app.menu_index = 0

    assert _handle_menu(app, pygame.K_RETURN)
    assert app.screen == "play"
    assert app.level_index == 0
    assert app.game is not None


def test_select_screen_starts_selected_level(tmp_path):
    app = new_app(tmp_path)
    app.screen = "select"
    app.select_index = 1

    assert _handle_select(app, pygame.K_RETURN)
    assert app.level_index == 1
    assert app.game is not None
    assert app.game.level.name.startswith("02")


def test_official_category_flow(tmp_path):
    app = new_app(tmp_path)
    app.screen = "menu"
    app.menu_index = 1

    assert _handle_menu(app, pygame.K_RETURN)
    assert app.screen == "official"

    assert _handle_official(app, pygame.K_RETURN)
    assert app.screen == "select"
    assert app.select_mode == "tutorial"
    assert len(app.select_entries) == 10
    assert app.select_entries[0].display_name == "第一步"

    assert _handle_select(app, pygame.K_ESCAPE)
    assert app.screen == "official"

    app.official_index = 1
    assert _handle_official(app, pygame.K_RETURN)
    assert app.screen == "select"
    assert app.select_mode == "chapter1"
    assert [entry.display_name for entry in app.select_entries] == ["1-1", "1-2"]

    assert _handle_select(app, pygame.K_ESCAPE)
    assert app.screen == "official"
    app.official_index = 2
    assert _handle_official(app, pygame.K_RETURN)
    assert app.select_mode == "chapter2"
    assert [entry.display_name for entry in app.select_entries] == ["2-1", "2-2", "2-3"]


def test_win_then_next_level(tmp_path):
    app = new_app(tmp_path)
    app.start_index(0)
    assert app.game is not None

    for _ in range(3):
        app.game.move(0, 1)
    for _ in range(3):
        app.game.move(1, 0)
    for _ in range(3):
        app.game.move(0, 1)

    assert app.game.won
    app.mark_win()
    assert app.progress.is_completed(app.entries[0].id)

    app.next_level()
    assert app.level_index == 1
    assert app.game is not None
    assert app.game.level.name.startswith("02")
