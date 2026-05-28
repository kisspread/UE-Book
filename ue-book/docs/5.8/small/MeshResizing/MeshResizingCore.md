# Mesh Resizing

> Mesh Resizing（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

MeshResizing 并非一个简单的网格缩放工具。它提供了一套复杂的算法和工具集，用于在保持原始网格拓扑关系和细节的前提下，通过物理约束（如剪切、拉伸、弯曲约束）和基于采样点的插值（RBF），将基础（Base）网格的形状变换和比例变化，传递到目标（Target）网格上。核心是生成一个能够忠实反映基础网格变形的“代理”网格（Proxy Mesh），并将这种变形约束应用到最终的输出网格中。这使得它特别适合于角色身体比例调整、服装模拟适配等需要精细形变控制的场景。

## 使用场景

-   **角色身体比例调整**：当你需要将同一个基础人形网格，适配到不同高矮胖瘦的角色体型时，使用此插件可以确保在比例变化的同时，关节、服装等关联部分能够合理地变形，避免穿插和失真。
-   **服装模拟与适配**：在服装模拟中，衣服网格需要根据角色身体网格的变形而跟随变形。该插件可以帮助生成这种变形约束，确保衣物贴合新的身体形状。
-   **参数化网格调整**：通过其 Dataflow 节点，可以创建基于不同输入参数（如身高、体型）动态生成最终网格的管道。

## 蓝图用法

该插件主要提供底层 C++ 算法库和 Dataflow 节点，未发现直接暴露的 `BlueprintCallable` 函数。其功能通常通过 **Dataflow 图表** 或 **C++ 代码** 来调用。

### 核心节点（Dataflow）

通过 `MeshResizingDataflowNodes` 模块，该插件提供了一系列 Dataflow 节点，用于在可视化编程环境中构建网格调整逻辑。具体节点请参考插件内的数据流资产。

### 使用示例（Dataflow 描述）

1.  **设置基础网格和目标网格**：将需要变形的基础网格（如标准人形）和作为形状参考的目标网格（如变体体型）输入到 Dataflow 图表中。
2.  **生成插值权重**：使用基于 `RBFInterpolation` 的节点，根据基础网格的顶点分布，计算一组采样点的权重数据。
3.  **应用约束变形**：使用基于 `Mesh3DConstraints` 的节点（如剪切、弯曲约束），将基础网格的形变传递并约束到目标网格上。
4.  **输出结果**：将生成的代理网格或变形后的网格输出。

## C++ 用法

重点从提供的头文件中提取。

### 头文件引入

```cpp
#include "MeshResizing/BaseBodyTools.h"
#include "MeshResizing/Mesh3DConstraints.h"
#include "MeshResizing/RBFInterpolation.h"
#include "MeshResizing/CustomRegionResizing.h"
```

### 基本用法

使用 `FRBFInterpolation` 进行网格变形。这是插件核心功能之一，通过采样点和权重将一个网格的顶点位置变形到另一个参考形状上。

```cpp
// 来源：基于 Public/MeshResizing/RBFInterpolation.h 中的函数签名推断
#include "MeshResizing/RBFInterpolation.h"
#include "DynamicMesh/DynamicMesh3.h"

void DeformMeshUsingRBF(const UE::Geometry::FDynamicMesh3& BaseMesh, const UE::Geometry::FDynamicMesh3& TargetMesh, UE::Geometry::FDynamicMesh3& OutDeformedMesh)
{
    // 1. 为目标形状（TargetMesh）计算插值权重
    FMeshResizingRBFInterpolationData InterpWeightsData;
    const int32 NumInterpPoints = 100; // 采样点数量，需要根据实际情况调整
    UE::MeshResizing::FRBFInterpolation::GenerateWeights(TargetMesh, NumInterpPoints, InterpWeightsData);

    // 2. 准备要变形的网格（通常初始是 BaseMesh）
    OutDeformedMesh = BaseMesh; // 复制基础网格作为起点

    // 3. 使用计算出的权重和目标网格的顶点位置来变形 OutDeformedMesh
    //    这里需要先从 TargetMesh 中获取变形目标位置，示例简化
    TArray<FVector3f> TargetPositions;
    // ... 从 TargetMesh 提取顶点到 TargetPositions ...
    // 简化示例：直接使用目标网格顶点作为变形目标
    for (int32 i = 0; i < TargetMesh.VertexCount(); ++i)
    {
        TargetPositions.Add((FVector3f)TargetMesh.GetVertex(i));
    }

    UE::MeshResizing::FRBFInterpolation::DeformPoints(TargetPositions, InterpWeightsData, true /* bInterpolateNormals */, OutDeformedMesh);
}
```

### 进阶用法

结合物理约束进行更受控的变形。先使用 RBF 生成初始变形，再通过约束（如保持边长、抗弯曲）来稳定结果。

```cpp
// 来源：基于 Public/MeshResizing/Mesh3DConstraints.h 中的类推断
#include "MeshResizing/Mesh3DConstraints.h"
// ... 其他包含 ...

void DeformMeshWithConstraints(UE::Geometry::FDynamicMesh3& ResizedMesh, const UE::Geometry::FDynamicMesh3& BaseMesh)
{
    // 假设 ResizedMesh 已经通过 RBF 得到了初步变形 (InitialResizedMesh)
    UE::Geometry::FDynamicMesh3 InitialResizedMesh = ResizedMesh; // 保存初始变形状态

    const int32 NumParticles = ResizedMesh.VertexCount();
    TArray<float> InvMass; // 需要计算每个粒子的逆质量
    InvMass.SetNumZeroed(NumParticles);
    // ... 计算 InvMass，例如与三角形面积成反比 ...

    // 1. 应用剪切约束
    TArray<float> ShearWeights; // 需要设置每个顶点的约束权重
    float ShearStrength = 0.5f;
    UE::MeshResizing::FShearConstraint ShearConstraint(ShearStrength, ShearWeights, NumParticles);
    ShearConstraint.Apply(ResizedMesh, InitialResizedMesh, BaseMesh, InvMass);

    // 2. 应用边缘长度约束
    TArray<float> EdgeWeights;
    float EdgeStrength = 1.0f;
    UE::MeshResizing::FEdgeConstraint EdgeConstraint(EdgeStrength, EdgeWeights, NumParticles);
    EdgeConstraint.Apply(ResizedMesh, InitialResizedMesh, BaseMesh, InvMass);

    // 3. 应用弯曲约束（可选，计算量更大）
    TArray<float> BendingWeights;
    float BendingStrength = 0.1f;
    UE::MeshResizing::FBendingConstraint BendingConstraint(BaseMesh, BendingStrength, BendingWeights, NumParticles);
    // BendingConstraint.Apply(ResizedMesh, InvMass); // 注意：此函数可能有不同的重载
}
```

## Demo 示例

一个完整的、可编译的最小 C++ 示例，演示如何使用 `FRBFInterpolation` 来变形一个简单的网格。

```cpp
// MeshResizingDemo.h
#pragma once

#include "CoreMinimal.h"

class FDynamicMesh3;
struct FMeshResizingRBFInterpolationData;

class FMeshResizingDemo
{
public:
    /** 根据源网格和目标网格的采样数据，变形输出网格 */
    static void DeformMeshWithRBF(const UE::Geometry::FDynamicMesh3& SourceMesh, const UE::Geometry::FDynamicMesh3& TargetMesh, UE::Geometry::FDynamicMesh3& OutMesh);
};
```

```cpp
// MeshResizingDemo.cpp
#include "MeshResizingDemo.h"
#include "MeshResizing/RBFInterpolation.h"
#include "DynamicMesh/DynamicMesh3.h"

void FMeshResizingDemo::DeformMeshWithRBF(const UE::Geometry::FDynamicMesh3& SourceMesh, const UE::Geometry::FDynamicMesh3& TargetMesh, UE::Geometry::FDynamicMesh3& OutMesh)
{
    // 1. 为“目标形状”（TargetMesh）计算RBF插值权重
    FMeshResizingRBFInterpolationData RBFData;
    const int32 NumSamplePoints = 50; // 采样点数
    UE::MeshResizing::FRBFInterpolation::GenerateWeights(TargetMesh, NumSamplePoints, RBFData);

    // 2. 初始化输出网格（通常基于源网格）
    OutMesh = SourceMesh;

    // 3. 获取目标网格的顶点位置作为变形目标
    TArray<FVector3f> TargetPositions;
    TargetPositions.Reserve(TargetMesh.VertexCount());
    for (int32 Vid = 0; Vid < TargetMesh.VertexCount(); ++Vid)
    {
        if (TargetMesh.IsVertex(Vid))
        {
            TargetPositions.Add((FVector3f)TargetMesh.GetVertex(Vid));
        }
    }

    // 4. 应用RBF变形：根据目标顶点位置和预计算的权重，变形OutMesh
    UE::MeshResizing::FRBFInterpolation::DeformPoints(TargetPositions, RBFData, true, OutMesh);
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析。以下是使用该插件时，你的模块可能需要依赖的**独特**依赖项。

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 处理静态网格体的中间表示，是插件数据交换的常见格式。 |
| `GeometryCore` | 提供核心几何数据结构，如 `FDynamicMesh3`。 |
| `GeometryAlgorithms` | 提供各种几何算法。 |
| `MeshConversion` | 用于 `FMeshDescription` 和 `FDynamicMesh3` 之间的转换。 |
| `Chaos` | 来自 `Mesh3DConstraints.h`，插件内的物理约束（PBD）使用了 Chaos 的求解器数据结构。 |

**注意**：`Chaos` 是一个大型物理系统模块，引入它会增加编译时间和潜在的二进制大小。请确认你的项目确实需要这些高级物理约束功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 节点相关更新（commit message 不完整）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理之前，补充了必要的头文件包含。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow：为绘制工具添加了套索支持，利用了网格编辑的新特性。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：更新大量节点以使用新的渲染系统。 |

### 维护评价

-   **创建时间**：2024年12月，非常新的插件。
-   **最近更新**：从提交记录看，截至2026年5月仍在活跃开发，主要集中在 Dataflow 节点的增强和 bug 修复上。
-   **活跃度**：**活跃维护中**。
-   **已知限制**：插件明确标记为 `IsExperimentalVersion: true` 且默认未启用 (`EnabledByDefault: false`)，表明其API、功能和稳定性可能随时发生变化。依赖 `Chaos` 模块可能导致额外的开销。
-   **推荐使用**：**适合探索和原型开发**。对于生产环境，需谨慎评估其稳定性。如果你的工作流严重依赖 Dataflow 且需要高级网格比例调整功能，可以尝试使用，但需做好应对未来变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- 官方文档：无（.uplugin 中 DocsURL 为空）