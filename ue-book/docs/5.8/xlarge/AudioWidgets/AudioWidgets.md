# Audio Widgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 中文名 | 音频控件集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UMG 控件、材质模板、样式资产） |
| 模块 | `AudioWidgetsCore` (RuntimeAndProgram), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 是一套专业的音频 UI 控件库，用于构建游戏内音频混音器、音频分析面板等需要与音频系统交互的界面。它不是简单的音频播放器，而是**音频控制与可视化**的基础设施。

核心解决的问题：
- 游戏中需要自定义音频混音界面（如音乐游戏、DJ 模拟器、音频编辑器）
- 需要实时可视化音频信号（频谱、波形、响度、矢量示波器）
- 需要专业级的音频参数控制控件（带 dB/频率映射的滑块、旋钮）
- 需要通过材质渲染的高性能音频控件（AudioMaterial 系列）

插件内部使用 AudioSynesthesia 进行频谱分析，通过 AudioBus 获取实时音频数据，并提供了完整的 Analyzer Rack 框架用于组合多个分析器。

## 使用场景

- 你在做一个游戏内音频混音器 → 用 `UAudioVolumeSlider` / `UAudioVolumeRadialSlider`
- 你需要实时频谱显示（类似 DAW 中的频谱仪）→ 用 `FAudioSpectrumAnalyzer` + `SAudioSpectrumPlot`
- 你需要波形显示和触发检测（示波器）→ 用 `UAudioOscilloscope`
- 你需要矢量示波器（Lissajous 图形）→ 用 `UAudioVectorscope`
- 你需要响度监测（LUFS/真峰值）→ 用 `FAudioLoudnessMeter`
- 你需要基于材质自定义外观的控件（高颜值）→ 用 `UAudioMaterialKnob` / `UAudioMaterialSlider` / `UAudioMaterialButton`
- 你需要频谱图（Spectrogram，时频图）→ 用 `SAudioSpectrogram`
- 你需要构建带多个分析器的音频仪表盘 → 用 `FAudioAnalyzerRack`

## 蓝图用法

### 核心控件节点

#### 音频滑块（Audio Slider）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOutputValue` | 从滑块归一化值(0-1)获取输出值（如 dB 或 Hz） | `UAudioSliderBase` |
| `GetSliderValue` | 从输出值获取滑块归一化值 | `UAudioSliderBase` |
| `SetSliderBackgroundColor` | 设置滑块背景颜色 | `UAudioSliderBase` |
| `SetSliderBarColor` | 设置滑块条颜色 | `UAudioSliderBase` |
| `SetSliderThumbColor` | 设置滑块把手颜色 | `UAudioSliderBase` |
| `SetUnitsText` | 设置单位文本 | `UAudioSliderBase` |
| `SetShowUnitsText` | 是否显示单位文本 | `UAudioSliderBase` |

#### 径向滑块（Audio Radial Slider）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOutputValue` | 从旋钮归一化值获取输出值 | `UAudioRadialSlider` |
| `GetSliderValue` | 从输出值获取旋钮归一化值 | `UAudioRadialSlider` |
| `SetSliderThickness` | 设置滑块厚度 | `UAudioRadialSlider` |
| `SetOutputRange` | 设置输出值范围 | `UAudioRadialSlider` |
| `SetHandStartEndRatio` | 设置指针起止比率 | `UAudioRadialSlider` |

#### 音频电平表（Audio Meter）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMeterChannelInfo` | 获取各通道的电平信息 | `UAudioMeter` |
| `SetMeterChannelInfo` | 设置各通道的电平信息 | `UAudioMeter` |
| `SetBackgroundColor` | 设置背景颜色 | `UAudioMeter` |
| `SetMeterValueColor` | 设置电平值颜色 | `UAudioMeter` |
| `SetMeterPeakColor` | 设置峰值颜色 | `UAudioMeter` |
| `SetMeterClippingColor` | 设置削波颜色 | `UAudioMeter` |

#### 材质控件（Audio Material Widgets）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValue` / `SetValue` | 获取/设置旋钮或滑块的值(0-1) | `UAudioMaterialKnob` / `UAudioMaterialSlider` |
| `SetTuneSpeed` | 设置鼠标调节速度 | `UAudioMaterialKnob` / `UAudioMaterialSlider` |
| `SetLocked` | 设置控件是否锁定（不可交互） | `UAudioMaterialKnob` / `UAudioMaterialSlider` |
| `SetStepSize` | 设置步进大小 | `UAudioMaterialKnob` / `UAudioMaterialSlider` |
| `GetIsPressed` / `SetIsPressed` | 获取/设置按钮按下状态 | `UAudioMaterialButton` |

#### 示波器 / 矢量示波器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartProcessing` | 开始处理音频数据 | `UAudioOscilloscope` / `UAudioVectorscope` |
| `StopProcessing` | 停止处理音频数据 | `UAudioOscilloscope` / `UAudioVectorscope` |

### 使用示例（蓝图描述）

**创建一个音量滑块**：
1. 在 UMG 蓝图中放置 `UAudioVolumeSlider` 控件
2. 设置 `Orientation` 为 `Vertical`
3. 连接 `OnValueChanged` 事件，调用 `GetOutputValue` 获取 dB 值
4. 使用返回的 dB 值设置音源音量

**创建一个频谱分析面板**：
1. 在 UMG 蓝图中放置 `UAudioOscilloscope` 控件
2. 设置 `AudioBus` 属性引用一个 AudioBus 资产
3. 设置 `TimeWindowMs`（时间窗口）和 `AnalysisPeriodMs`（分析周期）
4. 在 `BeginPlay` 或适当事件中调用 `StartProcessing()`
5. 波形将自动在控件中显示

## C++ 用法

### 头文件引入

```cpp
#include "AudioMeter.h"
#include "AudioSlider.h"
#include "AudioRadialSlider.h"
#include "AudioSpectrumAnalyzer.h"
#include "AudioAnalyzerRack.h"
```

### 基本用法 — 创建音频电平表

```cpp
// 来源: Public/AudioMeter.h 中 AudioWidgets::FAudioMeter 的构造方式

// 创建一个 2 通道的音频电平表
TSharedRef<AudioWidgets::FAudioMeter> Meter = MakeShared<AudioWidgets::FAudioMeter>(
    2,                          // 通道数
    AudioDeviceId,              // 音频设备 ID
    ExternalAudioBus            // 可选：外部 AudioBus
);

// 获取 Slate Widget 用于嵌入 UI
TSharedRef<SAudioMeter> MeterWidget = Meter->GetWidget();

// 或使用材质电平表样式
TSharedRef<AudioWidgets::FAudioMeter> MaterialMeter = MakeShared<AudioWidgets::FAudioMeter>(
    2,
    AudioDeviceId,
    AudioMaterialMeterStyle,    // FAudioMaterialMeterStyle
    ExternalAudioBus
);
```

### 基本用法 — 创建音频频谱分析器

```cpp
// 来源: Public/AudioSpectrumAnalyzer.h

// 使用参数结构体创建
AudioWidgets::FAudioSpectrumAnalyzerParams Params;
Params.NumChannels = 1;
Params.AudioDeviceId = AudioDeviceId;
Params.AnalyzerType = EAudioSpectrumAnalyzerType::CQT;
Params.Ballistics = EAudioSpectrumAnalyzerBallistics::Digital;
Params.FrequencyAxisScale = EAudioSpectrumPlotFrequencyAxisScale::Logarithmic;

TSharedRef<AudioWidgets::FAudioSpectrumAnalyzer> SpectrumAnalyzer = 
    MakeShared<AudioWidgets::FAudioSpectrumAnalyzer>(Params);

// 获取可视化 Widget
TSharedRef<SWidget> SpectrumWidget = SpectrumAnalyzer->GetWidget();
```

### 进阶用法 — Analyzer Rack 框架

```cpp
// 来源: Public/AudioAnalyzerRack.h

// 创建 Analyzer Rack（可组合多个分析器的仪表盘）
AudioWidgets::FAudioAnalyzerRack::FRackConstructParams RackParams;
RackParams.TabManagerLayoutName = FName("MyAudioAnalyzerLayout");
RackParams.StyleSet = nullptr; // 使用默认样式

TSharedRef<AudioWidgets::FAudioAnalyzerRack> Rack = 
    MakeShared<AudioWidgets::FAudioAnalyzerRack>(RackParams);

// 初始化，指定通道数和音频设备
Rack->Init(NumChannels, AudioDeviceId);

// 创建 Rack Widget
TSharedRef<SWidget> RackWidget = Rack->CreateWidget(DockTab, SpawnTabArgs);

// 开始处理音频数据
Rack->StartProcessing();

// 处理完毕后停止
Rack->StopProcessing();
Rack->DestroyAnalyzers();
```

### 进阶用法 — 波形数据提供器（用于示波器/矢量示波器）

```cpp
// 来源: Public/WaveformAudioSamplesDataProvider.h

// 创建波形音频数据提供器
TSharedRef<AudioWidgets::FWaveformAudioSamplesDataProvider> DataProvider = 
    MakeShared<AudioWidgets::FWaveformAudioSamplesDataProvider>(
        AudioDeviceId,
        AudioBus,               // UAudioBus*
        2,                      // 要提供的通道数
        50.0f,                  // 时间窗口(ms)
        5000.0f,                // 最大时间窗口(ms)
        10.0f                   // 分析周期(ms)
    );

// 开始采集
DataProvider->StartProcessing();

// 监听数据更新
DataProvider->OnDataViewGenerated.AddLambda(
    [](FFixedSampledSequenceView View, uint32 FirstSampleIndex) {
        // 处理新到的波形数据
    }
);

// 调整参数
DataProvider->SetTimeWindow(100.0f);
DataProvider->SetTriggerMode(EAudioOscilloscopeTriggerMode::RisingEdge);
DataProvider->SetTriggerThreshold(0.5f);

// 停止采集
DataProvider->StopProcessing();
```

## Demo 示例

### 自定义音频混音器面板（.h + .cpp）

```cpp
// MyAudioMixerPanel.h
#pragma once

#include "CoreMinimal.h"
#include "AudioWidgetsModule.h"
#include "AudioMeter.h"
#include "AudioSpectrumAnalyzer.h"
#include "Components/Widget.h"

class SVerticalBox;
class SAudioMeter;
class SAudioSpectrumPlot;

class FMyAudioMixerPanel
{
public:
    FMyAudioMixerPanel(Audio::FDeviceId InDeviceId, int32 InNumChannels);
    ~FMyAudioMixerPanel();

    TSharedRef<SWidget> GetWidget() const { return PanelWidget.ToSharedRef(); }
    void Start();
    void Stop();

private:
    void BuildUI();

    Audio::FDeviceId DeviceId;
    int32 NumChannels;

    TSharedPtr<SVerticalBox> PanelWidget;
    TSharedPtr<AudioWidgets::FAudioMeter> Meter;
    TSharedPtr<AudioWidgets::FAudioSpectrumAnalyzer> SpectrumAnalyzer;
};
```

```cpp
// MyAudioMixerPanel.cpp
#include "MyAudioMixerPanel.h"
#include "AudioMeter.h"
#include "AudioSpectrumAnalyzer.h"
#include "Widgets/Layout/SBox.h"

FMyAudioMixerPanel::FMyAudioMixerPanel(Audio::FDeviceId InDeviceId, int32 InNumChannels)
    : DeviceId(InDeviceId)
    , NumChannels(InNumChannels)
{
    BuildUI();
}

FMyAudioMixerPanel::~FMyAudioMixerPanel()
{
    Stop();
}

void FMyAudioMixerPanel::BuildUI()
{
    // 创建电平表
    Meter = MakeShared<AudioWidgets::FAudioMeter>(
        NumChannels, DeviceId);

    // 创建频谱分析器
    AudioWidgets::FAudioSpectrumAnalyzerParams SpectrumParams;
    SpectrumParams.NumChannels = NumChannels;
    SpectrumParams.AudioDeviceId = DeviceId;
    SpectrumAnalyzer = MakeShared<AudioWidgets::FAudioSpectrumAnalyzer>(SpectrumParams);

    // 组装面板
    PanelWidget = SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            SNew(SBox)
            .HeightOverride(100.0f)
            [
                Meter->GetWidget()
            ]
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        .Padding(4.0f)
        [
            SpectrumAnalyzer->GetWidget()
        ];
}

void FMyAudioMixerPanel::Start()
{
    // Analyzer 内部会在初始化时自动开始分析
}

void FMyAudioMixerPanel::Stop()
{
    SpectrumAnalyzer.Reset();
    Meter.Reset();
}
```

## 模块依赖

从 Build.cs 分析，以下为该插件的独特依赖（忽略常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 频谱分析引擎（FFT、CQT、响度分析） |
| `AudioMixer` | 音频混音器、AudioBus、音频设备接口 |
| `AudioAnalyzer` | 音频分析器基础设施（AnalyzerRack 框架） |
| `SignalProcessing` | 信号处理工具 |
| `Analytics` | 分析统计（UnrealInsights 集成） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-05-12 | `fcaaf385` | [AudioWidgets] Loudness Meters: context menu polish. Reorganize settings into Loudness Scale, Refere | 响度计右键菜单优化，重新组织设置分类 |
| 2026-05-12 | `d2e95dfd` | [AudioWidgets] Loudness Meter: add max value indicator line on meters that support max value. | 为支持最大值的电平表添加最大值指示线 |
| 2026-05-12 | `ba019a16` | [AudioWidgets] Audio Meter: implemented ClippingValue draw in SAudioMeterWidget. | 实现 AudioMeter 中削波值的绘制 |
| 2026-05-12 | `bd1d2d5c` | [AudioWidgets] [Audio Insights] Loudness Meters: set different default colors for Range and True Pea | 响度计中 Range 和 True Peak 使用不同默认颜色 |

### 维护评价

- **活跃维护**：最近一次更新在 2026-05-13，仅 1 天前，且连续多天有功能更新
- **维护质量高**：近期改动集中在响度计功能增强和 AudioMeter 改进，属于持续迭代
- **历史悠久**：2020 年创建，从最初的 4 个基础控件发展为包含 20+ 控件的完整音频 UI 库
- **无废弃风险**：`.uplugin` 中无 deprecated 标记，代码中虽有少量 `UE_DEPRECATED(5.6, ...)` 的旧接口，但均有新接口替代
- **⚠️ 注意**：插件默认未启用（`Installed: false`），需在 Plugins 面板手动启用
- **⚠️ 注意**：`AudioWidgetsCore` 模块类型为 `RuntimeAndProgram`，仅限 UnrealInsights 程序使用

**推荐使用**：如果你需要在 UE5 中构建自定义音频界面，这是官方提供的最全面的音频 UI 控件库，功能完善且持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 依赖插件：[AudioSynesthesia](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)