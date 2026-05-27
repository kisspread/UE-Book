# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产模板、编辑器工具） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个**数据驱动的高层音频创作与播放系统**，解决的核心问题是：如何用一种标准化、可配置的方式管理游戏中的复杂音频事件流，而不必在游戏逻辑中硬编码大量音频播放代码。

传统的 UE5 音频工作流通常需要直接操作 `UAudioComponent` 或 MetaSound，在游戏代码中散布大量播放/停止/参数设置的调用。Subsonic 提供了一套**事件集合（Event Collection）+ 执行器（Executor）+ 订阅者（Subscriber）** 的架构，将音频行为抽象为可编辑的事件动作（Action），支持：

- **双路径音频生成**：同时支持传统 `UAudioComponent` 路径和底层 `GeneratorSource`（波形直接生成）路径
- **内置 DSP 处理链**：音量（dB）、音高偏移（半音）、高通/低通滤波、淡出等，应用于 GeneratorSource 路径
- **MetaSound 集成**：GeneratorSource 路径可委托给 MetaSound 图，Subsonic 自动处理内置参数与 MetaSound 输入的桥接
- **跨线程安全通信**：通过 `FSubsonicRelay` 命令队列，将游戏线程的状态变更批量传递到音频渲染线程
- **作用域管理**：音频组件/源支持 Executor 级别和全局级别的命名池，支持复用和查找

## 使用场景

- 你在做一个**对话系统**，需要按对话节点延迟触发不同音效和语音 → 用 Subsonic 的 Event Collection + Delay Event 动作
- 你需要对音频做**实时 DSP 处理**（音量衰减、音高变化、滤波），但不想手动管理 AudioComponent 参数 → 用 GeneratorSource 路径的内置 DSP 参数
- 你有一个**复杂的音效编排需求**（多个音效按顺序/条件播放，播放完毕后触发下一个事件）→ 用 Execute On Finished 修饰器
- 你需要在**不同的执行上下文**（如多个敌人实例）中独立管理各自的音频状态，但音频组件名相同 → 用 Executor 作用域隔离
- 你想用 MetaSound 做音频生成，但又需要 Subsonic 的事件驱动控制 → GeneratorSource 自动桥接 MetaSound 输入参数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 从事件集合创建一个执行器实例 | `USubsonicSubsystem` |
| `Execute Event` | 通过 GameplayTag 触发事件集合中的指定事件 | `USubsonicEventCollectionExecutor` |

### 使用示例

**基础用法：创建执行器并触发事件**

1. 先创建一个 `USubsonicEventCollection` 资产（内容浏览器 → 右键 → Audio 菜单 → Subsonic Event Collection）
2. 在集合中配置事件和动作（如 Play Sound、Delay Event 等）
3. 在蓝图中：
   - 调用 `Create Executor` 节点，传入 WorldContextObject、名称和事件集合资产
   - 返回一个 `USubsonicEventCollectionExecutor` 对象
   - 调用该对象的 `Execute Event`，传入 GameplayTag（如 `GameplayCue.Player.Hit`）
   - 输出引脚 `OutResult` 可用分支判断执行是否成功（`Succeeded` / `Failed`）

**注意事项**：
- `Execute Event` 的 `OutResult` 参数使用了 `ExpandEnumAsExecs` 元数据，会自动生成执行引脚
- 执行器需要手动调用 `Unregister()` 清理资源（非自动销毁）

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"
```

### 基本用法：创建执行器并触发事件

```cpp
// 来源: Public/SubsonicSubsystem.h, Public/SubsonicEventCollectionObjects.h

// 获取 Subsonic 子系统
USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
if (SubsonicSubsystem)
{
    // 假设 Collection 是一个已加载的 USubsonicEventCollection 资产
    const USubsonicEventCollection* Collection = ...; 
    
    // 创建执行器
    USubsonicEventCollectionExecutor* Executor = SubsonicSubsystem->CreateExecutorBP(
        GetWorld(),           // WorldContextObject
        FName("MyExecutor"), // 执行器名称
        Collection            // 事件集合
    );
    
    if (Executor && Executor->IsValid())
    {
        // 触发事件
        ESubsonicExecutionResult Result;
        FGameplayTag EventTag = FGameplayTag::RequestGameplayTag(FName("Audio.Combat.Hit"));
        Executor->ExecuteEvent(EventTag, Result);
        
        if (Result == ESubsonicExecutionResult::Succeeded)
        {
            UE_LOG(LogTemp, Log, TEXT("Event executed successfully"));
        }
        
        // 使用完毕后清理
        Executor->Unregister();
    }
}
```

### 进阶用法：通过 GeneratorSourceSubscriber 直接播放波形

```cpp
// 来源: Public/StandardEventSubscribers/SubsonicGeneratorSourceSubscriber.h

// 获取 GeneratorSource 订阅者（它是一个 AudioEngineSubsystem）
USubsonicGeneratorSourceSubscriber* GeneratorSubscriber = nullptr;
if (FAudioDevice* AudioDevice = GEngine->GetMainAudioDevice())
{
    GeneratorSubscriber = AudioDevice->GetSubsystem<USubsonicGeneratorSourceSubscriber>();
}

if (GeneratorSubscriber)
{
    // 准备参数：音量、音高、滤波等
    FSubsonicParameterStore Params;
    // 假设 ParameterStore 有设置参数的方法
    
    // 在全局作用域播放
    GeneratorSubscriber->PlaySound(
        FName("Explosion_SFX"),    // 源的命名地址
        *ExplosionSoundWave,       // USoundWave 资产引用
        Params,                    // 参数存储
        true                       // 释放已有的同名源
    );
    
    // 在特定执行器作用域播放
    FExecutorScopeKey ScopeKey;
    ScopeKey.DeviceId = AudioDevice->DeviceID;
    GeneratorSubscriber->PlaySound(
        ScopeKey,                  // 执行器作用域键
        FName("AmbientLoop_SFX"),
        *AmbientSoundWave,
        Params
    );
    
    // 停止播放
    GeneratorSubscriber->StopSound(FName("Explosion_SFX"));
}
```

### 进阶用法：自定义参数写入 GeneratorSource

```cpp
// 来源: Public/StandardEventSubscribers/SubsonicGeneratorSourceSubscriber.h

// 设置实时参数（运行时，叠加到已有参数上）
GeneratorSubscriber->SetParameters(FName("MusicTrack"), RuntimeParams);

// 设置创作参数（编辑器预设，最低优先级层）
GeneratorSubscriber->SetAuthoredParameters(FName("MusicTrack"), AuthoredParams);
```

## Demo 示例

### 完整最小示例：Subsonic 事件触发系统

```cpp
// SubsonicDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SubsonicDemoComponent.generated.h"

class USubsonicEventCollection;
class USubsonicEventCollectionExecutor;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class YOURGAME_API USubsonicDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    USubsonicDemoComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 在蓝图中设置要使用的事件集合资产
    UPROPERTY(EditAnywhere, Category = "Subsonic")
    TObjectPtr<const USubsonicEventCollection> EventCollection;

    // 触发指定事件
    UFUNCTION(BlueprintCallable, Category = "Subsonic")
    bool TriggerAudioEvent(FGameplayTag EventTag);

protected:
    UPROPERTY()
    TObjectPtr<USubsonicEventCollectionExecutor> Executor;
};
```

```cpp
// SubsonicDemoComponent.cpp
#include "SubsonicDemoComponent.h"
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"

USubsonicDemoComponent::USubsonicDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void USubsonicDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    if (!EventCollection)
    {
        UE_LOG(LogTemp, Warning, TEXT("SubsonicDemoComponent: No Event Collection assigned."));
        return;
    }

    // 获取 Subsonic 子系统并创建执行器
    USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem)
    {
        Executor = SubsonicSubsystem->CreateExecutorBP(
            GetOwner(),
            FName("DemoExecutor"),
            EventCollection
        );

        if (!Executor)
        {
            UE_LOG(LogTemp, Error, TEXT("SubsonicDemoComponent: Failed to create executor."));
        }
    }
}

void USubsonicDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Executor)
    {
        Executor->Unregister();
        Executor = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}

bool USubsonicDemoComponent::TriggerAudioEvent(FGameplayTag EventTag)
{
    if (!Executor || !Executor->IsValid())
    {
        return false;
    }

    ESubsonicExecutionResult Result;
    Executor->ExecuteEvent(EventTag, Result);
    return Result == ESubsonicExecutionResult::Succeeded;
}
```

## 模块依赖

从源码结构推断，SubsonicEngine 依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 核心框架（事件集合定义、执行器、动作基类等） |
| `AudioMixer` | 底层音频混合器，GeneratorSource 和 FSubsonicRelay 使用 `FMixerDevice`、`ISoundGenerator`、`IAudioMixerGeneratorSource` |
| `MetaSound` | MetaSound 图集成，FSubsonicGenerator 支持将 MetaSound 生成器作为内部生成器 |
| `MetasoundFrontend` | MetaSound 前端，用于查询 MetaSound 输入端口 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并错误，回退对 Subscriber 的全量覆盖，保留最小非废弃修改 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃导致的合并冲突 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/消除 PVS Studio 静态分析警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增 Audio 菜单项（创建 Subsonic 资产的入口） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |

### 维护评价

**活跃维护中** — Subsonic 是一个 2026 年 1 月创建的新插件，目前处于**积极开发阶段**。

**优点**：
- 创建时间不足一年，最近一个月内仍有实质性的代码修改（合并修复、API 适配）
- 架构设计成熟：事件驱动 + 订阅者模式 + 跨线程安全的命令队列
- 双路径音频生成（AudioComponent + GeneratorSource）提供了灵活的音频处理方案
- 内置 DSP 处理链（音量/音高/滤波/淡出）覆盖常见需求

**注意事项**：
- ⚠️ 标记为 `IsExperimentalVersion: true`，**不保证向后兼容性**，API 可能随版本变更
- ⚠️ `EnabledByDefault: false`（隐含于 Experimental 标记），需要手动在项目设置中启用
- 从 git 历史看，近期有合并冲突相关的修复，说明主干分支合并可能带来不稳定因素
- FSoundWaveData API 废弃问题仍在处理中，上游 API 变化可能影响稳定性
- 文档 URL 为空，目前没有官方文档

**推荐**：适合**早期探索和原型验证**，不建议用于需要长期稳定的生产项目。关注 Epic 后续的正式发布版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)