import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ("baba", "wall", "box", "flag", "water", "fire", "rock", "door", "key", "portal")


def test_pixel_sprites_are_16x16():
    for name in SPRITES:
        data = (ROOT / "assets" / "sprites" / f"{name}.png").read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n", name
        width, height = struct.unpack(">II", data[16:24])
        assert (width, height) == (16, 16), name
