# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 低频音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个处于实验阶段的高级音频引擎系统。它并非用于简单的音效播放，而是旨在为开发者提供一套程序化、数据驱动的音频创作与回放框架。其核心目标是解决复杂动态音频场景（如交互式音乐、环境音效景观、参数化音频生成）的创作和管理难题，让音频设计能更紧密地与游戏逻辑集成。

## 使用场景

- 你需要为一个开放世界游戏创建一个能根据玩家行为、位置、天气和时间动态变化的复杂环境音效系统。
- 你正在开发一款音乐游戏，需要程序化地生成、混合和变换音乐片段，而非播放预录制的完整音轨。
- 你希望音频设计师能使用一种高层的、基于节点的工具来创作可交互的音频逻辑，并能在运行时由游戏代码驱动。
- 你想尝试使用 Epic Games 提供的最新实验性音频技术栈。

## 蓝图用法

由于该插件仍处于实验阶段，其公开的蓝图 API 可能在未来版本中发生重大变更。以下功能基于当前源码结构推断。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Subsonic Audio Asset` | 创建一个新的 Subsonic 音频资产实例，作为后续操作的对象。 | `USubsonicSubsystem` (推测) |
| `Set Parameter` | 设置音频资产上的一个命名参数（如音量、音高、滤波器截止频率等），用于运行时控制。 | `USubsonicAudioAsset` (推测) |
| `Play` | 在指定的音频通道或虚拟源上播放一个 Subsonic 音频资产。 | `USubsonicSubsystem` (推测) |
| `Stop` | 停止正在播放的特定 Subsonic 音频实例。 | `USubsonicSubsystem` (推测) |

### 使用示例（蓝图描述）

1.  **创建动态背景音**：在游戏开始时，通过一个 `BeginPlay` 事件，调用“Create Subsonic Audio Asset”节点创建一个名为“DynamicAmbience”的资产。随后，使用一个“Set Parameter”节点，将其“WindIntensity”参数绑定到一个游戏变量（如玩家所处环境的风速）。最后调用“Play”节点开始播放。在游戏中，随着玩家位置变化导致风速改变，通过事件不断更新该参数，背景音效将实时变化。
2.  **程序化音乐生成**：创建一个包含多个音乐“层次”（如打击乐、旋律、和声）的 Subsonic 资产。使用蓝图逻辑根据游戏进程（如战斗状态、探索状态）分别控制不同层次的“Volume”或“Mute”参数，实现音乐的动态层叠与过渡。

## C++ 用法

**重要提示**：由于插件的实验性质，以下 API 可能在未来的引擎版本中被修改或移除。使用前请确认当前引擎版本对应的头文件。

### 头文件引入

```cpp
#include "SubsonicCore.h"
#include "SubsonicEngine.h"
```

### 基本用法
以下示例展示如何创建并操作一个 Subsonic 音频资产。
*（来源：基于对测试模块 `SubsonicEngineTest` 的用法推断）*

```cpp
// 在某个 Actor 或 Subsystem 中
#include "SubsonicSubsystem.h" // 假设的子系统头文件

void AMyActor::SetupDynamicAudio()
{
    // 获取 Subsonic 子系统
    USubsonicSubsystem* SubsonicSub = GetWorld()->GetSubsystem<USubsonicSubsystem>();
    if (!SubsonicSub) return;

    // 创建一个音频资产实例
    USubsonicAudioAsset* AudioAsset = SubsonicSub->CreateAudioAsset(TEXT("MyDynamicSound"));
    if (AudioAsset)
    {
        // 设置初始参数
        AudioAsset->SetParameter(TEXT("Volume"), 1.0f);
        AudioAsset->SetParameter(TEXT("Pitch"), 1.0f);
        AudioAsset->SetParameter(TEXT("FilterCutoff"), 2000.0f);

        // 在某个音频虚拟源上播放
        SubsonicSub->PlayAudioAsset(AudioAsset, AudioVirtualSourceHandle);
    }
}

// 在游戏逻辑更新中
void AMyActor::UpdateAudioBasedOnGameplay(float DistanceToPlayer)
{
    if (USubsonicSubsystem* SubsonicSub = GetWorld()->GetSubsystem<USubsonicSubsystem>())
    {
        if (USubsonicAudioAsset* AudioAsset = /* 持有之前创建的资产引用 */)
        {
            // 根据与玩家的距离更新滤波器参数，模拟声音随距离衰减变闷
            float FilterValue = FMath::Clamp(10000.0f - (DistanceToPlayer * 50.0f), 500.0f, 10000.0f);
            AudioAsset->SetParameter(TEXT("FilterCutoff"), FilterValue);
        }
    }
}
```

### 进阶用法
结合多个资产和事件，构建一个响应式的音频环境。
*（来源：基于测试模块可能验证的场景推断）*

```cpp
void AMyGameMode::InitializeAudioSystem()
{
    USubsonicSubsystem* SubsonicSub = GetWorld()->GetSubsystem<USubsonicSubsystem>();

    // 为不同的游戏状态创建不同的音频资产
    USubsonicAudioAsset* ExploreMusic = SubsonicSub->CreateAudioAsset(TEXT("ExploreMusic"));
    USubsonicAudioAsset* CombatMusic = SubsonicSub->CreateAudioAsset(TEXT("CombatMusic"));

    // 将它们注册为可切换的音频层
    SubsonicSub->RegisterAudioLayer(TEXT("Music"), ExploreMusic);

    // 当游戏状态变为“战斗”时
    // SubsonicSub->SwitchAudioLayerAsset(TEXT("Music"), CombatMusic);
    // 或者交叉渐变
    // SubsonicSub->CrossfadeToAsset(TEXT("Music"), CombatMusic, 2.0f);
}
```

## Demo 示例

一个最小化示例，展示如何集成 Subsonic 子系统来播放一个可参数控制的音频。

### MySubsonicDemoActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySubsonicDemoActor.generated.h"

class USubsonicAudioAsset;
class USubsonicSubsystem;

UCLASS()
class MYPROJECT_API AMySubsonicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMySubsonicDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // 蓝图可调用的函数，用于调整音频参数
    UFUNCTION(BlueprintCallable, Category = "Subsonic Demo")
    void AdjustFilterCutoff(float NewCutoff);

private:
    UPROPERTY()
    USubsonicAudioAsset* AudioAssetInstance;

    UPROPERTY()
    USubsonicSubsystem* SubsonicSubsystem;

    float CurrentFilterCutoff = 5000.0f;
};
```

### MySubsonicDemoActor.cpp
```cpp
#include "MySubsonicDemoActor.h"
#include "SubsonicSubsystem.h"
#include "SubsonicAudioAsset.h" // 假设的资产头文件

AMySubsonicDemoActor::AMySubsonicDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMySubsonicDemoActor::BeginPlay()
{
    Super::BeginPlay();

    SubsonicSubsystem = GetWorld()->GetSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem)
    {
        // 创建音频资产
        AudioAssetInstance = SubsonicSubsystem->CreateAudioAsset(TEXT("DemoTone"));
        if (AudioAssetInstance)
        {
            // 设置一个基础音
            AudioAssetInstance->SetParameter(TEXT("WaveType"), 0.0f); // 例如，0=正弦波
            AudioAssetInstance->SetParameter(TEXT("Frequency"), 440.0f);
            AudioAssetInstance->SetParameter(TEXT("FilterCutoff"), CurrentFilterCutoff);
            AudioAssetInstance->SetParameter(TEXT("Volume"), 0.5f);

            // 开始播放
            SubsonicSubsystem->PlayAudioAsset(AudioAssetInstance);
        }
    }
}

void AMySubsonicDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 可以在这里做一些连续的音频更新
}

void AMySubsonicDemoActor::AdjustFilterCutoff(float NewCutoff)
{
    if (AudioAssetInstance)
    {
        CurrentFilterCutoff = FMath::Clamp(NewCutoff, 100.0f, 15000.0f);
        AudioAssetInstance->SetParameter(TEXT("FilterCutoff"), CurrentFilterCutoff);
    }
}
```

## 模块依赖

从测试模块的依赖关系和其他模块的一般职责推断，使用者可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 提供 Subsonic 系统的核心数据类型、接口和基础类。 |
| `SubsonicEngine` | 包含 Subsonic 音频引擎的具体实现、子系统和资产类型。 |
| `AudioMixer` | 提供底层音频混合和流处理能力，Subsonic 引擎可能基于此构建。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了一次错误的合并，撤销了对 Subsonic 订阅者的全面覆盖，并应用了最小化的非废弃修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了源代码分析工具（PVS-Studio）产生的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 为内容浏览器添加了新的音频菜单项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为 UE_LOGF。 |

### 维护评价
Subsonic 是一个**非常新且处于活跃实验阶段**的插件。从提交历史看，它在 2026 年 1 月至 5 月期间持续有更新，最近的提交集中在**解决集成问题、API 协调和代码质量改进**上，表明 Epic Games 内部正在积极使用和迭代这个系统。

**优点**：代表了 UE 音频管线的前沿方向，由 Epic 官方维护，潜力巨大。
**风险与限制**：
1.  **实验性**：明确标注为 `IsExperimentalVersion=true`，API 和功能**极有可能在未来发生破坏性变更**，甚至整个插件可能被重构或移除。
2.  **文档与支持缺失**：官方文档链接为空，完全依赖代码和测试用例，学习曲线陡峭。
3.  **生产环境慎用**：由于缺乏向后兼容性保证，不建议在需要长期稳定维护的项目中使用。

**推荐**：适合**技术预研、内部原型开发、或希望参与未来音频技术探索的团队**使用。对于商业项目，建议密切关注其发展，在它进入稳定阶段后再考虑集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)