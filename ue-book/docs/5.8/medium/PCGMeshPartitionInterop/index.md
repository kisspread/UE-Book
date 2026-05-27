# Procedural Content Generation Framework (PCG) Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件为 Unreal Engine 的程序化内容生成框架 (PCG) 与网格分区 (Mesh Partition) 插件之间提供了互操作性。它允许在 PCG 图表中直接使用网格分区功能，从而在程序化生成大型、复杂世界场景时，能够对生成的网格资产进行高效的分区、管理和优化。其核心价值在于将两个独立但相关的强大系统（PCG 和 Mesh Partition）连接起来，扩展了程序化工作流的能力边界。

## 使用场景

-   **大型开放世界场景生成**：使用 PCG 程序化生成地形、植被、建筑等元素后，需要将生成的静态网格体进行分区，以优化运行时性能和内存管理。
-   **动态内容流式加载**：结合 PCG 的动态生成能力与网格分区的空间划分，实现更精细的流式加载策略。
-   **资产管线集成**：在 PCG 工作流中，需要调用网格分区插件提供的特定功能（如网格合并、LOD 生成等）来处理程序化生成的资产。

## 蓝图用法

本插件主要提供 PCG 节点和数据类型，用于在 PCG 图表中集成网格分区操作。核心功能通过 PCG 节点暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Partition Mesh` | 将输入的网格体资产进行分区处理。 | `UPCGMeshPartitionSettings` |
| `Merge Partitions` | 将多个分区后的网格体合并。 | `UPCGMeshPartitionSettings` |

*详细节点参数与数据类型，请参阅模块文档 [PCGMeshPartitionInterop.md](PCGMeshPartitionInterop.md)。*

### 使用示例（蓝图描述）

在 PCG 图表中，创建一个 `Partition Mesh` 节点。将其输入连接到一个生成静态网格体资产的节点（例如 `Create Static Mesh`）。在 `Partition Mesh` 节点的细节面板中配置分区参数（如分区大小、LOD 设置等）。其输出可连接到后续的 `Merge Partitions` 节点或直接输出到场景。

## C++ 用法

本插件主要通过 PCG 节点和设置类进行扩展，C++ 用法通常涉及自定义 PCG 节点或与现有设置类交互。

### 头文件引入

```cpp
#include "PCGMeshPartitionInterop/PCGMeshPartitionSettings.h"
```

### 基本用法

创建并配置一个网格分区设置对象，用于在 PCG 图表外部或自定义节点中调用分区功能。
```cpp
// 创建一个网格分区设置实例
UPCGMeshPartitionSettings* PartitionSettings = NewObject<UPCGMeshPartitionSettings>();

// 配置分区参数（示例）
PartitionSettings->PartitionSize = FVector(1000.f, 1000.f, 1000.f);
PartitionSettings->bGenerateLODs = true;

// 假设你有一个 UStaticMesh* MeshToPartition
// 调用分区功能（具体函数需参考模块文档）
// PartitionSettings->PartitionMesh(MeshToPartition);
```
*（代码为示意，具体函数签名与用法请参考 [PCGMeshPartitionInterop.md](PCGMeshPartitionInterop.md)）*

## Demo 示例

一个最小的 PCG 图表示例，演示如何将一个程序化生成的网格体进行分区：
1.  使用 `Create Static Mesh` 节点生成一个网格体。
2.  连接 `Partition Mesh` 节点，并设置合理的分区尺寸。
3.  将 `Partition Mesh` 的输出连接到 `Output` 节点，或连接到 `Merge Partitions` 节点进行合并后再输出。

## 模块依赖

本插件依赖于以下其他插件，你的项目需要启用它们：

| 插件 | 用途 |
|---|---|
| `PCG` | 核心的程序化内容生成框架。 |
| `MeshPartition` | 提供网格分区的核心功能。 |
| `PCGGeometryScriptInterop` | 提供 PCG 与 Geometry Script 的互操作性，本插件可能依赖其基础结构。 |

*你的模块在使用本插件功能时，通常需要依赖 `PCGMeshPartitionInterop` 模块。*

## 维护状态

### 近期更新

- 2026-04-16 `445f07c6` [Mesh Partition]
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-27 `71c13324` Fixed localization warnings
- 2026-03-20 `4f6ea1be` [Mesh Partition]
- 2026-03-05 `29f7cf7b` [Mesh Partition]

### 维护评价

-   **创建时间**：2026年3月，非常新的插件。
-   **实验性状态**：`IsExperimentalVersion=true`，表明该插件仍处于实验阶段，API 和功能可能发生变化。
-   **维护评价**：作为实验性插件，其稳定性和长期支持存在不确定性。适合用于原型开发和功能探索，但不建议在需要长期稳定维护的生产项目中作为核心依赖。
-   **推荐使用**：如果你的项目需要深度集成 PCG 和网格分区功能，并且可以接受实验性 API 的潜在变动，可以尝试使用。否则，建议关注其后续版本或寻找替代方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
-   [官方文档 (PCG)](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
-   **模块文档**:
    -   [PCGMeshPartitionInterop.md](PCGMeshPartitionInterop.md) (Runtime 模块)
    -   [PCGMeshPartitionInteropEditor.md](PCGMeshPartitionInteropEditor.md) (Editor 模块)