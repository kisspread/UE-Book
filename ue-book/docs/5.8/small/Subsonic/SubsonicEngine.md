# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 亚音速音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一套面向数据驱动的音频逻辑管理系统。它解决的核心问题是：如何将复杂的音频播放逻辑（如状态切换、事件触发、参数变化、淡入淡出、序列播放）从硬编码的 C++ 或松散的蓝图逻辑中剥离出来，转化为设计师可编辑、可复用的资产。

传统的音频实现（如 AudioComponent、MetaSound）更侧重于单个声音的播放与 DSP 处理。Subsonic 则在更高维度上组织这些声音的“行为”和“流程”。它允许开发者将音频逻辑定义为一系列可配置的“事件集合”（Event Collection）和“动作”（Action），然后通过“执行器”（Executor）来驱动，从而实现对音频系统行为的集中化、可视化管理。

简单来说，如果你想构建一个类似于音乐播放器（包含播放、暂停、切换歌曲、淡入淡出、音量调节）或复杂音效序列系统（例如技能施放、环境氛围切换）的音频逻辑，Subsonic 提供了一套规范化的框架来替代临时的、基于代码的解决方案。

## 使用场景

- **复杂音乐管理系统**：你的游戏需要根据场景、战斗状态、玩家进度无缝切换和混合多段背景音乐，包含淡入淡出、音量分层、情绪过渡。
- **数据驱动的音效序列**：某个技能或机关需要触发一系列按特定顺序、有时序延迟或条件分支的音效（如：蓄力音效 → 释放音效 → 爆炸音效 → 环境回响）。
- **MetaSound 的高级控制层**：你使用 MetaSound 创作了复杂的合成器音效，但需要通过游戏逻辑（如“进入水下”）来批量调整多个参数（音量、滤波器、混响）。
- **音频逻辑的复用与维护**：团队中存在多个需要相似音频逻辑模式（如“循环播放直到被打断”）的角色或物体，你希望将这些逻辑封装成资产，避免重复代码。

## 蓝图用法

Subsonic 的核心蓝图交互围绕 `USubsonicSubsystem`、`USubsonicEventCollection` 和 `USubsonicEventCollectionExecutor` 展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 创建一个与指定事件集合绑定的执行器实例。这是与 Subsonic 系统交互的主要入口。 | `USubsonicSubsystem` |
| `Execute Event` | 在执行器上触发一个 GameplayTag 标识的事件，驱动事件集合中的对应动作链。 | `USubsonicEventCollectionExecutor` |

### 使用示例（蓝图描述）

1.  **创建事件集合资产**：在内容浏览器中右键创建 `SubsonicEventCollection` 资产。
2.  **编辑事件集合**：打开该资产，在其定义中配置“事件”（如 “Music.Intro”, “Music.Loop”）和关联的“动作”（Action）。例如，为 “Music.Intro” 事件配置一个 “播放声音（GeneratorSource）” 动作，并设置要播放的 `SoundWave`。
3.  **蓝图中创建执行器**：在角色的蓝图中，通过 `Get Subsystem` 节点获取 `USubsonicSubsystem`，然后调用 `Create Executor` 节点，传入世界上下文对象、一个名称标识和你创建的事件集合资产。将返回的 Executor 对象保存为变量。
4.  **蓝图中触发事件**：在需要播放音乐的地方（如 `BeginPlay`），调用保存的 Executor 变量的 `Execute Event` 节点，输入事件 Tag（如 “Music.Intro”）。系统将根据你在事件集合资产中配置的逻辑，自动处理声音的播放、组件的创建和参数应用。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicEventCollectionObjects.h" // 核心对象
#include "SubsonicSubsystem.h"             // 子系统
```

### 基本用法

以下代码演示了如何在 C++ 中以编程方式创建和使用 Subsonic 系统。

**来源文件**：`Engine/Tests/AudioTests/Private/Subsonic/SubsonicEngineTest.cpp`

```cpp
// 1. 创建事件集合定义，并注册一个“播放声音”动作
UE::Subsonic::Core::FSubsonicEventCollectionDefinition CollectionDef;
UE::Subsonic::FSubsonicEventAction_GeneratorSourcePlay PlayAction;
PlayAction.Name = TEXT("PrimarySource");
PlayAction.Sound = MySoundWaveAsset; // 一个 USoundWave 指针
PlayAction.Scope = UE::Subsonic::ESubsonicExecutionScope::Executor;

// 将动作附加到名为 “PlaySound” 的事件上
CollectionDef.Events.Add(TEXT("PlaySound"), {MakeShared<FSubsonicEventAction_GeneratorSourcePlay>(PlayAction)});

// 2. 将定义应用到 USubsonicEventCollection 对象
USubsonicEventCollection* EventCollection = NewObject<USubsonicEventCollection>();
EventCollection->SetDefinition(MoveTemp(CollectionDef));

// 3. 获取子系统并创建执行器
USubsonicSubsystem* Subsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
USubsonicEventCollectionExecutor* Executor = Subsystem->CreateExecutorBP(
    GetWorld(), TEXT("MyExecutor"), EventCollection, FAudioDeviceManager::Get()->GetMainAudioDeviceId());

// 4. 触发事件
FGameplayTag PlayTag = FGameplayTag::RequestGameplayTag(TEXT("Subsonic.PlaySound"));
ESubsonicExecutionResult Result;
Executor->ExecuteEvent(PlayTag, Result);

if (Result == ESubsonicExecutionResult::Succeeded)
{
    UE_LOG(LogTemp, Log, TEXT("Subsonic event executed successfully."));
}
```

### 进阶用法

**来源文件**：`Engine/Tests/AudioTests/Private/Subsonic/SubsonicEngineTest.cpp`

```cpp
// 使用参数存储来动态控制生成器
FSubsonicParameterStore ParamStore;
// 设置音量 (dB)
ParamStore.Parameters.AddFloat(TEXT("Volume"), -6.0f);
// 设置音高偏移 (半音)
ParamStore.Parameters.AddFloat(TEXT("PitchShift"), 2.0f);

// 在播放动作中应用参数
FSubsonicEventAction_GeneratorSourcePlay PlayWithParams;
PlayWithParams.Name = TEXT("DynamicSource");
PlayWithParams.Sound = MySoundWave;
PlayWithParams.Parameters = ParamStore;

// ... 后续注册和执行同上
```

**来源文件**：`Engine/Tests/AudioTests/Private/Subsonic/SubsonicEngineTest.cpp`

```cpp
// 使用音频组件动作
FSubsonicEventAction_AudioComponentPlay AudioCompPlayAction;
AudioCompPlayAction.Name = TEXT("MyComponent");
AudioCompPlayAction.Sound = SomeSoundBase;
AudioCompPlayAction.Scope = UE::Subsonic::ESubsonicExecutionScope::Executor;
AudioCompPlayAction.Access = UE::Subsonic::ESubsonicAudioComponentAccess::FindOrAdd;

FSubsonicEventAction_AudioComponentStop AudioCompStopAction;
AudioCompStopAction.Name = TEXT("MyComponent");
AudioCompStopAction.Scope = UE::Subsonic::ESubsonicExecutionScope::Executor;

// 将播放和停止动作注册到不同的事件
CollectionDef.Events.Add(TEXT("PlayAudio"), {MakeShared<FSubsonicEventAction_AudioComponentPlay>(AudioCompPlayAction)});
CollectionDef.Events.Add(TEXT("StopAudio"), {MakeShared<FSubsonicEventAction_AudioComponentStop>(AudioCompStopAction)});
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示了如何创建一个简单的 “播放并延迟停止” 的音频逻辑。

**SubsonicDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameplayTagContainer.h"
#include "SubsonicDemo.generated.h"

class USubsonicEventCollection;
class USubsonicEventCollectionExecutor;
class USoundWave;

UCLASS()
class YOURPROJECT_API ASubsonicDemo : public AActor
{
    GENERATED_BODY()

public:
    ASubsonicDemo();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(EditAnywhere, Category = "Subsonic")
    TObjectPtr<USoundWave> DemoSound;

    UPROPERTY()
    TObjectPtr<USubsonicEventCollection> DemoEventCollection;

    UPROPERTY()
    TObjectPtr<USubsonicEventCollectionExecutor> DemoExecutor;

    FGameplayTag StartPlaybackTag;
    FGameplayTag StopPlaybackTag;
};
```

**SubsonicDemo.cpp**
```cpp
#include "SubsonicDemo.h"
#include "SubsonicEventCollectionObjects.h"
#include "SubsonicSubsystem.h"
#include "Sound/SoundWave.h"
#include "SubsonicAction_GeneratorSource.h" // For FSubsonicEventAction_GeneratorSourcePlay
#include "SubsonicAction_EventCore.h"       // For FSubsonicEventAction_DelayEvent

ASubsonicDemo::ASubsonicDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASubsonicDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!DemoSound)
    {
        UE_LOG(LogTemp, Warning, TEXT("SubsonicDemo: No sound assigned."));
        return;
    }

    // 1. 构建事件集合定义
    UE::Subsonic::Core::FSubsonicEventCollectionDefinition CollectionDef;

    // 注册 “播放声音” 动作到 “Start” 事件
    UE::Subsonic::FSubsonicEventAction_GeneratorSourcePlay PlayAction;
    PlayAction.Name = TEXT("MainSource");
    PlayAction.Sound = DemoSound;
    PlayAction.Scope = UE::Subsonic::ESubsonicExecutionScope::Executor;
    CollectionDef.Events.Add(TEXT("Start"), { MakeShared<UE::Subsonic::FSubsonicEventAction_GeneratorSourcePlay>(PlayAction) });

    // 注册 “延迟后停止” 动作到 “Stop” 事件
    // 动作1：延迟2秒
    UE::Subsonic::FSubsonicEventAction_DelayEvent DelayAction;
    DelayAction.DelayName = TEXT("StopDelay");
    DelayAction.EventName = FGameplayTag::RequestGameplayTag(TEXT("Subsonic.StopNow"));
    DelayAction.Delay = 2.0f;
    CollectionDef.Events.Add(TEXT("Stop"), { MakeShared<UE::Subsonic::FSubsonicEventAction_DelayEvent>(DelayAction) });

    // 注册 “停止声音” 动作到 “StopNow” 事件 (由延迟事件触发)
    UE::Subsonic::FSubsonicEventAction_GeneratorSourceStop StopAction;
    StopAction.Name = TEXT("MainSource");
    StopAction.Scope = UE::Subsonic::ESubsonicExecutionScope::Executor;
    CollectionDef.Events.Add(TEXT("StopNow"), { MakeShared<UE::Subsonic::FSubsonicEventAction_GeneratorSourceStop>(StopAction) });

    // 2. 创建事件集合对象
    DemoEventCollection = NewObject<USubsonicEventCollection>(this);
    DemoEventCollection->SetDefinition(MoveTemp(CollectionDef));

    // 3. 创建执行器
    USubsonicSubsystem* Subsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
    if (Subsystem && DemoEventCollection)
    {
        DemoExecutor = Subsystem->CreateExecutorBP(this, TEXT("DemoExecutor"), DemoEventCollection,
            FAudioDeviceManager::Get()->GetMainAudioDeviceId());
    }

    // 4. 立即触发“开始”事件
    StartPlaybackTag = FGameplayTag::RequestGameplayTag(TEXT("Subsonic.Start"));
    StopPlaybackTag = FGameplayTag::RequestGameplayTag(TEXT("Subsonic.Stop"));

    if (DemoExecutor)
    {
        ESubsonicExecutionResult Result;
        DemoExecutor->ExecuteEvent(StartPlaybackTag, Result);
        UE_LOG(LogTemp, Log, TEXT("SubsonicDemo: Started playback. Will auto-stop in 2 seconds."));

        // 2秒后触发停止事件 (在真实项目中，这可能由UI按钮或游戏逻辑触发)
        FTimerHandle TimerHandle;
        GetWorldTimerManager().SetTimer(TimerHandle, [this]()
        {
            if (DemoExecutor)
            {
                ESubsonicExecutionResult Result;
                DemoExecutor->ExecuteEvent(StopPlaybackTag, Result);
                UE_LOG(LogTemp, Log, TEXT("SubsonicDemo: Stop event triggered."));
            }
        }, 2.0f, false);
    }
}
```

## 模块依赖

要使用 Subsonic 插件，你的模块需要依赖以下模块（除标准核心模块外）：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 的核心类型和接口定义 |
| `SubsonicEngine` | Subsonic 的主要运行时引擎实现 |
| `AudioMixer` | 底层音频混合器，用于声音生成和播放 |
| `MetasoundFrontend` | MetaSound 的前端API，用于集成 MetaSound 生成器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了一个糟糕的合并，撤销了对 Subscriber 的大幅改动，应用了最小化的非弃用修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 弃用修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/静默了 PVS（静态代码分析）警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | （非插件直接相关）新增了内容浏览器的音频菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF。 |

### 维护评价

Subsonic 插件处于**活跃开发**阶段。
- **年龄**：创建于 2026 年初，是一个非常新的系统。
- **更新频率**：最近一次更新在 2026 年 5 月，距今不到一个月，并且是修复合并错误和兼容性问题，表明核心功能仍在调整和稳定中。
- **状态**：作为实验性插件（`IsExperimentalVersion: true`），API 和行为可能会发生变化，不保证向后兼容。
- **推荐度**：**推荐用于实验和原型开发**。它解决了音频逻辑管理的实际痛点，设计理念先进。但由于其**实验性质和近期频繁的非功能性修复**，不建议在需要长期稳定支持的商业项目中作为核心依赖，除非团队有意愿并有能力跟踪和适应其 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/AudioTests/Private/Subsonic)