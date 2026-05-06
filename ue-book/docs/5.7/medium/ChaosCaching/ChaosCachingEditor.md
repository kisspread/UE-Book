# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（缓存资产、编辑器工具） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件提供了对 Chaos 物理模拟进行记录和回放的支持。在游戏开发中，物理模拟通常是不确定的，在不同帧率或平台上表现可能不一致。通过将物理模拟状态缓存为资产，开发者可以在需要时精确回放预先计算好的物理效果，而无需重新运行模拟。该插件尤其适用于：

- 需要精确重现物理事件的过场动画（如爆炸、倒塌）
- 网络环境下同步复杂的物理效果
- 性能优化：将昂贵的物理计算预先录制，运行时仅播放缓存数据

本编辑器模块（ChaosCachingEditor）提供了在编辑器中创建、编辑和管理缓存的工具，并深度集成到了 Sequencer（过场动画编辑器）和 Take Recorder（录制系统）中，方便艺术家和设计师使用。

## 使用场景

- **过场动画中的物理特效**：你想在过场动画中播放一个精确的物理爆炸效果，但每次回放时物理模拟可能略有不同。你可以先用 Chaos 模拟录制一次，然后使用 ChaosCaching 将这段物理缓存应用到过场动画中，确保每次播放效果完全一致。
- **多人游戏中的物理同步**：在多人游戏中，同步所有客户端的物理模拟非常困难。你可以将关键物理事件缓存下来，在服务器上播放并广播给客户端，避免物理差异导致的不同步问题。
- **性能优化**：某些场景（如大量布娃娃、碎片）物理计算开销大，可以预先录制并回放，从而在运行时节省 CPU/GPU 资源。

## 蓝图用法

### 核心节点

本模块主要面向编辑器操作，不直接暴露大量蓝图可调用函数。但以下类和函数可在蓝图中使用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ChaosCacheManager` | 蓝图中的 Chaos 缓存管理器 Actor（需从编辑器创建） | `AChaosCacheManager` (Runtime 模块) |
| `ChaosCacheManager->Activate` | 激活缓存管理器开始回放 | `AChaosCacheManager` (Runtime 模块) |
| `ChaosCacheManager->Deactivate` | 停止回放 | `AChaosCacheManager` (Runtime 模块) |
| `ObservedComponent` 结构中的 `Cache Mode` | 控制每个组件的记录/回放模式 | `FObservedComponent` (Runtime 模块) |

> 注意：运行时模块 `ChaosCaching` 提供了 `AChaosCacheManager` 以及相关的结构体和函数，这些可在蓝图中使用。编辑器模块主要负责创建工作流，但蓝图接口需要引用 Runtime 模块。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManager.h"          // AChaosCacheManager 等
#include "Chaos/CacheCollection.h"       // UChaosCacheCollection
#include "Chaos/CacheEditorCommands.h"    // 编辑器命令
```

### 基本用法

在 C++ 中，你可以通过编程方式创建和管理缓存管理器，并设置其属性。

```cpp
// 来源: Engine/Plugins/Experimental/ChaosCaching/Source/ChaosCachingEditor/Private/ActorFactoryCacheManager.cpp

#include "Chaos/ActorFactoryCacheManager.h"

// 使用 ActorFactory 从 ChaosCacheCollection 资产创建缓存管理器 Actor
UChaosCacheCollection* CacheCollection = LoadObject<UChaosCacheCollection>(nullptr, TEXT("/Game/MyCaches/ExplosionCache.ExplosionCache"));
if (CacheCollection)
{
    UActorFactoryCacheManager* Factory = NewObject<UActorFactoryCacheManager>();
    AActor* NewActor = Factory->CreateActor(CacheCollection, World->GetCurrentLevel(), FTransform::Identity);
    // NewActor 将自动附加 ChaosCacheManager 组件
}
```

### 进阶用法

更复杂的用法涉及 Sequencer 集成，例如在 C++ 中创建 Chaos Cache 轨道：

```cpp
// 来源: Engine/Plugins/Experimental/ChaosCaching/Source/ChaosCachingEditor/Private/ChaosCacheTrackEditor.cpp

// 在 Sequencer 中为指定对象绑定添加 Chaos Cache 轨道
void FChaosCacheTrackEditor::BuildChaosCacheTrack(TArray<FGuid> ObjectBindings, UMovieSceneTrack* Track)
{
    // 解析 ObjectBindings 并添加轨道
    // 具体实现见源代码
}
```

通过 `FMovieSceneChaosCacheTrackRecorder` 可以在录制时记录 Chaos 缓存：

```cpp
// 来源: Engine/Plugins/Experimental/ChaosCaching/Source/ChaosCachingEditor/Private/MovieSceneChaosCacheTrackRecorder.cpp

// 创建轨道录制器并开始录制
UMovieSceneChaosCacheTrackRecorder* Recorder = NewObject<UMovieSceneChaosCacheTrackRecorder>();
Recorder->CreateTrackImpl();                                    // 创建轨道
Recorder->RecordSampleImpl(CurrentFrameTime);                   // 每一帧录制
Recorder->FinalizeTrackImpl();                                  // 结束录制
```

## Demo 示例

以下是一个最小示例，演示如何在编辑器中使用 C++ 创建缓存管理器 Actor 并开始回放。

**CacheDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CacheDemoActor.generated.h"

class AChaosCacheManager;
class UChaosCacheCollection;

UCLASS()
class CHAOSDEMO_API ACacheDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ACacheDemoActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    TSoftObjectPtr<UChaosCacheCollection> CacheCollection;

    UFUNCTION(BlueprintCallable, Category = "Cache")
    void StartPlayback();

    UFUNCTION(BlueprintCallable, Category = "Cache")
    void StopPlayback();

private:
    UPROPERTY()
    AChaosCacheManager* CachedManager = nullptr;
};
```

**CacheDemoActor.cpp**
```cpp
#include "CacheDemoActor.h"
#include "Chaos/CacheManager.h"
#include "Chaos/CacheCollection.h"
#include "Engine/World.h"

ACacheDemoActor::ACacheDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ACacheDemoActor::StartPlayback()
{
    if (!CacheCollection.IsValid()) return;

    // 在当前位置生成一个 ChaosCacheManager
    FActorSpawnParameters SpawnParams;
    AChaosCacheManager* Manager = GetWorld()->SpawnActor<AChaosCacheManager>(AChaosCacheManager::StaticClass(), GetTransform(), SpawnParams);
    if (Manager)
    {
        Manager->CacheCollection = CacheCollection.LoadSynchronous();
        Manager->Activate();    // 开始回放
        CachedManager = Manager;
    }
}

void ACacheDemoActor::StopPlayback()
{
    if (CachedManager)
    {
        CachedManager->Deactivate();
        CachedManager->Destroy();
        CachedManager = nullptr;
    }
}
```

> 注意：此示例需要 `ChaosCaching` 运行时模块及其依赖。

## 模块依赖

使用 `ChaosCaching` 插件时，你的项目模块需要依赖以下模块（仅列出非标准/独特依赖）：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心模块 |
| `Takes` | 提供 Take Recorder 集成支持（录制系统） |
| `MovieScene` | Sequencer 基础框架 |
| `Sequencer` | 过场动画编辑器 |

其余常见依赖（Core, Engine, Slate 等）已被省略。

## 维护状态

### 近期更新

- 2025-10-03 `7e18bdc` — Chaos cache : restore simulate physics and event flags when deleting the cache actor or when the obs
- 2025-08-06 `c558619a` — Chaos Caching : make creation of chaos cache manager undo-able ( from the Actor > Chaos  menu )
- 2025-08-05 `ee041b71` — Chaos Cache - Add the ability to incrementally create new cache asset each time we are recording
- 2025-08-01 `691dbf0a` — Chaos cache manager : prevent transient component from being added when creating a chaos actor manag
- 2025-08-01 `22b00d1f` — Chaos Cache manager : expose observed component function to blueprint

### 维护评价

该插件目前处于**实验性**阶段（IsExperimentalVersion=true），但在 2025 年 8 月至 10 月期间有多次功能性更新（恢复物理标志、支持增量缓存、撤销操作等），开发活跃。由于插件较新（不足 1 年），可能存在 API 不稳定或缺少完善文档的问题。建议在非生产项目中使用，并关注后续更新。若有稳定版本需求，可考虑等待其转为正式版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching/Tests)（若有）