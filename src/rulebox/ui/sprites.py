"""像素精灵的加载与绘制。没有素材时调用方回退到色块。"""

from __future__ import annotations

from pathlib import Path

from ..core.catalog import BUNDLE_ROOT

SPRITE_DIR = BUNDLE_ROOT / "assets" / "sprites"
_CACHE: dict[tuple[str, int, int], object | None] = {}

# 待机动画：物件 -> (每帧毫秒, 帧序列)。序列可以重复帧，用来做“眨一下”这种短动作。
ANIMATIONS: dict[str, tuple[int, tuple[int, ...]]] = {
    "baba": (320, (0, 0, 0, 1)),
    "dog": (420, (0, 1)),
    "cat": (520, (0, 1)),
    "fish": (380, (0, 1)),
    "flower": (640, (0, 1)),
    "tree": (760, (0, 1)),
    "flag": (480, (0, 1)),
    "water": (180, (0, 1, 2, 3)),
    "fire": (200, (0, 1)),
    "portal": (700, (0, 1)),
    "lava": (420, (0, 1, 2)),
}


def animation_frame(object_id: str, ticks: int) -> int:
    """按毫秒时间取当前帧；不参与动画的物件永远是第 0 帧。"""
    animation = ANIMATIONS.get(object_id)
    if animation is None:
        return 0
    period, pattern = animation
    return pattern[(ticks // period) % len(pattern)]


def sprite_for(object_id: str, size: int, frame: int = 0):
    """按物件 id 加载并缩放到 size×size；缺失或失败返回 None。

    第 0 帧是 `<id>.png`，其余帧是 `<id>-<frame>.png`；缺帧时回退第 0 帧。
    """
    import pygame

    key = (object_id, size, frame)
    if key in _CACHE:
        return _CACHE[key]

    name = f"{object_id}.png" if frame == 0 else f"{object_id}-{frame}.png"
    path = SPRITE_DIR / name
    if not path.exists() and frame != 0:
        return sprite_for(object_id, size, 0)
    if not path.exists():
        _CACHE[key] = None
        return None

    try:
        image = pygame.image.load(str(path)).convert_alpha()
        image = pygame.transform.scale(image, (size, size))
    except pygame.error:
        _CACHE[key] = None
        return None

    _CACHE[key] = image
    return image


def draw_object(screen, entity, rect, frame: int = 0) -> bool:
    """在 rect 内居中绘制物件精灵；词块或缺图返回 False。"""
    if entity is None or entity.is_word or entity.kind != "object":
        return False
    size = max(8, min(rect.width, rect.height))
    sprite = sprite_for(entity.id, size, frame)
    if sprite is None:
        return False
    screen.blit(sprite, sprite.get_rect(center=rect.center))
    return True
