# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 亚音速音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、音频数据等） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个实验性的、高级的音频编辑和播放系统。它通过定义“事件集合”（Event Collection）来以数据驱动的方式组织和触发复杂的音频逻辑。其核心解决的问题是，传统 UE 音频播放需要将播放、停止、参数设置等逻辑硬编码在游戏代码中，而 Subsonic 允许音频设计师在编辑器中通过可序列化的资产来编排音频行为序列，包括播放声音、修改音频组件属性、延迟执行等，从而将音频逻辑从游戏逻辑中解耦，提高迭代效率和协作便利性。

## 使用场景

- **动态音频序列编排**：你需要实现一个复杂的过场动画音频序列，包含多个声音的按顺序播放、淡入淡出、以及根据游戏状态触发的不同音效分支，而不想在蓝图或 C++ 中编写大量流程控制代码。
- **音频与逻辑解耦**：音频设计师希望独立于程序员，通过编辑器资产来调整音频的触发时机和行为组合。
- **精确控制音频生命周期**：需要管理一组共享名称的音频资源（如环境音、音乐层），并能方便地通过标签（Tag）找到并执行预定义的播放、停止或参数调整操作。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 从一个事件集合创建执行器实例，用于触发集合内的音频事件。 | `USubsonicSubsystem` |
| `Execute Event` | 在执行器上触发一个指定标签的音频事件。 | `USubsonicEventCollectionExecutor` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键创建 “Subsonic” -> “Event Collection” 蓝图资产。在该资产的编辑器中，可以定义一组事件，每个事件可以包含多个按顺序执行的“动作”（Action），如 “Play Sound”、“Delay Event” 等。
2.  **获取执行器**：在游戏蓝图中，使用 `Create Executor` 节点，传入一个事件集合资产和一个名称（用于标识），得到一个执行器对象。
3.  **触发事件**：当需要播放音频时，调用执行器对象的 `Execute Event` 节点，并传入在事件集合中定义好的事件标签（例如 `Gameplay.Shoot.Fire`）。系统将根据事件集合中的定义，自动执行对应的音频播放、延迟等动作。

## C++ 用法

### 头文件引入

```cpp
// 使用 Subsonic 核心和引擎功能
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"
```

### 基本用法

从测试逻辑和公开 API 推断的用法。一个事件集合代表一个可执行的音频逻辑单元。

```cpp
// 1. 获取 Subsonic 子系统
USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
if (!SubsonicSubsystem) return;

// 2. 从资产或代码中获取一个事件集合对象
const USubsonicEventCollection* MyCollection = ...; // 通常从资产加载或创建

// 3. 为该集合创建一个执行器
USubsonicEventCollectionExecutor* MyExecutor = SubsonicSubsystem->CreateExecutorBP(
    GetWorld(), // WorldContextObject
    FName("MyExecutor"), 
    MyCollection
);

// 4. 通过执行器触发一个事件
ESubsonicExecutionResult Result;
MyExecutor->ExecuteEvent(FGameplayTag::RequestGameplayTag("Event.CoinPickup"), Result);

// 5. 使用完毕后，可以注销执行器以释放资源
MyExecutor->Unregister();
```

### 进阶用法

通过查看 `FSubsonicEventAction_AudioComponentModify` 等结构，可以了解如何在 C++ 中自定义或配置事件动作。这些结构体通常作为事件定义的数据部分，通过 `TInstancedStruct` 被包含在事件集合的定义中。

```cpp
// 假设我们正在构建一个事件集合的定义（通常由编辑器完成，代码仅作示例）
Core::FSubsonicEventCollectionDefinition Definition;

// 创建一个“播放声音”动作
FSubsonicEventAction_AudioComponentPlay PlayAction;
PlayAction.Name = FName("MainTheme");
PlayAction.Sound = SomeSoundAsset;
PlayAction.Scope = ESubsonicExecutionScope::Global;

// 将动作添加到某个事件的序列中 (这里需要访问底层定义结构，非公开API典型用法)
// Definition.AddActionToEvent("Music.Start", PlayAction);
```

## Demo 示例

一个最小的 C++ 示例，展示如何设置 Subsonic 系统的基本骨架。

### MySubsonicDemo.h
```cpp
// MySubsonicDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameplayTagContainer.h"
#include "MySubsonicDemo.generated.h"

class USubsonicEventCollection;
class USubsonicEventCollectionExecutor;
class USubsonicSubsystem;

UCLASS()
class MYPROJECT_API AMySubsonicDemo : public AActor
{
    GENERATED_BODY()

public:
    AMySubsonicDemo();

    UPROPERTY(EditAnywhere, Category = "Subsonic")
    const USubsonicEventCollection* DemoCollection;

    UFUNCTION(BlueprintCallable, Category = "Subsonic")
    void TriggerAudioEvent(FGameplayTag EventTag);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    USubsonicEventCollectionExecutor* Executor;
    USubsonicSubsystem* SubsonicSubsystem;
};
```

### MySubsonicDemo.cpp
```cpp
// MySubsonicDemo.cpp
#include "MySubsonicDemo.h"
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"

AMySubsonicDemo::AMySubsonicDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySubsonicDemo::BeginPlay()
{
    Super::BeginPlay();

    SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem && DemoCollection)
    {
        Executor = SubsonicSubsystem->CreateExecutorBP(
            GetWorld(),
            FName("DemoExecutor"),
            DemoCollection
        );
    }
}

void AMySubsonicDemo::TriggerAudioEvent(FGameplayTag EventTag)
{
    if (Executor)
    {
        ESubsonicExecutionResult Result;
        Executor->ExecuteEvent(EventTag, Result);
        // 可以处理 Result 来确认事件是否成功执行
    }
}
```

## 模块依赖

基于 `SubsonicEngine` 模块（当前分析的模块）和插件整体功能推断。

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 插件的核心基础类型、接口和定义，是其他模块的依赖基础。 |
| `MetasoundFrontend` / `Metasound` | 用于集成和驱动 MetaSound 音频图表生成器。 |
| `AudioMixer` | 访问底层音频混音器设备（`FMixerDevice`），用于管理 GeneratorSource 和音频渲染线程通信。 |
| `AudioPlatformSettings` | 获取音频设备配置和设置。 |
| `GameplayTags` | 核心的事件标识和路由机制依赖。 |
| `PropertyBag` / `PropertyPath` | 用于管理参数存储（`FSubsonicParameterStore`）和数据驱动。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复错误合并导致的覆盖问题，回退部分变更并应用最小修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 弃用相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默 PVS 代码分析警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | （可能与内容浏览器菜单相关，非直接功能更新）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移为新的 UE_LOGF 宏。 |

### 维护评价

- **状态**：**实验性**。作为实验性插件（`IsExperimentalVersion=true`），其 API 和功能可能在未来版本中发生重大变化。
- **活跃度**：近期（2026年4-5月）有维护性更新，包括代码合并冲突修复、警告清理和 API 适配，表明仍在维护中。
- **功能成熟度**：从源码看，系统架构（事件、动作、订阅者、生成器）完整，但作为实验性功能，其稳定性和文档可能不完善。
- **建议**：**谨慎评估使用**。非常适合愿意承担实验性风险、追求高级音频工作流的项目。不推荐在需要长期稳定性的生产环境中作为核心音频解决方案。应密切关注 Epic 的更新日志和兼容性说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- 官方文档：无（.uplugin 中 `DocsURL` 为空）
- 测试用例：[SubsonicEngineTest](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)