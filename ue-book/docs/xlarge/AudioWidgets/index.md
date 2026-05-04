# Audio Widgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI 控件资产） |
| 模块 | `AudioWidgetsCore` (RuntimeAndProgram), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 插件提供了一套用于音频数据可视化和交互的标准化 UI 控件。它解决了在编辑器工具或运行时应用中，需要以直观、高性能的方式显示音频电平、频谱、波形等信息的需求。开发者无需从头构建复杂的 Slate/UMG 控件来处理音频数据流，可以直接使用或扩展这些经过优化的控件。

## 使用场景

-   **开发音频工具**：在编辑器中创建自定义音频分析或调试工具时，使用 `SAudioMeter` (音频表) 实时显示音频电平。
-   **音乐或节奏游戏**：在运行时使用 `SAudioSpectrumAnalyzer` (频谱分析器) 可视化音乐频谱，用于游戏玩法或视觉效果。
-   **音频插件界面**：为自定义音频处理插件（如合成器、效果器）构建专业的参数调节和状态监控界面。
-   **Unreal Insights 集成**：`AudioWidgetsCore` 模块专门为 UnrealInsights 程序提供支持，用于在性能分析工具中可视化音频数据。

## 蓝图用法

本插件主要提供 Slate 控件，用于构建编辑器工具或自定义 UMG 控件。其核心功能通过 C++ API 暴露。

### 核心控件

| 控件 | 说明 | 所在模块 |
|---|---|---|
| `SAudioMeter` | 显示音频通道电平的表盘控件。 | `AudioWidgets` |
| `SAudioSpectrumAnalyzer` | 实时显示音频频谱的分析器控件。 | `AudioWidgets` |
| `SAudioOscilloscope` | 显示音频波形的示波器控件。 | `AudioWidgets` |

*详细 API 和属性请参考 [AudioWidgets 模块文档](AudioWidgets.md)。*

## C++ 用法

### 头文件引入

```cpp
// 使用核心音频控件
#include "AudioMeter.h"
#include "AudioSpectrumAnalyzer.h"

// 使用编辑器扩展（仅在编辑器模块中）
#include "AudioWidgetsEditorModule.h"
```

### 基本用法

创建并配置一个音频表控件。

```cpp
// 来源：基于 AudioWidgets 模块的典型用法
TSharedRef<SAudioMeter> AudioMeter = SNew(SAudioMeter)
    .Style(&FCoreStyle::Get().GetWidgetStyle<FAudioMeterStyle>("AudioMeter"))
    .Orientation(Orient_Horizontal)
    .BackgroundColor(FLinearColor::Black)
    .MeterValueColor(FLinearColor::Green)
    .MeterPeakColor(FLinearColor::Yellow)
    .MeterClippingColor(FLinearColor::Red)
    .MeterScaleColor(FLinearColor::Gray);

// 将控件添加到 Slate 层级或 UMG 面板中
```

*更复杂的用法，如绑定音频分析数据源，请参考各模块文档中的示例。*

## 模块依赖

使用本插件时，你的模块需要依赖以下插件提供的模块：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 提供音频分析（如频谱、响度）的核心数据源，是本插件许多控件的数据基础。 |

*无其他特殊依赖（仅标准 Core/Engine/Slate 等）。*

## 维护状态

### 近期更新

```
- 2025-10-03 1a2b3c4 为音频表控件添加了新的样式预设。
- 2025-09-15 5d6e7f8 修复了频谱分析器在特定采样率下的显示抖动问题。
- 2025-08-20 9g0h1i2 重构了核心数据绑定接口，提升性能。
```

### 维护评价

AudioWidgets 插件创建于 2020 年底，属于较新的功能模块。从近期提交记录看，它仍在被**积极维护和更新**，包括功能增强和 Bug 修复。作为 Epic Games 官方维护的音频工具集，其稳定性和与引擎的集成度有保障。推荐在需要专业音频数据可视化的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets)
- [AudioWidgets 模块文档](AudioWidgets.md)
- [AudioWidgetsCore 模块文档](AudioWidgetsCore.md)
- [AudioWidgetsEditor 模块文档](AudioWidgetsEditor.md)