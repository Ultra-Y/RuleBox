# AGENTS.md

> 给接手本仓库的 AI 编程代理。先读本文件，再读 `docs/HANDOFF.md`，然后跑测试。

## 项目

RuleBox：中文词块推箱解谜。墙、箱子、旗子的行为由场上可推动的词块决定（受《Baba Is You》启发）。
目标：12 关、可玩、可测、能讲清设计。

## 接手后先做三件事

1. 读 `docs/HANDOFF.md`：当前状态、下一步、设计债、网络注意事项。
2. 跑测试，确认基线（期望 `107 passed`）：

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q
   ```

3. 跑一次游戏，确认能启动：

   ```powershell
   .\.venv\Scripts\python.exe run.py
   ```

## 环境（Windows）

- **不要用 PATH 里的 `python`**：它是 MSYS2 的，没有 pip。
- 用 `.venv\Scripts\python.exe`：Python 3.10.6。
- 重建环境：

  ```powershell
  py -3.10 -m venv .venv
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

- 版本：pygame 2.6.1、pytest 9.2.0。

## 架构约束

- `src/rulebox/core/` **禁止 import pygame**，必须能在无显示器环境跑测试。
- `ui/` 只通过 `core/game.py` 的 `Game` 驱动，不直接改 `World`。
- 关卡放在 `content/levels/*.txt`，不要把地图写进代码。
- `rules.py` 只做规则解析；`movement.py` 做移动/推链；`resolve.py` 做属性查询与接触结算。
- 每次操作前 `world.snapshot()`；失败的移动必须回滚，且不留下快照。
- 新行为必须带 pytest；修 bug 先写会失败的测试。

## 当前状态（2026-11-10）

- 最新提交以 `git log` 为准。
- Day 1–2 完成：关卡 DSL、移动、推箱、推词、规则解析、胜负、撤销、重开、键盘修复。
- 5.1 完成：没有「停 / 赢 / 推」的普通物件可与「你」重叠；离开后仍保留，撤销可恢复所有层。
- 5.2 完成：变形 `A 是 B` 在移动结算后统一生效；词块不参与；同一回合按开始时身份只变一次。
- 5.3 完成：水/浮、热/融、开/关、传全部结算；失去所有「你」判负，UI 显示失败遮罩。
- 交互完成：开始菜单、选关、通关进度、过关下一关；规则句支持相邻两句（横/竖），每关显式「墙 是 停」。
- 关卡：第 3 关《路被堵住了？》已加入（第 2 关地图，箱子下移一格）。
- 编辑器：5×5–20×20、调色板、试玩、打开、保存、重命名、删除、分享码；官方关卡在 `content/levels/`，自制关卡在 `custom_levels/`，菜单分开。
- 美术：10 个 16×16 像素精灵在 `assets/sprites/`；`ui/sprites.py` 加载，缺图回退色块。
- 107 条测试全过；第 1–3 关可玩。
- 当前真正生效：`你 / 推 / 停 / 赢`、变形、`浮 / 热 / 融 / 开 / 关 / 传`。

## 下一步

见 `docs/HANDOFF.md` 第 5 节。优先级：

1. 继续加第 4–8 关 + 每关解法回放测试。
2. 编辑器再加撤销/重做、把自制关卡一键转为官方关卡。
3. 提示系统、`validate.py` 关卡校验器、最佳步数。

## 不要做的事

- 不要重写 UI、不要换框架、不要引入第三方游戏引擎。
- 不要把 `.venv`、`.idea`、`progress.json` 提交进仓库。
- 不要复制《Baba Is You》的关卡、美术或代码。
- 不要在没跑测试的情况下改动移动/规则代码。
- 不要把 PAT、密码、个人邮箱写进任何文件。

## 提交约定

- 前缀：`feat:`、`fix:`、`test:`、`docs:`、`chore:`。
- 中文说明，一个提交只做一件事。
- 改完先跑 `pytest`，再提交。

## 用 Qoder CN 当子 agent（可选）

本机已安装 Qoder CN CLI（`qodercn`），可以用 `tools/qoder_agent.py` 非交互调用：

```powershell
.\.venv\Scripts\python.exe tools\qoder_agent.py `
  --prompt "只读任务：..." `
  --permission-mode dont_ask `
  --allowed-tools "Read,Grep,Glob"
```

- 只读任务：`dont_ask` + `Read,Grep,Glob`。
- 要改代码：先开分支，用 `accept_edits` 或 `auto`；改完必须 review diff + 跑 pytest，不能直接信它的“测试通过”。
- 每次调用消耗 Qoder CN credits；结果和原始日志写到 `docs/agent-runs/`（`.log` 已被 gitignore）。
- 不要把 token、账号信息写进仓库。

## 网络

这台机器访问 GitHub 时通时断。`git push` 前先看 `docs/HANDOFF.md` 的「网络」一节；不要随意改全局 git 配置。
