"""关卡 DSL 的解析。

格式示例见 content/levels/01-first-step.txt：
    name 01 第一步
    size 11 7
    legend
      # wall
      . empty
      @ baba
      人 word 人
    grid
      ###########
      ...
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .entities import Entity, make_object, make_word


class LevelFormatError(ValueError):
    """关卡文件格式错误，带行号，方便定位。"""

    def __init__(self, message: str, line_no: int | None = None, source: str = "<string>"):
        self.line_no = line_no
        self.source = source
        where = f"{source}:{line_no}" if line_no is not None else source
        super().__init__(f"{where}: {message}")


@dataclass
class Level:
    name: str
    width: int
    height: int
    cells: list[list[Entity | None]]

    def entity_at(self, row: int, col: int) -> Entity | None:
        if not (0 <= row < self.height and 0 <= col < self.width):
            raise IndexError(f"坐标越界：({row}, {col})")
        return self.cells[row][col]


def load_level(path: str | Path) -> Level:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    return parse_level(text, source=str(path))


def parse_level(text: str, source: str = "<string>") -> Level:
    name: str | None = None
    width: int | None = None
    height: int | None = None
    legend: dict[str, Entity | None] = {}
    grid_lines: list[tuple[int, str]] = []
    state = "header"

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue

        if state == "grid":
            grid_lines.append((line_no, line))
            continue

        if line.startswith("name "):
            name = line[5:].strip()
        elif line.startswith("size "):
            parts = line.split()
            if len(parts) != 3:
                raise LevelFormatError("size 需要两个整数，例如 `size 11 7`", line_no, source)
            try:
                width, height = int(parts[1]), int(parts[2])
            except ValueError as exc:
                raise LevelFormatError("size 的两个值必须是整数", line_no, source) from exc
        elif line == "legend":
            state = "legend"
        elif line == "grid":
            state = "grid"
        elif state == "legend":
            _parse_legend_line(line, line_no, source, legend)
        else:
            raise LevelFormatError(f"无法识别的行：{line}", line_no, source)

    if width is None or height is None:
        raise LevelFormatError("缺少 size 行", source=source)
    if not legend:
        raise LevelFormatError("缺少 legend 段", source=source)
    if len(grid_lines) != height:
        raise LevelFormatError(
            f"grid 应有 {height} 行，实际 {len(grid_lines)} 行", source=source
        )

    cells: list[list[Entity | None]] = []
    for line_no, row in grid_lines:
        if len(row) != width:
            raise LevelFormatError(
                f"该行宽度应为 {width}，实际 {len(row)}", line_no, source
            )
        cells.append([_cell_at(row[col], col, line_no, source, legend) for col in range(width)])

    return Level(name=name or "未命名关卡", width=width, height=height, cells=cells)


def _parse_legend_line(
    line: str, line_no: int, source: str, legend: dict[str, Entity | None]
) -> None:
    parts = line.split(None, 2)
    if len(parts) < 2:
        raise LevelFormatError("legend 行格式：`符号 类型`，例如 `# wall`", line_no, source)

    symbol, kind = parts[0], parts[1]
    if len(symbol) != 1:
        raise LevelFormatError(f"legend 的符号必须是单个字符：{symbol!r}", line_no, source)
    if symbol in legend:
        raise LevelFormatError(f"legend 符号重复：{symbol!r}", line_no, source)

    if kind == "empty":
        legend[symbol] = None
    elif kind == "word":
        if len(parts) < 3 or not parts[2].strip():
            raise LevelFormatError("word 类型要写出词，例如 `W word 墙`", line_no, source)
        try:
            legend[symbol] = make_word(parts[2].strip())
        except KeyError as exc:
            raise LevelFormatError(str(exc), line_no, source) from exc
    else:
        try:
            legend[symbol] = make_object(kind)
        except KeyError as exc:
            raise LevelFormatError(str(exc), line_no, source) from exc


def _cell_at(
    symbol: str,
    col: int,
    line_no: int,
    source: str,
    legend: dict[str, Entity | None],
) -> Entity | None:
    if symbol not in legend:
        raise LevelFormatError(
            f"符号 {symbol!r} 没有在 legend 中定义（第 {col + 1} 列）", line_no, source
        )
    return legend[symbol]
