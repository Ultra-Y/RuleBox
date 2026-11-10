"""物件与词块的数据定义。

这里只描述"有什么"，不描述"能做什么"。
行为（推、停、赢……）由后续的 rules / resolve 模块实现。
"""

from __future__ import annotations

from dataclasses import dataclass

Color = tuple[int, int, int]

# 物件定义：id -> (显示文字, 颜色)
OBJECTS: dict[str, tuple[str, Color]] = {
    "baba": ("人", (245, 205, 120)),
    "wall": ("墙", (92, 96, 120)),
    "box": ("箱", (205, 145, 80)),
    "flag": ("旗", (110, 200, 130)),
    "water": ("水", (70, 130, 220)),
    "fire": ("火", (230, 90, 60)),
    "rock": ("石", (145, 145, 150)),
    "door": ("门", (160, 105, 65)),
    "key": ("钥", (235, 200, 90)),
    "portal": ("传", (150, 100, 220)),
}

NOUN_WORDS = frozenset({"人", "墙", "箱", "旗", "水", "火", "石", "门", "钥", "传送"})
CONNECTOR_WORDS = frozenset({"是", "和", "不"})
PROPERTY_WORDS = frozenset(
    {"你", "推", "停", "赢", "浮", "热", "融", "开", "关", "传", "败"}
)
ALL_WORDS = NOUN_WORDS | CONNECTOR_WORDS | PROPERTY_WORDS

_WORD_COLORS: dict[str, Color] = {
    **{word: (86, 132, 214) for word in NOUN_WORDS},
    **{word: (220, 220, 228) for word in CONNECTOR_WORDS},
    **{word: (232, 150, 76) for word in PROPERTY_WORDS},
}


@dataclass(frozen=True)
class Entity:
    """网格里的一个物件或一块词。

    id 对物件是 "wall" 这类标识，对词是 "word:墙"。
    """

    id: str
    kind: str  # "object" | "word"
    text: str
    color: Color

    @property
    def is_word(self) -> bool:
        return self.kind == "word"


def make_object(object_id: str) -> Entity:
    if object_id not in OBJECTS:
        raise KeyError(f"未知物件：{object_id}")
    text, color = OBJECTS[object_id]
    return Entity(id=object_id, kind="object", text=text, color=color)


def make_word(text: str) -> Entity:
    if text not in ALL_WORDS:
        raise KeyError(f"未知词：{text}")
    return Entity(id=f"word:{text}", kind="word", text=text, color=_WORD_COLORS[text])
