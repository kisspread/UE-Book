# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合插件 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

Geometry Collection Plugin 是 Chaos 物理破坏系统的核心组成部分，负责**几何集合（Geometry Collection）** 的创建、编辑、数据处理与运行时支持。几何集合是一种用于高效模拟破碎、断裂、堆叠等物理效果的数据容器，它将多个碎块（Chunks）的几何体、材质、物理属性及层级关系整合为一个统一的集合资源。

该插件提供了：

- 一套完整的**数据流（Dataflow）节点**，允许用户以程序化管线方式定义几何集合的生成逻辑，包括属性转移、颜色设置、选择集操作、变换处理等。
- 编辑器的**几何集合编辑器**，用于预览、调整和构建几何集合资源。
- **关卡序列（Sequencer）集成**，支持在过场动画中控制几何集合的激活、隐藏、变换等。
- **运行时**模块，负责加载和释放几何集合数据，供 Chaos 物理解算器使用。

本模块 `GeometryCollectionDepNodes` 专门包含**已废弃的旧版数据流节点**（标记 `Deprecated = "5.5"`），这些节点曾用于早期的几何集合工作流。尽管功能已被更稳定高效的新节点取代，但旧节点仍保留以兼容旧版数据流图。主要功能包括：

- 从源几何集合向目标几何集合**转移**顶点标量属性（如重量、温度等），并支持基于距离的衰减和包围体层次（BVH）采样策略。
- 根据输入浮点数组**设置**集合的顶点颜色。
- 根据选定的顶点选择集**设置**集合的顶点颜色，以视觉高亮所选顶点。

这些节点展示了数据处理的基本模式，可作为理解几何集合数据流机制的参考。

## 使用场景

- **程序化破碎资产生成**：利用数据流节点将高模网格转换为带有多层次碎块的几何集合，并为每块分配物理属性。
- **属性传递**：在多个几何集合间传递自定义顶点属性，例如从模拟中获得的温度值或破坏阈值。
- **调试可视化**：通过顶点颜色节点直观显示选择集或属性值，帮助定位数据问题。
- **过场动画中的破坏效果**：在 Sequencer 中启用几何集合的可见性或变换，配合物理解算制造动态破坏场景。

## 蓝图用法

该插件中的数据流节点**不能直接通过蓝图调用**，而是通过 **Dataflow 编辑器**中的节点图表使用。以下是节点列表及其功能说明，以供在 Dataflow Editor 中手动放置时参考。

### 核心节点

| 节点 | 说明 | 所在结构体 |
|---|---|---|
| `TransferVertexScalarAttribute` | 从源集合向目标集合转移指定名称的顶点浮点属性，支持 BVH 采样和衰减控制 | `FGeometryCollectionTransferVertexScalarAttributeNode` |
| `SetVertexColorInCollectionFromFloatArray` | 根据输入浮点数组（缩放后）设置集合的顶点颜色 | `FSetVertexColorInCollectionFromFloatArrayDataflowNode` |
| `SetVertexColorInCollectionFromVertexSelection` | 根据顶点选择集设置集合的顶点颜色（选择的部分为指定色，其余为另一颜色） | `FSetVertexColorInCollectionFromVertexSelectionDataflowNode` |

### 使用示例（蓝图描述）

**例 1：为碎块赋予随机颜色**
1. 添加 `SetVertexColorInCollectionFromFloatArrayDataflow` 节点。
2. 将生成好的随机浮点数组（如通过 `Make Random Float Array` 节点）连接到 `FloatArray` 输入。
3. 连接几何集合对象到 `Collection` 输入，并输出到下游节点。
4. 调整 `Scale` 参数控制颜色强度。

**例 2：高亮选定顶点**
1. 添加 `SetVertexColorInCollectionFromVertexSelectionDataflow` 节点。
2. 通过 `GetVertexSelection` 节点或手动指定选择集连接到 `VertexSelection` 输入。
3. 设置 `SelectedColor` 和 `NonSelectedColor`。
4. 输出集合即可在预览中看到颜色差异。

**例 3：从高模传递属性到低模碎块**
1. 添加 `TransferVertexScalarAttribute` 节点。
2. 目标集合（低模）连接到 `Collection`，源集合（高模）连接到 `FromCollection`。
3. 指定要传递的属性名（如 `"Temperature"`）到 `AttributeKey`。
4. 选择采样策略（顶点/三角形、衰减类型等）。
5. 输出处理后的目标集合。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/GeometryCollectionTransferVertexScalarAttributeDepNode.h"
#include "Dataflow/SetVertexColorFromFloatArrayDepNode.h"
#include "Dataflow/SetVertexColorFromVertexSelectionDepNode.h"
```

### 基本用法

以下示例展示了如何在 C++ 中构建并评估一个废弃的转移节点（用于兼容旧数据流图）。**不推荐在新代码中使用**，但可帮助理解节点内部机制。

```cpp
// 来源：Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionDepNodes/Private/Dataflow/GeometryCollectionTransferVertexScalarAttributeDepNode.h

// 创建节点实例（需要 Dataflow 上下文）
UE::Dataflow::FContext Context;
FGuid NodeId = FGuid::NewGuid();
UE::Dataflow::FNodeParameters Params(Context, NodeId);

FGeometryCollectionTransferVertexScalarAttributeNode TransferNode(Params);

// 准备源和目标集合（假设已有 FManagedArrayCollection 对象）
FManagedArrayCollection SourceCollection = /* ... */;
FManagedArrayCollection TargetCollection = /* ... */;

// 设置输入数据
FCollectionAttributeKey AttrKey("Temperature");
TransferNode.FromCollection = SourceCollection;
TransferNode.AttributeKey = AttrKey;
TransferNode.BoundingVolumeType = EDataflowTransferNodeBoundingVolume::Dataflow_Transfer_Triangle;
TransferNode.SampleScale = EDataflowTransferNodeSampleScale::Dataflow_Transfer_Asset_Bound;
TransferNode.Falloff = EDataflowTransferNodeFalloff::Dataflow_Transfer_Squared;

// 注册输入输出连接（简化，实际需要完整图评估框架）
TransferNode.RegisterInputConnection(&TransferNode.FromCollection);
TransferNode.RegisterInputConnection(&TransferNode.AttributeKey);
TransferNode.RegisterOutputConnection(&TransferNode.Collection, &TransferNode.Collection);

// 评估节点（输出将写入 TransferNode.Collection）
TransferNode.Evaluate(Context, &TransferNode.Collection);

// 读取结果
const auto& ResultCollection = TransferNode.Collection;
```

### 进阶用法

多个废弃节点可组合成简易管线，例如先通过浮点数组设置颜色，再选择特定顶点重新着色。

```cpp
// 假设已有集合 MyCollection 和选择集 VertexSelection

// 1. 创建颜色设置节点（基于浮点数组）
FSetVertexColorInCollectionFromFloatArrayDataflowNode ColorFromFloat(Params);
ColorFromFloat.Collection = MyCollection;
TArray<float> FloatVals = {1.0f, 0.5f, 0.2f, /* ... */};
ColorFromFloat.FloatArray = FloatVals;
ColorFromFloat.Scale = 2.0f;
ColorFromFloat.Evaluate(Context, &ColorFromFloat.Collection);

// 2. 再从选择集覆盖颜色
FSetVertexColorInCollectionFromVertexSelectionDataflowNode ColorFromSel(Params);
ColorFromSel.Collection = ColorFromFloat.Collection;
ColorFromSel.VertexSelection = VertexSelection;
ColorFromSel.SelectedColor = FLinearColor::Red;
ColorFromSel.NonSelectedColor = FLinearColor::Green;
ColorFromSel.Evaluate(Context, &ColorFromSel.Collection);

// 最终 MyCollection 被修改（注意：实际引用传递需谨慎）
```

## Demo 示例

以下是一个完整的最小 C++ 示例，展示如何在 GeometryCollectionDepNodes 中创建一个简单的数据流管线，利用废弃节点设置顶点颜色。

```cpp
// GeometryCollectionDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowEngine.h"
#include "Dataflow/SetVertexColorFromVertexSelectionDepNode.h"

class FGeometryCollectionDemo
{
public:
    void RunDemo();
};
```

```cpp
// GeometryCollectionDemo.cpp
#include "GeometryCollectionDemo.h"
#include "GeometryCollection/GeometryCollection.h"
#include "Dataflow/DataflowNode.h"
#include "Dataflow/DataflowContext.h"

void FGeometryCollectionDemo::RunDemo()
{
    // 1. 创建一个简单的几何集合（例如一个盒体）
    UGeometryCollection* GCollection = NewObject<UGeometryCollection>();
    // 初始化... 此处省略生成几何数据（通常从静态网格体转换而来）

    // 2. 设置 Dataflow 上下文和参数
    UE::Dataflow::FContext Context;
    FGuid NodeId = FGuid::NewGuid();
    UE::Dataflow::FNodeParameters Params(Context, NodeId);

    // 3. 构建顶点选择集（假设选择所有顶点）
    FDataflowVertexSelection Selection;
    Selection.SetAll(TArray<bool>(/*顶点数*/, true));

    // 4. 创建颜色设置节点
    FSetVertexColorInCollectionFromVertexSelectionDataflowNode ColorNode(Params);
    ColorNode.Collection = *GCollection->GetGeometryCollection(); // 获取 FManagedArrayCollection
    ColorNode.VertexSelection = Selection;
    ColorNode.SelectedColor = FLinearColor(0.0f, 1.0f, 0.0f); // 绿色
    ColorNode.NonSelectedColor = FLinearColor(0.0f, 0.0f, 1.0f); // 蓝色

    // 5. 评估节点
    ColorNode.Evaluate(Context, &ColorNode.Collection);

    // 6. 输出结果（此处简化为日志，实际可用作其他下游处理）
    UE_LOG(LogTemp, Log, TEXT("Vertex colors set. Collection modified."));
}
```

## 模块依赖

该模块 `GeometryCollectionDepNodes` 依赖于以下独特模块（省略标准 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `Dataflow` | 数据流节点框架，提供节点注册、连接与评估机制 |
| `GeometryCollection` | 几何集合数据容器（`FManagedArrayCollection`）及核心操作 |
| `Chaos` | 物理引擎，提供 BVH层次结构（`TBoundingVolumeHierarchy`）等底层结构 |
| `GeometryCollectionEngine` | 几何集合运行时引擎支持 |

注意：`GeometryCollectionDepNodes` 本身不直接依赖其他子模块，但若使用完整插件，其他模块可能有额外依赖。

## 维护状态

### 近期更新

- 2025-09-25 `745ebb56` Add support for override materials for geometry collection root proxies
- 2025-09-24 `787ab8b2` Geometry collection : add cvar to disable the dialog that ask to create a Dataflow graph when opening
- 2025-09-23 `29aa54b8` Dataflow : add settings for Dataflow editor
- 2025-09-16 `9a2a2477` Dataflow : fix Tetrahedron rendering crashing when the source collection was split in multiple geometries
- 2025-09-06 `38d85df2` dataflow : expose all properties of TransformCollection node as inputs

### 维护评价

- **创建时间**：2025-09-06（约 1 个月前）
- **近期更新频率**：几乎每天都有功能性更新和 Bug 修复，团队活跃。
- **活跃程度**：处于**活跃维护**状态，不仅修复问题，还在添加新功能（如根代理材质覆盖、编辑器设置）。
- **已知问题**：标记为 `IsBetaVersion=true`，表明仍可能有不稳定的部分。
- **推荐使用**：对于需要使用 Chaos 破坏系统的项目，强烈推荐启用。旧版废弃节点（`GeometryCollectionDepNodes`）不推荐在新数据流图中使用，但作为参考仍有价值。建议使用 `GeometryCollectionNodes` 模块中的新版节点。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档：几何集合概述](https://docs.unrealengine.com/5.7/en-US/geometry-collections-in-unreal-engine/)
- [测试用例（主仓库内）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/DataflowTests/Tests/GeometryCollection)