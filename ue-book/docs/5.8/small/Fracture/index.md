# Fracture

> Adds Module for FractureEditor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 破裂引擎 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-17 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Fracture) | |

## 用途

Fracture 插件提供了 **Geometry Collection 破裂算法的核心运行时库**。它是 Chaos Destruction 系统编辑器端（FractureEditor）的底层算法实现模块，包含了对几何体进行各种方式切割、碎片聚类、采样、凸包简化等完整的工具链。

这个插件解决的核心问题：在编辑器中对静态网格体进行预破碎（pre-fracture）处理时，需要将几何体按不同策略（Voronoi、平面、切片、砖块、自定义网格）切割成碎片，并对碎片进行聚类管理、质量优化（修复微小几何体、重新采样碰撞数据、简化凸包等）。这些算法以纯 Runtime 模块形式存在，以便在数据流（Dataflow）节点和其他运行时场景中复用。

## 使用场景

- 你在使用 Chaos Destruction 系统对建筑物/岩石/玻璃进行预破碎 → 使用 Voronoi/Plane/Slice/Brick/Mesh 切割算法
- 你需要对破碎后的碎片进行自动聚类（AutoCluster），按空间位置或凸性分组 → 使用 FFractureEngineClustering
- 你要优化破碎结果：修复微小碎片、重新计算法线、重采样碰撞数据、简化碰撞凸包 → 使用 FFractureEngineUtility 和 FFractureEngineConvex
- 你需要对网格表面进行泊松采样以生成破碎种子点 → 使用 FFractureEngineSampling
- 你在 Dataflow 图中构建自定义破碎节点 → 调用 FractureEngine 中的静态函数

## 蓝图用法

该插件的源码中 **没有** `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标注的蓝图 API。所有功能均为 C++ 静态函数，供编辑器工具和 Dataflow 节点在 C++ 层调用。

如需在蓝图中使用破碎功能，请通过 Chaos Destruction 编辑器工具或 Dataflow 节点间接访问。

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

### 基本用法

#### Voronoi 破碎

```cpp
// 使用 Voronoi 算法对 Geometry Collection 进行破碎
// 来源: FractureEngineFracturing.h

FManagedArrayCollection& Collection = /* 获取 Geometry Collection 的底层数据 */;
FDataflowTransformSelection TransformSelection; // 要破碎的变换选择

// 定义 Voronoi 种子点
TArray<FVector> Sites;
Sites.Add(FVector(0, 0, 0));
Sites.Add(FVector(100, 100, 0));
Sites.Add(FVector(-100, 50, 0));

FTransform Transform = FTransform::Identity;
int32 RandomSeed = 42;

// 调用 Voronoi 破碎
int32 NewBoneCount = FFractureEngineFracturing::VoronoiFracture(
    Collection,
    TransformSelection,
    Sites,
    Transform,
    RandomSeed,
    1.0f,               // ChanceToFracture
    FIslandSplitSettings(), // 岛屿分割设置
    0.0f,               // Grout (灌浆宽度)
    0.0f, 0.0f, 0.0f, 0.0f, 0, // 噪声参数
    1.0f,               // PointSpacing
    true,               // AddSamplesForCollision
    5.0f                // CollisionSampleSpacing
);
```

#### 平面切割与切片切割

```cpp
// 来源: FractureEngineFracturing.h

FBox BoundingBox(FVector(-200, -200, -200), FVector(200, 200, 200));
FTransform Transform = FTransform::Identity;
int32 RandomSeed = 42;

// 生成随机切面变换
TArray<FTransform> CutPlanes;
FFractureEngineFracturing::GenerateSliceTransforms(BoundingBox, RandomSeed, 5, CutPlanes);

// 使用平面切割器
FFractureEngineFracturing::PlaneCutter(
    Collection, TransformSelection, BoundingBox, Transform,
    5,                  // NumPlanes
    RandomSeed,
    1.0f,               // ChanceToFracture
    FIslandSplitSettings(),
    0.0f,               // Grout
    0.0f, 0.0f, 0.0f, 0.0f, 0, // 噪声参数
    1.0f,               // PointSpacing
    true, 5.0f,         // 碰撞采样
    CutPlanes           // 自定义切面变换
);

// 使用切片切割器（沿 XYZ 轴规则切片）
FFractureEngineFracturing::SliceCutter(
    Collection, TransformSelection, BoundingBox,
    3, 3, 3,            // SlicesX, SlicesY, SlicesZ
    0.0f, 0.0f,         // AngleVariation, OffsetVariation
    RandomSeed,
    1.0f, FIslandSplitSettings(),
    0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0, 1.0f, true, 5.0f
);
```

### 进阶用法

#### 破碎 → 聚类 → 优化完整流程

```cpp
// 步骤 1: Voronoi 破碎
FDataflowTransformSelection TransformSelection;
FFractureEngineFracturing::VoronoiFracture(
    Collection, TransformSelection, Sites,
    FTransform::Identity, 42, 1.0f, FIslandSplitSettings(),
    0.0f, 0, 0, 0, 0, 0, 1.0f, true, 5.0f);

// 步骤 2: 自动聚类（将碎片按空间位置分组）
FGeometryCollection GeometryCollection; // 从 Collection 构造
FFractureEngineClustering::AutoCluster(
    GeometryCollection,
    0,                                  // ClusterIndex (根级)
    EFractureEngineClusterSizeMethod::ByNumber,
    8,                                  // SiteCount: 目标 8 个聚类
    0.5f,                               // SiteCountFraction
    50.0f,                              // SiteSize
    true,                               // bEnforceConnectivity
    true,                               // bAvoidIsolated
    false,                              // bEnforceSiteParameters
    2, 2, 2,                            // GridX, GridY, GridZ
    10.0f,                              // MinimumClusterSize
    500,                                // KMeansIterations
    false, 0.0f                         // 凸性参数
);

// 步骤 3: 修复微小几何体（将太小的碎片合并到邻居）
FFractureEngineUtility::FixTinyGeo(
    Collection, TransformSelection,
    EFixTinyGeoMergeType::MergeGeometry,
    true,                               // OnFractureLevel
    EFixTinyGeoGeometrySelectionMethod::VolumeCubeRoot,
    5.0f,                               // MinVolumeCubeRoot
    0.01f,                              // RelativeVolume
    EFixTinyGeoUseBoneSelection::NoEffect,
    false,                              // OnlyClusters
    EFixTinyGeoNeighborSelectionMethod::LargestNeighbor,
    true,                               // OnlyToConnected
    true                                // OnlySameParent
);

// 步骤 4: 简化凸包碰撞体
UE::FractureEngine::Convex::FSimplifyHullSettings Settings;
Settings.bUseGeometricTolerance = true;
Settings.ErrorTolerance = 5.0;
Settings.bUseTargetTriangleCount = true;
Settings.TargetTriangleCount = 20;

UE::FractureEngine::Convex::SimplifyConvexHulls(Collection, Settings);

// 步骤 5: 重采样碰撞数据
FFractureEngineUtility::ResampleGeometryCollection(
    Collection, TransformSelection, 5.0f);

// 步骤 6: 生成爆炸视图用于调试可视化
FFractureEngineFracturing::GenerateExplodedViewAttribute(
    Collection, FVector::OneVector, 2.0f);
```

#### 选择性操作

```cpp
// 来源: FractureEngineSelection.h

// 选择所有叶子节点
FDataflowTransformSelection LeafSelection;
FFractureEngineSelection::SelectLeaf(GeometryCollection, LeafSelection);

// 按体积范围选择
FDataflowTransformSelection SizeSelection;
FFractureEngineSelection::SelectByVolume(
    GeometryCollection, SizeSelection, 100.0f, 10000.0f);

// 选择父节点
FFractureEngineSelection::SelectParent(Collection, SelectedBones);

// 随机选择 50% 的碎片
FFractureEngineSelection::SelectByPercentage(
    SelectedBones, 50, true, 42.0f);
```

## Demo 示例

### 自定义破碎工具类

```cpp
// MyFractureTool.h
#pragma once

#include "CoreMinimal.h"
#include "FractureEngineFracturing.h"
#include "FractureEngineClustering.h"
#include "FractureEngineUtility.h"

class FMyFractureTool
{
public:
    /**
     * 对 Geometry Collection 执行完整的破碎流程：
     * Voronoi 破碎 → 自动聚类 → 修复微小几何体 → 重采样碰撞
     */
    static void PerformFullFracture(
        FManagedArrayCollection& InOutCollection,
        const FBox& InBounds,
        int32 InNumSites,
        int32 InRandomSeed,
        int32 InClusterCount = 8)
    {
        FDataflowTransformSelection Selection;

        // 1. 生成 Voronoi 种子点
        TArray<FVector> Sites;
        GenerateRandomSites(InBounds, InNumSites, InRandomSeed, Sites);

        // 2. Voronoi 破碎
        FFractureEngineFracturing::VoronoiFracture(
            InOutCollection, Selection, Sites,
            FTransform::Identity, InRandomSeed, 1.0f,
            FIslandSplitSettings(), 0.0f, 0, 0, 0, 0, 0, 1.0f, true, 5.0f);

        // 3. 修复微小碎片
        FFractureEngineUtility::FixTinyGeo(
            InOutCollection, Selection,
            EFixTinyGeoMergeType::MergeGeometry, true,
            EFixTinyGeoGeometrySelectionMethod::VolumeCubeRoot,
            2.0f, 0.005f,
            EFixTinyGeoUseBoneSelection::NoEffect, false,
            EFixTinyGeoNeighborSelectionMethod::LargestNeighbor,
            true, true);

        // 4. 分离岛屿
        FFractureEngineUtility::SplitIslands(
            InOutCollection, Selection, 1e-3, 0.0f);

        // 5. 重采样碰撞数据
        FFractureEngineUtility::ResampleGeometryCollection(
            InOutCollection, Selection, 5.0f);

        // 6. 验证集合完整性
        FFractureEngineUtility::ValidateGeometryCollection(
            InOutCollection, true, true, true);
    }

private:
    static void GenerateRandomSites(
        const FBox& Bounds, int32 Count, int32 Seed,
        TArray<FVector>& OutSites)
    {
        FRandomStream Rand(Seed);
        for (int32 i = 0; i < Count; ++i)
        {
            OutSites.Add(FVector(
                Rand.FRandRange(Bounds.Min.X, Bounds.Max.X),
                Rand.FRandRange(Bounds.Min.Y, Bounds.Max.Y),
                Rand.FRandRange(Bounds.Min.Z, Bounds.Max.Z)));
        }
    }
};
```

```cpp
// MyFractureTool.cpp
// 该文件可为空，所有实现均在头文件的内联函数中
// 如需分离声明与实现，将 PerformFullFracture 和 GenerateRandomSites 移至此处
```

## 模块依赖

从 `FractureEngine.Build.cs` 及 `.uplugin` 的 Plugins 依赖分析：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | Geometry Collection 运行时数据结构（FGeometryCollection） |
| `GeometryCollectionSimulationCore` | 破碎模拟核心类型 |
| `PlanarCut` | 平面切割算法（.uplugin 声明依赖） |
| `GeometryFramework` | 动态网格体（FDynamicMesh3） |

> ⚠️ 实际依赖请以 `Source/FractureEngine/FractureEngine.Build.cs` 为准。该模块依赖 Chaos Destruction 相关模块链，使用时需确保工程已启用 Chaos 物理系统。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `057caa09` | Add a split islands dataflow node + associated function in fracture engine utility | 新增岛屿分离数据流节点及底层工具函数 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至 UE_LOGF 新格式 |
| 2026-03-31 | `1843540e` | Add new split island controls to dataflow fracture and mesh-to-collection nodes | 为数据流破裂和网格转换节点添加岛屿分离控制 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 抑制警告 |
| 2026-01-22 | `49ee3dfa` | Geometry collection - fix crash when merging a single root bone that has an single embedded geometry | 修复合并含单个嵌入几何体的单根骨骼时的崩溃 |

### 维护评价

- **创建时间**：2022 年 10 月，相对较新的模块
- **维护状态**：**活跃维护中**。2026 年持续有功能性更新（岛屿分离、数据流节点、bug 修复）
- **实验性标记**：`IsBetaVersion=true`，`EnabledByDefault=false`，仍处于实验阶段
- **活跃度**：约每 1-2 个月有提交，开发节奏稳定
- **注意事项**：
  - 标记为 Beta，API 可能在未来版本发生变化
  - 不默认启用，需在插件设置中手动开启
  - 依赖 Chaos 物理引擎，不适用于传统 PhysX 模式
- **推荐**：如果你在开发 Chaos Destruction 相关工具或自定义 Dataflow 破碎节点，这是必选依赖；一般用户通过编辑器内置工具间接使用即可

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Fracture)
- 官方文档（无，`.uplugin` 中 DocsURL 为空）
- 测试用例（未发现独立测试文件）