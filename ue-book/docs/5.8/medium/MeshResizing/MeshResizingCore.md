# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

`MeshResizing` 是一个实验性的编辑器插件，旨在提供高级的网格（Mesh）调整和变形功能。它解决了在三维建模、角色创建（特别是服装和配饰）中，需要将网格（如衣服）精确地适配到不同体型或姿态的基体（如角色身体）上的问题。与简单的缩放或刚性绑定不同，该插件通过一系列约束求解器（如剪切、弯曲、边约束）和基于径向基函数（RBF）的插值算法，实现网格的物理模拟式变形，以保持网格的细节和结构完整性，避免不自然的拉伸或扭曲。

## 使用场景

- 你在制作一个角色换装系统，需要将一件标准尺寸的衣服网格精确地适配到不同体型（胖瘦高矮）的角色模型上。
- 你在创建一个角色，需要其装备（如盔甲、背包）在角色摆出各种姿势时，能够自然地跟随身体变形，而不是简单地父子绑定。
- 你需要一种可程序化、可参数化的方法来批量处理大量网格的适配工作。

## 蓝图用法

该插件目前的公开 API 以 C++ 静态函数和结构体为主，主要通过 `MeshResizingCore` 模块暴露。虽然头文件中没有直接标记 `BlueprintCallable`，但其核心数据结构（如 `FMeshResizingRBFInterpolationData`, `FMeshResizingCustomRegion`）和工具函数旨在被更高级的蓝图节点或编辑器工具调用。通常，你会通过 `MeshResizingEngine` 或 `MeshResizingDataflowNodes` 模块中的蓝图节点来使用这些核心功能。

### 核心概念节点

| 节点/函数 | 说明 | 所在类/命名空间 |
|---|---|---|
| `BaseBodyTools::AttachVertexMappingData` | 将顶点映射数据（如原始顶点索引）附加到动态网格上，用于后续的调整。 | `UE::MeshResizing::FBaseBodyTools` |
| `BaseBodyTools::GenerateResizableProxyFromVertexMappingData` | 基于源网格和目标网格上的顶点映射数据，生成一个用于调整的代理网格。 | `UE::MeshResizing::FBaseBodyTools` |
| `FRBFInterpolation::GenerateWeights` | 为网格生成基于径向基函数的插值权重数据。这是实现网格变形的关键准备步骤。 | `UE::MeshResizing::FRBFInterpolation` |
| `FRBFInterpolation::DeformPoints` | 使用预先计算好的插值权重，将目标网格的位置信息应用到待变形网格上，实现顶点变形。 | `UE::MeshResizing::FRBFInterpolation` |
| `FCustomRegionResizing::GenerateCustomRegion` | 为网格上的一个特定区域（如袖口、领口）生成自定义调整绑定数据。 | `UE::MeshResizing::FCustomRegionResizing` |
| `FCustomRegionResizing::InterpolateCustomRegionPoints` | 根据边界角点位置，插值计算自定义区域内顶点的新位置。 | `UE::MeshResizing::FCustomRegionResizing` |

### 约束类节点

| 节点/函数 | 说明 | 所在类 |
|---|---|---|
| `FShearConstraint::Apply` | 应用剪切约束，防止网格在变形时产生过度的剪切形变。 | `UE::MeshResizing::FShearConstraint` |
| `FEdgeConstraint::Apply` | 应用边约束，维持网格边的长度，保持网格的局部尺寸。 | `UE::MeshResizing::FEdgeConstraint` |
| `FBendingConstraint::Apply` | 应用弯曲约束，维持网格面片之间的角度，保持网格的曲面特征。 | `UE::MeshResizing::FBendingConstraint` |
| `FExternalForceConstraint::Apply` | 应用外部力约束，可用于施加重力等外力效果。 | `UE::MeshResizing::FExternalForceConstraint` |

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/BaseBodyTools.h"
#include "MeshResizing/RBFInterpolation.h"
#include "MeshResizing/CustomRegionResizing.h"
#include "MeshResizing/Mesh3DConstraints.h"
#include "DynamicMesh/DynamicMesh3.h"
```

### 基本用法：使用 RBF 插值变形网格

以下示例展示了如何使用 RBF 插值将一个网格适配到另一个网格上。

```cpp
// 假设 SourceMesh 和 TargetMesh 是已经准备好的 UE::Geometry::FDynamicMesh3 对象。
// TargetMesh 可能是通过雕刻或从其他软件导入的、已经调整好形状的网格。

// 1. 准备插值数据
UE::MeshResizing::FMeshResizingRBFInterpolationData InterpolationData;
const int32 NumInterpolationPoints = 256; // 采样点数量，影响精度和性能
UE::MeshResizing::FRBFInterpolation::GenerateWeights(SourceMesh, NumInterpolationPoints, InterpolationData);

// 2. 创建待变形的网格（可以是源网格的副本）
UE::Geometry::FDynamicMesh3 DeformingMesh = SourceMesh; // 创建副本

// 3. 执行变形
// TargetPositions 是从 TargetMesh 中提取的目标位置数组
TArray<FVector3f> TargetPositions;
// ... 填充 TargetPositions ...
UE::MeshResizing::FRBFInterpolation::DeformPoints(TargetPositions, InterpolationData, true /* bInterpolateNormals */, DeformingMesh);

// 现在 DeformingMesh 就是变形后的结果。
```

### 进阶用法：结合约束求解器

在简单的 RBF 插值基础上，可以结合物理约束来获得更自然的结果。

```cpp
// 在应用 RBF 插值后，可能需要多次迭代约束求解器来“收紧”网格。
// 1. 创建约束求解器实例
const int32 NumVertices = DeformingMesh.VertexCount();
TArray<float> ShearWeights; // 每个顶点的剪切约束权重
ShearWeights.SetNumZeroed(NumVertices); // 简化：全部设为1.0
UE::MeshResizing::FShearConstraint ShearSolver(1.0f /* Strength */, ShearWeights, NumVertices);

// 2. 保存一份初始状态用于约束求解
UE::Geometry::FDynamicMesh3 InitialDeformedMesh = DeformingMesh;

// 3. 迭代约束求解（通常在帧循环或模拟步进中进行）
for (int32 Iter = 0; Iter < 10; ++Iter)
{
    ShearSolver.Apply(DeformingMesh, InitialDeformedMesh, SourceMesh /* BaseMesh */);
    // 可以依次应用其他约束：FEdgeConstraint, FBendingConstraint 等。
}
```

## Demo 示例

一个最小的可编译示例，演示如何为一个源网格附加顶点映射数据。

```cpp
// MyMeshResizingDemo.h
#pragma once
#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"

class FMyMeshResizingDemo
{
public:
    static void AttachVertexDataToMesh(UE::Geometry::FDynamicMesh3& Mesh, const TArray<int32>& VertexMapping);
};

// MyMeshResizingDemo.cpp
#include "MyMeshResizingDemo.h"
#include "MeshResizing/BaseBodyTools.h"

void FMyMeshResizingDemo::AttachVertexDataToMesh(UE::Geometry::FDynamicMesh3& Mesh, const TArray<int32>& VertexMapping)
{
    // 使用预定义的属性名称将数据附加到网格上
    const FName AttrName = UE::MeshResizing::FBaseBodyTools::ImportedVertexVIDsAttrName;
    bool bSuccess = UE::MeshResizing::FBaseBodyTools::AttachVertexMappingData(AttrName, VertexMapping, Mesh);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully attached vertex mapping data to mesh."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to attach vertex mapping data."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 提供核心几何数据结构 `FDynamicMesh3` 和几何算法。 |
| `Chaos` | 提供约束求解器中使用的类型，如 `FPBDFlatWeightMapView`, `FSolverReal`, `TVec4`。 |
| `MeshDescription` | 用于处理基于 `FMeshDescription` 格式的网格数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数所产生的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: [Specific commit details not provided in prompt] | 数据流相关更新，具体内容未提供。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理之前，补充了必要的包含文件。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 数据流：为绘制工具添加套索支持，利用了网格中新增的功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 数据流：将大量节点更新为使用新的渲染系统。 |

### 维护评价

该插件创建于2024年底，截至2025年5月，依然有持续的功能更新（特别是Dataflow相关）和代码维护（如修复警告）。更新频率较为稳定，表明它正处于**活跃的实验性开发阶段**。由于其 `IsExperimentalVersion: true` 和 `EnabledByDefault: false` 的状态，意味着它尚未稳定，API 可能发生变化，且需要用户手动启用。推荐在实验性项目或学习研究中使用，不建议用于追求稳定性的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)