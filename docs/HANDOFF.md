# 交接说明（Handoff）

> 快照：2026-11-10（5.2 文档收尾）
> 最新代码提交：`da6c1b4`（以 `git log` 为准）
> 仓库：https://github.com/Ultra-Y/RuleBox （public）
> 交接 tag：`handoff-2026-11-10`

## 1. 一句话状态

Day 2、5.1、5.2 完成：能走、能推箱、能推词、能解析规则、能判胜负、能撤销重开；无「停」的普通物件可与「你」重叠；变形 `A 是 B` 在移动结算后生效；44 条测试全过；第 1、2 关可玩。
下一项是 5.3：**水/浮、热/融、开/关、传**（先做水/浮与热/融）。

## 2. 资源清单

| 资源 | 位置 | 说明 |
| :--- | :--- | :--- |
| 源码 | `src/rulebox/` | core 纯逻辑，ui 用 Pygame |
| 关卡 | `content/levels/01-*.txt`、`02-*.txt` | 文本 DSL |
| 测试 | `tests/` | 44 条 |
| 子 agent 封装 | `tools/qoder_agent.py` | 调用 Qoder CN CLI，结果在 `docs/agent-runs/` |
| 计划 | `docs/plan.md` | 12 关、6 周的原计划（快照） |
| 清单 | `docs/checklist.md` | 每日/每周行动清单（快照） |
| 截图 | `docs/preview_01.png`、`preview_02.png` | README 用 |
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

### 5.3 机关

水/浮、热/融、开/关、传。每加一个属性，先补属性交互测试，再补一关。

### 5.4 关卡 3–8

每关配 `solutions/XX.txt`（`URDL` 字符串），加回放测试；跑不通就不算关卡完成。

## 6. 已知问题

- 水、热、开关、传送只解析、未结算。
- 没有选关、存档、提示系统。
- 没有 `validate.py`，关卡“有解”目前只靠单关测试。
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
2. 运行 .\.venv\Scripts\python.exe -m pytest -q，确认 44 passed。
3. 运行 .\.venv\Scripts\python.exe run.py content\levels\02-move-aside.txt，确认能启动。

约束：
- 不要用 PATH 里的 python（MSYS2，没有 pip）。
- core/ 不能 import pygame。
- 改行为前先写测试；改完跑全量 pytest。
- 不要重写 UI，不要引入新框架。

下一项只做 HANDOFF 第 5.3 节的第一部分：水/浮（FLOAT）与热/融（HOT/MELT）的结算，并补测试。
先给我看实现计划和会新增/修改哪些测试，等我确认后再改代码，不要直接提交。
```

## 10. 交接检查清单

- [x] 代码已推送，远程 = 本地
- [x] 测试 44 passed
- [x] 计划 / 清单 / AI 记录进仓库
- [x] 交接 tag
- [x] 新 agent 跑通测试
- [ ] 用户实机确认键盘
