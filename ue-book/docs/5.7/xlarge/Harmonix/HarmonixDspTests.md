# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、蓝图资产、材质模板等） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是一个由 Epic Games 旗下 Harmonix GenTech 团队开发的综合性音乐与音频处理工具包。它并非一个简单的音频播放器，而是一个为**音乐游戏、互动音乐系统和高级音频处理**设计的底层框架。其核心价值在于提供了一套完整的、可编程的工具链，用于处理 MIDI 数据、实现复杂的 DSP（数字信号处理）效果，并将这些功能与 Unreal Engine 的 MetaSound 音频图系统深度集成。它解决了在引擎内创建节奏同步、音乐驱动的游戏玩法以及实现专业级音频效果时所面临的复杂技术挑战。

## 使用场景

-   **音乐节奏游戏**：你需要精确同步游戏事件（如打击判定）与音乐节拍，并处理来自玩家输入设备的 MIDI 信号。
-   **动态音乐系统**：你希望游戏音乐能够根据游戏状态（如战斗、探索、剧情）无缝过渡、分层混合或实时变奏，而不是简单的音轨切换。
-   **音频可视化与分析**：你需要实时分析音频频谱（FFT）或波形，用于驱动游戏内的视觉效果或游戏逻辑。
-   **自定义音频效果器**：你需要在 MetaSound 图中实现自定义的、高性能的 DSP 节点，如滤波器、延迟、失真等。
-   **MIDI 设备集成**：你的项目需要连接外部 MIDI 键盘、鼓垫等设备作为输入源。

## 蓝图用法

Harmonix 提供了丰富的蓝图接口，主要集中在音乐播放控制、MIDI 事件处理和 DSP 参数调节上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Music Player` | 创建一个用于播放和控制音乐资产的播放器实例。 | `UHarmonixMusicPlayer` |
| `Play` / `Pause` / `Stop` | 控制音乐播放器的播放状态。 | `UHarmonixMusicPlayer` |
| `Set Music Speed` | 动态调整音乐播放速度，常用于实现慢动作等效果。 | `UHarmonixMusicPlayer` |
| `Get Current Song Position` | 获取当前播放位置（以小节、拍、Tick 为单位），用于同步游戏逻辑。 | `UHarmonixMusicPlayer` |
| `Bind Event to On Midi Event` | 将蓝图事件绑定到 MIDI 事件回调，用于处理来自音序器或外部设备的 MIDI 消息。 | `UHarmonixMidiEventBroadcaster` |
| `Set Filter Cutoff` / `Set Reverb Wet` | 在蓝图中动态调整 MetaSound 图中 Harmonix DSP 节点的参数。 | `UHarmonixDspEffect` |

### 使用示例（蓝图描述）

1.  **创建音乐播放器**：在角色蓝图中，使用 `Create Music Player` 节点创建一个播放器变量。
2.  **播放音乐并同步**：调用 `Play` 节点开始播放。使用 `Get Current Song Position` 节点获取当前拍子，并与一个定时器或 Tick 事件结合，实现每拍触发一次游戏逻辑（如生成音符）。
3.  **处理 MIDI 输入**：将 `Bind Event to On Midi Event` 节点绑定到自定义事件。在该事件中，通过 `Midi Event Data` 结构体判断音符编号和力度，从而触发角色跳跃或攻击等操作。

## C++ 用法

### 头文件引入

```cpp
// 核心音乐播放功能
#include "Harmonix/HarmonixMusicPlayer.h"
// MIDI 事件处理
#include "HarmonixMidi/HarmonixMidiEventBroadcaster.h"
// DSP 效果控制
#include "HarmonixDsp/HarmonixDspEffect.h"
```

### 基本用法

以下示例展示了如何创建和控制一个音乐播放器，来源于 `HarmonixTests` 模块中的测试用例。

```cpp
// 来源: Engine/Plugins/Runtime/Harmonix/Source/HarmonixTests/Private/HarmonixMusicPlayerTests.cpp
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建音乐播放器实例
    UHarmonixMusicPlayer* MusicPlayer = NewObject<UHarmonixMusicPlayer>(this);
    MusicPlayer->Initialize(MyMusicAsset); // MyMusicAsset 是一个 UHarmonixMusicAsset

    // 2. 设置播放参数并开始播放
    MusicPlayer->SetMusicSpeed(1.0f);
    MusicPlayer->Play();

    // 3. 绑定节拍同步回调
    MusicPlayer->OnBeat.AddDynamic(this, &AMyActor::OnMusicBeat);
}

void AMyActor::OnMusicBeat(int32 BeatNumber, float BeatTime)
{
    // 在每个音乐拍子上执行游戏逻辑
    UE_LOG(LogTemp, Log, TEXT("Beat %d at time %f"), BeatNumber, BeatTime);
    SpawnBeatVisual();
}
```

### 进阶用法

结合 MIDI 事件广播器和 DSP 效果，实现一个响应 MIDI 输入并应用实时效果的系统。

```cpp
// 结合 HarmonixMidiEventBroadcaster 和 HarmonixDspEffect
void AMyActor::SetupMidiDrivenAudio()
{
    // 假设我们已经有一个 MetaSound 资产，其中包含 Harmonix 的滤波器节点
    UMetaSoundSource* MyMetaSound = ...;
    UHarmonixDspEffect* DspEffect = NewObject<UHarmonixDspEffect>(this);
    DspEffect->Initialize(MyMetaSound, FName("FilterNode")); // “FilterNode”是MetaSound图中的节点名

    // 创建 MIDI 事件广播器
    UHarmonixMidiEventBroadcaster* MidiBroadcaster = NewObject<UHarmonixMidiEventBroadcaster>(this);
    MidiBroadcaster->OnMidiEvent.AddDynamic(this, &AMyActor::HandleMidiEvent);

    // 在事件处理函数中，根据 MIDI 音符控制 DSP 参数
    void AMyActor::HandleMidiEvent(const FMidiEvent& Event)
    {
        if (Event.GetEventType() == EMidiEventType::NoteOn)
        {
            // 将 MIDI 音符编号映射到滤波器截止频率 (例如: 音符 60 (C4) -> 1000Hz)
            float CutoffHz = FMath::GetMappedRangeValueClamped(
                FVector2D(0, 127), // MIDI 音符范围
                FVector2D(100.0f, 10000.0f), // 频率范围
                Event.GetNoteNumber()
            );
            DspEffect->SetParameter(FName("Cutoff"), CutoffHz);
        }
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个简单的音乐播放器并响应节拍。

**MyHarmonixActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Harmonix/HarmonixMusicPlayer.h"
#include "MyHarmonixActor.generated.h"

UCLASS()
class MYPROJECT_API AMyHarmonixActor : public AActor
{
    GENERATED_BODY()

public:
    AMyHarmonixActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Harmonix")
    UHarmonixMusicAsset* MusicAsset;

    UPROPERTY()
    UHarmonixMusicPlayer* MusicPlayer;

    UFUNCTION()
    void OnMusicBeat(int32 BeatNumber, float BeatTime);
};
```

**MyHarmonixActor.cpp**
```cpp
#include "MyHarmonixActor.h"

AMyHarmonixActor::AMyHarmonixActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyHarmonixActor::BeginPlay()
{
    Super::BeginPlay();

    if (MusicAsset)
    {
        MusicPlayer = NewObject<UHarmonixMusicPlayer>(this);
        MusicPlayer->Initialize(MusicAsset);
        MusicPlayer->OnBeat.AddDynamic(this, &AMyHarmonixActor::OnMusicBeat);
        MusicPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("Harmonix Music Player Started."));
    }
}

void AMyHarmonixActor::OnMusicBeat(int32 BeatNumber, float BeatTime)
{
    // 在此处添加你的节拍同步逻辑
    UE_LOG(LogTemp, Log, TEXT("Beat!"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HarmonixDsp` | 提供核心的数字信号处理（DSP）算法和效果器节点。 |
| `HarmonixMidi` | 提供 MIDI 文件解析、事件处理和设备通信功能。 |
| `HarmonixMetasound` | 将 Harmonix 的功能（如音乐播放器、DSP 节点）封装为 MetaSound 节点，实现音频图集成。 |
| `MetaSound` | (引擎模块) HarmonixMetasound 的基础，用于构建和运行 MetaSound 图。 |

## 维护状态

### 近期更新

```
- a19cbe90c917 AdsrTests Unit Tests to confirm I haven't broken anything with the Harmonix ADSR settings
- 36c92c5ef56d [Harmonix] FFT Analyzer: Use FAlignedFloatBuffer instead of TAudioBuffer<float>
- 58b4b212c553 [Harmonix] Remove waveform analyzer #rb jake.burga
```

### 维护评价

Harmonix 插件创建于 2024 年初，是一个相对年轻的项目。从最近的提交记录看，团队仍在积极进行功能迭代和优化（如重构 FFT 分析器、清理代码、添加单元测试）。尽管在 `.uplugin` 中标记为 `IsExperimentalVersion: true` 且默认禁用，但其持续的更新表明它正处于**活跃开发与完善阶段**。它代表了 Epic 在互动音乐技术上的前沿探索，适合用于原型开发和实验性项目。对于生产环境项目，需要密切关注其 API 的稳定性和未来的正式发布计划。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [测试用例 (HarmonixTests)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixTests)
- [测试用例 (HarmonixDspTests)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [测试用例 (HarmonixMidiTests)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)
- [测试用例 (HarmonixMetasoundTests)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)