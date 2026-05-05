# DataflowVolumetric

> Adds volumetric support to Dataflow

| 属性 | 值 |
|---|---|
| 分类 | Dataflow |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（体积化资产/节点） |
| 模块 | `DataflowVolumeCore` (Editor), `DataflowVolumeNodes` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DataflowVolumetricPlugin) | |

## 用途

本插件为 Unreal Engine 的 **Dataflow**（数据流）系统扩展了**体积化（Volumetric）** 数据处理能力。它并非一个独立的渲染或物理系统，而是作为 Dataflow 框架的扩展，允许用户在数据流图中创建、操作和评估与体积相关的数据（如体素网格、SDF 等）。其核心目标是将复杂的体积数据生成与处理流程，通过 Dataflow 的节点化、可编程方式进行封装和可视化，从而简化程序化内容生成（PCG）或科学计算中涉及体积数据的工作流。

## 使用场景

-   **程序化地形与环境生成**：在 Dataflow 图中，使用体积节点生成高度场、密度场或侵蚀模拟数据，再将其转换为网格或用于材质驱动。
-   **体积特效与模拟**：构建用于驱动体积雾、火焰、云层等视觉效果的底层数据流。
-   **数据可视化与分析**：将科学计算或仿真产生的三维标量/矢量场数据，通过 Dataflow 节点进行处理、过滤和可视化。
-   **自定义体积资产创建**：在编辑器中通过节点图程序化地创建和编辑体积纹理（Volume Texture）或稀疏体积纹理（Sparse Virtual Texture）资产。

## 模块列表

本插件包含两个核心模块，共同构成体积化数据流的基础：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [`DataflowVolumeCore`](DataflowVolumeCore.md) | Editor | 提供体积数据在 Dataflow 框架中的核心类型定义、评估上下文和基础操作接口。 |
| [`DataflowVolumeNodes`](DataflowVolumeNodes.md) | Editor | 包含一系列具体的 Dataflow 节点，用于创建、转换和操作各种体积数据。 |

### 近期更新

- 2026-04-17 `49f946b4` [Dataflow]
- 2026-01-27 `bc6b71b7` Dataflow:
- 2026-01-24 `fa3617d8` [Backout] - CL50148102
- 2026-01-24 `b815c490` Dataflow:
- 2026-01-24 `67495252` Dataflow:

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DataflowVolumetricPlugin)
-   [Dataflow 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Dataflow) (前置依赖)