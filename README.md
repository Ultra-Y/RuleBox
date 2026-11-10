# RuleBox

推得动箱子，也推得动规则。

一款中文词块推箱解谜游戏：墙、箱子、旗子的行为，由场地上可推动的词块决定。
把「墙 是 停」推散，墙就不再挡路；拼出「箱 是 赢」，箱子就成了终点。

> 机制灵感来自《Baba Is You》；代码、关卡、美术均为原创。

![预览](docs/preview_01.png)

## 环境

- Python 3.10+
- pygame、pytest

## 安装

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行

```powershell
python run.py
python run.py content/levels/01-first-step.txt
```

Esc 退出。没有安装 pygame 时会自动退化为文本输出。

## 测试

```powershell
pytest
```

## 当前进度

- [x] 仓库初始化
- [x] 关卡 DSL 与加载
- [x] 世界快照与撤销
- [x] Pygame 关卡预览
- [ ] 移动与推箱
- [ ] 规则解析（你 / 推 / 停 / 赢）
- [ ] 12 关完整内容

## 目录

```text
RuleBox/
├── src/rulebox/
│   ├── core/           # 纯逻辑，不依赖 pygame
│   │   ├── entities.py
│   │   ├── level.py
│   │   └── world.py
│   └── ui/app.py       # Pygame 渲染
├── content/levels/     # 关卡文本
├── tests/              # pytest
├── run.py              # 启动器
└── requirements.txt
```
