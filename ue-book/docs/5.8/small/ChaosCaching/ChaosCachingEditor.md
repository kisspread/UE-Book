# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 物理缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（缓存资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件的核心功能是**录制并回放 Chaos 物理模拟**。它允许开发者将复杂的、实时计算的物理效果（如刚体碰撞、破碎、布料等）序列化到缓存资产中，并在需要时（如过场动画、游戏玩法）精确回放，从而：
1.  **离线预计算**：将耗时的物理模拟从实时运行时转移到编辑器或离线阶段进行预计算，确保最终效果符合预期且性能可控。
2.  **确定性回放**：为过场动画、游戏玩法事件提供确定性的物理表现，避免每次运行的随机性。
3.  **与 Sequencer 集成**：提供时间轴（Track）支持，便于在 Sequencer 中对物理缓存进行精确的剪辑、混合和同步。

## 使用场景

- 你正在制作一个包含大量物体碰撞、破坏的过场动画，希望确保每次播放效果一致 → 使用 ChaosCaching 录制并回放。
- 你的游戏中有一个基于物理的玩法机制（如保龄球），需要固定结果用于教学或测试 → 缓存并回放该次物理模拟。
- 你需要在编辑器中多次调试物理参数，并对比不同参数下的最终效果 → 缓存不同版本的模拟结果进行对比。
- 你希望将复杂的物理特效序列化，以便在资源有限的设备上播放预计算的结果。

## 蓝图用法

插件主要通过 `AChaosCacheManager` Actor 类在蓝图中暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Cache Mode` | 设置缓存管理器的工作模式（录制、回放、空闲等）。 | `AChaosCacheManager` |
| `Start Recording` | 开始录制指定的物理组件。 | `AChaosCacheManager` |
| `Stop Recording` | 停止录制，并将录制的数据保存到缓存资产中。 | `AChaosCacheManager` |
| `Start Playback` | 开始回放缓存中录制的物理动画。 | `AChaosCacheManager` |
| `Set Playback Time` | 在回放过程中，设置特定的时间点。 | `AChaosCacheManager` |
| `Set Playback Speed` | 设置回放的速度。 | `AChaosCacheManager` |

### 使用示例（蓝图描述）

1.  在关卡中放置一个 `AChaosCacheManager` Actor。
2.  在蓝图中，通过“Get Actor of Class”节点获取该 Actor 的引用。
3.  调用 `Set Cache Mode` 节点，将其设置为 `Record`。
4.  指定要录制的物理组件（如一个可破坏的静态网格体）。
5.  调用 `Start Recording` 开始录制。触发物理模拟（如生成一个冲击力）。
6.  模拟结束后，调用 `Stop Recording`。
7.  将模式切换为 `Playback`，然后调用 `Start Playback` 即可观看回放。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManager.h"
#include "Chaos/ChaosCacheCollection.h"
```

### 基本用法

以下代码演示如何创建一个缓存管理器并控制其录制过程。

```cpp
// 假设您已在场景中获取了一个 AChaosCacheManager* 指针，名为 CacheManager
// 假设您有一个要录制的 UPrimitiveComponent* 指针，名为 PhysicsComponent

// 1. 创建一个缓存集合资产
UChaosCacheCollection* CacheCollection = NewObject<UChaosCacheCollection>(GetTransientPackage(), TEXT("MyCacheCollection"));

// 2. 将缓存集合设置给管理器
CacheManager->SetCacheCollection(CacheCollection);

// 3. 设置缓存模式为录制模式
CacheManager->SetCacheMode(ECacheMode::Record);

// 4. 指定要录制的组件（可以添加多个）
CacheManager->AddObservedComponent(PhysicsComponent);

// 5. 开始录制
CacheManager->StartRecording();

// ... 此处可以触发物理模拟（如施加力）...

// 6. 停止录制
CacheManager->StopRecording();
```

### 进阶用法

录制完成后，切换到回放模式并精确控制。

```cpp
// 假设已经完成了上述录制步骤

// 1. 停止录制后，管理器会自动完成数据的序列化。
// 2. 将模式切换为回放
CacheManager->SetCacheMode(ECacheMode::Play);

// 3. 开始回放
CacheManager->StartPlayback();

// 4. 动态控制回放（例如在 Tick 中）
// 每帧更新回放状态
void AMyActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (CacheManager && CacheManager->GetCacheMode() == ECacheMode::Play)
    {
        // 可以在此处设置回放速度
        CacheManager->SetPlaybackSpeed(1.5f); // 1.5倍速回放
    }
}
```

## Demo 示例

一个最小的 Actor 示例，演示如何使用 ChaosCaching 录制并回放一个立方体的自由落体。

```cpp
// ChaosCacheDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ChaosCacheDemoActor.generated.h"

class AChaosCacheManager;
class UChaosCacheCollection;
class UStaticMeshComponent;

UCLASS()
class AChaosCacheDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosCacheDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComponent;

    UPROPERTY(VisibleAnywhere)
    AChaosCacheManager* CacheManager;

    UPROPERTY()
    UChaosCacheCollection* CacheCollection;

    // 用于控制状态的计时器
    float RecordTimer;
    bool bIsRecording;
    bool bIsPlaying;
};
```

```cpp
// ChaosCacheDemoActor.cpp
#include "ChaosCacheDemoActor.h"
#include "Chaos/CacheManager.h"
#include "Chaos/ChaosCacheCollection.h"
#include "Components/StaticMeshComponent.h"

AChaosCacheDemoActor::AChaosCacheDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;

    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
    MeshComponent->SetSimulatePhysics(true); // 启用物理模拟

    CacheManager = nullptr;
    CacheCollection = nullptr;
    RecordTimer = 0.f;
    bIsRecording = false;
    bIsPlaying = false;
}

void AChaosCacheDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建并配置缓存管理器 (通常可以通过编辑器放置)
    CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>();
    CacheCollection = NewObject<UChaosCacheCollection>(GetTransientPackage(), TEXT("DemoCacheCollection"));

    CacheManager->SetCacheCollection(CacheCollection);
    CacheManager->AddObservedComponent(MeshComponent);

    // 开始录制
    CacheManager->SetCacheMode(ECacheMode::Record);
    CacheManager->StartRecording();
    bIsRecording = true;
}

void AChaosCacheDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bIsRecording)
    {
        RecordTimer += DeltaTime;
        // 录制 2 秒后停止
        if (RecordTimer >= 2.0f)
        {
            CacheManager->StopRecording();
            CacheManager->SetCacheMode(ECacheMode::Play);
            bIsRecording = false;

            // 稍微延迟后开始回放
            FTimerHandle TimerHandle;
            GetWorldTimerManager().SetTimer(TimerHandle, [this]()
            {
                CacheManager->StartPlayback();
                bIsPlaying = true;
            }, 0.5f, false);
        }
    }
}
```

## 模块依赖

从插件描述和功能推断，其独特依赖如下（标准 Core/Engine 模块已省略）：

| 模块 | 用途 |
|---|---|
| `Takes` | 与 Sequencer 录制系统（Take Recorder）深度集成，用于将物理缓存作为录制源。 |
| `Chaos` | Chaos 物理引擎核心，提供底层物理模拟和缓存数据格式。 |
| `GeometryCollectionEngine` | 支持几何体集合（GeometryCollection）的破碎效果缓存。 |
| `LevelSequence`, `MovieScene` | Sequencer 相关模块，用于实现物理缓存的轨道编辑器和时间轴支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量强制转换为浮点数时产生的编译器警告。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复了几何体集合缓存适配器在处理根代理时的逻辑问题。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为 Chaos 事件中继添加了尾部数据支持。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 为内容浏览器新建菜单添加了“物理”分类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |

### 维护评价

**活跃维护中，但需注意其“实验性”状态。**
- **年龄与更新**：插件创建于2020年，但近一个月（2026年5月）内有多次针对底层逻辑和编译警告的修复，表明 Epic 内部仍在使用和维护。
- **功能完善度**：与 Sequencer、Take Recorder 的集成相当深入，提供了完整的编辑器工作流，不属于半成品。
- **主要风险**：`.uplugin` 标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着其 API 和功能在未来的引擎版本中可能会发生**破坏性更改或被移除**。
- **推荐**：适用于**原型开发、内部工具或对最新引擎版本跟进迅速的项目**。在准备进入正式发行阶段的项目中使用需谨慎，并做好应对 API 变更的准备。建议密切关注其状态更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- 官方文档：暂无公开链接。