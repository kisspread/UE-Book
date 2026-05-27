# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（网格资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

该插件提供在编辑器中对网格资产进行动态、非均匀缩放的核心框架与工具。它旨在解决在不修改原始资产数据的前提下，运行时或编辑时对网格进行尺寸调整的需求，适用于程序化内容生成、动态场景布置等场景。插件通过模块化设计，将核心算法、引擎集成、编辑器交互和数据流节点分离，便于扩展和维护。

## 使用场景

- 你需要在运行时根据游戏逻辑动态调整场景中物体的大小。
- 你需要在编辑器中对一批网格资产进行快速、非破坏性的尺寸调整。
- 你需要在 Dataflow 工具中创建复杂的网格变形与缩放管线。

## 模块概述

| 模块 | 类型 | 说明 |
|---|---|---|
| `MeshResizingCore` | Runtime | 核心算法与数据结构，提供网格缩放的基础计算与数据表示。 |
| `MeshResizingEditorTools` | Runtime | 编辑器工具与交互界面，为编辑器提供网格缩放的可视化操作与编辑功能。 |
| `MeshResizingEngine` | Runtime | 引擎运行时集成，负责将缩放后的网格数据提交给渲染与物理系统。 |
| `MeshResizingDataflowNodes` | Runtime | Dataflow 节点集合，提供可在 Dataflow 图中使用的网格缩放相关节点。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]() (暂无)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数而产生编译警告的问题。 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 模块更新（具体信息不足）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理前，预先添加必要的 include 指令。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 为 Dataflow 的绘制工具添加套索支持，利用了网格模块中的新功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 更新了大量 Dataflow 节点以使用新的渲染系统。 |

### 维护评价

该插件创建于 2024 年底，目前处于**活跃维护**状态。最近 1 年内有多次实质性功能更新（如 Dataflow 节点改进、编辑器工具增强），最近的提交集中在功能完善与编译问题修复。作为实验性插件，其 API 和功能可能仍在演变中，建议在评估后使用。