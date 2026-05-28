# USD Geometry Cache

> GeometryCacheUSD模块，为虚幻引擎提供从USD文件实时读取、流式加载和播放几何缓存（动态网格序列）的功能。

| 属性 | 值 |
|---|---|
| 中文名 | USD几何缓存 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、蓝图资产） |
| 模块 | `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |
| [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) | |

## 用途

`GeometryCacheUSD` 模块的核心作用是扩展虚幻引擎的几何缓存（GeometryCache）系统，使其能够直接从 USD 文件中实时读取和播放动态网格序列（例如角色动画、物理模拟或程序化动画）。它解决了传统几何缓存需要预先烘焙为专有资产的问题，允许开发者直接使用标准 USD 文件作为动画源，实现了跨DCC工具的无缝资产管线。通过流式加载机制，它还能优化内存使用，按需加载帧数据。

## 使用场景

- 你在使用USD格式进行资产交换，并希望直接在UE场景中预览或播放动态扫描的3D模型（如面部捕捉数据）。
- 你的动画管线主要基于USD（例如使用Houdini、Maya+USD插件生成），需要在虚幻中实时播放这些动画序列而无需中间转换。
- 你需要在建筑可视化或虚拟制片项目中，播放由外部程序生成的复杂、长序列的几何动画（如施工模拟、人群动画）。

## 蓝图用法

### 核心节点

基于 `UGeometryCacheTrackUsd` 和 `UGeometryCacheUsdComponent` 的蓝图类型暴露。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 使用USD Stage和Prim路径初始化几何缓存轨道 | `UGeometryCacheTrackUsd` |
| `UpdateMeshData` | 根据当前时间和播放状态更新网格数据 | `UGeometryCacheTrackUsd` |
| `GetMeshDataAtTime` | 获取指定时间点的网格数据 | `UGeometryCacheTrackUsd` |
| `LoadUsdStage` | 加载或重新关联USD Stage | `UGeometryCacheTrackUsd` |
| `UnloadUsdStage` | 卸载USD Stage以释放资源 | `UGeometryCacheTrackUsd` |
| `RegisterStream` / `UnregisterStream` | 注册/注销数据流，控制数据加载行为 | `UGeometryCacheTrackUsd` |
| （继承）播放、循环、速率控制等 | 来自父类 `UGeometryCacheComponent` | `UGeometryCacheUsdComponent` |

### 使用示例（蓝图描述）

1.  **设置阶段**：在蓝图中创建一个 `GeometryCacheUsdComponent` 组件。
2.  **初始化**：调用其关联的 `UGeometryCacheTrackUsd` 的 `Initialize` 节点，连接一个 `FUsdStage` 对象（通常由USD Stage资产提供），并指定Prim路径、起止帧和读取函数。
3.  **生命周期管理**：在Actor的 `BeginPlay` 中调用 `LoadUsdStage`，在 `EndPlay` 中调用 `UnloadUsdStage` 以管理资源。
4.  **播放控制**：通过组件的父类接口（如 `Play`、`SetPlaybackSpeed`）控制动画播放。动画播放时，组件内部会调用 `UpdateMeshData` 来获取新帧数据。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheUSD.h"
// 通常还需要包含 USD SDK 相关头文件
```

### 基本用法

从 `UGeometryCacheTrackUsd` 类提取的初始化和使用逻辑。

```cpp
// 假设已有 UsdStage 和 PrimPath
UE::FUsdStage MyStage = ...;
FString PrimPath = TEXT("/My/Animated/Mesh");
int32 StartFrame = 0;
int32 EndFrame = 100;

// 定义读取网格的回调函数
FReadUsdMeshFunction ReadFunc = [](const TWeakObjectPtr<UGeometryCacheTrackUsd> Track, float Time, FGeometryCacheMeshData& OutMeshData) -> bool
{
    // 在这里实现从 USD Stage 读取特定时间网格数据的逻辑
    // 例如使用 UsdToUnreal::ConvertMesh 等工具函数
    return true; // 返回是否成功
};

// 在某个 UObject（如自定义资产或Actor组件）中创建并初始化 Track
UGeometryCacheTrackUsd* Track = NewObject<UGeometryCacheTrackUsd>();
Track->Initialize(MyStage, PrimPath, StartFrame, EndFrame, ReadFunc);

// 在需要时加载 Stage 并注册流
Track->LoadUsdStage();
Track->RegisterStream();

// ... 在游戏运行时，通过 GeometryCacheUsdComponent 或直接调用 Track 的接口播放动画

// 结束时清理
Track->UnregisterStream();
Track->UnloadUsdStage();
```

### 进阶用法

结合 `UGeometryCacheUsdComponent` 在 Actor 中完整使用，并处理流式加载。

```cpp
// MyActor.h
UCLASS()
class AMyUSDActor : public AActor
{
    GENERATED_BODY()
public:
    AMyUSDActor();

    UPROPERTY(VisibleAnywhere)
    UGeometryCacheUsdComponent* UsdGeoCacheComp;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    UGeometryCacheTrackUsd* InternalTrack;
};

// MyActor.cpp
AMyUSDActor::AMyUSDActor()
{
    UsdGeoCacheComp = CreateDefaultSubobject<UGeometryCacheUsdComponent>(TEXT("USDGeoCache"));
    // 组件会自动管理其内部的 Track 资产
}

void AMyUSDActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取组件内部使用的 Track (假设已经通过蓝图或代码设置好)
    if (UGeometryCache* GeoCache = UsdGeoCacheComp->GetGeometryCache())
    {
        if (UGeometryCacheTrackUsd* Track = Cast<UGeometryCacheTrackUsd>(GeoCache->Tracks[0]))
        {
            Track->LoadUsdStage();
            Track->RegisterStream();
        }
    }
}

void AMyUSDActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UGeometryCache* GeoCache = UsdGeoCacheComp->GetGeometryCache())
    {
        if (UGeometryCacheTrackUsd* Track = Cast<UGeometryCacheTrackUsd>(GeoCache->Tracks[0]))
        {
            Track->UnregisterStream();
            Track->UnloadUsdStage();
        }
    }
    Super::EndPlay(EndPlayReason);
}
```

## Demo 示例

一个最小的、可在Actor中播放USD几何缓存的C++示例。

**USDGeometryActor.h**
```cpp
// 版权所有 Epic Games。保留所有权利。
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDGeometryActor.generated.h"

class UGeometryCacheUsdComponent;
class UGeometryCacheTrackUsd;

UCLASS()
class AUSDGeometryActor : public AActor
{
    GENERATED_BODY()

public:
    AUSDGeometryActor();

    // USD Stage 的路径
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "USD")
    FFilePath UsdStagePath;

    // 要加载的 Prim 路径
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "USD")
    FString UsdPrimPath;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY(VisibleAnywhere)
    UGeometryCacheUsdComponent* GeoCacheComponent;
};
```

**USDGeometryActor.cpp**
```cpp
// 版权所有 Epic Games。保留所有权利。
#include "USDGeometryActor.h"
#include "Components/GeometryCacheUsdComponent.h"
#include "GeometryCacheUSD.h"

AUSDGeometryActor::AUSDGeometryActor()
{
    GeoCacheComponent = CreateDefaultSubobject<UGeometryCacheUsdComponent>(TEXT("USDGeoCache"));
    RootComponent = GeoCacheComponent;
}

void AUSDGeometryActor::BeginPlay()
{
    Super::BeginPlay();

    // 此示例假设通过蓝图或其他方式已经为组件设置了包含 UGeometryCacheTrackUsd 的 GeometryCache 资产
    // 这里演示如何管理其内部 Track 的 Stage 生命周期
    UGeometryCache* GeoCache = GeoCacheComponent->GetGeometryCache();
    if (GeoCache && GeoCache->Tracks.Num() > 0)
    {
        UGeometryCacheTrackUsd* UsdTrack = Cast<UGeometryCacheTrackUsd>(GeoCache->Tracks[0]);
        if (UsdTrack)
        {
            UsdTrack->LoadUsdStage();
            UsdTrack->RegisterStream();
            // 可以设置播放参数
            GeoCacheComponent->Play();
        }
    }
}

void AUSDGeometryActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UGeometryCache* GeoCache = GeoCacheComponent->GetGeometryCache();
    if (GeoCache && GeoCache->Tracks.Num() > 0)
    {
        UGeometryCacheTrackUsd* UsdTrack = Cast<UGeometryCacheTrackUsd>(GeoCache->Tracks[0]);
        if (UsdTrack)
        {
            UsdTrack->UnregisterStream();
            UsdTrack->UnloadUsdStage();
        }
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `GeometryCacheUSD.Build.cs` 和代码推断的依赖关系。

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 基础几何缓存系统，是本模块的基类所在 |
| `USDIntegration` | USD SDK 与虚幻引擎集成的核心库 |
| `USDUtilities` | USD 工具函数库，用于 Stage、Prim 操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转换为单精度时的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增对独立于蓝图的控制绑定的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD varies | USD: 解决升级到26.03后，因LOD变化导致AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正32位格式说明符在参数为64位时的使用，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

- **活跃维护**：尽管插件创建于2018年（约7年），但Git记录显示直到2026年仍有持续的功能更新和Bug修复（如控制绑定支持、LOD相关修复），表明**仍在积极维护**。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明这仍是一个**实验性插件**，API和功能可能在未来版本中发生变化。
- **推荐使用**：推荐在USD工作流中需要实时预览动态几何的**实验性或开发环境**中使用。在生产环境中使用需谨慎，关注版本兼容性，并做好应对未来API变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)