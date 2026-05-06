# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（缓存资产、蓝图模板） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

`ChaosCaching` 插件提供了一套完整的流程，用于**录制**和**回放**使用 Chaos 物理引擎驱动的模拟结果。它将每一帧中物理对象的变换、断裂事件、碰撞事件、启用状态等数据存储在 `UChaosCache` 资产中，并能通过 `AChaosCacheManager` 管理器在运行时精确重放。

该插件解决了以下核心问题：

- **确定性回放**：重新模拟物理可能因性能、浮点误差或不确定因素导致结果不一致。通过缓存，可以精确复现之前运行的结果。
- **过场动画集成**：将物理模拟（如爆炸、碎块飞散）作为动画轨道放入 Sequencer，与逻辑、剧情完美对齐。
- **节省性能**：回放时不再运行昂贵的物理求解器，仅读取预先记录的变换数据，大幅降低计算开销。
- **异步/网络同步**：录制的结果可以用于在低配设备或网络上回放相同的物理表现。

## 使用场景

- 你正在制作一个包含破坏系统（如子弹击碎墙体）的射击游戏 → 用 Chaos 物理模拟后录制缓存，然后回放，确保每次视觉效果一致。
- 你需要将一段复杂的物理动画（如绳索、布料）整合到过场动画中，与角色动画同步 → 使用 Sequencer 的 Chaos Cache 轨道。
- 你希望为多个客户端或回放系统保存物理事件（如爆炸时的碎片飞溅）而不必重新模拟 → 录制缓存并网络同步。

## 蓝图用法

插件的主要蓝图接口集中在 `AChaosCacheManager` 及其子类（如 `AChaosCachePlayer`、`AChaosCacheRecorder`）。以下为核心可用节点（从 `CacheManagerActor.h` 提取）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetObservedComponent` | 设置一个被观测的组件及其缓存配置 | `AChaosCacheManager` |
| `ObservedComponents` | 蓝图可读写属性，包含所有被观测的组件列表 | `AChaosCacheManager` |
| `StartPlayback` | 开始回放已录制的缓存数据 | `AChaosCacheManager` |
| `StopPlayback` | 停止回放 | `AChaosCacheManager` |
| `StartRecording` | 开始录制当前物理模拟数据到指定的缓存资产 | `AChaosCacheRecorder` |
| `StopRecording` | 停止录制并保存缓存数据 | `AChaosCacheRecorder` |
| `ActivateObservedComponent` | 按名称激活一个被观测组件（触发式启动） | `AChaosCacheManager` |
| `DeactivateObservedComponent` | 停用一个被观测组件 | `AChaosCacheManager` |
| `GetInterpolationMode` / `SetInterpolationMode` | 获取/设置缓存插值模式（四元数插值、欧拉插值、双四元数插值） | `UChaosCacheCollection` |

### 使用示例（蓝图）

1. **录制一段物理模拟**：
   - 在关卡中放置 `AChaosCacheRecorder` 或自行实现逻辑。
   - 在 `BeginPlay` 中调用 `StartRecording`，指定要录制的组件和缓存资产路径。
   - 物理模拟运行一段时间后，调用 `StopRecording`。

2. **在 Sequencer 中回放缓存**：
   - 创建 `AChaosCachePlayer` 演员，并设置其 `CacheCollection` 属性为一个预先创建的 `UChaosCacheCollection` 资产。
   - 在 Sequencer 中添加该 Actor 的 “Chaos Cache” 轨道，并关联对应的缓存部分。
   - 播放 Sequencer 时，物理变换将按缓存数据复原。

3. **使用 Triggered 模式**：
   - 将 `FObservedComponent` 的 `StartMode` 设为 `Triggered`。
   - 在需要触发时调用 `ActivateObservedComponent`，缓存回放将从此点开始。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManagerActor.h"
#include "Chaos/CacheCollection.h"
#include "Chaos/Adapters/CacheAdapter.h"
```

### 基本用法

```cpp
// 创建一个 ChaosCacheManager 实例
AChaosCacheManager* CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>(AChaosCacheManager::StaticClass());

// 创建一个观察到的组件结构体
FObservedComponent Observed;
Observed.CacheName = FName(TEXT("MyExplosionCache"));
Observed.Component = MyStaticMeshComponent; // UPrimitiveComponent*
Observed.bIsSimulating = true;
Observed.bPlaybackEnabled = true;

// 设置组件到管理器
CacheManager->SetObservedComponent(Observed);

// 开始录制
ICacheRecording* Recorder = Cast<ICacheRecording>(CacheManager);
if (Recorder)
{
    Recorder->StartRecording();
}

// 在适当的时候停止
Recorder->StopRecording();

// 切换到播放模式
CacheManager->PlaybackAll();
```

### 进阶用法

创建和配置 CacheCollection 资产：

```cpp
// 创建一个 Chaos Cache Collection 资产
UChaosCacheCollection* Collection = NewObject<UChaosCacheCollection>(GetTransientPackage(), NAME_None, RF_Transactional);

// 添加一个空白缓存槽
UChaosCache* Cache = Collection->FindOrAddCache(TEXT("Explosion1"));

// 设置插值模式
Collection->SetInterpolationMode(EChaosCacheInterpolationMode::DualQuatInterp);

// 保存为资产（编辑器环境下）
UPackage* Package = CreatePackage(TEXT("/Game/Caches/MyCollection"));
Collection = NewObject<UChaosCacheCollection>(Package, UChaosCacheCollection::StaticClass(), FName(TEXT("MyCollection")), RF_Public | RF_Standalone);
// ... 填充数据后
UPackage::SavePackage(Package, nullptr, RF_Public, *Package->GetName());
```

## Demo 示例

以下是一个最小化示例，展示如何通过 C++ 创建和管理一个 Chaos Cache 管理器，并录制 5 秒后停止。

**MyCacheDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCacheDemo.generated.h"

UCLASS()
class AMyCacheDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    class AChaosCacheManager* CacheManager;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    float RecordDuration = 5.0f;

    float RecordTimer = 0.0f;
    bool bIsRecording = false;
};
```

**MyCacheDemo.cpp**

```cpp
#include "MyCacheDemo.h"
#include "Chaos/CacheManagerActor.h"
#include "Chaos/CacheCollection.h"

void AMyCacheDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!CacheManager)
    {
        CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>(AChaosCacheManager::StaticClass());
        FTransform SpawnTransform;
        SpawnTransform.SetLocation(GetActorLocation());
        CacheManager->SetActorTransform(SpawnTransform);
    }

    // 假设有一个静态网格体组件附加在演示 Actor 上
    UPrimitiveComponent* Comp = FindComponentByClass<UPrimitiveComponent>();
    if (Comp)
    {
        FObservedComponent Observed;
        Observed.CacheName = TEXT("DemoCache");
        Observed.Component = Comp;
        CacheManager->SetObservedComponent(Observed);
    }

    CacheManager->StartRecordingAll();
    bIsRecording = true;
    RecordTimer = 0.0f;
}

void AMyCacheDemo::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (bIsRecording)
    {
        RecordTimer += DeltaSeconds;
        if (RecordTimer >= RecordDuration)
        {
            CacheManager->StopRecordingAll();
            bIsRecording = false;
            UE_LOG(LogTemp, Log, TEXT("Recording stopped after %.1f seconds"), RecordTimer);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Takes` (插件) | 录制时管理片段（取景），与缓存录制流程集成 |
| `Chaos` | 核心物理引擎，提供求解器、粒子句柄等底层支持 |
| `MovieScene` | Sequencer 轨道实现，支持缓存回放作为过场动画 |

其余依赖均为标准引擎模块（Core、Engine、CoreUObject等），此处省略。

## 维护状态

### 近期更新

- 2025-10-03 7e18bdc — Chaos cache : restore simulate physics and event flags when deleting the cache actor or when the observed component is deactivated
- 2025-08-06 c558619 — Chaos Caching : make creation of chaos cache manager undo-able ( from the Actor > Chaos menu )
- 2025-08-05 ee041b7 — Chaos Cache - Add the ability to incrementally create new cache asset each time we are recording
- 2025-08-01 691dbf0 — Chaos cache manager : prevent transient component from being added when creating a chaos actor manager
- 2025-08-01 22b00d1 — Chaos Cache manager : expose observed component function to blueprint

### 维护评价

该插件处于**早期开发阶段**（实验性），但更新频率非常高，基本每几天就有新功能修补。它是为 UE5.4+ 引入的新特性，旨在取代旧版物理缓存系统（如 `MovieSceneAnimation` 或自定义方案）。虽然标记为实验性，但其代码结构清晰，适配器模式易于扩展，且已经提供了对静态网格体、集合体（Geometry Collection）和骨骼网格体的缓存支持。推荐在非生产项目或垂直切片中使用，以验证其稳定性。由于还处于实验阶段，API 可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/chaos-cache/)（UE5.4 以上版本）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching/Tests)（若存在）