# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow 节点） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

MeshResizing 是一个实验性插件，用于对静态网格资产进行**尺寸缩放/重拓扑**操作。它解决了在不破坏网格拓扑质量的前提下，将已有网格资产调整到新尺寸的需求。插件通过 Dataflow 节点系统提供可视化的网格缩放工作流，包含绘制工具、套索选择等交互式编辑功能，并集成了自定义渲染管线来实时预览缩放结果。

核心场景：当你有一个预制的网格资产，需要将其尺寸调整为另一个比例，但又不想简单地进行非均匀缩放（会导致法线、碰撞等问题），而是希望得到一个几何上正确的、适配新尺寸的网格。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [MeshResizingCore](MeshResizingCore.md) | Runtime | 核心数据结构与基础类型定义 |
| [MeshResizingEditorTools](MeshResizingEditorTools.md) | Runtime | 编辑器中的交互式工具（绘制、套索选择等） |
| [MeshResizingEngine](MeshResizingEngine.md) | Runtime | 网格缩放算法引擎，执行实际的几何计算 |
| [MeshResizingDataflowNodes](MeshResizingDataflowNodes.md) | Runtime | Dataflow 节点，用于在 Dataflow 图中构建缩放管线 |

## 使用场景

- 你有一个角色模型，需要将其适配到不同体型的骨骼 → 用 MeshResizing 进行拓扑保持的缩放
- 你需要批量处理一批道具网格，将其统一调整到新的比例标准 → 通过 Dataflow 节点构建批处理管线
- 你需要对网格的局部区域进行交互式缩放编辑 → 使用绘制工具和套索选择精细控制缩放区域

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Tests)