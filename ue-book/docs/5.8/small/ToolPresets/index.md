# Tool Presets

> Adds support for saving and loading tool settings as presets.

| 属性 | 值 |
|---|---|
| 中文名 | 工具预设 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产类型定义、编辑器 UI） |
| 模块 | `ToolPresetAsset` (Editor), `ToolPresetEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-20 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets) | |

## 用途

ToolPresets 为建模模式（Modeling Mode）中的工具提供了**设置预设的保存与加载**能力。它解决的核心问题是：建模工具（如 Mesh Bevel、Extrude 等）通常有大量可调参数，每次重新配置非常繁琐。通过此插件，用户可以将当前工具的属性快照保存为预设资产，之后一键恢复，大幅提升工作流效率。

预设以嵌套 Map 结构存储，按工具名和预设名组织，内部保存的是工具属性的完整副本，回放时直接覆盖到活动工具上。

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| [ToolPresetAsset](ToolPresetAsset.md) | Editor | 定义预设资产类型 `UToolPresetAsset`，负责预设数据的序列化、保存与加载 |
| [ToolPresetEditor](ToolPresetEditor.md) | Editor | 提供建模模式内的预设交互 UI，包括选择、保存、应用、重命名预设 |

## 使用场景

- 你在 **Modeling Mode** 中反复使用相同的建模参数（如 Bevel 宽度、Extrude 深度） → 保存为预设快速切换
- 团队协作时需要共享标准化的建模参数 → 导出预设资产供他人使用
- 需要为不同任务维护多套参数模板（如"建筑硬表面"vs"有机体建模"） → 管理多个预设集合

## 蓝图用法

该插件的预设交互主要通过建模模式 UI 面板完成，需通过实验性 CVar `modeling.EnablePresets` 启用。详细 API 参见各模块文档。

## C++ 用法

详细 API 参见各模块文档：
- [ToolPresetAsset](ToolPresetAsset.md) — 资产类型与序列化 API
- [ToolPresetEditor](ToolPresetEditor.md) — 编辑器交互与 UI 注册

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。此插件是 **ModelingToolsEditorMode** 的依赖项。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | FJsonObject 重构以支持 FString 和 FSharedString |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | ContentBrowser 新增杂项菜单项 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换后的第二次提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退 CL51314860 |

### 维护评价

该插件创建于 2023 年 1 月，初始提交后**长期未有实质性功能更新**。近期的 git 提交均为底层框架变更（如 FJsonObject 重构），并非针对 ToolPresets 本身的功能迭代。插件仍标记为 `IsExperimentalVersion=true`，属于实验性功能。

综合评价：
- ⚠️ **实验性状态**：插件自创建以来一直为实验性，未毕业为正式功能
- ⚠️ **功能停滞性**：最近 3 年无针对本插件的功能性更新
- ✅ **默认启用**：虽然实验性，但默认启用且无严重已知问题
- 📌 **建议**：可放心使用，但需注意其实验性状态，未来 API 可能变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets)
- [ToolPresetAsset 模块文档](ToolPresetAsset.md)
- [ToolPresetEditor 模块文档](ToolPresetEditor.md)