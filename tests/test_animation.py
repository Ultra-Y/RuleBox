import os
import struct
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from rulebox.core.entities import OBJECTS
from rulebox.ui.sprites import ANIMATIONS, animation_frame, sprite_for

ROOT = Path(__file__).resolve().parents[1]
SPRITE_DIR = ROOT / "assets" / "sprites"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path.name
    return struct.unpack(">II", data[16:24])


def test_every_animation_target_is_an_object():
    for object_id in ANIMATIONS:
        assert object_id in OBJECTS, object_id


def test_animated_objects_have_two_different_frames():
    for object_id in ANIMATIONS:
        first = SPRITE_DIR / f"{object_id}.png"
        second = SPRITE_DIR / f"{object_id}-1.png"
        assert first.exists(), f"缺少第一帧：{object_id}"
        assert second.exists(), f"缺少第二帧：{object_id}"
        expected = (32, 32) if object_id == "dog" else (16, 16)
        assert png_size(first) == expected
        assert png_size(second) == expected
        assert first.read_bytes() != second.read_bytes(), f"{object_id} 两帧一样"


def test_static_objects_have_no_second_frame():
    for object_id in OBJECTS:
        if object_id in ANIMATIONS:
            continue
        assert not (SPRITE_DIR / f"{object_id}-1.png").exists(), object_id


def test_animation_frame_follows_pattern():
    for object_id, (period, pattern) in ANIMATIONS.items():
        for step in range(len(pattern) * 2):
            assert animation_frame(object_id, step * period) == pattern[step % len(pattern)]
            assert animation_frame(object_id, step * period + period - 1) == pattern[
                step % len(pattern)
            ]


def test_animation_frames_exist_on_disk():
    for object_id, (_period, pattern) in ANIMATIONS.items():
        for frame in set(pattern):
            if frame == 0:
                path = SPRITE_DIR / f"{object_id}.png"
            else:
                path = SPRITE_DIR / f"{object_id}-{frame}.png"
            assert path.exists(), f"{object_id} 缺第 {frame} 帧"


def test_water_flows_through_four_frames():
    _period, pattern = ANIMATIONS["water"]

    assert set(pattern) == {0, 1, 2, 3}
    assert len(pattern) >= 4


def test_lava_has_multiple_frames():
    _period, pattern = ANIMATIONS["lava"]

    assert len(set(pattern)) >= 2


def test_static_objects_never_animate():
    for object_id in OBJECTS:
        if object_id in ANIMATIONS:
            continue
        assert animation_frame(object_id, 10_000) == 0, object_id


def test_animation_is_deterministic():
    for ticks in (0, 1, 999, 100_000):
        assert animation_frame("fire", ticks) == animation_frame("fire", ticks)


def test_baba_view_names():
    from rulebox.ui.sprites import baba_sprite_name

    assert baba_sprite_name("down") == "baba"
    assert baba_sprite_name("up") == "baba-up"
    assert baba_sprite_name("left") == "baba-side"
    assert baba_sprite_name("right") == "baba-side"
    assert baba_sprite_name("nonsense") == "baba"


def test_sprite_loading_supports_frames():
    import pygame

    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((64, 64))

    first = sprite_for("baba", 32, 0)
    second = sprite_for("baba", 32, 1)
    fallback = sprite_for("wall", 32, 1)  # 没有第二帧时回退第一帧

    assert first is not None and second is not None and fallback is not None
    assert first.get_size() == (32, 32)
    assert second.get_size() == (32, 32)


def test_animation_gif_demo_exists():
    data = (ROOT / "docs" / "sprites_anim.gif").read_bytes()

    assert data[:6] in (b"GIF87a", b"GIF89a")
    assert len(data) > 2000
