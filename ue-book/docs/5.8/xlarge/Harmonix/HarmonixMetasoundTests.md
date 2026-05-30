# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 和声音乐套件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例、测试） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件是一个专门为 **音乐节奏同步、高级音频处理（DSP）和 MIDI 事件触发** 设计的综合工具集。它源于知名音乐游戏开发商 Harmonix 的技术积累，旨在为 UE5 提供一套强大的、面向音乐驱动型游戏的运行时解决方案。

该插件的核心价值在于解决以下问题：
1.  **精确的音乐时钟与节奏同步**：提供一个高精度的音乐时钟系统，用于同步游戏逻辑（如音符下落、特效触发）与音频播放。
2.  **动态音乐系统**：支持通过 MIDI 或自定义逻辑来控制音乐的层叠、过渡和交互，实现“互动音乐”。
3.  **高级音频处理**：提供一系列 DSP 节点和功能，用于实时分析、处理和合成音频。
4.  **MetaSound 扩展**：为 UE 的 MetaSound 系统注入专业的音乐音频节点（如音序器、节奏触发器）。

它主要面向 **音乐节奏游戏（如《摇滚乐队》、《吉他英雄》类型）、需要动态配乐的互动游戏、以及任何需要精确音频分析或音乐驱动视觉效果的项目**。

## 使用场景

-   **你正在开发一款音乐节奏游戏** → 使用 `Harmonix` 模块的 `HarmonixDriver` 和 `MusicClock` 来同步玩家输入与背景音乐中的音符轨道。
-   **你需要创建一个根据玩家行为或游戏状态动态变化的配乐** → 使用 `HarmonixMidi` 解析 MIDI 文件，并结合 `HarmonixMetasound` 中的节点，在 MetaSound 图中控制不同音轨的播放和混合。
-   **你需要实时分析游戏中的音频信号（如频谱、响度）** → 使用 `HarmonixDsp` 中提供的 DSP 节点或工具。
-   **你想要在 MetaSound 中创建一个基于音乐节拍或小节的步进音序器** → 使用 `HarmonixMetasound` 提供的自定义 MetaSound 节点。

## 蓝图用法

由于插件包含多个子模块，以下蓝图节点分散在不同的类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMidiStream` | 从一个 MIDI 文件资产创建一个可读取的 MIDI 事件流。 | `UMidiStreamBlueprintLibrary` |
| `TickHarmonixDriver` | 每帧调用，驱动整个 Harmonix 音乐系统的核心时钟和事件更新。 | `UHarmonixDriverBlueprintLibrary` |
| `GetSongPos` | 获取当前精确的歌曲位置（小节、节拍、细分）。 | `UMusicClockBlueprintLibrary` |
| `AddMidiStreamLogger` | 将一个 MIDI 输出流连接到调试日志记录器，用于分析 MIDI 事件。 | `UHarmonixMetasoundFunctionalTestLibrary` |
| `SetAudioParameter` | （测试用）设置一个音频参数，用于触发 MetaSound 中的逻辑。 | `UHarmonixMetasoundFunctionalTestActionSetAudioParameter` |

### 使用示例（蓝图描述）

1.  **初始化音乐时钟**：
    *   在游戏开始时（例如 `Event BeginPlay`），调用 `Create Harmonix Driver` 节点来实例化一个驱动。
    *   使用 `Start Song` 节点，传入一个 `MidiStream`（通常从 MIDI 文件资产创建）和一个 `Sound Wave` 来启动播放。

2.  **同步游戏逻辑**：
    *   创建一个自定义事件（如 `OnBeat`）。
    *   在图表中，使用 `Bind Event to On Beat` 节点，将 `OnBeat` 事件绑定到 `HarmonixDriver` 的 `OnBeat` 委托上。
    *   当音乐播放到每个节拍时，`OnBeat` 事件会自动触发，你可以在其中放置生成音符的逻辑。

3.  **控制动态音轨**：
    *   在 MetaSound 图中，使用 `HarmonixMetasound` 提供的节点（如 `Midi Step Sequencer`）。
    *   通过蓝图中的 `Set Audio Parameter` 节点，将游戏状态（如“战斗状态强度”）转化为一个浮点值，输入到 MetaSound 中，控制不同音轨的音量或触发。

## C++ 用法

### 头文件引入

根据你使用的子模块，引入相应的头文件。

```cpp
// 核心驱动
#include "Harmonix/HarmonixDriver.h"
// 音乐时钟
#include "Harmonix/HarmonixMusicClock.h"
// MIDI 处理
#include "HarmonixMidi/Blueprint/MidiStreamBlueprintLibrary.h"
// DSP 功能
#include "HarmonixDsp/HarmonixDsp.h"
```

### 基本用法

以下是一个初始化 Harmonix 系统并获取歌曲位置的基础示例。

**来源参考**: `Source/Harmonix/Public/Harmonix/HarmonixDriver.h`, 测试用例

```cpp
#include "Harmonix/HarmonixDriver.h"

// 在你的 Actor 或 Component 中
void AMyMusicDrivenActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建 Harmonix 驱动实例
    HarmonixDriver = NewObject<UHarmonixDriver>(this);

    // 2. 准备 MIDI 流和音频源
    UMidiStream* MyMidiStream = UMidiStreamBlueprintLibrary::LoadMidiFileAsMidiStream(TEXT("/Game/Audio/Music/MainTheme"));
    USoundWave* MySoundWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/Audio/Music/MainTheme"));

    if (HarmonixDriver && MyMidiStream && MySoundWave)
    {
        // 3. 初始化并启动驱动
        HarmonixDriver->InitializeWithMidiStreamAndSoundWave(MyMidiStream, MySoundWave);
        HarmonixDriver->Play();
    }
}

void AMyMusicDrivenActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 4. 每帧更新驱动，推进音乐时钟
    if (HarmonixDriver)
    {
        HarmonixDriver->Advance(DeltaTime);

        // 5. 获取当前歌曲位置
        const FMidiSongPos& CurrentPos = HarmonixDriver->GetSongPos();
        // CurrentPos 包含 Bar, Beat, TimeMs 等信息
    }
}
```

### 进阶用法

绑定回调函数以响应 MIDI 事件。

**来源参考**: 测试用例 `HarmonixMetasoundFunctionalTest`

```cpp
// 在你的类头文件中声明回调函数
DECLARE_DELEGATE_OneParam(FOnMidiEvent, const FMidiEvent&);

// 在初始化后绑定
void AMyActor::BindToMidiEvents()
{
    if (HarmonixDriver)
    {
        HarmonixDriver->GetMidiStream()->OnMidiEvent.AddUObject(this, &AMyActor::HandleMidiEvent);
    }
}

void AMyActor::HandleMidiEvent(const FMidiEvent& Event)
{
    // 处理接收到的 MIDI 事件，例如 Note On
    if (Event.GetEventType() == EMidiEventType::NoteOn)
    {
        // 触发游戏中的音符生成或特效
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何使用核心驱动来同步音乐和游戏逻辑。

**MyMusicSyncActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Harmonix/HarmonixDriver.h"
#include "MyMusicSyncActor.generated.h"

UCLASS()
class MYGAME_API AMyMusicSyncActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyMusicSyncActor();

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY()
	TObjectPtr<UHarmonixDriver> HarmonixDriver;

	// 用于接收节拍事件的委托
	FDelegateHandle BeatDelegateHandle;
	
	void OnMusicBeat(int32 CurrentBar, int32 CurrentBeat);
};
```

**MyMusicSyncActor.cpp**
```cpp
#include "MyMusicSyncActor.h"
#include "Harmonix/HarmonixDriver.h"

AMyMusicSyncActor::AMyMusicSyncActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMyMusicSyncActor::BeginPlay()
{
	Super::BeginPlay();

	// 创建驱动
	HarmonixDriver = NewObject<UHarmonixDriver>(this);

	// 加载资源 (请确保路径正确)
	UObject* MidiObj = LoadObject<UObject>(nullptr, TEXT("/Game/Audio/TestMidi"));
	UMidiStream* MidiStream = Cast<UMidiStream>(MidiObj);
	USoundWave* SoundWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/Audio/TestSound"));

	if (HarmonixDriver && MidiStream && SoundWave)
	{
		// 初始化
		HarmonixDriver->InitializeWithMidiStreamAndSoundWave(MidiStream, SoundWave);

		// 绑定节拍事件
		BeatDelegateHandle = HarmonixDriver->GetMusicClock()->OnBeat.AddUObject(this, &AMyMusicSyncActor::OnMusicBeat);

		// 开始播放
		HarmonixDriver->Play();
	}
}

void AMyMusicSyncActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (HarmonixDriver && HarmonixDriver->IsPlaying())
	{
		// 关键：每帧推进驱动
		HarmonixDriver->Advance(DeltaTime);
	}
}

void AMyMusicSyncActor::OnMusicBeat(int32 CurrentBar, int32 CurrentBeat)
{
	// 在这里响应节拍！
	// 例如，生成一个音符 Actor
	UE_LOG(LogTemp, Log, TEXT("Beat! Bar: %d, Beat: %d"), CurrentBar, CurrentBeat);
	// SpawnBeatNote();
}
```

## 模块依赖

`Harmonix` 插件本身包含多个模块，你**不需要**直接依赖所有模块。根据你的需求，选择性地添加依赖。以下是除通用模块（Core, Engine等）外，一些值得注意的独特依赖：

| 模块 | 用途 |
|---|---|
| `MIDIDriver` | 提供低层的 MIDI 设备输入/输出支持。`HarmonixMidi` 依赖它。 |
| `MetasoundFrontend`, `MetasoundEngine` | MetaSound 系统的前端和核心引擎。`HarmonixMetasound` 依赖它们来扩展节点。 |
| `AudioMixerXAudio2` (或其他平台音频后端) | 音频混音器的平台实现。Harmonix 的 DSP 和音频播放功能可能需要底层的音频混音器支持。 |
| `FunctionalTesting` | UE 的自动化/功能测试框架。`Harmonix*Tests` 模块依赖它来实现测试逻辑。 |

**简单策略**：如果你只想要音乐时钟和基础 MIDI 功能，依赖 `Harmonix` 和 `HarmonixMidi`。如果你要创建自定义的音乐 MetaSound，依赖 `HarmonixMetasound`。具体的依赖关系请参考各子模块的 `Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音色库中按键区域排序和空指针防御。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associations. | 为 FusionPatch 代理添加用户对象，可用于跟踪关联活动。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa. | 修正了64位参数使用32位格式说明符的问题。 |

### 维护评价

-   **创建时间**：2024年1月，至今约1年半。
-   **近期活动**：最近的提交（2026年5月）集中在**编译警告修复、API 适配和底层 DSP/音色库的 bug 修复**，没有看到新功能特性的提交。
-   **维护状态**：**活跃维护，但处于稳定期**。从 GitHub 提交记录看，团队仍在持续维护代码，修复问题，确保其与引擎新版本的兼容性。但从功能性更新来看，当前版本已相对稳定。
-   **已知限制**：该插件默认未启用 (`EnabledByDefault: false`) 且标记为**实验性** (`IsExperimentalVersion: true`)。这意味着 Epic 官方认为其 API 可能发生变化，不建议在面向用户发布的正式项目中作为核心基础使用。
-   **推荐度**：**对于原型开发、内部工具或愿意承担 API 变动风险的团队，推荐使用**。它提供了 UE5 内置的、开箱即用的高级音乐同步功能，是目前引擎内最完整的方案。对于追求稳定性的商业项目，建议密切关注其版本更新，或考虑将其作为参考来实现自己的轻量级方案。

**警告**：该插件为实验性状态，API 和行为可能在未来的引擎版本中发生破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 官方文档：（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests) （示例）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests) （示例）