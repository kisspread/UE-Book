# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ChaosVisualDebugger 相关资源） |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-01（估计） |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 是 UE5 底层几何处理算法库，源自 Ryan Schmidt 的 [geometry3Sharp](https://github.com/gradientspace/geometry3Sharp) 移植。它解决的核心问题是：**在运行时对 2D/3D 几何数据进行数学计算和变换**，包括形状拟合、网格生成、UV 展开、多边形布尔运算、曲线拟合等。

这个插件存在的意义是为上层工具（如 Geometry Script、MeshModelingToolset、Chaos 物理系统）提供高性能的底层算法实现。它不直接面向终端用户，而是作为其他系统的算法后端。

**注意**：此插件标记为 Beta 且默认未启用（`Installed: false`）。需要在项目的 `.uproject` 中手动启用，或通过其他依赖它的插件间接启用。

## 使用场景

- 你需要在运行时从点云拟合包围体（胶囊、球、OBB）→ 用 `TFitCapsule3` / `TMinVolumeSphere3` / `TMinVolumeBox3`
- 你需要对 2D 多边形做布尔运算（并集、差集、交集）→ 用 `PolygonsUnion` / `PolygonsDifference` 等
- 你需要从三角面片生成四面体网格（用于物理模拟）→ 用 `FTetWild::ComputeTetMesh`
- 你需要自动 UV 展开 → 用 `XAtlasWrapper::ComputeUVs`
- 你需要约束 Delaunay 三角剖分 → 用 `TConstrainedDelaunay2`
- 你需要对点集做主成分分析（PCA）→ 用 `TPCA3`
- 你需要 B 样条曲线拟合 → 用 `BSplineCurveFit`
- 你需要计算 UV 质量指标（拉伸度、纹素密度）→ 用 `FUVMetrics`
- 你需要 MikkT 切线计算 → 用 `DynamicMeshMikkTWrapper::ComputeTangents`

## 模块概览

本插件包含 3 个模块，本文档重点覆盖 **GeometryAlgorithms** 模块。

| 模块 | 类型 | 说明 |
|---|---|---|
| **GeometryAlgorithms** | Runtime | 核心算法库：形状拟合、网格生成、UV 处理、多边形运算、距离/相交计算 |
| **DynamicMesh** | Runtime | 动态网格数据结构（`FDynamicMesh3`），支持运行时编辑的三角网格 |
| **MeshFileUtils** | DeveloperTool | 网格文件读写工具（仅开发阶段使用） |

> ⚠️ DynamicMesh 和 MeshFileUtils 的详细文档待补充。DynamicMesh 模块提供 `FDynamicMesh3` 数据结构，是 GeometryAlgorithms 中许多算法的输入/输出载体。

## 蓝图用法

**本模块不暴露任何蓝图节点。** GeometryAlgorithms 是纯 C++ 模板库，所有 API 均为 C++ 模板类和静态函数。

如需在蓝图中使用这些算法，请通过 [Geometry Script](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting) 插件间接访问，Geometry Script 在其蓝图函数内部调用了 GeometryAlgorithms 的底层实现。

## C++ 用法

### 算法分类总览

| 类别 | 算法 | 头文件 |
|---|---|---|
| 形状拟合 | PCA、胶囊、最小球、最小OBB | `PCA3.h`, `FitCapsule3.h`, `MinVolumeSphere3.h`, `MinVolumeBox3.h` |
| 四面体网格 | fTetWild 算法 | `FTetWildWrapper.h` |
| UV 展开 | XAtlas 自动 UV | `XAtlasWrapper.h` |
| UV 指标 | 拉伸度、纹素密度 | `Parameterization/UVMetrics.h` |
| 2D 多边形布尔 | 并集/差集/交集/异或 | `Curve/PolygonIntersectionUtils.h` |
| 2D 多边形偏移 | 扩展/收缩 | `Curve/PolygonOffsetUtils.h` |
| 三角剖分 | 约束 Delaunay | `ConstrainedDelaunay2.h` |
| 平面排列 | 线段排列 + 三角化 | `Arrangement2d.h` |
| 曲线拟合 | B 样条拟合 | `Curve/BSplineCurveFit.h` |
| 距离计算 | 线-圆距离 | `Distance/DistLine3Circle3.h` |
| 相交检测 | 圆柱-盒相交 | `Intersection/IntrCylinderBox3.h` |
| 切线计算 | MikkT 切线 | `DynamicMeshMikkTWrapper.h` |

### 头文件引入

```cpp
// 形状拟合
#include "PCA3.h"
#include "FitCapsule3.h"
#include "MinVolumeSphere3.h"
#include "MinVolumeBox3.h"

// 四面体网格
#include "FTetWildWrapper.h"

// UV 处理
#include "XAtlasWrapper.h"
#include "Parameterization/UVMetrics.h"

// 2D 多边形操作
#include "Curve/PolygonIntersectionUtils.h"
#include "Curve/PolygonOffsetUtils.h"

// 三角剖分
#include "ConstrainedDelaunay2.h"
#include "Arrangement2d.h"

// 曲线拟合
#include "Curve/BSplineCurveFit.h"

// 距离与相交
#include "Distance/DistLine3Circle3.h"
#include "Intersection/IntrCylinderBox3.h"

// 切线
#include "DynamicMeshMikkTWrapper.h"
```

### 基本用法

#### 1. 主成分分析（PCA）

从点集计算主方向，常用于对齐、包围体计算等场景。

```cpp
#include "PCA3.h"

using namespace UE::Geometry;

void ComputePCAExample()
{
    // 准备点集
    TArray<FVector> Points;
    Points.Add(FVector(0, 0, 0));
    Points.Add(FVector(10, 0, 0));
    Points.Add(FVector(0, 5, 0));
    Points.Add(FVector(10, 5, 0));
    Points.Add(FVector(5, 2.5, 0));

    // 计算 PCA
    FPCA3d PCA;
    FComputePCA3Options Options;
    Options.bSortEigenvalues = true;        // 按特征值降序排列
    Options.bScaleDataToUnitCube = true;    // 归一化到单位立方体

    bool bSuccess = PCA.Compute(
        TConstArrayView<FVector>(Points.GetData(), Points.Num()),
        Options
    );

    if (bSuccess)
    {
        // Mean: 点集中心
        FVector Center = PCA.Mean;
        
        // Eigenvectors[0]: 最大方差方向（主轴）
        FVector PrimaryAxis = PCA.Eigenvectors[0];
        
        // Eigenvalues: 各方向的方差
        FVector Variances = PCA.Eigenvalues;
    }
}
```

#### 2. 胶囊体拟合

从点集拟合最小包围胶囊体，用于碰撞体生成。

```cpp
#include "FitCapsule3.h"

using namespace UE::Geometry;

void FitCapsuleExample()
{
    // 准备点集
    TArray<FVector> Points;
    for (int32 i = 0; i < 100; ++i)
    {
        Points.Add(FVector(FMath::FRandRange(-10, 10),
                           FMath::FRandRange(-5, 5),
                           FMath::FRandRange(-2, 2)));
    }

    // 拟合胶囊体
    FCapsule3d Capsule;
    bool bSuccess = FFitCapsule3d::Solve(
        Points.Num(),
        [&Points](int32 Index) -> FVector { return Points[Index]; },
        Capsule
    );

    if (bSuccess)
    {
        // Capsule.Center: 胶囊中心
        // Capsule.Direction: 胶囊方向
        // Capsule.Radius: 半径
        // Capsule.Height: 高度（不含半球端）
        UE_LOG(LogTemp, Log, TEXT("Capsule: Radius=%.2f, Height=%.2f"),
               Capsule.Radius, Capsule.Height);
    }
}
```

#### 3. 最小包围球

```cpp
#include "MinVolumeSphere3.h"

using namespace UE::Geometry;

void MinVolumeSphereExample()
{
    TArray<FVector> Points = {
        FVector(1, 0, 0), FVector(-1, 0, 0),
        FVector(0, 1, 0), FVector(0, -1, 0),
        FVector(0, 0, 1), FVector(0, 0, -1)
    };

    FMinVolumeSphere3d Solver;
    bool bSuccess = Solver.Solve(
        Points.Num(),
        [&Points](int32 i) -> FVector { return Points[i]; },
        false  // bUseExactComputation: false 用 double，true 用高精度有理数（更慢但更精确）
    );

    if (bSuccess)
    {
        FSphere3d Sphere;
        Solver.GetResult(Sphere);
        // Sphere.Center: 球心
        // Sphere.Radius: 半径
    }
}
```

#### 4. 最小包围有向盒（OBB）

```cpp
#include "MinVolumeBox3.h"

using namespace UE::Geometry;

void MinVolumeBoxExample()
{
    TArray<FVector> Points;
    // ... 填充点集 ...

    FMinVolumeBox3d Solver;
    bool bSuccess = Solver.Solve(
        Points.Num(),
        [&Points](int32 i) -> FVector { return Points[i]; },
        false  // bMostAccurateFit: true 使用最精确（最慢）的方法
    );

    if (bSuccess)
    {
        FOrientedBox3d Box;
        Solver.GetResult(Box);
        // Box.Axis[0], Box.Axis[1], Box.Axis[2]: OBB 的三个轴
        // Box.Extents: 三个轴上的半尺寸
        // Box.Center: 中心点
    }

    // 对于大规模点集，可使用子采样版本加速
    FMinVolumeBox3d SolverSub;
    SolverSub.SolveSubsample(
        Points.Num(),
        1000,  // 最多采样 1000 个点
        [&Points](int32 i) -> FVector { return Points[i]; }
    );
}
```

#### 5. 2D 多边形布尔运算

```cpp
#include "Curve/PolygonIntersectionUtils.h"

using namespace UE::Geometry;

void PolygonBooleanExample()
{
    // 定义两个多边形（必须是闭合的）
    FGeneralPolygon2d PolygonA, PolygonB;
    // ... 设置多边形顶点 ...

    // 并集
    TArray<FGeneralPolygon2d> UnionResult;
    bool bOK = PolygonsUnion(
        {PolygonA, PolygonB},
        UnionResult,
        true  // bCopyInputOnFailure: 失败时复制输入到输出
    );

    // 差集（A - B）
    TArray<FGeneralPolygon2d> DiffResult;
    PolygonsDifference({PolygonA}, {PolygonB}, DiffResult);

    // 交集
    TArray<FGeneralPolygon2d> IntersectResult;
    PolygonsIntersection({PolygonA}, {PolygonB}, IntersectResult);

    // 异或
    TArray<FGeneralPolygon2d> XORResult;
    PolygonsExclusiveOr({PolygonA}, {PolygonB}, XORResult);
}
```

#### 6. 2D 多边形偏移（膨胀/收缩）

```cpp
#include "Curve/PolygonOffsetUtils.h"

using namespace UE::Geometry;

void PolygonOffsetExample()
{
    FGeneralPolygon2d Polygon;
    // ... 设置多边形 ...

    // 向外偏移 5 个单位，圆角连接
    TArray<FGeneralPolygon2d> OffsetResult;
    bool bOK = PolygonsOffset(
        5.0,                    // Offset: 正值向外，负值向内
        {Polygon},
        OffsetResult,
        true,                   // bCopyInputOnFailure
        2.0,                    // MiterLimit
        EPolygonOffsetJoinType::Round,  // 圆角
        EPolygonOffsetEndType::Polygon  // 闭合多边形模式
    );

    // 形态学开运算（先收缩再膨胀，去除小突起）
    TArray<FGeneralPolygon2d> OpenResult;
    PolygonsOffsets(
        -3.0,   // FirstOffset: 先收缩
        3.0,    // SecondOffset: 再膨胀
        {Polygon}, OpenResult, true, 2.0,
        EPolygonOffsetJoinType::Round
    );
}
```

#### 7. 约束 Delaunay 三角剖分

```cpp
#include "ConstrainedDelaunay2.h"

using namespace UE::Geometry;

void ConstrainedDelaunayExample()
{
    TConstrainedDelaunay2<double> Triangulator;

    // 添加顶点
    Triangulator.Vertices.Add(FVector2D(0, 0));
    Triangulator.Vertices.Add(FVector2D(10, 0));
    Triangulator.Vertices.Add(FVector2D(10, 10));
    Triangulator.Vertices.Add(FVector2D(0, 10));
    Triangulator.Vertices.Add(FVector2D(5, 5));  // 内部点

    // 添加边界边
    Triangulator.Edges.Add(FIndex2i(0, 1));
    Triangulator.Edges.Add(FIndex2i(1, 2));
    Triangulator.Edges.Add(FIndex2i(2, 3));
    Triangulator.Edges.Add(FIndex2i(3, 0));

    // 添加孔洞边（可选）
    // Triangulator.HoleEdges.Add(...);

    Triangulator.FillRule = TConstrainedDelaunay2<double>::EFillRule::NonZero;
    Triangulator.bSplitBowties = true;

    // 执行三角剖分
    TArray<FIndex3i> Triangles;
    bool bSuccess = Triangulator.Triangulate(Triangles);
}
```

#### 8. B 样条曲线拟合

```cpp
#include "Curve/BSplineCurveFit.h"

using namespace UE::Geometry;

void BSplineFitExample()
{
    // 3D 点集
    TArray<FVector3f> DataPoints;
    for (int32 i = 0; i < 50; ++i)
    {
        float t = (float)i / 49.0f;
        DataPoints.Add(FVector3f(t * 100, FMath::Sin(t * PI * 2) * 20, 0));
    }

    int32 SplineDegree = 3;       // 三次 B 样条
    int32 NumControlPoints = 10;   // 10 个控制点

    TArray<FVector3f> ControlPoints;
    bool bSuccess = BSplineCurveFit(
        DataPoints, SplineDegree, NumControlPoints, ControlPoints
    );

    // 要求: SplineDegree < NumControlPoints <= DataPoints.Num()
}
```

#### 9. 四面体网格生成（fTetWild）

```cpp
#include "FTetWildWrapper.h"

using namespace UE::Geometry;

void TetMeshExample()
{
    // 输入三角面片网格
    TArray<FVector> Vertices;
    TArray<FIntVector3> Faces;
    // ... 填充顶点和面 ...

    // 配置参数
    FTetWild::FTetMeshParameters Params;
    Params.IdealEdgeLengthRel = 0.05;  // 相对于包围盒的理想边长
    Params.EpsRel = 1e-3;              // 相对容差
    Params.MaxIts = 80;                // 最大优化迭代次数
    Params.bCoarsen = false;
    Params.OutsideFilterMethod = FTetWild::EFilterOutsideMethod::TrackedSurface;

    // 生成四面体网格
    TArray<FVector> OutVertices;
    TArray<FIntVector4> OutTets;

    FProgressCancel Progress;
    bool bSuccess = FTetWild::ComputeTetMesh(
        Params, Vertices, Faces,
        OutVertices, OutTets,
        &Progress  // 可选：支持取消和进度报告
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Tet mesh: %d vertices, %d tets"),
               OutVertices.Num(), OutTets.Num());
    }
}
```

#### 10. UV 质量指标

```cpp
#include "Parameterization/UVMetrics.h"

using namespace UE::Geometry;

void UVMetricsExample(const FDynamicMesh3& Mesh, int32 UVChannel)
{
    for (int32 Tid : Mesh.TriangleIndicesItr())
    {
        // Reed-Beta 拉伸度指标
        double ReedBeta = FUVMetrics::ReedBeta(Mesh, UVChannel, Tid);

        // Sander 拉伸度指标（L2 范数）
        double SanderL2 = FUVMetrics::Sander(Mesh, UVChannel, Tid, true);

        // 纹素密度（需要指定贴图尺寸）
        double TexDensity = FUVMetrics::TexelDensity(Mesh, UVChannel, Tid, 1024);
    }
}
```

### 进阶用法

#### 组合使用：从点云生成物理资产

```cpp
#include "PCA3.h"
#include "FitCapsule3.h"
#include "MinVolumeBox3.h"
#include "MinVolumeSphere3.h"

using namespace UE::Geometry;

struct FSimpleCollisionShape
{
    enum class EType { Capsule, Sphere, Box } Type;
    FCapsule3d Capsule;
    FSphere3d Sphere;
    FOrientedBox3d Box;
};

// 根据点集特征自动选择最佳包围体
FSimpleCollisionShape AutoFitCollision(const TArray<FVector>& Points)
{
    // 1. 先做 PCA 分析形状特征
    FPCA3d PCA;
    PCA.Compute(TConstArrayView<FVector>(Points.GetData(), Points.Num()));

    FVector AxisRatios = PCA.Eigenvalues;
    // Eigenvalues[0] >= Eigenvalues[1] >= Eigenvalues[2]（已排序）

    double Elongation = AxisRatios[0] / FMath::Max(AxisRatios[2], SMALL_NUMBER);
    double Flatness = AxisRatios[1] / FMath::Max(AxisRatios[2], SMALL_NUMBER);

    FSimpleCollisionShape Result;

    if (Elongation > 5.0)
    {
        // 细长形状 → 胶囊体
        Result.Type = FSimpleCollisionShape::EType::Capsule;
        FFitCapsule3d::Solve(
            Points.Num(),
            [&Points](int32 i) -> FVector { return Points[i]; },
            Result.Capsule
        );
    }
    else if (Flatness > 3.0)
    {
        // 扁平形状 → 有向盒
        Result.Type = FSimpleCollisionShape::EType::Box;
        FMinVolumeBox3d Solver;
        Solver.Solve(Points.Num(),
                     [&Points](int32 i) -> FVector { return Points[i]; });
        Solver.GetResult(Result.Box);
    }
    else
    {
        // 接近球形 → 球
        Result.Type = FSimpleCollisionShape::EType::Sphere;
        FMinVolumeSphere3d Solver;
        Solver.Solve(Points.Num(),
                     [&Points](int32 i) -> FVector { return Points[i]; });
        Solver.GetResult(Result.Sphere);
    }

    return Result;
}
```

#### 组合使用：2D 形状的膨胀 + 三角剖分

```cpp
#include "Curve/PolygonOffsetUtils.h"
#include "Curve/PolygonIntersectionUtils.h"
#include "ConstrainedDelaunay2.h"

using namespace UE::Geometry;

// 对多边形做膨胀后三角剖分（常用于生成导航网格或碰撞区域）
bool ExpandAndTriangulate(
    const FGeneralPolygon2d& InputPolygon,
    double ExpandAmount,
    TArray<FIndex3i>& OutTriangles)
{
    // 1. 膨胀多边形
    TArray<FGeneralPolygon2d> Expanded;
    if (!PolygonsOffset(ExpandAmount, {InputPolygon}, Expanded, true, 2.0,
                        EPolygonOffsetJoinType::Round))
    {
        return false;
    }

    // 2. 对膨胀结果做三角剖分
    for (const FGeneralPolygon2d& Poly : Expanded)
    {
        TConstrainedDelaunay2<double> Triangulator;

        // 添加外轮廓顶点
        const auto& Outer = Poly.GetOuter();
        int32 BaseIdx = Triangulator.Vertices.Num();
        for (const FVector2D& V : Outer.GetVertices())
        {
            Triangulator.Vertices.Add(V);
        }
        for (int32 i = 0; i < Outer.VertexCount(); ++i)
        {
            Triangulator.Edges.Add(FIndex2i(BaseIdx + i, BaseIdx + (i + 1) % Outer.VertexCount()));
        }

        // 添加孔洞
        for (const auto& Hole : Poly.GetHoles())
        {
            int32 HoleBase = Triangulator.Vertices.Num();
            for (const FVector2D& V : Hole.GetVertices())
            {
                Triangulator.Vertices.Add(V);
            }
            for (int32 i = 0; i < Hole.VertexCount(); ++i)
            {
                Triangulator.HoleEdges.Add(FIndex2i(HoleBase + i, HoleBase + (i + 1) % Hole.VertexCount()));
            }
        }

        Triangulator.FillRule = TConstrainedDelaunay2<double>::EFillRule::NonZero;
        Triangulator.bOrientedEdges = true;

        TArray<FIndex3i> Tris;
        if (Triangulator.Triangulate(Tris))
        {
            OutTriangles.Append(Tris);
        }
    }

    return OutTriangles.Num() > 0;
}
```

## Demo 示例

以下是一个完整的最小示例，演示从随机点集拟合包围体并生成四面体网格。

### MyGeometryExample.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyGeometryExample
{
public:
    /** 从点集拟合最小包围球并生成四面体网格 */
    static bool GenerateTetMeshFromPointCloud(
        const TArray<FVector>& Points,
        TArray<FVector>& OutTetVertices,
        TArray<FIntVector4>& OutTetFaces);
};
```

### MyGeometryExample.cpp

```cpp
#include "MyGeometryExample.h"

#include "MinVolumeSphere3.h"
#include "FTetWildWrapper.h"
#include "Util/ProgressCancel.h"

using namespace UE::Geometry;

bool FMyGeometryExample::GenerateTetMeshFromPointCloud(
    const TArray<FVector>& Points,
    TArray<FVector>& OutTetVertices,
    TArray<FIntVector4>& OutTetFaces)
{
    if (Points.Num() < 4)
    {
        return false;
    }

    // 1. 拟合最小包围球，获取点集的近似范围
    FMinVolumeSphere3d SphereSolver;
    if (!SphereSolver.Solve(
            Points.Num(),
            [&Points](int32 i) -> FVector { return Points[i]; }))
    {
        return false;
    }

    FSphere3d BoundingSphere;
    SphereSolver.GetResult(BoundingSphere);

    // 2. 用包围球生成一个粗糙的三角面片包围体（八面体细分）
    TArray<FVector> SurfaceVerts;
    TArray<FIntVector3> SurfaceFaces;

    // 生成八面体顶点
    double R = BoundingSphere.Radius * 1.1;  // 略大于包围球
    FVector C = BoundingSphere.Center;
    SurfaceVerts.Add(C + FVector(R, 0, 0));   // 0: +X
    SurfaceVerts.Add(C + FVector(-R, 0, 0));  // 1: -X
    SurfaceVerts.Add(C + FVector(0, R, 0));   // 2: +Y
    SurfaceVerts.Add(C + FVector(0, -R, 0));  // 3: -Y
    SurfaceVerts.Add(C + FVector(0, 0, R));   // 4: +Z
    SurfaceVerts.Add(C + FVector(0, 0, -R));  // 5: -Z

    // 八面体的 8 个三角面
    SurfaceFaces.Add(FIntVector3(0, 2, 4));
    SurfaceFaces.Add(FIntVector3(2, 1, 4));
    SurfaceFaces.Add(FIntVector3(1, 3, 4));
    SurfaceFaces.Add(FIntVector3(3, 0, 4));
    SurfaceFaces.Add(FIntVector3(2, 0, 5));
    SurfaceFaces.Add(FIntVector3(1, 2, 5));
    SurfaceFaces.Add(FIntVector3(3, 1, 5));
    SurfaceFaces.Add(FIntVector3(0, 3, 5));

    // 3. 使用 fTetWild 生成四面体网格
    FTetWild::FTetMeshParameters Params;
    Params.IdealEdgeLengthRel = 0.1;
    Params.EpsRel = 1e-2;
    Params.OutsideFilterMethod = FTetWild::EFilterOutsideMethod::TrackedSurface;

    FProgressCancel Progress;
    return FTetWild::ComputeTetMesh(
        Params, SurfaceVerts, SurfaceFaces,
        OutTetVertices, OutTetFaces, &Progress);
}
```

## 模块依赖

从 GeometryAlgorithms 模块的头文件依赖关系推断：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 基础几何类型（VectorTypes, BoxTypes, CapsuleTypes, SphereTypes, OrientedBoxTypes, LineTypes, CircleTypes, Polygon2, GeneralPolygon2 等） |
| `DynamicMesh` | 动态网格数据结构（FDynamicMesh3, FMeshTangents），被 UVMetrics 和 MikkT 切线计算使用 |

无特殊依赖（仅标准 Core/Engine 等 + 上述几何模块）。

> **注意**：如果你的模块需要使用 GeometryAlgorithms，需在 Build.cs 中添加对 `GeometryAlgorithms` 的依赖。如果直接使用 `FDynamicMesh3` 等类型，还需依赖 `DynamicMesh`。

## 维护状态

### 近期更新

```
- 41018735fbcb CIS fix for dynamic mesh mikkt wrapper non-unity build on platforms that don't support mikkt: add missing UE::Geometry namespace
- 4ca983de48aa fix trianglecount -> max triangle ID in dynamic mesh mikkt wrapper -- could result in non-compact meshes missing tangents for triangles w/ IDs > triangle count + guard against negative uv layer being requested
- 9046d138c10a move dynamic mesh mikkt support out of the calculate tangents op so it can be used by geometry script + fix handling of unset elements (normals, uvs) in the mesh overlay
```

近期更新集中在 **MikkT 切线计算** 的修复和重构：
- 修复非紧凑网格（triangle ID > triangle count）丢失切线的问题
- 修复负 UV 层请求的边界检查
- 将 MikkT 支持从 CalculateTangents Op 中抽出，使其可被 Geometry Script 直接调用
- 修复 non-unity build 的命名空间问题

### 维护评价

- **年龄**：约 6 年（2019 年至今），源自 geometry3Sharp 移植
- **维护状态**：**活跃维护中** — 近期有实质性 bug 修复和 API 重构
- **Beta 状态**：插件仍标记为 `IsBetaVersion: true`，API 可能发生变化
- **重要性**：作为 Geometry Script、MeshModelingToolset、Chaos 物理系统等的底层依赖，不太可能被废弃
- **推荐使用**：✅ 推荐用于需要底层几何算法的 C++ 项目。不建议直接在蓝图中使用（请通过 Geometry Script）。注意 Beta 状态意味着 API 可能在版本间发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing)
- [Geometry Script 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryScripting)（蓝图友好的上层封装）
- [MeshModelingToolset 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)（建模工具，使用本插件的算法）
- [geometry3Sharp 原始项目](https://github.com/gradientspace/geometry3Sharp)（本插件的算法来源）