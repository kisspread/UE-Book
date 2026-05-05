# WaveformEditorWidgets 模块

> 波形编辑器的 UI 组件模块，提供波形显示面板、缩放控制、网格数据、样式管理等 Slate 控件。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| LoadingPhase | Default |

## 概述

`WaveformEditorWidgets` 提供了波形编辑器的所有可视化 UI 组件。核心是 `STransformedWaveformViewPanel` —— 一个复合 Slate 控件，包含波形显示、时间标尺、播放头、变换叠加层、网格等子控件。

该模块还管理波形数据的转换和变换渲染层链的生成。

## 核心类

### STransformedWaveformViewPanel

波形编辑器的主视图面板，组合了多个子控件：

| 子控件 | 类型 | 说明 |
|---|---|---|
| `TimeRuler` | `SFixedSampledSequenceRuler` | 时间标尺 |
| `WaveformViewer` | `SFixedSampledSequenceViewer` | 波形数据可视化 |
| `PlayheadOverlay` | `SPlayheadOverlay` | 播放头覆盖层 |
| `WaveformTransformationsOverlay` | `SWaveformTransformationsOverlay` | 变换叠加层 |
| `InputRoutingOverlay` | `SWaveformEditorInputRoutingOverlay` | 输入事件路由 |
| `ValueGridOverlay` | `SSampledSequenceValueGridOverlay` | 值网格 |
| `BackgroundBorder` | `SBorder` | 背景 |

实现 `IFixedSampledSequenceViewReceiver` 接口，接收序列数据更新。

**关键方法：**

| 方法 | 说明 |
|---|---|
| `ReceiveSequenceView()` | 接收新的波形数据视图 |
| `SetPlayheadRatio()` | 设置播放头位置（0~1 比例） |
| `Tick()` | 每帧更新布局和播放头位置 |

### FWaveformEditorSequenceDataProvider

核心数据提供者，实现 `IFixedSampledSequenceViewProvider` 接口。

**职责：**
- 从 USoundWave 加载原始 PCM 数据
- 应用变换链生成变换后的 PCM 数据
- 为每个变换创建对应的渲染层（Render Layer）
- 管理变换后波形的边界范围

**关键方法：**

| 方法 | 说明 |
|---|---|
| `RequestSequenceView()` | 请求特定范围的波形数据视图 |
| `GenerateLayersChain()` | 变换链变更时重新生成渲染层 |
| `UpdateRenderElements()` | 变换参数变更时更新渲染元素 |
| `GetTransformedPCMData()` | 获取变换后的 PCM 数据 |
| `GetTransformedWaveformBounds()` | 获取变换后波形的时间边界 |

**委托：**

| 委托 | 说明 |
|---|---|
| `OnLayersChainGenerated` | 新的渲染层链创建时触发 |
| `OnRenderElementsUpdated` | 渲染元素更新时触发 |
| `OnDataViewGenerated` | 新数据视图生成时触发 |

### SWaveformTransformationsOverlay

变换叠加层控件，管理多个变换渲染器的空间布局。

使用 `SConstraintCanvas` 布局，每个变换渲染器占据一个带锚点约束的 slot。支持缩放时自动更新约束。

处理鼠标事件的路由和光标样式查询。

### SWaveformTransformationRenderLayer

单个变换渲染层的 Slate 控件容器。实现 `SLATE_DECLARE_WIDGET` 以支持自定义绘制。

将所有 Slate 事件（鼠标、键盘、绘制）转发给内部的 `IWaveformTransformationRenderer` 实例。

### FWaveformEditorZoomController

缩放控制器，管理波形视图的缩放和水平平移。

| 方法 | 说明 |
|---|---|
| `ZoomIn()` / `ZoomOut()` | 放大/缩小 |
| `ZoomByDelta()` | 按增量缩放 |
| `GetZoomRatio()` | 获取当前缩放比例 |
| `CheckBounds()` | 检查并限制平移范围 |

**缩放机制：** 使用对数缩放（base 100），`ZoomLevelStep = 2`，通过 `ConvertZoomLevelToLogRatio()` 转换为实际显示比例。

支持鼠标中键拖拽平移（`bIsPanning`）。

### FWaveformEditorGridData

网格数据服务，实现 `IFixedSampledSequenceGridService` 接口。

管理时间标尺的刻度、帧率和网格密度。根据显示范围和像素宽度动态调整网格间距。

| 方法 | 说明 |
|---|---|
| `UpdateDisplayRange()` | 更新显示范围 |
| `UpdateGridMetrics()` | 更新网格度量 |
| `SnapPositionToClosestFrame()` | 将像素位置吸附到最近的帧 |

### FWaveformTransformationRenderLayerFactory

工厂类，根据 `UWaveformTransformationBase` 的类型创建对应的 `IWaveformTransformationRenderer` 实例。

通过 `FWaveformTransformationRendererMapper` 单例查找注册的渲染器类型。

### FWaveformEditorStyle

样式管理单例，继承 `FSlateStyleSet`。

管理播放头、时间标尺、值网格、波形查看器的视觉样式。监听 `UWaveformEditorWidgetsSettings` 的变更，通过委托通知样式更新。

### SWaveformEditorMessageDialog

简单的消息对话框控件，用于在波形编辑器中显示通知消息。

## 类型别名

```cpp
using FTransformationLayerConstraints = TPair<float, float>;
using FTransformationRenderLayerInfo = TPair<TSharedPtr<IWaveformTransformationRenderer>, FTransformationLayerConstraints>;
using FTransformationToPropertiesPair = TPair<TObjectPtr<UWaveformTransformationBase>, TArray<TSharedRef<IPropertyHandle>>>;
```

## 依赖模块

| 模块 | 用途 |
|---|---|
| `WaveformTransformationsWidgets` | 变换渲染器接口和映射 |
| `AudioExtensions` | 音频扩展接口 |
| `AudioWidgets` | 音频 Slate 控件 |
| `SignalProcessing` | 信号处理 |
| `Slate` / `SlateCore` | UI 框架 |
| `UMG` | UMG 框架 |
| `InputCore` | 输入处理 |
