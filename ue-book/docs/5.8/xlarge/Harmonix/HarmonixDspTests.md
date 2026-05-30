# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 和谐音乐工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、测试资源） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Harmonix Music Systems 开发的一套底层音频框架，为 UE5 提供了专业级的音乐制作、分析和同步能力。它不仅仅是一个音频播放器，而是一个用于构建**节奏游戏、音乐可视化、交互式音乐系统**的核心工具包。该插件解决了在 UE 中精确处理 MIDI 事件、实时音频分析、复杂音乐时钟同步以及动态音乐层混合等高级音频需求，是 Epic 旗下如《Fortnite Festival》等音乐类游戏的技术基础。

## 使用场景

- **制作节奏游戏（如《Rock Band》、《Guitar Hero》风格）**：你需要精确同步玩家输入与音乐节拍，并根据时机反馈视觉效果。
- **开发音乐可视化工具**：你需要实时分析音频频谱、节拍、音符，用于生成与音乐同步的粒子、灯光或几何变化。
- **构建交互式音乐系统**：你需要根据游戏状态（如战斗强度、探索状态）动态切换或混合不同的音乐层（Stems），实现无缝过渡。
- **处理和编辑 MIDI 数据**：你需要在蓝图或 C++ 中加载、解析、生成或实时修改 MIDI 事件流，用于音序器或作曲工具。

## 蓝图用法

核心功能暴露在 `UHarmonixBlueprintLibrary`、`UHarmonixMidiBlueprintLibrary` 等类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadMidiFile` | 从资产路径加载一个 UMidiFile 资产。 | `UHarmonixBlueprintLibrary` |
| `GetMidiTracks` | 从 UMidiFile 中获取所有轨道信息。 | `UHarmonixBlueprintLibrary` |
| `GetMidiEvents` | 获取指定轨道中的所有 MIDI 事件。 | `UHarmonixBlueprintLibrary` |
| `CreateMidiStream` | 创建一个实时 MIDI 事件流，用于动态生成或处理 MIDI 数据。 | `UHarmonixBlueprintLibrary` |
| `ConvertMidiNoteToFrequency` | 将 MIDI 音符号（如 60, C4）转换为对应的频率值。 | `UHarmonixMidiBlueprintLibrary` |
| `GetBeatInfoFromClock` | 从音乐时钟获取当前节拍位置、小节等信息。 | `UHarmonixBlueprintLibrary` |
| `StartMusicClock` | 启动一个音乐时钟，以精确的采样精度同步音频事件。 | `UHarmonixBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **加载并遍历 MIDI 文件**：
    *   使用 `LoadMidiFile` 节点加载资产。
    *   连接 `GetMidiTracks` 节点获取轨道数组。
    *   使用 `ForEachLoop` 遍历每个轨道。
    *   在循环体内，连接 `GetMidiEvents` 节点获取当前轨道的事件数组，再次遍历这些事件，检查事件类型（如 NoteOn），并获取音符号、力度、时间等信息。

2.  **实时音频分析**：
    *   创建一个 `HarmonixAudioAnalyzer` 组件或蓝图节点。
    *   将其连接到一个音频输出组件（如 `Synesthesia`）。
    *   在事件图表中，订阅其输出引脚（如 `OnBeatDetected`, `OnSpectralAnalysis`），并用返回的数据驱动材质参数或控制其他逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "Harmonix.h"
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixDsp/AudioAnalyzer.h"
```

### 基本用法

加载 MIDI 文件并遍历音符事件。  
*（来源：根据 `HarmonixMidi` 模块功能推断）*

```cpp
// 假设在 Actor 或 GameInstance 中
UObject* LoadMidiFile(const FString& AssetPath)
{
    // 同步加载 MidiFile 资产
    UMidiFile* MidiFile = LoadObject<UMidiFile>(nullptr, *AssetPath);
    if (!MidiFile)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load MIDI file: %s"), *AssetPath);
        return nullptr;
    }

    // 获取第一个轨道
    const TArray<FMidiTrack>& Tracks = MidiFile->GetTracks();
    if (Tracks.Num() > 0)
    {
        const FMidiTrack& FirstTrack = Tracks[0];
        // 遍历事件
        for (const FMidiEvent& Event : FirstTrack.GetEvents())
        {
            if (Event.IsNoteOn())
            {
                int32 NoteNumber = Event.GetNoteNumber();
                int32 Velocity = Event.GetVelocity();
                // ... 处理音符事件
            }
        }
    }

    return MidiFile;
}
```

### 进阶用法

使用音乐时钟进行精确同步。  
*（来源：根据 `Harmonix` 核心模块和节奏游戏逻辑推断）*

```cpp
// 创建并管理一个音乐时钟
class AMyRhythmActor : public AActor
{
    UPROPERTY()
    UHarmonixMusicClock* MusicClock;

    void BeginPlay()
    {
        Super::BeginPlay();
        // 创建时钟
        MusicClock = NewObject<UHarmonixMusicClock>(this);
        // 配置 BPM 和拍号
        MusicClock->SetBPM(120.0f);
        MusicClock->SetTimeSignature(4, 4);
    }

    void Tick(float DeltaTime)
    {
        Super::Tick(DeltaTime);
        // 每帧推进时钟（实际应由音频引擎回调驱动更精确）
        MusicClock->Advance(DeltaTime);
        
        // 获取当前节拍信息
        float CurrentBeat = MusicClock->GetCurrentBeat();
        int32 CurrentBar = MusicClock->GetCurrentBar();
        
        // 可用于判断玩家输入时机
        if (IsPlayerHitNearBeat(CurrentBeat, MyHitTime))
        {
            // 触发“完美”判定
        }
    }
};
```

## Demo 示例

一个最小示例，展示在 C++ 中加载 MIDI 文件并打印前10个音符事件。

**MyMidiDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMidiDemo.generated.h"

class UMidiFile;
class UHarmonixMusicClock;

UCLASS()
class MYPROJECT_API AMyMidiDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyMidiDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="MIDI")
    FString MidiAssetPath;

    UPROPERTY()
    TObjectPtr<UMidiFile> LoadedMidiFile;
};
```

**MyMidiDemo.cpp**
```cpp
#include "MyMidiDemo.h"
#include "HarmonixMidi/MidiFile.h"

AMyMidiDemo::AMyMidiDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMidiDemo::BeginPlay()
{
    Super::BeginPlay();

    // 加载 MIDI 文件
    if (!MidiAssetPath.IsEmpty())
    {
        LoadedMidiFile = LoadObject<UMidiFile>(nullptr, *MidiAssetPath);
    }

    if (LoadedMidiFile)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded MIDI file with %d tracks."), LoadedMidiFile->GetTracks().Num());

        // 获取第一个轨道
        const TArray<FMidiTrack>& Tracks = LoadedMidiFile->GetTracks();
        if (Tracks.Num() > 0)
        {
            const FMidiTrack& FirstTrack = Tracks[0];
            UE_LOG(LogTemp, Log, TEXT("First track has %d events."), FirstTrack.GetEvents().Num());

            // 打印前10个 NoteOn 事件
            int32 Count = 0;
            for (const FMidiEvent& Event : FirstTrack.GetEvents())
            {
                if (Count >= 10) break;
                if (Event.IsNoteOn())
                {
                    UE_LOG(LogTemp, Log, TEXT("Event %d: NoteOn, Note=%d, Velocity=%d at time %f ticks."),
                        Count, Event.GetNoteNumber(), Event.GetVelocity(), Event.GetTick());
                    Count++;
                }
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load MIDI file from path: %s"), *MidiAssetPath);
    }
}
```

## 模块依赖

要使用 Harmonix 插件，你的项目模块通常需要依赖以下**非标准**模块（除了 Core, CoreUObject, Engine 等）：

| 模块 | 用途 |
|---|---|
| `Harmonix` | Harmonix 核心运行时模块，提供音乐时钟等基础功能。 |
| `HarmonixMidi` | 提供 MIDI 文件解析、数据结构和访问接口。 |
| `HarmonixDsp` | 提供数字信号处理和音频分析功能。 |
| `HarmonixMetasound` | 与 UE MetaSound 系统集成，提供音乐相关的 MetaSound 节点。 |

**注意**：由于插件包含 Editor 模块（如 `HarmonixEditor`），编辑器功能通常由插件自身处理，无需在你的游戏模块中直接依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音频引擎中音区键分配顺序问题，并增加空指针防御。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决合并冲突，涉及已弃用音频波形数据 API 的修复。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量转换为浮点数产生的编译器警告。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | 为 FusionPatch 代理添加用户对象，可用于关联跟踪活动。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正 64 位参数使用 32 位格式说明符的错误，反之亦然。 |

### 维护评价

**活跃维护**。

- **创建时间**：插件于 2024 年初移入引擎仓库，年龄较新（约 2 年）。
- **更新频率**：近期（2026年5月）有多次提交，主要集中在**错误修复**（如空指针防御、编译器警告、格式说明符修正）和**与底层音频引擎（Fusion）的集成改进**。这表明插件处于积极的 bug 修复和稳定性增强阶段。
- **实验性状态**：尽管 `.uplugin` 标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，但频繁的实质性更新（非简单重构）表明它正朝着稳定版本发展，目前被 Epic 自己用于商业项目（如 Fortnite Festival）。
- **推荐使用**：推荐用于需要**专业级音乐交互和音频分析**的项目。由于标记为实验性，需做好 API 可能变动的准备，但其功能深度和维护状态表明它值得投入学习和集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档]() （无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests) （示例：Midi 模块测试）