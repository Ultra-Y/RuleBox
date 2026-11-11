"""生成 RuleBox 的 16×16 像素精灵。

需要 Pillow；素材已经提交到 assets/sprites/，运行时不需要 Pillow。
    python tools/generate_sprites.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITE_DIR = ROOT / "assets" / "sprites"
DOCS = ROOT / "docs"

PALETTES = {
    "baba": {
        "o": (60, 45, 35, 255),
        "b": (245, 200, 110, 255),
        "l": (255, 235, 170, 255),
        "e": (30, 30, 40, 255),
        "m": (150, 90, 70, 255),
    },
    "wall": {
        "o": (40, 42, 56, 255),
        "b": (92, 96, 120, 255),
        "l": (110, 116, 140, 255),
        "m": (65, 68, 88, 255),
    },
    "box": {
        "o": (70, 45, 25, 255),
        "b": (205, 145, 80, 255),
        "l": (230, 180, 110, 255),
        "d": (150, 95, 50, 255),
    },
    "flag": {
        "o": (40, 40, 50, 255),
        "p": (180, 180, 190, 255),
        "g": (80, 190, 110, 255),
        "l": (140, 230, 160, 255),
    },
    "water": {
        "b": (50, 110, 200, 255),
        "l": (90, 160, 235, 255),
        "w": (190, 225, 255, 255),
    },
    "fire": {
        "o": (90, 30, 20, 255),
        "r": (220, 70, 40, 255),
        "y": (255, 200, 70, 255),
        "w": (255, 245, 200, 255),
    },
    "rock": {
        "o": (50, 50, 55, 255),
        "b": (120, 120, 130, 255),
        "l": (165, 165, 175, 255),
    },
    "door": {
        "o": (60, 35, 20, 255),
        "b": (140, 85, 45, 255),
        "d": (110, 65, 35, 255),
        "l": (180, 120, 70, 255),
        "k": (240, 200, 80, 255),
    },
    "key": {
        "o": (90, 65, 20, 255),
        "k": (240, 200, 80, 255),
        "l": (255, 230, 140, 255),
    },
    "portal": {
        "o": (55, 30, 80, 255),
        "p": (140, 80, 210, 255),
        "l": (200, 150, 245, 255),
    },
}

SPRITES = {
    "baba": [
        "................",
        "................",
        ".....oooooo.....",
        "....obbbbbbo....",
        "...obllllllbo...",
        "...obebbebbbo...",
        "...obbbbbbbbo...",
        "...obbmbbbbbo...",
        "....obbbbbbo....",
        ".....oooooo.....",
        "....obbbbbbo....",
        "...obbbbbbbbo...",
        "...obbbbbbbbo...",
        "...obbbbbbbbo...",
        "....obbbbbbo....",
        ".....oooooo.....",
    ],
    "wall": [
        "oooooooooooooooo",
        "obbbbbbbbbbbbbbo",
        "obllllllllllllbo",
        "obbbbbbbbbbbbbbo",
        "ommmmmmmmmmmmmmo",
        "obbbbbbbbbbbbbbo",
        "obbbbbbbbbbbbbbo",
        "obbbbbbbbbbbbbbo",
        "ommmmmmmmmmmmmmo",
        "obbbbbbbbbbbbbbo",
        "obbbbbbbbbbbbbbo",
        "obbbbbbbbbbbbbbo",
        "ommmmmmmmmmmmmmo",
        "obbbbbbbbbbbbbbo",
        "obbbbbbbbbbbbbbo",
        "oooooooooooooooo",
    ],
    "box": [
        "................",
        "..oooooooooooo..",
        "..obbbbbbbbbbo..",
        "..obllllllllbo..",
        "..oblddddddlbo..",
        "..obldbbbbdlbo..",
        "..obldbbbbdlbo..",
        "..oblddddddlbo..",
        "..obllllllllbo..",
        "..oooooooooooo..",
        "..obbbbbbbbbbo..",
        "..obllllllllbo..",
        "..oblddddddlbo..",
        "..obllllllllbo..",
        "..oooooooooooo..",
        "................",
    ],
    "flag": [
        "................",
        "...oo...........",
        "...opooooooo....",
        "...opgggggggo...",
        "...opgggggggo...",
        "...opggggggo....",
        "...opgggggo.....",
        "...opgggo.......",
        "...opggo........",
        "...opo..........",
        "...op...........",
        "...op...........",
        "...op...........",
        "...op...........",
        "..oooo..........",
        "................",
    ],
    "water": [
        "................",
        "................",
        "................",
        "................",
        "..llllllllllll..",
        "..bbbbbbbbbbbb..",
        "..bbbbbbbbbbbb..",
        "..wwwwwwwwwwww..",
        "..bbbbbbbbbbbb..",
        "..bbbbbbbbbbbb..",
        "..llllllllllll..",
        "..bbbbbbbbbbbb..",
        "..bbbbbbbbbbbb..",
        "..wwwwwwwwwwww..",
        "................",
        "................",
    ],
    "fire": [
        "................",
        ".......oo.......",
        "......orro......",
        ".....orrrro.....",
        "....orrrooro....",
        "....orroyyoro...",
        "...oroyyyyoro...",
        "...oroywwyoro...",
        "...oroyyyyoro...",
        "....oroyyoro....",
        "....orrrrrro....",
        ".....orrrro.....",
        "......oooo......",
        "................",
        "................",
        "................",
    ],
    "rock": [
        "................",
        "................",
        ".....oooo.......",
        "....obbbbo......",
        "...obllbbbo.....",
        "..obllbbbbbo....",
        "..obbbbbbbbo....",
        ".obbbbbbbbbbo...",
        ".obbbbbbbbbbo...",
        "..obbbbbbbbo....",
        "...obbbbbbo.....",
        "....oooooo......",
        "................",
        "................",
        "................",
        "................",
    ],
    "door": [
        "................",
        "...oooooooooo...",
        "...obbbbbbbbo...",
        "...obddddddbo...",
        "...obdlllldbo...",
        "...obdlllldbo...",
        "...obddddddbo...",
        "...obbbbbbbbo...",
        "...obddddddbo...",
        "...obdlllldbo...",
        "...obdlllldkbo..",
        "...obddddddbo...",
        "...obbbbbbbbo...",
        "...obbbbbbbbo...",
        "...oobbbbbboo...",
        "....oooooooo....",
    ],
    "key": [
        "................",
        "................",
        "......oooo......",
        ".....okkkko.....",
        ".....okllko.....",
        "......oooo......",
        ".......oo.......",
        ".......oo.......",
        ".......oo.......",
        "....ooooooo.....",
        "...okkkkkkko....",
        "...oklkkkkko....",
        "...okkkkkkko....",
        "....ooooooo.....",
        "................",
        "................",
    ],
    "portal": [
        "................",
        ".....oooooo.....",
        "....oppppppo....",
        "...oppllllppo...",
        "..oppllllllppo..",
        "..oppllllllppo..",
        "..oppllllllppo..",
        "..oppllllllppo..",
        "..oppllllllppo..",
        "..oppllllllppo..",
        "...oppllllppo...",
        "....oppppppo....",
        ".....oooooo.....",
        "................",
        "................",
        "................",
    ],
}


def main() -> None:
    SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    for name, rows in SPRITES.items():
        if len(rows) != 16 or any(len(row) != 16 for row in rows):
            bad = [index for index, row in enumerate(rows) if len(row) != 16]
            raise SystemExit(f"{name} 尺寸不是 16×16，问题行：{bad}")
        palette = PALETTES[name]
        image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        pixels = image.load()
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char != ".":
                    pixels[x, y] = palette[char]
        image.save(SPRITE_DIR / f"{name}.png")

    sheet = Image.new("RGBA", (5 * 72, 2 * 72), (24, 26, 34, 255))
    for index, name in enumerate(SPRITES):
        sprite = Image.open(SPRITE_DIR / f"{name}.png").resize((64, 64), Image.NEAREST)
        x = (index % 5) * 72 + 4
        y = (index // 5) * 72 + 4
        sheet.alpha_composite(sprite, (x, y))
    sheet.save(DOCS / "sprites.png")
    print("generated", len(SPRITES), "sprites")


if __name__ == "__main__":
    main()
