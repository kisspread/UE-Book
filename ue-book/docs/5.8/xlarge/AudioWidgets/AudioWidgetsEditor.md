# Audio Widgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 中文名 | 音频控件集 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图控件、材质） |
| 模块 | `AudioWidgetsCore` (RuntimeAndProgram), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

该插件的核心用途是为Unreal Insights程序提供一套专业的、可复用的音频调试和监控UI控件。它解决了在生产环境（非编辑器内）中，缺乏专用、美观且功能丰富的音频系统可视化界面的问题。插件通过Slate和UMG控件，将音频数据（如音量、响度、频谱）和系统状态以直观的图表、仪表盘和按钮形式展现，主要用于音频性能分析和调试。

## 使用场景

-   你在使用 **Unreal Insights** 进行性能分析，需要实时观察音频总线的音量、音频资产的状态。
-   你需要为游戏内的音频可视化（如音乐播放器界面）创建专业、风格统一的UI控件。
-   你正在开发一个音频工具，需要一个包含旋钮、滑块、电平表和频谱显示的现成控件库。

## 蓝图用法

`AudioWidgets` 模块提供了一系列蓝图可用的控件。虽然源码分析有限，但基于插件创建信息和常见音频控件，可推断其核心节点如下：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Audio Meter Value` | 设置音频电平表的当前值 | `UAudioMeterWidget` |
| `Set Audio Oscilloscope Source` | 为示波器控件设置音频数据源 | `UAudioOscilloscopeWidget` |
| `Set Audio Spectrum Analyzer Source` | 为频谱分析仪设置音频数据源 | `UAudioSpectrumAnalyzerWidget` |
| `Set Knob Value` | 设置旋钮控件的当前值 | `UAudioKnobWidget` |
| `Set Button State` | 设置音频切换按钮的状态 | `UAudioButtonWidget` |

### 使用示例（蓝图描述）

1.  在你的UI蓝图中，从控件面板拖入一个 `AudioMeter` 控件。
2.  通过`Set Audio Meter Value`节点，将音频系统（如 `Sound Submix`）的音量数据连接到该控件的输入。
3.  为了实时更新，你可以在 `Event Tick` 中持续获取音量数据并调用此节点。

## C++ 用法

该插件的Runtime模块（`AudioWidgets`）提供了Slate和UMG控件的C++实现。用户主要通过UMG在蓝图中使用，但也可在C++代码中创建和管理这些控件。

### 头文件引入

```cpp
#include "AudioWidgetsModule.h"
// 引入具体控件头文件，例如:
#include "AudioMeterWidget.h"
#include "AudioRadialSlider.h"
```

### 基本用法

```cpp
// 创建一个音频电平表控件（Slate层）
TSharedRef<SAudioMeter> SlateMeter = SNew(SAudioMeter);
SlateMeter->SetMeterValue(FMeterValue::Create(0.5f, 0.7f, 0.6f));

// 对于UMG控件，通常在蓝图中完成创建和绑定，C++中主要负责提供数据
```

*代码逻辑基于Slate/UMG控件通用模式推断*

### 进阶用法

可以继承或组合这些控件，创建自定义的音频调试面板。例如，组合 `SAudioOscilloscope`、`SAudioSpectrumAnalyzer` 和 `SAudioRadialSlider`，构建一个完整的音频分析窗口。

## Demo 示例

```cpp
// MyAudioDebugPanel.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyAudioDebugPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyAudioDebugPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
private:
    TSharedPtr<class SAudioMeter> AudioMeterWidget;
};

// MyAudioDebugPanel.cpp
#include "MyAudioDebugPanel.h"
#include "SAudioMeter.h"

void SMyAudioDebugPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Audio Level")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SAssignNew(AudioMeterWidget, SAudioMeter)
            .ShowMeterValueLabel(true)
            .ShowPeakMeterValue(true)
        ]
    ];
}
```

## 模块依赖

你的模块需要在 `.Build.cs` 文件中添加以下依赖才能使用本插件的功能：

| 模块 | 用途 |
|---|---|
| `AudioWidgets` | 核心音频控件运行时模块 |
| `AudioWidgetsEditor` | 编辑器特定功能（如属性注入），在编辑器工具中使用时依赖 |
| `AudioSynesthesia` | 插件依赖，用于高级音频分析（如响度） |

**无特殊依赖（仅标准 Slate/UMG 等）**

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `fcaaf385` | [AudioWidgets] Loudness Meters: context menu polish. Reorganize settings into Loudness Scale, Refere... | 响度表右键菜单优化，重新组织了设置项。 |
| 2026-05-12 | `d2e95dfd` | [AudioWidgets] Loudness Meter: add max value indicator line on meters that support max value. | 响度表增加了最大值指示线。 |
| 2026-05-12 | `ba019a16` | [AudioWidgets] Audio Meter: implemented ClippingValue draw in SAudioMeterWidget. | 实现了音频电平表的削波值绘制。 |
| 2026-05-12 | `bd1d2d5c` | [AudioWidgets] [Audio Insights] Loudness Meters: set different default colors for Range and True Pea... | 为响度表设置了不同的默认颜色（范围和真峰值）。 |

### 维护评价

该插件**正在被积极维护**。从2020年底创建以来，最近一次更新在2026年5月，专注于提升响度表（Loudness Meter）等核心控件的功能细节和用户体验。更新频率较高，内容集中在功能完善和UI打磨上，表明Epic仍将其作为Unreal Insights音频调试功能的重要组成部分。推荐在需要专业音频调试UI的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets)
- [官方文档]()
- [测试用例]()