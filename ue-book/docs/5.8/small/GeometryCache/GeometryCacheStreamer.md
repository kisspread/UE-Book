# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件用于播放预先烘焙（distilled）的几何体动画。它主要解决以下问题：

1. **高效播放复杂几何体动画**：对于顶点数巨大、拓扑结构不断变化的动画（如软体模拟、布料、流体），传统的骨骼动画系统难以高效处理。GeometryCache 将每一帧的网格数据（顶点位置、法线、UV等）预先计算并存储，在运行时直接加载播放，避免了实时计算的性能开销。
2. **支持 Alembic (.abc) 文件导入**：该插件是 Unreal Engine 中 Alembic 文件导入器的后端。当用户导入 Alembic 文件并选择“导入为几何缓存”时，实际上就是使用此插件来解析和播放动画。
3. **流式加载大数据**：通过 `GeometryCacheStreamer` 模块，支持对几何体动画数据进行流式加载，避免一次性将所有帧数据加载到内存中，适用于非常长的动画序列。

## 使用场景

- **视觉特效（VFX）**：播放由外部软件（如 Houdini, Maya, Blender）模拟生成的布料、流体、粒子等复杂几何体动画。
- **数字人/角色**：播放面部捕捉或复杂的次级运动（如头发、衣物）动画。
- **动画预览与回放**：在引擎内回放从 DCC 工具导出的高精度动画缓存。
- **大型场景动画**：当动画数据量过大，无法一次性加载到内存时，使用流式加载功能。

## 蓝图用法

GeometryCache 的蓝图节点主要集中在 `UGeometryCacheComponent` 类中。以下为核心节点分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Geometry Cache` | 设置组件要播放的 GeometryCache 资源。 | `UGeometryCacheComponent` |
| `Play` | 从当前时间点开始播放动画。 | `UGeometryCacheComponent` |
| `Play from Start` | 从第 0 帧开始播放动画。 | `UGeometryCacheComponent` |
| `Stop` | 停止播放。 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放。 | `UGeometryCacheComponent` |
| `Set Playback Speed` | 设置播放速度倍率。 | `UGeometryCacheComponent` |
| `Set Looping` | 设置是否循环播放。 | `UGeometryCacheComponent` |
| `Set Current Time` | 设置当前播放时间点（以秒为单位）。 | `UGeometryCacheComponent` |
| `Set Current Frame` | 设置当前播放的帧索引。 | `UGeometryCacheComponent` |
| `Get Playback Speed` | 获取当前播放速度。 | `UGeometryCacheComponent` |
| `Get Looping` | 获取是否循环播放。 | `UGeometryCacheComponent` |
| `Get Duration` | 获取动画总时长（秒）。 | `UGeometryCacheComponent` |
| `Get Num Frames` | 获取动画总帧数。 | `UGeometryCacheComponent` |
| `Is Playing` | 查询是否正在播放。 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

**示例1：播放一个 GeometryCache**
1. 在 Actor 中添加一个 `GeometryCacheComponent`。
2. 从内容浏览器拖拽一个 GeometryCache 资源（通常是导入的 .abc 文件）到组件的 `Geometry Cache` 属性上，或使用 `Set Geometry Cache` 节点在运行时设置。
3. 调用 `Play from Start` 节点开始播放。

**示例2：控制播放进度**
1. 使用 `Set Playback Speed` 节点将速度设为 2.0，实现快进效果。
2. 使用 `Set Current Time` 节点跳转到特定时间点（如 `Duration * 0.5`）。

**示例3：响应播放完成事件**
1. 在 `GeometryCacheComponent` 的事件列表中，绑定 `On Playback Finished` 事件。
2. 在该事件内执行播放下一个动画或清理资源的操作。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
#include "GeometryCacheMeshData.h"
```

### 基本用法

```cpp
// 在构造函数或BeginPlay中获取组件指针
UGeometryCacheComponent* CacheComp = FindComponentByClass<UGeometryCacheComponent>();

if (CacheComp)
{
    // 设置缓存资源
    UGeometryCache* MyCache = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/Path/To/YourCache"));
    CacheComp->SetGeometryCache(MyCache);

    // 播放
    CacheComp->Play();

    // 设置播放速度
    CacheComp->SetPlaybackSpeed(1.5f);

    // 设置为循环播放
    CacheComp->SetLooping(true);
}

// 监听播放结束
CacheComp->OnPlaybackFinished.AddDynamic(this, &AMyActor::HandlePlaybackFinished);
```

### 进阶用法：访问每一帧的网格数据

GeometryCacheTrack 提供了直接访问网格数据的接口，适用于需要在运行时修改顶点的高级用法。

```cpp
// 假设我们有一个UGeometryCacheTrack指针，通常可以通过遍历UGeometryCache资源获得
UGeometryCacheTrack* Track = GetCacheTrack();

if (Track)
{
    FGeometryCacheMeshData MeshData;
    // 获取特定帧（例如第10帧）的网格数据
    bool bSuccess = Track->GetMeshData(10, MeshData);

    if (bSuccess)
    {
        // 现在可以访问顶点数据了
        TArray<FVector3f>& Vertices = MeshData.Positions;
        // 例如，计算包围盒
        FBox Bounds(ForceInit);
        for (const FVector3f& Vert : Vertices)
        {
            Bounds += FVector(Vert);
        }
        UE_LOG(LogTemp, Log, TEXT("Bounding Box: %s"), *Bounds.ToString());
    }
}
```

## Demo 示例

**.h 文件**
```cpp
// MyGeometryCacheActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGeometryCacheActor.generated.h"

class UGeometryCacheComponent;
class UGeometryCache;

UCLASS()
class MYPROJECT_API AMyGeometryCacheActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGeometryCacheActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Geometry Cache")
    UGeometryCacheComponent* GeometryCacheComponent;

    UPROPERTY(EditAnywhere, Category = "Geometry Cache")
    UGeometryCache* GeometryCacheAsset;

    UFUNCTION()
    void OnPlaybackFinished();

    void TogglePlayback();
};
```

**.cpp 文件**
```cpp
// MyGeometryCacheActor.cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    PrimaryActorTick.bCanEverTick = false;

    GeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCacheComponent"));
    RootComponent = GeometryCacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();

    if (GeometryCacheAsset && GeometryCacheComponent)
    {
        // 设置资源
        GeometryCacheComponent->SetGeometryCache(GeometryCacheAsset);
        // 设置为循环播放
        GeometryCacheComponent->SetLooping(true);
        // 绑定事件
        GeometryCacheComponent->OnPlaybackFinished.AddDynamic(this, &AMyGeometryCacheActor::OnPlaybackFinished);
        // 开始播放
        GeometryCacheComponent->Play();
    }
}

void AMyGeometryCacheActor::OnPlaybackFinished()
{
    UE_LOG(LogTemp, Log, TEXT("Geometry Cache playback finished."));
    // 可以在这里触发下一个动画或做其他处理
}

void AMyGeometryCacheActor::TogglePlayback()
{
    if (GeometryCacheComponent)
    {
        if (GeometryCacheComponent->IsPlaying())
        {
            GeometryCacheComponent->Pause();
        }
        else
        {
            GeometryCacheComponent->Play();
        }
    }
}
```

## 模块依赖

`GeometryCache` 插件的模块依赖较为特殊，因为它既包含运行时功能，也包含编辑器特定功能（用于导入）。

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 提供网格处理的通用工具函数。 |
| `UnrealEd` | 提供编辑器功能，主要用于 Alembic 文件的导入和处理。 |

**注意**：`GeometryCacheEd` 和 `GeometryCacheSequencer` 模块依赖于 `UnrealEd`，因此仅在编辑器环境下可用。在运行时打包时，这些模块不会被包含。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport. | 重构了视口通知机制，与几何缓存无直接关系，属于引擎基础框架更新。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一个特定的提交（可能是引入了问题）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport. | 与 `cfb610df` 相同，是同一次修改的多次提交。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 宏迁移到新的 `UE_LOGF`，属于日志系统现代化更新。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 模块更新，新增了一个简单的可工具化时间线视图功能。 |

### 维护评价

- **活跃度**：**高**。插件自 2022 年从实验性模块迁移到正式模块后，一直保持活跃维护。最近的提交记录显示，它随着引擎核心框架（如视口、日志系统）和 Sequencer 模块的更新而同步更新，表明它被集成在主开发分支中。
- **稳定性**：作为官方支持的 Alembic 导入后端，其核心功能稳定。近期更新多为框架适配和编辑器功能增强，未见重大缺陷报告。
- **推荐使用**：**推荐**。对于需要播放复杂几何体动画的项目，这是官方提供的标准解决方案。其流式加载功能（`GeometryCacheStreamer`）能有效管理大体积动画数据，适合生产环境使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)（重点在于如何导入和使用）