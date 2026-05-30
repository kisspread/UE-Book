# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | Groom数据流 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands 插件（通常称为 Groom 插件）是 Unreal Engine 中用于处理和渲染高精度头发、皮毛及其他基于曲线资产的核心系统。它提供了一整套解决方案，涵盖从资产导入、物理模拟、蒙皮绑定到最终渲染的完整管线。

**核心功能包括：**
1.  **Groom 资产管理**：处理以 `.groom` 格式导入的头发和皮毛数据，包含用于渲染的 Strands（发丝）和用于物理模拟的 Guides（引导线）。
2.  **物理模拟**：基于 Chaos 物理引擎，实现逼真的头发和皮毛动态效果。
3.  **蒙皮与变形**：支持将 Groom 数据绑定到骨骼网格体（Skeletal Mesh），实现随角色骨骼运动。
4.  **数据流（Dataflow）集成**：提供了专门的 `HairStrandsDataflow` 模块，允许用户通过可视化数据流图（Dataflow Graph）程序化地处理和转换 Groom 数据，例如自动计算蒙皮权重、生成LOD、重采样曲线等。

本模块 `HairStrandsDataflow` 是 Groom 数据处理流程的蓝图和数据流核心，它解决了在数据流工作流中程序化构建、修改和优化 Groom 资产数据的问题。

## 使用场景

- **程序化生成头发资产**：在游戏角色创建器或工具中，通过数据流节点动态生成不同发型的 Groom 数据。
- **自动化蒙皮权重计算**：为导入的 Groom 数据自动从指定的骨骼网格体转移蒙皮权重，实现快速绑定。
- **调整 Groom 曲线形状**：通过重采样、平滑、生成引导线等节点，优化 Groom 的几何形状，以适应不同的视觉或模拟需求。
- **构建 Groom 的LOD**：为 Groom 数据生成不同细节层次（LOD），优化渲染性能。
- **创建骨骼绑定系统**：根据 Groom 的引导线数据自动生成对应的骨骼（Joints）和骨骼网格体，用于更复杂的变形或控制系统。

## 蓝图用法

`HairStrandsDataflow` 模块的核心在于其提供的各种 **Dataflow 节点**，这些节点可在 Dataflow 图编辑器中使用，用于构建 Groom 数据处理管线。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGroomAsset` | 从资产引用中获取 Groom 资产对象。 | `FGetGroomAssetDataflowNode_v2` |
| `GroomAssetToCollection` | 将 Groom 资产转换为可被其他数据流节点处理的 `FManagedArrayCollection` 数据集合。 | `FGroomAssetToCollectionDataflowNode` |
| `GroomAssetTerminal` | 数据流图的终端节点，用于将处理后的数据集合写回到 Groom 资产中。 | `FGroomAssetTerminalDataflowNode_v2` |
| `AttachCurveRoots` | 通过设置曲线根部的运动学权重为1.0来“固定”曲线根部。 | `FAttachCurveRootsDataflowNode` |
| `BuildCurveWeights` | 根据指定的曲线权重分布，在每条曲线上构建权重图。 | `FBuildCurveWeightsDataflowNode` |
| `TransferLinearSkinWeights` | 从骨骼网格体的几何体上转移线性蒙皮权重到 Groom 曲线。 | `FTransferGeometrySkinWeightsDataflowNode` |
| `BuildSplineSkinWeights` | 从骨骼网格体构建样条蒙皮数据，用于更复杂的蒙皮方案。 | `FBuildSplineSkinWeightsDataflowNode` |
| `SplineToLinearSkinWeights` | 将样条蒙皮数据转换为线性蒙皮数据。 | `FSplineToLinearSkinWeightsDataflowNode` |
| `LinearToSplineSkinWeights` | 将线性蒙皮数据转换为样条蒙皮数据。 | `FLinearToSplineSkinWeightsDataflowNode` |
| `ResampleCurvePoints` | 使用固定数量的点对曲线进行重采样。 | `FResampleCurvePointsDataflowNode` |
| `SmoothCurvePoints` | 平滑曲线点，使模拟或变形更稳定。 | `FSmoothCurvePointsDataflowNode` |
| `BuildCurveLODs` | 为曲线构建细节层次（LOD）数据。 | `FBuildCurveLODsDataflowNode` |
| `GenerateCurveGeometry` | 从源曲线集合中生成新的曲线几何体。 | `FGenerateCurveGeometryDataflowNode` |
| `GetCurveAttributes` | 获取曲线数据集合中的特定属性（如运动学权重、骨骼索引等）的键值。 | `FGetCurveAttributesDataflowNode` |
| `GuidesToJoints` | 终端节点，根据引导线选择生成骨骼关节并保存为骨架和骨骼网格体资产。 | `FDataflowGuidesToJointsNode` |

### 使用示例（蓝图描述）

在 Dataflow 编辑器中，一个典型的处理流程如下：

1.  **获取数据**：拖入一个 `GetGroomAsset` 节点，并指定一个 `.groom` 资产。
2.  **转换格式**：连接 `GroomAssetToCollection` 节点，选择要处理的曲线类型（Strands 或 Guides），并设置曲线厚度。
3.  **处理数据**：串联多个处理节点，例如：
    *   使用 `AttachCurveRoots` 固定根部。
    *   使用 `ResampleCurvePoints` 调整曲线点数。
    *   使用 `TransferLinearSkinWeights` 并输入一个骨骼网格体来计算蒙皮权重。
    *   使用 `SmoothCurvePoints` 平滑曲线。
4.  **输出结果**：最后连接到 `GroomAssetTerminal` 节点，将处理后的数据集合（Collection）写回原始的 Groom 资产，或者连接到 `GuidesToJoints` 节点生成新的骨骼资产。

## C++ 用法

### 头文件引入

使用 Dataflow 节点通常不需要直接包含模块的头文件，因为这些节点是作为 `USTRUCT` 注册的 Dataflow 节点，由 Dataflow 框架自动发现和实例化。开发自定义节点时，需要包含基础框架头文件：

```cpp
#include "Dataflow/DataflowNode.h"
#include "HairStrandsCore/HairStrandsInterface.h" // 用于访问 FManagedArrayCollection 等核心类型
#include "GroomCollection.h" // 如果存在，用于访问 Groom 相关的集合定义
```

### 基本用法

以下是一个简化的示例，展示如何在 C++ 代码中通过 Dataflow 上下文执行一个预定义的 Dataflow 图（例如，用于处理 Groom 数据的图）。

```cpp
// 假设我们已经有一个 Dataflow 资产和一个 Groom 资产
UDataflow* DataflowAsset = ...;
UGroomAsset* GroomAsset = ...;

// 创建一个 Dataflow 上下文
UE::Dataflow::FContext Context;

// 将 Groom 资产设置为上下文的一个输入变量，通常图的第一个节点会读取它
Context.SetInputValue<UGroomAsset*>(TEXT("GroomAsset"), GroomAsset);

// 执行 Dataflow 图。具体的图执行逻辑由框架管理，这里只是示意。
// DataflowAsset->Evaluate(Context);

// 从上下文中获取处理后的结果（如果有输出）
// UGroomAsset* ModifiedGroom = Context.GetOutputValue<UGroomAsset*>(TEXT("ResultAsset"));
```
*(来源：基于 Dataflow 框架的通用用法推断)*

### 进阶用法

更复杂的用法通常涉及创建**自定义的 Dataflow 节点**来扩展 Groom 数据处理能力。你需要继承 `FDataflowNode` 并定义输入输出属性。

```cpp
// MyCustomGroomNode.h
#include "Dataflow/DataflowNode.h"
#include "HairStrandsCore/HairStrandsInterface.h"

USTRUCT(meta = (DataflowGroom))
struct FMyCustomGroomProcessNode : public FDataflowNode
{
    GENERATED_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomGroomProcessNode, "MyCustomProcess", "Groom", "处理Groom数据的自定义节点")

public:
    FMyCustomGroomProcessNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;

    // 输入：Groom 数据集合，使用 Passthrough 使其可以在节点间传递
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection", DataflowRenderGroups = "Surface"))
    FManagedArrayCollection Collection;

    // 输入：一个自定义的参数
    UPROPERTY(EditAnywhere, Category = "Settings", meta = (DataflowInput))
    float MyParameter = 1.0f;

    // 输出：处理后的数据键（可选）
    UPROPERTY(meta = (DisplayName = "Output Key", DataflowOutput))
    FCollectionAttributeKey OutputKey;
};

// MyCustomGroomNode.cpp
#include "MyCustomGroomNode.h"
// ... 其他必要的头文件

FMyCustomGroomProcessNode::FMyCustomGroomProcessNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    // 注册输入输出连接
    RegisterInputConnection(&Collection);
    RegisterInputConnection(&MyParameter);
    RegisterOutputConnection(&Collection, &Collection);
    RegisterOutputConnection(&OutputKey);
}

void FMyCustomGroomProcessNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 1. 获取输入数据
    const FManagedArrayCollection& InCollection = GetValue(Context, Collection);
    const float InParameter = GetValue(Context, MyParameter);

    // 2. 执行自定义处理逻辑
    // 例如，遍历 Collection 中的顶点，根据 InParameter 修改其位置
    // ...

    // 3. 将处理结果输出
    if (Out == &Collection)
    {
        SetValue(Context, Collection, ModifiedCollection);
    }
    else if (Out == &OutputKey)
    {
        SetValue(Context, OutputKey, FCollectionAttributeKey(/* 构造输出的键 */));
    }
}
```
*(来源：基于 `BuildGroomSplineSkinningNode.h`、`AttachGuidesRootsNode.h` 等文件的结构推断)*

## Demo 示例

以下是一个最小化的自定义 Dataflow 节点示例，该节点接受一个 Groom 数据集合，并为集合中的每条曲线的每个顶点添加一个基于其坐标的简单权重属性。

**MyGroomWeightNode.h**
```cpp
#pragma once

#include "Dataflow/DataflowNode.h"
#include "HairStrandsCore/HairStrandsInterface.h"

USTRUCT(meta = (DataflowGroom, Experimental))
struct FMyGroomWeightNode : public FDataflowNode
{
    GENERATED_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyGroomWeightNode, "AddPositionalWeight", "Groom", "根据顶点位置添加权重")

public:
    FMyGroomWeightNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;

    /** 输入的Groom数据集合 */
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    /** 输出的权重属性键 */
    UPROPERTY(meta = (DisplayName = "Weight Key", DataflowOutput))
    FCollectionAttributeKey WeightKey;
};
```

**MyGroomWeightNode.cpp**
```cpp
#include "MyGroomWeightNode.h"
#include "HairStrandsCore/HairStrandsCollection.h" // 假设包含集合数据访问的定义

FMyGroomWeightNode::FMyGroomWeightNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    RegisterInputConnection(&Collection);
    RegisterOutputConnection(&Collection, &Collection);
    RegisterOutputConnection(&WeightKey);
}

void FMyGroomWeightNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    FManagedArrayCollection& CollectionRef = GetValue(Context, Collection);

    // 假设集合中有 Vertex 和 Position 属性
    const TArray<FVector3f>& Positions = CollectionRef.GetAttribute<FVector3f>(TEXT("Position"), FHairStrandsCollection::VerticesGroup);
    TArray<float>& Weights = CollectionRef.AddAttribute<float>(TEXT("PositionalWeight"), FHairStrandsCollection::VerticesGroup);

    // 根据顶点的Y坐标计算一个简单的权重
    for (int32 i = 0; i < Positions.Num(); ++i)
    {
        Weights[i] = FMath::Clamp(Positions[i].Y / 100.0f, 0.0f, 1.0f); // 假设模型在Y轴上有100个单位的高度
    }

    if (Out == &Collection)
    {
        SetValue(Context, Collection, CollectionRef);
    }
    else if (Out == &WeightKey)
    {
        // 构造刚添加的属性的键
        FCollectionAttributeKey Key;
        Key.Attribute = TEXT("PositionalWeight");
        Key.Group = FHairStrandsCollection::VerticesGroup;
        SetValue(Context, WeightKey, Key);
    }
}
```

## 模块依赖

从 `HairStrandsDataflow` 模块的 `Build.cs` 分析，要使用此模块的功能，你的项目模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 提供 Groom 数据的核心类型定义（如 `FManagedArrayCollection`、`FGroomCollection` 等）和基础功能。 |
| `Dataflow` | Unreal Engine 的数据流框架，是所有 Dataflow 节点运行的基础。 |
| `HairStrandsRuntime` | 提供 Groom 的运行时渲染和模拟支持。 |

*注：依赖关系可能随 UE 版本变化，请以实际项目的 `Build.cs` 为准。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复了在移动渲染器上使用 Groom 绑定时出现的崩溃。 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复了在选择 `addSolverDeformer` 数据流节点时发生的崩溃。 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复了在数据流编辑器中播放 Groom 时重新编译蓝图导致的崩溃，以及错误的顶点数量问题。 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从上下文菜单中移除了“创建 Groom 数据流资产”选项。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口优化：通过通知客户端关联和解除关联来减少必要的代码复制。 |

### 维护评价

**综合评价：维护活跃，但处于重大更新过渡期。**

*   **创建时间**：约6年，是较成熟的系统。
*   **近期更新**：过去一周内有多次提交，主要集中在**修复崩溃 Bug** 和**优化编辑器体验**，表明该模块正在被积极使用和修复问题。
*   **代码现状**：从提供的源码文件分析，存在大量标记为 `Experimental` 和 `Deprecated` 的节点（如 `FBuildGroomSplineSkinWeightsNode` 被标记为 5.7 版本废弃）。同时，也有许多替代的新版本节点（如 `FBuildSplineSkinWeightsDataflowNode`）。这表明该模块正在经历一次**API 和数据结构的重构**，旧节点正在被逐步替换。
*   **已知限制**：
    1.  大量节点仍为实验性，API 可能在未来版本发生变化。
    2.  部分节点（如 `FBuildGuidesLODsDataflowNode`）在头文件中声明了 `Deprecated` 但提供了替代版本，使用时需注意选择正确的类名。
    3.  `EnabledByDefault: false`，需要手动在项目中启用插件。
*   **推荐使用**：**推荐**用于生产项目，但需注意：
    1.  优先使用未标记 `Deprecated` 的新版本节点（类名通常带 `_v2` 或不带 `Deprecated` 宏）。
    2.  密切关注 UE5 后续版本的更新日志，特别是涉及 Groom 和 Dataflow 的部分。
    3.  由于其实验性，建议在将基于此模块构建的复杂管线升级到新引擎版本时进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/RenderingFeatures/HairAndFur/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands/Tests)（位于插件目录下）