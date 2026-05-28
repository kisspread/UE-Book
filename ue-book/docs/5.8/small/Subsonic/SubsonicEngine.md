# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 亚音速音频编排系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个高级音频编排和播放系统。它不同于简单的音效播放，其核心在于提供一种数据驱动的、可组合的方式来管理和触发复杂的音频事件序列。插件通过“事件集合”（`USubsonicEventCollection`）来定义一组音频事件（如播放、停止、修改参数）和它们之间的逻辑关系，然后通过“执行器”（`USubsonicEventCollectionExecutor`）在游戏运行时实例化并执行这些事件。它解决了以下问题：
1.  **复杂音效序列的编排**：可以将多个播放、停止、延迟、参数修改等动作组合成一个逻辑单元，方便管理。
2.  **音频资源的生命周期管理**：通过可寻址的“名称”和“作用域”（执行器或全局）来管理音频组件（`UAudioComponent`）或波形生成器源（`GeneratorSource`）的复用、创建和销毁。
3.  **音频参数的统一控制**：支持为音频源设置音量、音高、滤波器等内置参数，以及将参数转发到 MetaSound 生成器。
4.  **高级音频回放**：提供了“GeneratorSource”播放路径，支持在音频渲染线程上进行实时波形播放和DSP处理（音量、音高、滤波器），并与MetaSound系统集成。

简而言之，当你需要为游戏创建复杂、可控且可复用的音频交互（而不仅仅是播放一个音效）时，Subsonic 提供了基础架构。

## 使用场景

- 你正在制作一个剧情驱动的游戏，需要在过场动画中精确同步和控制一系列对话、环境音和背景音乐的播放、淡入淡出和参数变化。使用 Subsonic 可以将这些音频操作编排到一个“事件集合”中，通过单个“执行事件”节点按顺序触发。
- 你的游戏有一个动态音效系统，例如不同材质的脚步声。你可以创建一个事件集合，根据传入的标签（如“脚步_草地”、“脚步_金属”）来播放对应的声音，并立即应用不同的衰减和调制设置。
- 你需要一个管理复杂音频组件池的系统，例如场景中有多个可交互的收音机。使用 Subsonic 可以通过名称（如 “Radio_01”）来查找、创建或复用这些音频组件，避免手动管理对象的繁琐和内存泄漏风险。
- 你希望利用 MetaSound 的强大功能，但需要更高级的生命周期和参数控制，例如在播放 MetaSound 的同时控制其淡出，并在淡出结束后触发另一个游戏事件。

## 蓝图用法

Subsonic 的蓝图接口主要围绕创建和执行事件集合。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 从事件集合资产创建一个新的执行器实例。 | `USubsonicSubsystem` |
| `Execute Event` | 在执行器上触发一个指定的游戏标签（GameplayTag）事件。 | `USubsonicEventCollectionExecutor` |

### 使用示例（蓝图描述）

1.  **准备资产**：首先在编辑器中，右键创建“Subsonic Event Collection”资产。在该资产的细节面板中，你可以通过“事件”数组来定义事件，每个事件由一个游戏标签（如 `GameplayTag = “Event.Cue.BattleStart”`）和一系列“动作”（Actions）组成。动作类型包括“播放声音”、“停止声音”、“延迟事件”、“修改音频组件”等。
2.  **创建执行器**：在任何 Actor 的蓝图中，从 `Get Subsonic Subsystem` 节点拖出引线，调用 `Create Executor` 节点。将你准备好的事件集合作为 `Collection` 输入，并为执行器起一个名字（如 `BattleMusicExecutor`）。
3.  **触发事件**：当需要播放战斗音乐时，从上一步创建的执行器对象引出，调用 `Execute Event` 节点。将事件标签设置为 `Event.Cue.BattleStart`。这个节点会根据你在事件集合资产中定义的配置，自动执行相应的播放、延迟等动作。
4.  **管理音频组件**：如果在事件集合中使用了“Modify Audio Component”动作，你需要为其提供一个“名称”（如 `BattleAmbience`）和“作用域”（执行器或全局）。系统会根据作用域自动创建或查找对应的 `UAudioComponent` 实例。你可以在后续事件中通过相同的名称来停止或修改它。

## C++ 用法

核心API位于 `SubsonicEngine` 模块，主要涉及子系统、事件集合和执行器。

### 头文件引入

```cpp
#include “SubsonicSubsystem.h”
#include “SubsonicEventCollectionObjects.h”
```

### 基本用法

获取子系统并创建执行器，然后触发事件。这是最基础的交互方式。

```cpp
// 假设在某个 AActor 的成员函数中
void AMyActor::StartBattleMusic()
{
    // 1. 获取 Subsonic 引擎子系统
    USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
    if (!SubsonicSubsystem)
    {
        return;
    }

    // 2. 创建事件集合执行器
    // ‘BattleMusicCollection’ 是在编辑器中创建的 USubsonicEventCollection 资产引用
    USubsonicEventCollectionExecutor* Executor = SubsonicSubsystem->CreateExecutorBP(
        this, 
        FName(“BattleMusicExecutor”), 
        BattleMusicCollection
    );

    if (!Executor || !Executor->IsValid())
    {
        return;
    }

    // 3. 通过游戏标签触发一个事件
    // 假设在事件集合中定义了标签为 “Event.Cue.BattleStart” 的事件
    ESubsonicExecutionResult Result;
    Executor->ExecuteEvent(FGameplayTag::RequestGameplayTag(FName(“Event.Cue.BattleStart”)), Result);

    if (Result == ESubsonicExecutionResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT(“Battle music started successfully.”));
    }

    // 4. （可选）在不再需要时，取消注册执行器以释放资源
    // Executor->Unregister();
}
```

### 进阶用法

从源码分析，更复杂的用法涉及直接操作底层的 `FSubsonicExecutor` 和订阅器系统。然而，插件目前主要提供蓝图接口。C++ 进阶用法可能包括：
*   **自定义事件动作**：通过继承 `FSubsonicEventActionBase` 并实现 `Execute` 方法，来创建全新的音频动作类型。
*   **自定义参数存储**：直接使用 `FSubsonicParameterStore` 来更精细地控制传递给 `GeneratorSource` 或音频组件的参数。
*   **与音频线程交互**：通过 `FSubsonicRelay` 和 `FSubsonicGenerator`，理解其跨线程通信机制，用于深度集成或调试。

## Demo 示例

一个最小化的、可编译的 C++ 示例，展示如何通过代码创建并使用 Subsonic。

**MyAudioManager.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “GameplayTagContainer.h”
#include “MyAudioManager.generated.h”

class USubsonicEventCollection;
class USubsonicEventCollectionExecutor;

UCLASS()
class MYPROJECT_API AMyAudioManager : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioManager();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void TriggerAudioEvent(FGameplayTag EventTag);

private:
    // 在编辑器中指定的事件集合资产
    UPROPERTY(EditAnywhere, Category = “Audio”)
    TObjectPtr<USubsonicEventCollection> EventCollection;

    // 运行时创建的执行器实例
    UPROPERTY(Transient)
    TObjectPtr<USubsonicEventCollectionExecutor> EventExecutor;

    UPROPERTY(EditAnywhere, Category = “Audio”)
    FName ExecutorName = “MainExecutor”;
};
```

**MyAudioManager.cpp**
```cpp
#include “MyAudioManager.h”
#include “SubsonicSubsystem.h”
#include “SubsonicEventCollectionObjects.h”

AMyAudioManager::AMyAudioManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAudioManager::BeginPlay()
{
    Super::BeginPlay();

    // 确保有事件集合资产
    if (!EventCollection)
    {
        UE_LOG(LogTemp, Warning, TEXT(“AMyAudioManager: EventCollection asset is not set.”));
        return;
    }

    // 获取子系统并创建执行器
    USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem)
    {
        EventExecutor = SubsonicSubsystem->CreateExecutorBP(this, ExecutorName, EventCollection);
        if (!EventExecutor || !EventExecutor->IsValid())
        {
            UE_LOG(LogTemp, Error, TEXT(“AMyAudioManager: Failed to create Subsonic Executor.”));
        }
    }
}

void AMyAudioManager::TriggerAudioEvent(FGameplayTag EventTag)
{
    if (!EventExecutor || !EventExecutor->IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT(“AMyAudioManager: Executor is not valid.”));
        return;
    }

    ESubsonicExecutionResult Result;
    EventExecutor->ExecuteEvent(EventTag, Result);

    if (Result != ESubsonicExecutionResult::Succeeded)
    {
        UE_LOG(LogTemp, Warning, TEXT(“AMyAudioManager: Event ‘%s’ failed to execute.”), *EventTag.ToString());
    }
}
```

## 模块依赖

要使用 Subsonic 的 `SubsonicEngine` 模块，你的模块 `Build.cs` 需要添加以下依赖。

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 插件广泛使用 `FGameplayTag` 来标识和触发事件，这是核心依赖。 |
| `MetasoundEngine` | 用于与 MetaSound 生成器集成，处理 `UMetaSoundSource` 相关逻辑。 |
| `AudioMixer` | 用于访问 `FMixerDevice` 和 `IAudioMixerGeneratorSource`，是 `GeneratorSource` 回放路径的基础。 |

（注：常见依赖如 `Core`, `CoreUObject`, `Engine`, `AudioMixerCore` 等已省略）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了一个错误的合并，恢复了被意外覆盖的订阅器代码，并应用了最小的非废弃化修改。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或消除了 PVS（可能的代码缺陷）静态分析警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中增加了音频相关的分类菜单（可能是编辑器集成）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将部分 `UE_LOG` 宏迁移为新的 `UE_LOGF` 格式。 |

### 维护评价

Subsonic 是一个于 **2026年初创建的较新插件**，目前处于 **实验性阶段**（`IsExperimentalVersion=true`）。从 Git 历史看，它在 **2026年5月** 近期仍有活动，主要集中在**编译错误修复、合并冲突解决和代码质量改进**上，而非功能迭代。这表明它目前处于一种**基础架构稳固但功能可能不完整**的状态。

作为 Epic Games 官方维护的实验性插件，它有持续更新的潜力，但 API 和行为**可能在未来版本中发生变化**，不适合直接用于追求稳定性的生产环境。建议用于**原型开发、内部工具或对音频系统有深度定制需求且愿意承担维护风险的场景**。对于核心游戏功能，应优先考虑成熟的解决方案或等待该插件转为正式支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)