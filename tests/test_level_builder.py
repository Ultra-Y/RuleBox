from pathlib import Path

import pytest

from rulebox.core.level import load_level
from rulebox.core.level_builder import (
    PALETTE,
    blank_cells,
    build_level_text,
    save_level_text,
    share_decode,
    share_encode,
)


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
