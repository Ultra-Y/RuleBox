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
    if i >= len(tokens):
        return None

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


def parse_run_spans(tokens: list[str]) -> list[tuple[int, int, Rule]]:
    """把一段连续词块切成句子，并返回每句在 tokens 中的区间。

    相邻的两句（例如「墙 是 停 人 是 你」）不再互相破坏：
    整段解析失败时，退回按前缀切分，取句子数最多的切法。
    """
    total = len(tokens)
    memo: dict[int, list[tuple[int, int, Rule]] | None] = {}

    def solve(start: int) -> list[tuple[int, int, Rule]] | None:
        if start == total:
            return []
        if start in memo:
            return memo[start]

        best: list[tuple[int, int, Rule]] | None = None
        for end in range(start + 3, total + 1):
            rule = parse_sentence(tokens[start:end])
            if rule is None:
                continue
            rest = solve(end)
            if rest is None:
                continue
            candidate = [(start, end, rule), *rest]
            if best is None or len(candidate) > len(best):
                best = candidate

        memo[start] = best
        return best

    return solve(0) or []


def parse_run(tokens: list[str]) -> list[Rule]:
    return [rule for _start, _end, rule in parse_run_spans(tokens)]


def _word_runs(world: World):
    """产出 (行, 列, 行方向, 列方向, 词序列) 的所有词块长串。"""
    for row in range(world.height):
        col = 0
        while col < world.width:
            if _is_word(world, row, col):
                start = col
                while col < world.width and _is_word(world, row, col):
                    col += 1
                if col - start >= 3:
                    tokens = [_word_text(world, row, c) for c in range(start, col)]
                    yield row, start, 0, 1, tokens
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
                    yield start, col, 1, 0, tokens
            else:
                row += 1


def _scan_run_spans(tokens: list[str]) -> list[tuple[int, int, Rule]]:
    """扫描一段词块里所有合法子句；长句优先，允许子句重叠。

    例如「旗 是 箱 是 开」会同时得到「旗 是 箱」和「箱 是 开」；
    「人 旗 是 开」只取后缀「旗 是 开」；
    「旗 是 开 关」只取前缀「旗 是 开」。
    """
    candidates: list[tuple[int, int, Rule]] = []
    total = len(tokens)
    for start in range(total):
        for end in range(start + 3, total + 1):
            rule = parse_sentence(tokens[start:end])
            if rule is not None:
                candidates.append((start, end, rule))

    # 只保留不被其他合法句包含的候选，避免「人 是 你 和 推」再拆出「人 是 你」。
    kept: list[tuple[int, int, Rule]] = []
    for index, (start, end, rule) in enumerate(candidates):
        contained = any(
            other_index != index
            and other_start <= start
            and end <= other_end
            and (other_start < start or end < other_end)
            for other_index, (other_start, other_end, _other_rule) in enumerate(candidates)
        )
        if not contained:
            kept.append((start, end, rule))
    kept.sort(key=lambda item: (item[0], item[1]))
    return kept


def _rule_spans(world: World):
    """产出 (行, 列, 行方向, 列方向, 开始, 结束, 规则)。"""
    for row, col, dr, dc, tokens in _word_runs(world):
        for start, end, rule in _scan_run_spans(tokens):
            yield row, col, dr, dc, start, end, rule


def parse_rules(world: World) -> list[Rule]:
    """扫描所有横向、纵向连续词块，返回语法有效的规则。"""
    rules = [span[-1] for span in _rule_spans(world)]
    return list(dict.fromkeys(rules))


def locked_nouns(rules: list[Rule]) -> set[str]:
    """自指规则 A 是 A 会锁定 A 的变形。"""
    return {
        noun
        for rule in rules
        if rule.transform
        for noun in rule.nouns
        if rule.transform == noun
    }


def is_blocked_transform(rule: Rule, locked: set[str]) -> bool:
    """被自指规则锁住的非自身变形句。"""
    if not rule.transform:
        return False
    return any(noun in locked and noun != rule.transform for noun in rule.nouns)


def effective_rules(rules: list[Rule]) -> list[Rule]:
    """去掉被锁住、实际不生效的变形句。"""
    locked = locked_nouns(rules)
    return [rule for rule in rules if not is_blocked_transform(rule, locked)]


def active_word_positions(world: World) -> set[tuple[int, int]]:
    """返回被生效句子使用的词块坐标；被拒绝的变形句不算。"""
    spans = list(_rule_spans(world))
    rules = list(dict.fromkeys(span[-1] for span in spans))
    locked = locked_nouns(rules)
    active: set[tuple[int, int]] = set()
    for row, col, dr, dc, start, end, rule in spans:
        if is_blocked_transform(rule, locked):
            continue
        for offset in range(start, end):
            active.add((row + dr * offset, col + dc * offset))
    return active


def blocked_transform_word_positions(world: World) -> set[tuple[int, int]]:
    """返回被拒绝变形句的主语词块坐标，用于画叉。"""
    spans = list(_rule_spans(world))
    rules = list(dict.fromkeys(span[-1] for span in spans))
    locked = locked_nouns(rules)
    marks: set[tuple[int, int]] = set()
    for row, col, dr, dc, start, _end, rule in spans:
        if is_blocked_transform(rule, locked):
            marks.add((row + dr * start, col + dc * start))
    return marks


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
    """变形规则：物件 -> 目标物件；被自指规则锁住的变形不生效。"""
    mapping: dict[str, str] = {}
    locked = locked_nouns(rules)
    for rule in rules:
        if not rule.transform or is_blocked_transform(rule, locked):
            continue
        for noun in rule.nouns:
            mapping[noun] = rule.transform
    return mapping


def _is_word(world: World, row: int, col: int) -> bool:
    return any(entity.is_word for entity in world.entities_at(row, col))


def _word_text(world: World, row: int, col: int) -> str:
    """返回格内词块文字；调用前已由 _is_word 确认词块存在。"""
    return next(entity.text for entity in world.entities_at(row, col) if entity.is_word)
