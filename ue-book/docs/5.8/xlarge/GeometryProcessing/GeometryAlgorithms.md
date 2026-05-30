# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry

| 属性 | 值 |
|---|---|
| 中文名 | 几何处理 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-26 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 是 UE5 的底层几何计算基础设施，提供处理 2D 和 3D 几何体所需的核心数据结构和算法库。它不是面向设计师的可视化工具，而是供引擎内部模块和高级程序员使用的纯 C++ 算法库。

该插件封装了大量经典计算几何算法，核心功能包括：

- **三角剖分**：2D/3D Delaunay 三角剖分、约束 Delaunay 三角剖分（CDT）
- **凸包计算**：2D/3D 凸包（分治法和增量法）
- **几何拟合**：最小二乘拟合圆柱体、锥体、环面、椭圆、多项式曲面等
- **距离查询**：点/线/段/圆/球/盒/截锥体之间的最近距离计算
- **曲面与曲线**：B 样条、NURBS 曲线/曲面/体的拟合和求值
- **2D 多边形运算**：Clipper2 库支持布尔运算（并/交/差）、偏移等
- **精确算术**：BSNumber/BSRational 任意精度数值类型，用于需要绝对正确的几何谓词
- **数值方法**：Cholesky 分解、Gauss-Newton 最小化、Levenberg-Marquardt 优化等

插件集成了两个主要第三方库：**Geometric Tools Engine (GTEngine)**（David Eberly 的计算几何库）和 **Clipper2**（多边形裁剪库），并在其基础上添加了 UE 特有的适配代码。

## 使用场景

- 你需要对点集进行 Delaunay 三角剖分生成网格 → 用 `Delaunay2`/`Delaunay3`
- 你需要计算一组点的凸包 → 用 `ConvexHull2`/`ConvexHull3`
- 你需要计算两个线段/圆/球之间的最近距离 → 用 `DCPQuery` 系列
- 你需要对 2D 多边形进行布尔运算或偏移 → 用 Clipper2 库
- 你需要从点云数据拟合一个圆柱体/锥体/环面 → 用 `ApprCylinder3`/`ApprCone3`/`ApprTorus3`
- 你需要通过采样数据拟合 B 样条曲面 → 用 `BSplineSurfaceFit`
- 你需要在几何算法中获得绝对精确的结果 → 用 `BSNumber`/`BSRational` 精确算术

## 蓝图用法

此插件主要提供纯 C++ 算法，不包含 Blueprint 节点。所有功能均通过 C++ API 访问。

如需在蓝图中使用几何处理功能，可通过自定义的 BlueprintCallable 函数包装器暴露特定算法。

## C++ 用法

### 头文件引入

```cpp
// 核心几何算法
#include "GeometryAlgorithms.h"

// 第三方库头文件
#include "ThirdParty/GTEngine/Mathematics/GteConvexHull3.h"
#include "ThirdParty/GTEngine/Mathematics/GteDelaunay2.h"
#include "ThirdParty/GTEngine/Mathematics/GteDistSegmentSegment.h"
#include "ThirdParty/clipper/clipper.h"
```

### 基本用法

#### 2D Delaunay 三角剖分

```cpp
#include "ThirdParty/GTEngine/Mathematics/GteDelaunay2.h"

// 定义点集
std::vector<gte::Vector2<double>> Points;
Points.push_back({0.0, 0.0});
Points.push_back({1.0, 0.0});
Points.push_back({0.5, 1.0});
Points.push_back({0.3, 0.4});
Points.push_back({0.7, 0.6});

// 计算 Delaunay 三角剖分
gte::Delaunay2<double, double> delaunay;
bool success = delaunay(static_cast<int>(Points.size()), Points.data(), 0.0);

if (success && delaunay.GetDimension() == 2)
{
    // 获取三角形索引（每三个索引构成一个三角形）
    const std::vector<int>& Indices = delaunay.GetIndices();
    int NumTriangles = delaunay.GetNumTriangles();

    for (int i = 0; i < NumTriangles; ++i)
    {
        std::array<int, 3> TriIndices;
        delaunay.GetIndices(i, TriIndices);
        // 使用 TriIndices[0], TriIndices[1], TriIndices[2]
    }
}
```

#### 3D 凸包计算

```cpp
#include "ThirdParty/GTEngine/Mathematics/GteConvexHull3.h"

std::vector<gte::Vector3<double>> Points;
Points.push_back({0.0, 0.0, 0.0});
Points.push_back({1.0, 0.0, 0.0});
Points.push_back({0.0, 1.0, 0.0});
Points.push_back({0.0, 0.0, 1.0});
Points.push_back({0.5, 0.5, 0.5});

gte::ConvexHull3<double, double> hull;
bool success = hull(static_cast<int>(Points.size()), Points.data(), 0.0);

if (success && hull.GetDimension() == 3)
{
    // 获取无序三角面片
    const std::vector<gte::TriangleKey<true>>& HullFaces = hull.GetHullUnordered();
    for (const auto& Face : HullFaces)
    {
        int v0 = Face.V[0], v1 = Face.V[1], v2 = Face.V[2];
        // 使用面片顶点索引
    }
}
```

#### 线段间最近距离

```cpp
#include "ThirdParty/GTEngine/Mathematics/GteDistSegmentSegment.h"

gte::Vector3<double> P0{0, 0, 0}, P1{1, 0, 0};
gte::Vector3<double> Q0{0.5, 1, 0}, Q1{0.5, 1, 1};

gte::DCPSegment3Segment3<double> query;
auto result = query(P0, P1, Q0, Q1);

double distance = result.distance;       // 最近距离
double sqDistance = result.sqrDistance;   // 距离平方
gte::Vector3<double> closestOnSeg0 = result.closest[0];  // 线段0上最近点
gte::Vector3<double> closestOnSeg1 = result.closest[1];  // 线段1上最近点
double s = result.parameter[0];  // 线段0上的参数
double t = result.parameter[1];  // 线段1上的参数
```

### 进阶用法

#### 约束 Delaunay 三角剖分（带约束边）

```cpp
#include "ThirdParty/GTEngine/Mathematics/GteConstrainedDelaunay2.h"

std::vector<gte::Vector2<double>> Vertices;
// ... 添加顶点 ...

gte::ConstrainedDelaunay2<double, double> cdt;
bool success = cdt(static_cast<int>(Vertices.size()), Vertices.data(), 0.0);

if (success)
{
    // 插入约束边（顶点索引对）
    std::array<int, 2> constraintEdge = {0, 3};
    std::vector<int> outEdge;
    cdt.Insert(constraintEdge, outEdge);

    // outEdge 包含约束边上实际使用的顶点序列
    // 获取最终三角剖分
    const std::vector<int>& Indices = cdt.GetIndices();
}
```

#### 点到截锥体（Frustum）最近距离

```cpp
#include "ThirdParty/GTEngine/Mathematics/GteDistPoint3Frustum3.h"

gte::Frustum3<double> frustum;
frustum.origin = {0, 0, 0};
frustum.dVector = {0, 0, 1};   // 朝向
frustum.uVector = {0, 1, 0};   // 上方向
frustum.rVector = {1, 0, 0};   // 右方向
frustum.dMin = 1.0;            // 近裁剪面距离
frustum.dMax = 10.0;           // 远裁剪面距离
frustum.uBound = 2.0;          // 近裁剪面上边界
frustum.rBound = 3.0;          // 近裁剪面右边界

gte::Vector3<double> testPoint{5, 0, 5};
gte::DCPQuery<double, gte::Vector3<double>, gte::Frustum3<double>> query;
auto result = query(testPoint, frustum);

double distToFrustum = result.distance;
gte::Vector3<double> closestOnFrustum = result.frustumClosestPoint;
```

#### 几何体拟合（圆柱体拟合）

```cpp
#include "ThirdParty/GTEngine/Mathematics/GteApprCylinder3.h"

std::vector<gte::Vector3<double>> Points;
// ... 添加圆柱体附近的点云数据 ...

// 方法1：通过半球搜索找到最优轴方向
gte::ApprCylinder3<double> fitter(
    0,    // numThreads（0 = 单线程）
    32,   // theta 采样数
    16    // phi 采样数
);

gte::Cylinder3<double> cylinder;
double error = fitter(static_cast<unsigned int>(Points.size()),
    Points.data(), cylinder);

// cylinder.axis.origin   = 圆柱体中心
// cylinder.axis.direction = 轴方向
// cylinder.radius        = 半径
// cylinder.height        = 高度

// 方法2：使用协方差特征向量
gte::ApprCylinder3<double> fitter2(0u); // eigenIndex=0（最小特征值）
double error2 = fitter2(static_cast<unsigned int>(Points.size()),
    Points.data(), cylinder);
```

## Demo 示例

以下示例演示如何使用 Delaunay 三角剖分生成网格数据，并构建 DynamicMesh。

### MyGeometryActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "MyGeometryActor.generated.h"

UCLASS()
class AMyGeometryActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGeometryActor();

    // 从 Delaunay 三角剖分生成 DynamicMesh
    UE::Geometry::FDynamicMesh3 CreateMeshFromDelaunay(
        const TArray<FVector2D>& Points2D, float Height);

protected:
    virtual void BeginPlay() override;
};
```

### MyGeometryActor.cpp

```cpp
#include "MyGeometryActor.h"

// 注意：以下头文件来自 GeometryProcessing 插件的 GeometryAlgorithms 模块
#include "ThirdParty/GTEngine/Mathematics/GteDelaunay2.h"
#include "DynamicMesh/DynamicMesh3.h"

AMyGeometryActor::AMyGeometryActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGeometryActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建测试点集
    TArray<FVector2D> TestPoints;
    TestPoints.Add(FVector2D(0.0, 0.0));
    TestPoints.Add(FVector2D(5.0, 0.0));
    TestPoints.Add(FVector2D(3.0, 4.0));
    TestPoints.Add(FVector2D(1.0, 2.0));
    TestPoints.Add(FVector2D(4.0, 2.5));

    UE::Geometry::FDynamicMesh3 Mesh = CreateMeshFromDelaunay(TestPoints, 100.0f);
    // 使用 Mesh 进行后续渲染或导出...
}

UE::Geometry::FDynamicMesh3 AMyGeometryActor::CreateMeshFromDelaunay(
    const TArray<FVector2D>& Points2D, float Height)
{
    UE::Geometry::FDynamicMesh3 Mesh;
    Mesh.EnableVertexNormals(FVector3f::Zero());
    Mesh.EnableVertexUVs(FVector2f::Zero());

    if (Points2D.Num() < 3)
    {
        return Mesh;
    }

    // 转换为 gte 格式
    std::vector<gte::Vector2<double>> GtePoints;
    GtePoints.reserve(Points2D.Num());
    for (const FVector2D& Pt : Points2D)
    {
        GtePoints.push_back({static_cast<double>(Pt.X), static_cast<double>(Pt.Y)});
    }

    // 执行 2D Delaunay 三角剖分
    gte::Delaunay2<double, double> Delaunay;
    bool bSuccess = Delaunay(static_cast<int>(GtePoints.size()), GtePoints.data(), 0.0);

    if (!bSuccess || Delaunay.GetDimension() != 2)
    {
        return Mesh;
    }

    // 添加顶点（底面 + 顶面）
    int32 NumBaseVertices = Points2D.Num();
    for (int32 i = 0; i < NumBaseVertices; ++i)
    {
        FVector3d BaseVertex(Points2D[i].X, Points2D[i].Y, 0.0);
        Mesh.AppendVertex(BaseVertex);

        FVector3d TopVertex(Points2D[i].X, Points2D[i].Y, static_cast<double>(Height));
        Mesh.AppendVertex(TopVertex);
    }

    // 从 Delaunay 结果创建底面和顶面三角形
    const std::vector<int>& Indices = Delaunay.GetIndices();
    int32 NumTriangles = Delaunay.GetNumTriangles();

    for (int32 i = 0; i < NumTriangles; ++i)
    {
        std::array<int, 3> TriIndices;
        Delaunay.GetIndices(i, TriIndices);

        // 底面三角形（法线朝下）
        Mesh.AppendTriangle(TriIndices[0], TriIndices[2], TriIndices[1]);

        // 顶面三角形（法线朝上，偏移顶点数）
        Mesh.AppendTriangle(
            NumBaseVertices + TriIndices[0],
            NumBaseVertices + TriIndices[1],
            NumBaseVertices + TriIndices[2]);
    }

    return Mesh;
}
```

## 模块依赖

该插件的 Build.cs 主要依赖常见模块，对使用者来说无特殊依赖。你的模块只需要在 Build.cs 中添加对 GeometryProcessing 相关模块的引用：

```csharp
// 在你的 .Build.cs 中
PublicDependencyModuleNames.AddRange(new string[] {
    "GeometryAlgorithms",  // 核心几何算法
    "DynamicMesh"          // 动态网格数据结构（如需使用）
});
```

如果需要使用第三方 GTEngine 或 Clipper2 的功能，直接 include 对应的 ThirdParty 头文件即可，无需额外链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `35f4c4a4` | Fix float overflow warning for arm64 build | 修复 ARM64 构建的浮点溢出警告 |
| 2026-05-15 | `35f66cf1` | Guard against INDEX_NONE / invalid edge id in hole fill util's fill color method | 填充颜色方法中防止无效边 ID 导致崩溃 |
| 2026-05-13 | `2c7d172e` | Clamp UV values to max float when invalid value is in returned as double (max double). | UV 值从 double 转 float 时钳制到最大浮点值 |
| 2026-05-12 | `64deb517` | Hook up AttributeAwareV2 simplifier in MeshTerrainStaticMeshTransformer | 在地形静态网格转换器中接入 V2 简化器 |
| 2026-05-12 | `68fbe22e` | [SkeletalMeshModelingTools] clamp smooth strength to 0 - 1 | 骨骼网格建模工具平滑强度钳制到 0-1 范围 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐

- **创建时间**：2021年7月从 Experimental 迁移到 Runtime，之前已有更长的实验期
- **最近更新**：2026年5月仍有持续的 bug 修复和功能改进
- **代码规模**：734个源文件，是 UE5 中规模最大的几何计算库之一
- **核心地位**：作为 Geometry 底层基础库，被 GeometryScript、MeshModelingTools 等多个上层插件依赖
- **Beta 状态**：标记为 `IsBetaVersion=true`，API 可能在未来版本中发生变化
- **支持程序**：.uplugin 中声明支持 ChaosVisualDebugger，暗示与物理调试工具集成
- **已知限制**：第三方库（GTEngine、Clipper2）被集成在 Private 目录中，版本更新可能滞后于上游

**推荐使用**：对于需要底层几何算法的 C++ 开发者强烈推荐。这是 UE5 几何处理的基石库。但请注意 Beta 状态，生产环境中应做好 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryProcessing)
- [Geometric Tools Engine (GTEngine)](https://www.geometrictools.com/) - 第三方几何算法库
- [Clipper2](https://angusj.com/clipper2/Docs/Overview.htm) - 第三方多边形裁剪库
- [GeometryScript](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GeometryScriptConverter) - 基于此插件构建的蓝图几何脚本系统