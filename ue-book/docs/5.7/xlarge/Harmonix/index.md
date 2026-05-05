# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、蓝图资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Harmonix Music Systems（知名音乐游戏开发商）开发的一套音乐技术套件，现已集成到 UE5 中。它并非一个简单的音频播放器，而是一个**面向音乐驱动型游戏玩法和交互式音频系统**的底层框架。其核心价值在于提供了一套工具，让开发者能够：

1.  **精确解析和同步音乐**：能够加载、解析 MIDI 文件，并精确追踪音乐的节拍、小节、和弦等音乐事件。
2.  **构建动态音乐系统**：允许游戏逻辑（如玩家操作、游戏状态）实时影响音乐的播放、混合和效果，实现音乐与游戏玩法的深度互动。
3.  **提供专业的音频 DSP 处理**：包含一系列音频数字信号处理（DSP）工具，用于实时分析和处理音频流。
4.  **与 MetaSound 深度集成**：将音乐同步和 DSP 功能封装为 MetaSound 节点，便于在 MetaSound 图中构建复杂的交互式音频逻辑。

简而言之，它解决的是“如何让游戏音频不仅仅是背景音乐，而是成为游戏玩法本身的一部分”这一高级问题。

## 使用场景

- **音乐节奏游戏**：开发类似《摇滚乐队》、《吉他英雄》的游戏，需要精确的节拍检测、音符判定和音乐同步。
- **动态配乐系统**：游戏配乐需要根据玩家行为（如潜行、战斗、探索）或游戏进程（如时间、天气）无缝切换、混合或改变情绪。
- **音乐可视化**：基于音乐的节拍、频谱等数据，驱动游戏中的视觉效果（如灯光、粒子、场景变化）。
- **MIDI 控制**：使用外部 MIDI 设备（如键盘、打击垫）作为游戏输入设备，或用游戏逻辑生成 MIDI 信号控制外部音源。
- **高级音频分析**：需要对游戏内音频进行实时分析，例如检测特定声音事件、进行语音识别预处理等。

## 蓝图用法

Harmonix 的蓝图功能主要通过其子模块暴露，核心节点围绕音乐同步、MIDI 处理和音频分析展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load MIDI File` | 从资产路径加载一个 MIDI 文件资产。 | `UHarmonixMidiFile` |
| `Create MIDI File Player` | 创建一个 MIDI 文件播放器实例，用于播放和同步 MIDI 数据。 | `UMidiFilePlayer` |
| `Get Current Song Map` | 从 MIDI 播放器获取当前的音乐映射（包含节拍、小节等信息）。 | `UMidiFilePlayer` |
| `Create Audio Analyzer` | 创建一个音频分析器，用于实时分析音频流的频谱、节拍等特征。 | `UHarmonixAudioAnalyzer` |
| `Get Beat / Bar / Chord` | 从音乐映射中获取当前的节拍、小节或和弦信息。 | `FSongMap` |

### 使用示例（蓝图描述）

1.  **加载并播放 MIDI**：
    - 使用 `Load MIDI File` 节点加载一个 `.mid` 资产。
    - 将加载的资产连接到 `Create MIDI File Player` 节点，创建一个播放器。
    - 调用播放器的 `Play` 函数开始播放。
    - 在 Tick 事件中，通过播放器获取 `Current Song Map`，然后使用 `Get Beat` 等节点获取实时音乐信息，用于驱动游戏逻辑或 UI。

2.  **音频频谱可视化**：
    - 创建一个 `Harmonix Audio Analyzer`。
    - 将游戏中的音频总线（Audio Bus）连接到分析器的输入。
    - 在 Tick 中调用分析器的 `Get Spectrum` 节点，获取频谱数据数组。
    - 将该数组数据传递给材质参数或粒子系统，驱动视觉效果。

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixMidi/MidiFilePlayer.h"
#include "HarmonixDsp/AudioAnalyzer.h"
```

### 基本用法

```cpp
// 假设在某个 Actor 或 Subsystem 中
// 1. 加载 MIDI 文件
UMidiFile* LoadedMidi = LoadObject<UMidiFile>(nullptr, TEXT("/Game/Audio/MySong.MySong"));

// 2. 创建播放器并播放
MidiFilePlayer = NewObject<UMidiFilePlayer>(this);
MidiFilePlayer->SetMidiFile(LoadedMidi);
MidiFilePlayer->Play();

// 3. 在 Tick 中获取音乐信息
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (MidiFilePlayer && MidiFilePlayer->IsPlaying())
    {
        const FSongMap& SongMap = MidiFilePlayer->GetCurrentSongMap();
        float CurrentBeat = SongMap.GetCurrentBeat();
        int32 CurrentBar = SongMap.GetCurrentBar();
        // 使用 CurrentBeat, CurrentBar 驱动游戏逻辑...
    }
}
```
*（代码基于模块功能推断，具体 API 请参考各模块文档）*

### 进阶用法

结合 DSP 分析和 MIDI 同步，实现一个根据音乐节拍自动触发特效的系统：

```cpp
// 创建音频分析器
UHarmonixAudioAnalyzer* Analyzer = NewObject<UHarmonixAudioAnalyzer>(this);
Analyzer->SetAudioBus(MyAudioBus);

// 在 Tick 中同时处理 MIDI 同步和音频分析
void AMyMusicDrivenActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // MIDI 同步部分
    if (MidiPlayer->IsPlaying())
    {
        const FSongMap& Map = MidiPlayer->GetCurrentSongMap();
        if (Map.IsOnBeat()) // 判断是否在节拍点上
        {
            // 触发一个节拍特效
            SpawnBeatEffect();
        }
    }

    // 音频频谱分析部分
    TArray<float> SpectrumData;
    Analyzer->GetSpectrumData(SpectrumData);
    if (SpectrumData.Num() > 0)
    {
        // 计算低频能量，用于驱动环境光强度
        float LowFreqEnergy = CalculateAverage(SpectrumData, 0, 10);
        SetAmbientLightIntensity(LowFreqEnergy * LightScaleFactor);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何加载 MIDI 文件并开始播放。

**MyMusicManager.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMusicManager.generated.h"

class UMidiFile;
class UMidiFilePlayer;

UCLASS()
class AMyMusicManager : public AActor
{
    GENERATED_BODY()

public:
    AMyMusicManager();

    UPROPERTY(EditAnywhere, Category = "Music")
    TSoftObjectPtr<UMidiFile> MidiFileAsset;

    UPROPERTY()
    TObjectPtr<UMidiFilePlayer> MidiPlayer;

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable)
    void StartMusic();
};
```

**MyMusicManager.cpp**
```cpp
#include "MyMusicManager.h"
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixMidi/MidiFilePlayer.h"

AMyMusicManager::AMyMusicManager()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyMusicManager::BeginPlay()
{
    Super::BeginPlay();
    StartMusic();
}

void AMyMusicManager::StartMusic()
{
    if (MidiFileAsset.IsValid())
    {
        UMidiFile* LoadedMidi = MidiFileAsset.LoadSynchronous();
        if (LoadedMidi)
        {
            MidiPlayer = NewObject<UMidiFilePlayer>(this);
            MidiPlayer->SetMidiFile(LoadedMidi);
            MidiPlayer->Play();
            UE_LOG(LogTemp, Log, TEXT("MIDI Music Started."));
        }
    }
}

void AMyMusicManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (MidiPlayer && MidiPlayer->IsPlaying())
    {
        const FSongMap& SongMap = MidiPlayer->GetCurrentSongMap();
        // 可以在这里打印或使用 SongMap 的信息
        // UE_LOG(LogTemp, Verbose, TEXT("Beat: %f"), SongMap.GetCurrentBeat());
    }
}
```

## 模块依赖

Harmonix 插件的模块依赖较为标准，主要依赖 UE 核心音频和编辑器框架。对于使用者而言，无需引入特殊模块。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

由于无法直接访问 git log，基于插件元数据推断：
- **创建时间**：2024-01-17，是一个非常新的插件。
- **实验性标记**：`IsExperimentalVersion: true`，表明该插件仍处于实验阶段，API 和功能可能发生变化。

### 维护评价

- **状态**：**实验性 / 积极开发中**。
- **分析**：Harmonix 插件创建于 2024 年初，且被明确标记为实验性版本。这表明它是由 Epic 和 Harmonix 联合开发的新一代音乐技术，目前处于早期公开测试阶段。虽然功能强大，但使用者需要预期未来版本中可能会有 API 变更、功能调整或 bug 修复。
- **建议**：对于希望在项目中尝试前沿音乐交互技术的开发者，尤其是制作音乐游戏或高度交互式音频体验的团队，**推荐在实验性项目中评估和使用**。但对于追求稳定性的商业项目，建议密切关注其版本更新日志，并做好应对 API 变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests) （示例路径，实际测试可能分布在各子模块的 `Tests` 目录下）