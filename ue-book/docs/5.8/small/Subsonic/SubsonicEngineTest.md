# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 低频音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产/数据） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途
Subsonic 是一个用于创建和播放复杂音频体验的高级框架。它超越了简单的音效播放，提供了一套完整的音频创作管线，用于管理、混合和控制游戏中的音乐、环境音、对话和空间音效。该插件旨在解决需要动态、交互式和电影级音频体验的场景，例如大型开放世界游戏中的动态配乐系统或 VR 应用中精确的空间音频定位。

## 使用场景
- 你正在开发一个大型开放世界游戏，需要一套系统来平滑地混合不同区域的环境音和背景音乐 → 使用 Subsonic 管理音频层和过渡。
- 你的游戏剧情复杂，需要根据玩家选择动态改变对话和配乐 → 使用 Subsonic 的蓝图节点和数据资产来定义音频逻辑。
- 你需要在 VR 环境中创建沉浸式、精确追踪的 3D 音效 → 利用 Subsonic 的空间化支持来放置和处理声音。

## 蓝图用法
基于源码分析，Subsonic 提供了一套用于音频创作和播放的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Subsonic Source` | 从数据资产创建一个 Subsonic 音频源实例 | `USubsonicBlueprintLibrary` |
| `Play Subsonic Source` | 播放一个已创建的 Subsonic 音频源 | `USubsonicBlueprintLibrary` |
| `Stop Subsonic Source` | 停止正在播放的 Subsonic 音频源 | `USubsonicBlueprintLibrary` |
| `Set Subsonic Source Parameter` | 动态设置音频源的某个参数（如音量、音调） | `USubsonicBlueprintLibrary` |
| `Apply Subsonic Effect` | 向音频源应用一个子音效（如混响、延迟） | `USubsonicBlueprintLibrary` |
| `Set Subsonic Mix` | 将音频源分配到指定的混音总线 | `USubsonicBlueprintLibrary` |

### 使用示例（蓝图描述）
1.  **创建并播放一个音效**：
    *   从“内容浏览器”拖拽一个 `USubsonicDataAsset` 到蓝图图表中。
    *   连接该资产到 `Create Subsonic Source` 节点的输入引脚，生成一个 `USubsonicSource` 对象引用。
    *   将该引用连接到 `Play Subsonic Source` 节点的输入引脚，并指定一个播放起始位置（如 `Attach To Component` 用于 3D 音效）。
    *   执行该事件以播放音效。

2.  **动态调整音乐强度**：
    *   使用 `Create Subsonic Source` 创建音乐音频源。
    *   使用 `Set Subsonic Source Parameter` 节点，通过一个浮点变量（例如“战斗强度”）来动态控制音乐中某个层（Layer）的音量或触发状态。

## C++ 用法
以下示例基于测试用例 `SubsonicEngineTest` 中的用法模式。

### 头文件引入
```cpp
#include "Subsonic/SubsonicSubsystem.h"
#include "Subsonic/SubsonicDataAsset.h"
#include "Subsonic/SubsonicSource.h"
```

### 基本用法
```cpp
// 来源：基于 SubsonicEngineTest 中的测试模式
void AMyActor::PlayBasicSound()
{
    // 1. 获取 Subsonic 子系统
    UWorld* World = GetWorld();
    if (UAudioEngineSubsystem* Subsystem = World->GetSubsystem<USubsonicSubsystem>())
    {
        // 2. 加载或引用 Subsonic 数据资产
        USubsonicDataAsset* MySoundData = LoadObject<USubsonicDataAsset>(nullptr, TEXT("/Game/Audio/SFX_MyEffect.SFX_MyEffect"));
        if (MySoundData)
        {
            // 3. 创建音频源
            USubsonicSource* SoundSource = Subsystem->CreateSource(MySoundData, GetActorLocation(), this);
            
            // 4. 播放音频源
            if (SoundSource)
            {
                SoundSource->Play();
            }
        }
    }
}
```

### 进阶用法
```cpp
// 来源：基于对子系统和多源管理的测试推断
void AMyAudioController::SetupDynamicMusic()
{
    UWorld* World = GetWorld();
    USubsonicSubsystem* Subsystem = World->GetSubsystem<USubsonicSubsystem>();

    // 1. 创建背景音乐主音源
    MusicSource = Subsystem->CreateSource(BackgroundMusicAsset, FVector::ZeroVector, this);
    
    // 2. 创建一个环境音层音源并绑定到主音源
    AmbientSource = Subsystem->CreateSource(AmbientLayerAsset, FVector::ZeroVector, this);
    MusicSource->AttachLayer(AmbientSource, FName("AmbientLayer"));

    // 3. 播放并开始根据游戏状态更新参数
    MusicSource->Play();
    
    // 在游戏循环中调用，例如 Tick()
    void AMyAudioController::UpdateMusicBasedOnGameState(float CombatIntensity)
    {
        if (MusicSource && MusicSource->IsPlaying())
        {
            // 动态控制环境音层的音量
            MusicSource->SetLayerParameter(FName("AmbientLayer"), FName("Volume"), FMath::Lerp(0.2f, 1.0f, CombatIntensity));
            
            // 可以添加额外的实时效果
            if (CombatIntensity > 0.8f)
            {
                MusicSource->ApplyDynamicEffect(SubsonicEffect_FightReverb);
            }
        }
    }
}
```

## Demo 示例
一个最小化的 C++ 示例，展示如何初始化并播放一个 Subsonic 音频源。

```cpp
// MySubsonicDemoComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MySubsonicDemoComponent.generated.h"

class USubsonicSource;
class USubsonicDataAsset;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class UMySubsonicDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Subsonic")
    USubsonicDataAsset* DemoSoundDataAsset;

    UFUNCTION(BlueprintCallable, Category = "Subsonic")
    void PlayDemoSound();

private:
    UPROPERTY()
    USubsonicSource* ActiveSoundSource;
};
```

```cpp
// MySubsonicDemoComponent.cpp
#include "MySubsonicDemoComponent.h"
#include "Subsonic/SubsonicSubsystem.h"
#include "Subsonic/SubsonicDataAsset.h"
#include "Subsonic/SubsonicSource.h"
#include "World.h"

void UMySubsonicDemoComponent::PlayDemoSound()
{
    if (!DemoSoundDataAsset) return;

    UWorld* World = GetWorld();
    if (!World) return;

    USubsonicSubsystem* SubsonicSubsystem = World->GetSubsystem<USubsonicSubsystem>();
    if (!SubsonicSubsystem) return;

    // 停止之前的音源（如果有）
    if (ActiveSoundSource && ActiveSoundSource->IsPlaying())
    {
        ActiveSoundSource->Stop();
    }

    // 创建并播放新的音源
    FVector Location = GetOwner() ? GetOwner()->GetActorLocation() : FVector::ZeroVector;
    ActiveSoundSource = SubsonicSubsystem->CreateSource(DemoSoundDataAsset, Location, GetOwner());
    if (ActiveSoundSource)
    {
        ActiveSoundSource->Play();
    }
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `Synthesis` | 提供底层音频合成和处理功能 |
| `SignalProcessing` | 提供音频信号处理算法 |
| `MediaUtils` | 提供媒体文件加载和处理的工具函数 |
| `Spatialization` | 提供 3D 音频空间化支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并冲突，回退了对 Subsonic 订阅机制的破坏性修改，并应用了非废弃性修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复了静态代码分析（PVS-Studio）产生的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新了内容浏览器的“添加”菜单，可能涉及音频资产创建选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将部分 UE_LOG 宏调用迁移为更现代的 UE_LOGF 格式化字符串宏。 |

### 维护评价
Subsonic 是一个非常新的实验性插件（创建于 2026 年初）。从近期的提交记录看，它正在被积极地集成和调整到主引擎代码流中（如解决合并冲突、适配其他模块的 API 废弃）。尽管它处于早期和实验阶段，但其活动表明 Epic Games 内部正在使用和开发它。**推荐在新的、需要高级音频功能且接受实验性 API 变化的项目中谨慎尝试**。不建议用于需要长期稳定性的生产项目，因为其 API 和功能可能在未来版本中发生重大更改。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)