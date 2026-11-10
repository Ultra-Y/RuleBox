# RuleBox 下一步清单

> 配套 [plan.md](plan.md)。按顺序做，做完一项勾一项。
> 每项都写了"怎么算做完"，避免"感觉做完了"。
>
> **注意**：这是 2026-11-10 的初始清单快照。Day 1–2 已完成，当前状态以 [HANDOFF.md](HANDOFF.md) 为准。

---

## 今天（30–60 分钟）：把地基摆好

- [ ] 在 `E:\ds\计概B大作业\` 下新建 `RuleBox\` 目录（课程资料留在上层，不要混进仓库）
- [ ] `git init`，写 `.gitignore`：`__pycache__/`、`.venv/`、`.pytest_cache/`、`*.pyc`、`progress.json`
- [ ] 确认 `python -V` ≥ 3.10
- [ ] 安装依赖：`pip install pygame pytest`
- [ ] 跑一个空窗口 3 秒，确认 pygame 能正常显示
- [ ] README 骨架（十个二级标题即可，内容留空）
- [ ] 建 `docs/ai-log.md`、`docs/playtest.md` 两个空模板
- [ ] 把 `PROJECT_PLAN.md` 复制到 `RuleBox/docs/plan.md`
- [ ] 首次 commit：`chore: init repo`

**完成标准**：`python -c "import pygame, pytest; print('ok')"` 输出 ok；`git log --oneline` 有一条记录。

---

## 第 1 天（2–3 小时）：数据与关卡

- [ ] `src/rulebox/core/entities.py`：`Entity` dataclass + 物件表（人/墙/箱/旗 + 词：墙、是、停、你、推、赢）
- [ ] `src/rulebox/core/level.py`：解析关卡 DSL（`name/size/legend/grid`），格式错误带行号
- [ ] `src/rulebox/core/world.py`：网格、取放物件、快照、撤销
- [ ] `content/levels/01-first-step.txt`：只有「人 是 你」「旗 是 赢」，走到旗子即胜
- [ ] `run.py` 启动器（`sys.path` 指向 `src/`，避免装包）
- [ ] `pyproject.toml` 里配 `pythonpath = ["src"]`、`testpaths = ["tests"]`
- [ ] `tests/test_level.py`：加载成功、尺寸不符报错、未知符号报错
- [ ] `tests/test_world.py`：放/取/撤销复原

**完成标准**：`pytest` 全绿；`python run.py` 能在终端打印出 11×7 的网格与图例。

---

## 第 2 天：让方块动起来，让规则生效

- [ ] `core/movement.py`：四方向移动、边界、`停` 阻挡、单层 `推`
- [ ] `core/rules.py`：扫描横向/纵向连续词块，解析 `名词 是 属性`（先不支持 `和`/`不`/变形）
- [ ] `core/resolve.py`：应用 `你` / `推` / `停` / `赢`
- [ ] `ui/app.py`：Pygame 窗口、网格、键盘输入、R 重开
- [ ] 关卡 `02-move-aside.txt`：推箱挡路
- [ ] 测试：边界撞墙、推不动、走到赢

**完成标准**：关卡 1–2 能完整玩通；`pytest` ≥ 8 条用例。

---

## 第 3 天：推得动规则

- [ ] 多层推链（最多 10 层）
- [ ] 推词块（与推箱子同一套逻辑）
- [ ] `Z` 撤销、`R` 重开
- [ ] 关卡 `03-break-wall.txt`：把「停」推走，墙失效
- [ ] 测试：推链 3 层、链顶撞墙、撤销逐步复原
- [ ] `docs/playtest.md` 写下第一次自测记录

**完成标准**：3 关全部能通；`pytest` ≥ 12 条；自己从零玩一遍不卡壳。

---

## 第 1 周末：M1 验收

- [ ] 启动 → 选关（先 3 关）→ 玩 → 过关 → 下一关，全流程可演示
- [ ] 推箱、推词、拆规则三种操作都能用
- [ ] `Z` 撤销、`R` 重开正常
- [ ] `pytest` 全绿
- [ ] 按 README 能跑起来
- [ ] 至少 5 次有意义的 commit
- [ ] 找 1 位同学试玩，记录卡点

> 如果第 1 周末做不到"M1 可玩"，先砍画面（用色块代替），不要砍引擎。

---

## 第 2 周：M2（规则面板与改写）

- [ ] 规则面板：实时列出当前生效的句子
- [ ] 关卡 4「箱子是赢」：把 `旗 是 赢` 改成 `箱 是 赢`
- [ ] 关卡 5「换个人」：`石 是 你`
- [ ] 解析测试扩到 15 例：横向、纵向、断开、无效、多规则
- [ ] `停` 优先于 `推` 的测试
- [ ] 每周五跑一次全量测试

**完成标准**：第 4、5 关不看代码能玩懂；解析测试全绿。

---

## 第 3 周：M3（机关）

- [ ] 变形规则 `A 是 B`
- [ ] `和`、`不`
- [ ] 水 / `浮`
- [ ] 热 / `融`
- [ ] `开` / `关`
- [ ] `传`（成对传送）
- [ ] 关卡 6–8
- [ ] 交互矩阵测试 20 例
- [ ] `tools/validate.py` + 每关 `solutions/XX.txt`

**完成标准**：8 关全部能被校验器回放通关；属性测试全绿。

---

## 第 4–6 周（一句话版）

- **W4**：关卡 9–12、选关、提示、进度保存、第一轮真实试玩
- **W5**：动画/粒子/中文字体/音效（可选）、README、截图、编辑器（可选）
- **W6**：功能冻结、PDF、`v1.0.0`、新目录复现演练

---

## 现在不要做的事

- ❌ 先做关卡编辑器、音效、粒子、菜单美化 —— 等 8 关能玩再说
- ❌ 一次写 12 关 —— 先用 3 关验证引擎，再批量生产
- ❌ 优化性能 —— 20×15 的网格用不着
- ❌ 做存档/选关系统 —— W4 再做
- ❌ 英文版、联网、剧情 —— 明确不做
- ❌ 把课程资料、作业说明放进游戏仓库

---

## 固定动作

- **每天**：至少 1 次 commit，消息用 `feat/fix/test/docs:` 前缀
- **每修一个 bug**：补一条会失败的测试，再修
- **每周三**：找 1 个人试玩当前关卡，记录卡点
- **每周五**：跑 `pytest` + `validate`，更新进度
- **每周日**：落后就按计划的裁剪顺序砍功能，不延期

---

## 卡住时的求助顺序

1. 用关卡 DSL 写一个**最小复现局面**（3×3 也行）
2. 对照计划 2.5 的结算顺序，确认是不是顺序问题
3. 先写一条**会失败**的测试，把"期望 vs 实际"固定下来
4. 再问 AI，附上：局面、操作、期望、实际、已经排除了什么

> 不要问"为什么我的游戏不工作"，要问"这个 3×3 局面按 R 后箱子没动，期望是动，测试在 tests/test_push.py:42"。

---

## 附：初始化命令

```powershell
cd E:\ds\计概B大作业
mkdir RuleBox
cd RuleBox
git init

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pygame pytest

ni .gitignore
```

`run.py` 最小版本：

```python
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from rulebox.ui.app import main

raise SystemExit(main())
```

`pyproject.toml` 最小版本：

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```
