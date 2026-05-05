# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Harmonix Music Systems（知名音乐游戏《Rock Band》、《Guitar Hero》的开发商）开发的一套高级音乐与音频处理技术集合，现已集成到 Unreal Engine 5 中。它并非一个简单的音频播放器，而是一个为**音乐驱动型交互体验**设计的底层框架。

该插件的核心价值在于解决以下问题：
1.  **精确的音乐同步**：提供高精度的音乐时间轴和节拍跟踪，使游戏逻辑、动画、特效能够与音乐节奏（BPM）严格同步。
2.  **音乐分析**：能够实时分析音频流，提取节奏、音高等信息。
3.  **MIDI 处理**：提供完整的 MIDI 文件解析、播放和事件处理能力，是实现音乐游戏“下落音符”等玩法的关键。
4.  **与 MetaSound 集成**：将音乐处理能力深度集成到 UE5 的 MetaSound 音频图系统中，允许在可视化音频图中直接使用 Harmonix 的节点进行音乐逻辑编程。
5.  **DSP（数字信号处理）**：包含一系列专为音乐和游戏音频优化的 DSP 算法。

简而言之，如果你需要开发一个**音乐节奏游戏**、**音乐可视化应用**或任何需要**深度音乐交互**的项目，Harmonix 提供了传统音频系统无法比拟的底层控制力和精度。

## 使用场景

-   你在开发一个类似《Hi-Fi Rush》或《Beat Saber》的**音乐节奏游戏**，需要精确的节拍同步和音符判定。
-   你需要创建一个**音乐可视化**应用，让场景中的物体或粒子效果跟随音乐的节奏、音高或频谱变化。
-   你正在制作一个**交互式音乐体验**，玩家的行为（如射击、移动）可以改变或触发音乐的不同部分。
-   你需要使用 **MIDI 文件**作为游戏逻辑的驱动源，例如控制过场动画、触发事件或作为游戏输入。
-   你希望利用 **MetaSound** 的强大功能，并需要在其音频图中集成专业的音乐时间轴和节奏处理节点。

## 蓝图用法

Harmonix 提供了丰富的蓝图接口，主要通过子系统（Subsystem）和资产类暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Harmonix Subsystem` | 获取全局的 Harmonix 子系统实例，是访问大部分功能的入口。 | `UHarmonixSubsystem` |
| `Create Music Player` | 创建一个音乐播放器实例，用于播放和控制音频/音乐。 | `UHarmonixSubsystem` |
| `Load MIDI File Asset` | 加载一个 `UHarmonixMidiFileAsset` 资产。 | `UHarmonixSubsystem` |
| `Create MIDI Player` | 创建一个 MIDI 播放器实例，用于播放 MIDI 文件并接收事件。 | `UHarmonixSubsystem` |
| `Get Current Song Position` | 获取当前播放的音乐位置（以小节、拍、Tick 等单位）。 | `UHarmonixPlayer` |
| `Get Beat` | 获取当前的节拍信息（是否在拍上、拍子位置等）。 | `UHarmonixPlayer` |
| `Set Tempo` | 动态设置播放速度（BPM）。 | `UHarmonixPlayer` |
| `Bind Event to On Midi Note On` | 绑定事件到 MIDI 音符开始（Note On）消息。 | `UHarmonixMidiPlayer` |
| `Bind Event to On Midi Note Off` | 绑定事件到 MIDI 音符结束（Note Off）消息。 | `UHarmonixMidiPlayer` |

### 使用示例（蓝图描述）

1.  **基础音乐播放与节拍同步**：
    *   在 BeginPlay 中，使用 `Get Harmonix Subsystem` 节点获取子系统。
    *   调用 `Create Music Player` 创建一个播放器，并传入一个 Sound Wave 资产。
    *   调用 `Play` 开始播放。
    *   使用 `Get Beat` 节点，并将其输出的 `Is On Beat` 布尔值连接到一个 Branch 节点，用于在每个节拍上触发一个事件（如生成一个粒子效果）。

2.  **MIDI 音符事件处理**：
    *   加载一个 `UHarmonixMidiFileAsset`。
    *   使用 `Create MIDI Player` 创建一个 MIDI 播放器，并关联该资产。
    *   使用 `Bind Event to On Midi Note On` 节点，创建一个自定义事件。
    *   在该自定义事件中，从 `Midi Note On Event` 结构体中提取 `Note Number` 和 `Velocity`，根据这些信息在游戏世界中生成对应的“下落音符”Actor。

## C++ 用法

### 头文件引入

```cpp
#include "Harmonix/HarmonixSubsystem.h"
#include "HarmonixMidi/HarmonixMidiFileAsset.h"
#include "HarmonixMidi/HarmonixMidiPlayer.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个 MIDI 播放器并监听音符事件。此用法基于 `HarmonixMidiTests` 模块中的测试逻辑提炼。

```cpp
// MyMidiActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HarmonixMidi/HarmonixMidiPlayer.h"
#include "MyMidiActor.generated.h"

UCLASS()
class AMyMidiActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMidiActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // MIDI 播放器实例
    UPROPERTY()
    TObjectPtr<UHarmonixMidiPlayer> MidiPlayer;

    // MIDI 文件资产
    UPROPERTY(EditAnywhere, Category = "MIDI")
    TObjectPtr<UHarmonixMidiFileAsset> MidiFileAsset;

    // 处理 MIDI 音符开始事件的函数
    UFUNCTION()
    void OnMidiNoteOn(const FMidiNoteEvent& Event);
};
```

```cpp
// MyMidiActor.cpp
#include "MyMidiActor.h"
#include "Harmonix/HarmonixSubsystem.h"

AMyMidiActor::AMyMidiActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMidiActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取 Harmonix 子系统
    UHarmonixSubsystem* HarmonixSubsystem = UHarmonixSubsystem::Get(GetWorld());
    if (!HarmonixSubsystem || !MidiFileAsset)
    {
        return;
    }

    // 2. 创建 MIDI 播放器
    MidiPlayer = HarmonixSubsystem->CreateMidiPlayer(MidiFileAsset);
    if (MidiPlayer)
    {
        // 3. 绑定音符开始事件
        MidiPlayer->OnMidiNoteOn.AddDynamic(this, &AMyMidiActor::OnMidiNoteOn);

        // 4. 开始播放
        MidiPlayer->Play();
    }
}

void AMyMidiActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理：停止播放并解绑事件
    if (MidiPlayer)
    {
        MidiPlayer->Stop();
        MidiPlayer->OnMidiNoteOn.RemoveDynamic(this, &AMyMidiActor::OnMidiNoteOn);
    }
    Super::EndPlay(EndPlayReason);
}

void AMyMidiActor::OnMidiNoteOn(const FMidiNoteEvent& Event)
{
    // 5. 处理音符事件
    // Event.NoteNumber: MIDI 音符号 (0-127)
    // Event.Velocity: 力度 (0-127)
    // Event.Channel: MIDI 通道
    UE_LOG(LogTemp, Log, TEXT("Note On: %d, Velocity: %d"), Event.NoteNumber, Event.Velocity);
    // 在此处添加你的游戏逻辑，例如生成音符 Actor
}
```
*来源：基于 `HarmonixMidiTests` 模块中 MIDI 文件导入导出和事件处理测试的逻辑提炼。*

### 进阶用法

结合音乐播放器进行节拍同步。此用法展示了如何让游戏逻辑与音乐的 BPM 严格同步。

```cpp
// 在 BeginPlay 中创建音乐播放器
MusicPlayer = HarmonixSubsystem->CreateMusicPlayer(MySoundWave);
if (MusicPlayer)
{
    MusicPlayer->Play();
}

// 在 Tick 或定时器中检查节拍
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (MusicPlayer && MusicPlayer->IsPlaying())
    {
        // 获取当前的音乐时间信息
        const FHarmonixMusicTime& MusicTime = MusicPlayer->GetCurrentMusicTime();

        // 检查是否在当前拍的起始位置（容差范围内）
        if (MusicTime.IsOnBeat(0.1f)) // 0.1f 为容差，单位秒
        {
            // 执行节拍同步逻辑，例如闪烁灯光
            TriggerBeatEffect();
        }
    }
}
```

## Demo 示例

一个完整的最小示例，演示如何创建一个 Actor，加载 MIDI 文件，并在接收到音符事件时在日志中打印信息。

```cpp
// HarmonixDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HarmonixMidi/HarmonixMidiPlayer.h"
#include "HarmonixDemoActor.generated.h"

class UHarmonixMidiFileAsset;

UCLASS()
class AHarmonixDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AHarmonixDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "Harmonix Demo")
    TObjectPtr<UHarmonixMidiFileAsset> DemoMidiAsset;

private:
    UPROPERTY()
    TObjectPtr<UHarmonixMidiPlayer> MidiPlayer;

    UFUNCTION()
    void HandleNoteOn(const FMidiNoteEvent& Event);
};
```

```cpp
// HarmonixDemoActor.cpp
#include "HarmonixDemoActor.h"
#include "Harmonix/HarmonixSubsystem.h"
#include "HarmonixMidi/HarmonixMidiFileAsset.h"

AHarmonixDemoActor::AHarmonixDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AHarmonixDemoActor::BeginPlay()
{
    Super::BeginPlay();

    UHarmonixSubsystem* Subsystem = UHarmonixSubsystem::Get(GetWorld());
    if (Subsystem && DemoMidiAsset)
    {
        MidiPlayer = Subsystem->CreateMidiPlayer(DemoMidiAsset);
        if (MidiPlayer)
        {
            MidiPlayer->OnMidiNoteOn.AddDynamic(this, &AHarmonixDemoActor::HandleNoteOn);
            MidiPlayer->Play();
            UE_LOG(LogTemp, Log, TEXT("Harmonix Demo: MIDI Player Started."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Harmonix Demo: Missing Subsystem or MIDI Asset."));
    }
}

void AHarmonixDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MidiPlayer)
    {
        MidiPlayer->Stop();
        MidiPlayer->OnMidiNoteOn.RemoveDynamic(this, &AHarmonixDemoActor::HandleNoteOn);
    }
    Super::EndPlay(EndPlayReason);
}

void AHarmonixDemoActor::HandleNoteOn(const FMidiNoteEvent& Event)
{
    // 将 MIDI 音符号映射到音名（C4=60）
    static const TCHAR* NoteNames[] = {TEXT("C"), TEXT("C#"), TEXT("D"), TEXT("D#"), TEXT("E"), TEXT("F"), TEXT("F#"), TEXT("G"), TEXT("G#"), TEXT("A"), TEXT("A#"), TEXT("B")};
    int32 Octave = (Event.NoteNumber / 12) - 1;
    int32 NoteIndex = Event.NoteNumber % 12;
    FString NoteName = FString::Printf(TEXT("%s%d"), NoteNames[NoteIndex], Octave);

    UE_LOG(LogTemp, Log, TEXT("Harmonix Demo: Note ON - %s (Number: %d, Velocity: %d)"), *NoteName, Event.NoteNumber, Event.Velocity);
}
```

## 模块依赖

要使用 Harmonix 插件的功能，你的项目模块需要依赖以下核心模块。已省略 `Core`, `CoreUObject`, `Engine` 等通用依赖。

| 模块 | 用途 |
|---|---|
| `Harmonix` | 核心运行时模块，提供子系统、播放器等基础框架。 |
| `HarmonixMidi` | MIDI 文件解析、资产和播放器。 |
| `HarmonixDsp` | 数字信号处理算法库。 |
| `HarmonixMetasound` | 与 MetaSound 系统集成的节点和功能。 |

**注意**：`HarmonixDspEditor`, `HarmonixMidiEditor` 等以 `Editor` 结尾的模块仅用于编辑器功能，不应在运行时模块中依赖。`*Tests` 模块仅用于自动化测试。

## 维护状态

### 近期更新

```
- 64a5b0f5fd83 Fix failing Test in MidiFileImportExportTests. Expected warnings have changed
- a846cfbb1a26 [Harmonix] Test voice id roundtrip and step sequencer stuck notes
- 0a5151449c19 Fix log spam in tests
```

### 维护评价

-   **创建时间**：2024年初，是一个相对较新的插件。
-   **更新频率**：近期（基于提供的git log）有持续的提交，主要集中在**测试修复和功能验证**上（如修复测试、测试音符ID往返和步进音序器卡音问题）。这表明插件处于**活跃开发和稳定化阶段**。
-   **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，明确标记为实验性功能。这意味着其API可能在未来版本中发生变化，不建议在需要长期稳定性的核心项目中无条件使用。
-   **综合评价**：Harmonix 是一个功能强大且前沿的音乐交互框架，目前由 Epic 和 Harmonix 团队积极维护。由于其**实验性**标签，使用者应做好应对API变动的准备。它非常适合用于**原型开发、游戏jam或明确接受实验性API风险的项目**。对于追求稳定性的商业项目，建议密切关注其版本更新日志，并在升级引擎版本时进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests) (示例：MIDI 测试模块)