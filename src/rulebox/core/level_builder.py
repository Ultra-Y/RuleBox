"""关卡编辑用的调色板、DSL 生成与分享码。"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .level import parse_level


@dataclass(frozen=True)
class PaletteItem:
    symbol: str
    kind: str  # empty | object | word
    value: str
    label: str


_OBJECTS = [
    ("#", "wall", "墙"),
    (".", "empty", "空"),
    ("@", "baba", "人"),
    ("$", "box", "箱"),
    ("F", "flag", "旗"),
    ("~", "water", "水"),
    ("^", "fire", "火"),
    ("o", "rock", "石"),
    ("D", "door", "门"),
    ("K", "key", "钥"),
    ("P", "portal", "传"),
]

_WORDS = [
    ("1", "人", "人"),
    ("2", "是", "是"),
    ("3", "你", "你"),
    ("4", "墙", "墙"),
    ("5", "停", "停"),
    ("6", "箱", "箱"),
    ("7", "推", "推"),
    ("8", "旗", "旗"),
    ("9", "赢", "赢"),
    ("0", "传送", "传送"),
    ("+", "和", "和"),
    ("-", "不", "不"),
    ("=", "浮", "浮"),
    ("[", "热", "热"),
    ("]", "融", "融"),
    ("(", "开", "开"),
    (")", "关", "关"),
    ("|", "传", "传"),
    ("!", "败", "败"),
]

PALETTE: list[PaletteItem] = [
    PaletteItem(symbol, "empty" if value == "empty" else "object", value, label)
    for symbol, value, label in _OBJECTS
] + [PaletteItem(symbol, "word", value, label) for symbol, value, label in _WORDS]

BY_SYMBOL = {item.symbol: item for item in PALETTE}


def blank_cells(width: int = 11, height: int = 8) -> list[list[str]]:
    cells = [["." for _ in range(width)] for _ in range(height)]
    for col in range(width):
        cells[0][col] = "#"
        cells[height - 1][col] = "#"
    for row in range(height):
        cells[row][0] = "#"
        cells[row][width - 1] = "#"
    return cells


def build_level_text(name: str, cells: list[list[str]]) -> str:
    name = (name or "自制关卡").replace("\n", " ").strip() or "自制关卡"
    height = len(cells)
    width = len(cells[0]) if height else 0
    if width < 3 or height < 3:
        raise ValueError("关卡至少 3×3")

    lines = [f"name {name}", f"size {width} {height}", "", "legend"]
    for item in PALETTE:
        if item.kind == "empty":
            lines.append(f"  {item.symbol} empty")
        elif item.kind == "word":
            lines.append(f"  {item.symbol} word {item.value}")
        else:
            lines.append(f"  {item.symbol} {item.value}")

    lines.extend(["", "grid"])
    for row in cells:
        if len(row) != width:
            raise ValueError("每行宽度必须一致")
        lines.append(f"  {''.join(row)}")
    return "\n".join(lines) + "\n"


def share_encode(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")


def share_decode(code: str) -> str:
    cleaned = "".join((code or "").split())
    if not cleaned:
        raise ValueError("分享码是空的")
    try:
        raw = base64.urlsafe_b64decode(cleaned + "=" * (-len(cleaned) % 4))
        text = raw.decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError) as exc:
        raise ValueError("分享码无法解码") from exc
    parse_level(text, source="<share-code>")
    return text


def save_level_text(text: str, directory: Path, prefix: str = "custom") -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = directory / f"{prefix}-{stamp}.txt"
    index = 2
    while path.exists():
        path = directory / f"{prefix}-{stamp}-{index}.txt"
        index += 1
    path.write_text(text, encoding="utf-8")
    return path
