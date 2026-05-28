# Fracture

> Adds Module for FractureEditor（为 FractureEditor 提供破碎算法实现库）

| 属性 | 值 |
|---|---|
| 中文名 | 破碎引擎 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-17 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Fracture) | |

## 用途

Fracture 插件是 Chaos 物理破碎系统的核心算法库，为 ChaosEditor/FractureEditor 提供底层破碎实现。它封装了多种网格切割与破碎算法（Voronoi 破碎、平面切割、网格切割、砖块切割等），以及 GeometryCollection 上的聚类、采样、选择、材质分配、凸包处理等工具函数。

该插件本身不提供编辑器 UI，而是作为纯算法层被上层的 FractureEditor 调用。所有接口均为 `static` 函数，操作 `FManagedArrayCollection`（即 GeometryCollection 的底层数据结构）。

**注意**：该插件默认未启用（`EnabledByDefault=false`），且为实验性（`IsBetaVersion=true`），依赖 `PlanarCut` 插件。

## 使用场景

- 你需要在运行时对 GeometryCollection 执行 Voronoi 破碎 → 用 `FFractureEngineFracturing::VoronoiFracture`
- 你需要用网格形状作为切割器切割几何体 → 用 `FFractureEngineFracturing::MeshCutter` / `MeshArrayCutter`
- 你需要对破碎结果进行自动聚类（合并碎片为更大的刚体组） → 用 `FFractureEngineClustering::AutoCluster`
- 你需要在网格表面采样 Voronoi 种子点 → 用 `FFractureEngineSampling::ComputeUniformPointSampling`
- 你需要选择特定层级/大小/体积的骨骼进行操作 → 用 `FFractureEngineSelection` 提供的选择函数
- 你需要简化 GeometryCollection 的凸包碰撞体 → 用 `FractureEngine::Convex::SimplifyConvexHulls`
- 你需要修复过小碎片（merge tiny geometry） → 用 `FFractureEngineUtility::FixTinyGeo`

## 蓝图用法

该插件的所有公开类和函数均为 C++ static 方法，标记了 `UE_API`/`FRACTUREENGINE_API` 导出宏。虽然部分枚举（如 `EFractureBrickBondEnum`、`EMeshCutterCutDistribution` 等）标记了 `BlueprintType`，但核心操作函数本身不是 `BlueprintCallable`，主要面向 Dataflow 和 C++ 编程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `VoronoiFracture` | 使用 Voronoi 算法破碎 GeometryCollection | `FFractureEngineFracturing` |
| `PlaneCutter` | 使用随机平面切割 | `FFractureEngineFracturing` |
| `SliceCutter` | 使用规则网格切片切割 | `FFractureEngineFracturing` |
| `BrickCutter` | 使用砖块排列模式切割 | `FFractureEngineFracturing` |
| `MeshCutter` | 使用单个网格形状作为切割器 | `FFractureEngineFracturing` |
| `MeshArrayCutter` | 使用多个网格形状数组作为切割器 | `FFractureEngineFracturing` |
| `UniformFracture` | 统一随机破碎 | `FFractureEngineFracturing` |
| `AutoCluster` | 自动聚类碎片 | `FFractureEngineClustering` |
| `FixTinyGeo` | 修复/合并过小碎片 | `FFractureEngineUtility` |
| `ComputeUniformPointSampling` | 均匀泊松采样 | `FFractureEngineSampling` |
| `SimplifyConvexHulls` | 简化凸包碰撞体 | `FractureEngine::Convex` |

## C++ 用法

### 头文件引入

```cpp
#include "FractureEngineFracturing.h"
#include "FractureEngineClustering.h"
#include "FractureEngineSampling.h"
#include "FractureEngineUtility.h"
#include "FractureEngineConvex.h"
#include "FractureEngineSelection.h"
#include "FractureEngineMaterials.h"
#include "FractureEngineEdit.h"
```

### 基本用法 — Voronoi 破碎

对 GeometryCollection 执行 Voronoi 破碎是该插件最核心的功能。

```cpp
#include "FractureEngineFracturing.h"

// 对 GeometryCollection 的指定层级执行 Voronoi 破碎
FManagedArrayCollection& Collection = GeometryCollection->GetManagedCollection();

// 选择要破碎的骨骼
FDataflowTransformSelection TransformSelection;
// ... 设置选择

// 定义 Voronoi 种子点
TArray<FVector> Sites;
Sites.Add(FVector(0, 0, 0));
Sites.Add(FVector(100, 0, 0));
Sites.Add(FVector(0, 100, 0));

FTransform Transform = FTransform::Identity;
FIslandSplitSettings IslandSplitSettings;

int32 NumFractured = FFractureEngineFracturing::VoronoiFracture(
    Collection,
    TransformSelection,
    Sites,
    Transform,
    /*RandomSeed=*/42,
    /*ChanceToFracture=*/1.0f,
    IslandSplitSettings,
    /*Grout=*/0.0f,
    /*Amplitude=*/0.0f,    // 噪声参数
    /*Frequency=*/0.0f,
    /*Persistence=*/0.0f,
    /*Lacunarity=*/0.0f,
    /*OctaveNumber=*/0,
    /*PointSpacing=*/1.0f,
    /*AddSamplesForCollision=*/false,
    /*CollisionSampleSpacing=*/0.0f
);

// NumFractured 返回实际破碎的骨骼数量
```

### 基本用法 — 采样 Voronoi 种子点

在网格表面均匀采样，生成 Voronoi 破碎所需的种子点：

```cpp
#include "FractureEngineSampling.h"

// 在网格表面执行泊松盘采样
const UE::Geometry::FDynamicMesh3& Mesh = /* 你的网格 */;
TArray<FTransform> Samples;
TArray<int32> TriangleIDs;
TArray<FVector> BarycentricCoords;

FFractureEngineSampling::ComputeUniformPointSampling(
    Mesh,
    /*SamplingRadius=*/10.0f,     // 采样点之间的最小间距
    /*MaxNumSamples=*/500,         // 最大采样数
    /*SubSampleDensity=*/0.01f,    // 子采样密度
    /*RandomSeed=*/42,
    Samples,
    TriangleIDs,
    BarycentricCoords
);

// 将采样结果转换为 Voronoi 种子点
TArray<FVector> Sites;
for (const FTransform& Sample : Samples)
{
    Sites.Add(Sample.GetLocation());
}
```

### 进阶用法 — 自动聚类与碎片修复

破碎后通常需要对碎片进行聚类，并修复过小碎片：

```cpp
#include "FractureEngineClustering.h"
#include "FractureEngineUtility.h"

FGeometryCollection& GeoCollection = *GeometryCollection;
int32 ClusterIndex = 0; // 要聚类的层级索引

// 按网格密度自动聚类，使用 2x2x2 的网格
FFractureEngineClustering::AutoCluster(
    GeoCollection,
    ClusterIndex,
    EFractureEngineClusterSizeMethod::ByGrid,
    /*SiteCount=*/8,
    /*SiteCountFraction=*/0.5f,
    /*SiteSize=*/100.0f,
    /*bEnforceConnectivity=*/true,    // 确保连通性
    /*bAvoidIsolated=*/true,          // 避免孤立碎片
    /*bEnforceSiteParameters=*/false,
    /*GridX=*/2, /*GridY=*/2, /*GridZ=*/2,
    /*MinimumClusterSize=*/0,
    /*KMeansIterations=*/500
);

// 修复过小碎片：合并到最近邻
FDataflowTransformSelection TransformSelection;
FFractureEngineUtility::FixTinyGeo(
    Collection,
    TransformSelection,
    EFixTinyGeoMergeType::MergeGeometry,          // 合并几何体而非聚类
    /*OnFractureLevel=*/true,
    EFixTinyGeoGeometrySelectionMethod::VolumeCubeRoot,
    /*MinVolumeCubeRoot=*/1.0f,                    // 体积立方根阈值
    /*RelativeVolume=*/0.0f,
    EFixTinyGeoUseBoneSelection::NoEffect,
    /*OnlyClusters=*/false,
    EFixTinyGeoNeighborSelectionMethod::NearestCenter,  // 合并到最近中心的邻居
    /*OnlyToConnected=*/true,                      // 只合并到连通的邻居
    /*OnlySameParent=*/true                        // 只合并到同父级的邻居
);
```

### 进阶用法 — 凸包简化

为提升运行时碰撞性能，简化 GeometryCollection 的凸包碰撞体：

```cpp
#include "FractureEngineConvex.h"

UE::FractureEngine::Convex::FSimplifyHullSettings Settings;
Settings.SimplifyMethod = EConvexHullSimplifyMethod::MeshQSlim;
Settings.bUseGeometricTolerance = true;
Settings.ErrorTolerance = 5.0;          // 几何误差容忍度
Settings.bUseTargetTriangleCount = false;
Settings.bUseExistingVertexPositions = true;

// 简化所有凸包
bool bSuccess = UE::FractureEngine::Convex::SimplifyConvexHulls(
    Collection,
    Settings,
    /*bRestrictToSelection=*/false
);
```

## Demo 示例

一个完整的可编译最小示例，演示如何使用 FractureEngine 模块执行破碎操作：

```cpp
// MyFractureExample.h
#pragma once

#include "CoreMinimal.h"

class FMyFractureExample
{
public:
    /**
     * 对传入的 GeometryCollection 执行随机 Voronoi 破碎，
     * 然后自动聚类并修复过小碎片。
     */
    static void FractureAndCluster(
        FGeometryCollection& GeometryCollection,
        int32 ClusterIndex,
        int32 NumVoronoiSites,
        int32 RandomSeed);
};
```

```cpp
// MyFractureExample.cpp
#include "MyFractureExample.h"

#include "FractureEngineFracturing.h"
#include "FractureEngineClustering.h"
#include "FractureEngineUtility.h"
#include "FractureEngineSelection.h"
#include "GeometryCollection/GeometryCollection.h"

void FMyFractureExample::FractureAndCluster(
    FGeometryCollection& GeometryCollection,
    int32 ClusterIndex,
    int32 NumVoronoiSites,
    int32 RandomSeed)
{
    FManagedArrayCollection& Collection = GeometryCollection.GetManagedCollection();

    // 1. 获取该层级的根骨骼
    TArray<int32> RootBones;
    FFractureEngineSelection::GetRootBones(Collection, RootBones);
    if (RootBones.Num() == 0)
    {
        return;
    }

    // 2. 使用 UniformFracture 进行破碎
    FDataflowTransformSelection TransformSelection;
    FUniformFractureSettings FractureSettings;
    FractureSettings.Transform = FTransform::Identity;
    FractureSettings.MinVoronoiSites = NumVoronoiSites;
    FractureSettings.MaxVoronoiSites = NumVoronoiSites;
    FractureSettings.InternalMaterialID = 0;
    FractureSettings.RandomSeed = RandomSeed;
    FractureSettings.ChanceToFracture = 1.0f;
    FractureSettings.GroupFracture = false;
    FractureSettings.SplitIslands = true;
    FractureSettings.CloseVertexDistance = 1e-3;
    FractureSettings.VertexToSurfaceBridgeDistance = 0;
    FractureSettings.Grout = 0.0f;
    FractureSettings.AddSamplesForCollision = false;
    FractureSettings.CollisionSampleSpacing = 0.0f;

    FFractureEngineFracturing::UniformFracture(
        Collection, TransformSelection, FractureSettings);

    // 3. 自动聚类：按网格分布，强制连通性
    FFractureEngineClustering::AutoCluster(
        GeometryCollection,
        ClusterIndex,
        EFractureEngineClusterSizeMethod::ByGrid,
        8, 0.5f, 100.0f,
        /*bEnforceConnectivity=*/true,
        /*bAvoidIsolated=*/true,
        /*bEnforceSiteParameters=*/false,
        2, 2, 2
    );

    // 4. 修复过小碎片
    FDataflowTransformSelection FixSelection;
    FFractureEngineUtility::FixTinyGeo(
        Collection, FixSelection,
        EFixTinyGeoMergeType::MergeGeometry,
        true,
        EFixTinyGeoGeometrySelectionMethod::VolumeCubeRoot,
        1.0f, 0.0f,
        EFixTinyGeoUseBoneSelection::NoEffect,
        false,
        EFixTinyGeoNeighborSelectionMethod::NearestCenter,
        true, true
    );

    // 5. 验证 GeometryCollection 完整性
    FFractureEngineUtility::ValidateGeometryCollection(
        Collection,
        /*bRemoveUnreferencedGeometry=*/true,
        /*bRemoveClustersOfOne=*/true,
        /*bRemoveDanglingClusters=*/true
    );
}
```

## 模块依赖

从 FractureEngine.Build.cs 和 .uplugin 的 Plugins 字段提取：

| 模块 | 用途 |
|---|---|
| `PlanarCut` | 平面切割算法，FractureEngine 的核心依赖插件 |
| `GeometryCore` | 动态网格（FDynamicMesh3）操作 |
| `GeometryCollectionEngine` | GeometryCollection 运行时数据结构 |
| `Chaos` | Chaos 物理引擎，凸包碰撞体处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `057caa09` | Add a split islands dataflow node + associated function in fracture engine utility | 新增拆分岛屿 Dataflow 节点及 FractureEngine 中对应函数 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-31 | `1843540e` | Add new split island controls to dataflow fracture and mesh-to-collection nodes | 为 Dataflow 破碎和网格转集合节点新增拆分岛屿控制参数 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 静态分析抑制标记 |
| 2026-01-22 | `49ee3dfa` | Geometry collection - fix crash when merging a single root bone that has an single embedded geometry | 修复合并含单个嵌入几何体的单根骨骼时的崩溃 |

### 维护评价

- **年龄**：约 4 年（2022 年创建），仍属较新插件
- **活跃度**：近 3 个月内有多次功能更新（split islands 功能），持续活跃维护中
- **状态**：标记为实验性（`IsBetaVersion=true`）且默认未启用，API 可能随版本变化
- **已知限制**：纯 C++ 算法库，不直接暴露蓝图节点（枚举有 `BlueprintType` 但函数非 `BlueprintCallable`）；依赖 PlanarCut 插件
- **推荐**：如果你正在开发 Dataflow 破碎工具链或需要程序化破碎，这是核心依赖库，推荐使用。但注意它是实验性模块，生产环境需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Fracture)
- 测试用例：该插件目录内未发现独立测试文件