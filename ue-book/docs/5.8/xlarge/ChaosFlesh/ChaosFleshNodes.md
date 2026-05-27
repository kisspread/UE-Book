# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肌肉 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow 节点） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🏛️ 文物（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

Chaos Flesh 是 Unreal Engine 5 的一个实验性物理模拟插件，其核心目的是提供一套完整的工具链，用于创建和模拟基于物理的肌肉（Flesh）系统。它解决的是生物力学与动画领域中一个特定的问题：如何在虚拟角色上实现逼真、物理正确的肌肉收缩、膨胀、皮肤滑动以及与骨骼的交互效果。

这个插件不同于传统的基于曲线或蒙皮的动画方式，它利用 **Chaos 物理求解器** 对由**四面体（Tetrahedron）** 构成的**体积网格（Volumetric Mesh）** 进行动力学模拟。这意味着肌肉被视为一个具有体积、质量和物理属性的实体，而不是表面的几何形状。插件提供了完整的 **Dataflow（数据流图）** 工作流，允许用户以节点式的方式构建模拟资产，定义肌肉的几何形状、物理属性（如密度、刚度、阻尼、不可压缩性）、与骨骼的绑定约束、以及驱动肌肉收缩的激活数据。

**简单来说，它的存在是为了实现：**
1.  **物理驱动的肌肉变形**：基于物理引擎模拟真实的肌肉收缩、膨胀过程。
2.  **精确的约束系统**：定义肌肉附着点（起源/插入点）与骨骼的约束（运动学或弱约束）。
3.  **皮肤-肌肉交互**：模拟皮肤在肌肉表面的滑动效果。
4.  **完整的资产管线**：通过 Dataflow 图从几何数据生成最终的 `FleshAsset`，用于运行时模拟。

## 使用场景

-   **你需要为角色创建逼真的肌肉变形动画**：例如，战斗角色手臂发力时肱二头肌的隆起，或者面部角色表情驱动下的细微肌肉运动。使用 Chaos Flesh 可以基于物理模拟得到，而无需手动 K 动画曲线。
-   **你正在开发一个生物力学或医学可视化应用**：需要模拟真实的人体肌肉组织行为，Chaos Flesh 提供的四面体网格和物理属性设置非常适合这类科学可视化。
-   **你的游戏或应用包含需要物理交互的软体角色**：例如，具有可变形肉体的怪物或生物，其形变可以由物理引擎实时计算，增加沉浸感。
-   **你需要一个标准化的工作流来制作肌肉模拟资产**：Chaos Flesh 的 Dataflow 节点图提供了一个清晰、可复用、可参数化的资产制作管线。

## 蓝图用法

Chaos Flesh 的主要使用界面是 **Dataflow 图（Dataflow Graph）**。用户在 Editor 中创建 Dataflow 资产，然后通过组合下面列出的各种节点来构建完整的肌肉模拟资产生成流程。这些节点通过引脚连接数据（如 `FManagedArrayCollection`，即几何与物理数据的集合）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateTetrahedron` | 将三角面片网格转换为四面体体积网格。支持 IsoStuffing 和 TetWild 两种网格化方法。 | `FCreateTetrahedronDataflowNode` |
| `SetFleshBonePositionTargetBinding` | 将肌肉顶点与骨骼表面进行绑定（运动学或弱约束）。 | `FSetFleshBonePositionTargetBindingDataflowNode_v2` |
| `ComputeFiberField` | 根据指定的肌肉起源（Origin）和插入（Insertion）点，计算每个四面体的纤维方向。 | `FComputeFiberFieldNode` |
| `SetMuscleActivationParameter` | 设置肌肉收缩的全局或逐肌肉的激活参数（如收缩体积比、长度激活曲线等）。 | `FSetMuscleActivationParameterNode` |
| `GenerateSurfaceBindings` | 生成四面体体积网格与外部渲染网格（StaticMesh 或 SkeletalMesh）之间的表面绑定。 | `FGenerateSurfaceBindings` |
| `SetVertexTrianglePositionTargetBinding` | 在不同几何体表面之间创建点-三角形弱约束（弹簧），用于模拟皮肤滑动。 | `FSetVertexTrianglePositionTargetBindingDataflowNode` |
| `MakeFleshAsset` | 将构建好的 `Collection` 数据打包生成最终的 `FleshAsset`，可用于运行时加载。 | `FMakeFleshAssetNode` |
| `GetFleshAsset` | 获取已生成的 `FleshAsset` 并将其 `Collection` 数据输出到 Dataflow 图中。 | `FGetFleshAssetDataflowNode` |
| `AppendTetrahedralCollection` | 将两个四面体集合合并，常用于组合多个肌肉部分。 | `FAppendTetrahedralCollectionDataflowNode_v2` |
| `SetFleshDefaultProperties` | 设置肌肉的基本物理属性（密度、刚度、阻尼、不可压缩性等）。 | `FSetFleshDefaultPropertiesNode` |

### 使用示例（蓝图描述）

一个典型的 **Chaos Flesh** 资产制作 Dataflow 图流程如下：

1.  **输入几何**：首先使用 `GetStaticMesh` 或 `GetSkeletalMesh` 等节点获取源几何数据（一个代表肌肉轮廓的封闭网格）。
2.  **生成四面体**：将网格连接到 `CreateTetrahedron` 节点，配置网格化方法（如 `IsoStuffing`）和细分参数，输出四面体集合。
3.  **设置属性**：连接到 `SetFleshDefaultProperties` 节点，设置肌肉的物理材质属性。
4.  **定义纤维场**：通过 `GetVertexSelection` 等节点选择肌肉的起源和插入点索引，连接到 `ComputeFiberField` 节点，计算纤维方向。
5.  **创建绑定**：连接到 `SetFleshBonePositionTargetBinding` 节点，输入目标 `SkeletalMesh`，将四面体顶点与骨骼表面绑定。
6.  **设置激活**：连接到 `SetMuscleActivationParameter` 节点，配置肌肉如何根据骨骼动画收缩。
7.  **生成资产**：最终将输出的 `Collection` 连接到 `MakeFleshAsset` 节点，指定资产路径，点击“构建”即可生成 `FleshAsset`。

## C++ 用法

由于 Chaos Flesh 主要通过 Dataflow 系统使用，其 C++ API 主要用于编写自定义的 Dataflow 节点或直接操作底层的 `FleshCollection` 数据。

### 头文件引入

```cpp
#include "ChaosFleshNodes.h" // 访问 Dataflow 节点定义
#include "ChaosFlesh/ChaosFleshCollection.h" // 访问 FFleshCollection (通常由 FManagedArrayCollection 代表)
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个简单的 Dataflow 节点，并使用 Chaos Flesh 的核心数据结构。

```cpp
// 示例来源：基于源码中节点定义模式推断
// 假设我们要创建一个自定义节点，用于读取 FleshCollection 中的顶点数量。

#include "Dataflow/DataflowNode.h"
#include "ManagedArrayCollection.h"

USTRUCT(meta = (DataflowFlesh))
struct FMyFleshNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyFleshNode, "MyFleshNode", "Flesh", "Custom");

public:
    // 输入：一个 FleshCollection (本质是 FManagedArrayCollection)
    UPROPERTY(meta = (DataflowInput, DisplayName = "Collection"))
    FManagedArrayCollection Collection;

    // 输出：顶点数量
    UPROPERTY(meta = (DataflowOutput, DisplayName = "VertexCount"))
    int32 VertexCount;

    FMyFleshNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&VertexCount);
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        if (Out->IsSame(&VertexCount))
        {
            // 从输入的 Collection 中获取顶点组数据，并计算其大小
            if (Collection.HasGroup(TEXT("Vertices")))
            {
                const auto& Vertices = Collection.GetAttribute<FVector3f>(TEXT("Vertex"), TEXT("Vertices"));
                VertexCount = Vertices.Num();
            }
            else
            {
                VertexCount = 0;
            }
        }
    }
};
```

### 进阶用法

Chaos Flesh 节点通常处理复杂的几何和物理数据。以下示例展示了如何访问四面体元素和纤维方向数据。

```cpp
// 示例：访问并打印每个四面体的纤维方向（假设 ComputeFiberField 节点已运行）
virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
{
    if (Collection.HasGroup(TEXT("Tetrahedra")) && Collection.HasAttribute(TEXT("FiberDirection"), TEXT("Tetrahedra")))
    {
        const auto& Tetrahedra = Collection.GetAttribute<FIntVector4>(TEXT("Element"), TEXT("Tetrahedra"));
        const auto& FiberDirections = Collection.GetAttribute<FVector3f>(TEXT("FiberDirection"), TEXT("Tetrahedra"));
        
        // 假设我们想计算所有四面体纤维方向的平均值
        FVector3f AverageDirection = FVector3f::ZeroVector;
        for (int32 i = 0; i < Tetrahedra.Num(); ++i)
        {
            AverageDirection += FiberDirections[i];
        }
        if (Tetrahedra.Num() > 0)
        {
            AverageDirection /= static_cast<float>(Tetrahedra.Num());
        }
        // 将平均值存储到输出或用于其他计算...
    }
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何在 C++ 中定义并注册一个简单的 Chaos Flesh Dataflow 节点。

```cpp
// MyFleshDemoNode.h
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowNode.h"
#include "MyFleshDemoNode.generated.h"

USTRUCT(meta = (DataflowFlesh))
struct FMyFleshDemoNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyFleshDemoNode, "DemoFleshNode", "Flesh", "Demo Node");

public:
    FMyFleshDemoNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DisplayName = "Collection", DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyFleshDemoNode.cpp
#include "MyFleshDemoNode.h"
#include "ChaosFleshNodesModule.h" // 用于注册节点

FMyFleshDemoNode::FMyFleshDemoNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    // 注册输入和输出引脚
    RegisterInputConnection(&Collection);
    RegisterOutputConnection(&Collection, &Collection); // 数据直接传递
}

void FMyFleshDemoNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 在此编写节点的核心逻辑
    // 示例：确保输入的 Collection 包含最小必要的数据组
    if (Collection.HasGroup(TEXT("Vertices")))
    {
        // 执行一些操作，例如添加自定义属性
        // Collection.AddAttribute<FString>(TEXT("DemoAttribute"), TEXT("Vertices")) = TEXT("Hello Flesh!");
    }
    // 由于设置了 DataflowPassthrough，Collection 会自动传递给输出。
}

// 在模块的 StartupModule 中注册此节点（通常通过一个全局注册函数）
void RegisterMyCustomNodes()
{
    UE::Dataflow::RegisterNodeStruct<FMyFleshDemoNode>();
}
```

## 模块依赖

要使用 **ChaosFlesh** 插件，你的模块（例如一个自定义的 Dataflow 节点模块或游戏模块）通常需要依赖以下模块。这些依赖主要围绕 Chaos 物理系统、几何处理和 Dataflow 框架。

| 模块 | 用途 |
|---|---|
| `Chaos` | 底层的 Chaos 物理求解器和核心类型。 |
| `ChaosFlesh` | Chaos Flesh 插件的核心模块，提供 `FleshCollection` 等基础类型。 |
| `ChaosFleshNodes` | 提供所有官方的 Dataflow 节点定义。如果需要扩展或引用这些节点，则需要依赖。 |
| `GeometryFramework` | 提供 `UDynamicMesh` 等动态网格资产，常用于 Dataflow 节点的输出预览。 |
| `GeometryProcessing` | 提供网格处理算法，如网格化（`TetWild`）、网格分析等，被 `CreateTetrahedron` 等节点使用。 |
| `ModelingComponents` | 提供建模工具和组件，与 Dataflow 和几何处理紧密集成。 |
| `Dataflow` | UE5 的 Dataflow 数据流图框架。 |
| `DataflowEngine` | Dataflow 框架的运行时引擎支持。 |
| `MeshConversion` | 用于在不同网格表示（如 `FMeshDescription`, `FDynamicMesh3`）之间转换。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量到浮点数转换产生警告的代码。 |
| 2026-05-12 | `981bc9da` | Dataflow: | [提交信息不完整，通常为通用更新或小修复] |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理肌肉纤维场生成节点的代码。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区数量的赋值错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 在肌肉资产中弃用静态网格体属性。 |

### 维护评价

**活跃维护中**。
- **创建时间**：2022年3月，插件历史超过4年。
- **近期更新**：最近一次更新在 **2026年5月**，且当月有多次提交，主要集中在 **代码清理**、**节点优化** 和 **错误修复** 上。
- **维护频率**：更新频率较高，表明该插件仍然处于 **积极开发和维护** 状态。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion=true`，且默认未启用，这表明其 API 和功能仍有可能发生变化，但更新活动证明 Epic 仍在持续投入。
- **推荐使用**：**推荐**用于**实验性**或**高级项目**中，以探索基于物理的肌肉模拟。不建议在需要高度稳定性的商业项目的核心流程中完全依赖，但可以用于研究和原型开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档：暂无
- 测试用例：暂无公开信息