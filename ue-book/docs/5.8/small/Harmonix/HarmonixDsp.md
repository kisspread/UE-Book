# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、Fusion Patch 配置） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 的 Harmonix GenTech 团队开发的**专业级音乐音频处理框架**。它提供了一套完整的音乐相关音频功能栈，核心能力包括：

1. **Fusion Sampler（融合采样器）**：一个完整的 MIDI 虚拟乐器系统，支持多音色（Keyzone）映射、力度分层、声部管理、ADSR 包络、LFO 调制、弯音、滑音（Portamento）等专业采样器功能。底层使用 `FFusionVoicePool` 进行声部池管理和复用。
2. **DSP 处理管线**：提供 Biquad 滤波器、FIR 滤波器、延迟（Delay）、失真（Distortion）、Vocoder 等多种音频效果器。
3. **音高变换与时间拉伸**：通过 `IStretcherAndPitchShifter` 接口和 `FSmbPitchShifter` 实现高质量的 Pitch Shifting，支持可插拔的工厂模式扩展。
4. **多声道音频管理**：支持从单声道到 7.1 环绕声、Ambisonics 的全通道布局，包含增益矩阵（GainMatrix）、声像定位（Panner）等空间音频处理。
5. **音乐时钟同步**：内置节拍/速度同步、小节/拍子追踪能力，LFO 和延迟等效果器可锁定到音乐节拍。
6. **音频分析**：FFT 频谱分析器，支持 Mel 频率分箱。
7. **MetaSound 集成**：通过 `HarmonixMetasound` 模块将采样器和 DSP 功能暴露为 MetaSound 节点。
8. **流式音频渲染**：`FStreamingAudioRendererV2` 支持流式解码和渲染音频数据。

该插件最初作为实验性功能存在于 Experimental 目录，于 UE 5.4 正式迁移到 Runtime 目录向授权用户开放。它主要服务于**节奏/音乐类游戏**（如 Fortnite Festival）的实时音乐播放、交互和音频处理需求。

## 使用场景

- 你在做一个**节奏/音乐游戏**（如音游、Festival 模式）→ 用 Fusion Sampler 进行 MIDI 乐器采样播放
- 你需要在运行时**实时调整音频速度但保持音高**（或反之）→ 用 Pitch Shifter 和时间拉伸功能
- 你要实现**专业的音频效果器链**（滤波、延迟、失真、Vocoder）→ 用 HarmonixDsp 中的各种效果器
- 你需要**多声道空间音频**（立体声到 7.1 环绕声）的精细控制 → 用 GainMatrix 和 Panner
- 你要在 MetaSound 图中使用**采样器节点**→ 用 HarmonixMetasound 模块
- 你需要**节拍同步的 LFO / 延迟**效果→ 用内置的 BeatSync 功能
- 你正在做**音频频谱分析**用于可视化 → 用 FFTAnalyzer

## 蓝图用法

Harmonix 插件主要面向 C++ 使用，但部分设置结构体和资产类型已暴露到蓝图。

### 核心资产类型

| 类型 | 说明 |
|---|---|
| `UFusionPatch` | Fusion 采样器音色包，包含键区映射（Keyzone）和采样器设置 |
| `FFusionPatchData` | Fusion Patch 的运行时数据结构，包含键区数组和补丁设置 |
| `FKeyzoneSettings` | 单个键区设置，定义音高范围、力度范围、采样波形、ADSR 等 |

### 核心设置结构体（蓝图可编辑）

| 结构体 | 说明 |
|---|---|
| `FFusionPatchSettings` | 采样器全局设置：音量、声像、弯音范围、滤波器、ADSR、LFO 等 |
| `FAdsrSettings` | ADSR 包络设置，支持攻击/衰减/持续/释放在内的曲线控制 |
| `FLfoSettings` | LFO 调制器设置，支持正弦/方波/锯齿/三角/随机波形 |
| `FDelaySettings` | 延迟效果器设置，支持节拍同步、滤波器、LFO、立体声模式 |
| `FDistortionSettingsV2` | 失真效果器设置，支持多种失真类型和滤波 |
| `FPannerDetails` | 声像定位详情，支持立体声/环绕声/极坐标/直接通道分配多种模式 |
| `FTimeStretchConfig` | 时间拉伸配置，控制是否维持时间、节拍同步等 |
| `FTypedParameter` | 类型化参数包装器，支持 bool/double/float/int 等多种类型 |

### 使用示例（蓝图描述）

创建一个 Fusion Patch 资产：

1. 在 Content Browser 中右键 → Audio → Fusion Patch
2. 在 Fusion Patch 编辑器中添加 Keyzone，设置音高范围（MinNote/MaxNote）、力度范围（MinVelocity/MaxVelocity）
3. 为每个 Keyzone 指定 SoundWave 采样
4. 配置 FFusionPatchSettings：设置全局音量、ADSR 包络、LFO 调制、滤波器等
5. 通过 MetaSound 节点或 C++ 代码在运行时触发 NoteOn/NoteOff 播放

## C++ 用法

### 头文件引入

```cpp
// Fusion Sampler（采样器核心）
#include "HarmonixDsp/FusionSampler/FusionSampler.h"
#include "HarmonixDsp/FusionSampler/FusionVoice.h"
#include "HarmonixDsp/FusionSampler/FusionVoicePool.h"
#include "HarmonixDsp/FusionSampler/FusionPatch.h"

// DSP 效果器
#include "HarmonixDsp/Effects/BiquadFilter.h"
#include "HarmonixDsp/Effects/Delay.h"
#include "HarmonixDsp/Effects/DistortionV2.h"

// 音频缓冲区和工具
#include "HarmonixDsp/AudioBuffer.h"
#include "HarmonixDsp/GainMatrix.h"
#include "HarmonixDsp/Panner.h"
#include "HarmonixDsp/PannerDetails.h"

// Pitch Shifting
#include "HarmonixDsp/StretcherAndPitchShifter.h"
#include "HarmonixDsp/StretcherAndPitchShifterFactory.h"
```

### 基本用法：音频缓冲区操作

`TAudioBuffer<float>` 是 Harmonix 的核心音频缓冲区类型，支持交错/非交错多声道数据。

```cpp
// 来源: Public/HarmonixDsp/AudioBuffer.h

// 创建一个非交错的立体声缓冲区，4096 帧，由缓冲区自行管理内存
HarmonixDsp::TAudioBuffer<float> Buffer;
Buffer.Configure(2, 4096, EAudioBufferCleanupMode::Delete);

// 也可以指定通道布局
Buffer.Configure(EAudioBufferChannelLayout::Stereo, 4096, EAudioBufferCleanupMode::Delete);

// 填充静音
Buffer.ZeroValidFrames();

// 填充白噪声（用于测试）
Buffer.FillWithWhiteNoise(0.5f);

// 获取峰值
float Peak = Buffer.GetPeak();        // 所有通道的最大峰值
float Ch0Peak = Buffer.GetPeak(0);    // 通道 0 的峰值

// 设置有效帧数（滑动窗口场景）
Buffer.SetFirstFrame(1000);
Buffer.SetLengthInFrames(512);

// 检查缓冲区完整性（检测内存越界）
Buffer.CheckIntegrity();
```

### 基本用法：Biquad 滤波器

```cpp
// 来源: Public/HarmonixDsp/Effects/BiquadFilter.h

using namespace Harmonix::Dsp::Effects;

// 创建滤波器系数，指定采样率
FBiquadFilterCoefs Coefs;
// 从设置生成低通滤波器系数（F0=1000Hz, Q=0.7, 采样率=48000）
FBiquadFilterSettings Settings;
Settings.Type = EBiquadFilterType::LowPass;
Settings.Freq = 1000.0f;
Settings.Q = 0.7f;
Coefs.MakeFromSettings(Settings, 48000.0f);

// 创建滤波器实例并处理音频
FBiquadFilter Filter;
float InputBuffer[128];   // 输入音频
float OutputBuffer[128];  // 输出音频

// 逐样本处理
for (int32 i = 0; i < 128; ++i)
{
    OutputBuffer[i] = Filter.Filter(InputBuffer[i], Coefs);
}

// 或者批量处理（带增益）
Filter.Process(InputBuffer, OutputBuffer, 128, Coefs, 1.0);

// 使用转置直接 II 型（数值更稳定）
Filter.ProcessTransposed(InputBuffer, OutputBuffer, 128, Coefs, 1.0);
```

### 基本用法：GainMatrix 和 Panner

```cpp
// 来源: Public/HarmonixDsp/GainMatrix.h, Public/HarmonixDsp/Panner.h

// 创建增益矩阵，将单声道信号分配到立体声输出
FGainMatrix GainMatrix(1, 2, EAudioBufferChannelLayout::Stereo);

// 设置声像：中置位置（Pan = 0.0），全增益
FPannerDetails PanDetails(EPannerMode::Stereo, 0.0f, 1.0f);
GainMatrix.Set(1.0f, PanDetails);

// 将声像应用到缓冲区
float MonoInput[256];
float LeftOutput[256];
float RightOutput[256];

// 将单声道输入分配到左声道
GainMatrix.ApplyToBuffer(MonoInput, 0, LeftOutput, 0, 256);
// 将单声道输入分配到右声道
GainMatrix.ApplyToBuffer(MonoInput, 0, RightOutput, 1, 256);

// 使用 FPanner 进行带平滑的声像处理
FPanner Panner;
Panner.Setup(PanDetails, 1, 2, EAudioBufferChannelLayout::Stereo, ESpeakerMask::Stereo, 1.0f);
Panner.SetRampTimeMs(48000.0f / 128.0f, 50.0f);  // 50ms 平滑时间
```

### 进阶用法：Fusion Sampler 采样器

Fusion Sampler 是一个完整的 MIDI 虚拟乐器，用于在运行时播放基于采样的音色。

```cpp
// 来源: Public/HarmonixDsp/FusionSampler/FusionSampler.h, FusionVoicePool.h

// 1. 获取或创建声部池
float SampleRate = 48000.0f;
FSharedFusionVoicePoolPtr VoicePool = FFusionVoicePool::GetDefault(SampleRate);

// 或者自定义配置创建
FFusionVoiceConfig Config;
Config.NumTotalVoices = 64;
Config.SoftVoiceLimit = 48;
FSharedFusionVoicePoolPtr CustomPool = FFusionVoicePool::Create(Config, SampleRate);

// 2. 创建 Fusion Sampler 实例
FFusionSampler Sampler(SampleRate);

// 3. 准备采样器（指定通道布局和最大帧数）
Sampler.Prepare(SampleRate, EAudioBufferChannelLayout::Stereo, 4096);

// 4. 加载 Fusion Patch
// UFusionPatch* Patch = LoadObject<UFusionPatch>(nullptr, TEXT("/Game/MyPatch"));
// Sampler.SetPatch(Patch->CreateProxyData(...));

// 5. 发送 MIDI NoteOn/NoteOff
FMidiVoiceId VoiceId;
Sampler.NoteOn(VoiceId, 60, 100, 0);   // C4, velocity=100, channel=0
Sampler.NoteOff(VoiceId, 60, 0);       // 释放 C4

// 6. 设置 MIDI 控制器
Sampler.SetPitchBend(0.5f, 0);         // 弯音 [-1, 1]
Sampler.SetMidiChannelVolume(-6.0f, 0.0f, 0);  // 音量 -6dB
Sampler.SetMidiChannelMute(false, 0);

// 7. 处理音频输出
TAudioBuffer<float> OutputBuffer;
OutputBuffer.Configure(EAudioBufferChannelLayout::Stereo, 4096, EAudioBufferCleanupMode::DontDelete);
// Sampler.Process(...) 由音频线程自动调用
```

### 进阶用法：延迟效果器

```cpp
// 来源: Public/HarmonixDsp/Effects/Delay.h

using namespace Harmonix::Dsp::Effects;

FDelay DelayEffect;

// 准备延迟效果器（采样率、最大通道数、最大延迟时间）
DelayEffect.Prepare(48000.0f, 2, 5000.0f);  // 5 秒最大延迟

// 配置延迟参数
DelayEffect.SetDelaySeconds(0.5f);       // 500ms 延迟
DelayEffect.SetFeedbackGain(0.4f);       // 40% 反馈
DelayEffect.SetWetGain(0.6f);            // 60% 湿信号
DelayEffect.SetDryGain(0.8f);            // 80% 干信号

// 启用节拍同步
DelayEffect.SetTimeSyncOption(ETimeSyncOption::TempoSync);
DelayEffect.SetTempo(120.0f);            // 120 BPM

// 启用湿信号滤波
DelayEffect.SetWetFilterEnabled(true);
DelayEffect.SetFilterType(EBiquadFilterType::LowPass);
DelayEffect.SetFilterFreq(2000.0f);      // 低通 2kHz
DelayEffect.SetFilterQ(1.0f);

// 处理音频
Audio::FMultichannelBufferView BufferView;
DelayEffect.Process(BufferView);
```

## Demo 示例

### 自定义音频分析器使用示例

```cpp
// MyAudioAnalyzer.h
#pragma once

#include "CoreMinimal.h"
#include "HarmonixDsp/AudioAnalysis/FFTAnalyzer.h"

class FMyAudioSpectrumAnalyzer
{
public:
    FMyAudioSpectrumAnalyzer(float InSampleRate = 48000.0f)
        : Analyzer(InSampleRate)
    {
        // 配置 FFT 分析器
        FHarmonixFFTAnalyzerSettings Settings;
        Settings.FFTSize = 1024;
        Settings.MinFrequencyHz = 20.0f;
        Settings.MaxFrequencyHz = 16000.0f;
        Settings.MelScaleBinning = true;
        Settings.NumResultBins = 128;
        Analyzer.SetSettings(Settings);
    }

    void AnalyzeBuffer(const Audio::FAlignedFloatBuffer& InAudioBuffer)
    {
        Analyzer.Process(InAudioBuffer, Results);

        // 使用频谱数据
        for (int32 i = 0; i < Results.Spectrum.Num(); ++i)
        {
            // Results.Spectrum[i] 包含每个频段的能量值
        }
    }

    void Reset()
    {
        Analyzer.Reset();
    }

private:
    Harmonix::Dsp::AudioAnalysis::FFFTAnalyzer Analyzer;
    FHarmonixFFTAnalyzerResults Results;
};
```

### 自定义 Biquad 滤波器效果器示例

```cpp
// MyFilterEffect.h
#pragma once

#include "CoreMinimal.h"
#include "HarmonixDsp/Effects/BiquadFilter.h"
#include "HarmonixDsp/AudioBuffer.h"

class FMyMultiBandFilter
{
public:
    void Prepare(float InSampleRate)
    {
        SampleRate = InSampleRate;

        // 设置低频带通滤波器
        Harmonix::Dsp::Effects::FBiquadFilterSettings LowSettings;
        LowSettings.Type = EBiquadFilterType::LowPass;
        LowSettings.Freq = 300.0f;
        LowSettings.Q = 0.7f;
        LowCoefs.MakeFromSettings(LowSettings, SampleRate);

        // 设置高频带通滤波器
        Harmonix::Dsp::Effects::FBiquadFilterSettings HighSettings;
        HighSettings.Type = EBiquadFilterType::HighPass;
        HighSettings.Freq = 4000.0f;
        HighSettings.Q = 0.7f;
        HighCoefs.MakeFromSettings(HighSettings, SampleRate);
    }

    void ProcessBuffer(float* InOutData, int32 NumFrames, int32 NumChannels)
    {
        // 对每个通道应用低通滤波
        for (int32 Ch = 0; Ch < NumChannels; ++Ch)
        {
            // 为每个通道创建独立的滤波器状态
            Harmonix::Dsp::Effects::FBiquadFilter ChannelFilter;

            // 分离通道数据处理
            TArray<float> ChannelData;
            ChannelData.SetNum(NumFrames);
            for (int32 i = 0; i < NumFrames; ++i)
            {
                ChannelData[i] = InOutData[i * NumChannels + Ch];
            }

            // 应用低通滤波
            ChannelFilter.Process(
                ChannelData.GetData(),
                ChannelData.GetData(),
                NumFrames,
                LowCoefs,
                1.0
            );

            // 写回
            for (int32 i = 0; i < NumFrames; ++i)
            {
                InOutData[i * NumChannels + Ch] = ChannelData[i];
            }
        }
    }

    void SetLowFreq(float Freq)
    {
        Harmonix::Dsp::Effects::FBiquadFilterSettings Settings;
        Settings.Type = EBiquadFilterType::LowPass;
        Settings.Freq = Freq;
        Settings.Q = 0.7f;
        LowCoefs.MakeFromSettings(Settings, SampleRate);
    }

private:
    float SampleRate = 48000.0f;
    Harmonix::Dsp::Effects::FBiquadFilterCoefs LowCoefs;
    Harmonix::Dsp::Effects::FBiquadFilterCoefs HighCoefs;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册和发现（Fusion Patch 资产管理） |
| `UnrealEd` | 编辑器集成（资产导入/导出、属性编辑） |
| `MetasoundEngine` | MetaSound 集成（采样器/DSP 节点暴露为 MetaSound） |
| `MetasoundFrontend` | MetaSound 前端框架 |
| `AudioMixer` | 音频混合器基础框架 |
| `SignalProcessing` | 信号处理基础库（FFT、窗口函数等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复声部键区排序并增加空指针防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 为 FusionPatch 代理添加用户对象用于活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**活跃维护** — Harmonix 插件正处于积极开发和维护中。

- **创建时间**：2024 年 1 月，从 Experimental 迁移到 Runtime，约 1 年历史
- **更新频率**：最近 1 个月内有多次提交，涉及 bug 修复、API 清理和功能增强
- **维护状态**：活跃维护中，Epic Harmonix GenTech 团队持续开发
- **已知限制**：
  - `IsExperimentalVersion = true`，API 可能发生变化
  - `EnabledByDefault = false`，需要手动在项目设置中启用
  - 部分模块依赖 `UnrealEd`（标注为 Runtime 但实际需要编辑器模块），可能影响纯运行时构建
  - Pitch Shifter 接口标记了 `UE_DEPRECATED(5.8)` 的旧方法，正在过渡期
- **推荐使用**：如果你在开发音乐/节奏类游戏，该插件提供了非常专业的音频处理能力。但注意它是实验性插件，API 可能在版本间变化，建议做好版本适配准备。核心的 Fusion Sampler 和 DSP 效果器功能已经相当成熟和稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 官方文档（暂无）
- 测试用例位于 `Source/HarmonixDspTests/`、`Source/HarmonixMetasoundTests/`、`Source/HarmonixMidiTests/` 目录