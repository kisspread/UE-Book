# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

LidarPointCloud 是 UE5 内置的 LiDAR 点云处理插件，用于导入、管理和渲染大规模三维激光扫描数据。它解决的核心问题是：如何在游戏引擎中高效存储和实时渲染数百万甚至数十亿个点的点云数据。

该插件基于 **八叉树（Octree）** 数据结构组织点云，支持按需流式加载（streaming）、LOD 层级控制、视锥裁剪（frustum culling）和遮挡剔除，使得即使在普通硬件上也能流畅浏览超大规模点云资产。它适用于建筑信息建模（BIM）、自动驾驶仿真、数字孪生、文化遗产数字化等需要将真实世界三维扫描数据引入虚拟环境的场景。

**默认未启用**——需要在 Edit > Plugins 中手动启用。

## 使用场景

- 你在做自动驾驶/ADAS 仿真，需要导入 LiDAR 传感器采集的 LAS/LAZ 点云数据 → 用 LidarPointCloud
- 你在做数字孪生项目，需要将激光扫描的建筑物/工厂点云导入 UE 场景 → 用 LidarPointCloud
- 你需要在蓝图或 C++ 中对点云进行空间查询（射线检测、区域查询）、修改颜色/可见性 → 用 LidarPointCloud
- 你需要从点云生成碰撞体或网格（Mesh）用于物理交互 → 用 LidarPointCloud
- 你需要将多个点云对齐合并为一个统一场景 → 用 `AlignClouds` + `Merge`

## 模块概览

本插件由两个模块组成，详见各自的子文档：

| 模块 | 文件数 | 说明 |
|---|---|---|
| [LidarPointCloudRuntime](Runtime.md) | ~37 | 核心运行时：资产、八叉树、文件IO、渲染、LOD、碰撞、网格化 |
| [LidarPointCloudEditor](Editor.md) | ~22 | 编辑器工具：导入工厂、编辑模式、视口、属性面板、资产操作 |

## 核心架构

```
ULidarPointCloud (UObject 资产)
  └── FLidarPointCloudOctree (八叉树数据结构)
        └── FLidarPointCloudOctreeNode[] (节点，支持按需流式加载)
              └── FLidarPointCloudPoint[] (点数据)

ULidarPointCloudComponent (场景组件)
  └── 引用 ULidarPointCloud
  └── 渲染参数 (PointSize, ColorSource, ScalingMethod 等)
  └── FLidarPointCloudSceneProxy (渲染线程代理)

ALidarPointCloudActor (Actor)
  └── ULidarPointCloudComponent

FLidarPointCloudLODManager (全局 LOD 管理器)
  └── 管理所有组件的节点选择和点预算分配

ULidarPointCloudFileIO (文件IO系统)
  ├── ULidarPointCloudFileIO_LAS (LAS/LAZ 格式)
  ├── ULidarPointCloudFileIO_E57 (E57 格式，仅 Windows)
  └── ULidarPointCloudFileIO_ASCII (TXT/XYZ/PTS 格式)

ALidarClippingVolume (裁剪体积)
  └── 控制点云在指定区域内的显示/隐藏
```

## 支持的文件格式

| 格式 | 扩展名 | 导入 | 导出 | 平台限制 | 并发插入 |
|---|---|---|---|---|---|
| LAS | `.las` | ✅ | ✅ | Win64, Mac, Linux | ✅ |
| LAZ (压缩LAS) | `.laz` | ✅ | ✅ | Win64, Mac | ✅ |
| E57 | `.e57` | ✅ | ❌ | 仅 Win64 | ❌ |
| ASCII (TXT/XYZ/PTS) | `.txt`, `.xyz`, `.pts` | ✅ | ✅ | 全平台 | ❌ |

## 蓝图用法

### 核心节点

#### 创建与导入

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Lidar Point Cloud From File` | 从文件创建点云资产（支持异步） | `ULidarPointCloudBlueprintLibrary` |
| `Create Lidar Point Cloud From Data` | 从点数据数组创建点云资产 | `ULidarPointCloudBlueprintLibrary` |
| `Create Lidar Point Cloud From File (ASCII)` | 从 ASCII 文件创建，带列映射设置 | `ULidarPointCloudFileIO_ASCII` |
| `Create Empty Lidar Point Cloud` | 创建空的点云资产 | `ULidarPointCloudBlueprintLibrary` |
| `Export Point Cloud To File` | 导出点云到文件 | `ULidarPointCloudBlueprintLibrary` |

#### 查询与射线检测

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LineTraceSingle` | 单点射线检测 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `LineTraceMulti` | 多点射线检测 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `HasPointsInSphere` | 球形区域内是否有可见点 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `HasPointsInBox` | 盒形区域内是否有可见点 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `GetPointsInSphereAsCopies` | 获取球形区域内点的副本 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `GetPointsInBoxAsCopies` | 获取盒形区域内点的副本 | `ULidarPointCloud` / `ULidarPointCloudComponent` |

#### 可见性控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetVisibilityOfPointsInSphere` | 设置球形区域内点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsInBox` | 设置盒形区域内点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfFirstPointByRay` | 设置射线命中的第一个点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsByRay` | 设置射线命中的所有点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `HideAll` | 隐藏所有点 | `ULidarPointCloud` |
| `UnhideAll` | 显示所有点 | `ULidarPointCloud` |

#### 颜色修改

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyColorToAllPoints` | 给所有点应用颜色 | `ULidarPointCloud` |
| `ApplyColorToPointsInSphere` | 给球形区域内的点应用颜色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `ApplyColorToPointsInBox` | 给盒形区域内的点应用颜色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `ApplyColorToFirstPointByRay` | 给射线命中的第一个点应用颜色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `ApplyColorToPointsByRay` | 给射线命中的所有点应用颜色 | `ULidarPointCloud` / `ULidarPointCloudComponent` |

#### 数据操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InsertPoint` / `InsertPoints` | 插入单个/批量点 | `ULidarPointCloud` |
| `RemovePointsInSphere` / `RemovePointsInBox` | 按区域删除点 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `RemoveFirstPointByRay` / `RemovePointsByRay` | 按射线删除点 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `RemoveHiddenPoints` | 删除所有隐藏的点 | `ULidarPointCloud` |
| `SetData` | 用新数据替换整个点云 | `ULidarPointCloud` |
| `Merge` / `MergeSingle` | 合并其他点云 | `ULidarPointCloud` |

#### 属性与设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumPoints` | 获取总点数 | `ULidarPointCloud` |
| `GetNumVisiblePoints` | 获取可见点数 | `ULidarPointCloud` |
| `GetNumLODs` | 获取 LOD 层级数 | `ULidarPointCloud` |
| `GetBounds` | 获取包围盒 | `ULidarPointCloud` |
| `GetEstimatedPointSpacing` | 获取估算的点间距 | `ULidarPointCloud` |
| `GetDataSize` | 获取数据大小（MB） | `ULidarPointCloud` |
| `CalculateNormals` | 计算法线（Latent，异步） | `ULidarPointCloud` |
| `BuildCollision` / `RemoveCollision` | 构建/移除碰撞 | `ULidarPointCloud` |
| `CenterPoints` | 居中点云 | `ULidarPointCloud` |
| `SetLocationOffset` | 设置位置偏移 | `ULidarPointCloud` |
| `AlignClouds` | 对齐多个点云 | `ULidarPointCloudBlueprintLibrary` |

### 使用示例（蓝图描述）

**从文件导入点云并添加到场景：**

1. 使用 `Create Lidar Point Cloud From File` 节点，指定文件路径和 `bUseAsync = true`
2. 从 `AsyncMode` 引脚分支：Success 路径继续
3. 使用 `Spawn Actor From Class` 拖入 `LidarPointCloudActor` 类
4. 调用 `SetPointCloud` 将导入的资产赋给 Actor
5. 该 Actor 自动显示在场景中

**射线检测查询点云：**

1. 从 `LineTraceSingle` 节点，输入射线 Origin、Direction、Radius
2. 设置 `bVisibleOnly = true` 只检测可见点
3. 返回的 `PointHit` 包含位置、颜色、法线等信息

**运行时动态修改点云颜色：**

1. 获取场景中的 `LidarPointCloudComponent` 引用
2. 调用 `ApplyColorToPointsInSphere`，传入新颜色、中心点和半径
3. 点云立即更新显示

## C++ 用法

### 头文件引入

```cpp
// 运行时模块（核心功能）
#include "LidarPointCloud.h"
#include "LidarPointCloudComponent.h"
#include "LidarPointCloudActor.h"
#include "LidarPointCloudShared.h"

// 文件导入
#include "IO/LidarPointCloudFileIO.h"
#include "IO/LidarPointCloudFileIO_ASCII.h"

// 设置
#include "LidarPointCloudSettings.h"
```

### 基本用法

**从文件创建点云资产**（参考 `ULidarPointCloud::CreateFromFile`）：

```cpp
#include "LidarPointCloud.h"

// 同步导入
ULidarPointCloud* PointCloud = ULidarPointCloud::CreateFromFile(
    TEXT("/path/to/scan.las"),
    nullptr,  // 使用默认导入设置
    GetTransientPackage(),
    NAME_None,
    RF_NoFlags
);

// 异步导入（带进度回调）
FLidarPointCloudAsyncParameters AsyncParams(
    true,  // bUseAsync
    [](float Progress) { UE_LOG(LogTemp, Log, TEXT("Progress: %.1f%%"), Progress * 100.f); },
    [](bool bSuccess) { UE_LOG(LogTemp, Log, TEXT("Import %s"), bSuccess ? TEXT("succeeded") : TEXT("failed")); }
);
ULidarPointCloud* AsyncPointCloud = ULidarPointCloud::CreateFromFile(
    TEXT("/path/to/scan.las"),
    AsyncParams
);
```

**空间查询**（参考 `LidarPointCloud.h` 中的查询函数）：

```cpp
#include "LidarPointCloud.h"

// 射线检测 - 查找第一个命中的点
FLidarPointCloudPoint* HitPoint = PointCloud->LineTraceSingle(
    FLidarPointCloudRay(Origin, Direction),
    5.0f,   // Radius
    true    // bVisibleOnly
);

// 区域查询 - 获取球形区域内的所有点副本
TArray<FLidarPointCloudPoint> Points;
PointCloud->GetPointsInSphereAsCopies(
    Points,
    FSphere(Center, 100.0f),
    true,   // bVisibleOnly
    true    // bReturnWorldSpace
);

// 检查区域内是否有可见点
bool bHasPoints = PointCloud->HasPointsInBox(
    FBox(MinExtent, MaxExtent),
    true  // bVisibleOnly
);
```

### 进阶用法

**程序化创建点云**（参考 `CreateFromData`）：

```cpp
#include "LidarPointCloud.h"

// 创建点数据
TArray<FLidarPointCloudPoint> Points;
for (int32 i = 0; i < 10000; ++i)
{
    float X = FMath::RandRange(-500.f, 500.f);
    float Y = FMath::RandRange(-500.f, 500.f);
    float Z = FMath::RandRange(0.f, 200.f);
    Points.Add(FLidarPointCloudPoint(X, Y, Z, 1.0f, 0.5f, 0.2f, 1.0f)); // R, G, B, A
}

// 创建资产
ULidarPointCloud* GeneratedCloud = ULidarPointCloud::CreateFromData(Points, false);
```

**使用组件进行渲染和交互**：

```cpp
#include "LidarPointCloudComponent.h"

// 在 Actor 中创建组件
ULidarPointCloudComponent* Comp = NewObject<ULidarPointCloudComponent>(this);
Comp->SetPointCloud(MyPointCloud);
Comp->PointSize = 3.0f;
Comp->ScalingMethod = ELidarPointCloudScalingMethod::PerNodeAdaptive;
Comp->ColorSource = ELidarPointCloudColorationMode::Data;
Comp->bUseFrustumCulling = true;
Comp->RegisterComponent();

// 动态修改外观
Comp->Saturation = FVector4(1.2, 1.2, 1.2, 1.0);  // 增加饱和度
Comp->Contrast = FVector4(1.1, 1.1, 1.1, 1.0);     // 增加对比度
Comp->ColorTint = FLinearColor(1.0, 0.9, 0.8, 1.0); // 暖色色调
```

**使用文件IO系统**（参考 `ULidarPointCloudFileIO`）：

```cpp
#include "IO/LidarPointCloudFileIO.h"

// 获取支持的导入格式
TArray<FString> ImportExts = ULidarPointCloudFileIO::GetSupportedImportExtensions();
for (const FString& Ext : ImportExts)
{
    UE_LOG(LogTemp, Log, TEXT("Supported import: %s"), *Ext);
}

// 手动导入（带自定义设置）
auto ImportSettings = ULidarPointCloudFileIO::GetImportSettings(TEXT("scan.las"));
FLidarPointCloudImportResults Results;
bool bSuccess = ULidarPointCloudFileIO::Import(TEXT("/path/to/scan.las"), ImportSettings, Results);
```

## Demo 示例

### 最小可编译示例：程序化创建并渲染点云

**MyLidarActor.h**

```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyLidarActor.generated.h"

class ULidarPointCloudComponent;
class ULidarPointCloud;

UCLASS()
class AMyLidarActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLidarActor();

    UPROPERTY(VisibleAnywhere)
    ULidarPointCloudComponent* PointCloudComponent;

    UPROPERTY()
    ULidarPointCloud* PointCloudAsset;

    virtual void BeginPlay() override;
};
```

**MyLidarActor.cpp**

```cpp
#include "MyLidarActor.h"
#include "LidarPointCloudComponent.h"
#include "LidarPointCloud.h"

AMyLidarActor::AMyLidarActor()
{
    PointCloudComponent = CreateDefaultSubobject<ULidarPointCloudComponent>(TEXT("PointCloud"));
    RootComponent = PointCloudComponent;
}

void AMyLidarActor::BeginPlay()
{
    Super::BeginPlay();

    // 程序化生成 10000 个随机点
    TArray<FLidarPointCloudPoint> Points;
    for (int32 i = 0; i < 10000; ++i)
    {
        Points.Add(FLidarPointCloudPoint(
            FMath::RandRange(-500.f, 500.f),
            FMath::RandRange(-500.f, 500.f),
            FMath::RandRange(0.f, 200.f),
            FMath::FRand(), FMath::FRand(), FMath::FRand(), 1.0f
        ));
    }

    PointCloudAsset = ULidarPointCloud::CreateFromData(Points, false);
    PointCloudComponent->SetPointCloud(PointCloudAsset);
    PointCloudComponent->PointSize = 4.0f;
    PointCloudComponent->ColorSource = ELidarPointCloudColorationMode::Data;
}
```

**YourModule.Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "LidarPointCloudRuntime"
});
```

## 模块依赖

### LidarPointCloudRuntime

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `Slate` / `SlateCore` | UI 框架 |
| `GeometryCore` | 几何算法 |
| `MeshConversion` / `MeshDescription` / `StaticMeshDescription` | 网格生成 |
| `InputCore` | 输入系统 |
| `Projects` | 插件项目系统 |

### LidarPointCloudEditor

| 模块 | 用途 |
|---|---|
| `LidarPointCloudRuntime` | 运行时核心（必须） |
| `UnrealEd` | 编辑器框架 |
| `AssetDefinition` | 资产定义系统 |
| `ContentBrowser` | 内容浏览器集成 |
| `PropertyEditor` | 属性面板 |
| `ToolMenus` | 工具菜单 |
| `AdvancedPreviewScene` | 预览场景 |
| `EditorInteractiveToolsFramework` / `InteractiveToolsFramework` | 交互工具框架 |
| `StatusBar` | 状态栏集成 |

## 全局设置（ULidarPointCloudSettings）

通过 Edit > Project Settings > Plugins > Lidar Point Cloud 访问：

| 设置 | 说明 |
|---|---|
| **Octree** | |
| DuplicateHandling | 重复点处理策略（Ignore / SelectFirst / SelectBrighter） |
| MaxDistanceForDuplicate | 重复点判定的最大距离 |
| MaxBucketSize | 节点中未分配点的最大数量（影响 LOD 精度 vs 内存） |
| NodeGridResolution | 节点虚拟网格分辨率 |
| **Performance** | |
| MultithreadingInsertionBatchSize | 多线程插入的批量大小 |
| bUseAsyncImport | 是否异步导入 |
| bPrioritizeActiveViewport | 是否优先活跃视口 |
| CachedNodeLifetime | 缓存节点在 RAM 中的保留时间 |
| bReleaseAssetAfterSaving | 保存后释放内存 |
| bReleaseAssetAfterCooking | Cook 后释放内存 |
| bUseRenderDataSmoothing | 分帧生成渲染数据 |
| bUseFastRendering | 快速渲染（4倍 VRAM 换性能） |
| **RayTracing** | |
| bEnableLidarRayTracing | 启用光追（显著增加 VRAM） |
| **Collision** | |
| MeshingBatchSize | 碰撞网格化的批量大小 |
| **Automation** | |
| bAutoCenterOnImport | 导入时自动居中 |
| bAutoCalculateNormalsOnImport | 导入时自动计算法线 |
| bAutoBuildCollisionOnImport | 导入时自动构建碰撞 |
| **Import / Export** | |
| ImportScale | 导入缩放 |
| ExportScale | 导出缩放 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-16 | `62b9753b2024` | Updated PointCloud plugin with more API exposed to BP | 将更多 API 暴露给蓝图，表明 Epic 持续增强蓝图可用性 |
| 2025-08-26 | `ce867df381b7` | [HWRT] Refactored FRayTracingInstanceCollector for multiple views | 硬件光追重构，属于引擎级改动影响点云光追渲染 |
| 2025-07-14 | `8c4cad918a59` | Changed WITH_EDITORONLY_DATA properties to have accessors | 编辑器属性访问器重构，适配引擎代码规范 |

### 维护评价

- **创建时间**：2020 年 1 月，已有约 6 年历史
- **最近更新**：2025 年 9 月有实质性 API 更新，说明 Epic 仍在积极维护
- **维护状态**：**活跃维护** — 持续有功能更新和引擎适配
- **平台支持**：Win64、Mac、Linux（E57 仅 Windows）
- **已知限制**：
  - 默认未启用，需手动开启
  - E57 格式仅 Windows 支持
  - LAZ 格式 Linux 不支持
  - 大规模点云可能消耗大量内存和 VRAM
- **推荐使用**：✅ 推荐。对于需要在 UE5 中处理 LiDAR 点云数据的项目，这是官方提供的唯一内置方案，且维护活跃、功能完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/LidarPointCloud)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [运行时模块文档](Runtime.md)
- [编辑器模块文档](Editor.md)
