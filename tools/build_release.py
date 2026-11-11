"""打 Windows 免安装包：dist/RuleBox/RuleBox.exe + zip。

    .\.venv\Scripts\python.exe tools\build_release.py

需要 PyInstaller：pip install pyinstaller
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP_NAME = "RuleBox"
STALE_DIRS = ("RuleBox-Windows", "RuleBox-test", "package-test", "extracted")


def clean_dir(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
        print(f"清理旧解压目录：{path}")


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("缺少 PyInstaller：pip install pyinstaller")
        return 1

    for name in STALE_DIRS:
        clean_dir(DIST / name)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
        "--paths",
        str(ROOT / "src"),
        "--add-data",
        f"{ROOT / 'assets'}{os.pathsep}assets",
        "--add-data",
        f"{ROOT / 'content'}{os.pathsep}content",
        "--distpath",
        str(DIST),
        "--workpath",
        str(ROOT / "build" / "pyinstaller"),
        "--specpath",
        str(ROOT / "build"),
        str(ROOT / "run.py"),
    ]
    print("building:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode

    app_dir = DIST / APP_NAME
    if not (app_dir / f"{APP_NAME}.exe").exists():
        print("找不到生成的 exe：", app_dir)
        return 1

    play_doc = ROOT / "docs" / "HOW-TO-PLAY.txt"
    if play_doc.exists():
        shutil.copy2(play_doc, app_dir / "HOW-TO-PLAY.txt")
    (app_dir / "custom_levels").mkdir(exist_ok=True)

    zip_path = DIST / f"{APP_NAME}-Windows.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(app_dir.rglob("*")):
            if path.is_file():
                archive.write(path, Path(APP_NAME) / path.relative_to(app_dir))
    print(f"\n压缩包：{zip_path}（{zip_path.stat().st_size / 1024 / 1024:.1f} MB）")
    shutil.rmtree(app_dir, ignore_errors=True)
    print(f"已清理构建目录：{app_dir}")
    print("dist/ 只保留最新 zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
