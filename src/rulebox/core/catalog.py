"""关卡目录与通关进度。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .level import load_level

ROOT = Path(__file__).resolve().parents[3]
LEVELS_DIR = ROOT / "content" / "levels"
PROGRESS_PATH = ROOT / "progress.json"


@dataclass(frozen=True)
class LevelEntry:
    path: Path
    number: str
    name: str

    @property
    def id(self) -> str:
        return self.path.stem

    @property
    def title(self) -> str:
        return f"{self.number} {self.name}"


def discover_levels(levels_dir: Path = LEVELS_DIR) -> list[LevelEntry]:
    """按文件名排序读取关卡，编号取文件名第一段。"""
    entries: list[LevelEntry] = []
    for path in sorted(levels_dir.glob("*.txt")):
        level = load_level(path)
        number = path.stem.split("-", 1)[0]
        entries.append(LevelEntry(path=path, number=number, name=level.name))
    return entries


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
        if not progress.is_completed(entry.id):
            return index
    return 0
