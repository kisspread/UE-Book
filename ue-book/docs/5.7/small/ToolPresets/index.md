# Tool Presets

> Adds support for saving and loading tool settings as presets.

| 属性 | 值 |
|---|---|
| 中文名 | 工具预设 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（预设资产、UI 资源） |
| 模块 | `ToolPresetAsset` (Editor), `ToolPresetEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets) | |

## 总体用途

Tool Presets 插件为 Unreal Editor 中的各种工具（如建模、网格编辑、地形工具等）提供了预设系统。它允许用户**保存工具当前的所有设置为一组命名预设**，并在需要时快速加载、共享或管理这些预设。核心功能包括：

- 创建、重命名、删除预设集合
- 将预设应用于工具（恢复全部设置）
- 预设的导入/导出（用于团队协作）
- 与现有的工具系统无缝集成

该插件解决了“每次使用工具前反复调整参数”的痛点，提升了迭代工作流的效率。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `ToolPresetAsset` | Editor | 定义预设资产（`UToolPresetAsset`）的 UObject 结构、保存/加载逻辑，提供运行时预设操作 API。 |
| `ToolPresetEditor` | Editor | 提供预设管理 UI（面板、菜单）、资产工厂、编辑器集成以及预设的复制/粘贴/导入导出功能。 |

各模块详细文档：
- [ToolPresetAsset.md](ToolPresetAsset.md)
- [ToolPresetEditor.md](ToolPresetEditor.md)

## 使用场景

- **建模师工作流**：保存常用建模工具的细分级别、对称设置、网格类型等，快速在不同模型间切换。
- **团队协作**：项目经理将预设导出为 `.upresets` 文件，团队成员导入后统一工具行为标准。
- **自动化与脚本**：通过 C++ 或 Python 加载预设，批量对多个对象应用相同工具设置。
- **临时方案测试**：在调试某工具参数时，保存当前状态为预设，避免因误操作丢失调试配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ToolPresets)