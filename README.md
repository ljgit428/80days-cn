# 80 Days 汉化工具（简体中文）

为 inkle 出品的《80 Days》（**GOG 原版 PC，Unity 5 / Mono**）制作简体中文汉化所用的工具与技术笔记。

## 版权说明

- 《80 Days》的文本、代码与资源版权归 **inkle Ltd.** 所有，本项目与 inkle 无关，请购买正版。
- **本仓库只包含自写的工具代码与技术笔记，不包含任何游戏文件、游戏文本（英文原文或中文译文）、反编译代码或打好补丁的文件。**
- 使用这些工具需要自己拥有正版游戏，并自备译文。
- 代码以 MIT 协议发布（见 `LICENSE`）。

## 内容

```
_tools/        提取游戏文本、分析格式、生成与替换中文字体（make_cn_fonts / patch_font）
_tools2/       翻译流水线：可译判定、遍历 ink 剧本与数据文件、回写 resources.assets、
               场景界面文字回写、TextMeshPro 后备字体、差异补丁打包等
cnpatch/       C# 程序补丁
  CNText/        CNText.dll：中文断行、中文间空格与重复标点整理、时间/界面短标签（线索句模板 CNClue.cs 含译文，不公开，需自备）
  Patcher/       用 Mono.Cecil 按译文表替换程序内字符串、注入 CNText 调用
  Tester/        CNText 小测试
docs/          技术笔记（ink 格式、字体、排版、踩坑记录）
```

## 译文格式（需自备）

工具从 `translation/`（本仓库不含）读取译文：

- `tm_zh.json`：`{"英文片段": "中文"}`，或公开安全版 `translation/hashed/tm_zh.json`：`{"sha1(英文)[:16]": "中文"}`
- `tm_line.json`：按文件区分的短串 `{"文件名": {...}}`
- `code_strings.json`：程序内字符串 `{"类型::方法": {"英文": "中文"}}`
- `ui_scene.json`：场景界面文字 `{"英文": "中文"}`
- `ink_patches.json` / `bb_override.json`：少量 ink 结构补丁（可为空 `[]` / `{}`）

## 构建流程

环境：Windows，Python 3.10 + `UnityPy==1.25.0`、`TypeTreeGeneratorAPI`、`fontTools`；.NET SDK。
脚本中的路径默认为 `F:\Games\80 Days`（游戏）与 `D:\git\project\80 days CN`（本项目），请按需修改。

1. 把正版游戏目录复制到 `ORIGINAL_BACKUP/`（仅本地）。
2. `python _tools\dump_textassets.py` 提取文本到 `extracted/`（仅本地）。
3. 字体：`_tools\make_cn_fonts.py` → `_tools\patch_font.py` → `_tools2\fix_tmp_atlas.py`。
4. `cd _tools2 && python apply.py`：译文写回 `resources.assets`。
5. `python _tools2\apply_ui.py`：界面文字。
6. `cnpatch\CNText` 下 `dotnet build -c Release`，复制 `CNText.dll` 到游戏 `Managed\`；再在 `cnpatch\Patcher` 下 `dotnet run -c Release`。

## 致谢

原作：inkle Ltd.《80 Days》。字体：Noto Sans SC（SIL OFL 1.1）。
