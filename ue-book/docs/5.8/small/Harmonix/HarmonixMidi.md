# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 和声 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MIDI资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是一个功能强大的音乐和音频处理插件包。它远不止是一个简单的MIDI文件读写工具，而是一个完整的、面向游戏和交互式音频的**音乐时间系统**。它解决了将专业音乐数据（如MIDI文件）中的时序、节奏、和弦、段落等信息，转化为游戏引擎中可实时查询和交互的、精确的时间数据（如节拍、小节、拍号、速度）的问题。

插件的核心是 `HarmonixMidi` 模块，它提供了 `FSongMaps`、`FMidiSongPos` 等核心数据结构。这些结构封装了从MIDI数据中解析出的所有音乐映射信息（速度图、节拍图、小节图、段落图、和弦进行图），并允许开发者根据时间或Tick（MIDI时间单位）精确查询任意时刻的音乐状态。这使得实现诸如音乐同步动画、精准的节奏打击判定、动态音乐段落切换等高级交互功能成为可能。

## 使用场景

-   你正在开发一个**节奏游戏**，需要精确判断玩家输入是否在“拍子”上 → 使用 `HarmonixMidi` 的 `FMidiSongPos` 获取当前精准的拍号和节拍位置。
-   你的游戏中有**动态音乐系统**，音乐需要根据游戏进度在不同段落（Verse, Chorus）之间无缝切换 → 使用 `FSongMaps` 中的 `SectionMap` 来查找和跳转到特定的音乐段落。
-   你需要在**音乐的某个特定小节或和弦**改变时触发游戏事件 → 查询 `BarMap` 和 `ChordProgressionMap`。
-   你需要将游戏内的时间（秒）转换为**音乐时间**（小节.拍），或者反过来 → 使用 `FSongMaps` 或 `ISongMapEvaluator` 提供的大量转换函数。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Midi Note To int64` / `int64 to FMidiNote` | FMidiNote 与整数之间的转换 | `UMidiNoteFunctionLibrary` |
| `Tick to Quarter Note` / `Quarter Note to Tick` | MIDI Tick 与四分音符之间的转换 | `UMusicalTickFunctionLibrary` |
| `Make MIDI Song Position from Time` | 从时间、BPM、拍号等参数创建一个 `FMidiSongPos` | `UMidiSongPosFunctionLibrary` |
| `Lerp (MIDI Song Position)` | 在两个 `FMidiSongPos` 之间线性插值 | `UMidiSongPosFunctionLibrary` |
| `Is MIDI Song Position Valid` | 检查一个 `FMidiSongPos` 是否有效 | `UMidiSongPosFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **获取当前音乐时间**：假设你有一个 `FMidiSongPos` 变量 `CurrentSongPos` 和一个 `FSongMaps` 变量 `SongMaps`。你可以使用节点 `Set By Time (Midi Song Position)`，传入游戏经过的秒数和 `SongMaps` 来更新 `CurrentSongPos`。然后，你可以从中读取 `Timestamp.Bar` 和 `Timestamp.Beat` 来得到当前的小节和拍。
2.  **判断是否为强拍**：在上述更新后，检查 `CurrentSongPos.BeatType`，如果等于 `EMusicalBeatType::Downbeat`，则表示当前是小节的第一拍（强拍）。

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixMidi/SongMaps.h"
#include "HarmonixMidi/MidiSongPos.h"
#include "HarmonixMidi/MidiFile.h"
```

### 基本用法

加载一个MIDI文件并查询其音乐信息。
*来源: `Public/HarmonixMidi/MidiFile.h`, `Public/HarmonixMidi/SongMaps.h`*

```cpp
// 假设已经获得一个指向 UMidiFile 资产的指针 UMidiFile* MyMidiFile;
if (MyMidiFile)
{
    // 1. 获取歌曲映射数据。FSongMaps 包含了所有解析出的音乐结构信息。
    const FSongMaps* SongMaps = MyMidiFile->GetSongMaps();
    if (SongMaps)
    {
        // 2. 查询第10000个 Tick 时的速度 (BPM)
        float TempoAtTick = SongMaps->GetTempoAtTick(10000);
        
        // 3. 查询第10.5秒时所在的音乐小节和拍
        FMusicTimestamp Timestamp = SongMaps->TickToMusicTimestamp(SongMaps->MsToTick(10500.0f));
        int32 Bar = Timestamp.Bar;
        float Beat = Timestamp.Beat;
        
        // 4. 获取当前播放位置的完整信息
        FMidiSongPos CurrentPos;
        CurrentPos.SetByTime(10500.0f, *SongMaps);
        // 现在 CurrentPos 包含了秒数、Tick、小节、拍、拍型、段落等所有信息
    }
}
```

### 进阶用法

在游戏循环中实时更新音乐位置，并根据拍型触发事件。
*来源: `Public/HarmonixMidi/MidiSongPos.h`*

```cpp
// 在游戏的 Tick 函数中
void AMyMusicActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (SongMapEvaluator) // 假设持有一个 ISongMapEvaluator* (例如来自 FSongMaps)
    {
        // 1. 根据累计的毫秒数更新音乐位置
        CurrentSongPos.SetByTime(AccumulatedMs, *SongMapEvaluator);
        
        // 2. 检查是否刚刚进入一个新的小节（Downbeat）
        if (CurrentSongPos.IsValid() && PreviousSongPos.IsValid())
        {
            bool bNowOnDownbeat = (CurrentSongPos.BeatType == EMusicalBeatType::Downbeat);
            bool bWasOnDownbeat = (PreviousSongPos.BeatType == EMusicalBeatType::Downbeat);
            
            if (bNowOnDownbeat && !bWasOnDownbeat)
            {
                // 刚刚进入一个新小节的第一个强拍，触发事件！
                OnDownbeatEvent.Broadcast(CurrentSongPos.Timestamp.Bar);
            }
        }
        
        // 保存上一帧的位置用于比较
        PreviousSongPos = CurrentSongPos;
    }
}
```

## Demo 示例

一个最小的示例，演示如何解析MIDI文件并打印基本音乐信息。
*MyMusicAnalyzer.h*
```cpp
#pragma once
#include "CoreMinimal.h"
#include "HarmonixMidi/SongMaps.h"
#include "MyMusicAnalyzer.generated.h"

UCLASS()
class UMyMusicAnalyzer : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Music")
    bool AnalyzeMidiFile(UMidiFile* InMidiFile, float QueryTimeMs, int32& OutBar, float& OutBeat, float& OutTempo);

private:
    TSharedPtr<FSongMaps> SongMaps;
};
```

*MyMusicAnalyzer.cpp*
```cpp
#include "MyMusicAnalyzer.h"
#include "HarmonixMidi/MidiFile.h"

bool UMyMusicAnalyzer::AnalyzeMidiFile(UMidiFile* InMidiFile, float QueryTimeMs, int32& OutBar, float& OutBeat, float& OutTempo)
{
    if (!InMidiFile) return false;
    
    // 获取歌曲映射数据
    const FSongMaps* Maps = InMidiFile->GetSongMaps();
    if (!Maps) return false;
    
    // 将毫秒转换为 MIDI Tick
    float Tick = Maps->MsToTick(QueryTimeMs);
    
    // 从 Tick 获取音乐时间戳 (Bar 和 Beat)
    FMusicTimestamp Timestamp = Maps->TickToMusicTimestamp(Tick);
    OutBar = Timestamp.Bar;
    OutBeat = Timestamp.Beat;
    
    // 获取该 Tick 时的速度 (BPM)
    OutTempo = Maps->GetTempoAtTick(static_cast<int32>(Tick));
    
    return true;
}
```

## 模块依赖

从 `HarmonixMidi` 模块的 Build.cs 中提取。使用此模块需要在你的 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 用于资产注册和元数据管理，HarmonixMidi 依赖它来提供MIDI资产的标签信息。 |
| `UnrealEd` | 编辑器相关功能，HarmonixMidi 依赖它来实现数据验证（IsDataValid）和编辑器属性变更通知（PostEditChangeProperty）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与FSoundWaveData API废弃修复相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associated systems. | 为FusionPatch代理添加用户对象，可用于跟踪关联系统中的活动。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复32位格式说明符：当参数为64位时改为64位，反之亦然。 |
| 2026-04-10 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | [音频] 修复FFusionVoice::AssignIDs中KeyZone的排序并增加结构空值防御。 |

### 维护评价

-   **创建时间**：插件于2024年1月创建，时间较短。
-   **近期更新频率**：2026年4月至5月期间有多次提交，主要集中在**编译警告修复、API冲突解决、以及底层的音频系统（FusionVoice）改进**上。这表明插件仍在**积极维护**中，但近期的更新更多是**稳定性和兼容性修复**，而非新功能添加。
-   **实验性状态**：插件的 `.uplugin` 明确标记为 `IsExperimentalVersion: true`，这意味着其API可能不完全稳定，未来版本可能会有变动。
-   **推荐使用**：对于需要高级音乐时间同步的项目（如节奏游戏），Harmonix 是 UE 中功能最完整的解决方案。尽管处于实验阶段，但其核心功能（MIDI解析、音乐时间映射）已经相当成熟。**建议在新项目中使用，但要做好在未来版本中应对其API可能发生变化的心理准备**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
-   官方文档：无
-   测试用例：源码中包含 `HarmonixMidiTests` 模块，提供了针对其核心功能的自动化测试。