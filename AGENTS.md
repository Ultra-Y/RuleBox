# AGENTS.md

> 给接手本仓库的 AI 编程代理。先读本文件，再读 `docs/HANDOFF.md`，然后跑测试。

## 项目

RuleBox：中文词块推箱解谜。墙、箱子、旗子的行为由场上可推动的词块决定（受《Baba Is You》启发）。
目标：教程关 + 主线关卡，可玩、可测、能讲清设计。

## 接手后先做三件事

1. 读 `docs/HANDOFF.md`：当前状态、下一步、设计债、网络注意事项。
2. 跑测试，确认基线（期望 `152 passed`）：

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

## 当前状态（2026-11-11）

- 最新提交以 `git log` 为准。
- Day 1–2 完成：关卡 DSL、移动、推箱、推词、规则解析、胜负、撤销、重开、键盘修复。
- 5.1 完成：没有「停 / 赢 / 推」的普通物件可与「你」重叠；离开后仍保留，撤销可恢复所有层。
- 5.2 完成：变形 `A 是 B` 在移动结算后统一生效；词块不参与；同一回合按开始时身份只变一次。
- 5.3 完成：浮层、热/融、开/关、传全部结算；水是普通物件，没有内建属性；失去所有「你」判负，UI 显示失败遮罩。
- 交互完成：开始菜单、选关、通关进度、过关下一关；规则句支持相邻两句（横/竖），每关显式「墙 是 停」。
- 关卡：第 1–10 关作为教程，第一章 1-1/1-2、第二章 2-1；菜单 `官方关卡` 下分 `教程` / `第一章` / `第二章`；04–09 每关配 `solutions/` 回放测试，10 由作者实测通过。
- 编辑器：5×5–20×20、调色板、试玩、打开、保存、重命名、删除、撤销/重做、分享码；官方收录不在编辑器里做，由维护者复制到 `content/levels/` 并补解法。
- 美术：10 个 16×16 像素精灵在 `assets/sprites/`；`ui/sprites.py` 加载，缺图回退色块。
- 词块：`active_word_positions` 标记有效句子；未生效词块压暗，棋盘和编辑器共用。
- 规则：`A 是 A` 锁定 A 的变形；冲突的 `A 是 B` 不生效，棋盘上整句压暗并在主语词块画红叉；一段词块里的合法子句可重叠/取前后缀生效；`A 是 B 和 属性` 同时变性并加属性。
- 移动：`停 + 推` 的物件可以被推；只有“停但不可推”的物件挡路；`关 + 推` 的门同理；`OPEN` 遇 `SHUT` 双方抵消；`败` 与「你」同格判负；`沉` 与同格所有物件/词块一起消失；「你」自身带 `WIN` 时操作即胜。
- 浮：`FLOAT` 是独立层；词块受 `词` 属性影响；浮物块可推词，浮词块任意层「你」可推；浮物件不能穿过 `STOP`；所有带浮的实体（包括词块）免疫沉。
- 152 条测试全过；教程 10 关 + 第一章 1-1/1-2 + 第二章 2-1 可玩。
- 发布：`tools/build_release.py` 打 Windows 免安装包，产物在 `dist/`（gitignore）；说明见 `docs/DISTRIBUTION.md`。
- 当前真正生效：`你 / 推 / 停 / 赢`、变形、`浮 / 热 / 融 / 开 / 关 / 传`。

## 下一步

见 `docs/HANDOFF.md` 第 5 节。优先级：

1. 补主线 2-2 及后续章节。
2. 提示系统。
3. `validate.py` 关卡校验器。
4. 最佳步数与存档扩展。

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













