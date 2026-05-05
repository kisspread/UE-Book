# AudioSynesthesia 模块

> 蓝图友好的运行时分析器封装层，将底层 DSP 算法暴露为 Blueprint 可用的 UAudioAnalyzer 和 UAudioAnalyzerNRT 子类。

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| 加载阶段 | PreDefault |
| 头文件 | 13 个 (.h) |
| 源文件 | 12 个 (.cpp) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `SignalProcessing` | DSP 工具 |
| `AudioMixerCore` | 音频混音器核心 |
| `AudioMixer` | 音频混音器 |
| `AudioAnalyzer` | 分析器基类（UAudioAnalyzer、UAudioAnalyzerNRT） |
| `AudioSynesthesiaCore` | 底层 DSP 分析引擎 |

## 架构概述

本模块是 AudioSynesthesiaCore 与蓝图之间的桥梁。每个分析器由一对 Settings + Analyzer 类组成：

```
UXXXSettings (UAudioSynesthesiaSettings)  ← 可创建为资产
  └── UXXXAnalyzer (UAudioAnalyzer)        ← 运行时分析，通过 Delegate 广播结果
```

NRT 分析器类似：

```
UXXXNRTSettings (UAudioSynesthesiaNRTSettings)  ← 配置
  └── UXXXNRT (UAudioSynesthesiaNRT)              ← 离线分析资产，通过函数查询结果
```

## 基类

### UAudioSynesthesiaSettings

**头文件**: `Classes/AudioSynesthesia.h`

所有实时分析器设置的基类，继承自 `UAudioAnalyzerSettings`。支持蓝图创建为资产。

### UAudioSynesthesiaNRTSettings / UAudioSynesthesiaNRT

**头文件**: `Classes/AudioSynesthesiaNRT.h`

所有离线分析器设置和结果资产的基类，分别继承自 `UAudioAnalyzerNRTSettings` 和 `UAudioAnalyzerNRT`。

## 实时分析器（Real-Time）

### ULoudnessAnalyzer — 响度分析器

**头文件**: `Classes/Loudness.h`

实时计算感知响度。支持 A/B/C/D/K 等响度曲线加权。

**设置 (`ULoudnessSettings`)**:

| 属性 | 默认值 | 说明 |
|---|---|---|
| `AnalysisPeriod` | 0.01s | 测量间隔 (0.01~0.25) |
| `MinimumFrequency` | 20 Hz | 最低分析频率 |
| `MaximumFrequency` | 20000 Hz | 最高分析频率 |
| `CurveType` | D | 等响度曲线类型 |
| `NoiseFloorDb` | -60 dB | 噪声底限 |
| `ExpectedMaxLoudness` | 0 dB | 预期最大响度 |

**结果 (`FLoudnessResults`)**:

| 字段 | 说明 |
|---|---|
| `Loudness` | 原始响度 (dB) |
| `NormalizedLoudness` | 归一化响度 (0.0~1.0) |
| `PerceptualEnergy` | 感知能量 |
| `TimeSeconds` | 时间戳 |

**Delegate**:

| 委托 | 说明 |
|---|---|
| `OnOverallLoudnessResults` | 整体响度结果数组 |
| `OnLatestOverallLoudnessResults` | 最新整体响度 |
| `OnPerChannelLoudnessResults` | 每通道响度结果数组 |
| `OnLatestPerChannelLoudnessResults` | 每通道最新响度 |

### UConstantQAnalyzer — 常数 Q 变换分析器

**头文件**: `Classes/ConstantQ.h`

实时计算 CQT 频谱，适合音乐信号的对数频率分析。

**设置 (`UConstantQSettings`)**:

| 属性 | 默认值 | 说明 |
|---|---|---|
| `StartingFrequencyHz` | 40 Hz | 起始频率 |
| `NumBands` | 48 | 频段总数 |
| `NumBandsPerOctave` | 12 | 每八度频段数 |
| `AnalysisPeriodInSeconds` | 0.01s | 分析周期 |
| `bDownmixToMono` | false | 是否下混为单声道 |
| `FFTSize` | XLarge (4096) | FFT 大小 |
| `WindowType` | Blackman | 窗口类型 |
| `SpectrumType` | PowerSpectrum | 频谱类型 |
| `BandWidthStretch` | 1.0 | 带宽拉伸因子 |
| `CQTNormalization` | EqualEnergy | 归一化方式 |
| `NoiseFloorDb` | -60 dB | 噪声底限 |

**结果 (`FConstantQResults`)**:

| 字段 | 说明 |
|---|---|
| `TimeSeconds` | 时间戳 |
| `SpectrumValues` | 频谱值数组 |

**蓝图函数**:

| 函数 | 说明 |
|---|---|
| `GetCenterFrequencies` | 获取中心频率数组 |
| `GetNumCenterFrequencies` | 获取中心频率数量 |

**Delegate**: `OnConstantQResults`, `OnLatestConstantQResults`（均按通道）

### UMeterAnalyzer — 电平表分析器

**头文件**: `Classes/Meter.h`

实时测量音频电平，支持多种峰值模式和削波检测。

**设置 (`UMeterSettings`)**:

| 属性 | 默认值 | 说明 |
|---|---|---|
| `AnalysisPeriod` | 0.01s | 测量间隔 |
| `PeakMode` | RootMeanSquared | 峰值模式 |
| `MeterAttackTime` | 300 ms | 起音时间 |
| `MeterReleaseTime` | 300 ms | 释放时间 |
| `PeakHoldTime` | 100 ms | 峰值保持时间 |
| `ClippingThreshold` | 1.0 | 削波阈值 |

**峰值模式** (`EMeterPeakType`): MeanSquared, RootMeanSquared, Peak

**结果 (`FMeterResults`)**:

| 字段 | 说明 |
|---|---|
| `TimeSeconds` | 时间戳 |
| `MeterValue` | 电平值 |
| `PeakValue` | 峰值 |
| `NumSamplesClipping` | 削波采样数 |
| `ClippingValue` | 削波值 |

**Delegate**: 整体/每通道 × 全部/最新，共 4 个动态委托 + 4 个原生委托

### ULKFSAnalyzer — LKFS 响度分析器

**头文件**: `Classes/LKFS.h`

符合 ITU-R BS.1770 标准的实时 LKFS/LUFS 响度测量。

**设置 (`ULKFSSettings`)**:

| 属性 | 默认值 | 说明 |
|---|---|---|
| `AnalysisPeriod` | 0.1s | 测量间隔 |
| `AnalysisWindowDuration` | 0.4s | 单次分析窗口时长 |
| `ShortTermLoudnessDuration` | 3.0s | 短期响度时长 |
| `IntegratedLoudnessAnalysisPeriod` | 1.0s | 积分响度更新间隔 |
| `IntegratedLoudnessDuration` | 60.0s | 积分响度分析时长 |

**Delegate**: 整体/每通道 × 全部/最新，共 4 个动态委托 + 4 个原生委托

### USynesthesiaSpectrumAnalyzer — 频谱分析器

**头文件**: `Classes/SynesthesiaSpectrumAnalysis.h`

标准 FFT 频谱分析。

**设置 (`USynesthesiaSpectrumAnalysisSettings`)**:

| 属性 | 默认值 | 说明 |
|---|---|---|
| `AnalysisPeriod` | 0.01s | 分析周期 |
| `FFTSize` | DefaultSize | FFT 大小 |
| `SpectrumType` | PowerSpectrum | 频谱类型 |
| `WindowType` | Hann | 窗口类型 |
| `bDownmixToMono` | true | 是否下混为单声道 |

**结果 (`FSynesthesiaSpectrumResults`)**: TimeSeconds + SpectrumValues 数组

**蓝图函数**: `GetCenterFrequencies(InSampleRate, OutCenterFrequencies)`, `GetNumCenterFrequencies()`

## 离线分析器（NRT）

### ULoudnessNRT — 离线响度分析

**头文件**: `Classes/LoudnessNRT.h`

对 SoundWave 进行离线响度分析，结果保存为资产。

**设置 (`ULoudnessNRTSettings`)**: AnalysisPeriod, MinimumFrequency, MaximumFrequency, CurveType, NoiseFloorDb

**蓝图函数**:

| 函数 | 说明 |
|---|---|
| `GetLoudnessAtTime(Seconds, OutLoudness)` | 获取指定时间的整体响度 |
| `GetChannelLoudnessAtTime(Seconds, Channel, OutLoudness)` | 获取指定时间指定通道的响度 |
| `GetNormalizedLoudnessAtTime(Seconds, OutLoudness)` | 获取归一化响度 |
| `GetNormalizedChannelLoudnessAtTime(Seconds, Channel, OutLoudness)` | 获取指定通道归一化响度 |

### UConstantQNRT — 离线 CQT 分析

**头文件**: `Classes/ConstantQNRT.h`

**设置 (`UConstantQNRTSettings`)**: 与实时版本类似的 CQT 参数。

**蓝图函数**:

| 函数 | 说明 |
|---|---|
| `GetChannelConstantQAtTime(Seconds, Channel, OutCQT)` | 获取指定时间指定通道的 CQT |
| `GetNormalizedChannelConstantQAtTime(Seconds, Channel, OutCQT)` | 获取归一化 CQT |

### ULKFSNRT — 离线 LKFS 分析

**头文件**: `Classes/LKFSNRT.h`

**设置 (`ULKFSNRTSettings`)**: AnalysisPeriod, AnalysisWindowDuration, ShortTermLoudnessDuration

**蓝图函数**:

| 函数 | 说明 |
|---|---|
| `GetLoudnessAtTime(Seconds, OutLoudness)` | 整体响度 |
| `GetChannelLoudnessAtTime(Seconds, Channel, OutLoudness)` | 通道响度 |
| `GetLoudnessData()` | 完整整体响度数据 |
| `GetLoudnessDataForChannel(Channel)` | 完整通道响度数据 |
| `GetLoudnessDataAtTime(Seconds)` | 指定时间整体数据 |
| `GetLoudnessDataForChannelAtTime(Seconds, Channel)` | 指定时间通道数据 |
| `GetIntegratedLoudness()` | 积分响度 |
| `GetIntegratedLoudnessForChannel(Channel)` | 通道积分响度 |
| `GetGatedLoudness()` | 门控响度 |
| `GetGatedLoudnessForChannel(Channel)` | 通道门控响度 |

### UOnsetNRT — 离线起音检测

**头文件**: `Classes/OnsetNRT.h`

**设置 (`UOnsetNRTSettings`)**: bDownmixToMono, GranularityInSeconds, Sensitivity, MinimumFrequency, MaximumFrequency

**蓝图函数**:

| 函数 | 说明 |
|---|---|
| `GetChannelOnsetsBetweenTimes(Start, End, Channel, OutTimestamps, OutStrengths)` | 获取时间范围内的起音点 |
| `GetNormalizedChannelOnsetsBetweenTimes(Start, End, Channel, OutTimestamps, OutStrengths)` | 获取归一化起音强度 |

## 源码链接

- [AudioSynesthesia 模块目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia/Source/AudioSynesthesia)
