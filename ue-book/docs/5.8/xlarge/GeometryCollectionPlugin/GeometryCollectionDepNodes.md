# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合插件 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图标资源） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

GeometryCollectionPlugin 是 UE5 Chaos Destruction 系统的核心数据基础设施。它提供了一种基于 `FManagedArrayCollection` 的容器，用于存储和管理可破坏几何体的所有数据——包括顶点、三角形、变换层级、骨骼映射、物理属性等。

这个插件解决的核心问题是：**如何将一个复杂网格体拆分为多个独立的物理碎片，并以高效的数据结构统一管理它们的拓扑关系、变换层级和属性数据。** 它是 Chaos Destruction 中 GeometryCollectionComponent 的底层数据引擎。

插件包含五个模块，分别负责：
- **GeometryCollectionNodes**：核心的 Dataflow 处理节点（几何体操作）
- **GeometryCollectionDepNodes**：已废弃（5.5 起）的 Dataflow 节点（属性传递、顶点着色等）
- **GeometryCollectionEditor**：编辑器内可视化和操作工具
- **GeometryCollectionSequencer**：Sequencer 关键帧支持
- **GeometryCollectionTracks**：动画轨道集成

> ⚠️ **重要提示**：`GeometryCollectionDepNodes` 模块中的节点已全部标记为 `Deprecated = "5.5"`，在 UE 5.5 及以后版本中应使用替代节点。

## 使用场景

- 你需要制作可破坏的建筑物/物体，碎裂成多个物理碎片 → 使用 GeometryCollection + Chaos Destruction
- 你需要通过 Dataflow 图处理几何体数据（属性传递、顶点选择、着色）→ 使用此插件的 Dataflow 节点
- 你需要在 Sequencer 中动画控制破坏过程 → 使用 GeometryCollectionSequencer 模块
- 你需要自定义碎裂方式（Voronoi 分割、平面切割等）→ 使用 GeometryCollectionNodes 的 Dataflow 图

## 蓝图用法

此插件主要通过 Dataflow 图（编辑器中的节点图）工作，而非传统的蓝图节点。以下是从源码中提取的核心数据流节点。

### 核心 Dataflow 节点（已废弃，UE 5.5 前可用）

以下节点均位于 `GeometryCollectionDepNodes` 模块，已在 UE 5.5 废弃：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TransferVertexScalarAttribute` | 将浮点属性从源集合传递到目标集合（支持距离衰减、BVH 加速） | `FGeometryCollectionTransferVertexScalarAttributeNode` |
| `SetVertexColorInCollectionFromVertexSelection` | 根据顶点选择集设置顶点颜色 | `FSetVertexColorInCollectionFromVertexSelectionDataflowNode` |
| `SetVertexColorInCollectionFromFloatArray` | 根据浮点数组设置顶点颜色 | `FSetVertexColorInCollectionFromFloatArrayDataflowNode` |

### 属性传递节点参数

`TransferVertexScalarAttribute` 节点提供以下可配置参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `BoundingVolumeType` | Enum | 边界体类型：Vertex（基于顶点）或 Triangle（基于三角形） |
| `SampleScale` | Enum | BVH 单元格大小：Component Edge / Asset Edge / Asset Bound |
| `Falloff` | Enum | 距离衰减模式：Squared（平方衰减）/ Linear（线性）/ None（无衰减） |
| `FalloffThreshold` | float | 衰减阈值，默认 0.01（三角形尺寸的 1%） |
| `EdgeMultiplier` | float | 边长乘数，控制 BVH 搜索半径 |
| `BoundMultiplier` | float | 包围盒乘数，控制 BVH 搜索半径 |

### Dataflow 图使用示例

在 Dataflow 编辑器中：

1. 创建一个 `Collection Input` 节点作为数据源
2. 添加 `TransferVertexScalarAttribute` 节点，连接源集合和目标集合
3. 指定 `AttributeKey` 来选择要传递的属性
4. 调整 `Falloff` 和 `Threshold` 控制传递精度
5. 输出连接到 `Collection Output`

对于顶点着色工作流：

1. 使用 `Vertex Selection` 节点选择目标顶点
2. 连接到 `SetVertexColorInCollectionFromVertexSelection`
3. 设置 `SelectedColor` 和 `NonSelectedColor` 参数

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCollectionDepNodesPlugin.h"
#include "Dataflow/GeometryCollectionTransferVertexScalarAttributeDepNode.h"
#include "Dataflow/SetVertexColorFromVertexSelectionDepNode.h"
#include "Dataflow/SetVertexColorFromFloatArrayDepNode.h"
```

### 基本用法

Dataflow 节点通过 `Evaluate` 方法在图执行时被调用。以下展示了如何程序化操作几何体集合的属性传递：

```cpp
// 创建几何体集合和 Dataflow 上下文
FManagedArrayCollection SourceCollection;
FManagedArrayCollection TargetCollection;

// 设置属性键以指定要传递的属性
FCollectionAttributeKey AttributeKey;
AttributeKey.Group = "Vertices";
AttributeKey.Attribute = "MyScalarAttribute";

// 配置传递节点参数
// 注意：此节点已在 UE 5.5 废弃
FGeometryCollectionTransferVertexScalarAttributeNode TransferNode(Parameters);

// 配置边界体和衰减参数
TransferNode.BoundingVolumeType = EDataflowTransferNodeBoundingVolume::Dataflow_Transfer_Triangle;
TransferNode.SampleScale = EDataflowTransferNodeSampleScale::Dataflow_Transfer_Asset_Bound;
TransferNode.Falloff = EDataflowTransferNodeFalloff::Dataflow_Transfer_Squared;
TransferNode.FalloffThreshold = 0.01f;

// 执行评估（通过 Dataflow 图执行引擎调用）
// TransferNode.Evaluate(Context, Output);
```

### 进阶用法

理解 `FGeometryCollectionTransferVertexScalarAttributeNode` 的内部机制：

```cpp
// 源码中的传递流程（来自 Evaluate 实现）

// 1. 建立源几何体到目标几何体的映射
TArray<FIntVector2> GeometryMap = TransferNode.FindSourceToTargetGeometryMap(
    SourceCollection, TargetCollection);

// 2. 根据是否有几何体对应关系，选择传递策略
if (GeometryMap.Num() > 0)
{
    // 已配对几何体：通过三角形-顶点交集传递
    TransferNode.PairedGeometryTransfer(
        AttributeKey, GeometryMap, SampleFacade, TargetFacade, TargetFloatArray);
}
else
{
    // 未配对几何体：最近顶点传递
    TransferNode.NearestVertexTransfer(
        AttributeKey, SampleFacade, TargetFacade, TargetFloatArray);
}

// 3. 内部使用 BVH 加速空间查询
// BuildParticleSphereBVH 根据顶点和搜索半径构建加速结构
UE::Private::BVH* BVH = FGeometryCollectionTransferVertexScalarAttributeNode
    ::BuildParticleSphereBVH(ComponentSpaceVertices, SearchRadius);

// 4. 三角形到顶点的相交检测
TArray<int32> IntersectedVertices;
FGeometryCollectionTransferVertexScalarAttributeNode
    ::TriangleToVertexIntersections(*BVH, ComponentSpaceVertices, Triangle, IntersectedVertices);

// 5. 距离衰减计算
float FalloffScale = FGeometryCollectionTransferVertexScalarAttributeNode
    ::CalculateFalloffScale(
        EDataflowTransferNodeFalloff::Dataflow_Transfer_Squared,
        Threshold, Distance);
```

## Demo 示例

以下展示如何自定义一个 Dataflow 节点来操作几何体集合：

```cpp
// MyGeometryCollectionNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"

/**
 * 自定义几何体集合处理节点
 * 演示如何创建一个简单的顶点偏移节点
 */
USTRUCT()
struct FMyVertexOffsetNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyVertexOffsetNode, "VertexOffset", "GeometryCollection", "Offset vertices by a vector")

public:
    /** 输入/输出的几何体集合 */
    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    /** 偏移向量 */
    UPROPERTY(EditAnywhere, Category = "Offset")
    FVector Offset = FVector(0, 0, 100.0);

    FMyVertexOffsetNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterInputConnection(&Offset);
        RegisterOutputConnection(&Collection, &Collection);
    }

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyGeometryCollectionNode.cpp
#include "MyGeometryCollectionNode.h"

void FMyVertexOffsetNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 获取输入数据
    FManagedArrayCollection CollectionData = Context.GetValue<FManagedArrayCollection>(this, Collection);
    const FVector OffsetValue = Context.GetValue<FVector>(this, Offset);

    // 获取顶点位置数组
    if (TManagedArray<FVector3f>* Vertices = CollectionData.FindAttribute<FVector3f>(
            "Vertex", FGeometryCollection::VerticesGroup))
    {
        // 对每个顶点应用偏移
        for (int32 i = 0; i < Vertices->Num(); ++i)
        {
            FVector3f CurrentPos = (*Vertices)[i];
            (*Vertices)[i] = CurrentPos + FVector3f(OffsetValue);
        }
    }

    // 输出修改后的集合
    Context.SetValue<FManagedArrayCollection>(this, CollectionData, Out);
}
```

## 模块依赖

基于 Dataflow 节点的代码模式和 `FManagedArrayCollection` 的使用，此插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionCore` | 核心几何体集合数据结构（`FManagedArrayCollection`、`TManagedArray`） |
| `Dataflow` | Dataflow 图引擎框架（`FDataflowNode`、`FContext`） |
| `DataflowEngine` | Dataflow 图执行引擎 |
| `Chaos` | Chaos 物理求解器（用于底层物理模拟） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化警告 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 节点相关更新 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退之前的一次提交 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 节点相关更新 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增为几何体集合创建外部碰撞的 Dataflow 节点 |

### 维护评价

**综合评价：活跃维护，但实验性状态持续**

- **创建时间**：2018 年，已有约 8 年历史，最初从物理引擎开发分支（Dev-Physics）引入
- **活跃度**：近期（2026 年 5 月）仍有功能性更新，包括新 Dataflow 节点的添加和 UE 5.8 适配
- **实验性**：始终标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，需要手动启用
- **废弃风险**：`GeometryCollectionDepNodes` 模块中的所有节点已标记为 `Deprecated="5.5"`，核心功能已迁移至引擎内置模块
- **推荐使用**：对于新项目，应优先使用引擎内置的 GeometryCollection 功能（GeometryCollectionCore / GeometryCollectionEngine / GeometryCollectionSimulationCore）。此实验插件主要提供额外的 Dataflow 处理节点，适合需要自定义几何体数据流处理的高级用户

> ⚠️ 此插件持续保持"实验性"标签长达 8 年。核心 GeometryCollection 容器功能已集成到引擎主体中，此插件更多作为 Dataflow 扩展节点的载体存在。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- 官方文档：（无）