# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、着色器资源） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

该插件提供了一套完整的激光雷达（LiDAR）点云数据处理管线，解决的核心问题是：**如何在虚幻引擎中高效地导入、存储、查询和渲染海量三维点云数据**。

普通网格无法胜任点云数据的表达——一个典型的 LiDAR 扫描可以包含数千万甚至数亿个点，每个点仅携带位置、颜色、法线和分类信息。该插件通过以下技术栈解决这一难题：

- **八叉树（Octree）空间索引**：将点云数据组织为多层级八叉树，支持按空间范围高效查询、插入、删除点，同时为 LOD 流式加载提供基础
- **全局 LOD 管理器**：跨所有点云实例统一管理渲染预算，在视口视锥体范围内智能选择最合适的节点层级，确保帧率稳定
- **自定义顶点工厂与 GPU 缓冲区**：通过专用着色器和 StructuredBuffer 在 GPU 上高效渲染点，支持点精灵（Sprite）、分类着色、高程着色等多种可视化模式
- **多格式文件 I/O**：内置 LAS/LAZ、ASCII（XYZ/TXT/PTS）、E57 格式支持，具备可扩展的处理器注册机制
- **运行时数据编辑**：支持实时插入、删除、修改点的颜色/可见性，适用于实时扫描数据流或交互式编辑场景

`EnabledByDefault=false`，需要手动在项目设置中启用。因为点云相关资产体积通常较大，对内存和 GPU 有一定要求，不适合所有项目默认开启。

## 使用场景

- **数字孪生与城市规划**：导入无人机 LiDAR 扫描的城市三维点云，叠加到 UE5 场景中进行可视化分析
- **影视虚拟制片**：使用实景扫描的点云作为虚拟背景或场景参考，配合摄像机漫游
- **自动驾驶仿真**：将车载 LiDAR 的实时点云数据流式导入，可视化传感器感知范围
- **建筑 BIM 对比**：将施工扫描点云与设计模型对比，检测偏差
- **考古与文化遗产**：高精度三维扫描遗址，在引擎中进行虚拟修复或展示
- **地形与地质分析**：渲染大范围地形点云，使用高程着色快速识别地貌特征
- **工业逆向工程**：导入三维扫描仪输出的点云数据，在引擎中进行可视化检查

## 蓝图用法

该插件提供了丰富的蓝图 API，所有核心类均暴露了 `BlueprintCallable` / `BlueprintPure` 函数。按功能分为以下几组：

### 点云资产查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumPoints` | 返回点云总点数 | `ULidarPointCloud` |
| `GetNumVisiblePoints` | 返回当前可见点数 | `ULidarPointCloud` |
| `GetNumLODs` | 返回 LOD 层级数 | `ULidarPointCloud` |
| `GetNumNodes` | 返回八叉树节点总数 | `ULidarPointCloud` |
| `GetEstimatedPointSpacing` | 返回估算的点间距 | `ULidarPointCloud` |
| `GetDataSize` | 返回占用内存（MB） | `ULidarPointCloud` |
| `GetBounds` | 返回包围盒 | `ULidarPointCloud` |
| `IsFullyLoaded` | 是否所有节点已加载到内存 | `ULidarPointCloud` |
| `IsOptimizedForDynamicData` | 是否启用了动态数据优化模式 | `ULidarPointCloud` |

### 空间查询（蓝图函数库）

这些函数是 `ULidarPointCloudBlueprintLibrary` 的静态函数，通过点云组件的 `WorldContextObject` 调用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasPointsInSphere` | 球体内是否存在点 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `HasPointsInBox` | 盒体内是否存在点 | 同上 |
| `HasPointsByRay` | 射线是否命中点 | 同上 |
| `LineTraceSingle` | 射线检测，返回第一个命中的点 | 同上 |
| `LineTraceMulti` | 射线检测，返回所有命中点 | 同上 |
| `GetPointsInSphereAsCopies` | 获取球体内点的副本 | 同上 |
| `GetPointsInBoxAsCopies` | 获取盒体内点的副本 | 同上 |
| `GetPointsAsCopies` | 获取所有点的副本（支持分页） | `ULidarPointCloud` |

### 可见性控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetVisibilityOfPointsInSphere` | 设置球体内点的可见性 | `ULidarPointCloud` / `ULidarPointCloudComponent` |
| `SetVisibilityOfPointsInBox` | 设置盒体内点的可见性 | 同上 |
| `SetVisibilityOfFirstPointByRay` | 设置射线首个命中点的可见性 | 同上 |
| `SetVisibilityOfPointsByRay` | 设置射线所有命中点的可见性 | 同上 |
| `HideAll` / `UnhideAll` | 隐藏/显示所有点 | `ULidarPointCloud` |

### 颜色编辑

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyColorToAllPoints` | 对所有点应用颜色 | `ULidarPointCloud` |
| `ApplyColorToPointsInSphere` | 对球体内点应用颜色 | 同上 |
| `ApplyColorToPointsInBox` | 对盒体内点应用颜色 | 同上 |
| `ApplyColorToFirstPointByRay` | 对射线首个命中点应用颜色 | 同上 |
| `ApplyColorToPointsByRay` | 对射线所有命中点应用颜色 | 同上 |

### 数据修改

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InsertPoint` / `InsertPoints` | 插入一个/一组点 | `ULidarPointCloud` |
| `RemovePoint` | 删除指定点 | `ULidarPointCloud` |
| `RemovePointsInSphere` | 删除球体内所有点 | 同上 |
| `RemovePointsInBox` | 删除盒体内所有点 | 同上 |
| `RemoveFirstPointByRay` | 删除射线首个命中点 | 同上 |
| `RemovePointsByRay` | 删除射线所有命中点 | 同上 |

### 碰撞与法线

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildCollision` | 构建碰撞网格 | `ULidarPointCloud` |
| `BuildCollisionWithCallback` | 带回调的异步碰撞构建 | `ULidarPointCloud` |
| `RemoveCollision` | 移除碰撞网格 | `ULidarPointCloud` |
| `HasCollisionData` | 是否已生成碰撞数据 | `ULidarPointCloud` |
| `GetColliderPolys` | 返回碰撞多边形数 | `ULidarPointCloud` |

### 坐标与导入导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLocationOffset` | 设置位置偏移 | `ULidarPointCloud` |
| `CenterPoints` | 将点云居中 | `ULidarPointCloud` |
| `RestoreOriginalCoordinates` | 恢复原始坐标 | `ULidarPointCloud` |
| `Reimport` | 从源文件重新导入（支持异步） | `ULidarPointCloud` |
| `Export` | 导出到文件 | `ULidarPointCloud` |

### 蓝图函数库（静态节点）

`ULidarPointCloudBlueprintLibrary` 提供了可通过任何 `WorldContextObject` 调用的静态函数，方便在任何蓝图中对场景中的点云进行操作：

| 节点 | 说明 |
|---|---|
| `LineTraceSingle` (静态) | 对场景中的所有点云执行射线检测 |
| `LineTraceMulti` (静态) | 返回所有命中点 |
| `SetVisibilityOfPointsInSphere` (静态) | 对场景中点云设置可见性 |
| `ApplyColorToPointsInSphere` (静态) | 对场景中点云应用颜色 |

### 使用示例（蓝图描述）

**场景1：射线检测点云**

1. 获取场景中的 `ALidarPointCloudActor`，通过 `GetPointCloudComponent` → `LineTraceSingle` 进行射线检测
2. 将射线起点设为玩家摄像机位置，方向为摄像机朝向
3. 设置检测半径（如 50cm），`bVisibleOnly` 设为 true
4. 输出的 `FLidarPointCloudPoint` 结构体包含 `Location`、`Color`、`ClassificationID` 等信息

**场景2：动态编辑点云颜色**

1. 通过 `GetPointCloud` 获得 `ULidarPointCloud` 引用
2. 使用 `ApplyColorToPointsInSphere` 节点，传入球心坐标、半径和目标颜色
3. 可用于交互式编辑或实时数据可视化

**场景3：异步导入点云文件**

1. 使用 `Create Lidar Point Cloud From File (ASCII)` 或 LAS 对应节点
2. 设置 `bUseAsync=true`，连接 `AsyncMode` 执行引脚
3. 监听 `Progress` 浮点变量（0-1），更新加载进度条
4. 异步模式完成时获得 `ULidarPointCloud` 资产引用

## C++ 用法

### 头文件引入

```cpp
#include "LidarPointCloud.h"
#include "LidarPointCloudComponent.h"
#include "LidarPointCloudActor.h"
#include "LidarPointCloudShared.h"
#include "LidarPointCloudOctree.h"
#include "LidarPointCloudSettings.h"
```

### 基本用法

**创建点云并插入点**（参考 `ULidarPointCloud::Initialize` 和 `InsertPoints` 的使用方式）：

```cpp
// 创建一个新的点云资产
ULidarPointCloud* PointCloud = NewObject<ULidarPointCloud>();

// 初始化八叉树，传入包围盒范围
FBox Bounds(FVector(-5000, -5000, -5000), FVector(5000, 5000, 5000));
PointCloud->Initialize(Bounds);

// 准备点数据
TArray<FLidarPointCloudPoint> Points;
for (int32 i = 0; i < 100000; ++i)
{
    float X = FMath::RandRange(-5000.f, 5000.f);
    float Y = FMath::RandRange(-5000.f, 5000.f);
    float Z = FMath::RandRange(-5000.f, 5000.f);
    Points.Emplace(X, Y, Z);
}

// 批量插入点（多线程）
// ELidarPointCloudDuplicateHandling 控制重复点处理策略
PointCloud->InsertPoints(
    Points,
    ELidarPointCloudDuplicateHandling::SelectFirst,
    true,  // bRefreshPointsBounds
    FVector::ZeroVector  // Translation
);
```

*来源：基于 `LidarPointCloud.h` 中 `ULidarPointCloud::InsertPoints` 和 `ELidarPointCloudDuplicateHandling` 定义*

**从文件导入点云**：

```cpp
#include "IO/LidarPointCloudFileIO.h"
#include "IO/LidarPointCloudFileIO_LAS.h"

// 方法1：使用文件IO类自动检测格式
TSharedPtr<FLidarPointCloudImportSettings> Settings = 
    ULidarPointCloudFileIO::GetImportSettings(TEXT("scan_data.las"));

FLidarPointCloudImportResults Results;
bool bSuccess = ULidarPointCloudFileIO::Import(
    TEXT("/Path/To/scan_data.las"),
    Settings,
    Results
);

if (bSuccess && Results.PointCloud)
{
    ULidarPointCloud* ImportedCloud = Results.PointCloud;
    UE_LOG(LogTemp, Log, TEXT("导入成功，点数：%lld"), ImportedCloud->GetNumPoints());
}

// 方法2：异步导入
FLidarPointCloudAsyncParameters AsyncParams;
AsyncParams.bUseAsync = true;
AsyncParams.CompletionCallback = [](ULidarPointCloud* PointCloud)
{
    UE_LOG(LogTemp, Log, TEXT("异步导入完成"));
};
```

*来源：基于 `LidarPointCloudFileIO.h` 中 `ULidarPointCloudFileIO` 接口定义*

**在场景中显示点云**：

```cpp
#include "LidarPointCloudActor.h"

// 获取或生成点云 Actor
UWorld* World = GetWorld();
ALidarPointCloudActor* Actor = World->SpawnActor<ALidarPointCloudActor>();
Actor->SetPointCloud(ImportedCloud);

// 配置组件参数
ULidarPointCloudComponent* Component = Actor->GetPointCloudComponent();
Component->PointSize = 5.0f;                           // 点大小（设为0则渲染1像素点）
Component->ScalingMethod = ELidarPointCloudScalingMethod::PerNodeAdaptive;
Component->ColorSource = ELidarPointCloudColorationMode::Data;  // 使用原始颜色
Component->bUseFrustumCulling = true;
```

*来源：基于 `LidarPointCloudComponent.h` 和 `LidarPointCloudActor.h` 中的属性定义*

### 进阶用法

**空间查询与射线检测**：

```cpp
#include "LidarPointCloudShared.h"

// 射线检测 - 查找最近的命中点
FLidarPointCloudRay Ray(CameraLocation, CameraForward);
float Radius = 50.0f;  // 检测半径（cm）
bool bVisibleOnly = true;

FLidarPointCloudPoint* HitPoint = PointCloud->LineTraceSingle(Ray, Radius, bVisibleOnly);
if (HitPoint)
{
    FVector WorldLocation = (FVector)HitPoint->Location + PointCloud->LocationOffset;
    FColor PointColor = HitPoint->Color;
    uint8 Classification = HitPoint->ClassificationID;
}

// 多点射线检测 - 获取所有命中点
TArray<FLidarPointCloudPoint> AllHits;
bool bHit = PointCloud->LineTraceMulti(Ray, Radius, bVisibleOnly, true, AllHits);
// true = bReturnWorldSpace，结果为世界坐标

// 球形区域查询 - 获取指针数组（高效，不复制数据）
TArray<FLidarPointCloudPoint*> PointsInSphere;
FSphere QuerySphere(CenterLocation, 500.0f);
PointCloud->GetPointsInSphere(PointsInSphere, QuerySphere, true);
for (FLidarPointCloudPoint* Pt : PointsInSphere)
{
    // 直接操作原始数据，性能最优
}

// 使用 TFunction 在空间范围内批量执行操作
PointCloud->ExecuteActionOnPointsInSphere(
    [](FLidarPointCloudPoint* Point)
    {
        Point->Color = FColor::Red;  // 将区域内所有点染红
    },
    FSphere(FVector::ZeroVector, 1000.0f),
    true  // bVisibleOnly
);
```

*来源：基于 `LidarPointCloud.h` 和 `LidarPointCloudOctree.h` 中的查询函数*

**碰撞构建与异步回调**：

```cpp
// 配置碰撞精度（0 = 自动优化）
PointCloud->MaxCollisionError = 10.0f;  // 精度10cm

// 同步构建碰撞（阻塞）
PointCloud->BuildCollision();

// 异步构建碰撞（带完成回调）
PointCloud->BuildCollision([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("碰撞构建完成"));
    }
});

// 检查碰撞状态
if (PointCloud->HasCollisionData())
{
    int32 PolyCount = PointCloud->GetColliderPolys();
    UE_LOG(LogTemp, Log, TEXT("碰撞多边形数：%d"), PolyCount);
}
```

*来源：基于 `LidarPointCloud.h` 中 `BuildCollision` 和 `IInterface_CollisionDataProvider` 实现*

**LOD 与渲染参数调优**：

```cpp
#include "LidarPointCloudSettings.h"

// 访问全局设置
ULidarPointCloudSettings* Settings = GetMutableDefault<ULidarPointCloudSettings>();
Settings->MaxBucketSize = 5000;               // 节点最大桶大小
Settings->NodeGridResolution = 4;             // 节点网格分辨率
Settings->CachedNodeLifetime = 30.0f;         // 节点缓存时长（秒）
Settings->bUseFastRendering = true;           // 启用快速渲染（VRAM x4）
Settings->bPrioritizeActiveViewport = true;   // 优先活跃视口
Settings->bUseRenderDataSmoothing = true;     // 渲染数据生成平滑

// 组件渲染属性
Component->PointSizeBias = 0.04f;             // LOD 过渡平滑
Component->GapFillingStrength = 0.3f;         // 缝隙填充
Component->Saturation = FVector4(1.2f, 1.2f, 1.2f, 1.0f);
Component->Contrast = FVector4(1.1f, 1.1f, 1.1f, 1.0f);
Component->ColorTint = FLinearColor(0.9f, 1.0f, 0.95f, 1.0f);

// 应用渲染参数到材质
Component->ApplyRenderingParameters();
```

*来源：基于 `LidarPointCloudSettings.h` 和 `LidarPointCloudComponent.h` 中的渲染参数定义*

**裁剪体积（Clipping Volume）**：

```cpp
#include "LidarPointCloud.h"

// 创建裁剪体积 Actor
FActorSpawnParameters SpawnParams;
ALidarClippingVolume* ClipVolume = World->SpawnActor<ALidarClippingVolume>(
    FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

ClipVolume->bEnabled = true;
ClipVolume->Mode = ELidarClippingVolumeMode::ClipInside;  // 裁剪体积内部
ClipVolume->Priority = 1;  // 处理优先级（用于多个裁剪体积重叠时）
```

*来源：基于 `LidarPointCloud.h` 中 `ALidarClippingVolume` 定义*

## Demo 示例

### 最小可编译示例：运行时创建并显示点云

**MyLidarActor.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LidarPointCloudShared.h"
#include "MyLidarActor.generated.h"

class ULidarPointCloud;
class ULidarPointCloudComponent;

UCLASS()
class MYPROJECT_API AMyLidarActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLidarActor();

    virtual void BeginPlay() override;

    /** 生成随机点云数据并显示 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void GenerateRandomPointCloud(int32 NumPoints, FVector Extent);

    /** 在鼠标点击位置染红一个球形区域 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void PaintRegionRed(FVector WorldCenter, float Radius);

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<ULidarPointCloudComponent> PointCloudComp;

    UPROPERTY()
    TObjectPtr<ULidarPointCloud> PointCloudAsset;
};
```

**MyLidarActor.cpp**：

```cpp
#include "MyLidarActor.h"
#include "LidarPointCloud.h"
#include "LidarPointCloudComponent.h"

AMylidarActor::AMylidarActor()
{
    PrimaryActorTick.bCanEverTick = false;

    PointCloudComp = CreateDefaultSubobject<ULidarPointCloudComponent>(TEXT("PointCloud"));
    RootComponent = PointCloudComp;
}

void AMyLidarActor::BeginPlay()
{
    Super::BeginPlay();
    GenerateRandomPointCloud(100000, FVector(500, 500, 200));
}

void AMyLidarActor::GenerateRandomPointCloud(int32 NumPoints, FVector Extent)
{
    // 创建点云资产
    PointCloudAsset = NewObject<ULidarPointCloud>(this, TEXT("DemoPointCloud"));

    // 初始化八叉树
    PointCloudAsset->Initialize(FBox(-Extent, Extent));

    // 生成随机点数据
    TArray<FLidarPointCloudPoint> Points;
    Points.Reserve(NumPoints);

    for (int32 i = 0; i < NumPoints; ++i)
    {
        float X = FMath::RandRange(-Extent.X, Extent.X);
        float Y = FMath::RandRange(-Extent.Y, Extent.Y);
        float Z = FMath::RandRange(-Extent.Z, Extent.Z);

        // 创建带颜色的点（高度映射颜色）
        float HeightRatio = (Z + Extent.Z) / (2.0f * Extent.Z);
        float R = HeightRatio;
        float G = 1.0f - HeightRatio;
        float B = 0.3f;

        Points.Emplace(X, Y, Z, R, G, B);
    }

    // 批量插入（多线程安全）
    PointCloudAsset->InsertPoints(
        Points,
        ELidarPointCloudDuplicateHandling::Ignore,
        true,
        FVector::ZeroVector
    );

    // 将点云资产绑定到组件
    PointCloudComp->SetPointCloud(PointCloudAsset);
    PointCloudComp->PointSize = 8.0f;
    PointCloudComp->ScalingMethod = ELidarPointCloudScalingMethod::PerNodeAdaptive;
}

void AMyLidarActor::PaintRegionRed(FVector WorldCenter, float Radius)
{
    if (!PointCloudAsset) return;

    PointCloudAsset->ApplyColorToPointsInSphere(
        FColor::Red,
        WorldCenter,
        Radius,
        true  // bVisibleOnly
    );
}
```

## 模块依赖

从 `LidarPointCloudRuntime.Build.cs` 分析，该插件的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 构建碰撞网格时使用 MeshDescription 数据结构 |
| `ImageWriteQueue` | 编辑器模块中的图像导出相关 |
| `RenderCore` | 自定义顶点工厂和 GPU 缓冲区的渲染基础设施 |
| `RHI` | 底层图形硬件接口，用于 ShaderResourceView 等 |
| `PhysicsCore` | 碰撞网格构建（`FTriMeshCollisionData`） |

其余为标准 Core/Engine/Slate 等依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知重构，影响点云组件的视口交互 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 撤回之前的变更，恢复原始行为 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与 `cfb610df` 相同的视口重构 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 硬件光线追踪参数扩展，点云光线追踪几何体受影响 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复64位平台上格式化字符串的位宽不匹配问题 |

### 维护评价

**维护状态：维护中（被动维护）**

- **创建时间**：2020年1月，至今约6年，属于成熟的企业级插件
- **最近更新**：近期提交主要为引擎级别的重构（视口通知、光线追踪基础设施、格式修复），而非点云插件自身的功能增强。这表明该插件处于稳定运行状态，跟随引擎底层架构变动被动更新
- **活跃程度**：2026年仍有commit记录，但属于引擎全局重构的波及影响，非点云专项维护
- **已知限制**：
  - `EnabledByDefault=false`，需要手动启用
  - E57 格式需要额外的第三方库支持（`LIBE57SUPPORTED`）
  - LAZ 压缩格式需要 `LASZIPSUPPORTED` 编译标志
  - `bUseFastRendering` 会将 VRAM 使用量翻四倍，对显存有限的项目需谨慎
- **推荐使用**：✅ 推荐。作为 UE5 内置的企业级点云解决方案，功能完整度高，API 设计合理，蓝图和 C++ 双语言支持完善。适用于需要处理 LiDAR 扫描数据的建筑可视化、影视、仿真类项目。对于超大规模点云（10亿+点），需注意内存管理策略（启用 `bReleaseAssetAfterSaving`、合理配置 `CachedNodeLifetime`）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)