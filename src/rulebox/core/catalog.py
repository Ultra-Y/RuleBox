"""关卡目录与通关进度。"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .level import load_level

IS_FROZEN = bool(getattr(sys, "frozen", False))
BUNDLE_ROOT = (
    Path(sys._MEIPASS)
    if IS_FROZEN and hasattr(sys, "_MEIPASS")
    else Path(__file__).resolve().parents[3]
)
USER_ROOT = Path(sys.executable).resolve().parent if IS_FROZEN else BUNDLE_ROOT

ROOT = USER_ROOT
OFFICIAL_DIR = BUNDLE_ROOT / "content" / "levels"
CUSTOM_DIR = USER_ROOT / "custom_levels"
LEVELS_DIR = OFFICIAL_DIR
PROGRESS_PATH = USER_ROOT / "progress.json"


@dataclass(frozen=True)
class LevelEntry:
    path: Path
    number: str
    name: str
    source: str = "official"

    @property
    def key(self) -> str:
        stem = self.path.stem
        return stem if self.source == "official" else f"custom:{stem}"

    @property
    def id(self) -> str:
        return self.key

    @property
    def display_name(self) -> str:
        """去掉关卡名前面的编号，只留标题。"""
        return re.sub(r"^\s*\d+\s+", "", self.name).strip() or self.name

    @property
    def title(self) -> str:
        return f"{self.number} {self.name}"


def discover_levels(
    levels_dir: Path = OFFICIAL_DIR, source: str = "official"
) -> list[LevelEntry]:
    """按文件名排序读取关卡，编号取文件名第一段。"""
    entries: list[LevelEntry] = []
    for path in sorted(Path(levels_dir).glob("*.txt")):
        level = load_level(path)
        number = path.stem.split("-", 1)[0]
        entries.append(
            LevelEntry(path=path, number=number, name=level.name, source=source)
        )
    return entries


def discover_custom() -> list[LevelEntry]:
    return discover_levels(CUSTOM_DIR, source="custom")


def next_official_number(levels_dir: Path = OFFICIAL_DIR) -> int:
    """下一个官方关卡编号：取现有数字前缀的最大值 + 1。"""
    numbers: list[int] = []
    for path in Path(levels_dir).glob("*.txt"):
        token = path.stem.split("-", 1)[0]
        if token.isdigit():
            numbers.append(int(token))
    return max(numbers, default=0) + 1


class Progress:
    def __init__(self, path: Path = PROGRESS_PATH):
        self.path = Path(path)
        self.completed: set[str] = set()
        self.load()

    def load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if isinstance(data, dict):
            completed = data.get("completed", [])
            if isinstance(completed, list):
                self.completed = {str(item) for item in completed}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"completed": sorted(self.completed)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def mark(self, level_id: str) -> None:
        self.completed.add(level_id)
        self.save()

    def is_completed(self, level_id: str) -> bool:
        return level_id in self.completed


def next_index(entries: list[LevelEntry], index: int) -> int | None:
    if 0 <= index < len(entries) - 1:
        return index + 1
    return None


def first_unfinished(entries: list[LevelEntry], progress: Progress) -> int:
    for index, entry in enumerate(entries):
        if not progress.is_completed(entry.key):
            return index
    return 0
