# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、Fusion Patch） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 的 Harmonix GenTech 团队开发的专业音乐音频引擎插件，提供了一套完整的音乐游戏音频解决方案。它并非普通的音频效果插件，而是一个面向**节奏音乐游戏**（如 Fortnite Festival）的完整 MIDI 合成器、采样器和 DSP 处理管线。

Harmonix 解决的核心问题：
- **MIDI 驱动的采样器**：FusionSampler 可以接收 MIDI 消息触发音频样本，支持键区映射、力度分层、多声部管理
- **专业级音频 DSP**：包含双二阶滤波器、延迟、失真、声码器、FFT 分析等效果器
- **高级声像控制**：支持从立体声到 7.1 环绕声的多种声道布局，含 Ambisonics
- **时间拉伸与音高变换**：基于 SMB 算法的实时音高变换引擎，支持节奏同步
- **流式音频渲染**：支持从流式音频数据生成音频输出
- **MetaSound 集成**：通过 HarmonixMetasound 模块将 Fusion Sampler 嵌入 MetaSound 图

该插件默认禁用且标记为实验性，主要为 UE 5.4+ 授权用户在 UE5.4 中首次可用。

## 使用场景

- 你正在开发一个**节奏音乐游戏**（如 Guitar Hero、Rock Band 类型）→ 使用 Harmonix 的 FusionSampler 接收 MIDI 音符播放样本
- 你需要**实时音高变换**且保持音频质量 → 使用 IStretcherAndPitchShifter 接口和 FSmbPitchShifter 实现
- 你需要一个支持**多种环绕声布局**的专业声像系统 → 使用 FGainMatrix 和 FPanner 处理立体声到 7.1 的声道映射
- 你需要在 MetaSound 中使用**MIDI 采样器** → 使用 HarmonixMetasound 模块的 MetaSound 节点
- 你需要**高精度的音频 DSP 效果链**（滤波器、延迟、失真、声码器） → 使用 HarmonixDsp 中的各种效果器类

## 蓝图用法

Harmonix 的核心 DSP 功能主要面向 C++ 开发者，但部分数据结构和资产类型可在蓝图中使用。

### 可蓝图访问的数据结构

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FusionPatch` | 蓝图资产类型，包含采样器的键区配置和采样数据 | `UFusionPatch` |
| `FAdsrSettings` | ADSR 包络参数配置 | `FAdsrSettings` |
| `FLfoSettings` | LFO 调制器参数配置 | `FLfoSettings` |
| `FPannerDetails` | 声像位置参数 | `FPannerDetails` |
| `FTimeStretchConfig` | 时间拉伸配置 | `FTimeStretchConfig` |
| `FHarmonixFFTAnalyzerSettings` | FFT 频谱分析设置 | `FHarmonixFFTAnalyzerSettings` |
| `FHarmonixFFTAnalyzerResults` | FFT 分析结果（频谱数据） | `FHarmonixFFTAnalyzerResults` |
| `FTypedParameter` | 类型化参数容器，支持 bool/int/float/string 等 | `FTypedParameter` |
| `FStreamingChannelParams` | 流式音频声道参数 | `FStreamingChannelParams` |
| `FTrackChannelInfo` | 音轨声道信息 | `FTrackChannelInfo` |
| `FDelaySettings` | 延迟效果设置 | `FDelaySettings` |
| `FDistortionSettingsV2` | 失真效果设置 | `FDistortionSettingsV2` |
| `FVocoderSettings` | 声码器设置 | `FVocoderSettings` |

### 核心资产

Fusion Patch 是 Harmonix 的核心蓝图资产：
1. 在 Content Browser 中右键 → **Audio → Fusion Patch** 创建
2. 配置 **Keyzones**（键区）：指定 MIDI 音符范围、力度范围、关联的 SoundWave
3. 配置 **Settings**：音量、声像、滤波器、ADSR、LFO 等
4. 将 Fusion Patch 连接到 MetaSound 中的 Fusion Sampler 节点使用

### 使用示例（蓝图描述）

1. **创建 Fusion Patch 资产**：Content Browser → 右键 → Audio → Fusion Patch
2. **配置键区**：在 Fusion Patch 编辑器中添加 Keyzone，设置 RootNote=60, MinNote=48, MaxNote=72，并关联一个 SoundWave 资产
3. **在 MetaSound 中使用**：将 Fusion Patch 拖入 MetaSound 图中创建 Fusion Patch 节点，连接到 Fusion Sampler 节点
4. **通过 MIDI 控制**：使用 HarmonixMidi 模块的 MIDI 播放器发送 NoteOn/NoteOff 消息触发采样播放

## C++ 用法

### 头文件引入

```cpp
// 核心 DSP 功能
#include "HarmonixDsp/AudioBuffer.h"
#include "HarmonixDsp/FusionSampler/FusionSampler.h"
#include "HarmonixDsp/GainMatrix.h"
#include "HarmonixDsp/Panner.h"

// 效果器
#include "HarmonixDsp/Effects/BiquadFilter.h"
#include "HarmonixDsp/Effects/Delay.h"
#include "HarmonixDsp/Effects/DistortionV2.h"

// 调制器
#include "HarmonixDsp/Modulators/Adsr.h"
#include "HarmonixDsp/Modulators/MorphingLfo.h"

// 采样器
#include "HarmonixDsp/FusionSampler/FusionVoicePool.h"
#include "HarmonixDsp/FusionSampler/FusionPatch.h"

// 音频分析
#include "HarmonixDsp/AudioAnalysis/FFTAnalyzer.h"

// 音高变换
#include "HarmonixDsp/StretcherAndPitchShifter.h"
#include "HarmonixDsp/Stretchers/SmbPitchShifter.h"
```

### 基本用法 — 音频缓冲区操作

来源：`Public/HarmonixDsp/AudioBuffer.h`

```cpp
// 创建一个非拥有的音频缓冲区（不负责释放内存）
TAudioBuffer<float> Buffer;
Buffer.Configure(2, 1024, EAudioBufferCleanupMode::DontDelete);

// 配置后可设置采样数据指针（外部管理内存）
float* ChannelData[2] = { LeftChannelData, RightChannelData };
// ... 将外部数据绑定到 Buffer 的通道

// 创建一个拥有的音频缓冲区（自动分配和释放内存）
TAudioBuffer<float> OwnedBuffer;
OwnedBuffer.Configure(EAudioBufferChannelLayout::Stereo, 1024, EAudioBufferCleanupMode::Delete);

// 清零并检查是否静音
OwnedBuffer.ZeroValidFrames();
bool bSilent = OwnedBuffer.GetIsSilent(); // true

// 获取峰值
float Peak = OwnedBuffer.GetPeak();        // 全通道峰值
float PeakCh0 = OwnedBuffer.GetPeak(0);    // 通道 0 峰值

// 填充白噪声
OwnedBuffer.FillWithWhiteNoise(0.5f);

// 饱和/限幅
OwnedBuffer.Saturate(-1.0f, 1.0f);
```

### 基本用法 — 双二阶滤波器

来源：`Public/HarmonixDsp/Effects/BiquadFilter.h`

```cpp
using namespace Harmonix::Dsp::Effects;

// 创建滤波器系数
FBiquadFilterCoefs Coefs;
Coefs.MakeFromSettings(FBiquadFilterSettings(EBiquadFilterType::LowPass, 1000.0f, 0.707f, 0.0f), 48000.0f);

// 使用单通道滤波器处理
FBiquadFilter Filter;
float Output[1024];
Filter.Process(InputBuffer, Output, 1024, Coefs, 1.0);
```

### 基本用法 — 延迟效果

来源：`Public/HarmonixDsp/Effects/Delay.h`

```cpp
using namespace Harmonix::Dsp::Effects;

// 创建并配置延迟
FDelay Delay;
Delay.Prepare(48000.0f, 2, 2000.0f); // 48kHz, 2通道, 最大2秒延迟

// 设置参数
Delay.SetDelaySeconds(0.375f);    // 375ms 延迟
Delay.SetFeedbackGain(0.4f);       // 40% 反馈
Delay.SetWetGain(0.5f);            // 50% 湿信号
Delay.SetDryGain(0.7f);            // 70% 干信号

// 处理音频缓冲区（使用 Audio::FMultichannelBufferView）
Audio::FMultichannelBufferView BufferView;
Delay.Process(BufferView);
```

### 基本用法 — ADSR 包络

来源：`Public/HarmonixDsp/Modulators/Adsr.h`

```cpp
using namespace Harmonix::Dsp::Modulators;

// 配置 ADSR 参数
FAdsrSettings Settings;
Settings.IsEnabled = true;
Settings.AttackTime = 0.01f;    // 10ms
Settings.DecayTime = 0.1f;     // 100ms
Settings.SustainLevel = 0.7f;  // -3dB
Settings.ReleaseTime = 0.5f;   // 500ms
Settings.Depth = 0.5f;
Settings.Calculate();

// 创建 ADSR 并使用
FAdsr Adsr;
Adsr.UseSettings(&Settings);
Adsr.Prepare(48000.0f);

// 触发音符时
Adsr.Attack();

// 在音频处理循环中推进
Adsr.Advance(128); // 推进128个采样
float Value = Adsr.GetValue(); // 获取当前包络值

// 释放音符
Adsr.Release();

// 检查阶段
EAdsrStage Stage = Adsr.GetStage(); // Attack/Decay/Sustain/Release/Idle
```

### 基本用法 — LFO 调制器

来源：`Public/HarmonixDsp/Modulators/MorphingLfo.h`

```cpp
using namespace Harmonix::Dsp::Modulators;

// 创建 Morphing LFO（支持波形变形）
FMorphingLFO Lfo(48000.0f);
Lfo.Frequency = 2.0f;      // 2Hz
Lfo.Shape = 1.0f;           // 三角波（0=方波, 1=三角, 2=锯齿）
Lfo.Invert = false;

// 输出单个采样值
float Output;
Lfo.Advance(1, &Output); // 推进1帧并获取输出

// 输出缓冲区
float OutputBuffer[128];
Lfo.Advance(OutputBuffer, 128); // 推进128帧

// 支持音乐时钟同步
FMorphingLFO::FMusicTimingInfo TimingInfo;
TimingInfo.Tempo = 120.0f;
TimingInfo.TimeSignature = FTimeSignature(4, 4);
Lfo.SyncType = ETimeSyncOption::SpeedScale;
Lfo.Advance(OutputBuffer, 128, &TimingInfo);
```

### 进阶用法 — GainMatrix 声道矩阵

来源：`Public/HarmonixDsp/GainMatrix.h`

```cpp
using namespace HarmonixDsp;

// 创建增益矩阵（立体声到环绕声的映射）
FGainMatrix GainMatrix(2, 6, EAudioBufferChannelLayout::FivePointOne);

// 设置环绕声声像
GainMatrix.SetFromMinusOneToOneSurroundPan(1.0f, -0.5f); // 偏左

// 应用到音频缓冲区
float* SourceLeft = LeftChannelData;
float* DestLeftFront = OutputChannels[0];
GainMatrix.ApplyToBuffer(SourceLeft, 0, DestLeftFront, 0, 1024);
GainMatrix.ApplyAndAccumulateToBuffer(SourceLeft, 0, OutputChannels[1], 1, 1024);

// 在两个增益矩阵间插值
FGainMatrix MatrixA(2, 2, EAudioBufferChannelLayout::Stereo);
FGainMatrix MatrixB(2, 2, EAudioBufferChannelLayout::Stereo);
FGainMatrix Interpolated(MatrixA, MatrixB, 0.5f); // 50% 插值
```

### 进阶用法 — FusionSampler MIDI 采样器

来源：`Public/HarmonixDsp/FusionSampler/FusionSampler.h`

```cpp
// 创建 Fusion Sampler
TSharedPtr<FFusionSampler> Sampler = MakeShared<FFusionSampler>(48000.0f, false);

// 准备采样器
Sampler->Prepare(48000.0f, EAudioBufferChannelLayout::Stereo, 2048, true);

// 设置 Fusion Patch
Sampler->SetPatch(FusionPatchData);

// 发送 MIDI 消息
FMidiVoiceId VoiceId = 0;
Sampler->NoteOn(VoiceId, 60, 100, 0); // Note On: C4, velocity 100, channel 0
Sampler->NoteOff(VoiceId, 60, 0);     // Note Off: C4

// 设置 MIDI 控制器
Sampler->SetMidiChannelVolume(-6.0f, 0.5f, 0); // -6dB, 0.5秒渐变, channel 0
Sampler->SetPitchBend(0.5f, 0);                  // 半程弯音

// 设置速度
Sampler->SetSpeed(1.5f, true); // 1.5x 速度，保持音高
Sampler->SetTempo(140.0f);      // 140 BPM

// 获取声部使用情况
int32 MaxVoices = Sampler->GetMaxNumVoices();
int32 ActiveVoices = Sampler->GetNumVoicesInUse();
```

### 进阶用法 — FFT 频谱分析

来源：`Public/HarmonixDsp/AudioAnalysis/FFTAnalyzer.h`

```cpp
using namespace Harmonix::Dsp::AudioAnalysis;

// 创建 FFT 分析器
FFFTAnalyzer Analyzer(48000.0f);

// 配置分析参数
FHarmonixFFTAnalyzerSettings Settings;
Settings.FFTSize = 512;
Settings.MinFrequencyHz = 20.0f;
Settings.MaxFrequencyHz = 20000.0f;
Settings.MelScaleBinning = true;
Settings.NumResultBins = 128;
Analyzer.SetSettings(Settings);

// 分析音频缓冲区
Audio::FAlignedFloatBuffer AudioData;
// ... 填充音频数据 ...
FHarmonixFFTAnalyzerResults Results;
Analyzer.Process(AudioData, Results);

// 读取频谱数据
for (float BinValue : Results.Spectrum)
{
    // 处理每个频率 bin 的能量值
}
```

## Demo 示例

### ADSR 包络 + 滤波器调制的最小示例

```cpp
// MyMusicalSynth.h
#pragma once

#include "CoreMinimal.h"
#include "HarmonixDsp/Modulators/Adsr.h"
#include "HarmonixDsp/Modulators/MorphingLfo.h"
#include "HarmonixDsp/Effects/BiquadFilter.h"

class FMyMusicalSynth
{
public:
    void Init(float InSampleRate);
    void NoteOn();
    void NoteOff();
    void Process(float* OutBuffer, int32 NumFrames);

private:
    float SampleRate = 48000.0f;

    Harmonix::Dsp::Modulators::FAdsrSettings VolumeAdsrSettings;
    Harmonix::Dsp::Modulators::FAdsr VolumeAdsr;

    Harmonix::Dsp::Modulators::FMorphingLFO FilterLfo;

    Harmonix::Dsp::Effects::FBiquadFilterCoefs FilterCoefs;
    Harmonix::Dsp::Effects::FBiquadFilter Filter;
};
```

```cpp
// MyMusicalSynth.cpp
#include "MyMusicalSynth.h"

void FMyMusicalSynth::Init(float InSampleRate)
{
    SampleRate = InSampleRate;

    // 配置音量 ADSR
    VolumeAdsrSettings.IsEnabled = true;
    VolumeAdsrSettings.AttackTime = 0.01f;
    VolumeAdsrSettings.DecayTime = 0.2f;
    VolumeAdsrSettings.SustainLevel = 0.6f;
    VolumeAdsrSettings.ReleaseTime = 0.3f;
    VolumeAdsrSettings.Depth = 1.0f;
    VolumeAdsrSettings.Calculate();

    VolumeAdsr.UseSettings(&VolumeAdsrSettings);
    VolumeAdsr.Prepare(SampleRate);

    // 配置 LFO 调制滤波器频率
    FilterLfo.Reset(SampleRate);
    FilterLfo.Frequency = 0.5f;
    FilterLfo.Shape = 1.0f; // 三角波

    // 配置初始滤波器系数
    FilterCoefs.MakeFromSettings(
        Harmonix::Dsp::Effects::FBiquadFilterSettings(
            EBiquadFilterType::LowPass, 2000.0f, 0.707f, 0.0f),
        SampleRate);
}

void FMyMusicalSynth::NoteOn()
{
    VolumeAdsr.Attack();
}

void FMyMusicalSynth::NoteOff()
{
    VolumeAdsr.Release();
}

void FMyMusicalSynth::Process(float* OutBuffer, int32 NumFrames)
{
    // 推进 ADSR
    VolumeAdsr.Advance(NumFrames);
    float EnvValue = VolumeAdsr.GetValue();

    // 推进 LFO 并调制滤波器频率
    float LfoValue;
    FilterLfo.Advance(NumFrames, &LfoValue);

    // 将 LFO 值映射到滤波器频率 (500Hz - 5000Hz)
    float FilterFreq = 500.0f + LfoValue * 4500.0f;
    FilterCoefs.MakeFromSettings(
        Harmonix::Dsp::Effects::FBiquadFilterSettings(
            EBiquadFilterType::LowPass, FilterFreq, 0.707f, 0.0f),
        SampleRate);

    // 生成简单振荡器波形并应用滤波器和包络
    for (int32 i = 0; i < NumFrames; ++i)
    {
        // 简单的锯齿波生成（示例）
        float Sample = FMath::Fmod(static_cast<float>(i) * 440.0f / SampleRate, 1.0f) * 2.0f - 1.0f;

        // 应用滤波器
        Sample = Filter.Filter(Sample, FilterCoefs);

        // 应用包络
        OutBuffer[i] = Sample * EnvValue;
    }
}
```

## 模块依赖

该插件的各模块之间存在以下依赖关系（仅列出独特依赖）：

| 模块 | 用途 |
|---|---|
| `HarmonixDsp` | 音频 DSP 处理核心（采样器、滤波器、延迟、失真等） |
| `HarmonixMidi` | MIDI 数据处理与播放 |
| `HarmonixMetasound` | MetaSound 集成（将 Fusion Sampler 暴露为 MetaSound 节点） |
| `AssetRegistry` | 资产注册与发现（Fusion Patch 资产的元数据查询） |
| `MetaSoundCore` | MetaSound 框架集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 FusionVoice 键区分配顺序并增加空指针防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断到 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | 为 FusionPatch 代理添加用户对象用于关联活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串的位宽不匹配问题 |

### 维护评价

Harmonix 是一个**活跃维护中**的实验性插件，创建于 2024 年初，由 Epic Games 的 Harmonix GenTech 团队持续开发。近期提交显示该插件仍在积极迭代：修复 bug、改进 API、添加新功能。最近一次实质性更新距今不到一个月。

**注意事项**：
- ⚠️ 该插件标记为 **IsExperimentalVersion = true**，API 可能随版本变化
- ⚠️ 默认 **DisabledByDefault = false**，需要手动在项目设置中启用
- 该插件包含 11 个模块、500+ 源文件，是一个大型且复杂的音频系统
- 主要为 Fortnite Festival 等节奏音乐游戏设计，通用性可能有限
- **推荐用于**：需要 MIDI 采样器和专业音频 DSP 的项目，特别是音乐/节奏游戏

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 测试用例位于各子模块的 `Tests` 目录中（`HarmonixDspTests`、`HarmonixMidiTests`、`HarmonixMetasoundTests`）