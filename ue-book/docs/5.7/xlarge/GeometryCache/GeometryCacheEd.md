# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-04-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache) | |

---

## 用途

GeometryCache 插件用于导入和回放**预烘焙的几何体动画**（Geometry Animation）。它解决的核心问题是：当网格体的顶点逐帧变化（而非骨骼驱动）时，如何高效地在 UE5 中播放这类动画数据。

典型来源包括：
- **Alembic (.abc) 文件**：从 Houdini、Maya、Blender 等 DCC 工具导出的顶点缓存动画（布料模拟、流体、破碎、粒子转网格体等）
- **程序化生成的帧数据**：运行时或离线生成的逐帧网格体变形

与骨骼动画不同，GeometryCache 存储的是每一帧完整的顶点位置数据，因此适合**拓扑结构会变化**或**变形极其复杂**的场景。代价是内存/磁盘占用较大，插件通过 Streaming 模块来缓解这个问题。

## 使用场景

- 你在 Houdini 中做了一个布料模拟，导出为 Alembic → 用 GeometryCache 导入并在引擎中回放
- 你需要在实时场景中播放预烘焙的破碎动画（碎石飞溅）→ 用 GeometryCache
- 你在 Sequencer 中编排过场动画，需要精确控制几何体变形的时间线 → 用 GeometryCache + GeometryCacheSequencer
- 你的 GeometryCache 文件很大（数 GB），需要按需加载 → 用 GeometryCacheStreamer
- 你从 Maya 导出了一段粒子转网格体的流体动画 → 用 GeometryCache 导入

## 蓝图用法

GeometryCache 的蓝图交互主要通过 `UGeometryCacheComponent` 完成，该组件负责挂载和回放 GeometryCache 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 从当前位置开始正向播放 | `UGeometryCacheComponent` |
| `PlayReversed` | 从当前位置开始反向播放 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放 | `UGeometryCacheComponent` |
| `Stop` | 停止播放并重置到起始位置 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度倍率（默认 1.0） | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取当前播放速度 | `UGeometryCacheComponent` |
| `SetLooping` | 设置是否循环播放 | `UGeometryCacheComponent` |
| `IsLooping` | 查询是否为循环模式 | `UGeometryCacheComponent` |
| `IsPlaying` | 查询是否正在播放 | `UGeometryCacheComponent` |
| `IsPaused` | 查询是否已暂停 | `UGeometryCacheComponent` |
| `GetDuration` | 获取动画总时长（秒） | `UGeometryCacheComponent` |
| `GetNumberOfFrames` | 获取总帧数 | `UGeometryCacheComponent` |
| `SetStartTimeOffset` | 设置起始时间偏移 | `UGeometryCacheComponent` |
| `GetStartTimeOffset` | 获取起始时间偏移 | `UGeometryCacheComponent` |
| `SetGeometryCache` | 运行时切换 GeometryCache 资产 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

**基本回放控制：**

1. 在 Actor 上添加 `GeometryCacheComponent`
2. 在 Details 面板中指定 `GeometryCache` 资产
3. 勾选 `bAutoPlay` 实现自动播放，或在 BeginPlay 中调用 `Play` 节点

**Sequencer 集成：**

1. 在 Sequencer 中为 GeometryCacheActor 添加轨道
2. 使用 GeometryCacheSection 控制播放的起止帧
3. 可通过曲线控制播放速度

**运行时切换缓存：**

1. 获取 GeometryCacheComponent 引用
2. 调用 `Stop` 停止当前播放
3. 调用 `SetGeometryCache` 传入新的 UGeometryCache 资产
4. 调用 `Play` 开始播放新缓存

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
```

### 基本用法

创建一个 GeometryCacheComponent 并控制回放：

```cpp
// 在 Actor 中创建组件
UPROPERTY(VisibleAnywhere)
UGeometryCacheComponent* CacheComponent;

// BeginPlay 中初始化
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    CacheComponent = NewObject<UGeometryCacheComponent>(this);
    CacheComponent->RegisterComponent();
    CacheComponent->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);

    // 加载 GeometryCache 资产
    UGeometryCache* Cache = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/MyGeometryCache"));
    if (Cache)
    {
        CacheComponent->SetGeometryCache(Cache);
        CacheComponent->SetLooping(true);
        CacheComponent->SetPlaybackSpeed(1.0f);
        CacheComponent->Play();
    }
}
```

### 进阶用法

**查询播放状态并响应事件：**

```cpp
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (CacheComponent && CacheComponent->IsPlaying())
    {
        // 获取当前播放进度
        float Duration = CacheComponent->GetDuration();
        int32 NumFrames = CacheComponent->GetNumberOfFrames();

        UE_LOG(LogTemp, Log, TEXT("GeometryCache: %d frames, %.2f seconds"), NumFrames, Duration);
    }
}

// 动态调整播放参数
void AMyActor::SetSlowMotion()
{
    CacheComponent->SetPlaybackSpeed(0.25f);
}

void AMyActor::ReversePlay()
{
    CacheComponent->Stop();
    CacheComponent->PlayReversed();
}
```

**程序化生成 GeometryCache（高级用法）：**

```cpp
#include "GeometryCache.h"
#include "GeometryCacheTrack.h"

// 通过工厂方法或编辑器导入创建 GeometryCache 资产
// 运行时通常通过 SetGeometryCache 切换预导入的资产
```

## Demo 示例

### 最小可编译示例：GeometryCache 回放 Actor

**MyGeometryCacheActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGeometryCacheActor.generated.h"

class UGeometryCacheComponent;

UCLASS()
class AMyGeometryCacheActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGeometryCacheActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "GeometryCache")
    UGeometryCacheComponent* CacheComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "GeometryCache")
    float PlaybackSpeed = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "GeometryCache")
    bool bLoop = true;

    UFUNCTION(BlueprintCallable, Category = "GeometryCache")
    void RestartPlayback();

protected:
    virtual void BeginPlay() override;
};
```

**MyGeometryCacheActor.cpp**

```cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    CacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCache"));
    RootComponent = CacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();

    CacheComponent->SetLooping(bLoop);
    CacheComponent->SetPlaybackSpeed(PlaybackSpeed);
    CacheComponent->Play();
}

void AMyGeometryCacheActor::RestartPlayback()
{
    CacheComponent->Stop();
    CacheComponent->Play();
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "GeometryCache"
});
```

## 模块依赖

从各模块的 Build.cs 提取的独特依赖（已省略 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 网格体工具通用功能，用于几何体数据处理 |
| `RenderCore` | 渲染核心，用于 GPU 顶点数据上传 |
| `RHI` | 渲染硬件接口，用于底层缓冲区管理 |
| `SequencerCore` | Sequencer 核心，用于时间线集成 |
| `MovieScene` | 影片场景框架，用于 Sequencer 轨道支持 |
| `LevelSequence` | 关卡序列，用于序列化播放控制 |

## 子模块概览

由于本插件规模较大（xlarge，180 个源文件），按模块拆分说明：

| 模块 | 类型 | 职责 |
|---|---|---|
| **GeometryCache** | Runtime | 核心模块：资产类 `UGeometryCache`、组件 `UGeometryCacheComponent`、轨道基类 `UGeometryCacheTrack`、渲染代理、序列化 |
| **GeometryCacheEd** | Runtime | 编辑器支持：资产缩略图渲染、Actor 工厂（拖放创建）、资产代理（组件-资产绑定）、资产定义（内容浏览器显示） |
| **GeometryCacheSequencer** | Runtime | Sequencer 集成：GeometryCache Section 和 Track，支持在时间线中精确控制缓存回放 |
| **GeometryCacheStreamer** | Runtime | 流式加载：支持大型 GeometryCache 文件的按需加载，减少内存峰值占用 |
| **GeometryCacheTracks** | Runtime | 轨道实现：Flipbook 动画轨道、Transform 组动画轨道、可流式轨道等具体轨道类型 |

### GeometryCacheEd 模块详情

编辑器集成模块，提供以下功能：

| 类 | 职责 |
|---|---|
| `FGeometryCacheEdModule` | 模块入口，管理 AssetBroker 的生命周期 |
| `FGeometryCacheAssetBroker` | 资产代理：实现 `IComponentAssetBroker` 接口，支持将 GeometryCache 资产拖放到组件上 |
| `UActorFactoryGeometryCache` | Actor 工厂：将 GeometryCache 资产拖入视口时自动创建 `AGeometryCacheActor` |
| `UAssetDefinition_GeometryCache` | 资产定义：定义内容浏览器中的显示名称、颜色、分类、导入支持和打开行为 |
| `FGeometryCacheThumbnailScene` | 缩略图场景：为内容浏览器缩略图设置预览 Actor 和摄像机参数 |
| `UGeometryCacheThumbnailRenderer` | 缩略图渲染器：在内容浏览器中渲染 GeometryCache 资产的预览图 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `03a86c9cdc3a` | Fix hang when previewing Geometry Cache with 1 frame | 修复了只有 1 帧的 GeometryCache 在预览时挂起的 bug |
| 近期 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码现代化：添加内联生成宏，减少编译时间 |
| 近期 | `f57e1f6aa544` | Remove legacy viewport toolbar usage | 编辑器 UI 适配：迁移到新的视口工具栏系统 |

### 维护评价

- **创建时间**：2018 年，约 7 年历史，是 UE 的成熟功能模块
- **更新频率**：持续有维护性更新，包括 bug 修复和引擎框架适配
- **维护状态**：**活跃维护中** — 作为 UE5 核心功能的一部分，随引擎版本持续更新
- **已知限制**：
  - 大型 GeometryCache 文件内存占用较高（可通过 Streamer 模块缓解）
  - 不支持运行时程序化生成缓存数据（需通过编辑器导入）
  - Alembic 导入流程依赖编辑器，运行时无法导入
- **推荐程度**：✅ **推荐使用** — 这是 UE5 处理顶点动画缓存的标准方案，功能成熟稳定，与 Sequencer 深度集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)