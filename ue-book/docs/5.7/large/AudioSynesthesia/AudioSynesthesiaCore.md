# AudioSynesthesiaCore 模块

> 底层 DSP 分析引擎，提供所有音频分析算法的核心实现和工厂类。

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| 加载阶段 | PreDefault |
| 头文件 | 25 个 (.h) |
| 源文件 | 21 个 (.cpp) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `SignalProcessing` | DSP 工具（FFT、窗口函数等） |
| `AudioMixerCore` | 音频混音器核心（私有依赖） |
| `AudioAnalyzer` | 分析器接口和基类（仅头文件引用） |

## 架构概述

AudioSynesthesiaCore 采用 **工厂模式** 组织分析器。每个分析算法由三个类组成：

```
FXXXFactory (IAnalyzerFactory)
  ├── FXXXWorker (IAnalyzerWorker)    ← 执行实际 DSP 计算
  └── FXXXResult (IAnalyzerResult)    ← 存储分析结果
```

设置通过 `FXXXSettings` 结构体传入，所有类均位于 `Audio` 命名空间。

## 实时分析器（Real-Time Analyzers）

### LoudnessAnalyzer — 响度分析器

**头文件**: `Public/LoudnessAnalyzer.h`

基于 FFT 的感知响度分析。将音频分解为频段，应用等响度曲线（A/B/C/D/K），计算加权能量。

- `FLoudnessFactory` — 工厂类
- `FLoudnessWorker` — 分析工作线程
- `FLoudnessAnalyzerResult` — 结果存储（按通道 + 整体）
- `FLoudnessAnalyzerSettings` — 设置（FFT 大小、窗口类型、响度曲线、频率范围、缩放方式）

**响度曲线类型** (`ELoudnessCurveType`): A, B, C, D, K, None

### ConstantQAnalyzer — 常数 Q 变换分析器

**头文件**: `Public/ConstantQAnalyzer.h`

计算 CQT（Constant-Q Transform），按对数频率间隔排列频段，适合音乐信号分析。

- `FConstantQFactory` / `FConstantQWorker` / `FConstantQAnalyzerResult`
- `FConstantQAnalyzerSettings` — 起始频率、频段数、每八度频段数、FFT 大小、窗口类型、频谱类型、带宽拉伸、归一化方式、噪声底限

**归一化方式** (`EConstantQNormalizationEnum`): EqualEuclideanNorm, EqualEnergy, EqualAmplitude

**FFT 大小** (`EConstantQFFTSizeEnum`): 64 ~ 16384

### MeterAnalyzer — 电平表分析器

**头文件**: `Public/MeterAnalyzer.h`

实时测量音频幅度，支持 RMS、峰值、削波检测。

- `FMeterFactory` / `FMeterWorker` / `FMeterAnalyzerResult`
- `FMeterAnalyzerSettings` — 分析周期、峰值模式（MeanSquared/RootMeanSquared/Peak）、Attack/Release 时间、峰值保持时间、削波阈值

### LKFSAnalyzer — LKFS 响度分析器（新增 2025）

**头文件**: `Public/LKFSFactory.h`

符合 ITU-R BS.1770 标准的 LKFS/LUFS 响度测量。提供瞬时响度、短期响度、积分响度和门控响度。

- `FLKFSFactory` / `FLKFSWorker` / `FLKFSAnalyzerResult`
- `FLKFSSettings` — 分析周期（默认 0.1s）、分析窗口时长（默认 0.4s）、短期响度时长（标准 3s）、积分响度时长（默认 60s）

**结果结构 `FLKFSResults`**:

| 字段 | 说明 |
|---|---|
| `Channel` | 通道索引，-1 表示整体 |
| `Timestamp` | 时间戳（秒） |
| `Energy` | 感知加权能量（相对满刻度） |
| `Loudness` | 瞬时响度 (dB) |
| `ShortTermLoudness` | 短期平均响度 (dB) |
| `IntegratedLoudness` | 积分平均响度 (dB) |
| `GatedLoudness` | 门控平均响度 (dB) |

### SynesthesiaSpectrumAnalyzer — 频谱分析器

**头文件**: `Public/SynesthesiaSpectrumAnalyzer.h`

标准 FFT 频谱分析，输出频段能量数组。

- `FSynesthesiaSpectrumAnalysisFactory` / `FSynesthesiaSpectrumWorker` / `FSynesthesiaSpectrumAnalyzerResult`
- `FSynesthesiaSpectrumAnalysisSettings` — 分析周期、FFT 大小、频谱类型、窗口类型、是否下混为单声道

### OnsetAnalyzer — 起音检测器

**头文件**: `Public/OnsetAnalyzer.h`

检测音频中的起音点（onset），使用频谱通量和峰值拾取算法。

- `FOnsetNRTFactory` / `FOnsetWorker` / `FOnsetAnalyzerResult`
- 依赖 `PeakPicker` 工具类

### PitchTracker — 音高追踪器

**头文件**: `Public/PitchTracker.h`, `Public/MaxStrengthPitchTracker.h`, `Public/FFTPeakPitchDetector.h`, `Public/AutoCorrelationPitchDetector.h`

多种音高检测算法实现：
- `FFTPeakPitchDetector` — 基于 FFT 峰值的音高检测
- `AutoCorrelationPitchDetector` — 基于自相关的音高检测
- `MaxStrengthPitchTracker` — 选择最强信号的音高追踪器

## NRT 分析器工厂（Non-Real-Time）

用于离线分析 SoundWave 并将结果保存为资产。

| 工厂类 | 头文件 | 说明 |
|---|---|---|
| `FLoudnessNRTFactory` | `Public/LoudnessNRTFactory.h` | 离线响度分析 |
| `FConstantQNRTFactory` | `Public/ConstantQNRTFactory.h` | 离线 CQT 分析 |
| `FOnsetNRTFactory` | `Public/OnsetNRTFactory.h` | 离线起音检测 |
| `FLKFSNRTFactory` | `Public/LKFSNRTFactory.h` | 离线 LKFS 响度分析 |
| `FSynesthesiaSpectrumAnalysisNRTFactory` | `Public/SynesthesiaSpectrumAnalysisFactory.h` | 离线频谱分析 |

## 工具类

| 类 | 头文件 | 说明 |
|---|---|---|
| `PeakPicker` | `Public/PeakPicker.h` | 峰值拾取算法，用于起音检测 |
| `FindNearestByTimestamp` | `Public/FindNearestByTimestamp.h` | 按时间戳查找最近结果 |
| `InterpolateSorted` | `Public/InterpolateSorted.h` | 排序数据的插值工具 |

## 自定义版本管理

`AudioSynesthesiaCustomVersion` 用于资产序列化版本控制，确保向后兼容。

## 源码链接

- [AudioSynesthesiaCore 模块目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia/Source/AudioSynesthesiaCore)
