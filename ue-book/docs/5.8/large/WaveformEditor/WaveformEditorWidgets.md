# Waveform Editor

> Editor tool for waveforms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 波形编辑器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，配置资产） |
| 模块 | `WaveformEditor` (Runtime), `WaveformEditorWidgets` (Runtime), `WaveformTransformations` (Runtime), `WaveformTransformationsWidgets` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor) | |

## 用途

WaveformEditor 插件是一个用于音频资产（`USoundWave`）的可视化编辑工具。它旨在为音频编辑器（如 Sound Cue 编辑器或可能的外部工具）提供核心的波形显示和交互功能，解决在编辑器内直接、直观地查看和操作音频波形的需求。

其核心功能是**为音频波形（PCM数据）及其变换效果提供一个可交互的UI**。它不是一个完整的音频编辑器，而是一个可嵌入的、功能强大的波形查看和编辑组件。它能够：
1.  **渲染波形**：将 `USoundWave` 的原始 PCM 数据可视化。
2.  **应用并可视化变换链**：支持在原始波形上叠加多个“变换”（如裁剪、淡入淡出等），并将变换后的结果实时渲染在原始波形之上，方便用户预览效果。
3.  **提供交互控制**：包括播放头移动、时间轴缩放、网格显示、选区操作等。

这个插件存在的主要原因是提供一个标准化的、高性能的波形渲染和交互框架，供 Unreal Engine 内部的音频编辑工具使用，避免各个工具重复开发基础波形显示功能。

## 使用场景

-   **音频设计师**在 Unreal 编辑器内编辑音效（`Sound Wave`）时，需要查看波形细节、裁剪静音部分、设置淡入淡出点，可以使用此插件提供的界面。
-   **开发音频编辑器插件**时，需要一个成熟的波形显示和交互控件，可以直接集成此插件的 `STransformedWaveformViewPanel` 或相关组件。
-   **需要为自定义的音频变换（`UWaveformTransformationBase` 子类）创建对应的编辑器 UI**，可以使用 `FWaveformTransformationRenderLayerFactory` 和相关接口来注册和渲染变换层。

## 蓝图用法

此插件主要提供 Slate 控件和 C++ 服务类，蓝图直接交互的节点较少。但其配置资产 `UWaveformEditorWidgetsSettings` 是蓝图可访问的，用于全局定制波形编辑器的外观。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateLayersChain` | 当波形变换链发生变化时调用，用于重新生成变换层的 UI | `FWaveformEditorSequenceDataProvider` |
| `UpdateRenderElements` | 当变换参数变化时调用，用于更新渲染数据并通知 UI 刷新 | `FWaveformEditorSequenceDataProvider` |
| `SetPlayheadRatio` | 设置播放头在波形中的相对位置（0.0 - 1.0） | `STransformedWaveformViewPanel` |
| `SetPlayheadFramePosition` | 根据采样帧位置设置播放头位置 | `STransformedWaveformViewPanel` |
| `ReceiveSequenceView` | 接收新的波形数据视图用于显示 | `STransformedWaveformViewPanel` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接操作 `STransformedWaveformViewPanel`，而是通过 C++ 代码创建和管理它。但是，你可以通过修改 `UWaveformEditorWidgetsSettings` 资产来改变波形编辑器的颜色、线条粗细等视觉属性。在项目设置（Project Settings）中找到 “Waveform Editor Display” 分类，即可修改相关参数。

## C++ 用法

### 头文件引入

```cpp
// 引入核心数据提供者和视图面板
#include "WaveformEditorSequenceDataProvider.h"
#include "STransformedWaveformViewPanel.h"
// 引入配置类
#include "WaveformEditorWidgetsSettings.h"
```

### 基本用法

创建一个波形编辑器视图的核心是实例化 `FWaveformEditorSequenceDataProvider` 和 `STransformedWaveformViewPanel`。

```cpp
// 假设你已经有一个有效的 USoundWave 指针
USoundWave* MySoundWave = ...; // 从内容浏览器获取或创建

// 1. 创建数据提供者
FWaveformEditorSequenceDataProvider DataProvider(MySoundWave);

// 2. 创建 Slate 视图面板
TSharedRef<STransformedWaveformViewPanel> WaveformPanel = SNew(STransformedWaveformViewPanel);
// 通过一个临时的 `FFixedSampledSequenceView` 或直接从数据提供者获取初始数据来构造面板
// WaveformPanel->Construct(Arguments, DataProvider.RequestSequenceView(...));

// 3. 通常，你会将 WaveformPanel 添加到一个 SWindow 或 SOverlay 中显示。
// 4. 当需要应用变换时，调用数据提供者的方法更新状态和 UI。
DataProvider.GenerateLayersChain(); // 应用变换后调用
DataProvider.UpdateRenderElements(); // 变换参数变化时调用
```

**来源参考**：基本结构基于 `FWaveformEditorSequenceDataProvider` 和 `STransformedWaveformViewPanel` 的公共接口。

### 进阶用法

你可以监听数据提供者发出的委托，以响应波形数据或UI的更新。

```cpp
// 监听数据视图更新（例如，用于其他需要波形数据的控件）
DataProvider.OnDataViewGenerated.AddLambda([](FFixedSampledSequenceView View, uint32 FirstSampleIndex)
{
    // 使用新的视图数据
});

// 监听变换层链更新
DataProvider.OnLayersChainGenerated.AddLambda([](FTransformationRenderLayerInfo* FirstLayer, int32 NumLayers)
{
    // 可以获取变换层信息进行进一步处理
});

// 自定义样式：通过修改 UWaveformEditorWidgetsSettings 来改变全局外观
// 首先获取设置对象
const UWaveformEditorWidgetsSettings* Settings = GetDefault<UWaveformEditorWidgetsSettings>();
// 然后使用 Settings->PlayheadColor, Settings->WaveformLineThickness 等属性。
// 监听设置变更：
FWaveformEditorStyle::OnNewPlayheadOverlayStyle.AddLambda([](FPlayheadOverlayStyle NewStyle){
    // 响应播放头样式变化
});
```

## Demo 示例

一个最小化的示例，展示如何在编辑器工具中创建并显示一个波形编辑器面板。

```cpp
// MyAudioEditorWidget.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "WaveformEditorSequenceDataProvider.h"
#include "STransformedWaveformViewPanel.h"

class SMyAudioEditorWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyAudioEditorWidget) {}
        SLATE_ARGUMENT(USoundWave*, SoundWave)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<FWaveformEditorSequenceDataProvider> DataProvider;
    TSharedPtr<STransformedWaveformViewPanel> WaveformPanel;
};

// MyAudioEditorWidget.cpp
#include "MyAudioEditorWidget.h"

void SMyAudioEditorWidget::Construct(const FArguments& InArgs)
{
    if (InArgs._SoundWave)
    {
        // 创建数据提供者
        DataProvider = MakeShareable(new FWaveformEditorSequenceDataProvider(InArgs._SoundWave));

        // 创建并初始化波形面板
        // 注意：实际构造时需要提供合适的参数和数据，此处为示意
        WaveformPanel = SNew(STransformedWaveformViewPanel);
        // 初始化面板布局...
        // WaveformPanel->Construct(FArguments(), DataProvider->RequestSequenceView(FRange(0.0, 1.0)));

        // 将面板添加到本控件的子层级
        ChildSlot
        [
            WaveformPanel.ToSharedRef()
        ];

        // 生成初始变换层（如果需要）
        // DataProvider->GenerateLayersChain();
    }
}
```

## 模块依赖

你的模块若要使用 `WaveformEditor` 插件，通常需要依赖 `WaveformEditorWidgets` 和 `WaveformEditor` 模块。

| 模块 | 用途 |
|---|---|
| `WaveformEditor` | 核心波形处理、变换和音频分析功能 |
| `WaveformTransformations` | 波形变换的基类定义 |
| `AudioMixer` | 底层音频数据处理和采样率转换 |
| `SampledSequenceView` | 提供 `FFixedSampledSequenceView` 等基础数据结构和接口 |
| `AssetRegistry` | 用于处理 `USoundWave` 资产的加载和引用 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `40a5c76a` | [Waveform] Performance regression when dragging trimfade extents | 修复了拖拽修剪/淡出控件时的性能回退问题 |
| 2026-05-14 | `1f67ea84` | [Waveform editor] Remove no-op trimfade transform option | 移除了无效的修剪淡出变换选项，简化UI |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的编译警告 |
| 2026-04-28 | `d67c3aa3` | [Waveform editor] - Shift + space returns playhead to start, but playback does not start at beginnin | 修复了Shift+空格键重置播放头但播放不从头开始的问题 |
| 2026-04-17 | `93be7d91` | [Waveform] Performance regression when dragging trimfade extents | 修复了拖拽修剪/淡出控件时的性能回退问题 |

### 维护评价

WaveformEditor 插件是一个**活跃维护中**的实验性模块。

-   **创建时间**：约4年前（2022年），对于核心编辑器功能来说较新。
-   **近期更新**：最近提交集中在**性能优化**和**交互逻辑修复**（如播放头行为、拖拽性能），表明其正在从基础功能向稳定性和用户体验优化阶段过渡。更新频率较高。
-   **实验性状态**：`.uplugin` 标记为 `IsBetaVersion: true`，且 `EnabledByDefault: false`，这意味着它还未被认为是稳定API，可能存在未完成的特性或未来的接口变动，不建议用于需要长期稳定维护的项目代码中，但非常适合早期采用和反馈。
-   **推荐使用**：**推荐在编辑器工具开发中谨慎使用**。如果你正在开发一个需要波形显示的编辑器工具，并且能够接受潜在的API变化，这是一个强大的基础。对于最终用户来说，它是一个隐藏在音频编辑功能背后的强大引擎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中明确列出)