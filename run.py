"""RuleBox 启动器：把 src 放进 sys.path，免得先装包。"""

import os
import pathlib
import sys

# 让 Windows 终端里的中文正常显示（PowerShell 7 默认按 UTF-8 读）
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

# 隐藏 pygame 的启动横幅
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rulebox.ui.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
