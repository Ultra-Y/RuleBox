from pathlib import Path

import rulebox.ui.editor as editor_module
from rulebox.core.level_builder import PALETTE
from rulebox.ui.editor import (
    PALETTE_COLS,
    PALETTE_GAP,
    PALETTE_TILE,
    PALETTE_Y,
    Editor,
)


def test_palette_fits_editor_canvas():
    editor = Editor()
    last = editor._palette_rect(len(PALETTE) - 1)

    assert len(PALETTE) <= PALETTE_COLS * 4
    assert last.bottom <= 650, "调色板压到操作提示行"
    assert last.right < 590, "调色板压到右侧消息区"


def test_editor_save_rename_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(editor_module, "CUSTOM_DIR", tmp_path)
    monkeypatch.setattr(editor_module, "EXPORTS_DIR", tmp_path / "exports")

    editor = Editor()
    editor.name = "自制测试"
    editor.cells[2][3] = "@"
    editor.cells[2][7] = "F"
    editor.save()

    saved = editor.current_path
    assert saved is not None
    assert saved.exists()

    editor.name = "改名后"
    editor.rename()
    renamed = editor.current_path
    assert renamed is not None
    assert renamed.name == "改名后.txt"
    assert not saved.exists()
    assert renamed.exists()

    editor.delete()
    assert not renamed.exists()
    assert editor.current_path is None


def test_editor_playtest_calls_back(tmp_path, monkeypatch):
    monkeypatch.setattr(editor_module, "CUSTOM_DIR", tmp_path)
    seen: list[str] = []
    editor = Editor(on_playtest=lambda text: seen.append(text) or True)
    editor.cells[2][3] = "@"
    editor.cells[2][7] = "F"

    editor.playtest()

    assert len(seen) == 1
    assert "@" in seen[0]
    assert "F" in seen[0]


def test_editor_resize_starts_blank(tmp_path, monkeypatch):
    monkeypatch.setattr(editor_module, "CUSTOM_DIR", tmp_path)
    editor = Editor()
    editor.resize(6, 5)

    assert (editor.width, editor.height) == (6, 5)
    assert editor.cells[0][0] == "."
    assert editor.cells[-1][-1] == "."
    assert editor.cells[2][2] == "."


def test_editor_undo_redo():
    editor = Editor()
    editor.cells[2][3] = "@"
    editor.resize(15, 12)
    editor.clear()

    editor.undo()
    assert (editor.width, editor.height) == (15, 12)
    assert editor.cells[2][3] == "@"

    editor.undo()
    assert (editor.width, editor.height) == (11, 8)
    assert editor.cells[2][3] == "@"

    editor.redo()
    assert (editor.width, editor.height) == (15, 12)
