# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格体缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

这是一个**实验性插件**，其核心功能是提供**基于节点化（Dataflow）的网格体几何编辑与缩放**能力。它不仅仅进行简单的缩放，而是提供了一套在编辑器和运行时对网格体顶点进行程序化操作和非均匀调整的工具。该插件是虚幻引擎中用于复杂网格体变形和资产处理的新工作流的一部分。

## 使用场景

- 你需要程序化地调整或变形静态网格体，而非简单的等比缩放。
- 你想使用可视化的节点图（Dataflow）来构建网格体处理逻辑。
- 你在开发需要动态调整角色或物体轮廓的系统（如角色创建、装备适配）。
- 你需要批量或通过蓝图资产来处理网格体几何数据。

## 模块列表

- **MeshResizingCore**: 提供网格体缩放的核心数据结构、数学计算和基础功能库。
- **MeshResizingEngine**: 包含用于处理网格体缩放操作的运行时引擎逻辑和计算内核。
- **MeshResizingEditorTools**: 提供编辑器内的专用工具、资产类型和编辑界面。
- **MeshResizingDataflowNodes**: 包含用于在 Dataflow 图中构建网格体缩放和操作逻辑的节点。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 节点相关更新。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将进行的头文件清理前添加必要的头文件包含。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow：为画笔工具添加套索支持，利用网格体中的新功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：将大量节点更新为使用新的渲染系统。 |

### 维护评价

该插件**创建时间较晚（2024年12月）**，目前处于**实验性阶段（IsExperimentalVersion=true）**，默认不启用。从近期提交记录（最后一次为2026年5月）来看，**仍在活跃开发中**，更新频率较高，主要围绕其核心的 Dataflow 节点功能进行增强和修复。

由于其实验性质，API和功能可能随时发生重大变化，不建议在关键生产项目中使用。它适合作为技术预览，用于探索基于节点的网格体程序化处理流程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]() (暂无)