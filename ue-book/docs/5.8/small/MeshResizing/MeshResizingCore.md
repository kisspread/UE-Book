# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

MeshResizing 插件提供了一套基于约束求解的网格缩放与变形工具。其核心解决的问题是：在改变网格尺寸的同时，如何保持网格的形状特征（如剪切不变性、边长比例、弯曲角度等）。

插件采用基于物理模拟（PBD，Position Based Dynamics）的约束系统，通过剪切约束、边长约束、弯曲约束等多种约束的迭代求解，实现网格的高质量缩放。同时提供了基于 RBF（径向基函数）插值的变形方案，以及自定义区域的局部变形能力，适用于角色服装适配、道具尺寸调整等场景。

## 使用场景

- 你需要将一个角色服装网格适配到不同体型的骨架上 → 使用 RBF 插值变形
- 你需要保持网格形状特征的同时调整整体尺寸 → 使用约束求解器（剪切/边长/弯曲约束）
- 你需要对网格的某个局部区域进行独立缩放 → 使用自定义区域缩放（CustomRegionResizing）
- 你在 Dataflow 中搭建网格变形工作流 → 使用 MeshResizingDataflowNodes

## 蓝图用法

当前模块 MeshResizingCore 主要提供 C++ 底层 API。蓝图可用的结构体类型如下：

### 核心数据结构

| 结构体 | 说明 | 所在头文件 |
|---|---|---|
| `FMeshResizingRBFInterpolationData` | RBF 插值的采样索引、静止位置和权重数据 | `RBFInterpolation.h` |
| `FMeshResizingCustomRegion` | 自定义区域的顶点、坐标系和边界信息 | `CustomRegionResizing.h` |

### 枚举

| 枚举值 | 说明 |
|---|---|
| `EMeshResizingCustomRegionType::TrilinearInterpolation` | 三线性插值模式 |

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/BaseBodyTools.h"
#include "MeshResizing/Mesh3DConstraints.h"
#include "MeshResizing/RBFInterpolation.h"
#include "MeshResizing/CustomRegionResizing.h"
```

### 基本用法 — RBF 插值变形

使用 RBF 方法在源网格和目标网格之间进行插值变形：

```cpp
#include "MeshResizing/RBFInterpolation.h"
#include "DynamicMesh/DynamicMesh3.h"

using namespace UE::MeshResizing;

// 1. 从基础网格生成插值权重
FMeshResizingRBFInterpolationData InterpolationData;
FRBFInterpolation::GenerateWeights(BaseMesh, /*NumInterpolationPoints=*/64, InterpolationData);

// 2. 根据目标位置变形网格
FRBFInterpolation::DeformPoints(TargetPositions, InterpolationData, /*bInterpolateNormals=*/true, DeformingMesh);
```

### 基本用法 — 约束求解

使用物理约束对缩放后的网格进行形状保持：

```cpp
#include "MeshResizing/Mesh3DConstraints.h"

using namespace UE::MeshResizing;

// 创建约束
const int32 NumParticles = ResizedMesh.VertexCount();
TArray<float> ShearWeights, EdgeWeights, BendingWeights;
// ... 初始化权重数组 ...

FShearConstraint Shear(1.0f, ShearWeights, NumParticles);
FEdgeConstraint Edge(1.0f, EdgeWeights, NumParticles);
FBendingConstraint Bending(BaseMesh, 1.0f, BendingWeights, NumParticles);

// 创建反质量数组（用于约束求解）
TArray<float> InvMass;
InvMass.SetNumZeroed(NumParticles);

// 迭代求解
for (int32 Iter = 0; Iter < NumIterations; ++Iter)
{
    Shear.Apply(ResizedMesh, InitialResizedMesh, BaseMesh, InvMass);
    Edge.Apply(ResizedMesh, InitialResizedMesh, BaseMesh, InvMass);
    Bending.Apply(ResizedMesh, InvMass);
}
```

### 进阶用法 — 顶点映射与代理网格生成

在源网格和目标网格之间建立顶点映射，生成可调整尺寸的代理网格：

```cpp
#include "MeshResizing/BaseBodyTools.h"

using namespace UE::MeshResizing;

// 将顶点映射数据附加到网格
TArray<int32> VertexMappingData;
// ... 填充映射数据 ...
FBaseBodyTools::AttachVertexMappingData(
    FBaseBodyTools::ImportedVertexVIDsAttrName,
    VertexMappingData,
    SourceMesh
);

// 从两个网格的映射数据生成代理网格
UE::Geometry::FDynamicMesh3 ProxyMesh;
FBaseBodyTools::GenerateResizableProxyFromVertexMappingData(
    SourceMesh, FBaseBodyTools::ImportedVertexVIDsAttrName,
    TargetMesh, FBaseBodyTools::ImportedVertexVIDsAttrName,
    ProxyMesh
);

// 或者通过混合两个网格来插值代理
FBaseBodyTools::InterpolateResizableProxy(SourceMesh, TargetMesh, 0.5f, ProxyMesh);
```

### 进阶用法 — 自定义区域缩放

对网格的局部区域进行独立变形：

```cpp
#include "MeshResizing/CustomRegionResizing.h"

using namespace UE::MeshResizing;

// 生成自定义区域绑定
TSet<int32> BoundVertices;
// ... 填充区域顶点 ...
FMeshResizingCustomRegion RegionData;
FCustomRegionResizing::GenerateCustomRegion(BoundPositions, SourceMesh, BoundVertices, RegionData);

// 计算区域坐标系
FVector3d Origin;
FVector3f TangentU, TangentV, Normal;
FCustomRegionResizing::CalculateFrameForCustomRegion(SourceMesh, RegionData, Origin, TangentU, TangentV, Normal);

// 根据新边界角点插值区域顶点位置
TArray<FVector3d> BoundsCorners; // 新的边界角点
FCustomRegionResizing::InterpolateCustomRegionPoints(RegionData, BoundsCorners, BoundPositions);
```

## Demo 示例

```cpp
// MeshResizingExample.h
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "MeshResizing/RBFInterpolation.h"
#include "MeshResizing/Mesh3DConstraints.h"

class FMeshResizingExample
{
public:
    /** 将源网格通过 RBF 插值变形到目标形状 */
    static void DeformMeshToTarget(
        const UE::Geometry::FDynamicMesh3& SourceMesh,
        const TArray<FVector3f>& TargetPositions,
        UE::Geometry::FDynamicMesh3& OutDeformedMesh);
};
```

```cpp
// MeshResizingExample.cpp
#include "MeshResizingExample.h"

using namespace UE::MeshResizing;

void FMeshResizingExample::DeformMeshToTarget(
    const UE::Geometry::FDynamicMesh3& SourceMesh,
    const TArray<FVector3f>& TargetPositions,
    UE::Geometry::FDynamicMesh3& OutDeformedMesh)
{
    // 复制源网格作为输出
    OutDeformedMesh.Copy(SourceMesh);

    // 步骤1：生成 RBF 插值权重
    const int32 NumInterpolationPoints = 64;
    FMeshResizingRBFInterpolationData InterpolationData;
    FRBFInterpolation::GenerateWeights(SourceMesh, NumInterpolationPoints, InterpolationData);

    // 步骤2：使用 RBF 权重将目标位移传播到整个网格
    FRBFInterpolation::DeformPoints(TargetPositions, InterpolationData, /*bInterpolateNormals=*/true, OutDeformedMesh);

    // 步骤3：应用约束保持形状质量（可选）
    const int32 NumParticles = OutDeformedMesh.VertexCount();
    TArray<float> ZeroWeights;
    ZeroWeights.SetNumZeroed(NumParticles);
    TArray<float> InvMass;
    InvMass.SetNumZeroed(NumParticles);

    FShearConstraint Shear(0.5f, ZeroWeights, NumParticles);
    FEdgeConstraint Edge(0.5f, ZeroWeights, NumParticles);

    const int32 NumSolverIterations = 5;
    for (int32 i = 0; i < NumSolverIterations; ++i)
    {
        Shear.Apply(OutDeformedMesh, OutDeformedMesh, SourceMesh, InvMass);
        Edge.Apply(OutDeformedMesh, OutDeformedMesh, SourceMesh, InvMass);
    }
}
```

## 模块依赖

基于源码中使用的类型推断，使用者需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | `FDynamicMesh3` 等几何数据结构 |
| `Chaos` | `FPBDFlatWeightMapView`、`FSolverReal` 等物理约束求解器类型 |
| `MeshDescription` | `FMeshDescription` 网格描述格式 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关更新 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在头文件清理前补充必要的 include 引用 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow 绘制工具新增套索选择支持 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow 大量节点迁移至新渲染系统 |

### 维护评价

**活跃维护中**。该插件于 2024 年 12 月创建，至今约 1.4 年，仍在持续开发中。最近一次提交距今不足 1 个月，且更新内容从编译警告修复到 Dataflow 新功能引入，表明项目处于活跃迭代阶段。

注意事项：
- 插件标记为实验性（`IsExperimentalVersion=true`），默认不启用，API 可能发生变化
- 从 commit 历史来看，Dataflow 节点是当前重点开发方向
- 使用 Chaos 物理引擎的约束求解类型，与引擎物理模块深度耦合
- **推荐用于实验和原型开发**，不建议在生产环境中依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- 官方文档（暂无）