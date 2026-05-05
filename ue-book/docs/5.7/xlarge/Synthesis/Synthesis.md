# Synthesis and DSP Effects

> A variety of realtime synthesizers and DSP source and submix effects.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI样式资源、合成器预设） |
| 模块 | `Synthesis` (Runtime), `SynthesisEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-01-10 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis) | |

## 用途

Synthesis 是 UE5 内置的**音频合成与 DSP 效果**插件，提供了一套完整的运行时音频处理工具链。它解决的核心问题是：**在不依赖第三方中间件的情况下，让开发者能够在引擎内直接创建、处理和操控音频**。

插件包含三大类功能：

1. **实时合成器组件**（Synth Components）：可挂载到 Actor 上的音频生成组件，包括正弦波发生器、波表合成器、颗粒合成器和采样播放器，用于程序化生成音频或播放音频素材。

2. **源效果**（Source Effects）：作用于单个 Sound Wave 的 DSP 效果链，包括压缩器/限制器/扩展器/门限、EQ 均衡器、滤波器、延迟、合唱、相位器、环形调制、失真、卷积混响等 15+ 种效果。

3. **子混音效果**（Submix Effects）：作用于 Submix 总线的 DSP 效果，包括延迟、滤波器、Flexiverb 混响、立体声延迟、多抽头延迟、卷积混响、立体声转四声道等。

此外还提供了专用的 Slate UI 控件（旋钮、2D 滑块），用于构建音频相关的编辑器工具或运行时音频界面。

## 使用场景

- 你在做一个**音乐游戏**，需要程序化生成音调 → 用 `USynthComponentToneGenerator`
- 你需要**播放和操控音频采样**（变速、定位、擦洗）→ 用 `USynthSamplePlayer`
- 你要实现**颗粒合成**效果（声音纹理、氛围音效）→ 用 `UGranularSynth`
- 你需要给音效添加**压缩、EQ、滤波、延迟、失真**等效果 → 用对应的 Source Effect Preset
- 你要在 Submix 总线上添加**混响、延迟、滤波**等全局效果 → 用对应的 Submix Effect Preset
- 你需要**基于脉冲响应的真实空间混响** → 用 `USourceEffectConvolutionReverbPreset`
- 你在构建**音频编辑器工具**，需要专业的旋钮和滑块控件 → 用 `USynthKnob` / `USynth2DSlider`

## 蓝图用法

### 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLogFrequency` | 将线性值映射为对数频率（适合线性滑块控制频率） | `USynthesisUtilitiesBlueprintFunctionLibrary` |
| `GetLinearFrequency` | 将对数频率映射回线性值 | `USynthesisUtilitiesBlueprintFunctionLibrary` |

### 合成器组件

#### 音调发生器（Tone Generator）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetFrequency` | 设置正弦波频率（Hz） | `USynthComponentToneGenerator` |
| `SetVolume` | 设置音量（0-1 线性） | `USynthComponentToneGenerator` |

#### 采样播放器（Sample Player）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSoundWave` | 加载并设置要播放的 SoundWave | `USynthSamplePlayer` |
| `SetPitch` | 设置播放音高，支持平滑过渡时间 | `USynthSamplePlayer` |
| `SeekToTime` | 跳转到指定时间位置 | `USynthSamplePlayer` |
| `SetScrubMode` | 启用/禁用擦洗模式 | `USynthSamplePlayer` |
| `GetSampleDuration` | 获取采样总时长（秒） | `USynthSamplePlayer` |
| `GetCurrentPlaybackProgressPercent` | 获取当前播放进度百分比 | `USynthSamplePlayer` |
| `IsLoaded` | 检查采样是否已加载完成 | `USynthSamplePlayer` |

#### 颗粒合成器（Granular Synth）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSoundWave` | 加载音频素材用于颗粒合成 | `UGranularSynth` |
| `NoteOn` | 触发音符（频率、力度、持续时间） | `UGranularSynth` |
| `NoteOff` | 停止音符 | `UGranularSynth` |
| `SetGrainsPerSecond` | 设置每秒生成的颗粒数 | `UGranularSynth` |
| `SetGrainPitch` | 设置颗粒音高及随机范围 | `UGranularSynth` |
| `SetPlaybackSpeed` | 设置播放头移动速度 | `UGranularSynth` |
| `SetGrainEnvelopeType` | 设置颗粒包络类型（矩形、三角、高斯等） | `UGranularSynth` |
| `SetAttackTime` / `SetDecayTime` / `SetSustainGain` / `SetReleaseTimeMsec` | 设置 ADSR 包络参数 | `UGranularSynth` |

### 源效果预设（Source Effect Presets）

每个源效果预设都有 `SetSettings` 蓝图可调用函数，用于运行时修改效果参数。

| 效果预设类 | 功能 | 设置结构体 |
|---|---|---|
| `USourceEffectBitCrusherPreset` | 位压缩（降低采样率/位深度） | `FSourceEffectBitCrusherSettings` |
| `USourceEffectDynamicsProcessorPreset` | 动态处理（压缩/限制/扩展/门限） | `FSourceEffectDynamicsProcessorSettings` |
| `USourceEffectEQPreset` | 多频段参量均衡器 | `FSourceEffectEQSettings` |
| `USourceEffectEnvelopeFollowerPreset` | 包络跟踪器 | `FSourceEffectEnvelopeFollowerSettings` |
| `USourceEffectFilterPreset` | 滤波器（LP/HP/BP/BS，支持音频总线调制） | `FSourceEffectFilterSettings` |
| `USourceEffectFoldbackDistortionPreset` | 折叠失真 | `FSourceEffectFoldbackDistortionSettings` |
| `USourceEffectMidSideSpreaderPreset` | 中/侧声场扩展 | `FSourceEffectMidSideSpreaderSettings` |
| `USourceEffectPannerPreset` | 声像控制 | `FSourceEffectPannerSettings` |
| `USourceEffectPhaserPreset` | 相位器效果 | `FSourceEffectPhaserSettings` |
| `USourceEffectRingModulationPreset` | 环形调制 | `FSourceEffectRingModulationSettings` |
| `USourceEffectSimpleDelayPreset` | 简单延迟（支持基于距离的延迟） | `FSourceEffectSimpleDelaySettings` |
| `USourceEffectStereoDelayPreset` | 立体声延迟（Normal/Cross/PingPong） | `FSourceEffectStereoDelaySettings` |
| `USourceEffectWaveShaperPreset` | 波形整形 | `FSourceEffectWaveShaperSettings` |
| `USourceEffectConvolutionReverbPreset` | 卷积混响（基于脉冲响应） | `FSourceEffectConvolutionReverbSettings` |

### 子混音效果预设（Submix Effect Presets）

| 效果预设类 | 功能 | 设置结构体 |
|---|---|---|
| `USubmixEffectDelayPreset` | 延迟效果 | `FSubmixEffectDelaySettings` |
| `USubmixEffectFilterPreset` | 滤波器 | `FSubmixEffectFilterSettings` |
| `USubmixEffectFlexiverbPreset` | 轻量级混响（适合小空间） | `FSubmixEffectFlexiverbSettings` |
| `USubmixEffectStereoDelayPreset` | 立体声延迟 | `FSubmixEffectStereoDelaySettings` |
| `USubmixEffectStereoToQuadPreset` | 立体声转四声道 | `FSubmixEffectStereoToQuadSettings` |
| `USubmixEffectTapDelayPreset` | 多抽头延迟 | `FSubmixEffectTapDelaySettings` |

### UI 控件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValue` / `SetValue` | 获取/设置旋钮值（0-1） | `USynthKnob` |
| `GetValue` / `SetValue` | 获取/设置 2D 滑块值（FVector2D） | `USynth2DSlider` |

### 使用示例（蓝图描述）

**创建一个带滤波器的音调发生器：**

1. 在 Actor 上添加 `SynthComponentToneGenerator` 组件
2. 设置 `Frequency` 为 440（A4 音高），`Volume` 为 0.5
3. 创建 `SourceEffectFilterPreset` 资产，设置 `FilterType` 为 LowPass，`CutoffFrequency` 为 2000
4. 在 Sound Effect Source Chain 中引用该 Filter Preset

**创建一个颗粒合成器并控制播放：**

1. 在 Actor 上添加 `GranularSynth` 组件
2. 调用 `SetSoundWave` 加载一个音频文件
3. 调用 `NoteOn`（Note=60, Velocity=100, Duration=-1）开始持续播放
4. 通过 `SetGrainsPerSecond`（如 50）和 `SetGrainPitch`（BasePitch=0, PitchRange=(-12, 12)）调整颗粒参数
5. 调用 `NoteOff` 停止播放

## C++ 用法

### 头文件引入

```cpp
// 合成器组件
#include "SynthComponents/SynthComponentToneGenerator.h"
#include "SynthComponents/SynthComponentWaveTable.h"
#include "SynthComponents/SynthComponentGranulator.h"

// 源效果
#include "SourceEffects/SourceEffectFilter.h"
#include "SourceEffects/SourceEffectDynamicsProcessor.h"
#include "SourceEffects/SourceEffectEQ.h"
#include "SourceEffects/SourceEffectStereoDelay.h"
#include "SourceEffects/SourceEffectConvolutionReverb.h"

// 子混音效果
#include "SubmixEffects/SubmixEffectDelay.h"
#include "SubmixEffects/SubmixEffectFilter.h"
#include "SubmixEffects/SubmixEffectTapDelay.h"

// UI 控件
#include "UI/SynthKnob.h"
#include "UI/Synth2DSlider.h"

// 工具函数
#include "SynthesisBlueprintUtilities.h"

// DSP 算法（底层）
#include "EpicSynth1.h"
#include "MonoWaveTable.h"
#include "Flexiverb.h"
#include "ConvolutionReverb.h"
```

### 基本用法：使用音调发生器组件

```cpp
// 在 Actor 头文件中
#include "SynthComponents/SynthComponentToneGenerator.h"

UPROPERTY(VisibleAnywhere)
TObjectPtr<USynthComponentToneGenerator> ToneGenerator;

// BeginPlay 中初始化
ToneGenerator = CreateDefaultSubobject<USynthComponentToneGenerator>(TEXT("ToneGen"));
ToneGenerator->Frequency = 440.0f;  // A4
ToneGenerator->Volume = 0.5f;
ToneGenerator->SetupAttachment(RootComponent);

// 运行时修改
ToneGenerator->SetFrequency(880.0f);  // 升高一个八度
ToneGenerator->SetVolume(0.3f);
```

### 基本用法：创建和配置源效果

```cpp
// 创建滤波器效果预设
USourceEffectFilterPreset* FilterPreset = NewObject<USourceEffectFilterPreset>();

FSourceEffectFilterSettings FilterSettings;
FilterSettings.FilterCircuit = ESourceEffectFilterCircuit::StateVariable;
FilterSettings.FilterType = ESourceEffectFilterType::LowPass;
FilterSettings.CutoffFrequency = 1000.0f;
FilterSettings.FilterQ = 2.0f;
FilterSettings.bFilterEnabled = true;

FilterPreset->SetSettings(FilterSettings);

// 将预设添加到 Sound Effect Source Chain
// SoundEffectSourceChain->AddEffect(FilterPreset);
```

### 基本用法：使用动态处理器（压缩器）

```cpp
#include "SourceEffects/SourceEffectDynamicsProcessor.h"

USourceEffectDynamicsProcessorPreset* CompressorPreset = NewObject<USourceEffectDynamicsProcessorPreset>();

FSourceEffectDynamicsProcessorSettings CompSettings;
CompSettings.DynamicsProcessorType = ESourceEffectDynamicsProcessorType::Compressor;
CompSettings.PeakMode = ESourceEffectDynamicsPeakMode::RootMeanSquared;
CompSettings.ThresholdDb = -12.0f;
CompSettings.Ratio = 4.0f;
CompSettings.AttackTimeMsec = 10.0f;
CompSettings.ReleaseTimeMsec = 100.0f;
CompSettings.KneeBandwidthDb = 6.0f;
CompSettings.InputGainDb = 0.0f;
CompSettings.OutputGainDb = 3.0f;
CompSettings.bStereoLinked = true;
CompSettings.bAnalogMode = true;

CompressorPreset->SetSettings(CompSettings);
```

### 进阶用法：使用卷积混响

```cpp
#include "SourceEffects/SourceEffectConvolutionReverb.h"
#include "EffectConvolutionReverb.h"

// 创建脉冲响应资产
UAudioImpulseResponse* IRAsset = NewObject<UAudioImpulseResponse>();
// 加载脉冲响应数据（通常从文件导入）
// IRAsset->ImpulseResponse = LoadedSamples;
// IRAsset->NumChannels = 2;
// IRAsset->SampleRate = 44100;
IRAsset->NormalizationVolumeDb = -24.0f;
IRAsset->bTrueStereo = true;

// 创建卷积混响预设
USourceEffectConvolutionReverbPreset* ConvReverbPreset = NewObject<USourceEffectConvolutionReverbPreset>();
ConvReverbPreset->SetImpulseResponse(IRAsset);

FSourceEffectConvolutionReverbSettings ConvSettings;
ConvSettings.WetVolumeDb = -6.0f;
ConvSettings.DryVolumeDb = 0.0f;
ConvSettings.bBypass = false;
ConvReverbPreset->SetSettings(ConvSettings);
```

### 进阶用法：使用多抽头延迟（Submix Effect）

```cpp
#include "SubmixEffects/SubmixEffectTapDelay.h"

USubmixEffectTapDelayPreset* TapDelayPreset = NewObject<USubmixEffectTapDelayPreset>();

FSubmixEffectTapDelaySettings TapSettings;
TapSettings.MaximumDelayLength = 5000.0f;
TapSettings.InterpolationTime = 200.0f;

// 添加多个延迟抽头
FTapDelayInfo Tap1;
Tap1.TapLineMode = ETapLineMode::Panning;
Tap1.DelayLength = 500.0f;
Tap1.Gain = -6.0f;
Tap1.PanInDegrees = -45.0f;
TapSettings.Taps.Add(Tap1);

FTapDelayInfo Tap2;
Tap2.TapLineMode = ETapLineMode::Panning;
Tap2.DelayLength = 1000.0f;
Tap2.Gain = -12.0f;
Tap2.PanInDegrees = 45.0f;
TapSettings.Taps.Add(Tap2);

TapDelayPreset->SetSettings(TapSettings);
```

### 进阶用法：使用滤波器音频总线调制

```cpp
#include "SourceEffects/SourceEffectFilter.h"

// 创建音频总线用于调制
UAudioBus* ModulationBus = UAudioBus::NewAudioBus(GetWorld(), 2);

USourceEffectFilterPreset* FilterPreset = NewObject<USourceEffectFilterPreset>();

FSourceEffectFilterSettings FilterSettings;
FilterSettings.FilterCircuit = ESourceEffectFilterCircuit::Ladder;
FilterSettings.FilterType = ESourceEffectFilterType::LowPass;
FilterSettings.CutoffFrequency = 2000.0f;
FilterSettings.FilterQ = 3.0f;
FilterSettings.bFilterEnabled = true;

// 配置音频总线调制
FSourceEffectFilterAudioBusModulationSettings BusModSettings;
BusModSettings.AudioBus = ModulationBus;
BusModSettings.FilterParam = ESourceEffectFilterParam::FilterFrequency;
BusModSettings.EnvelopeFollowerAttackTimeMsec = 10;
BusModSettings.EnvelopeFollowerReleaseTimeMsec = 100;
BusModSettings.MinFrequencyModulation = -24.0f;
BusModSettings.MaxFrequencyModulation = 24.0f;
BusModSettings.EnvelopeGainMultiplier = 1.0f;

FilterSettings.AudioBusModulation.Add(BusModSettings);
FilterPreset->SetSettings(FilterSettings);
```

## Demo 示例

### 最小示例：带延迟效果的音调发生器

**MySynthActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SynthComponents/SynthComponentToneGenerator.h"
#include "SourceEffects/SourceEffectSimpleDelay.h"
#include "MySynthActor.generated.h"

UCLASS()
class AMySynthActor : public AActor
{
    GENERATED_BODY()

public:
    AMySynthActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<USynthComponentToneGenerator> ToneGenerator;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TObjectPtr<USourceEffectSimpleDelayPreset> DelayPreset;

    UFUNCTION(BlueprintCallable)
    void PlayTone(float InFrequency, float InVolume);

    UFUNCTION(BlueprintCallable)
    void StopTone();
};
```

**MySynthActor.cpp**
```cpp
#include "MySynthActor.h"

AMySynthActor::AMySynthActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建音调发生器组件
    ToneGenerator = CreateDefaultSubobject<USynthComponentToneGenerator>(TEXT("ToneGenerator"));
    RootComponent = ToneGenerator;
    ToneGenerator->Frequency = 440.0f;
    ToneGenerator->Volume = 0.5f;

    // 创建延迟效果预设
    DelayPreset = CreateDefaultSubobject<USourceEffectSimpleDelayPreset>(TEXT("DelayPreset"));

    FSourceEffectSimpleDelaySettings DelaySettings;
    DelaySettings.DelayAmount = 0.3f;       // 300ms 延迟
    DelaySettings.Feedback = 0.4f;          // 40% 反馈
    DelaySettings.DryAmount = 0.8f;         // 干信号
    DelaySettings.WetAmount = 0.5f;         // 湿信号
    DelaySettings.bDelayBasedOnDistance = false;
    DelayPreset->SetSettings(DelaySettings);
}

void AMySynthActor::PlayTone(float InFrequency, float InVolume)
{
    ToneGenerator->SetFrequency(InFrequency);
    ToneGenerator->SetVolume(InVolume);
}

void AMySynthActor::StopTone()
{
    ToneGenerator->SetVolume(0.0f);
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "Synthesis"  // Synthesis 插件的 Runtime 模块
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioSynesthesiaCore` | 音频分析核心库，Synthesis 的 Build.cs 中声明的依赖 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。插件级别依赖 `AudioSynesthesia` 插件。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `21534ae4` | Fix Chorus Modulation #jira UE-289485 | 修复合唱效果的调制问题，属于 bug 修复 |
| 近期 | `2dbbc22c` | Remove source effect compressor bypass change | 移除压缩器旁路相关的改动，可能是回退有问题的变更 |
| 近期 | `eff61998` | Renaming EQ source effect Enable property; Enabling Dynamic source effect Bypass property | API 改进：重命名 EQ 的 Enable 属性使其语义更清晰，同时修复动态处理器的 Bypass 属性 |

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：2017 年，已有约 8 年历史，是 UE 音频系统的核心组件
- **更新频率**：近期仍有功能性更新和 bug 修复，说明 Epic 持续维护
- **代码质量**：代码结构清晰，Source Effect 和 Submix Effect 遵循统一的 Preset 模式，DSP 算法封装良好
- **API 稳定性**：近期 commit 显示 Epic 在逐步完善 API 命名（如 EQ 的 Enable 属性重命名），说明 API 仍在演进中
- **已知限制**：Flexiverb 在较长衰减时间下会产生金属质感；卷积混响需要手动管理脉冲响应资产
- **推荐程度**：✅ **强烈推荐**。这是 UE5 官方音频效果的首选方案，覆盖了绝大多数常见的音频处理需求，且默认启用，无需额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis)
- [AudioSynesthesia 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia)（关联插件）