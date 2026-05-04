# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、事件集合定义） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个**高层音频编排与播放系统**，解决的核心问题是：在复杂游戏场景中，需要一种声明式、事件驱动的方式来管理音频播放，而不是手动编写大量播放/停止/参数调节的代码。

具体来说，Subsonic 提供：

1. **事件集合（Event Collection）**：将一组相关的音频事件（播放、停止、延迟、参数调节等）组织成一个可复用的数据资产，通过 GameplayTag 触发
2. **执行器（Executor）**：绑定到事件集合，负责执行其中的事件，支持作用域隔离（每个执行器独立或全局共享）
3. **双路音频播放**：
   - **AudioComponent 路径**：传统的 UE AudioComponent 播放方式，适合一次性音效
   - **GeneratorSource 路径**：直接在音频渲染线程生成音频，支持实时 DSP 参数（音量、音高、高低通滤波），适合需要精细控制的持续音效
4. **MetaSound 集成**：GeneratorSource 路径支持 MetaSound 图作为音频源，参数可实时透传
5. **线程安全的参数传递**：通过 FSubsonicRelay 机制，游戏线程的参数变更安全地批量传递到音频渲染线程

**为什么存在**：传统的 UE 音频系统（AudioComponent + SoundCue）在面对复杂的音频编排需求时（如：触发事件 A 后延迟 2 秒播放音效 B，同时调节正在播放的音效 C 的音量），需要大量手写蓝图或 C++ 逻辑。Subsonic 将这些编排逻辑数据化，让音频设计师可以在数据资产中声明式地定义音频行为。

## 使用场景

- 你在做一个开放世界游戏，需要根据玩家位置/状态触发复杂的环境音效组合 → 用 Subsonic Event Collection 定义事件，用 Executor 触发
- 你需要实时调节正在播放的音效参数（音量渐变、音高变化、滤波器扫频）→ 用 GeneratorSource 路径 + SubsonicParameterStore
- 你有 MetaSound 图需要被游戏逻辑驱动，且需要统一的参数管理 → 用 GeneratorSource 的 MetaSound 集成
- 你需要管理大量命名的 AudioComponent 实例，避免手动创建/销毁 → 用 AudioComponent Subscriber 的 FindOrAdd 模式
- 你需要在音频事件之间添加延迟、条件分支等编排逻辑 → 用 DelayEvent Action 和 EventResolutionRule

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 创建一个绑定到指定 Event Collection 的执行器 | `USubsonicSubsystem` |
| `Execute Event` | 通过 GameplayTag 触发事件集合中的事件，返回执行结果 | `USubsonicEventCollectionExecutor` |

### 使用示例（蓝图描述）

**基本用法：创建执行器并触发事件**

1. 获取 `USubsonicSubsystem`（通过 Get Game Instance Subsystem 节点）
2. 调用 `Create Executor`，传入：
   - World Context Object（通常是 Self）
   - Name：执行器的命名标识
   - Collection：一个 `USubsonicEventCollection` 资产引用
3. 将返回的 `USubsonicEventCollectionExecutor` 保存为变量
4. 在需要触发音频时，调用 `Execute Event`，传入 GameplayTag（如 `Audio.Event.Footstep`）
5. 通过 `OutResult` 输出引脚判断是否执行成功（Succeeded / Failed）

**事件集合中的 Action 配置（编辑器中）**

在 `USubsonicEventCollection` 资产中，你可以配置以下 Action：

- **Play Sound (AudioComponent)**：通过 AudioComponent 播放声音，支持 FindOrAdd 模式复用组件
- **Modify Audio Component**：修改已有的 AudioComponent 参数（音量、音高等）
- **Play Sound (GeneratorSource)**：通过 GeneratorSource 播放声音，支持实时 DSP 参数
- **Stop Sound (GeneratorSource)**：停止指定的 GeneratorSource
- **Delay Event**：延迟指定时间后触发另一个事件

每个 Action 都有 `Name`（命名标识）和 `Scope`（Executor 作用域或全局作用域）属性，用于在同一批 Action 之间共享音频实例。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"
#include "SubsonicGeneratorSourceSubscriber.h"
```

### 基本用法

**创建执行器并触发事件**

```cpp
// 来源: Public/SubsonicSubsystem.h, Public/SubsonicEventCollectionObjects.h

// 获取 Subsonic 子系统
USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();

// 创建执行器（绑定到一个 Event Collection 资产）
USubsonicEventCollectionExecutor* Executor = SubsonicSubsystem->CreateExecutorBP(
    GetWorld(),                          // WorldContextObject
    FName("MyExecutor"),                 // 执行器名称
    MyEventCollection                    // USubsonicEventCollection* 资产引用
);

// 触发事件
ESubsonicExecutionResult Result;
Executor->ExecuteEvent(FGameplayTag::RequestGameplayTag("Audio.Event.Combat"), Result);

if (Result == ESubsonicExecutionResult::Succeeded)
{
    // 事件成功执行
}

// 用完后注销执行器，释放关联的音频资源
Executor->Unregister();
```

### 进阶用法

**直接操作 GeneratorSource Subscriber 播放声音并设置参数**

```cpp
// 来源: Public/StandardEventSubscribers/SubsonicGeneratorSourceSubscriber.h

// 获取音频设备上的 GeneratorSource Subscriber
// （通常通过 Subsonic 内部的 Action 系统自动调用，但也可以直接访问）
USubsonicGeneratorSourceSubscriber* GenSubscriber = AudioDevice->GetSubsystem<USubsonicGeneratorSourceSubscriber>();

// 播放声音
GenSubscriber->PlaySound(
    FName("AmbientLoop"),                // 命名标识
    *MySoundWave,                        // USoundWave 引用
    AuthoredParams,                      // FSubsonicParameterStore（初始参数）
    true                                 // bReleaseExisting：是否释放同名的已有实例
);

// 实时设置参数（最高优先级，覆盖初始参数）
FSubsonicParameterStore RuntimeParams;
// ... 设置参数 ...
GenSubscriber->SetParameters(FName("AmbientLoop"), RuntimeParams);

// 停止声音
GenSubscriber->StopSound(FName("AmbientLoop"));
```

**使用 FSubsonicRelay 进行线程安全的参数传递**

```cpp
// 来源: Public/StandardEventSubscribers/SubsonicRelay.h

// FSubsonicRelay 负责将游戏线程的命令批量传递到音频渲染线程
// 通常由 Subscriber 内部管理，不需要直接操作

// 命令类型：
// - FRelayCommand::EType::SetParameters：设置参数
// - FRelayCommand::EType::Play：开始播放
// - FRelayCommand::EType::Stop：停止播放
```

## Demo 示例

### 最小示例：创建执行器并触发音频事件

```cpp
// MyAudioManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAudioManager.generated.h"

class USubsonicEventCollection;
class USubsonicEventCollectionExecutor;

UCLASS()
class AMyAudioManager : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioManager();

    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<USubsonicEventCollection> EventCollection;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void TriggerAudioEvent(FGameplayTag EventTag);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    TObjectPtr<USubsonicEventCollectionExecutor> Executor;
};
```

```cpp
// MyAudioManager.cpp
#include "MyAudioManager.h"
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"

AMyAudioManager::AMyAudioManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAudioManager::BeginPlay()
{
    Super::BeginPlay();

    if (EventCollection)
    {
        USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
        if (SubsonicSubsystem)
        {
            Executor = SubsonicSubsystem->CreateExecutorBP(
                this,
                FName("GameplayAudio"),
                EventCollection
            );
        }
    }
}

void AMyAudioManager::TriggerAudioEvent(FGameplayTag EventTag)
{
    if (!Executor)
    {
        return;
    }

    ESubsonicExecutionResult Result;
    Executor->ExecuteEvent(EventTag, Result);

    if (Result == ESubsonicExecutionResult::Failed)
    {
        UE_LOG(LogTemp, Warning, TEXT("Subsonic event '%s' not found in collection"), *EventTag.ToString());
    }
}

void AMyAudioManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Executor)
    {
        Executor->Unregister();
        Executor = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 Build.cs 分析，SubsonicEngine 模块的依赖关系：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 核心类型定义（Executor、EventCollection、ParameterStore 等） |
| `GameplayTags` | 用于事件标识的 GameplayTag 系统 |
| `StructUtils` | TInstancedStruct 支持，用于 Action 的多态存储 |
| `AudioMixer` | 音频渲染线程接口（IAudioMixerGeneratorSource、FMixerDevice） |
| `MetasoundFrontend` | MetaSound 图集成（FMetasoundGenerator） |
| `SignalProcessing` | DSP 工具（滤波器、重采样器） |

## 维护状态

### 近期更新

- 2026-04-23 `129c3dc2` Fix/silence PVS warnings
- 2026-04-14 `01c9ce5d` [ContentBrowser] New Add Menu Audio Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-13 `cb602f27` Subsonic: Subscriber implementation consolidation and removal of action and event scope
- 2026-04-02 `cd4230bd` Remove code optimization submitted by mistake

### 维护评价

- **创建时间**：2026-04-02（标记为未来日期，可能是开发分支的占位时间戳）
- **实验性标记**：`IsExperimentalVersion: true`，`EnabledByDefault: false`
- **代码成熟度**：
  - 代码结构清晰，有完整的模块划分（Core/Editor/Engine/Test）
  - 有测试模块（SubsonicEngineTest），说明有自动化测试覆盖
  - 使用了现代 UE 惯例（Subsystem、GameplayTag、TInstancedStruct）
  - 线程安全设计（FSubsonicRelay、atomic 标志位）
- **已知限制**：
  - 实验性插件，不保证向后兼容
  - 默认未启用，需要手动在插件管理器中启用
  - 文档 URL 为空，官方文档尚未发布
- **推荐程度**：⚠️ **谨慎使用**。适合早期原型开发和内部实验，不建议在生产项目中使用。如果需要稳定的音频编排方案，建议等待正式版本或使用传统的 AudioComponent + Blueprint 方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic)
- 官方文档：暂无（DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)