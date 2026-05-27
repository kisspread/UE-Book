# PCG Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区PCG互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件为 **PCG（程序化内容生成框架）** 和 **Mesh Partition（网格分区系统）** 之间建立互操作层。通过此插件，PCG 图表节点能够调用网格分区功能，实现程序化地形分区烘焙、网格属性处理等操作。典型场景是大规模程序化地形生成中，将 PCG 流程与网格地形切片（Mesh Terrain Section）的烘焙管线打通，使得程序化生成的地块可以高效地分区和烘焙到运行时网格中。

## 使用场景

- 你使用 PCG 框架程序化生成大规模地形，需要将生成结果分区烘焙为网格地形切片 → 用此插件
- 你需要在 PCG 图表中执行 BakeMeshAttr / BakeMeshTerrainSection 等网格分区操作 → 用此插件
- 你希望 PCG 流程与 Geometry Script 管线协同工作来处理网格分区 → 用此插件（依赖 PCGGeometryScriptInterop）

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [PCGMeshPartitionInterop](PCGMeshPartitionInterop.md) | Runtime | 核心运行时模块，提供 PCG 与网格分区的互操作逻辑和数据类型 |
| [PCGMeshPartitionInteropEditor](PCGMeshPartitionInteropEditor.md) | Editor | 编辑器模块，提供 PCG 节点、节点设置等编辑器集成 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 程序化内容生成框架核心 |
| `MeshPartition` | 网格分区运行时功能 |
| `PCGGeometryScriptInterop` | PCG 与 Geometry Script 的互操作层 |

> 该插件需要同时启用 `PCG`、`MeshPartition` 和 `PCGGeometryScriptInterop` 三个前置插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复烘焙网格属性/地形切片读取无效RHI资源时的崩溃 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增烘焙网格地形切片节点 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断为浮点的警告 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | Get Mesh Terrain Section 节点中跟踪最终层键以在修改器变更时刷新 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复将压缩纹理绑定为UAV导致的GPU崩溃 |

### 维护评价

- **活跃维护中**：近一个月内有多次功能性更新和 bug 修复，开发节奏密集
- 创建仅约 2 个月，属于新晋实验性插件
- 标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能随时变更
- 近期修复涉及 GPU 崩溃、RHI 资源读取等底层问题，说明仍处于早期打磨阶段
- **建议**：可在实验项目中尝试，但不建议用于生产环境

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档 - PCG 框架](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- 运行时模块文档：[PCGMeshPartitionInterop](PCGMeshPartitionInterop.md)
- 编辑器模块文档：[PCGMeshPartitionInteropEditor](PCGMeshPartitionInteropEditor.md)