# Synthesis and DSP Effects

> A variety of realtime synthesizers and DSP source and submix effects.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 合成器与 DSP 效果 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Synthesis` (Runtime), `SynthesisEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-01-10 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis) | |

## 用途

Synthesis 是 UE5 内置的音频合成与处理插件，为开发者提供**实时音频生成和 DSP 效果处理**的完整工具链。它解决的核心问题是：如何在运行时从零创建和处理音频，而不是依赖预先录制的音频文件。

该插件包含：
- **多复音虚拟模拟合成器**（ModularSynth）：模拟经典硬件合成器的振荡器、滤波器、包络和 LFO
- **单音波表合成器**（MonoWaveTable）：基于波表的合成，支持任意波形
- **源效果**（Source Effects）：直接作用于音频源的 DSP 处理（压缩、均衡、滤波、失真等）
- **子混音效果**（Submix Effects）：作用于混音总线的效果（延迟、卷积混响、滤波器等）
- **音频脉冲响应**（Audio Impulse Response）：用于卷积混响的 IR 资产
- **调制系统**：LFO、包络跟随器等调制源

该插件的存在使得游戏开发者可以在蓝图中直接创建程序化音频，无需编写 C++ 音频代码。

## 使用场景

- 你需要在游戏中实现**程序化音效**（如武器射击、爆炸、环境音随参数动态变化）→ 用 ModularSynth 或 Source Effects
- 你需要创建**动态音乐系统**（MIDI 控制的合成器、音序器）→ 用 ModularSynth 的 MIDI 接口
- 你需要对音频添加**实时 DSP 处理**（混响、延迟、滤波、压缩）→ 用 Submix Effects 和 Source Effects
- 你需要实现**波表合成**（扫描不同波形生成声音）→ 用 MonoWaveTable
- 你需要实现**卷积混响**（使用真实空间的脉冲响应）→ 用 AudioImpulseResponse + ConvolutionReverb
- 你在做一个**音频可视化或音频实验项目** → 整个 Synthesis 插件都是为此设计的

## 蓝图用法

### 核心节点

#### 合成器组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Synth Preset` | 设置模块化合成器预设参数 | `UModularSynthComponent` |
| `Note On` | 触发音符（MIDI Note） | `UModularSynthComponent` |
| `Note Off` | 释放音符 | `UModularSynthComponent` |
| `Set Oscillator Gain` | 设置振荡器增益 | `UModularSynthComponent` |
| `Set Oscillator Frequency Mod` | 设置振荡器频率调制 | `UModularSynthComponent` |
| `Set Oscillator Type` | 设置振荡器波形类型 | `UModularSynthComponent` |
| `Set Filter Settings` | 设置滤波器参数（截止频率、共振等） | `UModularSynthComponent` |
| `Set Enable Legato` | 启用/禁用连奏模式 | `UModularSynthComponent` |
| `Set Enable Unison` | 启用/禁用齐奏模式 | `UModularSynthComponent` |
| `Set Enable Patch` | 启用/禁用补丁路由 | `UModularSynthComponent` |
| `Set Spread` | 设置立体声扩展 | `UModularSynthComponent` |
| `Set LFO Patch` | 设置 LFO 路由 | `UModularSynthComponent` |
| `Set LFO Frequency` | 设置 LFO 频率 | `UModularSynthComponent` |
| `Set LFO Gain` | 设置 LFO 深度 | `UModularSynthComponent` |
| `Set LFO Type` | 设置 LFO 波形类型 | `UModularSynthComponent` |
| `Set Attack Time` | 设置包络起音时间 | `UModularSynthComponent` |
| `Set Decay Time` | 设置包络衰减时间 | `UModularSynthComponent` |
| `Set Sustain Gain` | 设置包络持续增益 | `UModularSynthComponent` |
| `Set Release Time` | 设置包络释放时间 | `UModularSynthComponent` |

#### 波表合成器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Wave Table Position` | 设置波表扫描位置 | `UMonoWaveTableSynthComponent` |
| `Set Frequencies` | 设置基频 | `UMonoWaveTableSynthComponent` |
| `Set ADSR Attack Time` | 设置 ADSR 起音 | `UMonoWaveTableSynthComponent` |
| `Set ADSR Decay Time` | 设置 ADSR 衰减 | `UMonoWaveTableSynthComponent` |
| `Set ADSR Sustain Gain` | 设置 ADSR 持续 | `UMonoWaveTableSynthComponent` |
| `Set ADSR Release Time` | 设置 ADSR 释放 | `UMonoWaveTableSynthComponent` |
| `Note On` | 触发音符 | `UMonoWaveTableSynthComponent` |
| `Note Off` | 释放音符 | `UMonoWaveTableSynthComponent` |
| `Set Low Pass Filter Frequency` | 设置低通滤波截止频率 | `UMonoWaveTableSynthComponent` |
| `Set Low Pass Filter Resonance` | 设置低通滤波共振 | `UMonoWaveTableSynthComponent` |

#### 子混音效果

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Settings` | 设置延迟效果参数 | `USubmixEffectDelayPreset` |
| `Set Settings` | 设置滤波器效果参数 | `USubmixEffectFilterPreset` |
| `Set Settings` | 设置卷积混响参数 | `USubmixEffectConvolutionReverbPreset` |
| `Set Settings` | 设置立体声延迟参数 | `USubmixEffectStereoDelayPreset` |
| `Set Settings` | 设置 Flexiverb 混响参数 | `USubmixEffectFlexiverbPreset` |

#### 源效果

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Settings` | 设置动态处理器参数（压缩/限制/扩展） | `USourceEffectDynamicsProcessorPreset` |
| `Set Settings` | 设置均衡器参数 | `USourceEffectEQPreset` |
| `Set Settings` | 设置滤波器参数 | `USourceEffectFilterPreset` |
| `Set Settings` | 设置简单延迟参数 | `USourceEffectSimpleDelayPreset` |
| `Set Settings` | 设置立体声延迟参数 | `USourceEffectStereoDelayPreset` |
| `Set Settings` | 设置失真参数 | `USourceEffectFoldbackDistortionPreset` |
| `Set Settings` | 设置波形整形参数 | `USourceEffectWaveShaperPreset` |
| `Set Settings` | 设置相位器参数 | `USourceEffectPhaserPreset` |
| `Set Settings` | 设置环形调制参数 | `USourceEffectRingModulationPreset` |

#### 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Chord Note` | 根据调式获取和弦音 | `UModularSynthLibrary` |
| `Get Scale Degree Name` | 获取音阶名称 | `UModularSynthLibrary` |

### 使用示例（蓝图描述）

**创建一个 MIDI 控制的合成器：**

1. 在 Actor 上添加 `ModularSynthComponent`
2. 创建 `UModularSynthPreset` 资产，配置振荡器类型、滤波器截止频率、ADSR 包络等参数
3. 使用 `Set Synth Preset` 节点将预设应用到组件
4. 在需要发声时调用 `Note On`（传入 MIDI Note Number 和 Velocity）
5. 在需要停止时调用 `Note Off`（传入相同的 MIDI Note Number）
6. 可在运行时通过 `Set Filter Settings`、`Set LFO Frequency` 等节点动态调整参数

**添加混响效果链：**

1. 创建 `SubmixEffectConvolutionReverbPreset` 资产并加载脉冲响应波形
2. 创建 `SourceEffectDynamicsProcessorPreset` 用于压缩
3. 在子混音的 Effect Chain 中按顺序添加这两个效果
4. 运行时通过 `Set Settings` 节点调整参数

## C++ 用法

### 头文件引入

```cpp
#include "SynthComponent.h"
#include "MonoWaveTableSynthPreset.h"
#include "ModularSynthPreset.h"
#include "SubmixEffectDelay.h"
#include "SubmixEffectFilter.h"
#include "SubmixEffectConvolutionReverb.h"
#include "SourceEffectDynamicsProcessor.h"
#include "SourceEffectFilter.h"
#include "SourceEffectEQ.h"
```

### 基本用法

**创建自定义合成器组件（继承 USynthComponent）：**

```cpp
// 来源: Engine/Plugins/Runtime/Synthesis/Source/Synthesis/Classes/SynthComponents/
#include "SynthComponent.h"
#include "Kismet/GameplayStatics.h"

UCLASS()
class UMySynthComponent : public USynthComponent
{
    GENERATED_BODY()

public:
    // 初始化合成器的 DSP 图
    virtual bool Init(int32& SampleRate) override;

    // 每帧调用，返回生成的音频 buffer
    virtual int32 OnGenerateAudio(float* OutAudio, int32 NumSamples) override;

private:
    float Frequency = 440.0f;
    float Phase = 0.0f;
};
```

```cpp
// MySynthComponent.cpp
bool UMySynthComponent::Init(int32& SampleRate)
{
    // 使用当前音频设备采样率
    SampleRate = GetSampleRate();
    return true;
}

int32 UMySynthComponent::OnGenerateAudio(float* OutAudio, int32 NumSamples)
{
    const float PhaseIncrement = Frequency / GetSampleRate();

    for (int32 i = 0; i < NumSamples; ++i)
    {
        // 简单的正弦波生成
        OutAudio[i] = FMath::Sin(2.0f * PI * Phase);
        Phase += PhaseIncrement;
        if (Phase >= 1.0f) Phase -= 1.0f;
    }

    return NumSamples;
}
```

**使用 ModularSynth 的预设系统：**

```cpp
// 来源: Engine/Plugins/Runtime/Synthesis/Source/Synthesis/Classes/ModularSynthPreset.h
#include "ModularSynthPreset.h"

// 创建预设
FModularSynthPreset Preset;
Preset.Osc1Type = ESynth1OscillatorType::Saw;
Preset.Osc2Type = ESynth1OscillatorType::Square;
Preset.Osc1Gain = 0.5f;
Preset.Osc2Gain = 0.3f;
Preset.FilterFrequency = 2000.0f;
Preset.FilterQ = 1.5f;
Preset.EnvAttackTime = 0.01f;
Preset.EnvDecayTime = 0.1f;
Preset.EnvSustainGain = 0.7f;
Preset.EnvReleaseTime = 0.3f;
```

### 进阶用法

**使用 SynthCommand 跨线程安全地修改参数：**

```cpp
// 来源: SynthCommand 接口用于从游戏线程安全地向音频渲染线程传递参数变更
// 这是 Synthesis 插件的核心设计模式

// 在游戏线程中修改参数（安全方式）
SynthComponent->SetSynthPreset(Preset);

// 触发音符
SynthComponent->NoteOn(60, 1.0f); // MIDI Note 60 (Middle C), Velocity 1.0
SynthComponent->NoteOff(60, true); // 释放音符，发送 Note Off

// 动态调整滤波器
FSynthFilterSettings FilterSettings;
FilterSettings.FilterFrequency = 1500.0f;
FilterSettings.FilterQ = 2.0f;
FilterSettings.FilterType = ESynthFilterType::LowPass;
```

**使用音频脉冲响应进行卷积混响：**

```cpp
// 来源: AudioImpulseResponseAsset.h
#include "AudioImpulseResponseAsset.h"

// 创建脉冲响应资产（需要加载单声道 PCM 波形数据）
UAudioImpulseResponse* IR = NewObject<UAudioImpulseResponse>();
// IR 需要从 SoundWave 加载 PCM 数据
```

**使用 MonoWaveTable 的波表数据：**

```cpp
// 来源: MonoWaveTableSynthPreset.h
#include "MonoWaveTableSynthPreset.h"

// 创建波表预设
FMonoWaveTableSynthPreset WaveTablePreset;
WaveTablePreset.Amplitude = 1.0f;
// 设置波表曲线数据（0-1 范围的波形采样点）
```

## Demo 示例

**自定义锯齿波合成器组件：**

```cpp
// MySawSynthComponent.h
#pragma once

#include "SynthComponent.h"
#include "MySawSynthComponent.generated.h"

UCLASS(ClassGroup = Synth, meta = (BlueprintSpawnableComponent))
class MYGAME_API UMySawSynthComponent : public USynthComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Synth")
    float SawFrequency = 440.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Synth")
    float Volume = 0.5f;

protected:
    virtual bool Init(int32& SampleRate) override;
    virtual int32 OnGenerateAudio(float* OutAudio, int32 NumSamples) override;

private:
    float Phase = 0.0f;
    int32 CurrentSampleRate = 48000;
};
```

```cpp
// MySawSynthComponent.cpp
#include "MySawSynthComponent.h"

bool UMySawSynthComponent::Init(int32& SampleRate)
{
    CurrentSampleRate = GetSampleRate();
    SampleRate = CurrentSampleRate;
    return true;
}

int32 UMySawSynthComponent::OnGenerateAudio(float* OutAudio, int32 NumSamples)
{
    const float PhaseInc = SawFrequency / static_cast<float>(CurrentSampleRate);

    for (int32 i = 0; i < NumSamples; ++i)
    {
        // 锯齿波: 输出值从 -1 线性增长到 +1，然后重置
        float SawSample = 2.0f * Phase - 1.0f;
        OutAudio[i] = SawSample * Volume;

        Phase += PhaseInc;
        if (Phase >= 1.0f)
        {
            Phase -= 1.0f;
        }
    }

    return NumSamples;
}
```

## 模块依赖

从 Build.cs 分析，该插件的模块依赖如下：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesiaCore` | 音频感知分析核心库（Synthesis 依赖，用于音频特征提取和分析） |

> 注意：Synthesis 通过 .uplugin 的 Plugins 字段声明了对 `AudioSynesthesia` 插件的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断到 float 的编译警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单入口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-03-10 | `22707c32` | [Subsonic] Generator sources can be played/stopped through subsonic actions, and get cleaned up when | Subsonic 生成器源支持通过 Subsonic 动作播放/停止，并在销毁时清理 |
| 2026-03-09 | `a5cf226b` | Rename FModulationDestination::UpdateModulators to SetModulators | 重命名调制目标的更新函数为 SetModulators |

### 维护评价

**活跃维护中** ✅

Synthesis 插件创建于 2017 年 1 月，至今约 9 年历史，但仍在**积极维护**中：

- **最近更新**：2026 年 5 月仍有功能性更新和代码质量改进
- **更新频率**：近 3 个月内有多次提交，涵盖新功能（Subsonic 集成）、代码现代化（UE_LOGF 迁移）和编译修复
- **稳定性**：作为 Epic 官方维护的音频核心插件，经历了 9 年的迭代，API 稳定成熟
- **注意事项**：
  - 部分 API 经历过重命名（如 `UpdateModulators` → `SetModulators`），需注意版本兼容性
  - 该插件对音频渲染线程安全性有严格要求，跨线程参数传递需使用 SynthCommand 模式
  - 虽然标记为 `IsBetaVersion: false`，但某些高级功能可能仍有行为变更

**推荐使用**：对于需要实时音频合成或 DSP 处理的项目，这是 UE5 官方推荐的方案，API 完善且有长期维护保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis)
- [官方文档]()（无公开文档链接）