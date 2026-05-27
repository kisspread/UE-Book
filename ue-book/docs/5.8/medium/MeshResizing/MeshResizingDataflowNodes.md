# Mesh Resizing

> Mesh Resizing（网格大小调整）

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

基于源码分析，Mesh Resizing 插件的核心用途是**为 Dataflow 提供一套用于调整（缩放/变形）网格体的工具节点**。它并非简单的缩放，而是提供更高级的网格体处理能力，例如：
1. **拓扑转移（Mesh Wrap）**：将一个网格体的拓扑结构（顶点连接关系）“包裹”到另一个网格体的形状上，实现基于地标的网格体配准和变形。
2. **径向基函数（RBF）插值**：基于采样点和权重，将一个网格体变形到另一个网格体的形状，适用于形状插值和迁移。
3. **UV 操作**：提供对网格体 UV 坐标进行对齐、变换和解包的功能，以配合网格体几何形状的调整。
4. **纹理生长**：基于 UV 区域在纹理上查找并平铺一个瓦片，以处理网格体调整后可能出现的纹理拉伸问题。
5. **约束变形**：提供带有物理模拟（如弯曲、剪切、边约束）的网格体变形能力。

该插件主要服务于需要程序化、数据驱动方式调整或适配网格体几何形状的流程，例如角色身体部位适配、程序化物体变形等。

## 使用场景

- 你需要将一个角色的身体网格体形状“适配”到另一个具有不同比例的角色网格体上（例如，将一个高瘦角色的网格拓扑适配到一个矮胖角色的形状上），且需要保持拓扑结构以便后续绑定动画 → 使用 `MeshWrapNode`。
- 你需要在一个基础形状和一个目标形状之间生成一系列平滑过渡的网格体（例如，不同体型的角色之间进行形状插值） → 组合使用 `GenerateResizableProxyDataflowNode` 和 `GenerateInterpolatedProxyDataflowNode`。
- 你需要将网格体的 UV 坐标根据其新的几何形状进行重新对齐、缩放或解包，以避免纹理拉伸 → 使用 `AlignUVMeshNode`、`UVMeshTransformNode`、`UVUnwrapNode` 等节点。
- 你正在构建一个基于 Dataflow 的程序化资产生成管线，其中包含网格体的动态调整步骤 → 集成本插件提供的 Dataflow 节点。

## 蓝图用法

该插件的核心功能以 **Dataflow 节点**的形式提供。这些节点可以在支持 Dataflow 的编辑器工具（如用于骨骼网格体编辑的工具）或蓝图数据流图中使用。

### 核心节点

以下是从源码中提取的关键 Dataflow 节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshToMesh` | 将骨骼网格体 (`USkeletalMesh`) 转换为动态网格体 (`UDynamicMesh`) 或数据流网格体 (`UDataflowMesh`)，并可记录导入顶点信息用于拓扑映射。 | `FSkeletalMeshToMeshDataflowNode`, `FSkeletalMeshToMeshDataflowNode_v2` |
| `GenerateResizableProxy` | 基于源网格体和目标网格体，生成一对具有相同拓扑的代理网格体，用于后续的插值变形。 | `FGenerateResizableProxyDataflowNode` |
| `GenerateInterpolatedProxy` | 基于源代理网格体和目标代理网格体，生成在指定 `BlendAlpha`（0到1）之间插值的网格体。 | `FGenerateInterpolatedProxyDataflowNode` |
| `MeshWrapLandmarks` | 定义用于 Mesh Wrap 操作的地标。地标通过标识符和顶点索引在源网格体和目标网格体上对应。 | `FMeshWrapLandmarksNode` |
| `MeshWrap` | 执行网格体包裹操作。将源拓扑网格体包裹到目标形状网格体上，利用匹配的地标来优化结果。输出包裹后的网格体。 | `FMeshWrapNode` |
| `GenerateRBFResizingWeights` | 从源网格体上采样点，并生成用于 RBF 插值的权重数据。 | `FGenerateRBFResizingWeightsNode` |
| `ApplyRBFResizing` | 将预计算的 RBF 插值权重应用到待调整的网格体上，使其变形为目标网格体的形状。 | `FApplyRBFResizingNode` |
| `MeshWarp` | 一个高级节点，集成了 `WrapDeform` 和 `RBFInterpolate` 两种网格体变形方法。 | `FMeshWarpNode` |
| `AlignUVMeshNode` | 根据基础网格体的 UV 布局，对齐和缩放调整后网格体的 UV 坐标。 | `FAlignUVMeshNode` |
| `UVMeshTransformNode` | 对网格体指定 UV 通道进行平移、旋转、缩放变换。 | `FUVMeshTransformNode` |
| `UVUnwrapNode` | 对网格体指定 UV 通道进行重新解包（展平），支持多种算法。 | `FUVUnwrapNode` |
| `UVResizeController` | 控制器节点，用于判断网格体是否适合 UV 调整并返回相关 UV 通道信息。 | `FUVResizeControllerNode` |
| `GrowTileRegion` | 在纹理上基于网格体的 UV 区域查找一个瓦片，并将其平铺到整个图像，用于修复纹理拉伸。 | `FMeshResizingGrowTileRegionNode` |
| `MeshConstrainedDeformationTestPlayground` | 带有物理约束（剪切、弯曲、边、重力）的网格体变形测试节点。 | `FMeshConstrainedDeformationNode` |

### 使用示例（蓝图描述）

**场景：使用 RBF 方法将一个球体网格体变形为一个立方体网格体的形状**
1. 创建两个输入网格体：一个作为“源形状”（球体），一个作为“目标形状”（立方体）。通常使用 `SkeletalMeshToMesh` 或其他方式获取 `UDataflowMesh`。
2. 将“源形状”网格体连接到 `GenerateRBFResizingWeights` 节点的 `SourceMesh` 输入。该节点会输出 `InterpolationData`。
3. 将待变形的原始网格体（可以是球体或其他任意网格）连接到 `ApplyRBFResizing` 节点的 `MeshToResize` 输入。
4. 将步骤2中生成的 `InterpolationData` 连接到 `ApplyRBFResizing` 节点的 `InterpolationData` 输入。
5. 将“目标形状”网格体连接到 `ApplyRBFResizing` 节点的 `TargetMesh` 输入。
6. 运行数据流图，`ApplyRBFResizing` 节点的 `ResizedMesh` 输出即为变形后的网格体，其形状应近似于立方体。

## C++ 用法

该插件的 C++ 用法主要涉及创建和使用其定义的数据流节点结构体。

### 头文件引入

```cpp
#include "MeshResizing/MeshWrapNode.h"
```

### 基本用法

Dataflow 节点通常通过其结构体在数据流上下文中被实例化和评估。以下示例展示了如何在 C++ 中访问一个 Dataflow 节点的属性（非直接实例化，通常由 Dataflow 框架管理）：

```cpp
// 假设在一个数据流节点的 Evaluate 函数内部，或者通过某种方式获取了节点指针
// 例如：FMeshWrapNode* WrapNode = ...;
// 注意：直接实例化 Dataflow 节点通常不发生在常规 C++ 代码中，而是由 Dataflow 上下文管理。

// 设置 Wrap 节点的参数
WrapNode->MaxNumOuterIterations = 15;
WrapNode->NumInnerIterations = 30;
WrapNode->LaplacianStiffness = 0.5f;
WrapNode->ProjectionTolerance = 1e-5f;

// 设置地标数据
TArray<FMeshWrapLandmark> SourceLandmarks, TargetLandmarks;
// ... 填充地标数据
WrapNode->SourceTopologyLandmarks = SourceLandmarks;
WrapNode->TargetShapeLandmarks = TargetLandmarks;

// 节点会由 Dataflow 上下文在需要时自动调用其 Evaluate 方法。
```
*来源: Public/MeshResizing/MeshWrapNode.h*

### 进阶用法

自定义一个继承自 `FDataflowNode` 的新节点，并复用插件提供的功能结构体：

```cpp
#include "Dataflow/DataflowNode.h"
#include "MeshResizing/MeshWrapNode.h" // 复用 FMeshWrapLandmark

// 假设我们定义一个自定义的、结合了地标生成和包裹的简化节点
USTRUCT(Meta = (Experimental))
struct FMyCustomWrapNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()

    // 复用插件提供的地标结构体
    TArray<FMeshWrapLandmark> MyLandmarks;

    // ... 其他输入输出属性 ...

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        // 在这里，你可以直接使用 MyLandmarks 数据，
        // 并可能内部调用 FMeshWrapNode 相似的逻辑，或者使用其他 MeshResizing 模块提供的辅助函数。
        // 注意：直接调用另一个节点的 Evaluate 通常不是标准做法，但可以封装底层逻辑。
    }
};
```

## Demo 示例

一个演示如何使用 `GenerateRBFResizingWeights` 和 `ApplyRBFResizing` 节点逻辑的最小 C++ 示例片段。请注意，实际使用中节点由 Dataflow 框架管理。

```cpp
// MyMeshResizingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Dataflow/DataflowNode.h"
#include "MeshResizing/RBFInterpolationNodes.h" // 为了使用 FMeshResizingRBFInterpolationData

UCLASS(BlueprintType)
class UMyMeshResizingDemo : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 演示如何通过 Dataflow 节点结构体处理网格体调整（概念性代码）。
     * 实际项目中，这些节点会连接到 Dataflow 图中。
     */
    UFUNCTION(BlueprintCallable, Category = "Mesh Resizing Demo")
    void PerformRBFResize(UDataflowMesh* Source, UDataflowMesh* Target, UDataflowMesh* ToResize);
};

// MyMeshResizingDemo.cpp
#include "MyMeshResizingDemo.h"

void UMyMeshResizingDemo::PerformRBFResize(UDataflowMesh* Source, UDataflowMesh* Target, UDataflowMesh* ToResize)
{
    if (!Source || !Target || !ToResize) return;

    // 注意：以下代码仅为说明数据流和过程，直接实例化节点通常由框架完成。
    // 这里模拟生成权重的节点输入输出。
    FGenerateRBFResizingWeightsNode::FNodeParameters WeightParams;
    // ... 配置参数 ...
    FGenerateRBFResizingWeightsNode WeightNode(WeightParams);
    // 假设通过某种方式设置了节点的输入 (SourceMesh) ...
    // 节点被评估后，其输出 InterpolationData 被填充。
    FMeshResizingRBFInterpolationData InterpData;
    // InterpData = WeightNode.GetOutputValue(WeightNode.InterpolationData); // 伪代码

    // 模拟应用变形的节点。
    FApplyRBFResizingNode::FNodeParameters ApplyParams;
    // ... 配置参数 ...
    FApplyRBFResizingNode ApplyNode(ApplyParams);
    // 将 InterpData 和 ToResize 设置为 ApplyNode 的输入...
    // 节点被评估后，其输出 ResizedMesh 即为结果。
    // UDataflowMesh* ResizedResult = ApplyNode.GetOutputValue(ApplyNode.ResizedMesh); // 伪代码
}
```
*说明：此示例为概念性演示，展示了数据流。实际在 UE 编辑器中，你会在 Dataflow 图编辑器里连接这些节点。*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshResizingCore` | 提供网格调整的核心数据类型（如 `UDataflowMesh`）和基础功能。 |
| `MeshResizingEngine` | 提供网格调整的引擎层实现，如几何处理算法。 |
| `MeshResizingEditorTools` | 提供与编辑器集成的工具，如地标选择工具 (`UMeshWrapLandmarkSelectionTool`)。 |
| `GeometryCore`, `GeometryFramework`, `GeometryNodes` | 提供基础的几何处理框架、动态网格体 (`UDynamicMesh`) 和相关的 Dataflow 节点基础设施。 |
| `MeshConversion`, `MeshDescription` | 用于在 `USkeletalMesh`、`UStaticMesh`、`UDynamicMesh` 和 `UDataflowMesh` 之间转换。 |
| `ModelingComponents` | 提供编辑器工具中使用的通用组件，如交互器、选择器等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数时产生警告的代码。 |
| 2026-05-12 | `a7802337` | Dataflow: | （信息不完整，推测为数据流相关的更新或修复）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理工作预先添加必要的包含文件。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 数据流：为绘制工具添加了套索支持，利用了网格中新增的功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 数据流：将许多节点更新为使用新的渲染系统。 |

### 维护评价

**综合评价：活跃维护中的实验性插件**

- **年龄**：插件于2024年底创建，非常年轻。
- **维护频率**：从提交历史看，**非常活跃**。在创建后的一年多时间里，有多次功能性更新（如添加套索支持、更新渲染系统、修复警告），表明 Epic 的开发者正在积极开发和迭代此插件。
- **状态**：**实验性**。`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认未启用。API 和功能在未来版本中可能发生变化。
- **限制与已知问题**：作为实验性插件，其 API 和节点接口可能不稳定。部分节点（如 `FSkeletalMeshToMeshDataflowNode`）已被标记为 `Deprecated`，并在新版本（v2）中替代。使用时应关注更新日志。
- **推荐使用**：**谨慎推荐**。适用于需要前沿网格调整功能，特别是结合 Dataflow 进行程序化内容生成的 **实验性项目**或**内部工具开发**。不建议在追求稳定性的生产环境中直接依赖。使用前应评估其功能是否满足需求，并准备好应对可能的 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档](https://epicgames.com)（.uplugin 中 DocsURL 为空，暂无独立官方文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Tests)（如果存在）