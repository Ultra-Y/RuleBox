#!/usr/bin/env python3
"""把 Qoder CN CLI 当子 agent 调用：非交互跑一个任务，返回结果并留档。

用法：
    .\.venv\Scripts\python.exe tools\qoder_agent.py --prompt "读 AGENTS.md，总结当前状态" \
        --permission-mode dont_ask --allowed-tools "Read,Grep,Glob"
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ("default", "accept_edits", "auto", "dont_ask", "bypass_permissions")

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def find_cli() -> str:
    for name in ("qoderclicn", "qodercn"):
        path = shutil.which(name)
        if path and path.lower().endswith(".exe"):
            return path
    candidate = Path.home() / ".qoder-cn" / "bin" / "qoderclicn" / "qoderclicn.exe"
    if candidate.exists():
        return str(candidate)
    raise SystemExit(
        "找不到 qoderclicn.exe。先安装："
        "irm https://static.qoder.com.cn/qoder-cli-cn/install.ps1 | iex"
    )


def parse_result(raw: str) -> dict | None:
    for line in reversed(raw.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "result" in obj:
            return obj
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="用 Qoder CN CLI 跑一次非交互任务")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--workspace", default=str(ROOT))
    parser.add_argument("--permission-mode", default="auto", choices=MODES)
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--model", default="")
    parser.add_argument("--allowed-tools", default="")
    parser.add_argument("--out-dir", default="docs/agent-runs")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir():
        print(f"工作区不存在：{workspace}", file=sys.stderr)
        return 2

    cli = find_cli()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = workspace / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"{stamp}.raw.log"
    result_path = out_dir / f"{stamp}.result.md"

    cmd = [
        cli,
        "-w",
        str(workspace),
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        args.permission_mode,
        "--max-turns",
        str(args.max_turns),
    ]
    if args.model:
        cmd += ["-m", args.model]
    if args.allowed_tools:
        cmd += ["--allowed-tools", args.allowed_tools]
    cmd.append(args.prompt)

    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    raw = proc.stdout or ""
    if proc.stderr:
        raw += ("\n" if raw and not raw.endswith("\n") else "") + proc.stderr
    raw_path.write_text(raw, encoding="utf-8")

    obj = parse_result(raw)
    if obj is None:
        print(raw, file=sys.stderr)
        print(f"无法解析 Qoder CN 输出，原始日志：{raw_path}", file=sys.stderr)
        return 2

    result = str(obj.get("result", ""))
    meta = (
        f"turns={obj.get('num_turns')} credits={obj.get('total_credits')} "
        f"session={obj.get('session_id')} error={obj.get('is_error')}"
    )
    result_path.write_text(
        f"# Qoder CN run {stamp}\n\n"
        f"- workspace: `{workspace}`\n"
        f"- permission: `{args.permission_mode}`\n"
        f"- {meta}\n\n"
        f"## Result\n\n{result}\n",
        encoding="utf-8",
    )

    print(result)
    print(meta, file=sys.stderr)
    print(f"raw: {raw_path}", file=sys.stderr)
    print(f"result: {result_path}", file=sys.stderr)
    return 1 if obj.get("is_error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
