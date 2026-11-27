# 每次更新后的固定流程（AI 提示词）

> 用途：用户每提出一次 RuleBox 更新后，把顶部提示词贴给 AI；AI 按下面清单执行。
> 当前基线：**219 passed**、**23 个官方关卡**、**6 个官方分类**、编辑器调色板 **53 项**（17 物件含空 + 36 词块）。
> 详细状态以 `docs/HANDOFF.md` 顶部和 `git log` 为准。

## 一、可直接粘贴的提示词

```text
接手 RuleBox，按 docs/UPDATE-CHECKLIST.md 执行本次更新。

要求：
1. 先读 AGENTS.md 和 docs/HANDOFF.md 顶部的“新会话从这里读”，再跑 pytest 确认基线。
2. 先判断本次改动类型：机制/引擎、关卡、UI/编辑器、纯文档。
3. 写代码前先写/补会失败的测试；机制改动必须覆盖正例和至少一个边界。
4. 完成后跑完整 pytest，更新所有受影响的计数、分类、截图和文档。
5. 如果改了代码、关卡或 UI，重建 dist/RuleBox-Windows.zip；纯文档可跳过并说明。
6. 用中文提交，前缀 feat/fix/test/docs/chore；推送后确认 git status 干净。
7. 最后汇报：改了什么、测试数、关卡数、包路径、提交号、没做什么。
```

## 二、每次更新都要做的事

### 0. 同步现场

```powershell
git status --short
git log --oneline -3
.\.venv\Scripts\python.exe -m pytest -q
```

- 确认当前基线；如果测试本来就不是全绿，先报告，不要假装通过。
- 不要覆盖用户未提交的改动；不要删除 `custom_levels/`、`progress.json`。

### 1. 判断改动类型

| 类型 | 典型改动 | 必做 |
| :--- | :--- | :--- |
| 机制/引擎 | 新属性、新规则、移动/接触结算 | 先测后改；core 不 import pygame；检查快照/撤销 |
| 关卡 | 新关、改地图、改规则位置 | 更新章节、测试、截图；不自动生成解法 |
| UI/编辑器 | 菜单、选关、编辑器布局、调色板 | 截图检查；调色板/画布尺寸回归 |
| 纯文档 | 说明、交接、提示词 | 更新计数和链接；无需重建包 |

### 2. 机制/引擎改动

- 在 `tests/` 先加一个会失败的测试。
- 涉及移动时同时检查：
  - `world.snapshot()` 和失败回滚；
  - 推链、浮层、`停/推/开/关/沉/败/弱/移/拉` 的交互；
  - `有` 的死亡生成顺序；
  - 是否误触发胜利。
- 规则解析改动要覆盖：合法句、非法句、重叠/前后缀子句。
- 跑完整测试，不只跑新测试。

### 3. 关卡改动

- 新关文件放 `content/levels/`，命名：
  - 教程：`01-*.txt` … `10-*.txt`
  - 主线：`main-<章>-<关>.txt`
- 章节由文件名自动推导，不要手工写死关卡列表。
- 更新 `tests/test_app_flow.py` 中对应章节的关卡列表。
- 生成 `docs/preview_main_<章>_<关>.png`。
- 新章节还要更新：
  - `official.png`
  - `select_chapter<N>.png`
  - `menu.png`（如果菜单可见内容变化）
- 官方关卡暂无自动解法时，在汇报中明确说明；不要伪造 `solutions/` 回放。
- 如果用户给了解法/回放串，才补 `solutions/` 和 `tests/test_solutions.py`。

### 4. UI/编辑器改动

- 截图检查实际布局，不只看代码。
- 编辑器调色板当前 53 项，14 列 4 行；新增词块时检查是否换行、是否遮挡提示文字。
- 画布默认完全空白，不自动围墙。
- 一个格子最多一个物件 + 一个词块；右键移除顶层。
- 试玩/保存/分享码都要能保留 `stack` 叠放层。

### 5. 文档和计数

每次改动后至少检查这些文件：

- `README.md`：功能列表、关卡表、截图、测试基线
- `AGENTS.md`：当前状态、测试数、下一步
- `docs/HANDOFF.md`：顶部快速交接、资源、关卡分类、已知边界
- `docs/MECHANICS.md`：机制说明、属性表、结算顺序
- `docs/HOW-TO-PLAY.txt`：玩家操作和分类
- `docs/DISTRIBUTION.md`：关卡数量、发布检查项
- `docs/ai-log.md`：本次改动的真实记录
- `docs/UPDATE-CHECKLIST.md`：如果流程本身变化，更新本文件

容易漏的计数：

- 测试数
- 官方关卡总数
- 各章节关卡数
- 调色板物件/词块/总项数
- 截图文件名
- 最新提交号（文档里尽量写“以 git log 为准”，避免刚提交就过期）

### 6. 截图

```powershell
# 单关预览
.\.venv\Scripts\python.exe run.py content\levels\main-5-1.txt --shot docs\preview_main_5_1.png

# 菜单
.\.venv\Scripts\python.exe run.py --shot docs\menu.png
```

分类页/选关页用无头 pygame 渲染后保存；检查：
- 标题正确；
- 分类数量正确；
- 没有文字重叠/截断；
- 新关卡在列表里可见。

### 7. 构建发布包

只在代码、关卡或 UI 变化时执行：

```powershell
.\.venv\Scripts\python.exe tools\build_release.py
```

构建后确认：

```powershell
Get-ChildItem dist
```

- `dist/` 最终只保留 `RuleBox-Windows.zip`；
- 压缩包内关卡数正确；
- 不把 `dist/` 提交进 git。

纯文档更新可以跳过构建，但要在汇报里明确“未重建包”。

### 8. 提交与推送

```powershell
git status --short
git add <本次相关文件>
git commit -m "feat: ..."   # 或 fix/test/docs/chore
```

- 一个提交只做一件事。
- 不提交 `.venv`、`progress.json`、`custom_levels/`、`dist/`、日志。
- GitHub 网络不稳时按 `docs/HANDOFF.md` 的网络说明换 IP 重试；成功后确认：

```powershell
git status -sb
```

### 9. 最终汇报格式

```text
已完成：<一句话>
- 机制/关卡：<具体变化>
- 测试：<N> passed
- 关卡：<总数> 关
- 发布包：dist/RuleBox-Windows.zip（或“本次为文档更新，未重建”）
- 提交：<hash> <message>
- 未做/已知边界：<...>
```

## 三、完成标准

- [ ] 完整 pytest 全绿，且新增行为有测试
- [ ] 没有破坏 core 无 pygame 约束
- [ ] 关卡分类、测试列表、截图同步
- [ ] README/HANDOFF/MECHANICS/AGENTS/HOW-TO-PLAY/DISTRIBUTION/ai-log 已检查
- [ ] 计数与实际一致
- [ ] 需要时已重建 zip，包内关卡数正确
- [ ] 已提交并推送，工作区干净
- [ ] 汇报里写清测试数、关卡数、包路径、提交号、未做项

## 四、不要做

- 不要重写 UI、换框架或引入游戏引擎。
- 不要删除/重置用户自制关卡和进度。
- 不要在编辑器里加“转官方”按钮；官方收录由维护者手动完成。
- 不要伪造解法或声称未运行的测试通过。
- 不要把 PAT、密码、个人邮箱写进仓库。
- 不要为了小改动重建整个包，除非本次确实改了代码/关卡/UI 或用户要求。
