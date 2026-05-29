# Synthesis and DSP Effects

> A variety of realtime synthesizers and DSP source and submix effects.

| 属性 | 值 |
|---|---|
| 中文名 | 音频合成与DSP效果器 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板、样式资源） |
| 模块 | `Synthesis` (Runtime), `SynthesisEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-01-10 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis) | |

## 用途

Synthesis 插件为 Unreal Engine 提供了一套完整的**实时音频合成与 DSP 处理框架**。它解决的核心问题是：在引擎运行时通过程序化方式生成和处理音频信号，而无需依赖预制的音频文件。

具体功能包括：

- **实时音频合成器**：虚拟模拟合成器（EpicSynth1）、波表合成器（MonoWaveTable）、粒子合成器（GranularSynth）和简单音调发生器（ToneGenerator），可在运行时实时生成声音
- **Source Effects（声源效果器）**：应用于单个音频源的效果处理链，包括滤波器、压缩/限制/扩展器、延迟、失真、混响、均衡器、合唱、移相器等
- **Submix Effects（子混音效果器）**：应用于音频子混音总线的效果处理，包括卷积混响、多频段压缩器、立体声延迟等
- **专业级 DSP 算法**：内置 FDN 混响（Flexiverb）、卷积混响、各种滤波器类型（State Variable、Ladder、OnePole）等高质量音频处理算法
- **调制系统**：支持 LFO、包络跟随器、外部音频总线调制等丰富的调制路由能力

## 子模块文档

由于本插件规模较大（101 个源文件），文档分为以下子页面：

- [SynthComponents — 合成器组件](SynthComponents.md) — EpicSynth1、MonoWaveTable、GranularSynth、ToneGenerator、SamplePlayer
- [SourceEffects — 声源效果器](SourceEffects.md) — 滤波器、压缩器、延迟、混响、失真、合唱、移相器等
- [SubmixEffects & Utilities — 子混音效果器与工具](SubmixEffects.md) — 卷积混响、多频段压缩、延迟、Flexiverb，以及 Slate UI 控件

## 使用场景

- **你需要在游戏中实时生成音乐或音效** → 使用 `UModularSynthComponent`（虚拟模拟合成器）或 `UMonoWaveTableSynthComponent`（波表合成器）
- **你需要粒子合成器制作纹理音效** → 使用 `UGranularSynth`（粒子合成器），可对采样进行精细的粒度控制
- **你需要为音频源添加效果处理** → 创建 Source Effect Preset（如 `USourceEffectFilterPreset`、`USourceEffectDynamicsProcessorPreset`）并添加到声源的效果链
- **你需要在子混音总线上应用全局效果** → 使用 Submix Effect（如 `USubmixEffectConvolutionReverbPreset` 卷积混响、`USubmixEffectMultibandCompressorPreset` 多频段压缩）
- **你需要用 MIDI 控制合成器** → 通过 `NoteOn`/`NoteOff` 函数传入 MIDI 音符号和力度，支持复音、滑音（Portamento）和弯音（Pitch Bend）
- **你需要在编辑器中构建自定义合成器 UI** → 使用内置的 `SSynthKnob`（旋钮控件）和 `SSynth2DSlider`（二维滑块控件）

## 模块依赖

从 Build.cs 提取的非标准依赖：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesiaCore` | 音频分析核心模块，卷积混响等效果器依赖 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新 API |
| 2026-03-10 | `22707c32` | [Subsonic] Generator sources can be played/stopped through subsonic actions | Subsonic 系统支持通过动作控制生成器源的播放/停止 |
| 2026-03-09 | `a5cf226b` | Rename FModulationDestination::UpdateModulators to SetModulators | 重命名调制目标 API 方法以提高语义一致性 |

### 维护评价

Synthesis 插件创建于 2017 年 1 月（约 9 年前），属于 UE 的核心音频模块。从近期提交记录看，该插件**仍在活跃维护中**（2026 年仍有功能性更新和 API 迁移），但更新频率不高——最近几次主要是编译警告修复和 API 命名规范化，而非重大功能添加。

该插件已被广泛用于 UE 的音频系统，作为官方提供的默认合成器和效果器方案，整体稳定性较好。由于依赖 `AudioSynesthesiaCore` 模块，在使用前需确认该依赖已启用。

**推荐使用**：对于需要在 UE5 中进行实时音频合成或 DSP 处理的项目，Synthesis 是唯一且成熟的官方方案，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis)
- [SynthComponents 子文档](SynthComponents.md)
- [SourceEffects 子文档](SourceEffects.md)
- [SubmixEffects 子文档](SubmixEffects.md)

---

# SynthComponents — 合成器组件

## 概述

Synthesis 插件提供了五种可直接在蓝图中使用的合成器组件，每种组件代表不同的音频生成方式：

| 组件 | 类名 | 用途 |
|---|---|---|
| 虚拟模拟合成器 | `UModularSynthComponent` | 多声部复音合成器，双振荡器 + 双 LFO + 包络 + 滤波器 + 延迟/合唱效果链 |
| 波表合成器 | `USynthComponentMonoWaveTable` | 单声部波表合成器，通过曲线定义波形形状 |
| 粒子合成器 | `UGranularSynth` | 粒子合成器，将音频采样拆分为微小颗粒进行精细控制 |
| 音调发生器 | `USynthComponentToneGenerator` | 简单的正弦/方波等波形发生器 |
| 采样播放器 | `USynthSamplePlayer` | 基于采样的播放器，支持变速、定位和搓碟模式 |

## UModularSynthComponent

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NoteOn` | 触发音符（MIDI 音符号、力度、可选持续时间） | `UModularSynthComponent` |
| `NoteOff` | 停止音符（支持 bAllNotesOff 全部停止） | `UModularSynthComponent` |
| `SetEnablePolyphony` | 开启/关闭复音模式 | `UModularSynthComponent` |
| `SetOscType` | 设置振荡器类型（Sine/Saw/Triangle/Square/Noise） | `UModularSynthComponent` |
| `SetOscGain` | 设置振荡器增益 | `UModularSynthComponent` |
| `SetOscOctave` | 设置振荡器八度偏移 | `UModularSynthComponent` |
| `SetOscSemitones` | 设置振荡器半音偏移 | `UModularSynthComponent` |
| `SetFilterFrequency` | 设置滤波器截止频率 | `UModularSynthComponent` |
| `SetFilterQ` | 设置滤波器共振（Q 值） | `UModularSynthComponent` |
| `SetFilterType` | 设置滤波器类型（LowPass/HighPass/BandPass/BandStop） | `UModularSynthComponent` |
| `SetLFOFrequency` | 设置 LFO 频率 | `UModularSynthComponent` |
| `SetLFOType` | 设置 LFO 波形类型 | `UModularSynthComponent` |
| `SetPan` | 设置立体声声像 [-1.0, 1.0] | `UModularSynthComponent` |
| `SetSpread` | 设置振荡器立体声扩展 [0.0, 1.0] | `UModularSynthComponent` |
| `SetPitchBend` | 设置弯音 | `UModularSynthComponent` |
| `SetPortamento` | 设置滑音量 [0.0, 1.0] | `UModularSynthComponent` |
| `SetStereoDelayIsEnabled` | 开启/关闭立体声延迟效果 | `UModularSynthComponent` |
| `SetStereoDelayTime` | 设置延迟时间 | `UModularSynthComponent` |
| `SetStereoDelayFeedback` | 设置延迟反馈量 | `UModularSynthComponent` |
| `SetChorusEnabled` | 开启/关闭合唱效果 | `UModularSynthComponent` |
| `SetSynthPreset` | 通过预设结构体一次性设置所有参数 | `UModularSynthComponent` |
| `CreatePatch` | 创建调制路由（LFO/包络到目标参数） | `UModularSynthComponent` |

### 使用示例（蓝图描述）

**基本旋律播放：**
1. 在 Actor 上添加 `ModularSynthComponent` 组件
2. 设置 `VoiceCount` 属性（默认 1，最大 32）
3. 使用 `SetOscType` 将振荡器 1 设为 Saw 波，振荡器 2 设为 Square 波
4. 使用 `SetFilterFrequency` 设置滤波器截止频率为 8000 Hz
5. 使用 `NoteOn(60.0, 100)` 触发 C4 音符，力度 100
6. 使用 `NoteOn(64.0, 80)` 触发 E4 音符（复音模式下会叠加）

**MIDI 控制流：**
1. 通过 MIDI 事件驱动 `NoteOn`/`NoteOff`
2. MIDI CC 消息映射到 `SetFilterFrequency`、`SetPitchBend` 等
3. `SetPortamento(0.5)` 使音符切换时产生平滑滑音

**预设系统：**
1. 创建 `FModularSynthPreset` 结构体（支持数据表行）
2. 填充振荡器、滤波器、包络、延迟、合唱等所有参数
3. 调用 `SetSynthPreset` 一次性应用

## USynthComponentMonoWaveTable

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NoteOn` | 触发音符 | `USynthComponentMonoWaveTable` |
| `NoteOff` | 停止音符 | `USynthComponentMonoWaveTable` |
| `SetFrequency` | 设置频率（Hz） | `USynthComponentMonoWaveTable` |
| `SetFrequencyWithMidiNote` | 通过 MIDI 音符号设置频率 | `USynthComponentMonoWaveTable` |
| `SetWaveTablePosition` | 设置波表位置 [0.0, 1.0] | `USynthComponentMonoWaveTable` |
| `SetPosLfoFrequency` | 设置波表位置 LFO 频率 | `USynthComponentMonoWaveTable` |
| `SetPosLfoDepth` | 设置波表位置 LFO 深度 | `USynthComponentMonoWaveTable` |
| `SetLowPassFilterFrequency` | 设置低通滤波器频率 | `USynthComponentMonoWaveTable` |
| `SetLowPassFilterResonance` | 设置低通滤波器共振 | `USynthComponentMonoWaveTable` |
| `SetAmpEnvelopeAttackTime` | 设置振幅包络起音时间（ms） | `USynthComponentMonoWaveTable` |
| `SetFilterEnvelopeAttackTime` | 设置滤波器包络起音时间 | `USynthComponentMonoWaveTable` |
| `SetPositionEnvelopeAttackTime` | 设置位置包络起音时间 | `USynthComponentMonoWaveTable` |
| `SetCurveValue` | 设置波表曲线关键帧值 | `USynthComponentMonoWaveTable` |
| `SetCurveInterpolationType` | 设置曲线插值类型 | `USynthComponentMonoWaveTable` |
| `RefreshWaveTable` | 刷新指定波表数据 | `USynthComponentMonoWaveTable` |
| `GetKeyFrameValuesForTable` | 获取波表关键帧数据 | `USynthComponentMonoWaveTable` |

## UGranularSynth

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSoundWave` | 设置用于粒子合成的音频源 | `UGranularSynth` |
| `NoteOn` | 开始粒子合成播放 | `UGranularSynth` |
| `NoteOff` | 停止粒子合成播放 | `UGranularSynth` |
| `SetGrainsPerSecond` | 设置每秒粒子数 | `UGranularSynth` |
| `SetGrainProbability` | 设置粒子触发概率 | `UGranularSynth` |
| `SetGrainPitch` | 设置粒子基音高和随机范围 | `UGranularSynth` |
| `SetGrainVolume` | 设置粒子基音量和随机范围 | `UGranularSynth` |
| `SetGrainDuration` | 设置粒子基持续时间和随机范围 | `UGranularSynth` |
| `SetGrainPan` | 设置粒子基声像和随机范围 | `UGranularSynth` |
| `SetGrainEnvelopeType` | 设置粒子包络类型（14 种可选） | `UGranularSynth` |
| `SetPlaybackSpeed` | 设置播放速度 | `UGranularSynth` |
| `SetPlayheadTime` | 设置播放头位置 | `UGranularSynth` |
| `SetScrubMode` | 开启搓碟模式 | `UGranularSynth` |

## C++ 用法

### 头文件引入

```cpp
#include "SynthComponents/EpicSynth1Component.h"
#include "SynthComponents/SynthComponentMonoWaveTable.h"
#include "SynthComponents/SynthComponentGranulator.h"
```

### 基本用法 — ModularSynth

```cpp
// 在 Actor 中创建合成器组件并触发音符
// 参考自 Classes/SynthComponents/EpicSynth1Component.h

UModularSynthComponent* Synth = NewObject<UModularSynthComponent>(MyActor);
Synth->RegisterComponent();

// 设置振荡器类型
Synth->SetOscType(0, ESynth1OscType::Saw);   // 振荡器 1 使用锯齿波
Synth->SetOscType(1, ESynth1OscType::Square); // 振荡器 2 使用方波

// 设置滤波器
Synth->SetFilterFrequency(5000.0f);
Synth->SetFilterQ(2.0f);
Synth->SetFilterType(ESynthFilterType::LowPass);

// 触发音符 (MIDI Note 60 = C4, Velocity 100)
Synth->NoteOn(60.0f, 100);

// 2 秒后停止
Synth->NoteOff(60.0f);
```

### 进阶用法 — 预设与调制

```cpp
// 使用预设结构体和调制系统
// 参考自 Classes/SynthComponents/EpicSynth1Component.h

FModularSynthPreset Preset;
Preset.bEnablePolyphony = true;
Preset.Osc1Type = ESynth1OscType::Saw;
Preset.Osc2Type = ESynth1OscType::Square;
Preset.FilterFrequency = 8000.0f;
Preset.FilterQ = 2.0f;
Preset.FilterAlgorithm = ESynthFilterAlgorithm::Ladder;
Preset.StereoDelayTime = 500.0f;
Preset.StereoDelayFeedback = 0.5f;
Preset.bStereoDelayEnabled = true;
Preset.bChorusEnabled = true;
Preset.ChorusDepth = 0.3f;

// 应用预设
Synth->SetSynthPreset(Preset);

// 创建调制路由：LFO1 调制滤波器频率
TArray<FSynth1PatchCable> PatchCables;
FSynth1PatchCable Cable;
Cable.Destination = ESynth1PatchDestination::FilterFrequency;
Cable.Depth = 0.5f;
PatchCables.Add(Cable);

Synth->CreatePatch(ESynth1PatchSource::LFO1, PatchCables, true);
```

---

# SourceEffects — 声源效果器

## 概述

Source Effects 是应用于**单个音频源**的效果处理单元。每个效果器都有一个对应的 Preset 类（可在编辑器中创建资产）和底层 DSP 实例类。

| 效果器 | Preset 类 | 功能简述 |
|---|---|---|
| 滤波器 | `USourceEffectFilterPreset` | 低通/高通/带通/带阻，支持 AudioBus 调制 |
| 动态处理器 | `USourceEffectDynamicsProcessorPreset` | 压缩/限制/扩展/门限/向上压缩 |
| 延迟 | `USourceEffectSimpleDelayPreset` | 基于距离或固定时间的延迟 |
| 立体声延迟 | `USourceEffectStereoDelayPreset` | 正常/交叉/PingPong 模式立体声延迟 |
| 混响 | `USourceEffectConvolutionReverbPreset` | 基于脉冲响应的卷积混响 |
| 合唱 | `USourceEffectChorusPreset` | 合唱效果，支持调制系统 |
| 移相器 | `USourceEffectPhaserPreset` | 移相器效果，多种 LFO 类型 |
| 均衡器 | `USourceEffectEQPreset` | 多频段参数均衡器 |
| 失真 | `USourceEffectFoldbackDistortionPreset` | 折叠失真效果 |
| 位破碎 | `USourceEffectBitCrusherPreset` | 降低采样率和位深度 |
| 环形调制 | `USourceEffectRingModulationPreset` | 环形调制（多种调制波形） |
| 声像器 | `USourceEffectPannerPreset` | 声像/宽度控制 |
| 中侧扩展 | `USourceEffectMidSideSpreaderPreset` | Mid/Side 声场宽度处理 |
| 包络跟随器 | `USourceEffectEnvelopeFollowerPreset` | 信号包络追踪，支持蓝图回调 |
| 运动滤波器 | `USourceEffectMotionFilterPreset` | 基于声源运动的动态滤波 |

## 核心节点

### SourceEffectFilter

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置滤波器完整参数 | `USourceEffectFilterPreset` |

滤波器支持三种电路实现：`OnePole`、`StateVariable`、`Ladder`，四种类型：`LowPass`、`HighPass`、`BandPass`、`BandStop`。

### SourceEffectDynamicsProcessor

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置动态处理器参数 | `USourceEffectDynamicsProcessorPreset` |

支持五种处理类型：`Compressor`（压缩）、`Limiter`（限制）、`Expander`（扩展）、`Gate`（门限）、`UpwardsCompressor`（向上压缩）。

### SourceEffectChorus

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置基础参数 | `USourceEffectChorusPreset` |
| `SetModulationSettings` | 设置调制参数 | `USourceEffectChorusPreset` |
| `SetDepthModulator` | 设置深度调制源 | `USourceEffectChorusPreset` |
| `SetFrequency` | 设置合唱频率 | `USourceEffectChorusPreset` |

### SourceEffectConvolutionReverb

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置卷积混响参数 | `USourceEffectConvolutionReverbPreset` |
| `SetImpulseResponse` | 设置脉冲响应资产 | `USourceEffectConvolutionReverbPreset` |

### SourceEffectEnvelopeFollower

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置包络跟随器参数 | `USourceEffectEnvelopeFollowerPreset` |
| `RegisterEnvelopeFollowerListener` | 注册包络值监听器 | `USourceEffectEnvelopeFollowerPreset` |

## 使用示例（蓝图描述）

**为声源添加滤波器效果：**
1. 创建 `SourceEffectFilterPreset` 资产
2. 在内容浏览器中配置 Settings（Circuit: StateVariable, Type: LowPass, Cutoff: 2000 Hz, Q: 2.0）
3. 将 Preset 拖入声源的 SourceEffectChain
4. 运行时可通过 `SetSettings` 动态调整参数

**包络跟随器自动 Wah 效果：**
1. 创建 `SourceEffectFilterPreset` 并开启 AudioBusModulation
2. 创建 `SourceEffectEnvelopeFollowerPreset` 资产
3. 创建 `UEnvelopeFollowerListener` 组件监听包络值
4. 通过 AudioBus 将包络值路由到滤波器频率调制

---

# SubmixEffects & Utilities — 子混音效果器与工具

## Submix Effects 概述

Submix Effects 应用于**音频子混音总线**，影响该总线上所有音频的混合信号。

| 效果器 | Preset 类 | 功能简述 |
|---|---|---|
| 卷积混响 | `USubmixEffectConvolutionReverbPreset` | 基于脉冲响应的卷积混响，支持硬件加速 |
| 多频段压缩 | `USubmixEffectMultibandCompressorPreset` | 多频段动态处理，支持外部侧链 |
| 延迟 | `USubmixEffectDelayPreset` | 基础延迟效果 |
| Tap 延迟 | `USubmixEffectTapDelayPreset` | 多 Tap 延迟（支持独立声像控制） |
| 立体声延迟 | `USubmixEffectStereoDelayPreset` | 立体声延迟（正常/交叉/PingPong） |
| 滤波器 | `USubmixEffectFilterPreset` | 子混音滤波器 |
| Flexiverb | `USubmixEffectFlexiverbPreset` | 轻量级 FDN 混响，适合低性能平台 |

## SubmixEffectMultibandCompressor

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置多频段压缩器参数 | `USubmixEffectMultibandCompressorPreset` |
| `SetAudioBus` | 设置外部侧链 AudioBus | `USubmixEffectMultibandCompressorPreset` |
| `SetExternalSubmix` | 设置外部侧链 Submix | `USubmixEffectMultibandCompressorPreset` |
| `ResetKey` | 重置侧链输入 | `USubmixEffectMultibandCompressorPreset` |

支持五种动态处理器类型、三种峰值检测模式和三种通道链接模式。每个频段有独立的阈值、比率、起音/释放时间设置。

## SubmixEffectConvolutionReverb

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置卷积混响参数 | `USubmixEffectConvolutionReverbPreset` |
| `SetImpulseResponse` | 设置脉冲响应资产 | `USubmixEffectConvolutionReverbPreset` |

卷积混响的核心数据资产是 `UAudioImpulseResponse`，它存储了从音频文件导入的脉冲响应采样数据。支持真立体声（TrueStereo）模式以实现通道串扰。

`FConvolutionReverb` 内部管线：输入音频 → 解交织 → 输入格式转换 → 卷积算法 → 输出格式转换 → 交织 → 输出音频。

## SubmixEffectTapDelay

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSettings` | 设置 Tap 延迟参数 | `USubmixEffectTapDelayPreset` |
| `AddTap` | 动态添加 Tap | `USubmixEffectTapDelayPreset` |
| `RemoveTap` | 移除 Tap | `USubmixEffectTapDelayPreset` |
| `SetTap` | 修改指定 Tap 参数 | `USubmixEffectTapDelayPreset` |
| `GetTap` | 获取 Tap 参数 | `USubmixEffectTapDelayPreset` |
| `GetTapIds` | 获取所有 Tap ID | `USubmixEffectTapDelayPreset` |

每个 Tap 支持三种模式：`SendToChannel`（直接发送到指定通道）、`Panning`（基于角度声像）、`Disabled`（禁用并淡出）。

## Slate UI 控件

Synthesis 插件还提供了两个自定义 Slate 控件和对应的 UMG Widget，用于构建合成器编辑器 UI：

### SSynthKnob / USynthKnob

自定义旋钮控件，支持：
- 可配置鼠标速度和微调速度
- 参数名称和单位的工具提示显示
- 键盘/手柄焦点控制
- 参数范围映射

### SSynth2DSlider / USynth2DSlider

自定义二维滑块控件，同时输出 X/Y 两个轴的值 [0.0, 1.0]，适合用于：
- 合成器的 XY 参数映射
- 频率/共振的二维控制

## Flexiverb 混响

`FFlexiverb` 是一个计算开销极低的 FDN 混响算法，专为低性能平台设计。使用 Householder 矩阵作为散射矩阵，在有限的乘法运算下最大化回声密度。

| 设置 | 范围 | 说明 |
|---|---|---|
| Complexity | 2-6 | 复杂度（越大回声密度越高，但内存和 CPU 开销也越大） |
| DecayTime | 0.4-5.0 秒 | 衰减到 -60 dB 的时间 |
| PreDelay | 0-30 ms | 初始反射延迟 |
| RoomDampening | 60-12000 Hz | 房间阻尼频率 |

## C++ 用法 — Submix Effects

### 头文件引入

```cpp
#include "SubmixEffects/SubmixEffectConvolutionReverb.h"
#include "SubmixEffects/SubmixEffectMultibandCompressor.h"
#include "EffectConvolutionReverb.h"
```

### 基本用法 — 卷积混响

```cpp
// 创建并配置卷积混响
// 参考自 Classes/SubmixEffects/SubmixEffectConvolutionReverb.h

USubmixEffectConvolutionReverbPreset* ReverbPreset = NewObject<USubmixEffectConvolutionReverbPreset>();

FSubmixEffectConvolutionReverbSettings Settings;
Settings.WetVolumeDb = -6.0f;
Settings.DryVolumeDb = 0.0f;
Settings.bBypass = false;
Settings.bMixInputChannelFormatToImpulseResponseFormat = true;
Settings.bMixReverbOutputToOutputChannelFormat = true;

ReverbPreset->SetSettings(Settings);

// 设置脉冲响应
ReverbPreset->SetImpulseResponse(MyImpulseResponseAsset);
```

### 进阶用法 — Flexiverb 低开销混响

```cpp
// 直接使用 FFlexiverb 进行单声道混响处理
// 参考自 Public/Flexiverb.h

Audio::FFlexiverb Flexiverb;
Flexiverb.Init(48000);

Audio::FFlexiverbSettings Settings;
Settings.Complexity = 4;
Settings.DecayTime = 6.0f;
Settings.PreDelay = 6.0f;
Settings.RoomDampening = 220.0f;
Flexiverb.SetSettings(Settings);

// 在音频回调中逐帧处理
float InputBuffer[2];
float OutputBuffer[2];
Flexiverb.ProcessAudioFrame(InputBuffer, 2, OutputBuffer, 2);
```

### 进阶用法 — 卷积混响底层 API

```cpp
// 使用 FConvolutionReverb 进行自定义卷积处理
// 参考自 Public/ConvolutionReverb.h

Audio::FConvolutionReverbInitData InitData;
InitData.InputAudioFormat = ...;
InitData.OutputAudioFormat = ...;
InitData.Samples = ImpulseResponseSamples;
InitData.ImpulseSampleRate = 48000.0f;
InitData.TargetSampleRate = 48000.0f;
InitData.NormalizationVolume = 1.0f;

auto Reverb = Audio::FConvolutionReverb::CreateConvolutionReverb(InitData);

// 处理音频块
Audio::FAlignedFloatBuffer OutputAudio;
Reverb->ProcessAudio(NumInputChannels, InputAudio, NumOutputChannels, OutputAudio);
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频资产创建菜单 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的格式化 API |
| 2026-03-10 | `22707c32` | [Subsonic] Generator sources can be played/stopped through subsonic actions | Subsonic 系统支持通过动作控制合成器源的播放/停止 |
| 2026-03-09 | `a5cf226b` | Rename FModulationDestination::UpdateModulators to SetModulators | 调制目标 API 重命名以提高语义一致性 |

### 维护评价

**活跃维护中。** 尽管创建于 2017 年（约 9 年前），该插件仍在 2026 年持续获得更新，包括 API 迁移、编译警告修复和新功能集成（Subsonic 系统）。最近的更新主要是维护性改动而非重大功能添加，说明该插件已经非常成熟和稳定。

作为 UE 官方音频系统的核心组件，Synthesis 插件提供了市面上最全面的实时合成与 DSP 效果器集合，推荐所有需要程序化音频生成或处理的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis)
- [SynthComponents 合成器组件](SynthComponents.md)
- [SourceEffects 声源效果器](SourceEffects.md)
- [SubmixEffects 子混音效果器](SubmixEffects.md)