import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ("baba", "wall", "box", "flag", "water", "fire", "rock", "door", "key", "portal")


def test_pixel_sprites_have_expected_size():
    # 主角单独用 32×32（更修长、细节更多），其余物件保持 16×16。
    for name in SPRITES:
        data = (ROOT / "assets" / "sprites" / f"{name}.png").read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n", name
        width, height = struct.unpack(">II", data[16:24])
        expected = (32, 32) if name == "baba" else (16, 16)
        assert (width, height) == expected, name
