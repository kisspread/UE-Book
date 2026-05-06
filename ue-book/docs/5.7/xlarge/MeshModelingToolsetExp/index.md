# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产、编辑器 UI 预制件） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 总体用途

该插件在官方 Modeling Mode（网格建模模式）之上提供一系列**实验性**的扩展工具和 UI 组件。它基于 Interactive Tools Framework 构建，专注于更高级的网格创建、编辑与几何处理操作。主要解决官方基础建模工具未覆盖或尚在试验阶段的场景，例如：

- 高级网格生成（如立方体网格、布尔运算扩展）
- 几何处理适配与转换（将动态网格源转换为静态网格等）
- 更完善的建模编辑器 UI（属性面板、操作菜单）
- 实验性工具的原型验证

## 模块列表

| 模块 | 一句话概述 |
|---|---|
| `GeometryProcessingAdapters` (Runtime) | 提供几何处理任务的适配接口，桥接底层几何算法与建模工具 |
| `MeshModelingToolsEditorOnlyExp` (Runtime) | 包含仅可在编辑器环境下使用的实验性建模工具（如合并、近似等） |
| `MeshModelingToolsExp` (Runtime) | 核心实验性建模工具集（立方体网格、转换操作等） |
| `ModelingEditorUI` (Runtime) | 建模模式下的扩展编辑器 UI 组件（工具条、设置面板） |
| `ModelingUI` (Runtime) | 通用建模 UI 基础设施（按钮、滑块、列表等复用小部件） |

## 使用场景

- **快速原型与实验**：开发者需要测试新的网格生成或编辑算法，可以基于此插件已有的实验性工具快速搭建流程。
- **建模工作流增强**：标准 Modeling Mode 缺少特定操作（如“接受并新建”命令、多动态网格转换为静态网格），本插件提供补充。
- **编辑器界面自定义**：通过 `ModelingEditorUI` 和 `ModelingUI` 可以复用或扩展建模模式的 UI 布局。
- **几何处理管道**：当需要将不同来源的网格数据（动态网格、静态网格）进行统一处理时，`GeometryProcessingAdapters` 提供适配层。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [子模块文档 - GeometryProcessingAdapters](./GeometryProcessingAdapters.md)
- [子模块文档 - MeshModelingToolsEditorOnlyExp](./MeshModelingToolsEditorOnlyExp.md)
- [子模块文档 - MeshModelingToolsExp](./MeshModelingToolsExp.md)
- [子模块文档 - ModelingEditorUI](./ModelingEditorUI.md)
- [子模块文档 - ModelingUI](./ModelingUI.md)