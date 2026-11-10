"""规则句的扫描与解析。

支持：
    名词 (和 名词)* 是 属性 (和 属性)*
    名词 (和 名词)* 是 不 属性 (和 属性)*
    名词 (和 名词)* 是 名词              # 变形，Day 3 才真正生效
"""

from __future__ import annotations

from dataclasses import dataclass

from .entities import (
    ID_TO_PROP,
    NOUN_TO_OBJECT,
    NOUN_WORDS,
    OBJECT_TO_NOUN,
    PROP_TO_ID,
    PROPERTY_WORDS,
)
from .world import World


@dataclass(frozen=True)
class Rule:
    nouns: frozenset[str]  # 物件 id，如 {"wall"}
    props: frozenset[str] = frozenset()  # 属性 id，如 {"STOP"}
    transform: str | None = None  # 变形目标物件 id
    negated: frozenset[str] = frozenset()

    def display(self) -> str:
        """给规则面板显示用，例如「墙 是 停」。"""
        left = " 和 ".join(OBJECT_TO_NOUN[n] for n in sorted(self.nouns))
        if self.transform:
            return f"{left} 是 {OBJECT_TO_NOUN[self.transform]}"
        if self.negated:
            right = " 和 ".join(ID_TO_PROP[p] for p in sorted(self.negated))
            return f"{left} 是 不 {right}"
        right = " 和 ".join(ID_TO_PROP[p] for p in sorted(self.props))
        return f"{left} 是 {right}"


def parse_sentence(tokens: list[str]) -> Rule | None:
    """把一串连续词块解析成规则；不合法就返回 None。"""
    if len(tokens) < 3:
        return None

    i = 0
    if tokens[i] not in NOUN_WORDS:
        return None
    nouns = [NOUN_TO_OBJECT[tokens[i]]]
    i += 1

    while i < len(tokens) and tokens[i] == "和":
        i += 1
        if i >= len(tokens) or tokens[i] not in NOUN_WORDS:
            return None
        nouns.append(NOUN_TO_OBJECT[tokens[i]])
        i += 1

    if i >= len(tokens) or tokens[i] != "是":
        return None
    i += 1

    negated = False
    if i < len(tokens) and tokens[i] == "不":
        negated = True
        i += 1
        if i >= len(tokens):
            return None

    # 变形句：石 是 箱
    if not negated and tokens[i] in NOUN_WORDS:
        if i != len(tokens) - 1:
            return None
        return Rule(frozenset(nouns), transform=NOUN_TO_OBJECT[tokens[i]])

    props: list[str] = []
    while i < len(tokens):
        if tokens[i] not in PROPERTY_WORDS:
            return None
        props.append(PROP_TO_ID[tokens[i]])
        i += 1
        if i < len(tokens) and tokens[i] == "和":
            i += 1
            if i >= len(tokens):
                return None
            continue
        break

    if i != len(tokens) or not props:
        return None

    if negated:
        return Rule(frozenset(nouns), negated=frozenset(props))
    return Rule(frozenset(nouns), frozenset(props))


def parse_rules(world: World) -> list[Rule]:
    """扫描所有横向、纵向连续词块，返回生效的规则。"""
    rules: list[Rule] = []

    for row in range(world.height):
        col = 0
        while col < world.width:
            if _is_word(world, row, col):
                start = col
                while col < world.width and _is_word(world, row, col):
                    col += 1
                if col - start >= 3:
                    tokens = [_word_text(world, row, c) for c in range(start, col)]
                    rule = parse_sentence(tokens)
                    if rule:
                        rules.append(rule)
            else:
                col += 1

    for col in range(world.width):
        row = 0
        while row < world.height:
            if _is_word(world, row, col):
                start = row
                while row < world.height and _is_word(world, row, col):
                    row += 1
                if row - start >= 3:
                    tokens = [_word_text(world, r, col) for r in range(start, row)]
                    rule = parse_sentence(tokens)
                    if rule:
                        rules.append(rule)
            else:
                row += 1

    return rules


def property_map(rules: list[Rule]) -> dict[str, set[str]]:
    """把规则合并成「物件 -> 属性集合」。"""
    positive: dict[str, set[str]] = {}
    negative: dict[str, set[str]] = {}

    for rule in rules:
        if rule.transform:
            continue
        for noun in rule.nouns:
            if rule.props:
                positive.setdefault(noun, set()).update(rule.props)
            if rule.negated:
                negative.setdefault(noun, set()).update(rule.negated)

    for noun, negated in negative.items():
        if noun in positive:
            positive[noun] -= negated
    return positive


def transform_map(rules: list[Rule]) -> dict[str, str]:
    """变形规则：物件 -> 目标物件。"""
    mapping: dict[str, str] = {}
    for rule in rules:
        if rule.transform:
            for noun in rule.nouns:
                mapping[noun] = rule.transform
    return mapping


def _is_word(world: World, row: int, col: int) -> bool:
    return any(entity.is_word for entity in world.entities_at(row, col))


def _word_text(world: World, row: int, col: int) -> str:
    """返回格内词块文字；调用前已由 _is_word 确认词块存在。"""
    return next(entity.text for entity in world.entities_at(row, col) if entity.is_word)
