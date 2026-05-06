# Fracture

> Adds Module for FractureEditor

| 属性 | 值 |
|---|---|
| 中文名 | 破碎编辑器模块 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-27 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Fracture) | |

## 用途

Fracture 插件是 UE5 破碎系统（Fracture Editor）的底层引擎模块，提供了用于几何体集合（Geometry Collection）的破碎、聚类、凸包简化、采样、编辑、选择等核心算法。它主要作为 Dataflow 节点的后端实现，以及 C++ 开发的工具库，使得开发者能够在运行时或编辑器中对可破坏物体进行高级控制。

该插件解决的核心问题：为 Chaos 物理破坏系统提供可控的、可编程的破碎逻辑，包括 Voronoi 破碎、砖块模式破碎、网格剪切割等，以及后续的优化（如合并小块、分离不连通部分、简化凸包等）。它依赖于 PlanarCut 插件进行平面切割操作。

## 使用场景

- 在 Dataflow 资产中构建自定义破碎流程时，使用 FractureEngine 提供的节点（如 Uniform Fracture、Brick Fracture、Mesh Cutter 等）
- 在 C++ 代码中直接调用 `FractureEngine` 命名空间下的函数，对 `FGeometryCollection` 进行程序化破碎操作
- 需要分析或修改可破坏物体的聚类结构（如 K-Means 分区、合并孤立分区）
- 需要对破碎后的凸包进行简化或重建，以优化碰撞性能
- 需要从几何体集合中提取特定层级（根、叶子、子级等）进行选择操作

## 蓝图用法

该插件的核心功能**不直接暴露为蓝图节点**，而是通过 Dataflow 节点暴露（Dataflow 资产支持蓝图赋值，但节点调用发生在编辑器或运行时 Dataflow 图中）。因此，在普通蓝图事件图表中无法直接调用 FractureEngine 函数。

如果你需要在蓝图中间接使用，可以：

1. 将 Dataflow 资产应用于蓝图中的几何体集合
2. 通过蓝图调用 `Execute Dataflow` 节点运行预定义的 Dataflow 图

以下枚举类型可被蓝图直接使用：

| 枚举 | 说明 |
|---|---|
| `EFractureBrickBondEnum` | 砖块破碎的砌合方式（Stretcher / Stack / English / Header / Flemish） |
| `EMeshCutterCutDistribution` | 网格切割器的分布方式（Single / UniformRandom / Grid） |
| `EMeshCutterPerCutMeshSelection` | 每次切割使用的网格选择方式（All / Random / Sequential） |
| `ENonUniformSamplingDistributionMode` | 非均匀采样分布模式（Uniform / Smaller / Larger） |
| `ENonUniformSamplingWeightMode` | 非均匀采样权重模式（WeightToRadius / FilledWeightToRadius / WeightedRandom） |
| `EFixTinyGeoMergeType` | 微小几何体合并类型（MergeGeometry / MergeClusters） |
| `EFixTinyGeoNeighborSelectionMethod` | 合并到邻居的选择方法（LargestNeighbor / NearestCenter） |
| `EFixTinyGeoUseBoneSelection` | 参考骨骼选择的处理方式（NoEffect / AlsoMergeSelected / OnlyMergeSelected） |
| `EFixTinyGeoGeometrySelectionMethod` | 几何体选择方法（VolumeCubeRoot / RelativeVolume） |
| `EConvexHullSimplifyMethod` | 凸包简化方法（MeshQSlim / AngleTolerance） |

## C++ 用法

### 头文件引入

```cpp
#include "FractureEngineFracturing.h"
#include "FractureEngineClustering.h"
#include "FractureEngineConvex.h"
#include "FractureEngineSelection.h"
#include "FractureEngineUtility.h"
#include "FractureEngineEdit.h"
#include "FractureEngineMaterials.h"
#include "FractureEngineSampling.h"
```

### 基本用法

以下示例展示了如何使用 `FFractureEngineFracturing` 执行基础的 Voronoi 破碎：

```cpp
// 来源：FractureEngineFracturing.h (示例截取)
// 假设已有一个 FGeometryCollection 对象 GeometryCollection
// 以及一个 FUniformFractureSettings 结构体 Settings

FUniformFractureSettings Settings;
Settings.Transform = FTransform::Identity;
Settings.MinVoronoiSites = 5;
Settings.MaxVoronoiSites = 10;
Settings.InternalMaterialID = 0;
Settings.RandomSeed = 12345;
Settings.ChanceToFracture = 1.0f;
Settings.GroupFracture = false;
Settings.SplitIslands = true;
Settings.Grout = 0.0f;
Settings.NoiseSettings = FNoiseSettings(); // 默认噪音
Settings.AddSamplesForCollision = true;
Settings.CollisionSampleSpacing = 5.0f;

// 执行均匀破碎
// 注意：实际调用可能通过 Dataflow 节点或引擎内部，此处为逻辑示意
// UE::FractureEngine::UniformFracture(GeometryCollection, Settings);
```

### 进阶用法

**K-Means 聚类分区与后处理：**

```cpp
// 来源：FractureEngineClustering.h
// 将几何体集合中的第 ClusterIndex 个集群体划分为 k 个分区

const FGeometryCollection* Collection = ...;
int32 ClusterIndex = 0;
FVoronoiPartitioner Partitioner(Collection, ClusterIndex);

// 执行 K-Means 分区，目标分区数 4，最多迭代 500 次
Partitioner.KMeansPartition(4, 500);

// 分离不连通的分区，合并单元素分区
Partitioner.SplitDisconnectedPartitions(GeometryCollection);
Partitioner.MergeSingleElementPartitions(GeometryCollection);

// 获取分区结果
int32 PartitionCount = Partitioner.GetPartitionCount();
TArray<int32> PartitionIndices = Partitioner.GetPartition(0);
```

**凸包简化：**

```cpp
// 来源：FractureEngineConvex.h
using namespace UE::FractureEngine::Convex;

FManagedArrayCollection Collection; // 包含凸包数据
FSimplifyHullSettings HullSettings;
HullSettings.SimplifyMethod = EConvexHullSimplifyMethod::AngleTolerance;
HullSettings.AngleThreshold = 15.0; // 角度容差

// 简化集合中所有凸包
bool bSuccess = SimplifyConvexHulls(Collection, HullSettings);

// 仅简化指定骨骼的凸包
TArray<int32> TransformSelection = { 2, 5, 10 };
bSuccess = SimplifyConvexHulls(Collection, HullSettings, true, TransformSelection);
```

**选择操作：**

```cpp
// 来源：FractureEngineSelection.h
FFractureEngineSelection::SelectLeaf(GeometryCollection, SelectedBones);
FFractureEngineSelection::SelectByVolume(GeometryCollection, SelectedBones, 10.0f, 100.0f);
```

## Demo 示例

以下是一个最小的控制台应用程序示例（仅 C++，需在 Unreal Engine 模块中使用）：

```cpp
// FractureDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "FractureEngineFracturing.h"
#include "FractureEngineSelection.h"

class FFractureDemo
{
public:
    static void RunFractureDemo()
    {
        // 1. 获取或创建几何体集合
        UGeometryCollection* CollectionObject = NewObject<UGeometryCollection>();
        FGeometryCollection* GeometryCollection = CollectionObject->GetGeometryCollection().Get();
        // 实际需要先填充几何体数据，此处省略

        // 2. 设置破碎参数
        FUniformFractureSettings Settings;
        Settings.MinVoronoiSites = 3;
        Settings.MaxVoronoiSites = 8;
        Settings.RandomSeed = 42;
        Settings.ChanceToFracture = 1.0f;

        // 3. 执行破碎
        // UE::FractureEngine::UniformFracture(*GeometryCollection, Settings);

        // 4. 选择所有叶子节点
        TArray<int32> Selected;
        FFractureEngineSelection::SelectLeaf(*GeometryCollection, Selected);

        // 5. 输出结果
        UE_LOG(LogTemp, Log, TEXT("Fractured into %d leaf nodes"), Selected.Num());
    }
};
```

```cpp
// FractureDemo.cpp
#include "FractureDemo.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, FractureDemo)
```

此示例需要你的模块依赖 `FractureEngine` 和 `GeometryCollectionEngine` 等模块。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PlanarCut` | 提供平面切割的核心算法和数据结构 |
| `GeometryFramework` | 动态网格（`FDynamicMesh3`）支持 |
| `GeometryCore` | 几何计算核心库 |
| `Chaos` | Chaos 物理系统（凸包类型 `Chaos::FConvex`） |
| `DataflowCore` | Dataflow 节点框架（部分节点定义） |
| `DataflowEngine` | Dataflow 执行引擎（可选） |

> 注意：运行时模块 `FractureEngine` 本身隐含 `Core`, `CoreUObject`, `Engine` 等常见依赖，已省略。

## 维护状态

### 近期更新

- 2025-06-26 ec90099 为具有 .gen.cpp 文件的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME（编译修复）
- 2025-06-26 d809745 为 PlaneCutter Dataflow 节点添加 "Cut Planes" 数组输入，支持直接指定切割平面
- 2025-06-09 f202c11 扩展砖块破碎模式的边界范围，修复砖块未完全覆盖内部区域的问题
- 2025-06-04 2bd7bc4 修复依赖 Chaos 模块的方式，改用模块设置函数
- 2025-05-27 bd9ec47 支持 TinyGeo "Merge Geometry" 模式的 "Only Same Parent" 选项

### 维护评价

该插件处于**活跃维护**状态。自创建（2025-05-27）以来，每月均有功能性更新和问题修复，包括新的 Dataflow 节点输入、算法改进和编译兼容性修复。作为实验性插件，其 API 和功能仍在快速迭代中，可能会有不兼容的变化。目前尚未发现明显已知问题或废弃标记。推荐在项目中使用，但要注意实验性标签，建议定期跟踪更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Fracture)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（搜索 "Fracture Editor" 或 "Geometry Collection"）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Fracture/Tests)（如果存在）