import struct
from pathlib import Path

from rulebox.core.entities import NOUN_TO_OBJECT, OBJECTS

ROOT = Path(__file__).resolve().parents[1]
SPRITE_DIR = ROOT / "assets" / "sprites"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path.name
    return struct.unpack(">II", data[16:24])


def test_every_object_has_a_16x16_sprite():
    for object_id in OBJECTS:
        path = SPRITE_DIR / f"{object_id}.png"
        assert path.exists(), f"缺少精灵：{object_id}"
        assert png_size(path) == (16, 16), object_id


def test_new_nouns_are_playable_objects():
    for noun, object_id in {
        "狗": "dog",
        "猫": "cat",
        "花": "flower",
        "树": "tree",
        "鱼": "fish",
    }.items():
        assert NOUN_TO_OBJECT[noun] == object_id
        assert object_id in OBJECTS
        assert OBJECTS[object_id][0] == noun


def test_sprite_sheet_covers_every_object():
    data = (ROOT / "docs" / "sprites.png").read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    # 5 列 × 3 行，每格 72px；15 个物件刚好放满。
    assert (width, height) == (5 * 72, 3 * 72)
