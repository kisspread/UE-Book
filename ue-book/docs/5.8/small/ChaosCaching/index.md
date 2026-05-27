# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，Chaos物理资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件旨在为 Unreal Engine 5 的 Chaos 物理系统提供**模拟结果录制与回放**功能。它解决的核心问题是：物理模拟（如布料、破碎、粒子等）在实时运行时具有随机性且计算成本高。通过将物理模拟的关键数据（如物体位置、速度、变形状态）录制到“缓存资产”（Chaos Cache）中，可以在后续精确地回放该模拟结果，从而实现：

1. **确定性回放**：在多人游戏或过场动画中，确保物理事件（如爆炸、建筑倒塌）在不同设备上表现完全一致。
2. **性能优化**：预先录制复杂的物理模拟，在运行时直接播放缓存，避免实时计算的性能开销。
3. **迭代创作**：允许美术和设计师反复观看、调整物理模拟效果，无需等待漫长的实时模拟计算。

它与 Unreal 的 **Sequencer** 和 **Take Recorder** 系统深度集成，使录制和回放过程能够与游戏的时间轴、镜头切换和后期处理无缝协同。

## 使用场景

- 你在制作一个需要展示大规模建筑倒塌的电影化过场动画 → 使用 ChaosCaching 录制 Chaos 破碎模拟，然后在 Sequencer 中精确控制回放时间。
- 你的游戏包含一个可破坏的环境，但希望所有玩家看到相同的破坏序列以保持游戏公平性 → 预先录制破坏模拟，在多人游戏中同步播放。
- 你正在开发一个物理驱动的解谜游戏，需要确保谜题的物理反馈每次都相同 → 录制并缓存关键物理交互的结果。
- 你需要优化移动端游戏的性能，但保留 PC 端的复杂物理效果 → 在 PC 上录制高质量模拟，将缓存资产用于移动端回放。

## 蓝图用法

本插件的核心功能主要通过 **编辑器工具** 和 **资产类型** 提供，蓝图运行时节点较少。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `Chaos Cache` | 核心资产，存储录制的物理模拟数据。在内容浏览器中创建。 |

### 核心编辑器功能

插件主要在 **编辑器** 中操作，通常不通过蓝图节点直接调用。

1. **录制**：通过 Sequencer 的录制功能（“录制”按钮）或 Take Recorder 将场景中的物理模拟捕获到 Chaos Cache 资产。
2. **回放**：在 Sequencer 轨道上添加 Chaos Cache 轨道，将缓存资产拖入，即可控制回放。
3. **预览**：在编辑器视窗中实时预览缓存的回放效果。

### 使用示例（蓝图描述）

虽然不常用，但可以在蓝图中通过 `UChaosCacheComponent` 控制回放：

1. 从一个拥有 `UChaosCacheComponent` 的 Actor 开始。
2. 在 `BeginPlay` 时，使用 `Set Cache` 节点并指定一个 Chaos Cache 资产。
3. 使用 `Play` 节点开始回放，`Stop` 节点停止。
4. 可通过 `Set Play Rate` 调整回放速度。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/ChaosCache.h"
#include "Components/ChaosCacheComponent.h"
#include "Chaos/CacheEvents.h"
```

### 基本用法

在 C++ 中，主要通过 `UChaosCacheComponent` 来管理缓存的播放。
```cpp
// 在某个 Actor 的头文件中
UPROPERTY(VisibleAnywhere)
UChaosCacheComponent* CacheComponent;

// 在 BeginPlay 中初始化并播放缓存
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    if (CacheComponent && ChaosCacheAsset)
    {
        CacheComponent->SetCache(ChaosCacheAsset);
        CacheComponent->Play();
    }
}
```
*(示例基于常见 Chaos 物理组件使用模式)*

### 进阶用法

插件提供了缓存事件（`FChaosCacheEvent`）系统，允许在回放特定时间点触发自定义逻辑。
```cpp
// 监听缓存事件
void AMyActor::BindToCacheEvents(UChaosCacheComponent* InComponent)
{
    if (InComponent)
    {
        InComponent->OnCacheEvent.AddDynamic(this, &AMyActor::HandleCacheEvent);
    }
}

void AMyActor::HandleCacheEvent(const FChaosCacheEvent& Event)
{
    if (Event.EventType == EChaosCacheEventType::Fragmented)
    {
        // 处理破碎事件，例如播放声音
    }
}
```
*(示例基于插件事件结构推断)*

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中设置并播放 Chaos 缓存。

**MyCachingActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCachingActor.generated.h"

class UChaosCacheComponent;
class UChaosCache;

UCLASS()
class AMyCachingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCachingActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Caching")
    UChaosCacheComponent* CacheComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Caching")
    UChaosCache* CacheAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Caching")
    float PlayRate = 1.0f;
};
```

**MyCachingActor.cpp**
```cpp
#include "MyCachingActor.h"
#include "Components/ChaosCacheComponent.h"
#include "Chaos/ChaosCache.h"

AMyCachingActor::AMyCachingActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建缓存组件
    CacheComponent = CreateDefaultSubobject<UChaosCacheComponent>(TEXT("ChaosCache"));
    RootComponent = CacheComponent;
}

void AMyCachingActor::BeginPlay()
{
    Super::BeginPlay();

    if (CacheComponent && CacheAsset)
    {
        // 设置要播放的缓存资产
        CacheComponent->SetCache(CacheAsset);
        // 设置播放速率
        CacheComponent->SetPlayRate(PlayRate);
        // 开始播放
        CacheComponent->Play();
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。插件自身依赖 `Takes` 插件，但使用者无需直接处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何体集合缓存适配器处理根代理时的逻辑问题。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为混沌事件中继添加尾部数据。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | [内容浏览器] 新增“添加”菜单中的“物理”分类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF。 |

### 维护评价

**活跃维护中**。该插件在 2026 年 5 月仍有功能性更新（如修复根代理逻辑、优化事件数据），表明 Epic Games 持续维护此插件以确保其与最新 Chaos 物理系统兼容。作为实验性插件，它尚未标记为稳定（Stable）或默认启用，这意味着其 API 和功能在未来版本中可能发生不兼容的更改。对于需要确定性物理回放或高级物理模拟录制的工作流，推荐在了解其风险的前提下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [官方文档]() （.uplugin 中 DocsURL 为空，暂无官方文档链接）
- [测试用例]() （根据文件结构，测试用例可能集成在引擎测试中，不在插件目录内）