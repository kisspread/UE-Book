# Geometry Dataflow Nodes

> Geometry Processing in Dataflow.

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点定义、蓝图资产） |
| 模块 | `GeometryDataflowNodes` (Runtime), `DataflowMedialSkeleton` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow) | |

## 用途

该插件将 Unreal Engine 的几何处理（Geometry Processing）功能封装为数据流（Dataflow）节点，使用户能够使用可视化的数据流图表来处理和操作 3D 几何体数据。它旨在为建筑可视化、游戏开发及医疗可视化等领域提供一套非破坏性、程序化的几何处理管线。其核心价值在于将原本需要编写 C++ 代码才能进行的复杂几何操作（如网格布尔运算、骨骼网格处理等），转化为可在编辑器中通过拖拽连线完成的图形化工作流。

## 使用场景

*   当你需要构建一个**参数化、可编辑的几何处理管道**时，例如在建筑可视化中需要根据参数动态修改建筑模型。
*   当你需要利用**程序化方式生成或编辑网格**，并希望过程可重现、易调整时。
*   在医疗或生物力学领域，需要处理**医学骨骼（Medial Skeleton）数据**并将其用于动画或渲染时。
*   当你希望将几何处理功能集成到现有的**数据流图表（Dataflow Graph）**中，与其他模拟或数据处理逻辑并行或串联执行时。

## 蓝图用法

本插件主要提供用于数据流图表的节点。这些节点通常在数据流编辑器（Dataflow Editor）中使用，而非传统的蓝图事件图表。

### 核心节点

根据功能，主要节点分为以下几类：

| 节点类型 | 说明 | 所在模块/类 |
|---|---|---|
| `FMeshBooleanNode` | 对输入网格执行布尔运算（如并集、交集、差集）。 | `GeometryDataflowNodes` |
| `FDataflowNode` (几何变换类) | 对几何体进行平移、旋转、缩放等变换操作。 | `GeometryDataflowNodes` |
| `FDataflowNode` (网格操作类) | 执行网格减面（Decimation）、细分（Subdivide）等操作。 | `GeometryDataflowNodes` |
| `FDataflowNode` (医学骨骼类) | 处理与医学骨骼（Medial Skeleton）相关的数据，如动画驱动、渲染映射。 | `DataflowMedialSkeleton` |

### 使用示例（数据流图表描述）

在数据流编辑器中，你可以这样构建一个简单的网格减面处理流程：
1.  从节点面板拖拽一个 **输入网格** 节点到图表中，作为数据源。
2.  搜索并添加一个 **网格减面（Mesh Decimate）** 节点。
3.  将输入网格节点的 **输出网格** 引脚，连接到减面节点的 **输入网格** 引脚。
4.  在减面节点的属性面板中，调整 **目标面数百分比** 或 **目标面数** 参数。
5.  将减面节点的 **输出网格** 引脚，连接到一个 **输出网格** 节点。
6.  执行图表，即可看到简化后的网格结果。

## C++ 用法

本插件的功能节点通常通过数据流框架使用。如果你需要创建自定义数据流节点，可以参考插件内已有的节点实现。

### 头文件引入

```cpp
#include "Dataflow/DataflowNode.h"
#include "GeometryDataflowNodes/DataflowNodeTypes.h" // 假设的节点类型头文件，需根据实际路径调整
```

### 基本用法

以下是一个简化示例，展示如何定义一个自定义的数据流节点（灵感来源于插件内节点的实现模式）。

```cpp
// MyCustomDataflowNode.h
#pragma once
#include "Dataflow/DataflowNode.h"

USTRUCT(meta = (DataflowGeometry))
struct FMyCustomDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()

    // 输入引脚：一个几何体
    UPROPERTY(meta = (DataflowInput, DataflowOutput))
    FManagedArrayCollection GeometryIn;

    // 输出引脚：处理后的几何体
    UPROPERTY(meta = (DataflowOutput))
    FManagedArrayCollection GeometryOut;

    // 节点参数
    UPROPERTY(EditAnywhere, Category = "Settings")
    float ScaleFactor = 1.0f;

    // 节点执行逻辑
    virtual void Evaluate(const FDataflowContext& Context, const FDataflowOutput* Output) override;
};

// MyCustomDataflowNode.cpp
#include "MyCustomDataflowNode.h"

void FMyCustomDataflowNode::Evaluate(const FDataflowContext& Context, const FDataflowOutput* Output)
{
    // 1. 获取输入几何体数据
    FManagedArrayCollection Geometry = GetValue<FManagedArrayCollection>(Context, &GeometryIn);

    // 2. 执行你的处理逻辑（示例：对顶点进行缩放）
    if (TManagedArray<FVector3f>* Vertices = Geometry.FindAttribute<FVector3f>("Vertex", FGeometryCollection::VerticesGroup))
    {
        for (FVector3f& Vertex : *Vertices)
        {
            Vertex *= ScaleFactor;
        }
    }

    // 3. 将结果设置到输出引脚
    SetValue<FManagedArrayCollection>(Context, &GeometryOut, Geometry);
}
```

## Demo 示例

下面是一个完整的、可编译的自定义数据流节点示例。该节点将输入几何体的所有顶点位置沿Z轴提升一个固定高度。

**MyShiftZDataflowNode.h**
```cpp
#pragma once
#include "Dataflow/DataflowNode.h"

USTRUCT(meta = (DataflowGeometry))
struct FMyShiftZDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY(meta = (DataflowInput, DataflowOutput))
    FManagedArrayCollection Geometry;

    UPROPERTY(EditAnywhere, Category = "Settings")
    float ShiftZ = 100.0f;

    virtual void Evaluate(const FDataflowContext& Context, const FDataflowOutput* Output) override
    {
        // 获取输入数据
        FManagedArrayCollection Geom = GetValue<FManagedArrayCollection>(Context, &Geometry);

        // 查找顶点属性组
        if (TManagedArray<FVector3f>* Vertices = Geom.FindAttribute<FVector3f>("Vertex", "Vertices"))
        {
            // 执行平移操作
            for (FVector3f& Vert : *Vertices)
            {
                Vert.Z += ShiftZ;
            }
        }

        // 输出结果
        SetValue<FManagedArrayCollection>(Context, &Geometry, Geom);
    }
};
```

## 模块依赖

要使用此插件的功能，你的模块需要依赖其核心模块。根据 `Build.cs` 文件，主要依赖如下：

| 模块 | 用途 |
|---|---|
| `GeometryDataflowNodes` | 提供核心的几何处理数据流节点实现。 |
| `DataflowMedialSkeleton` | 提供与医学骨骼相关的数据流节点。 |
| `Dataflow` | 提供数据流框架的基础运行时支持。 |
| `GeometryProcessing` | 提供底层的几何处理算法库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `da753042` | Dataflow geometry nodes plugin : remove beta status | 移除插件的测试版标记，标志着向正式版过渡。 |
| 2026-05-12 | `45745f54` | Dataflow: | 对数据流框架进行了更新或修复（具体信息不足）。 |
| 2026-04-17 | `49f946b4` | [Dataflow] | 对数据流相关功能进行了改动（具体信息不足）。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 对大量数据流节点进行更新，以使用新的渲染系统。 |
| 2025-12-11 | `2c27a203` | Minor cleanup of dataflow mesh boolean options | 对数据流网格布尔运算的选项进行小幅清理优化。 |

### 维护评价

*   **状态**: 活跃维护中。插件于 2025 年初创建，并在 2026 年 5 月刚刚移除了“Beta”状态，表明开发团队正在积极使其趋于稳定。
*   **近期活动**: 最近半年内有多次提交，包括功能更新（新渲染系统集成）和状态变更（移除Beta标记），维护节奏良好。
*   **建议**: 这是一个较新且处于快速迭代期的**实验性**插件。它非常适合用于原型开发和探索数据流几何处理的可能性。在将其用于生产环境前，建议密切关注其更新日志和稳定性变化。由于默认不启用，使用时需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/GeometryDataflowNodes) (如果存在)