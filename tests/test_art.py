import os
import struct
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from rulebox.core.entities import NOUN_TO_OBJECT, OBJECTS

ROOT = Path(__file__).resolve().parents[1]
SPRITE_DIR = ROOT / "assets" / "sprites"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path.name
    return struct.unpack(">II", data[16:24])


def test_every_object_has_a_sprite():
    for object_id in OBJECTS:
        expected = (64, 64) if object_id == "baba" else (16, 16)
        path = SPRITE_DIR / f"{object_id}.png"
        assert path.exists(), f"缺少精灵：{object_id}"
        assert png_size(path) == expected, object_id


def test_baba_uses_higher_resolution():
    # 主角单独用 64×64，其他物件保持 16×16。
    assert png_size(SPRITE_DIR / "baba.png") == (64, 64)
    assert png_size(SPRITE_DIR / "baba-1.png") == (64, 64)


def test_baba_has_directional_views():
    # 正面 baba 之外，背面/侧面各有两帧。
    for name in ("baba-up", "baba-side"):
        first = SPRITE_DIR / f"{name}.png"
        second = SPRITE_DIR / f"{name}-1.png"
        assert png_size(first) == (64, 64), name
        assert png_size(second) == (64, 64), name
        assert first.read_bytes() != second.read_bytes(), name


def test_new_nouns_are_playable_objects():
    for noun, object_id in {
        "狗": "dog",
        "猫": "cat",
        "花": "flower",
        "树": "tree",
        "鱼": "fish",
        "岩浆": "lava",
    }.items():
        assert NOUN_TO_OBJECT[noun] == object_id
        assert object_id in OBJECTS
        assert OBJECTS[object_id][0] in noun


def test_sprite_sheet_covers_every_object():
    data = (ROOT / "docs" / "sprites.png").read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    rows = (len(OBJECTS) + 4) // 5
    # 5 列，每格 72px；精灵数量按行铺开。
    assert (width, height) == (5 * 72, rows * 72)


def test_liquid_tiles_cover_the_whole_cell():
    import pygame

    for object_id in ("water", "lava"):
        image = pygame.image.load(str(SPRITE_DIR / f"{object_id}.png"))
        assert image.get_size() == (16, 16), object_id
        for x in range(16):
            for y in range(16):
                assert image.get_at((x, y)).a == 255, f"{object_id} 在 ({x},{y}) 是透明的"

