# AudioGameplay

> Core plugin for audio gameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频游戏玩法 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频相关逻辑资产） |
| 模块 | `AudioGameplay` (Runtime), `AudioGameplayTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay) | |

## 用途
该插件为基于音频逻辑的游戏玩法（Audio-driven Gameplay）提供核心框架与支持。其核心目标是解耦音频系统的播放逻辑与复杂的游戏逻辑，允许开发者通过蓝图或C++将音频事件（如声音播放、音量变化、声音停止等）作为游戏状态或玩家行为的一部分进行监听、响应和控制。它超越了基础的“播放声音”功能，专注于创建与游戏进程深度集成的、动态的、可响应游戏状态的音频体验。

## 使用场景
- 你需要根据游戏事件（如角色跳跃、拾取物品、受到伤害）动态触发复杂的音频反馈，而不仅仅是播放一个音效。
- 你需要一个音频状态机，可以根据游戏进度（如战斗、探索、对话）自动切换环境音或背景音乐层。
- 你希望实现音频驱动的游戏机制，例如通过检测玩家发出的特定声音（拍手、喊叫）来与环境互动。
- 你的项目需要一套标准化的接口来管理游戏中所有与玩法相关的音频请求，避免音频逻辑分散在各处。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Audio Event` | 根据音频事件数据播放对应的声音，并可返回播放句柄用于后续控制。 | `UAudioGameplay` |
| `Stop Audio` | 通过播放句柄停止一个正在播放的音频事件。 | `UAudioGameplay` |
| `Set Audio Parameter` | 修改正在播放音频事件的参数，如音量、音高。 | `UAudioGameplay` |
| `Get Audio Component` | 获取管理特定音频事件播放的 AudioComponent 引用。 | `UAudioGameplay` |
| `Add Audio Tag` / `Remove Audio Tag` | 为 Actor 或对象添加/移除音频标签，用于基于标签的音频查询和触发。 | `UAudioGameplayStatics` |

### 使用示例（蓝图描述）

1.  **基础事件响应**：在角色蓝图中，当 `OnJump` 事件触发时，调用 `Play Audio Event` 节点，并传入一个预定义的 `JumpSoundEvent` 数据资产。可以将返回的句柄存储起来，以便在落地时调用 `Stop Audio` 停止可能存在的落地准备音效。
2.  **环境音状态管理**：在关卡蓝图中，使用一个 `AudioGameplay` 子系统或管理器。根据游戏状态变量（如“是否在室内”），调用 `Set Audio Parameter` 节点去调整“室内”环境音效的音量，实现平滑过渡。
3.  **音频标签查询**：给场景中所有可交互物体（如门、箱子）添加 `InteractiveObject` 音频标签。在播放通用的“世界交互”音效前，可以使用 `Get Actors with Audio Tag` 节点查询附近是否存在此类物体，以决定是否播放特定的环境反馈音。

## C++ 用法

### 头文件引入

```cpp
#include "AudioGameplayModule.h"
// 根据具体使用的类，可能需要包含其他头文件，如：
#include "AudioGameplay/AudioGameplaySubsystem.h"
```

### 基本用法

以下是一个典型的使用流程，通过子系统播放一个音频事件。
*(注：具体函数签名基于插件常见架构推断)*

```cpp
// 在 Actor 或其他游戏类中
#include "AudioGameplay/AudioGameplaySubsystem.h"
#include "AudioGameplay/AudioGameplayEvent.h"

void AMyCharacter::PlayFootstep()
{
    // 获取音频游戏玩法子系统
    UAudioGameplaySubsystem* AudioSubSystem = GetWorld()->GetSubsystem<UAudioGameplaySubsystem>();
    if (AudioSubSystem)
    {
        // 创建一个音频事件数据 (通常来自一个 UObject 资产)
        FAudioGameplayEventData EventData;
        EventData.Event = FootstepSoundEvent; // 假设是一个 UAudioGameplayEvent* 指针
        EventData.Location = GetActorLocation();
        
        // 播放事件，并获取句柄
        FAudioGameplayHandle Handle = AudioSubSystem->PlayAudioEvent(EventData);
        
        // 存储句柄以备后续使用（如停止、调整）
        CurrentFootstepHandle = Handle;
    }
}

void AMyCharacter::StopFootstep()
{
    UAudioGameplaySubsystem* AudioSubSystem = GetWorld()->GetSubsystem<UAudioGameplaySubsystem>();
    if (AudioSubSystem && CurrentFootstepHandle.IsValid())
    {
        AudioSubSystem->StopAudio(CurrentFootstepHandle);
        CurrentFootstepHandle.Invalidate();
    }
}
```

### 进阶用法

结合音频标签和动态参数调整，实现更复杂的交互。

```cpp
#include "AudioGameplay/AudioGameplaySubsystem.h"
#include "AudioGameplay/AudioGameplayTag.h"

void AMyCharacter::InteractWithObject()
{
    // 检查被交互物体是否有特定音频标签
    if (InteractableObject->AudioGameplayTags.HasTag(AudioTag_WetSurface))
    {
        // 构建一个带有附加参数的事件
        FAudioGameplayEventData EventData;
        EventData.Event = SurfaceInteractSoundEvent;
        EventData.Location = InteractableObject->GetActorLocation();
        EventData.Parameters.Add(FName(TEXT("SurfaceType")), 1.0f); // 假设 1.0f 代表“湿滑”
        
        // 播放，并立即对句柄应用参数
        UAudioGameplaySubsystem* SubSystem = GetWorld()->GetSubsystem<UAudioGameplaySubsystem>();
        FAudioGameplayHandle Handle = SubSystem->PlayAudioEvent(EventData);
        
        // 动态调整音量
        SubSystem->SetAudioParameter(Handle, FName(TEXT("VolumeMultiplier")), 0.8f);
    }
}
```

## Demo 示例

以下是一个最小的 Actor 示例，展示了如何响应游戏逻辑播放音频。

**AudioGameplayDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioGameplayDemoActor.generated.h"

class UAudioGameplayEvent;
class FAudioGameplayHandle;

UCLASS()
class MYPROJECT_API AAudioGameplayDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AAudioGameplayDemoActor();

    /** 要播放的音频事件资产 */
    UPROPERTY(EditAnywhere, Category = "Audio")
    UAudioGameplayEvent* ExplosionEvent;

    /** 蓝图可调用的播放函数 */
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void TriggerExplosionSound();

protected:
    virtual void BeginPlay() override;

private:
    /** 存储当前播放的音频句柄 */
    FAudioGameplayHandle CurrentHandle;
};
```

**AudioGameplayDemoActor.cpp**
```cpp
#include "AudioGameplayDemoActor.h"
#include "AudioGameplay/AudioGameplaySubsystem.h"
#include "AudioGameplay/AudioGameplayEvent.h"

AAudioGameplayDemoActor::AAudioGameplayDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ExplosionEvent = nullptr;
}

void AAudioGameplayDemoActor::BeginPlay()
{
    Super::BeginPlay();
}

void AAudioGameplayDemoActor::TriggerExplosionSound()
{
    if (!ExplosionEvent || !GetWorld()) return;

    UAudioGameplaySubsystem* AudioSubSystem = GetWorld()->GetSubsystem<UAudioGameplaySubsystem>();
    if (!AudioSubSystem) return;

    // 准备事件数据
    FAudioGameplayEventData EventData;
    EventData.Event = ExplosionEvent;
    EventData.Location = GetActorLocation();
    EventData.Instigator = GetInstigator(); // 可选，记录触发者

    // 播放音频并存储句柄
    CurrentHandle = AudioSubSystem->PlayAudioEvent(EventData);

    // 3秒后自动停止（示例逻辑）
    if (CurrentHandle.IsValid())
    {
        FTimerHandle TimerHandle;
        GetWorldTimerManager().SetTimer(TimerHandle, [this, AudioSubSystem]()
        {
            if (CurrentHandle.IsValid())
            {
                AudioSubSystem->StopAudio(CurrentHandle);
                CurrentHandle.Invalidate();
            }
        }, 3.0f, false);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 提供底层音频混合和渲染功能。 |
| `AudioExtensions` | 可能提供音频系统扩展点，用于插件集成。 |
| `AudioPlatformSettings` | 处理不同平台的音频设置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到更安全的 UE_LOGF 格式，提升日志健壮性。 |
| 2025-09-09 | `723f87e6` | Added missing include. | 修复了编译时缺失头文件包含的问题。 |
| 2025-08-20 | `1746b743` | AGV Updates / Glow up | 对插件进行了功能更新和界面/体验优化。 |
| 2025-07-29 | `a6ddb9ae` | AudioMixerCore put string definitions for Insights events into .cpp file | 重构，将性能分析事件的字符串定义移至 .cpp 文件，优化编译。 |
| 2025-07-25 | `5d147547` | [Audio] Add BP utility functions to AudioAssetUserData for interacting with audio asset tags | 为 AudioAssetUserData 添加了蓝图工具函数，用于操作音频资产标签。 |

### 维护评价

AudioGameplay 插件创建于 2021 年（约 4 年前），目前仍处于 **Beta** 实验性阶段。从 Git 历史看，直至 2026 年 4 月仍有活跃的提交，主要集中在编译修复、代码质量提升和功能增强上（如 AGV Updates）。这表明该插件仍在被维护和迭代，但 **尚未达到正式发布（Stable）状态**。

**主要注意事项**：
- **Beta 状态**：作为实验性插件，其 API 和功能可能会在后续版本中发生变动，不建议在关键的生产项目中重度依赖。
- **启用方式**：该插件默认不启用（`Installed: false`），需要在项目设置中手动启用，或通过 `Plugins` 界面启用。
- **文档缺失**：目前没有官方文档链接，使用时需主要依赖源码、示例和社区经验。

**推荐**：适合用于新项目原型开发或希望在音频交互玩法上进行探索的团队。若计划用于正式发布项目，需密切关注其版本更新和 API 稳定性公告，并准备在升级 UE 版本时处理可能的兼容性问题。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay/Source/AudioGameplayTests)