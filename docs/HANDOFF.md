# 交接说明（Handoff）

> 快照：2026-11-10 17:10（UTC+8）
> 最新提交：`054dba3`
> 仓库：https://github.com/Ultra-Y/RuleBox （public）
> 交接 tag：`handoff-2026-11-10`

## 1. 一句话状态

Day 2 完成：能走、能推箱、能推词、能解析规则、能判胜负、能撤销重开；34 条测试全过；第 1、2 关可玩。
第 3 关之前必须先修一个设计债：**没有「停」的物件目前仍按实心处理**。

## 2. 资源清单

| 资源 | 位置 | 说明 |
| :--- | :--- | :--- |
| 源码 | `src/rulebox/` | core 纯逻辑，ui 用 Pygame |
| 关卡 | `content/levels/01-*.txt`、`02-*.txt` | 文本 DSL |
| 测试 | `tests/` | 34 条 |
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

### 5.1 设计债：没有「停」的物件应当可穿过（阻塞第 3 关）

现状：`movement._move_one()` 对“不是 PUSH、不是 WIN”的物件一律返回“挡住”。
后果：第 3 关「拆墙」不成立——把「停」推走，墙还是挡路。

期望行为（先用测试锁住）：

- 目标格有 `STOP` → 挡住。
- 目标格是 `WIN` → 「你」接触即胜。
- 目标格有 `PUSH` → 尝试推；推不动则整体不动。
- 以上都不是 → 「你」可以进入该格，与它**重叠**；离开后物件还在。
- 非「你」的物体不能进入已被占据的格子。
- 撤销要同时恢复两层。

建议实现：把 `World.cells` 从 `Entity | None` 改成两层（`base` + `occupants`）或每格一个小列表；渲染先画 base 再画 occupants；`you_positions` 要扫描两层。**先加一组失败测试，再改实现。**

### 5.2 变形结算

`石 是 箱` 目前只解析、不生效。移动结算后统一替换，注意不要替换词块自身。

### 5.3 机关

水/浮、热/融、开/关、传。每加一个属性，先补属性交互测试，再补一关。

### 5.4 关卡 3–8

每关配 `solutions/XX.txt`（`URDL` 字符串），加回放测试；跑不通就不算关卡完成。

## 6. 已知问题

- 5.1 的可穿过语义未实现。
- 变形、水、热、开关、传送只解析、未结算。
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
2. 运行 .\.venv\Scripts\python.exe -m pytest -q，确认 34 passed。
3. 运行 .\.venv\Scripts\python.exe run.py content\levels\02-move-aside.txt，确认能启动。

约束：
- 不要用 PATH 里的 python（MSYS2，没有 pip）。
- core/ 不能 import pygame。
- 改行为前先写测试；改完跑全量 pytest。
- 不要重写 UI，不要引入新框架。

今天只做 HANDOFF 第 5.1 节：让没有「停」属性的物件可穿过/可重叠，并补测试。
先给我看实现计划和会新增/修改哪些测试，等我确认后再改代码，不要直接提交。
```

## 10. 交接检查清单

- [x] 代码已推送，远程 = 本地
- [x] 测试 34 passed
- [x] 计划 / 清单 / AI 记录进仓库
- [x] 交接 tag
- [ ] 新 agent 跑通测试
- [ ] 用户实机确认键盘
