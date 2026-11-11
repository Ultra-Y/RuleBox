# 发布 / 给别人体验

## 推荐：Windows 免安装包

构建后得到：

```text
dist/RuleBox-Windows.zip      约 13 MB
dist/RuleBox/RuleBox.exe
```

把 **整个 zip** 发给对方，对方：

1. 解压到有写权限的文件夹（不要直接在压缩包里运行）；
2. 双击 `RuleBox.exe`；
3. 如果 SmartScreen 提示“未知发布者”，点“更多信息 → 仍要运行”。

这是 Windows 10/11 64 位包，不需要安装 Python。

### 存档位置

`progress.json`、`custom_levels/`、`exports/` 都会生成在 `RuleBox.exe` 旁边。
换电脑时把整个 `RuleBox` 文件夹一起拷走，就能保留自制关卡和通关记录。

### 分发方式

- GitHub Releases：新建 release，把 `RuleBox-Windows.zip` 拖进去，发 release 链接；
- 网盘 / 微信 / QQ：直接发 zip；
- 不要只发 exe：`_internal` 文件夹里有 Python 运行时、素材和关卡，缺了会启动失败。

## 源码运行

对方有 Python 3.10 时：

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

## 自己重新打包

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe tools\build_release.py
```

脚本会调用 PyInstaller，把 `assets/`、`content/` 和 `run.py` 打进去，生成
`dist/RuleBox/` 与 `dist/RuleBox-Windows.zip`。

打包完成后脚本会自动清理：

- `dist/RuleBox-Windows/`、`dist/RuleBox-test/`、`dist/package-test/` 等旧解压目录；
- `dist/RuleBox/` 构建目录。

所以正常结果只剩 `dist/RuleBox-Windows.zip`。如果你把旧包解压到了别的位置，脚本不会去动它，需要手动删除。

- 打包机需要 Windows x64 + Python 3.10；
- 生成的 exe 没有代码签名，SmartScreen 提示是正常的；
- 更新关卡或素材后重新跑一次脚本即可；
- `dist/`、`build/` 已在 `.gitignore`，不要把构建产物提交进仓库，发 Release 附件即可。

## 其他平台

- macOS / Linux：在对应系统上用同一份源码和 PyInstaller 重新打包；
- 网页版：Pygame 可以用 pygbag 转 WebAssembly，但本作的 `progress.json`、编辑器保存和分享码依赖本地文件，需要额外改成浏览器存储，目前没有做。

## 体验前的检查清单

- [ ] 解压后 `RuleBox.exe` 与 `_internal/` 在同一层；
- [ ] 菜单显示 10 个官方关卡；
- [ ] 能进入第 1 关、看到像素精灵；
- [ ] 过关后 `progress.json` 出现在 exe 旁边；
- [ ] 编辑器能保存到 `custom_levels/`。
