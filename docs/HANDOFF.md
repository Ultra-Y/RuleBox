# 交接说明（Handoff）

> 快照：2026-11-11（教程 10 关 + 主线 1-1/1-2 + Windows 免安装包）
> 最新代码提交：以 `git log` 为准
> 仓库：https://github.com/Ultra-Y/RuleBox （public）
> 交接 tag：`handoff-2026-11-10`

## 1. 一句话状态

Day 2、5.1、5.2、5.3 完成，并补上开始菜单、官方/自制关卡分离、官方关卡分类（教程 / 第一章）、通关进度、过关下一关；规则层支持相邻两句（横/竖）、显式「墙 是 停」和自指规则锁；第 1–10 关作为教程，主线从 1-1 开始，当前到 1-2；04–09 每关配 `solutions/` 回放测试，10 由作者实测通过；编辑器支持 5×5–20×20、试玩、打开、重命名、删除、撤销/重做、分享码；物件已换成 16×16 像素精灵，未生效词块自动压暗；133 条测试全过；教程 10 关 + 主线 1-1/1-2 可玩。
Windows 免安装包已构建并验证：`dist/RuleBox-Windows.zip`（约 13 MB，解压双击 `RuleBox.exe`）；第 11–12 关待补，之后可做提示系统、`validate.py` 和最佳步数。

## 2. 资源清单

| 资源 | 位置 | 说明 |
| :--- | :--- | :--- |
| 源码 | `src/rulebox/` | core 纯逻辑，ui 用 Pygame |
| 关卡 | `content/levels/01-*.txt` 到 `10-*.txt` + `main-1-1.txt`、`main-1-2.txt` | 教程 01–10，主线 1-1/1-2 |
| 解法 | `solutions/*.txt` | `URDL` 回放串 |
| 测试 | `tests/` | 133 条 |
| 机制说明 | `docs/MECHANICS.md` | 结算顺序、规则语法、属性表、已知边界 |
| 美术 | `assets/sprites/` | 10 个 16×16 像素精灵；生成脚本 `tools/generate_sprites.py` |
| 发布包 | `dist/RuleBox-Windows.zip` | 约 13 MB，免安装 Windows 包；`dist/` gitignore，不提交 |
| 发布脚本 | `tools/build_release.py` | PyInstaller；玩家说明 `docs/HOW-TO-PLAY.txt` |
| 发布说明 | `docs/DISTRIBUTION.md` | 分发、SmartScreen、存档位置、重新打包 |
| 子 agent 封装 | `tools/qoder_agent.py` | 调用 Qoder CN CLI，结果在 `docs/agent-runs/` |
| 计划 | `docs/plan.md` | 12 关、6 周的原计划（快照） |
| 清单 | `docs/checklist.md` | 每日/每周行动清单（快照） |
| 截图 | `docs/preview_01.png`–`preview_09.png`、`preview_main_1_1.png`、`preview_main_1_2.png`、`official.png`、`select_tutorial.png`、`select_chapter1.png`、`menu.png`、`select.png`、`editor.png`、`word_states.png`、`sprites.png` | README 用 |
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
- `OPEN` 与 `SHUT` 同格时双方一起抵消；`OPEN` 物件不会保留。
- `OPEN`/`SHUT` 同物件不自毁；`STOP` 优先于 `OPEN`。
- `SHUT + WIN`：没有 `OPEN` 摸不到；有 `OPEN` 直接判胜（胜利短路，门不摧毁）。

**传**

- 恰好两个 `TELE` 格时生效；只传“本步移动轨迹”里的非词块、非 `TELE` 物件。
- 只结算一次，不连锁；目的地住户不受影响；被推的箱子也会传。
- 传送后再走水/热/开关结算，所以传进水里会淹死。

**顺序**：移动 → 传送 → 开/关 → 水 → 热/融 → 变形 → 重新解析 → 判负。

实现：`resolve.is_obstacle` / `apply_teleports` / `_shut_victims`；`movement` 用 `trail` 记录本步移动；`Game.lost`；`ui` 失败遮罩。
验证：82 passed（新增 20 条开关/传送测试）。
已知边界：传送落点没有重新检查 `STOP`/`SHUT`。等关卡需要时再收紧。

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
- 验证：133 passed（新增目录/编辑器/尺寸/素材测试 22 条）；菜单/官方选关/编辑器截图检查。

### 5.3.4 像素精灵（已完成）

- 10 个物件精灵：人、墙、箱、旗、水、火、石、门、钥、传送门，16×16 PNG，`assets/sprites/`。
- `ui/sprites.py` 负责加载/缓存/最近邻缩放；棋盘与编辑器调色板共用；缺图回退色块+文字。
- `tools/generate_sprites.py` 是生成脚本（需要 Pillow，运行时不需要）。
- 验证：133 passed（新增素材完整性测试）；九关、菜单、官方选关、编辑器截图检查。

### 5.3.5 词块生效状态（已完成）

- `rules.active_word_positions` 复用 `parse_run_spans`，返回被有效句子占用的格子。
- 棋盘与编辑器把未生效词块压暗（颜色 ×0.48），生效词块保持原色。
- 验证：133 passed（新增横/竖/相邻/无效句判定）；`docs/word_states.png` 对比截图。

### 5.3.6 编辑器撤销/重做（已完成）

- 编辑器网格操作、尺寸调整、清空、放置/擦除进入撤销栈，最多 60 步；`Ctrl+Z` / `Ctrl+Y`。
- 官方收录不在编辑器里做：由维护者把 `custom_levels/` 的文件复制到 `content/levels/`，补编号、解法回放和文档。
- 验证：133 passed（撤销/重做）；编辑器截图检查。

### 5.3.7 自指规则锁（已完成）

- `A 是 A` 作为锁；存在锁时 `A 是 B` 不生效。
- `transform_map` 跳过被锁的变形；规则面板用 `effective_rules` 过滤。
- 被拒绝的句子整句压暗，主语词块画红叉；棋盘和编辑器共用。
- 验证：133 passed（自指锁/属性不受影响/叉位置）；`docs/rule_lock.png` 演示图。

### 5.3.8 官方关卡分类（已完成）

- 菜单 `官方关卡` 先进入分类页：`教程（10 关）` / `第一章（2 关）`。
- 教程对应 01–10；第一章对应 `main-1-1.txt`、`main-1-2.txt`。
- 选关支持分类过滤，Esc 从子列表返回分类页。
- 验证：133 passed（分类页/过滤/返回流程）；`docs/official.png` 等截图。

### 5.3.9 停 + 推 优先级（已完成）

- `停` 的优先级低于 `推`：同时带 `停` 和 `推` 的物件可以被推。
- 只有“停但不可推”的物件才挡路；推链仍按原规则递归。
- 验证：133 passed（新增 STOP+PUSH 推动测试）；`test_wall_blocks` 继续保证纯 STOP 阻挡。

### 5.3.10 编辑器补全名词词块（已完成）

- 调色板补上 `水 / 火 / 石 / 门 / 钥` 五个名词词块；现在 11 个物件 + 24 个词块。
- 调色板改为 12 列 3 行，仍能放在原编辑区。
- 验证：133 passed（新增“调色板包含全部名词”测试）；编辑器截图检查。

### 5.3.11 败与门优先级（已完成）

- `败`：`DEFEAT` 现在生效；任意「你」与带 `败` 的物件同格即判负。
- `关`：`SHUT + PUSH` 的门像其他可推物件一样可以被推；只有 `SHUT` 且不可推的门才挡住没有 `OPEN` 的移动方。
- `OPEN` 例外：带 `OPEN` 的移动方遇到 `SHUT + PUSH` 时优先抵消门，不推门。
- 验证：133 passed（新增 DEFEAT 接触、可推门、纯 SHUT 阻挡测试）。

### 5.3.12 开/关抵消与自身带赢（已完成）

- 同格 `OPEN` + `SHUT`：双方一起消失；单个物件同时带两种属性且没有对手时不自毁。
- 教程 06 改成“推钥匙撞门”：钥匙和门一起抵消，Baba 保留；避免 OPEN 的「你」撞门后直接判负。
- 「你」自身带 `WIN`：操作它移动时直接胜利，不要求走进赢格。
- 验证：133 passed（OPEN+SHUT 抵消、OPEN 抵消 SHUT+PUSH、YOU+WIN 直胜）。

### 5.3.13 局部合法子句（已完成）

- 规则扫描改为：一段连续词块中所有合法子句都生效，允许重叠、前缀、后缀。
- `旗 是 箱 是 开` → `旗 是 箱` + `箱 是 开`；`人 旗 是 开` → 只取 `旗 是 开`；`旗 是 开 关` → 只取 `旗 是 开`。
- 长句优先，被更长合法句包含的子句不重复列出。
- 验证：133 passed（重叠、后缀、前缀三类扫描测试）。

### 5.4 关卡 4–8（已完成）

- **04 拆掉规则**：把「停」从「墙 是 停」中推出，规则失效后穿过整排墙；解法 `UDDDD`。
- **05 过河**：把「浮」推进「人 是」句子，获得浮水能力后过河；解法 `ULDDDR`。
- **06 开门**：用法是 `钥 是 推 和 开`，推钥匙撞门，钥匙和门一起抵消；解法 `DDDD`。
- **07 传送门**：两个 `TELE` 门成对传送，越过整排墙；解法 `RD`。
- **08 融化**：把带「融」的石头推进火里，石头融化后穿过火；解法 `DDD`。
- 每关配 `solutions/XX.txt`（`URDL` 字符串），`tests/test_solutions.py` 回放判定通关。
- 验证：133 passed（新增 5 条解法回放）；第 4–8 关截图检查。

### 5.5 第 09–10 关与主线 1-1/1-2

- **09 钥匙**：先拼「钥 是 开 和 推」，再推钥匙开门；解法 `ULDLLLDDDRDRR`。
- **10 意识转移**：作者自制并实测通过；关卡文本在 `content/levels/10-意识转移.txt`，暂无自动回放。
- **主线 1-1**：`content/levels/main-1-1.txt`，16×12。
- **主线 1-2**：`content/levels/main-1-2.txt`，16×14。
- 第 09 关静态规则放在地图外沿，谜题规则故意留缺口。
- 验证：133 passed；第 9 关截图检查，第 10 关由作者实测。
- 原第 09《石头变箱子》、第 10《沉箱》、第 12《传送钥匙》已删除；《钥匙》顺延为 09。
- 主线 1-3 及后续章节待补。

### 5.6 后续（非关卡）

1. 补主线 1-3 及后续章节。
2. 提示系统。
3. `validate.py` 关卡校验器。
4. 最佳步数与存档扩展。
5. 发布包（已完成）：`tools/build_release.py` → `dist/RuleBox-Windows.zip`，解压双击 `RuleBox.exe`。

### 5.7 官方收录流程

1. 玩家/策划在编辑器保存到 `custom_levels/`；
2. 维护者读文件，确认可解；
3. 复制到 `content/levels/`，用下一个编号，`name` 改成 `0X 标题`；
4. 补 `solutions/0X.txt`、回放测试、截图和文档；
5. 跑 pytest、重新打包发布。

不要直接把未验证草稿放进 `content/levels/`：游戏会把它当正式官方关卡。

## 6. 已知问题

- 传送落点未复查 `STOP`/`SHUT`。
- 没有提示系统，也没有 `validate.py`；关卡“有解”目前只靠解法回放测试。
- `progress.json` 只记录完成，不记录最佳步数。
- 主线 1-3 及后续章节待补；第 10 关、1-1、1-2 暂时只有作者实测，没有自动解法回放。
- 编辑器画布上限 20×20；撤销栈最多 60 步；编辑器不提供“转官方”按钮，官方收录由维护者手动完成。
- 导入依赖剪贴板，剪贴板不可用时需要手动复制 `.code`。
- 美术是固定 16×16 静态精灵，没有动画/朝向；词块仍是文字色块。
- 发布包未做代码签名，Windows SmartScreen 会提示“未知发布者”；分发时说明“更多信息 → 仍要运行”。
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
2. 运行 .\.venv\Scripts\python.exe -m pytest -q，确认 133 passed。
3. 运行 .\.venv\Scripts\python.exe run.py，确认开始菜单能启动。

约束：
- 不要用 PATH 里的 python（MSYS2，没有 pip）。
- core/ 不能 import pygame。
- 改行为前先写测试；改完跑全量 pytest。
- 不要重写 UI，不要引入新框架。

下一项按 5.6 补主线 1-3 或做提示系统；改动关卡时继续配 `solutions/XX.txt` 回放。
先给我看关卡设计与测试计划，等我确认后再改代码，不要直接提交。
```

## 10. 交接检查清单

- [x] 代码已推送，远程 = 本地
- [x] 测试 133 passed
- [x] 计划 / 清单 / AI 记录进仓库
- [x] 交接 tag
- [x] 新 agent 跑通测试
- [ ] 用户实机确认键盘






