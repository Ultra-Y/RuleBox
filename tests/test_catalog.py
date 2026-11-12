from pathlib import Path

from rulebox.core.catalog import (
    LevelEntry,
    Progress,
    discover_levels,
    first_unfinished,
    next_index,
    next_official_number,
)


def write_level(directory: Path, stem: str, name: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    text = (
        f"name {name}\n"
        "size 3 3\n"
        "legend\n"
        "  . empty\n"
        "grid\n"
        "  ...\n"
        "  ...\n"
        "  ...\n"
    )
    (directory / f"{stem}.txt").write_text(text, encoding="utf-8")


def test_discover_levels_sorted(tmp_path):
    write_level(tmp_path, "02-b", "第二关")
    write_level(tmp_path, "01-a", "第一关")
    write_level(tmp_path, "10-c", "第十关")

    entries = discover_levels(tmp_path)

    assert [entry.number for entry in entries] == ["01", "02", "10"]
    assert [entry.name for entry in entries] == ["第一关", "第二关", "第十关"]
    assert entries[0].title == "01 第一关"


def test_progress_roundtrip(tmp_path):
    path = tmp_path / "progress.json"
    progress = Progress(path)
    progress.mark("01-a")

    again = Progress(path)
    assert again.is_completed("01-a")
    assert not again.is_completed("02-b")


def test_progress_tolerates_missing_or_bad_file(tmp_path):
    missing = Progress(tmp_path / "nope.json")
    assert missing.completed == set()

    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert Progress(bad).completed == set()


def test_display_name_strips_number():
    entry = LevelEntry(Path("01-a.txt"), "01", "01 第一步")
    assert entry.display_name == "第一步"
    assert entry.title == "01 01 第一步"
    numbered = LevelEntry(Path("main-1-1.txt"), "main", "1-1")
    assert numbered.display_name == "1-1"


def test_custom_level_key_is_prefixed(tmp_path):
    write_level(tmp_path, "my-level", "我的关卡")
    entries = discover_levels(tmp_path, source="custom")

    assert len(entries) == 1
    assert entries[0].key == "custom:my-level"
    assert entries[0].display_name == "我的关卡"


def test_level_categories():
    tutorial = LevelEntry(Path("01-a.txt"), "01", "01 第一步")
    main = LevelEntry(Path("main-1-1.txt"), "main", "1-1")
    custom = LevelEntry(Path("我的.txt"), "我的", "我的", source="custom")

    assert tutorial.category == "tutorial"
    assert main.category == "main"
    assert custom.category == "custom"
    assert main.chapter == 1
    chapter2 = LevelEntry(Path("main-2-1.txt"), "main", "2-1")
    assert chapter2.chapter == 2


def test_next_official_number(tmp_path):
    write_level(tmp_path, "01-a", "第一关")
    write_level(tmp_path, "03-c", "第三关")
    assert next_official_number(tmp_path) == 4
    assert next_official_number(tmp_path / "empty") == 1


def test_first_unfinished_and_next():
    entries = [
        LevelEntry(Path("01.txt"), "01", "一"),
        LevelEntry(Path("02.txt"), "02", "二"),
        LevelEntry(Path("03.txt"), "03", "三"),
    ]
    progress = Progress(Path("unused.json"))
    progress.completed = {"01", "02"}

    assert first_unfinished(entries, progress) == 2
    assert next_index(entries, 0) == 1
    assert next_index(entries, 2) is None
    assert next_index(entries, -1) is None
