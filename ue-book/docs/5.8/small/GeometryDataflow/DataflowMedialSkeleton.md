# Geometry Dataflow Nodes

> Geometry Processing in Dataflow.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点资产） |
| 模块 | `GeometryDataflowNodes` (Runtime), `DataflowMedialSkeleton` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow) | |

## 用途

该插件旨在将几何处理功能（如网格布尔运算）集成到 Unreal Engine 的 **Dataflow（数据流）** 可视化脚本系统中。Dataflow 是一种基于节点的程序化内容创建系统，常用于模拟、动画和程序化生成。此插件通过提供专门的几何处理节点，让用户可以在 Dataflow 图中直接执行复杂的几何操作（如布尔、切割、平滑等），而无需编写 C++ 代码或切换到其他工具。

其核心解决的问题是：将 **GeometryProcessing** 模块的底层算法暴露给 Dataflow 的非程序员用户（如技术美术师、特效师），使他们能够以可视化、非破坏性的方式构建几何处理工作流。

## 使用场景

- 你需要在一个动态模拟或程序化生成的流程中，对生成的网格（Mesh）进行实时或近实时的布尔运算（如减去、合并）。
- 你正在使用 Dataflow 构建一个角色布料或物理资产的生成管线，需要在其中插入几何清理或优化步骤。
- 你想为技术美术师或关卡设计师提供一个可视化的工具，让他们能自己组合几何处理操作来创建独特的资产，而无需程序员介入。

## 蓝图用法

由于这是一个运行时模块，其节点主要在 Dataflow 图编辑器中使用，而非传统的蓝图图表。相关 API 集中在 Dataflow 节点定义中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshBoolean` | 执行两个网格之间的布尔运算（如并集、交集、差集）。这是插件创建初期迁移的首个核心节点。 | `UDataflowMeshBooleanNode` (推测，基于commit信息) |
| `FDataflowMedialSkeleton` | 表示一个中轴骨架（Medial Skeleton）数据结构，用于高级几何分析和变形。 | `FDataflowMedialSkeleton` |

### 使用示例（蓝图描述）

在 **Dataflow 编辑器** 中：
1.  打开或创建一个 Dataflow 图资产。
2.  在节点搜索菜单中，搜索 “Geometry” 或 “Mesh Boolean”。
3.  拖出一个 **Mesh Boolean** 节点。
4.  该节点通常有两个或多个输入（如 `Mesh A`， `Mesh B`）和一个输出（`Result Mesh`）。
5.  将其他生成网格的 Dataflow 节点（如 “Box” 或 “Sphere”）的输出，连接到该节点的输入。
6.  在节点的细节面板中，选择布尔操作类型（Union， Intersection， Difference）。
7.  将该节点的输出连接到下游需要使用结果网格的节点（如渲染或碰撞生成节点）。

## C++ 用法

该插件主要提供运行时模块，因此 C++ 用法通常涉及在自定义模块中依赖并使用其提供的数据结构和可能的函数。

### 头文件引入

```cpp
#include "DataflowMedialSkeleton.h" // 用于使用 FDataflowMedialSkeleton 结构体
#include "DataflowMedialSkeletonModule.h" // 模块接口
```

### 基本用法

主要数据结构是 `FDataflowMedialSkeleton`，它是一个 `USTRUCT`，用于包装底层的中轴骨架数据。
（来源文件：`Source/DataflowMedialSkeleton/Public/Dataflow/DataflowMedialSkeleton.h`）

```cpp
// 在代码中，你可能会在 Dataflow 节点或相关资产中遇到或使用这个结构体
FDataflowMedialSkeleton MySkeletonData;
// 该结构体内部持有 UE::Geometry::MedialAxis::FMedialSkeleton Skeleton;
// 具体的操作（如生成、修改）通常由 Dataflow 节点或 GeometryProcessing 模块完成。
```

## Demo 示例

以下是一个最简化的示例，展示了如何在代码中定义一个使用 `FDataflowMedialSkeleton` 结构体的简单 Dataflow 节点（概念性代码）。

**MySimpleSkeletonNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowNode.h"
#include "Dataflow/DataflowMedialSkeleton.h"
#include "MySimpleSkeletonNode.generated.h"

USTRUCT(meta = (DataflowTerminal))
struct FMySimpleSkeletonContext : public FDataflowContext
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY()
    FDataflowMedialSkeleton InputSkeleton;
};

UCLASS()
class UMySimpleSkeletonNode : public UDataflowNode
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Input")
    FDataflowMedialSkeleton SkeletonInput;

    UPROPERTY()
    FDataflowMedialSkeleton SkeletonOutput;

    virtual void Evaluate(const FDataflowContext& Context, FDataflowOutput& Output) override
    {
        // 此处可以对 SkeletonInput 进行处理，然后赋值给 SkeletonOutput
        SkeletonOutput = SkeletonInput;
        Output.SetPropertyValue(UE::Dataflow::TConnection<FDataflowMedialSkeleton>(SkeletonOutput));
    }
};
```

## 模块依赖

从 `Build.cs` 文件分析，使用此插件提供的功能，你的项目模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Dataflow` | 数据流系统的核心框架。 |
| `GeometryProcessing` | 提供底层的几何处理算法（如网格布尔运算）。 |
| `ModelingComponents` | 几何建模相关的组件和工具。 |
| `GeometryCore` | 几何处理的核心数学和数据结构。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `da753042` | Dataflow geometry nodes plugin : remove beta status | 移除了插件的“Beta”标记，表明其核心功能已趋于稳定。 |
| 2026-05-12 | `45745f54` | Dataflow: | （提交信息不完整）可能是对数据流系统的基础性更新。 |
| 2026-04-17 | `49f946b4` | [Dataflow] | （提交信息不完整）数据流相关的改进或修复。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 将大量数据流节点迁移到新的渲染系统，这是一次重大的内部更新。 |
| 2025-12-11 | `2c27a203` | Minor cleanup of dataflow mesh boolean options | 对网格布尔运算节点的选项进行了轻微清理和优化。 |

### 维护评价

**积极维护中**。该插件创建于 2025 年初，至今（约 1 年）保持着持续的更新。从提交历史看：
1.  **活跃开发**：最近一次更新（2026-05-14）直接移除了 Beta 状态，表明 Epic 认为其已达到可用标准，这是一个非常积极的信号。
2.  **功能迭代**：此前有针对新渲染系统的大量节点迁移（2025-12-19），说明其在不断适应引擎的底层架构变化。
3.  **问题修复**：有具体的清理和修复提交（2025-12-11）。
4.  **实验性**：虽然 `.uplugin` 中 `IsBetaVersion` 为 `false`，但它位于 `Experimental` 目录且 `EnabledByDefault` 为 `false`，用户需手动启用，这仍然符合“实验性”插件的特征。

**推荐使用**，特别是对于希望在 Dataflow 中利用几何处理能力的项目。但需注意其仍被标记为实验性，API 可能在未来版本中发生变化。建议在非核心生产管线中先行试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow)
- [官方文档]()（暂无）
- [测试用例]()（在提供的信息中未明确指定路径，通常可能位于 `Engine/Tests/` 或插件内部的 `Tests/` 目录下）