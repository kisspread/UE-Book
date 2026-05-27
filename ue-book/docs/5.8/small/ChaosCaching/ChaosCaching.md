# Chaos Caching

> Chaos Cache asset support for recording and playing back physics simulations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 物理模拟缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件为 UE5 的 Chaos 物理引擎提供了缓存系统，允许开发者录制物理模拟（如刚体碰撞、破坏、粒子运动）的完整过程，并将其存储为缓存资产。这些缓存可以在运行时精确回放，从而实现以下目标：
1.  **精确重现**：无需再次运行耗时的物理模拟，即可重现特定的、期望的物理效果（如精心设计的建筑倒塌、车辆碰撞）。
2.  **性能优化**：将复杂的物理计算结果烘焙为数据，在运行时以更低的开销进行回放。
3.  **生产流程集成**：与 Sequencer 和 Take Recorder 深度集成，支持在影视制作和过场动画中录制和编辑物理效果。

核心机制是通过一个适配器（`FComponentCacheAdapter`）系统，为不同类型的物理组件（如静态网格体、几何集合）提供统一的录制和回放接口。

## 使用场景

-   **影视与过场动画制作**：在 Sequencer 时间线上精确控制物理破坏或物体运动的时机和效果，用于电影级的实时渲染。
-   **可重复的物理效果**：在开发中调试出满意的破坏效果后，将其录制为缓存，确保每次运行时效果完全一致。
-   **物理调试与测试**：录制一次物理模拟，然后通过缓存播放器反复观察和分析，用于定位问题或验证行为。
-   **游戏中的预计算物理**：对于不需要实时交互但需要复杂物理表现的场景（如场景破坏触发器），预先计算并缓存结果。

## 蓝图用法

蓝图功能主要围绕 `AChaosCacheManager` 和 `AChaosCachePlayer` 这两个 Actor 类展开。`AChaosCachePlayer` 是 `AChaosCacheManager` 的简化版本，专用于播放。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 开始在指定时间点评估缓存（播放或静态姿态）。如果已在评估，则会先停止再重新开始。 | `AChaosCacheManager` |
| `Stop` | 停止缓存的评估。 | `AChaosCacheManager` |
| `TriggerComponent` | 通过物理组件触发其对应的缓存条目开始播放或录制。 | `AChaosCacheManager` |
| `TriggerComponentByCache` | 通过缓存名称触发对应的组件开始播放或录制。 | `AChaosCacheManager` |
| `TriggerAll` | 触发所有已观察组件的播放或录制。 | `AChaosCacheManager` |
| `ResetAllComponentTransforms` | 将所有观察到的组件重置回其缓存录制时的初始世界变换。 | `AChaosCacheManager` |
| `FindOrAddObservedComponent` | 动态查找或向管理器添加一个待观察的物理组件。 | `AChaosCacheManager` |
| `IsRecording` | 查询管理器当前是否处于录制状态。 | `AChaosCacheManager` |

### 使用示例（蓝图描述）

1.  **录制物理效果**：
    *   在场景中放置一个 `AChaosCacheManager` Actor。
    *   在其细节面板中，设置 `CacheMode` 为 `Record`，`StartMode` 为 `Triggered`。
    *   将需要录制的物理组件（如移动的刚体、几何集合）添加到 `ObservedComponents` 数组中。
    *   通过蓝图调用 `TriggerAll` 或 `TriggerComponent` 节点来启动录制。
    *   录制完成后，管理器会自动将数据保存到其关联的 `CacheCollection` 资产中。

2.  **播放缓存**：
    *   使用 `AChaosCachePlayer` Actor，或将 `AChaosCacheManager` 的 `CacheMode` 切换为 `Play`。
    *   指定同一个 `CacheCollection` 资产。
    *   调用 `Start` 节点，传入 `StartTime` 参数来决定从缓存的哪个时间点开始播放。
    *   可以通过 Sequencer 驱动 `StartTime` 属性，实现与动画的同步。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManagerActor.h" // 主要管理类
#include "Chaos/ChaosCache.h"         // 缓存数据类
#include "Chaos/CacheCollection.h"    // 缓存集合资产类
```

### 基本用法

（来自 `ChaosCaching` 模块源码推断的通用模式）

```cpp
// 1. 创建一个缓存管理器实例（通常在游戏逻辑中）
AChaosCacheManager* CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>();

// 2. 设置缓存集合资产
UChaosCacheCollection* MyCollection = LoadObject<UChaosCacheCollection>(nullptr, TEXT("/Game/Path/To/MyCacheCollection"));
CacheManager->SetCacheCollection(MyCollection);

// 3. 设置缓存模式
CacheManager->SetCacheMode(ECacheMode::Play); // 或 ECacheMode::Record

// 4. 动态添加要观察/控制的组件
if (UPrimitiveComponent* TargetComp = FindComponentByClass<UPrimitiveComponent>())
{
    CacheManager->FindOrAddObservedComponent(TargetComp, TEXT("MyComponentCacheName"));
}

// 5. 控制播放/录制
CacheManager->Start(0.0f); // 从头开始
// ... 在 Tick 或其他逻辑中 ...
CacheManager->Stop();
```

### 进阶用法

**实现自定义组件的缓存适配器**：
为新的物理组件类型（如自定义约束）添加缓存支持需要继承 `Chaos::FComponentCacheAdapter`。

```cpp
// 引入适配器基类
#include "Chaos/Adapters/CacheAdapter.h"

class FMyCustomComponentCacheAdapter : public Chaos::FComponentCacheAdapter
{
public:
    // 声明此适配器支持的组件类
    virtual SupportType SupportsComponentClass(UClass* InComponentClass) const override
    {
        if (InComponentClass->IsChildOf<UMyCustomPhysicsComponent>())
        {
            return SupportType::Direct;
        }
        return SupportType::None;
    }

    virtual UClass* GetDesiredClass() const override
    {
        return UMyCustomPhysicsComponent::StaticClass();
    }

    virtual uint8 GetPriority() const override
    {
        return Chaos::FComponentCacheAdapter::UserAdapterPriorityBegin; // 用户适配器优先级
    }

    // 实现录制和回放逻辑（物理线程）
    virtual void Record_PostSolve(UPrimitiveComponent* InComp, const FTransform& InRootTransform, FPendingFrameWrite& OutFrame, Chaos::FReal InTime) const override;
    virtual void Playback_PreSolve(UPrimitiveComponent* InComponent, UChaosCache* InCache, Chaos::FReal InTime, FPlaybackTickRecord& TickRecord, TArray<Chaos::TPBDRigidParticleHandle<Chaos::FReal, 3>*>& OutUpdatedRigids) const override;

    // 其他必要接口实现...
    virtual FGuid GetGuid() const override
    {
        // 必须返回一个稳定且唯一的GUID，它将标识录制的缓存类型
        return FGuid(TEXT("...")); 
    }
    // ...
};

// 在模块启动时注册适配器
void FMyModule::StartupModule()
{
    Chaos::RegisterAdapter(new FMyCustomComponentCacheAdapter());
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何设置一个简单的缓存管理器来播放一个几何集合的缓存。

```cpp
// MyCachePlayerComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyCachePlayerComponent.generated.h"

class AChaosCacheManager;
class UChaosCacheCollection;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyCachePlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyCachePlayerComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    TObjectPtr<UChaosCacheCollection> CacheCollectionAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    float StartTime = 0.0f;

    UFUNCTION(BlueprintCallable, Category = "Cache")
    void PlayCache();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<AChaosCacheManager> CacheManager;
};
```

```cpp
// MyCachePlayerComponent.cpp
#include "MyCachePlayerComponent.h"
#include "Chaos/CacheManagerActor.h"
#include "Chaos/CacheCollection.h"

UMyCachePlayerComponent::UMyCachePlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyCachePlayerComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建缓存管理器（通常作为子Actor）
    UWorld* World = GetOwner()->GetWorld();
    if (World)
    {
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = GetOwner();
        CacheManager = World->SpawnActor<AChaosCacheManager>(AChaosCachePlayer::StaticClass(), SpawnParams);

        if (CacheManager && CacheCollectionAsset)
        {
            CacheManager->SetCacheCollection(CacheCollectionAsset);
            CacheManager->SetCacheMode(ECacheMode::Play);
            // CacheManager 会自动开始播放（如果 bStartOnBeginPlay 为 true）
            // 否则，调用 PlayCache()
        }
    }
}

void UMyCachePlayerComponent::PlayCache()
{
    if (CacheManager)
    {
        CacheManager->Start(StartTime);
    }
}
```

**使用方法**：
1.  将 `UMyCachePlayerComponent` 添加到任何 Actor。
2.  在组件的属性面板中，指定一个已录制好的 `UChaosCacheCollection` 资产。
3.  设置 `StartTime` 控制播放起始点。
4.  在蓝图或C++中调用 `PlayCache()` 开始播放。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PhysicsCore` | Chaos 物理引擎核心类型和接口。 |
| `GeometryCollectionEngine` | 几何集合组件的缓存适配器实现。 |
| `ChaosSolverEngine` | 与 Chaos 物理求解器交互，获取求解器事件。 |
| `Engine` | 引擎核心（通用依赖）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数产生警告的代码。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复了几何集合缓存适配器处理根代理时的逻辑问题。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为混沌事件中继添加了拖尾数据。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | [内容浏览器] 新增物理菜单项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF。 |

### 维护评价

-   **创建时间**：插件创建于 2020 年，已有约 6 年历史。
-   **活跃度**：从提交记录看，最近一次更新在 2026 年 5 月，且提交内容包含功能添加（事件中继）和逻辑修复，表明插件仍在被积极使用和维护，没有废弃迹象。
-   **状态**：尽管名称和路径中包含“Experimental”，但其核心功能稳定，且持续有更新。这表明它可能处于“功能稳定但API未完全固化”的阶段。
-   **推荐使用**：对于需要录制和精确回放复杂Chaos物理模拟（特别是几何集合破坏）的项目，这是一个强大且必要的工具。建议在可控的范围内使用，并注意其实验性标签可能带来的未来API变化风险。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
-   官方文档（无）