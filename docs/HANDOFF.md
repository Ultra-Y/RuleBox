# 交接说明（Handoff）

> 快照：2026-11-11（像素精灵 + 词块生效状态）
> 最新代码提交：以 `git log` 为准
> 仓库：https://github.com/Ultra-Y/RuleBox （public）
> 交接 tag：`handoff-2026-11-10`

## 1. 一句话状态

Day 2、5.1、5.2、5.3 完成，并补上开始菜单、官方/自制关卡分离、通关进度、过关下一关；规则层支持相邻两句（横/竖）与显式「墙 是 停」；第 3 关《路被堵住了？》已加入；编辑器支持 5×5–20×20、试玩、打开、重命名、删除、分享码；物件已换成 16×16 像素精灵，未生效词块自动压暗；111 条测试全过；第 1–3 关可玩。
下一项是 5.4：**继续加第 4–8 关 + 每关解法回放测试**。

## 2. 资源清单

| 资源 | 位置 | 说明 |
| :--- | :--- | :--- |
| 源码 | `src/rulebox/` | core 纯逻辑，ui 用 Pygame |
| 关卡 | `content/levels/01-*.txt`、`02-*.txt` | 文本 DSL |
| 测试 | `tests/` | 111 条 |
| 机制说明 | `docs/MECHANICS.md` | 结算顺序、规则语法、属性表、已知边界 |
| 美术 | `assets/sprites/` | 10 个 16×16 像素精灵；生成脚本 `tools/generate_sprites.py` |
| 子 agent 封装 | `tools/qoder_agent.py` | 调用 Qoder CN CLI，结果在 `docs/agent-runs/` |
| 计划 | `docs/plan.md` | 12 关、6 周的原计划（快照） |
| 清单 | `docs/checklist.md` | 每日/每周行动清单（快照） |
| 截图 | `docs/preview_01.png`、`preview_02.png`、`preview_03.png`、`menu.png`、`select.png`、`editor.png` | README 用 |
| AI 记录 | `docs/ai-log.md` | 真实协作记录，课程提交要用 |
| 试玩 | `docs/playtest.md` | 模板，待填 |
| 远端 | GitHub `Ultra-Y/RuleBox` | public，可直接 clone |
| 离线包 | `RuleBox-handoff-2026-11-10.zip` / `.bundle` | 在上级目录，见第 8 节 |

## 3. 环境

- Windows，Python **3.10.6**（`.venv`），pygame 2.6.1，pytest 9.2.0。
- **不要用 PATH 里的 `python`**：它是 MSYS2 的，没有 pip。
- 命令一律用 `.\.venv\Scripts\python.exe`。

全新机器上重建：

```powershell
git clone https://github.com/Ultra-Y/RuleBox.git
cd RuleBox
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

## 4. 已冻结的设计决策（改之前先确认）

1. **每一步顺序**：输入 → 解析规则 → 找「你」→ 移动/推链 → 接触结算 → 变形 → 重新解析 → 判定胜负 → 存快照。
2. **词块永远可推、不会被毁**：避免把关键词推进水里造成死局。
3. **WIN 只由「你」接触触发**：把箱子推进赢物件不算赢；推动链里的物体不能触发胜利。
4. **推链失败整体不动**：不能出现“推了一半”。
5. **失败的移动不留快照**：撤销只会回到真实的上一步。
6. **中文词块、中文 UI**：这是和原版最主要的差异，不要英文化。
7. **core 不依赖 pygame**：所有规则/移动必须能 headless 测试。

## 5. 下一步（按顺序）

### 5.1 已完成：没有「停」的物件可穿过、可重叠

原问题：`movement._move_one()` 对“不是 PUSH、不是 WIN”的物件一律返回“挡住”，导致拆散「墙 是 停」后墙仍然挡路。

已实现的行为，并由测试锁定：

- 目标格有 `STOP` → 挡住。
- 目标格是 `WIN` → 「你」接触即胜。
- 目标格有 `PUSH` → 尝试推；推不动则整体不动。
- 以上都不是 → 「你」可以进入该格，与普通物件**重叠**；离开后物件还在。
- 非「你」的物体不能进入已被占据的格子。
- 撤销同时恢复格子的所有层。

实现采用每格 `list[Entity]`：`World` 新增 `entities_at()/add()/remove()`，快照复制每格列表；`you_positions` 和规则扫描兼容多层；UI 按底层到顶层绘制。新增 4 条测试，并将旧堵墙测试改为显式设置「墙 是 停」。

验证：38 passed；第 2 关两帧渲染启动正常；SDL dummy 的重叠局面渲染正常；`core/` 无 `pygame` 导入。

### 5.2 已完成：变形结算

行为（由测试锁定）：

- `石 是 箱` 在移动结算后统一生效；同一回合按开始时的身份只替换一次。
- 词块不参与变形。
- 同格其他实体与层叠顺序保留（`World.replace`）。
- 变形后下一步重新解析规则，属性随之变化。

实现：`movement.try_move` 在接触结算后调用 `resolve.apply_transforms`；`rules.transform_map` 提供映射；`World.replace` 原地替换。
验证：44 passed（新增 6 条变形测试）。

### 5.3 已完成：水/浮、热/融、开/关、传

**水/浮**

- 水（`water`）与同格非 `FLOAT` 物件接触即摧毁；带 `FLOAT` 的物件可共存。
- 词块与水免疫；水自身不被水摧毁。
- 同格存在 `HOT` 时摧毁 `MELT`；同一物件同时带 `HOT`/`MELT` 不自毁。

**开/关**

- `SHUT` 阻挡进入和推动；只有带 `OPEN` 的移动方能进入。
- `OPEN` 物件进入 `SHUT` 格后，同格摧毁 `SHUT`；被推的钥匙也能开门。
- `OPEN`/`SHUT` 同物件不自毁；`STOP` 优先于 `OPEN`。
- `SHUT + WIN`：没有 `OPEN` 摸不到；有 `OPEN` 直接判胜（胜利短路，门不摧毁）。

**传**

- 恰好两个 `TELE` 格时生效；只传“本步移动轨迹”里的非词块、非 `TELE` 物件。
- 只结算一次，不连锁；目的地住户不受影响；被推的箱子也会传。
- 传送后再走水/热/开关结算，所以传进水里会淹死。

**顺序**：移动 → 传送 → 开/关 → 水 → 热/融 → 变形 → 重新解析 → 判负。

实现：`resolve.is_obstacle` / `apply_teleports` / `_shut_victims`；`movement` 用 `trail` 记录本步移动；`Game.lost`；`ui` 失败遮罩。
验证：82 passed（新增 20 条开关/传送测试）。
已知边界：传送落点没有重新检查 `STOP`/`SHUT`；门同时带 `PUSH`+`SHUT` 时 `OPEN` 会先推门而不是开门。等关卡需要时再收紧。

### 5.3.1 规则句与墙修复（已完成）

- 相邻的两句（横排或竖排）不再互相破坏：`rules.parse_run` 用 DP 切成句子数最多的合法切法。
- 墙不再默认实心：每关显式放「墙 是 停」；第 1 关横排、第 2 关竖排「墙 / 是 / 停」。
- 验证：91 passed（新增相邻句 2 条、目录/流程 7 条）。

### 5.3.2 开始菜单、选关、进度（已完成）

- `core/catalog.py`：`discover_levels`、`Progress`（读写 `progress.json`）、`next_index`、`first_unfinished`。
- UI：菜单（开始游戏 / 选关 / 退出）、选关（✓ 标记已完成）、过关后 `N`/`Enter` 下一关、`Esc` 回菜单、失败 `R` 重开。
- 进度文件 `progress.json` 已 gitignore。
- 验证：91 passed，含无头 UI 流程 3 条。

### 5.3.3 关卡编辑器与分享码（已完成）

- 官方关卡：`content/levels/*.txt`；自制关卡：`custom_levels/*.txt`（gitignore），菜单分开显示。
- `core/level_builder.py`：调色板、字符网格 ↔ DSL、分享码 base64、按名称安全保存。
- `ui/editor.py`：5×5–20×20 画布、调色板、放置/擦除、试玩、打开、重命名、删除、导出/导入分享码。
- 试玩不落盘：`App.play_editor_level` 直接构造 `Game`，Esc 回编辑器，不写进度。
- 保存/导入前都用 `parse_level` 校验，坏码不会进关卡库。
- 验证：111 passed（新增目录/编辑器/尺寸/素材测试 19 条）；菜单/官方选关/编辑器截图检查。

### 5.3.4 像素精灵（已完成）

- 10 个物件精灵：人、墙、箱、旗、水、火、石、门、钥、传送门，16×16 PNG，`assets/sprites/`。
- `ui/sprites.py` 负责加载/缓存/最近邻缩放；棋盘与编辑器调色板共用；缺图回退色块+文字。
- `tools/generate_sprites.py` 是生成脚本（需要 Pillow，运行时不需要）。
- 验证：111 passed（新增素材完整性测试）；三关、菜单、官方选关、编辑器截图检查。

### 5.3.5 词块生效状态（已完成）

- `rules.active_word_positions` 复用 `parse_run_spans`，返回被有效句子占用的格子。
- 棋盘与编辑器把未生效词块压暗（颜色 ×0.48），生效词块保持原色。
- 验证：111 passed（新增横/竖/相邻/无效句判定）；`docs/word_states.png` 对比截图。

### 5.4 关卡 3–8（进行中）

- **03 已加入**：`content/levels/03-blocked-road.txt`，第 2 关地图，箱子从 `(4,5)` 下移到缺口 `(5,5)`；布局测试锁住坐标。解法由策划提供，代码只保证加载、渲染和规则正确。
- 04–08 待做；每关配 `solutions/XX.txt`（`URDL` 字符串）和回放测试，跑不通不算完成。

## 6. 已知问题

- 传送落点未复查 `STOP`/`SHUT`；`PUSH`+`SHUT` 门的开关优先级待关卡验证。
- 没有提示系统，也没有 `validate.py`；关卡“有解”目前只靠单关测试。
- 关卡 3–8 尚未做完；`progress.json` 只记录完成，不记录最佳步数。
- 编辑器画布上限 20×20；没有撤销/重做，也没有把自制关卡转为官方关卡的按钮（需手动复制到 `content/levels/`）。
- 导入依赖剪贴板，剪贴板不可用时需要手动复制 `.code`。
- 美术是固定 16×16 静态精灵，没有动画/朝向；词块仍是文字色块。
- 键盘问题已修（焦点/IME/连发），但需要用户实机再确认；`--debug-keys` 可打印按键。

## 7. 网络（这台机器）

GitHub 时通时断，DNS 可能把 `github.com` 指到不通的 IP。

已经做过：

```powershell
git config --local http.curloptResolve "github.com:443:140.82.114.3"
```

push 超时时换一个 IP：

```powershell
git config --local http.curloptResolve "github.com:443:140.82.113.3"
# 备选：140.82.121.3、20.27.177.113
```

浏览器需要 hosts（管理员）：

```text
140.82.114.3 github.com
```

然后 `ipconfig /flushdns`。

这些配置只在本机、本仓库生效；换机器时删掉，不要写进仓库。

## 8. 离线交接

上级目录（`E:\ds\计概B大作业\`）有：

- `RuleBox-handoff-2026-11-10.zip`：HEAD 快照，不含 git 历史。
- `RuleBox-handoff-2026-11-10.bundle`：完整 git 历史，可离线 clone。

```powershell
git clone RuleBox-handoff-2026-11-10.bundle RuleBox
```

## 9. 给新 agent 的启动提示词

把下面整段贴给新 agent：

```text
你接手一个已有项目 RuleBox，工作目录 E:\ds\计概B大作业\RuleBox。

第一步：
1. 读 AGENTS.md、docs/HANDOFF.md、docs/plan.md。
2. 运行 .\.venv\Scripts\python.exe -m pytest -q，确认 111 passed。
3. 运行 .\.venv\Scripts\python.exe run.py，确认开始菜单能启动。

约束：
- 不要用 PATH 里的 python（MSYS2，没有 pip）。
- core/ 不能 import pygame。
- 改行为前先写测试；改完跑全量 pytest。
- 不要重写 UI，不要引入新框架。

下一项按策划给的地图继续加第 4–8 关；每关配 `solutions/XX.txt` 和回放测试。
先给我看关卡设计与测试计划，等我确认后再改代码，不要直接提交。
```

## 10. 交接检查清单

- [x] 代码已推送，远程 = 本地
- [x] 测试 111 passed
- [x] 计划 / 清单 / AI 记录进仓库
- [x] 交接 tag
- [x] 新 agent 跑通测试
- [ ] 用户实机确认键盘
