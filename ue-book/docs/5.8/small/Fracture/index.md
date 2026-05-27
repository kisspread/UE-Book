# Fracture

> Adds Module for FractureEditor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 破碎工具库 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-17 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Fracture) | |

## 用途

Fracture 插件的核心是一个**运行时算法库** (`FractureEngine` 模块)，它为 UE5 的几何体编辑器（`Geometry Collection Editor` 或 `Fracture Editor`）提供底层破碎和几何体处理功能。它解决的核心问题是：**为物理模拟的破碎效果提供预处理算法**。

该插件的存在是为了将破碎、聚类、切割、采样等复杂的几何体处理算法从具体的编辑器 UI 中解耦出来，形成一个独立、可复用的库。编辑器插件（如 `FractureEditor`）或 `Dataflow` 节点可以调用此库中的函数来处理 `GeometryCollection` 资产，从而实现可控的破碎模式生成、网格优化、聚类组织等操作，为后续的物理破碎模拟做好准备。

**注意**：此插件默认未启用 (`EnabledByDefault=false`)，且标记为实验性 (`IsBetaVersion=true`)，通常需要配合 `FractureEditor` 或 `GeometryProcessing` 等编辑器插件使用，不建议单独在最终项目中启用。

## 使用场景

- **制作可破坏的物体**：当你需要为一个静态网格体创建复杂的、可控的破碎效果（如墙壁、柱子、雕像）时，可以使用此插件提供的算法来生成 `GeometryCollection`。
- **编辑破碎模式**：在 `Geometry Collection Editor` 中，你希望以编程方式或通过自定义工具生成 Voronoi 破碎、平面切割、砖块切割或使用自定义网格体进行切割。
- **管理破碎层次结构**：需要将破碎后的碎片自动聚类，以控制模拟时的父子关系和约束。
- **优化破碎资产**：在生成破碎效果后，需要修复极小的几何体、重新采样碰撞体、或为不同层级的碎片设置材质。
- **运行时动态破碎**：在运行时，需要根据物体形状动态计算切割平面或破碎点（例如 `MeshCutter` 函数），虽然此库为运行时模块，但其使用场景更偏向于编辑器预处理。

## 蓝图用法

此插件模块 (`FractureEngine`) 是 C++ 运行时库，其核心函数多为 `static` 方法，未直接暴露为 `BlueprintCallable`。通常通过 `FractureEditor` 模块的蓝图函数库（如 `UBlueprintFractureLibrary`）或 `Dataflow` 节点来间接使用。

以下是其核心功能对应的蓝图节点（基于源码推断的潜在接口）：

### 核心节点（概念）

| 功能 | 说明 | 可能关联的类 |
|---|---|---|
| **VoronoiFracture** | 根据 Voronoi 站点对物体进行破碎 | `FFractureEngineFracturing` |
| **PlaneCutter** | 使用随机平面切割物体 | `FFractureEngineFracturing` |
| **SliceCutter** | 使用网格模式切割物体 | `FFractureEngineFracturing` |
| **BrickCutter** | 使用砖块模式切割物体 | `FFractureEngineFracturing` |
| **MeshCutter** | 使用自定义网格体作为切割器 | `FFractureEngineFracturing` |
| **AutoCluster** | 自动将碎片聚类 | `FFractureEngineClustering` |
| **FixTinyGeo** | 合并过小的几何碎片 | `FFractureEngineUtility` |
| **SetBoneColor** | 设置碎片层级颜色（调试用） | `FFractureEngineFracturing` |
| **SelectParent/Children/Siblings** | 在层级中选择相关的骨骼/碎片 | `FFractureEngineSelection` |

### 使用示例（蓝图描述）

假设你有一个名为 `MyFracturedObject` 的 `GeometryCollection` 资产，并已加载到一个 Actor 中。

1.  **蓝图中调用破碎函数**：
    *   在编辑器工具或 Dataflow 图中，获取 `GeometryCollection` 的 `FManagedArrayCollection` 数据。
    *   创建一个 `FDataflowTransformSelection` 来指定要破碎的骨骼索引（例如，选择根骨骼）。
    *   调用相应的破碎函数，如 `FFractureEngineFracturing::VoronoiFracture`，传入集合、选择、随机站点、变换等参数。
    *   函数会修改传入的 `FManagedArrayCollection`，添加新的破碎骨骼。

2.  **蓝图中进行聚类**：
    *   在破碎后，你可能有一堆无序的碎片。
    *   调用 `FFractureEngineClustering::AutoCluster`，传入 `GeometryCollection` 和需要聚类的骨骼索引。
    *   函数会在 `GeometryCollection` 中创建新的聚类层级。

3.  **蓝图中设置颜色（调试）**：
    *   调用 `FFractureEngineFracturing::SetBoneColorByLevel` 来为不同层级的骨骼分配不同颜色，便于在编辑器中查看破碎层级结构。

## C++ 用法

### 头文件引入

根据你需要使用的功能，包含对应的头文件：

```cpp
// 主要破碎功能
#include "FractureEngineFracturing.h"

// 聚类功能
#include "FractureEngineClustering.h"

// 几何体修复与工具
#include "FractureEngineUtility.h"

// 凸包处理
#include "FractureEngineConvex.h"

// 选择功能
#include "FractureEngineSelection.h"

// 材质设置
#include "FractureEngineMaterials.h"

// 编辑功能（删除分支、合并）
#include "FractureEngineEdit.h"

// 采样功能
#include "FractureEngineSampling.h"
```

### 基本用法

以下示例展示了如何对一个 `GeometryCollection` 进行 Voronoi 破碎。这通常在自定义编辑器工具或处理 `GeometryCollection` 资产的命令中进行。

```cpp
#include "GeometryCollection/GeometryCollection.h"
#include "FractureEngineFracturing.h"

// 假设你有一个已经加载的 FGeometryCollection 对象
FGeometryCollection* MyGeometryCollection = ...;

// 1. 获取其底层可修改的数据集合
FManagedArrayCollection& Collection = MyGeometryCollection->GetManagedArrayCollection();

// 2. 定义要破碎的目标（例如，选择索引为0的根骨骼）
FDataflowTransformSelection TransformSelection;
TransformSelection.Initialize(/* Num Elements */ 1);
TransformSelection.SetSelected(0, true);

// 3. 定义 Voronoi 站点
TArray<FVector> VoronoiSites;
// 生成一些随机站点，例如在包围盒内
for (int32 i = 0; i < 10; ++i)
{
    VoronoiSites.Add(FMath::RandPointInBox(FBox(FVector(-100), FVector(100))));
}

// 4. 定义破碎参数
FTransform ObjectTransform = FTransform::Identity;
int32 RandomSeed = 42;
float ChanceToFracture = 1.0f; // 100% 破碎概率
FIslandSplitSettings IslandSplitSettings; // 可设置岛屿分割选项
float Grout = 0.0f; // 灰缝宽度
// ... 其他噪声参数 ...

// 5. 执行 Voronoi 破碎
int32 NumNewBones = FFractureEngineFracturing::VoronoiFracture(
    Collection,
    TransformSelection,
    VoronoiSites,
    ObjectTransform,
    RandomSeed,
    ChanceToFracture,
    IslandSplitSettings,
    Grout,
    /* InAmplitude */ 0.0f,
    /* InFrequency */ 0.0f,
    /* InPersistence */ 0.0f,
    /* InLacunarity */ 0.0f,
    /* InOctaveNumber */ 0,
    /* InPointSpacing */ 0.0f,
    /* InAddSamplesForCollision */ false,
    /* InCollisionSampleSpacing */ 0.0f
);

// 现在，MyGeometryCollection 中已包含了新的破碎骨骼数据。
// 你可能需要刷新相关的编辑器显示或重新构建渲染数据。
```

### 进阶用法

结合聚类和修复功能，形成一个完整的破碎处理流水线。

```cpp
#include "FractureEngineFracturing.h"
#include "FractureEngineClustering.h"
#include "FractureEngineUtility.h"

void ProcessFracturedGeometry(FGeometryCollection* GeometryCollection)
{
    FManagedArrayCollection& Collection = GeometryCollection->GetManagedArrayCollection();

    // 假设我们刚刚完成了破碎，得到了很多碎片

    // 步骤1：修复极小的几何体，将其合并到邻居中
    FDataflowTransformSelection AllSelection;
    AllSelection.Initialize(GeometryCollection->NumTransforms());
    AllSelection.SetAllSelected(true);

    FFractureEngineUtility::FixTinyGeo(
        Collection,
        AllSelection,
        EFixTinyGeoMergeType::MergeGeometry,
        /* InOnFractureLevel */ true,
        EFixTinyGeoGeometrySelectionMethod::VolumeCubeRoot,
        /* InMinVolumeCubeRoot */ 0.5f, // 体积的立方根小于0.5的视为“极小”
        /* InRelativeVolume */ 0.0f,
        EFixTinyGeoUseBoneSelection::NoEffect,
        /* InOnlyClusters */ false,
        EFixTinyGeoNeighborSelectionMethod::LargestNeighbor,
        /* InOnlyToConnected */ true,
        /* InOnlySameParent */ true
    );

    // 步骤2：将剩余的碎片自动聚类，便于物理模拟
    TArray<int32> BoneIndicesToCluster;
    // 获取所有“叶子”骨骼（即没有子项的破碎碎片）
    for (int32 i = 0; i < GeometryCollection->NumTransforms(); ++i)
    {
        if (GeometryCollection->Children[i].Num() == 0)
        {
            BoneIndicesToCluster.Add(i);
        }
    }

    if (BoneIndicesToCluster.Num() > 0)
    {
        FFractureEngineClustering::AutoCluster(
            *GeometryCollection,
            BoneIndicesToCluster,
            EFractureEngineClusterSizeMethod::ByNumber,
            /* SiteCount */ 5, // 聚类成大约5组
            /* SiteCountFraction */ 0.0f,
            /* SiteSize */ 0.0f,
            /* bEnforceConnectivity */ true,
            /* bAvoidIsolated */ true,
            /* bEnforceSiteParameters */ false,
            /* GridX */ 2,
            /* GridY */ 2,
            /* GridZ */ 2,
            /* MinimumClusterSize */ 0,
            /* KMeansIterations */ 100,
            /* bPreferConvexity */ false,
            /* ConcavityErrorTolerance */ 0.0f
        );
    }

    // 步骤3：为不同层级设置颜色以便调试
    FRandomStream RandomStream(123);
    FFractureEngineFracturing::SetBoneColorByLevel(Collection, 0); // 根层级
    FFractureEngineFracturing::SetBoneColorByLevel(Collection, 1); // 第一层子级
    // ... 或者按聚类设置颜色
    FFractureEngineFracturing::SetBoneColorByCluster(Collection, RandomStream, 1, 40, 190);

    // 现在 GeometryCollection 已经经过了清理、聚类和着色，可以用于物理模拟了。
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何创建一个简单的盒子并对其进行破碎。假设你在一个编辑器工具或自定义模块中运行。

**FractureDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FFractureDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 运行一个简单的破碎演示 */
    static void RunFractureDemo();
};
```

**FractureDemo.cpp**
```cpp
#include "FractureDemo.h"

#include "GeometryCollection/GeometryCollection.h"
#include "FractureEngineFracturing.h"
#include "FractureEngineUtility.h" // For DeconstructMesh

#define LOCTEXT_NAMESPACE "FFractureDemoModule"

void FFractureDemoModule::StartupModule()
{
    // 模块启动时的逻辑，可以在这里注册控制台命令等
}

void FFractureDemoModule::ShutdownModule()
{
}

void FFractureDemoModule::RunFractureDemo()
{
    // 1. 创建一个临时的 GeometryCollection
    TUniquePtr<FGeometryCollection> TempGeometryCollection = MakeUnique<FGeometryCollection>();
    FManagedArrayCollection& Collection = TempGeometryCollection->GetManagedArrayCollection();

    // 2. 构建一个简单的盒子网格数据（简化版，实际使用 FDynamicMesh3 更好）
    TArray<FVector3f> BoxVertices;
    TArray<FIntVector> BoxTriangles;
    FBox BoxBounds(FVector(-50), FVector(50));
    FFractureEngineUtility::ConvertBoxToVertexAndTriangleData(BoxBounds, BoxVertices, BoxTriangles);

    // 这里需要将BoxVertices和BoxTriangles添加到GeometryCollection中，这通常由GeometryCollectionUtility模块完成。
    // 为简化，我们假设已经有一个有效的GeometryCollection数据。

    // 3. 选择所有要破碎的几何体
    FDataflowTransformSelection Selection;
    Selection.Initialize(1); // 假设只有一个根骨骼
    Selection.SetSelected(0, true);

    // 4. 执行平面切割
    int32 NumPlanes = 5;
    TArray<FTransform> CuttingPlaneTransforms;
    FFractureEngineFracturing::GenerateSliceTransforms(
        BoxBounds,
        12345, // Random Seed
        NumPlanes,
        CuttingPlaneTransforms
    );

    FFractureEngineFracturing::PlaneCutter(
        Collection,
        Selection,
        BoxBounds,
        FTransform::Identity,
        NumPlanes,
        12345,
        1.0f, // 100% Chance
        FIslandSplitSettings(),
        0.0f, // Grout
        0.0f, 0.0f, 0.0f, 0.0f, 0, // Noise params
        0.0f, // Point spacing
        false, // Add collision samples
        0.0f, // Collision sample spacing
        CuttingPlaneTransforms
    );

    UE_LOG(LogTemp, Display, TEXT("Fracture Demo: Created %d bones from plane cutting."), Collection.NumElements(FGeometryCollection::TransformGroup));

    // 注意：此示例仅为演示调用流程。实际操作GeometryCollection需要完整的顶点/索引/几何体数据。
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FFractureDemoModule, FractureDemo)
```

## 模块依赖

`FractureEngine` 模块的 `Build.cs` 文件通常依赖以下模块（基于其功能推断）。在你的项目中使用此插件时，需要在 `Build.cs` 中添加对应的依赖。

| 模块 | 用途 |
|---|---|
| `GeometryCollection` | 核心依赖，提供 `FGeometryCollection` 和 `FManagedArrayCollection` 数据结构。 |
| `GeometryFramework` | 提供 `FDynamicMesh3` 等几何体处理工具。 |
| `Chaos` | 物理引擎相关，用于凸包 (`FConvex`) 等物理数据。 |

*（常见依赖如 Core, Engine, PhysicsCore, etc. 已省略）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `057caa09` | Add a split islands dataflow node + associated function in fracture engine utility | 添加了分割岛屿的Dataflow节点及FractureEngineUtility中的相关函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移到UE_LOGF格式。 |
| 2026-03-31 | `1843540e` | Add new split island controls to dataflow fracture and mesh-to-collection nodes | 为数据流破碎和网格转集合节点添加了新的分割岛屿控制。 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 移除了不再需要的PVS（持久性抑制）代码。 |
| 2026-01-22 | `49ee3dfa` | Geometry collection - fix crash when merging a single root bone that has a single embedded geometry | 修复合并单个根骨骼（包含单个嵌入几何体）时发生的崩溃。 |

### 维护评价

- **活跃维护**：从2026年1月至4月的更新记录来看，此插件仍在**活跃开发**中。近期的提交主要集中在功能增强（添加分割岛屿功能）、代码质量改进（日志迁移、清理PVS）和Bug修复。
- **实验性**：插件本身标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它仍被视为实验性功能，API 和功能可能发生变动。
- **推荐使用**：如果你正在开发与破碎相关的编辑器工具或 Dataflow 节点，这是一个**推荐使用的底层算法库**。对于最终游戏项目，通常不会直接依赖此模块，而是使用由它支持的更高层级功能。
- **注意事项**：作为实验性模块，其接口稳定性不如核心引擎模块。在升级引擎版本时，需要关注可能发生的API变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Fracture)
- 官方文档：无
- 测试用例：未在提供的路径中发现公开的测试用例文件。测试可能集成在编辑器插件或 Dataflow 的测试中。