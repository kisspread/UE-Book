# WaveformTransformations 模块

> 音频变换算法模块，实现 Trim/Fade、Normalize、Markers、EffectChain 等波形变换操作。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| LoadingPhase | PreDefault |

## 概述

`WaveformTransformations` 提供了所有波形变换的 UObject 和对应的 `Audio::IWaveTransformation` 实现。这些变换附加在 USoundWave 上，在音频播放和编辑时应用。

每个变换由两部分组成：
1. **UObject 子类** (`UWaveformTransformationBase`) — 序列化配置参数，在编辑器属性面板中编辑
2. **IWaveTransformation 实现** (`Audio::IWaveTransformation`) — 实际的音频处理逻辑，通过 `CreateTransformation()` 创建

## 变换类详解

### UWaveformTransformationTrimFade / FWaveTransformationTrimFade

**功能：** 裁剪音频的起止时间，并在裁剪边界处应用淡入/淡出效果。

**UObject 属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `StartTime` | double | 裁剪起始时间（秒），ClampMin=0 |
| `EndTime` | double | 裁剪结束时间（秒），-1 表示不裁剪结尾 |
| `FadeFunctions` | FFadeFunctionData | 淡入/淡出函数配置 |

**淡入/淡出函数体系：**

`UFadeFunction` (Abstract) → 淡入/淡出曲线的基类，包含 `Duration` 属性

| 淡出类型 | 类 | 曲线参数 | 说明 |
|---|---|---|---|
| Linear | `UFadeFunctionLinear` | 无 | 线性淡入淡出 |
| Exponential | `UFadeCurveFunctionExponential` | FadeCurve [1, 10] | 指数曲线，默认 3 |
| Logarithmic | `UFadeCurveFunctionLogarithmic` | FadeCurve [0, 1] | 对数曲线，默认 0.25 |
| Sigmoid | `UFadeCurveFunctionSigmoid` | SFadeCurve [0, 1] | S 型曲线，默认 0.6 |

`FFadeFunctionData` 结构体分别持有 FadeIn 和 FadeOut 的函数实例。

**变换优先级：** High（文件长度可变）

### UWaveformTransformationNormalize / FWaveTransformationNormalize

**功能：** 将音频归一化到目标响度。

**UObject 属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `Target` | float | 目标最大音量 (dB)，ClampMax=0 |
| `MaxGain` | float | 最大增益限制 (dB)，ClampMin=0 |
| `Mode` | ENormalizationMode | 分析模式 |

**归一化模式 (ENormalizationMode)：**

| 模式 | 说明 |
|---|---|
| Peak | 峰值归一化 |
| RMS | 均方根归一化 |
| DWeightedLoudness | D 加权响度归一化 |

**变换优先级：** Low（文件长度不变）

### UWaveformTransformationMarkers / FWaveTransformationMarkers

**功能：** 管理波形标记（Cue Points）和循环区域（Loop Regions）。

**UObject 属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `Markers` | UWaveCueArray* | 标记数组容器 |
| `StartLoopTime` | double | 循环区域起始时间 |
| `EndLoopTime` | double | 循环区域结束时间（<0 表示不激活） |
| `bIsPreviewingLoopRegion` | bool | 是否正在预览循环区域 |

**UWaveCueArray：**
- `CuesAndLoops` — `TArray<FSoundWaveCuePoint>` 标记和循环点数组
- `SelectedCue` — 当前选中的标记索引
- `MinLoopSize = 10` — 循环区域最小帧数

**关键方法：**

| 方法 | 说明 |
|---|---|
| `ModifyMarkerLoopRegion()` | 通过键盘快捷键调整标记/循环边界 |
| `CycleMarkerLoopRegion()` | 在标记和循环之间循环选择 |
| `GetFramesToNextZeroCrossing()` | 查找下一个零交叉点 |
| `IsLoopRegionActive()` | 循环区域是否激活 |
| `SetLoopPreviewing()` / `ResetLoopPreviewing()` | 控制循环预览 |

**变换优先级：** Low

### UWaveformTransformationEffectChain / FWaveTransformationEffectChain

**功能：** 将音源效果链（Source Effect Chain）应用到波形上。

**UObject 属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `EffectChain` | USoundEffectSourcePresetChain* | 效果链资产 |
| `InlineEffects` | TArray<USoundEffectSourcePreset*> | 内联效果实例 |

**变换优先级：** High（文件长度可变）
**特殊能力：** `SupportsRealtimePreview() = true`

## 音频分析函数

`WaveformAudioAnalysis` 命名空间提供静态分析工具：

| 函数 | 说明 |
|---|---|
| `GetRMSPeak()` | 获取 RMS 峰值 |
| `GetLoudnessPeak()` | 获取响度峰值 |
| `GetPeakSampleValue()` | 获取最大采样值 |
| `GetLUFS()` | 获取 LUFS 响度（K 加权，非实时） |

## 日志类别

`LogWaveformTransformation` — 变换模块的日志分类。

## 依赖模块

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | IWaveTransformation 接口 |
| `AudioSynesthesiaCore` | 音频分析 |
| `SignalProcessing` | 信号处理算法 |
| `PropertyEditor` | 属性编辑器 |
| `UnrealEd` | 编辑器功能 |
| `Engine` | USoundWave 等引擎类型 |
