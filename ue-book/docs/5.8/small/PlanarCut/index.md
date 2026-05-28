# Planar Cut

> Adds Module for Planar Cuts.

| 属性 | 值 |
|---|---|
| 中文名 | 平面切割 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlanarCut` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlanarCutPlugin) | |

## 用途
PlanarCut 是一个面向运行时的 C++ 工具库，专门用于对 `FGeometryCollection`（几何体集合，通常用于可破碎的几何体）进行平面切割、Voronoi 切割和网格切割，并提供后续的几何体处理功能。它解决的核心问题是：如何在运行时或编辑器中，高效地将单个几何体（网格）按照平面、Voronoi 图或另一个网格形状，切割成多个碎片，并处理这些碎片的内部表面材质、UV 坐标和法线等属性。这不仅仅是简单的布尔运算，而是一个完整的破碎工作流，包括切割、分离岛屿、UV 重投影、纹理烘焙以及碎片的优化与合并。

## 使用场景
- 你在开发一个赛车或动作游戏，需要车辆、建筑物等物体在碰撞时发生**实时物理破碎**（基于 Chaos Destruction）。
- 你需要在编辑器中预先设计破碎效果，将一个静态网格（如墙壁、柱子）**切割成多个预设的碎片**，用于过场动画或可控的破坏。
- 你为破碎后的内部表面添加了新的材质，需要为这些新表面**自动生成和布局 UV**，以便应用纹理。
- 你需要将破碎产生的**体积过小的碎片合并到相邻的大碎片上**，以优化物理模拟性能。

## 蓝图用法
PlanarCut 模块主要是一个 C++ 库，其核心功能通过 `PLANARCUT_API` 宏导出的 C++ 函数提供。虽然这些函数不是蓝图节点，但可以通过 C++ 调用并封装为蓝图节点。

### 核心函数
以下是从公开头文件提取的主要可调用函数，按功能分组：

#### 平面与 Voronoi 切割
| 函数 | 说明 | 所在头文件 |
|---|---|---|
| `CutWithPlanarCells` | 使用 `FPlanarCells`（定义切割平面和空间划分）切割单个几何体变换组。 | `PlanarCut.h` |
| `CutMultipleWithPlanarCells` | 使用 `FPlanarCells` 切割多个几何体变换组。 | `PlanarCut.h` |
| `CutMultipleWithMultiplePlanes` | 使用多个独立的 `FPlane` 切割多个几何体变换组。 | `PlanarCut.h` |
| `CreateCuttingSurfacePreview` | 生成切割表面的预览网格（用于可视化）。 | `PlanarCut.h` |
| `SplitIslands` | 将已有的几何体按其连通分量（岛屿）进行分离。 | `PlanarCut.h` |

#### UV 处理与纹理烘焙
| 函数 | 说明 | 所在头文件 |
|---|---|---|
| `BoxProjectUVs` | 对指定面进行盒体投影 UV。 | `FractureAutoUV.h` |
| `UVLayout` | 为几何体集合生成无重叠的 UV 图集。 | `FractureAutoUV.h` |
| `MergeUVIslands` | 基于法线角度和失真阈值合并现有的 UV 岛屿。 | `FractureAutoUV.h` |
| `TextureSpecifiedFaces` | 为指定面烘焙纹理属性（如距离、AO、曲率等）到图像。 | `FractureAutoUV.h` |

#### 碎片优化与合并
| 函数 | 说明 | 所在头文件 |
|---|---|---|
| `FindBoneVolumes` | 计算几何体体积。 | `PlanarCut.h` |
| `FindSmallBones` | 查找体积小于阈值的碎片。 | `PlanarCut.h` |
| `FilterBonesByVolume` | 使用自定义体积过滤器筛选碎片。 | `PlanarCut.h` |
| `MergeBones` | 将选中的碎片合并到其邻居中。 | `PlanarCut.h` |
| `MergeClusters` | 将选中的碎片合并到相邻的簇中。 | `PlanarCut.h` |
| `MergeAllSelectedBones` | 将所有选中的碎片合并为一个节点。 | `PlanarCut.h` |

#### 辅助与后处理
| 函数 | 说明 | 所在头文件 |
|---|---|---|
| `RecomputeNormalsAndTangents` | 重新计算几何体的法线和切线。 | `PlanarCut.h` |
| `AddCollisionSampleVertices` | 为几何体添加稀疏的碰撞采样顶点。 | `PlanarCut.h` |

### 使用示例（C++ 描述）
典型的调用流程如下：
1.  **准备切割源**：创建一个 `FPlanarCells` 对象。可以通过单个平面、一组 Voronoi 种子点或一组包围盒来初始化。
2.  **执行切割**：调用 `CutWithPlanarCells` 或 `CutMultipleWithMultiplePlanes`，传入待切割的 `FGeometryCollection` 和变换索引。
3.  **处理内部表面**：可以通过 `RecomputeNormalsAndTangents` 更新法线，或通过 `BoxProjectUVs` / `UVLayout` 为新生成的内部表面设置 UV。
4.  **优化碎片**：使用 `FindSmallBones` 和 `MergeBones` 合并过小的碎片。
5.  **烘焙纹理（可选）**：使用 `TextureSpecifiedFaces` 为特定属性（如内部表面距离）烘焙纹理。

## C++ 用法

### 头文件引入
```cpp
#include "PlanarCut.h"
#include "FractureAutoUV.h" // 如果需要 UV 处理功能
```

### 基本用法：使用单个平面切割
```cpp
#include "PlanarCut.h"
#include "GeometryCollection/GeometryCollection.h"

void CutCollectionWithSinglePlane(FGeometryCollection& Collection, int32 TransformIndex, const FPlane& CutPlane)
{
    // 1. 从单个平面创建 FPlanarCells
    UE::PlanarCut::FPlanarCells Cells(CutPlane);

    // 2. 设置可选的切割参数
    double Grout = 0.0f; // 碎片间的缝隙
    double CollisionSampleSpacing = 0.0f; // 碰撞采样点间距
    int32 RandomSeed = 12345; // 用于噪声的随机种子
    FIslandSplitSettings IslandSplitSettings; // 使用默认设置，会自动分离不连通的岛屿

    // 3. 执行切割
    // 返回值是切割后新增的第一个几何体的索引，-1 表示未切割
    int32 NewGeomIndex = UE::PlanarCut::CutWithPlanarCells(
        Cells,
        Collection,
        TransformIndex,
        Grout,
        CollisionSampleSpacing,
        RandomSeed,
        TOptional<FTransform>(), // 使用默认的 Identity 变换
        true, // 包含未被切割到的外部部分
        true, // 从集合中设置默认的内部材质
        nullptr, // 无进度取消器
        FVector::ZeroVector, // Cells 的原点
        IslandSplitSettings
    );

    if (NewGeomIndex != INDEX_NONE)
    {
        // 切割成功，处理新产生的碎片...
    }
}
```

### 进阶用法：Voronoi 切割与 UV 布局
```cpp
#include "PlanarCut.h"
#include "FractureAutoUV.h"
#include "Voronoi/Voronoi.h"

void VoronoiCutAndLayoutUVs(FGeometryCollection& Collection, const TArray<int32>& TransformIndices, const TArray<FVector>& VoronoiSites)
{
    // 1. 创建 Voronoi 图
    FVoronoiDiagram Voronoi;
    // ... (省略 Voronoi 图的生成和边界计算细节)

    // 2. 从 Voronoi 图创建 FPlanarCells
    UE::PlanarCut::FPlanarCells Cells(VoronoiSites, Voronoi);

    // 3. 为内部表面设置噪声，使断裂面更自然
    Cells.SetNoise(FNoiseSettings());

    // 4. 对多个几何体执行 Voronoi 切割
    int32 RandomSeed = 54321;
    int32 FirstNewIndex = UE::PlanarCut::CutMultipleWithPlanarCells(
        Cells,
        Collection,
        TransformIndices,
        0.1, // Grout
        0.0, // CollisionSampleSpacing
        RandomSeed
    );

    // 5. 为切割后几何体的所有内部面重新布局 UV
    if (FirstNewIndex != INDEX_NONE)
    {
        // 假设我们要更新 UV Layer 0
        const int32 TargetUVLayer = 0;
        // 仅处理内部面（即新生成的断裂面）
        UE::PlanarCut::ETargetFaces TargetFaces = UE::PlanarCut::ETargetFaces::InternalFaces;
        UE::PlanarCut::UVLayout(TargetUVLayer, Collection, 1024, 1.0f, TargetFaces);
    }
}
```

## Demo 示例
一个最小示例，展示如何从 C++ 代码中对一个几何体集合应用单平面切割。

**MyFractureComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GeometryCollection/GeometryCollection.h"
#include "MyFractureComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyFractureComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Fracture")
    int32 GeometryIndexToCut = 0;

    UPROPERTY(EditAnywhere, Category="Fracture")
    FVector CutPlaneNormal = FVector::UpVector;

    UPROPERTY(EditAnywhere, Category="Fracture")
    FVector CutPlanePoint = FVector::ZeroVector;

    UFUNCTION(BlueprintCallable, Category="Fracture")
    void PerformCut();
};
```

**MyFractureComponent.cpp**
```cpp
#include "MyFractureComponent.h"
#include "PlanarCut.h"

void UMyFractureComponent::PerformCut()
{
    AActor* Owner = GetOwner();
    if (!Owner) return;

    // 假设场景中有一个带 GeometryCollectionComponent 的 Actor
    // 这里需要你根据实际场景获取 FGeometryCollection
    // 通常从 UGeometryCollectionComponent 获取
    /*
    if (UGeometryCollectionComponent* GCComp = Owner->FindComponentByClass<UGeometryCollectionComponent>())
    {
        FGeometryCollection* Collection = GCComp->GetRestCollection()->GetGeometryCollection();
        if (Collection && GeometryIndexToCut < Collection->NumElements(FGeometryCollection::TransformGroup))
        {
            FPlane CutPlane(CutPlanePoint, CutPlaneNormal.GetSafeNormal());
            UE::PlanarCut::FPlanarCells Cells(CutPlane);

            int32 NewGeomIndex = UE::PlanarCut::CutWithPlanarCells(
                Cells,
                *Collection,
                GeometryIndexToCut,
                0.0, 0.0, 12345
            );

            if (NewGeomIndex != INDEX_NONE)
            {
                // 切割成功，更新几何体集合的视图
                GCComp->MarkRenderStateDirty();
            }
        }
    }
    */
    // 注意：以上为概念示例，实际使用需要确保 GeometryCollection 生命周期和线程安全。
}
```

## 模块依赖
从 `.uplugin` 和代码使用分析，您的模块若要使用 PlanarCut 功能，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `PlanarCut` | 核心切割与处理功能。 |
| `GeometryProcessing` | 提供基础的几何处理（网格布尔运算、UV 展开等）。 |
| `ChaosDestruction` (或 `GeometryCollectionEngine`) | 提供 `FGeometryCollection` 数据结构。 |

请在您模块的 `.Build.cs` 文件中添加对这些模块的依赖。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `ac6557dd` | generalize noise for PlanarCut's fracture methods to optionally take an arbitrary function, as an al | 泛化了破碎方法中的噪声生成，现在可以接收任意函数作为噪声源。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 宏。 |
| 2026-03-31 | `c6ce7f1c` | fix double-vs-int comparison in geometrymeshconversion.cpp | 修复 `geometrymeshconversion.cpp` 中双精度浮点数与整数的比较问题。 |
| 2026-03-31 | `d5256966` | Add more options to control island splitting on fracture (threshold distance, whether to connect acr | 增加了更多控制破碎后岛屿分离的选项（阈值距离、是否跨越连接等）。 |

### 维护评价
PlanarCut 是一个**实验性**（`IsBetaVersion=true`，`EnabledByDefault=false`）的运行时插件。从提交记录看，它在 2026 年内仍有**活跃的功能更新和 Bug 修复**，最近一次提交距今不到一个月，表明它正在被积极维护和改进。它依赖于同样在持续更新的 `GeometryProcessing` 和 `Chaos` 系统。

**主要风险与限制**：
1.  **实验性**：API 可能会随着版本更新而发生变化。
2.  **复杂性**：正确使用需要理解 `FGeometryCollection`、`FPlanarCells` 等数据结构以及几何处理的基本概念。
3.  **性能**：运行时切割的性能取决于网格复杂度、切割类型和噪声设置。

**推荐**：如果你的项目明确需要运行时或编辑器内对 Chaos 几何体进行复杂的平面/Voronoi 破碎和 UV 处理，并且愿意接受实验性 API 可能的变化，那么 PlanarCut 是一个**强大且值得尝试**的工具。建议在开发中密切跟踪其更新日志。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlanarCutPlugin)
- 官方文档（无）