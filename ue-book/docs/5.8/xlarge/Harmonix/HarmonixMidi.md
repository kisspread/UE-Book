# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 和声音乐套件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音乐数据资产、MIDI文件、示例内容） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件是一套专为虚幻引擎设计的、功能完备的音乐与音频处理工具集。它主要解决游戏开发中**精确音乐同步、音乐数据解析与交互**的核心需求。该插件的核心功能是解析标准MIDI文件，并将MIDI数据转换为游戏可用的音乐结构化信息，包括节奏（Tempo）、拍号（Time Signature）、小节（Bar）、拍子（Beat）、和弦（Chord）和歌曲段落（Section）。这些结构化信息可以用来驱动游戏中的音乐交互、可视化、节奏事件和动态音乐系统。此外，插件还包含底层的DSP处理和MetaSound集成模块，用于更复杂的音频合成与处理场景。

## 使用场景

- 你在开发一款**音乐节奏游戏**（如音游），需要精确知道当前音乐的位置、拍子类型（强拍、弱拍）以判定玩家输入 → 使用 `FBeatMap` 和 `FMidiSongPos`
- 你的游戏拥有**动态音乐系统**，需要根据游戏事件（如进入战斗、发现秘密）切换到音乐的特定段落（如副歌、间奏） → 使用 `FSectionMap`
- 你需要从MIDI文件中提取**和弦进行信息**，用于驱动游戏内的视觉特效或音乐生成算法 → 使用 `FChordProgressionMap`
- 你的项目需要处理MIDI控制器输入，或者需要将游戏逻辑映射到MIDI控制消息上 → 使用 `FMidiMsg` 和 `EControllerID`
- 你希望在MetaSound图表中直接使用MIDI数据来驱动音高、音量或其他参数 → 使用 `HarmonixMetasound` 模块中的节点

## 蓝图用法

Harmonix 插件提供了丰富的蓝图函数库和结构体，用于在蓝图中处理音乐数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeSongPosFromTime` | 根据时间、BPM和拍号创建一个MIDI歌曲位置 | `UMidiSongPosFunctionLibrary` |
| `LerpSongPos` | 在两个MIDI歌曲位置之间进行线性插值 | `UMidiSongPosFunctionLibrary` |
| `TickToMusicTimestamp` | 将MIDI Tick转换为音乐时间戳（小节.拍） | `FBarMap` |
| `MusicTimestampToTick` | 将音乐时间戳（小节.拍）转换为MIDI Tick | `FBarMap` |
| `GetTempoAtTick` | 获取指定Tick位置的BPM | `ISongMapEvaluator` (通过 `FSongMaps` 访问) |
| `GetTimeSignatureAtTick` | 获取指定Tick位置的拍号 | `ISongMapEvaluator` (通过 `FSongMaps` 访问) |
| `GetChordNameAtTick` | 获取指定Tick位置的和弦名称 | `ISongMapEvaluator` (通过 `FSongMaps` 访问) |
| `GetSectionNameAtTick` | 获取指定Tick位置的歌曲段落名称 | `ISongMapEvaluator` (通过 `FSongMaps` 访问) |
| `CalcPositionInSpan` | 计算当前播放位置在一个定义好的音乐时间跨度（如4小节）内的归一化进度 | `FMusicalTimeSpan` |

### 使用示例（蓝图描述）

1.  **查询当前歌曲信息**：
    - 从你的 `UMidiFile` 资产或运行时生成的 `FSongMaps` 获取句柄。
    - 使用 “Get Song Maps” 节点获取 `FSongMaps` 结构体。
    - 将 `FSongMaps` 拖入图表，然后从中拉出连线，你会看到诸如 `Get Tempo At Tick`、`Get Time Signature At Tick` 等查询节点。
    - 连接一个 `FMidiSongPos`（通常来自音乐播放组件）的 `TicksIncludingCountIn` 属性到这些查询节点的 `Tick` 输入。
    - 输出的 `FTimeSignature` 结构体将包含 `Numerator` 和 `Denominator` 属性，代表当前的拍号。

2.  **判断是否在强拍上**：
    - 使用 `Get Beat Type At Tick` 节点，输入当前的 Tick。
    - 返回值 `EMusicalBeatType` 可以与 `Strong` 或 `Downbeat` 枚举值进行比较，用于触发与节奏同步的视觉效果。

## C++ 用法

Harmonix 的 C++ API 强大且直接，核心是围绕 `FSongMaps` 和 `ISongMapEvaluator` 展开的查询系统。

### 头文件引入

```cpp
#include "HarmonixMidi/SongMaps.h"
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixMidi/MidiSongPos.h"
```

### 基本用法

以下示例展示了如何加载一个MIDI文件并查询其基本信息。
**来源文件**: `HarmonixMidi/MidiFile.h`, `HarmonixMidi/SongMaps.h`

```cpp
// 假设你已经有了一个加载好的 UMidiFile* MidiFileAsset
UMidiFile* MidiFileAsset = LoadObject<UMidiFile>(nullptr, TEXT("/Game/Music/MySong.MySong"));
if (!MidiFileAsset) return;

// 获取内部的 SongMaps 数据，它包含了所有解析出的音乐结构
const FSongMaps* SongMaps = MidiFileAsset->GetSongMaps();
if (!SongMaps || SongMaps->IsEmpty()) return;

// 1. 查询歌曲的总长度（以Tick为单位）
int32 SongLengthTicks = SongMaps->GetSongLengthData().LengthTicks;
UE_LOG(LogTemp, Log, TEXT("Song length: %d ticks"), SongLengthTicks);

// 2. 查询在 Tick 1920 位置的 BPM（假设 TicksPerQuarterNote 为 960，那么 1920 大约是两个拍子）
float BPMAtTick1920 = SongMaps->GetTempoMap().GetTempoAtTick(1920);
UE_LOG(LogTemp, Log, TEXT("BPM at tick 1920: %.2f"), BPMAtTick1920);

// 3. 查询在 Tick 960 位置的和弦
FName ChordNameAtTick960 = SongMaps->GetChordMap().GetChordNameAtTick(960);
UE_LOG(LogTemp, Log, TEXT("Chord at tick 960: %s"), *ChordNameAtTick960.ToString());
```

### 进阶用法

结合 `FMidiSongPos` 和 `FMidiCursor` 进行实时歌曲位置跟踪和MIDI事件处理。
**来源文件**: `HarmonixMidi/MidiSongPos.h`, `HarmonixMidi/MidiCursor.h`

```cpp
// 假设有一个持续更新的 FMidiSongPos CurrentPos
FMidiSongPos CurrentPos;
// 假设 SongMaps 是有效的
const ISongMapEvaluator* Evaluator = SongMaps; // ISongMapEvaluator 是 SongMaps 的基类接口

// 更新歌曲位置（基于实时毫秒数）
CurrentPos.SetByTime(CurrentAudioPlaybackTimeMs, *Evaluator);

// 现在可以查询当前位置的音乐信息
if (CurrentPos.IsValid())
{
    // 是否在强拍？
    EMusicalBeatType BeatType = CurrentPos.BeatType;
    bool bIsOnStrongBeat = (BeatType == EMusicalBeatType::Downbeat || BeatType == EMusicalBeatType::Strong);

    // 获取当前和弦
    const FChordMapPoint* CurrentChord = Evaluator->GetChordAtTick(CurrentPos.TicksIncludingCountIn);
    if (CurrentChord)
    {
        FName Chord = CurrentChord->Name;
        // 触发与当前和弦相关的游戏逻辑...
    }
}

// 使用 FMidiCursor 处理 MIDI 事件流
FMidiCursor Cursor;
Cursor.Prepare(MidiFileAsset); // 关联一个 UMidiFile

// 在一个接收器中处理 MIDI 事件
class FMyMidiReceiver : public FMidiCursor::FReceiver
{
    virtual void OnMidiMessage(int32 TrackIndex, int32 Tick, uint8 Status, uint8 Data1, uint8 Data2, bool bIsPreroll) override
    {
        if (Harmonix::Midi::Constants::IsNoteOn(Status))
        {
            // 处理音符开启事件...
        }
    }
};

FMyMidiReceiver Receiver;
// 假设有一个 Tick 范围需要处理 (例如，根据游戏帧更新的音乐范围)
int32 StartTick = /* ... */;
int32 EndTick = /* ... */;
Cursor.Process(StartTick, EndTick, Receiver);
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何使用 `FSongMaps` 查询音乐信息。

```cpp
// MyMusicHelper.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "HarmonixMidi/SongMaps.h"
#include "MyMusicHelper.generated.h"

UCLASS(BlueprintType)
class UMyMusicHelper : public UObject
{
    GENERATED_BODY()

public:
    /** 使用一个已经包含SongMaps的MIDI文件数据来初始化助手 */
    UFUNCTION(BlueprintCallable, Category = "Music")
    void InitializeWithSongMaps(const FSongMaps& InSongMaps);

    /** 查询指定Tick（音乐时间）的BPM */
    UFUNCTION(BlueprintPure, Category = "Music")
    float GetBPMAtTick(int32 Tick) const;

    /** 查询指定Tick的和弦名称 */
    UFUNCTION(BlueprintPure, Category = "Music")
    FName GetChordNameAtTick(int32 Tick) const;

    /** 查询指定Tick是否是小节的第一拍（Downbeat） */
    UFUNCTION(BlueprintPure, Category = "Music")
    bool IsDownbeatAtTick(int32 Tick) const;

private:
    // 持有对音乐数据的引用
    TSharedPtr<FSongMaps> SongMaps;
};
```

```cpp
// MyMusicHelper.cpp
#include "MyMusicHelper.h"

void UMyMusicHelper::InitializeWithSongMaps(const FSongMaps& InSongMaps)
{
    // 拷贝一份SongMaps数据
    SongMaps = MakeShared<FSongMaps>(InSongMaps);
}

float UMyMusicHelper::GetBPMAtTick(int32 Tick) const
{
    if (!SongMaps.IsValid())
    {
        return 0.0f;
    }
    // 通过SongMaps访问TempoMap
    return SongMaps->GetTempoMap().GetTempoAtTick(Tick);
}

FName UMyMusicHelper::GetChordNameAtTick(int32 Tick) const
{
    if (!SongMaps.IsValid())
    {
        return NAME_None;
    }
    // 通过SongMaps访问ChordMap
    return SongMaps->GetChordMap().GetChordNameAtTick(Tick);
}

bool UMyMusicHelper::IsDownbeatAtTick(int32 Tick) const
{
    if (!SongMaps.IsValid())
    {
        return false;
    }
    // 通过SongMaps访问BeatMap并查询拍子类型
    EMusicalBeatType BeatType = SongMaps->GetBeatMap().GetBeatTypeAtTick(Tick);
    return (BeatType == EMusicalBeatType::Downbeat);
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，使用 `HarmonixMidi`（插件核心功能之一）时，你的模块通常需要依赖以下模块。以下是**独特**的依赖项（已省略常见的Core、Engine等）：

| 模块 | 用途 |
|---|---|
| `HarmonixMidi` | 核心MIDI解析、音乐数据结构（SongMaps， BarMap， TempoMap等） |
| `MetasoundFrontend` | 如果你需要将Harmonix集成到MetaSound图表中 |
| `Quartz` | 提供 `EQuartzCommandQuantization` 枚举，用于音乐时间量化 |

**注意**：`HarmonixDsp` 和 `HarmonixMetasound` 等模块还有更具体的依赖（如 `AudioMixer`， `SignalProcessing`），如果你只使用MIDI相关功能，通常无需依赖它们。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复音频融合系统中KeyZone排序问题并增加空指针防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与FSoundWaveData API废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ... | 为FusionPatch代理添加用户对象，用于追踪关联活动 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复64位参数使用32位格式说明符的问题，反之亦然 |

### 维护评价

**综合评价：积极维护中，但处于实验性阶段。**

- **创建时间**：2024年1月，是一个相对较新的插件。
- **近期更新**：从git日志看，在2026年5月仍有活跃的提交，内容涉及功能修复、API调整和代码健壮性改进，表明该插件正在被积极使用和维护。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion` 标记为 `true`，且 `EnabledByDefault` 为 `false`。这意味着该插件的API在未来版本中可能会发生**不兼容的更改**，需要手动在项目中启用。
- **已知限制**：作为实验性插件，其API稳定性是一个主要限制。此外，完整的音频DSP和MetaSound集成可能需要更复杂的配置。
- **推荐使用**：**推荐在新项目中谨慎使用**。如果你的项目严重依赖精确的MIDI音乐同步和分析，并且你愿意接受未来可能的API变更，那么这是一个非常强大和必要的工具。对于需要长期稳定API的商业项目，建议密切跟踪其版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)