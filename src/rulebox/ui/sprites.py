"""像素精灵的加载与绘制。没有素材时调用方回退到色块。"""

from __future__ import annotations

from pathlib import Path

from ..core.catalog import BUNDLE_ROOT

SPRITE_DIR = BUNDLE_ROOT / "assets" / "sprites"
_CACHE: dict[tuple[str, int], object | None] = {}


def sprite_for(object_id: str, size: int):
    """按物件 id 加载并缩放到 size×size；缺失或失败返回 None。"""
    import pygame

    key = (object_id, size)
    if key in _CACHE:
        return _CACHE[key]

    path = SPRITE_DIR / f"{object_id}.png"
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


def draw_object(screen, entity, rect) -> bool:
    """在 rect 内居中绘制物件精灵；词块或缺图返回 False。"""
    if entity is None or entity.is_word or entity.kind != "object":
        return False
    size = max(8, min(rect.width, rect.height))
    sprite = sprite_for(entity.id, size)
    if sprite is None:
        return False
    screen.blit(sprite, sprite.get_rect(center=rect.center))
    return True
