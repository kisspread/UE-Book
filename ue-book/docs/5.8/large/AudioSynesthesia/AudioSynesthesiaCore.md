# Audio Synesthesia

> A variety of offline analyzers for integrating exposing extracted audio metadata to blueprints.

| 属性 | 值 |
|---|---|
| 中文名 | 音频联觉分析器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、分析器预设） |
| 模块 | `AudioSynesthesiaCore` (Runtime), `AudioSynesthesia` (Runtime), `AudioSynesthesiaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia) | |

## 用途

AudioSynesthesia 是一套**离线（非实时）音频分析框架**，用于从音频波形中提取结构化元数据（响度、频谱、音高、节奏起始点等），并将分析结果暴露给蓝图系统。

该插件解决的核心问题是：**游戏运行前或运行时，需要对音频进行深度分析，提取可用于游戏逻辑的声学特征**。例如：
- 分析一段音乐的整体响度范围，用于自动调节游戏音量平衡
- 检测音频中的节奏起始点（onset），用于实现音乐可视化或节拍同步
- 提取音高轨迹，用于卡拉 OK 评分系统
- 计算 LKFS 响度以符合广播标准

插件采用 **工厂模式** 设计：每种分析器由 Settings（配置）→ Worker（分析器）→ Result（结果）三件套组成，通过 Factory 统一创建。同时提供两套 API：
- **实时 API**（`IAnalyzerWorker` / `IAnalyzerResult`）：适用于运行时流式音频分析
- **非实时 API**（`IAnalyzerNRTWorker` / `IAnalyzerNRTResult`）：适用于音频资产的完整离线分析

## 使用场景

- 你正在制作音乐节奏游戏，需要在关卡加载时分析背景音乐的节拍和起始点 → 使用 **Onset 分析器**
- 你需要实现动态音量系统，根据当前音频的响度自动调整音效音量 → 使用 **Loudness 或 LKFS 分析器**
- 你在做卡拉 OK 功能，需要实时检测玩家歌声的音高 → 使用 **YIN 或 FFTPeak 音高检测器**
- 你需要实现音频可视化（频谱柱状图等）→ 使用 **ConstantQ 或 Spectrum 分析器**
- 你需要监控音频的削波和电平 → 使用 **Meter 分析器**
- 你需要用分析数据驱动视觉效果的节拍同步 → 使用 **Onset + MaxStrengthPitchTracker**

> ⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），且仍标记为 Beta（`IsBetaVersion: true`）。需要在项目设置中手动启用。

## 蓝图用法

AudioSynesthesia 的蓝图接口主要在 `AudioSynesthesia` 模块中（非 Core），通过 `UAudioSynesthesiaNRT` 资产类暴露。Core 模块中暴露给蓝图的主要是数据结构（USTRUCT）。

### 核心数据结构

| 结构体 | 说明 | 来源 |
|---|---|---|
| `FLKFSResults` | 瞬时响度数据：通道、时间戳、能量、短时/积分/门控响度 | `LKFSFactory.h` |
| `FLKFSNRTResults` | NRT 响度数据：通道、时间戳、能量、响度、短时响度 | `LKFSNRTFactory.h` |
| `FLKFSNRTAggregateStats` | 整段音频的聚合响度统计（积分响度、门控响度） | `LKFSNRTFactory.h` |
| `FPitchInfo` | 音高信息：频率(Hz)、强度、时间戳 | `PitchTracker.h` |

### 蓝图可读属性（FLKFSResults）

| 属性 | 类型 | 说明 |
|---|---|---|
| `Channel` | `int32` | 音频通道索引（-1 表示混合通道） |
| `Timestamp` | `float` | 对应的时间戳（秒） |
| `Energy` | `float` | 瞬时感知加权能量 |
| `Loudness` | `float` | 瞬时感知加权响度 (dB) |
| `ShortTermLoudness` | `float` | 短时平均响度 (dB) |
| `IntegratedLoudness` | `float` | 积分平均响度 (dB) |
| `GatedLoudness` | `float` | 门控平均响度 (dB) |
| `LoudnessRange` | `FFloatInterval` | 响度范围 LRA（EBU Tech 3342） |

### 使用示例（蓝图描述）

1. **创建 NRT 分析资产**：在内容浏览器中右键 → Audio → Audio Synesthesia NRT → 选择分析器类型（Loudness/ConstantQ/Onset 等）
2. **配置分析参数**：选中资产，在细节面板中设置分析周期、窗口大小、FFT 尺寸等
3. **关联音频资产**：将目标音频波形（Sound Wave）拖入分析资产的音频引用槽
4. **蓝图中查询结果**：使用 `Get Loudness at Time` / `Get Constant Q at Time` 等节点，传入时间戳获取插值后的分析数据

## C++ 用法

### 头文件引入

```cpp
// 实时分析器
#include "LoudnessFactory.h"
#include "ConstantQFactory.h"
#include "OnsetAnalyzer.h"
#include "MeterFactory.h"
#include "SynesthesiaSpectrumAnalysisFactory.h"
#include "LKFSFactory.h"

// 非实时分析器
#include "LoudnessNRTFactory.h"
#include "ConstantQNRTFactory.h"
#include "OnsetNRTFactory.h"
#include "LKFSNRTFactory.h"

// 音高检测
#include "YINPitchDetector.h"
#include "FFTPeakPitchDetector.h"
#include "AutoCorrelationPitchDetector.h"
#include "MaxStrengthPitchTracker.h"

// 工具函数
#include "InterpolateSorted.h"
#include "FindNearestByTimestamp.h"
```

### 基本用法：实时响度分析

使用实时 API 分析音频缓冲区，获取逐帧响度数据。

```cpp
// 来源: Public/LoudnessFactory.h + test cases

#include "LoudnessFactory.h"

void AnalyzeLoudnessRealtime(const TArray<float>& AudioData, float InSampleRate, int32 InNumChannels)
{
    using namespace Audio;

    // 1. 配置分析器参数
    FLoudnessSettings Settings;
    Settings.AnalysisPeriod = 0.01f; // 每 10ms 分析一次
    Settings.LoudnessCurveType = ELoudnessCurveType::K; // K 加权（ITU-R 468）
    Settings.FFTSize = 4096;

    // 2. 创建 Worker
    FAnalyzerParameters Params;
    Params.NumChannels = InNumChannels;
    Params.SampleRate = InSampleRate;

    FLoudnessFactory Factory;
    TUniquePtr<IAnalyzerWorker> Worker = Factory.NewWorker(Params, &Settings);
    TUniquePtr<IAnalyzerResult> Result = Factory.NewResult();

    // 3. 喂入音频数据（可以分多次喂入）
    TArrayView<const float> AudioView(AudioData);
    Worker->Analyze(AudioView, Result.Get());

    // 4. 获取结果
    FLoudnessResult* LoudnessResult = static_cast<FLoudnessResult*>(Result.Get());

    // 获取所有通道的响度数据
    const TArray<FLoudnessEntry>& OverallLoudness = LoudnessResult->GetLoudnessArray();
    for (const FLoudnessEntry& Entry : OverallLoudness)
    {
        UE_LOG(LogTemp, Log, TEXT("Time: %.3f s, Loudness: %.2f dB, Energy: %.4f"),
            Entry.Timestamp, Entry.Loudness, Entry.Energy);
    }

    // 获取特定通道的数据
    if (LoudnessResult->ContainsChannel(0))
    {
        const TArray<FLoudnessEntry>& Ch0 = LoudnessResult->GetChannelLoudnessArray(0);
        UE_LOG(LogTemp, Log, TEXT("Channel 0 has %d entries"), Ch0.Num());
    }
}
```

### 基本用法：NRT 响度分析

使用 NRT API 对完整音频文件进行离线分析。

```cpp
// 来源: Public/LoudnessNRTFactory.h + test cases

#include "LoudnessNRTFactory.h"

void AnalyzeLoudnessNRT(const TArray<float>& FullAudio, float InSampleRate, int32 InNumChannels)
{
    using namespace Audio;

    // 1. 配置
    FLoudnessNRTSettings Settings;
    Settings.AnalysisPeriod = 0.01f;

    // 2. 创建 NRT Worker
    FAnalyzerNRTParameters Params;
    Params.NumChannels = InNumChannels;
    Params.SampleRate = InSampleRate;

    FLoudnessNRTFactory Factory;
    TUniquePtr<IAnalyzerNRTWorker> Worker = Factory.NewWorker(Params, &Settings);
    TUniquePtr<IAnalyzerNRTResult> Result = Factory.NewResult();

    // 3. 喂入全部音频
    TArrayView<const float> AudioView(FullAudio);
    Worker->Analyze(AudioView, Result.Get());

    // 4. 必须调用 Finalize 完成分析
    Worker->Finalize(Result.Get());

    // 5. 使用结果
    FLoudnessNRTResult* LoudnessResult = static_cast<FLoudnessNRTResult*>(Result.Get());

    // 按时间戳查询最近的响度值
    float QueryTime = 5.0f; // 查询第 5 秒
    const TArray<FLoudnessDatum>& OverallLoudness = LoudnessResult->GetLoudnessArray();

    FLoudnessDatum Nearest;
    // 使用 FindNearestByTimestamp 工具函数
    const FLoudnessDatum* Found = FindNearestByTimestamp(OverallLoudness, QueryTime);
    if (Found)
    {
        UE_LOG(LogTemp, Log, TEXT("Loudness at %.1f s: %.2f dB"), QueryTime, Found->Loudness);
    }

    // 计算响度范围
    float LoudnessRange = LoudnessResult->GetLoudnessRange(-60.f); // 噪底 -60 dB
    UE_LOG(LogTemp, Log, TEXT("Loudness Range: %.2f dB"), LoudnessRange);
}
```

### 基本用法：音高检测

```cpp
// 来源: Public/YINPitchDetector.h + test cases

#include "YINPitchDetector.h"

void DetectPitchesWithYIN(const TArray<float>& MonoAudio, float SampleRate)
{
    using namespace Audio;

    // 1. 配置 YIN 检测器
    FYINPitchDetectorSettings Settings;
    Settings.AnalysisHopSeconds = 0.01f;     // 每 10ms 分析一次
    Settings.MinimumFrequency = 80.f;        // 最低检测 80 Hz
    Settings.MaximumFrequency = 2000.f;      // 最高检测 2000 Hz
    Settings.Threshold = 0.15f;              // 清晰人声推荐值

    // 2. 创建检测器
    FYINPitchDetector Detector(Settings, SampleRate);

    // 3. 分段检测（模拟流式输入）
    TArray<FPitchInfo> Pitches;
    const int32 BufferSize = 4096;

    for (int32 i = 0; i < MonoAudio.Num(); i += BufferSize)
    {
        int32 Count = FMath::Min(BufferSize, MonoAudio.Num() - i);
        FAlignedFloatBuffer Buffer;
        Buffer.Append(&MonoAudio[i], Count);
        Detector.DetectPitches(Buffer, Pitches);
    }

    // 4. 结束分析
    Detector.Finalize(Pitches);

    // 5. 使用结果
    for (const FPitchInfo& Pitch : Pitches)
    {
        UE_LOG(LogTemp, Log, TEXT("Time: %.3f s, Freq: %.1f Hz, Strength: %.3f"),
            Pitch.Timestamp, Pitch.Frequency, Pitch.Strength);
    }
}
```

### 进阶用法：节奏起始点检测 + 音高追踪

```cpp
// 来源: Public/OnsetAnalyzer.h + Public/MaxStrengthPitchTracker.h

#include "OnsetAnalyzer.h"
#include "MaxStrengthPitchTracker.h"
#include "YINPitchDetector.h"
#include "PeakPicker.h"

void AnalyzeRhythmAndPitch(const TArray<float>& AudioData, float SampleRate)
{
    using namespace Audio;

    // ===== Part 1: 起始点检测 =====
    {
        FOnsetStrengthSettings OnsetSettings;
        OnsetSettings.NumHopFrames = 1024;
        OnsetSettings.NumWindowFrames = 4096;
        OnsetSettings.FFTSize = 4096;

        FOnsetStrengthAnalyzer OnsetAnalyzer(OnsetSettings, SampleRate);

        // 计算起始强度包络
        TArray<float> OnsetStrengths;
        OnsetAnalyzer.CalculateOnsetStrengths(AudioData, OnsetStrengths);

        // 从包络中提取起始点索引
        FPeakPickerSettings PeakSettings;
        PeakSettings.MeanDelta = 0.07f;

        TArray<int32> OnsetIndices;
        OnsetExtractIndices(PeakSettings, OnsetStrengths, OnsetIndices);

        // 回溯到起始攻击的起点（用于精确剪切）
        TArray<int32> BacktrackedIndices;
        OnsetBacktrackIndices(OnsetStrengths, OnsetIndices, BacktrackedIndices);

        UE_LOG(LogTemp, Log, TEXT("Found %d onsets"), OnsetIndices.Num());
        for (int32 Idx : BacktrackedIndices)
        {
            float TimeSec = FOnsetStrengthAnalyzer::GetTimestampForIndex(OnsetSettings, SampleRate, Idx);
            UE_LOG(LogTemp, Log, TEXT("  Onset at %.3f s"), TimeSec);
        }
    }

    // ===== Part 2: 最强音高追踪 =====
    {
        // 创建 YIN 检测器
        FYINPitchDetectorSettings YINSettings;
        YINSettings.MinimumFrequency = 80.f;
        YINSettings.MaximumFrequency = 2000.f;

        TUniquePtr<IPitchDetector> Detector = MakeUnique<FYINPitchDetector>(YINSettings, SampleRate);

        // 用 MaxStrengthPitchTracker 追踪连续音高
        FMaxStrengthPitchTrackerSettings TrackerSettings;
        TrackerSettings.MinimumStrength = 0.3f;
        TrackerSettings.MaximumFrequencyRatioDeviation = 0.05f; // 5% 频率偏差容忍

        FMaxStrengthPitchTracker Tracker(TrackerSettings, MoveTemp(Detector));

        TArray<FPitchTrackInfo> PitchTracks;
        Tracker.TrackPitches(FAlignedFloatBuffer(AudioData), PitchTracks);
        Tracker.Finalize(PitchTracks);

        UE_LOG(LogTemp, Log, TEXT("Found %d pitch tracks"), PitchTracks.Num());
        for (int32 t = 0; t < PitchTracks.Num(); ++t)
        {
            UE_LOG(LogTemp, Log, TEXT("  Track %d: %d observations"), t, PitchTracks[t].Observations.Num());
        }
    }
}
```

### 进阶用法：Constant-Q 频谱分析

```cpp
// 来源: Public/ConstantQFactory.h + Public/ConstantQAnalyzer.h

#include "ConstantQFactory.h"

void AnalyzeConstantQ(const TArray<float>& AudioData, float SampleRate, int32 NumChannels)
{
    using namespace Audio;

    FConstantQSettings Settings;
    Settings.AnalysisPeriodInSeconds = 0.01f;
    Settings.bDownmixToMono = true;
    Settings.FFTSize = 4096;
    Settings.WindowType = EWindowType::Blackman;
    Settings.SpectrumType = ESpectrumType::PowerSpectrum;
    Settings.Scaling = EConstantQScaling::Decibel;

    FAnalyzerParameters Params;
    Params.NumChannels = NumChannels;
    Params.SampleRate = SampleRate;

    FConstantQFactory Factory;
    TUniquePtr<IAnalyzerWorker> Worker = Factory.NewWorker(Params, &Settings);
    TUniquePtr<IAnalyzerResult> Result = Factory.NewResult();

    Worker->Analyze(TArrayView<const float>(AudioData), Result.Get());

    FConstantQResult* CQResult = static_cast<FConstantQResult*>(Result.Get());

    int32 NumChannelsResult = CQResult->GetNumChannels();
    if (NumChannelsResult > 0)
    {
        const TArray<FConstantQFrame>& Frames = CQResult->GetFramesForChannel(0);
        UE_LOG(LogTemp, Log, TEXT("Channel 0: %d CQ frames"), Frames.Num());

        if (Frames.Num() > 0)
        {
            // 输出第一个频谱帧
            for (int32 bin = 0; bin < Frames[0].Spectrum.Num(); ++bin)
            {
                UE_LOG(LogTemp, Log, TEXT("  Bin %d: %.2f dB"), bin, Frames[0].Spectrum[bin]);
            }
        }
    }
}
```

## Demo 示例

一个完整的最小示例：从音频文件加载数据并执行响度分析。

### LoudnessDemo.h

```cpp
// LoudnessDemo.h
#pragma once

#include "CoreMinimal.h"
#include "LoudnessFactory.h"

class FLoudnessDemo
{
public:
    /** 分析音频缓冲区并打印响度信息 */
    static void RunDemo(const TArray<float>& AudioSamples, float SampleRate, int32 NumChannels);
};
```

### LoudnessDemo.cpp

```cpp
// LoudnessDemo.cpp
#include "LoudnessDemo.h"

void FLoudnessDemo::RunDemo(const TArray<float>& AudioSamples, float SampleRate, int32 NumChannels)
{
    using namespace Audio;

    if (AudioSamples.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No audio data to analyze"));
        return;
    }

    // 配置分析器
    FLoudnessSettings Settings;
    Settings.AnalysisPeriod = 0.01f;           // 10ms 分析间隔
    Settings.FFTSize = 4096;
    Settings.LoudnessCurveType = ELoudnessCurveType::K;

    // 设置分析参数
    FAnalyzerParameters Params;
    Params.NumChannels = NumChannels;
    Params.SampleRate = SampleRate;

    // 创建工厂、Worker 和 Result
    FLoudnessFactory Factory;
    TUniquePtr<IAnalyzerWorker> Worker = Factory.NewWorker(Params, &Settings);
    TUniquePtr<IAnalyzerResult> RawResult = Factory.NewResult();

    // 分析音频
    TArrayView<const float> AudioView(AudioSamples);
    Worker->Analyze(AudioView, RawResult.Get());

    // 转换并获取结果
    FLoudnessResult* Result = static_cast<FLoudnessResult*>(RawResult.Get());

    // 打印整体响度统计
    const TArray<FLoudnessEntry>& OverallLoudness = Result->GetLoudnessArray();
    UE_LOG(LogTemp, Log, TEXT("=== Loudness Analysis Results ==="));
    UE_LOG(LogTemp, Log, TEXT("Total entries: %d"), OverallLoudness.Num());
    UE_LOG(LogTemp, Log, TEXT("Channels: %d"), Result->GetNumChannels());

    // 找到最响和最安静的时刻
    float MaxLoudness = -TNumericLimits<float>::Max();
    float MinLoudness = TNumericLimits<float>::Max();
    float MaxTime = 0.f;
    float MinTime = 0.f;

    for (const FLoudnessEntry& Entry : OverallLoudness)
    {
        if (Entry.Loudness > MaxLoudness)
        {
            MaxLoudness = Entry.Loudness;
            MaxTime = Entry.Timestamp;
        }
        if (Entry.Loudness < MinLoudness)
        {
            MinLoudness = Entry.Loudness;
            MinTime = Entry.Timestamp;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Loudest: %.2f dB at %.3f s"), MaxLoudness, MaxTime);
    UE_LOG(LogTemp, Log, TEXT("Quietest: %.2f dB at %.3f s"), MinLoudness, MinTime);

    // 按时间戳查询指定时刻的响度
    float QueryTime = AudioSamples.Num() / (SampleRate * NumChannels) / 2.0f; // 音频中间时刻
    const FLoudnessDatum* Found = FindNearestByTimestamp(
        TArrayView<FLoudnessDatum>(const_cast<FLoudnessDatum*>(OverallLoudness.GetData()), OverallLoudness.Num()),
        QueryTime);

    if (Found)
    {
        UE_LOG(LogTemp, Log, TEXT("At %.3f s: Loudness = %.2f dB, Energy = %.4f"),
            QueryTime, Found->Loudness, Found->Energy);
    }
}
```

## 模块依赖

该插件的依赖关系主要涉及音频信号处理底层模块。由于无法直接访问 Build.cs，以下基于头文件引用关系推断：

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 底层 DSP 工具（FFT、窗函数、包络跟踪、Mel 频谱等） |
| `AudioAnalyzerCore` | 音频分析器基础框架（IAnalyzerNRTSettings、IAnalyzerNRTWorker 等接口定义） |
| `AudioMixer` | 音频混合器基础（FFTPeakPitchDetector 中引用了 FFmpeg FFT） |

> 无特殊依赖时，标准的 Core/CoreUObject/Engine 依赖已隐含。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 编辑器中新增音频资产创建菜单项 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-02 | `ebf191b8` | Add bounds check to skip processing when MaxBin is negative in the auto-correlation pitch detector | 自相关音高检测器添加负索引边界检查，防止越界 |
| 2026-03-18 | `803166cc` | Fix swapped arguments to CrossCorrelate in YIN pitch detector that caused truncated autocorrelation | 修复 YIN 音高检测器互相关参数顺序错误导致截断的问题 |
| 2026-03-16 | `d99b4142` | Add YIN pitch detection algorithm to AudioSynesthesiaCore | 新增 YIN 音高检测算法实现 |

### 维护评价

- **状态**: 🟢 **活跃维护中**
- **分析**: 该插件虽标记为 Beta 且已存在约 7 年，但近期（2026 年 3-4 月）仍有实质性功能更新，包括新增 YIN 音高检测算法、修复核心算法 bug、改进编辑器集成
- **风险点**: `IsBetaVersion = true` 和 `EnabledByDefault = false` 表明 Epic 可能尚未认为该插件达到生产稳定级别。API 可能在未来版本中发生变化
- **注意事项**: `LoudnessAnalyzer.h` 已被标记为 `UE_DEPRECATED_HEADER`，功能已迁移至 SignalProcessing 模块的 `DSP/LoudnessAnalyzer.h`
- **推荐**: ✅ 适用于需要离线音频分析的项目，尤其是音乐游戏、音频可视化等场景。不建议用于对 API 稳定性要求极高的生产项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)
- 官方文档：无（DocsURL 为空）
- 测试用例：位于插件内部的 `Source/` 目录（BDD 风格自动化测试）