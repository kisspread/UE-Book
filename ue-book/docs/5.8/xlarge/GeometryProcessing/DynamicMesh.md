# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry

| 属性 | 值 |
|---|---|
| 中文名 | 几何处理 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `DynamicMesh` (Runtime), `GeometryAlgorithms` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-26 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 插件是 UE5 几何处理的核心算法库，提供了完整的网格数据结构（`FDynamicMesh3`）和一系列几何操作算法。它本质上是 UE5 建模工具（Mesh Modeling Toolset）和 Procedural Mesh 的底层引擎，解决了以下问题：

1. **动态网格数据结构**：`FDynamicMesh3` 是一个拓扑灵活的三角网格，支持动态添加/删除顶点、边、三角形，以及多种属性叠加层（UV、法线、颜色、骨骼权重等）。
2. **网格简化与重网格化**：基于 QEM（Quadric Error Metric）的网格简化算法、基于边翻转/分割/折叠的自适应重网格化。
3. **参数化与 UV 生成**：包括共形映射（Conformal Map）、指数映射（ExpMap）、基于 Patch 的自动 UV 生成等多种 UV 参数化方案。
4. **网格布尔与切割**：平面切割、区域偏移/挤出、倒角等拓扑操作。
5. **几何约束求解**：基于拉普拉斯矩阵的网格变形求解器、约束泊松求解器等线性代数工具。
6. **烘焙与采样**：法线/AO/曲率等贴图的烘焙框架。
7. **测地线计算**：三角网格上的测地线路径追踪与最短路径查找。

该插件从 `Experimental` 迁移到 `Runtime`，说明 Epic 将其视为 UE5 几何处理的基础能力，大量官方工具（如编辑器建模工具、Geometry Script 等）都依赖于此。

## 使用场景

- 你需要在运行时动态修改网格拓扑（添加/删除三角形、边翻转）→ 用 `FDynamicMesh3`
- 你需要将高面数网格简化到目标面数或误差阈值 → 用 `TMeshSimplification`
- 你需要对网格进行自适应重网格化以获得均匀三角形 → 用 `FRemesher`
- 你需要自动生成 UV 坐标（自动展开、共形映射等）→ 用 `FPatchBasedMeshUVGenerator` 或 `FDynamicMeshUVEditor`
- 你需要用平面切割网格或将网格区域挤出/偏移 → 用 `FMeshPlaneCut` / `FOffsetMeshRegion`
- 你需要对网格顶点进行约束变形（拖拽变形、拉普拉斯平滑）→ 用 `FConstrainedMeshDeformationSolver`
- 你需要在运行时烘焙法线贴图或 AO → 用 `FMeshMapBaker`
- 你需要计算三角网格上的测地线路径 → 用 `FDeformableEdgePath` / `FMeshGeodesicSurfaceTracer`
- 你需要为碰撞检测生成简单形状近似（凸包、包围盒等）→ 用 `FMeshSimpleShapeApproximation`
- 你需要对网格进行倒角操作 → 用 `FMeshBevel`
- 你需要检测网格的平面镜像对称性 → 用 `FMeshPlanarSymmetry`
- 你需要在网格上做自由变形（FFD）→ 用 `FFFDLattice`
- 你需要转移蒙皮权重（从一个网格到另一个）→ 用 `FTransferBoneWeights`

## 蓝图用法

该插件主要是 **纯 C++ 库**，其 `BlueprintCallable` 接口非常少。大部分功能通过 Geometry Script 插件（`GeometryScripting`）暴露给蓝图。直接使用此插件的用户通常在 C++ 中调用。

以下是 GeometryProcessing 模块本身提供的少量公开蓝图接口：

### 核心节点

由于该插件以 C++ 算法库为主，蓝图可直接调用的节点极少。主要功能需要通过 C++ 或借助 Geometry Script 间接访问。

### 使用示例（蓝图描述）

如果你需要在蓝图中使用这些几何操作，推荐通过 **Geometry Script** 插件作为桥梁：

1. 在项目设置中启用 `Geometry Scripting` 和 `GeometryProcessing` 插件
2. 使用 Geometry Script 提供的蓝图节点（如 `Simplify Mesh`、`Remesh Mesh`、`Apply Mesh Plane Cut` 等）
3. 这些节点内部会调用 GeometryProcessing 的底层算法

## C++ 用法

### 头文件引入

```cpp
// DynamicMesh 核心数据结构
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAttributeSet.h"

// 网格操作
#include "Operations/MeshSimplification.h"
#include "Operations/MeshPlaneCut.h"
#include "Operations/OffsetMeshRegion.h"
#include "Operations/MeshBevel.h"

// 重网格化
#include "Remesher.h"
#include "SubRegionRemesher.h"

// 约束系统
#include "MeshConstraints.h"
#include "MeshConstraintsUtil.h"

// UV 参数化
#include "DynamicMesh/DynamicMeshUVEditor.h"
#include "Parameterization/PatchBasedMeshUVGenerator.h"

// 求解器
#include "Solvers/LaplacianMatrixAssembly.h"
#include "Solvers/ConstrainedMeshDeformationSolver.h"

// 测地线
#include "Operations/GeodesicPath.h"
#include "Operations/MeshGeodesicSurfaceTracer.h"

// 烘焙
#include "Sampling/MeshMapBaker.h"

// 形状近似
#include "ShapeApproximation/MeshSimpleShapeApproximation.h"
```

### 基本用法：网格简化

来源：`Public/MeshSimplification.h` 中 `TMeshSimplification` 类

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Operations/MeshSimplification.h"

using namespace UE::Geometry;

void SimplifyMyMesh(FDynamicMesh3& Mesh, int32 TargetTriangleCount)
{
    // 创建简化器（默认使用 Quadric Error Metric）
    TMeshSimplification<TQuadricError<double>> Simplifier(&Mesh);
    
    // 配置简化选项
    Simplifier.bPreserveBoundaryShape = true;    // 保持边界形状
    Simplifier.bAllowSeamCollapse = false;        // 不允许 UV 接缝塌陷
    Simplifier.CollapseMode = TMeshSimplification<TQuadricError<double>>::ESimplificationCollapseModes::MinimalQuadricPositionError;
    
    // 执行简化到目标三角形数量
    Simplifier.SimplifyToTriangleCount(TargetTriangleCount);
    
    // 也可以按其他标准简化：
    // Simplifier.SimplifyToMaxError(0.01);        // 按最大误差
    // Simplifier.SimplifyToEdgeLength(5.0);        // 按最小边长
    // Simplifier.SimplifyToMinimalPlanar();        // 仅简化平面区域
}
```

### 基本用法：自适应重网格化

来源：`Public/Remesher.h` 中 `FRemesher` 类

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Remesher.h"

using namespace UE::Geometry;

void RemeshMyMesh(FDynamicMesh3& Mesh, double TargetEdgeLength)
{
    // 创建重网格器
    FRemesher Remesher(&Mesh);
    
    // 设置目标边长
    Remesher.SetTargetEdgeLength(TargetEdgeLength);
    
    // 配置选项
    Remesher.bEnableFlips = true;
    Remesher.bEnableCollapses = true;
    Remesher.bEnableSplits = true;
    Remesher.bEnableSmoothing = true;
    Remesher.SmoothType = FRemesher::ESmoothTypes::Uniform;
    
    // 设置投影模式（可将修改后的顶点投射到原始表面）
    Remesher.ProjectionMode = FMeshRefinerBase::ETargetProjectionMode::AfterRefinement;
    
    // 预计算优化
    Remesher.Precompute();
    
    // 执行多轮重网格化
    for (int32 Pass = 0; Pass < 10; ++Pass)
    {
        Remesher.BasicRemeshPass();
        
        // 如果几乎没有边被修改，说明已收敛
        if (Remesher.ModifiedEdgesLastPass < 10)
            break;
    }
}
```

### 基本用法：UV 编辑

来源：`Public/Parameterization/DynamicMeshUVEditor.h` 中 `FDynamicMeshUVEditor` 类

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshUVEditor.h"

using namespace UE::Geometry;

void GenerateUVs(FDynamicMesh3& Mesh, const TArray<int32>& Triangles)
{
    // 创建 UV 编辑器
    FDynamicMeshUVEditor UVEditor(&Mesh, 0 /*UV Layer*/, true /*CreateIfMissing*/);
    
    // 方法一：使用共形映射（Least Squares Conformal Map）
    UVEditor.SetTriangleUVsFromFreeBoundaryConformal(Triangles);
    
    // 方法二：使用指数映射（适合单连通区域）
    // UVEditor.SetTriangleUVsFromExpMap(Triangles);
    
    // 方法三：平面投影（适合简单几何体）
    // FFrame3d ProjectionFrame(FVector3d::Zero(), FVector3d::UnitZ());
    // UVEditor.SetTriangleUVsFromPlanarProjection(Triangles, 
    //     [](const FVector3d& P) { return P; }, // 点变换
    //     ProjectionFrame, 
    //     FVector2d(1.0, 1.0)); // 尺寸
}
```

### 基本用法：平面切割

来源：`Public/Operations/MeshPlaneCut.h` 中 `FMeshPlaneCut` 类

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Operations/MeshPlaneCut.h"

using namespace UE::Geometry;

void CutMeshWithPlane(FDynamicMesh3& Mesh, FVector3d PlaneOrigin, FVector3d PlaneNormal)
{
    // 创建平面切割操作
    FMeshPlaneCut PlaneCut(&Mesh, PlaneOrigin, PlaneNormal);
    
    // 配置选项
    PlaneCut.bSimplifyAlongNewEdges = true;  // 简化切割产生的细长三角形
    PlaneCut.bCollapseDegenerateEdgesOnCut = true;
    
    // 执行切割（正半侧被删除）
    bool bSuccess = PlaneCut.Cut();
    
    // 获取切割产生的边界环
    for (const FMeshPlaneCut::FOpenBoundary& Boundary : PlaneCut.OpenBoundaries)
    {
        for (const FEdgeLoop& Loop : Boundary.CutLoops)
        {
            // 处理切割边界环...
        }
    }
    
    // 可选：填充切割产生的孔洞
    PlaneCut.SimpleHoleFill();
}
```

### 进阶用法：约束重网格化（保持属性接缝）

来源：`Public/MeshConstraintsUtil.h`、`Public/SubRegionRemesher.h`

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Remesher.h"
#include "SubRegionRemesher.h"
#include "MeshConstraints.h"
#include "MeshConstraintsUtil.h"

using namespace UE::Geometry;

void ConstrainedRemesh(FDynamicMesh3& Mesh, const TSet<int32>& VertexROI, double TargetEdgeLength)
{
    // 创建约束系统
    FMeshConstraints Constraints;
    
    // 约束所有属性接缝（UV、法线等），不允许翻转/分割/塌陷
    FMeshConstraintsUtil::ConstrainAllBoundariesAndSeams(
        Constraints, Mesh,
        EEdgeRefineFlags::FullyConstrained,  // 网格边界
        EEdgeRefineFlags::FullyConstrained,  // 组边界
        EEdgeRefineFlags::FullyConstrained,  // 材质边界
        false, false,  // 不允许接缝的分割和平滑
        true /*并行*/);
    
    // 创建局部重网格器
    FSubRegionRemesher Remesher(&Mesh);
    Remesher.SetTargetEdgeLength(TargetEdgeLength);
    Remesher.SetInitialVertexROI(VertexROI);
    Remesher.InitializeFromVertexROI();
    
    // 设置约束
    Remesher.SetExternalConstraints(MoveTemp(Constraints));
    
    // 投影到原始表面
    Remesher.ProjectionMode = FMeshRefinerBase::ETargetProjectionMode::AfterRefinement;
    
    // 执行重网格化
    Remesher.Precompute();
    for (int32 i = 0; i < 5; ++i)
    {
        Remesher.UpdateROI();
        Remesher.BasicRemeshPass();
    }
}
```

### 进阶用法：约束网格变形

来源：`Private/Solvers/Internal/ConstrainedMeshDeformationSolver.h`

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Solvers/ConstrainedMeshDeformationSolver.h"

using namespace UE::Geometry;

void DeformMesh(FDynamicMesh3& Mesh, TMap<int32, FVector3d>& HandleVertexTargets)
{
    // 创建变形求解器（使用余切权重拉普拉斯矩阵）
    FConstrainedMeshDeformationSolver Solver(
        Mesh, 
        ELaplacianWeightScheme::Cotangent,
        EMatrixSolverType::LU);
    
    // 添加约束（高权重 = 更接近目标位置）
    for (const auto& [VertexID, TargetPos] : HandleVertexTargets)
    {
        Solver.AddConstraint(VertexID, 1000.0, TargetPos, false);
    }
    
    // 求解变形
    TArray<FVector3d> ResultPositions;
    Solver.UpdateSolverConstraints();
    Solver.Deform(ResultPositions);
    
    // 应用结果到网格
    for (int32 i = 0; i < ResultPositions.Num(); ++i)
    {
        if (Mesh.IsVertex(i))
        {
            Mesh.SetVertex(i, ResultPositions[i]);
        }
    }
}
```

### 进阶用法：测地线路径计算

来源：`Public/Operations/GeodesicPath.h` 中 `FDeformableEdgePath`

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Operations/GeodesicPath.h"

using namespace UE::Geometry;

TArray<IntrinsicCorrespondenceUtils::FSurfacePoint> ComputeGeodesicPath(
    const FDynamicMesh3& Mesh, int32 StartVertexID, int32 EndVertexID)
{
    // 构建从起点到终点的初始边路径（最短边距离路径，非测地线）
    TArray<FEdgePath::FDirectedSegment> InitialPath;
    // ... 需要先通过 Dijkstra 等方式构建初始路径 ...
    
    // 创建可变形边路径（基于 intrinsic triangulation 的测地线优化）
    FDeformableEdgePath GeoPath(Mesh, InitialPath);
    
    // 最小化路径长度（path straightening）
    FDeformableEdgePath::FEdgePathDeformationInfo DeformInfo;
    GeoPath.Minimize(DeformInfo);
    
    UE_LOG(LogTemp, Log, TEXT("原始长度: %f, 最终长度: %f, 迭代次数: %d"),
        DeformInfo.OriginalLength, DeformInfo.FinalLength, DeformInfo.NumIterations);
    
    // 获取表面上的路径点
    TArray<IntrinsicCorrespondenceUtils::FSurfacePoint> SurfacePoints = GeoPath.AsSurfacePoints(0.01);
    
    return SurfacePoints;
}
```

## Demo 示例

### 完整示例：网格简化 + UV 生成

```cpp
// MyGeometryProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAttributeSet.h"

using namespace UE::Geometry;

class FMyGeometryProcessor
{
public:
    /**
     * 处理输入网格：简化到指定面数，然后自动生成 UV
     * @param InOutMesh 输入/输出网格
     * @param TargetTriCount 目标三角形数量
     */
    static void ProcessMesh(FDynamicMesh3& InOutMesh, int32 TargetTriCount);
    
    /**
     * 对网格的局部区域进行自适应重网格化
     * @param InOutMesh 输入/输出网格
     * @param ROI 顶点感兴趣区域
     * @param TargetEdgeLength 目标边长
     */
    static void RemeshRegion(FDynamicMesh3& InOutMesh, const TArray<int32>& ROI, double TargetEdgeLength);
};
```

```cpp
// MyGeometryProcessor.cpp
#include "MyGeometryProcessor.h"
#include "Operations/MeshSimplification.h"
#include "DynamicMesh/DynamicMeshUVEditor.h"
#include "SubRegionRemesher.h"
#include "MeshConstraints.h"
#include "MeshConstraintsUtil.h"

void FMyGeometryProcessor::ProcessMesh(FDynamicMesh3& InOutMesh, int32 TargetTriCount)
{
    if (InOutMesh.TriangleCount() <= TargetTriCount)
        return;
    
    // 1. 设置约束（保护属性接缝和边界）
    FMeshConstraints Constraints;
    FMeshConstraintsUtil::ConstrainAllBoundariesAndSeams(
        Constraints, InOutMesh,
        EEdgeRefineFlags::NoCollapse,
        EEdgeRefineFlags::NoCollapse,
        EEdgeRefineFlags::NoCollapse,
        false, false);
    
    // 2. 执行网格简化
    TMeshSimplification<TQuadricError<double>> Simplifier(&InOutMesh);
    Simplifier.SetExternalConstraints(MakeUnique<FMeshConstraints>(MoveTemp(Constraints)));
    Simplifier.bPreserveBoundaryShape = true;
    Simplifier.SimplifyToTriangleCount(TargetTriCount);
    
    // 3. 自动生成 UV
    TArray<int32> AllTriangles;
    AllTriangles.Reserve(InOutMesh.TriangleCount());
    for (int32 TID : InOutMesh.TriangleIndicesItr())
    {
        AllTriangles.Add(TID);
    }
    
    FDynamicMeshUVEditor UVEditor(&InOutMesh, 0, true);
    UVEditor.SetTriangleUVsFromFreeBoundaryConformal(AllTriangles);
}

void FMyGeometryProcessor::RemeshRegion(
    FDynamicMesh3& InOutMesh, const TArray<int32>& ROI, double TargetEdgeLength)
{
    if (ROI.Num() == 0)
        return;
    
    // 1. 收集 ROI 中的所有顶点
    TSet<int32> VertexSet;
    for (int32 TriID : ROI)
    {
        if (!InOutMesh.IsTriangle(TriID))
            continue;
        FIndex3i TriVerts = InOutMesh.GetTriangle(TriID);
        VertexSet.Add(TriVerts.A);
        VertexSet.Add(TriVerts.B);
        VertexSet.Add(TriVerts.C);
    }
    
    // 2. 设置约束
    FMeshConstraints Constraints;
    FMeshConstraintsUtil::ConstrainAllSeams(Constraints, InOutMesh, false, false);
    
    // 3. 配置局部重网格器
    FSubRegionRemesher Remesher(&InOutMesh);
    Remesher.SetTargetEdgeLength(TargetEdgeLength);
    Remesher.SetInitialVertexROI(VertexSet);
    Remesher.InitializeFromVertexROI();
    Remesher.SetExternalConstraints(MakeUnique<FMeshConstraints>(MoveTemp(Constraints)));
    
    // 4. 执行多轮重网格化
    Remesher.Precompute();
    for (int32 Pass = 0; Pass < 8; ++Pass)
    {
        Remesher.UpdateROI();
        Remesher.BasicRemeshPass();
        if (Remesher.ModifiedEdgesLastPass == 0)
            break;
    }
}
```

## 模块依赖

该插件的 Build.cs 文件信息未在提供的内容中完整展示，但从源码结构和头文件依赖分析：

无特殊依赖（仅标准 Core/Engine/Slate 等）。

GeometryProcessing 本身是底层库，依赖非常基础的 UE 模块。其内部使用了 Eigen 数学库（通过 UE 的 Eigen 集成）进行稀疏矩阵求解。模块间依赖关系：

- **DynamicMesh** 模块：核心数据结构，不依赖其他两个模块
- **GeometryAlgorithms** 模块：算法层，依赖 DynamicMesh
- **MeshFileUtils** 模块：文件 I/O，依赖 DynamicMesh

使用该插件的外部模块通常只需依赖 `DynamicMesh`（如果只用数据结构）或 `GeometryAlgorithms`（如果需要算法）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `35f4c4a4` | Fix float overflow warning for arm64 build | 修复 ARM64 构建时的浮点溢出警告 |
| 2026-05-15 | `35f66cf1` | Guard against INDEX_NONE / invalid edge id in hole fill util's fill color method | 修复孔洞填充工具中无效边 ID 导致的崩溃 |
| 2026-05-13 | `2c7d172e` | Clamp UV values to max float when invalid value is in returned as double (max double) | 修复 UV 值从 double 返回时为最大值导致的溢出问题 |
| 2026-05-12 | `64deb517` | Hook up AttributeAwareV2 simplifier in MeshTerrainStaticMeshTransformer | 在 MeshTerrain 中接入新版属性感知简化器 |
| 2026-05-12 | `68fbe22e` | [SkeletalMeshModelingTools] clamp smooth strength to 0 - 1 | 钳制骨骼网格建模工具中的平滑强度到 0-1 范围 |

### 维护评价

**活跃维护中**。该插件过去一个月内有多次实质性更新，涵盖：
- Bug 修复（UV 溢出、无效 ID 防护）
- 新功能集成（AttributeAwareV2 简化器）
- 跨平台兼容性修复（ARM64）
- 生态系统整合（SkeletalMeshModelingTools、MeshTerrain）

作为 UE5 几何处理的核心基础设施，该插件被 Geometry Script、Mesh Modeling Toolset、Procedural Mesh 等多个官方系统依赖，Epic 持续投入维护。尽管标记为 `IsBetaVersion = true`，但其 API 已经相当稳定成熟。**强烈推荐使用**，它是 UE5 中进行程序化几何处理的事实标准。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing/Tests)