# Audio Insights Runtime

> Enable sending profiling and debugging data via Blueprints to the Audio Insights plugin.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioInsightsRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsightsRuntime) | |

## 用途

该插件为 **Audio Insights** 编辑器工具提供了一个运行时接口。它的核心作用是允许游戏逻辑（通过蓝图或C++）在运行时向 Audio Insights 的事件日志发送自定义的、带上下文的事件消息。这解决了音频开发者在调试和分析音频系统时，需要将游戏状态、特定音效播放、或自定义逻辑与音频分析数据关联起来的需求。它充当了游戏运行时与 Audio Insights 分析工具之间的桥梁。

## 使用场景

- 你需要在 Audio Insights 的事件日志中记录一个自定义的音频相关事件，例如“玩家触发了对话”、“环境音效区域切换”或“音频系统错误”。
- 你希望将特定的 `USoundBase` 资产或 `AActor` 与一个音频事件关联起来，以便在 Audio Insights 中进行筛选和追踪。
- 你正在使用 `UAudioComponent` 播放声音，并希望为其记录一个生命周期事件（如开始、结束、被中断）。

## 蓝图用法

该插件提供了两个核心的蓝图函数，位于 `Audio|AudioInsights` 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Log Audio Insights Event` | 向 Audio Insights 事件日志发送一个事件，可关联声音资产和 Actor。 | `UAudioInsightsBlueprintLibrary` |
| `Log Audio Insights Event For Audio Component` | 向 Audio Insights 事件日志发送一个事件，并关联到指定的 AudioComponent。 | `UAudioInsightsBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **记录一个与特定音效和角色关联的事件**：
    - 在蓝图中，从 `Log Audio Insights Event` 节点开始。
    - 将 `World Context Object` 连接到当前世界上下文（例如 `Self` 或 `Get Player Character`）。
    - 设置 `Event Name` 为 “NPC_Dialogue_Started”。
    - 将 `Sound Asset` 引用连接到正在播放的对话声音资产。
    - 将 `Actor` 引用连接到正在说话的 NPC 角色。
    - 执行该节点，事件将出现在 Audio Insights 的事件日志中，并可按声音资产或角色进行筛选。

2.  **记录一个与特定 AudioComponent 关联的事件**：
    - 在蓝图中，从 `Log Audio Insights Event For Audio Component` 节点开始。
    - 将 `World Context Object` 连接到当前世界上下文。
    - 设置 `Event Name` 为 “AmbientSound_Loop_Stopped”。
    - 将 `Audio Component` 引用连接到刚刚停止的环境音效组件。
    - 执行该节点，事件将与该 AudioComponent 的详细信息（如位置、资产）一起被记录。

## C++ 用法

### 头文件引入

```cpp
#include "AudioInsightsBlueprintLibrary.h"
```

### 基本用法

从源码中的函数声明和注释提取的用法示例。

```cpp
// 假设在某个 Actor 或 Component 的函数中
#include "AudioInsightsBlueprintLibrary.h"
#include "Sound/SoundBase.h"
#include "Components/AudioComponent.h"

// 示例1：记录一个通用的音频事件
void AMyActor::OnSomeAudioEvent()
{
    // 获取世界上下文
    UWorld* World = GetWorld();
    if (World)
    {
        // 记录事件，关联一个声音资产和自身
        UAudioInsightsBlueprintLibrary::LogAudioInsightsEvent(
            World,
            TEXT("CustomEvent_Triggered"),
            MySoundAsset, // USoundBase* 指针
            this // AActor* 指针
        );
    }
}

// 示例2：记录一个与特定 AudioComponent 关联的事件
void AMyActor::OnAudioComponentStopped(UAudioComponent* StoppedComponent)
{
    if (StoppedComponent)
    {
        UAudioInsightsBlueprintLibrary::LogAudioInsightsEventForAudioComponent(
            GetWorld(),
            TEXT("AudioComponent_Stopped"),
            StoppedComponent
        );
    }
}
```

### 进阶用法

结合游戏逻辑，用于音频系统的调试和监控。

```cpp
// 在音频管理器中，跟踪所有播放中的音效
void UMyAudioManager::StartSoundWithTracking(USoundBase* Sound, AActor* Owner)
{
    UAudioComponent* Comp = UGameplayStatics::SpawnSoundAttached(Sound, Owner->GetRootComponent());
    if (Comp)
    {
        ActiveSoundComponents.Add(Comp);
        // 记录开始播放事件
        UAudioInsightsBlueprintLibrary::LogAudioInsightsEventForAudioComponent(
            GetWorld(),
            TEXT("SoundPlayback_Started"),
            Comp
        );
        // 绑定结束回调以记录停止事件
        Comp->OnAudioFinished.AddDynamic(this, &UMyAudioManager::OnTrackedSoundFinished);
    }
}

void UMyAudioManager::OnTrackedSoundFinished(UAudioComponent* FinishedComponent)
{
    UAudioInsightsBlueprintLibrary::LogAudioInsightsEventForAudioComponent(
        GetWorld(),
        TEXT("SoundPlayback_Finished"),
        FinishedComponent
    );
    ActiveSoundComponents.Remove(FinishedComponent);
}
```

## Demo 示例

一个最小的 C++ Actor 示例，演示如何使用该插件记录事件。

```cpp
// MyAudioInsightsDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAudioInsightsDemoActor.generated.h"

class USoundBase;
class UAudioComponent;

UCLASS()
class MYPROJECT_API AMyAudioInsightsDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioInsightsDemoActor();

    UPROPERTY(EditAnywhere, Category = "Audio")
    USoundBase* TestSound;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void PlayAndLogSound();

private:
    UPROPERTY()
    UAudioComponent* CurrentAudioComponent;

    UFUNCTION()
    void OnSoundFinished();
};
```

```cpp
// MyAudioInsightsDemoActor.cpp
#include "MyAudioInsightsDemoActor.h"
#include "AudioInsightsBlueprintLibrary.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"

AMyAudioInsightsDemoActor::AMyAudioInsightsDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAudioInsightsDemoActor::PlayAndLogSound()
{
    if (TestSound)
    {
        // 播放声音
        CurrentAudioComponent = UGameplayStatics::SpawnSoundAttached(
            TestSound,
            GetRootComponent()
        );

        if (CurrentAudioComponent)
        {
            // 记录开始播放事件
            UAudioInsightsBlueprintLibrary::LogAudioInsightsEventForAudioComponent(
                GetWorld(),
                TEXT("DemoActor_SoundStarted"),
                CurrentAudioComponent
            );

            // 绑定结束事件
            CurrentAudioComponent->OnAudioFinished.AddDynamic(this, &AMyAudioInsightsDemoActor::OnSoundFinished);
        }
    }
}

void AMyAudioInsightsDemoActor::OnSoundFinished()
{
    // 记录播放结束事件
    UAudioInsightsBlueprintLibrary::LogAudioInsightsEventForAudioComponent(
        GetWorld(),
        TEXT("DemoActor_SoundFinished"),
        CurrentAudioComponent
    );

    CurrentAudioComponent = nullptr;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-10-22 6f5faf67 [Audio Insights] Added Audio::Trace::EventLog::SendEvent API to Blueprints

### 维护评价

该插件**非常新**，创建于 2025 年 10 月 22 日，且目前仅有一条提交记录，即其初始功能实现。它被标记为 `IsBetaVersion = true`，表明其处于**早期开发或测试阶段**。由于功能单一且明确，短期内可能不会有频繁更新，但作为 Audio Insights 生态的一部分，其长期维护取决于 Audio Insights 主插件的发展。目前**不建议在生产环境中依赖此插件**，更适合用于原型开发、内部工具或音频调试场景。需要关注其 Beta 状态带来的潜在不稳定性和 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsightsRuntime)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsightsRuntime/Tests) (如果存在)