from pathlib import Path

import pytest

from rulebox.core.level import load_level
from rulebox.core.level_builder import (
    PALETTE,
    blank_cells,
    build_level_text,
    cells_from_text,
    safe_level_path,
    save_level_text,
    share_decode,
    share_encode,
)
from rulebox.ui.editor import Editor


def test_palette_symbols_are_unique():
    symbols = [item.symbol for item in PALETTE]
    assert len(symbols) == len(set(symbols))


def test_build_level_roundtrip(tmp_path):
    cells = blank_cells()
    cells[2][3] = "@"
    cells[2][7] = "F"
    cells[1][4] = "4"
    cells[1][5] = "2"
    cells[1][6] = "5"

    text = build_level_text("测试关", cells)
    path = tmp_path / "level.txt"
    path.write_text(text, encoding="utf-8")
    level = load_level(path)

    assert level.name == "测试关"
    assert (level.width, level.height) == (11, 8)
    assert level.entity_at(2, 3).id == "baba"
    assert level.entity_at(2, 7).id == "flag"
    assert level.entity_at(1, 4).text == "墙"


def test_share_code_roundtrip():
    text = build_level_text("分享关", blank_cells())
    code = share_encode(text)
    assert share_decode(code) == text


def test_share_code_rejects_garbage():
    with pytest.raises(ValueError):
        share_decode("not-a-real-code")


def test_save_level_text_is_unique(tmp_path):
    text = build_level_text("存档关", blank_cells())
    first = save_level_text(text, tmp_path)
    second = save_level_text(text, tmp_path)

    assert first != second
    assert first.exists() and second.exists()
    assert first.read_text(encoding="utf-8") == text


def test_build_rejects_tiny_grid():
    with pytest.raises(ValueError):
        build_level_text("小", [["#", "#"], ["#", "#"]])


def test_cells_from_text_roundtrip():
    cells = blank_cells()
    cells[2][3] = "@"
    cells[2][7] = "F"
    cells[1][4] = "4"
    text = build_level_text("回读", cells)

    name, read_cells = cells_from_text(text)

    assert name == "回读"
    assert read_cells[2][3] == "@"
    assert read_cells[2][7] == "F"
    assert read_cells[1][4] == "4"


def test_safe_level_path_avoids_overwrite(tmp_path):
    first = safe_level_path(tmp_path, "同名")
    first.write_text("x", encoding="utf-8")
    second = safe_level_path(tmp_path, "同名")

    assert first != second
    assert first.exists()


def test_editor_resize_and_build():
    editor = Editor()
    editor.resize(15, 12)

    assert (editor.width, editor.height) == (15, 12)
    text = editor.build_text()
    level = load_level_from_text(text)
    assert (level.width, level.height) == (15, 12)


def load_level_from_text(text: str):
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        path = handle.name
    try:
        return load_level(path)
    finally:
        Path(path).unlink(missing_ok=True)
