# WaveformTransformationsWidgets 模块

> 变换可视化渲染模块，为每种变换类型提供交互式图形渲染器，支持鼠标拖拽编辑参数。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| LoadingPhase | Default |

## 概述

`WaveformTransformationsWidgets` 提供了波形变换的可视化渲染系统。每个变换类型都有对应的渲染器（Renderer），负责在波形视图上绘制变换的视觉表示，并处理鼠标交互来编辑变换参数。

渲染器通过 `FWaveformTransformationRendererMapper` 单例注册，由 `FWaveformTransformationRenderLayerFactory` 创建。

## 渲染器接口

### IWaveformTransformationRenderer

所有变换渲染器的抽象接口。

**SWidget 事件转发方法：**

| 方法 | 说明 |
|---|---|
| `OnPaint()` | 自定义绘制 |
| `Tick()` | 每帧更新 |
| `OnMouseButtonDown/Up()` | 鼠标点击 |
| `OnMouseButtonDoubleClick()` | 双击 |
| `OnMouseMove()` | 鼠标移动 |
| `OnMouseWheel()` | 鼠标滚轮 |
| `OnMouseEnter/Leave()` | 鼠标进入/离开 |
| `OnCursorQuery()` | 光标样式查询 |
| `OnKeyUp()` | 键盘释放 |

**数据方法：**

| 方法 | 说明 |
|---|---|
| `SetTransformationWaveInfo()` | 设置波形信息（采样率、通道数、帧偏移等） |
| `SetWaveformTransformation()` | 设置关联的变换 UObject |

### FWaveformTransformationRenderInfo

传递给渲染器的波形信息结构体：

| 字段 | 类型 | 说明 |
|---|---|---|
| `SampleRate` | float | 采样率 |
| `NumChannels` | int32 | 通道数 |
| `StartFrameOffset` | int64 | 变换作用的起始帧偏移 |
| `TotalNumSamples` | uint32 | 原始波形总采样数 |
| `NumSamplesAvailable` | uint32 | 变换可用的采样数 |

## 渲染器基类

### FWaveformTransformationRendererBase

提供所有渲染器的默认实现：
- 默认的 `OnPaint()` 空实现
- 鼠标事件的默认转发
- `TransformationWaveInfo` 的存储
- 编辑器事务（Transaction）的 Begin/End 包装
- 已废弃的 `IPropertyHandle` 支持（5.7 废弃）

**交互常量：**

| 常量 | 值 | 说明 |
|---|---|---|
| `InteractionPixelXDelta` | 10 | X 方向交互检测像素容差 |
| `InteractionRatioYDelta` | 0.07 | Y 方向交互检测比例容差 |
| `MouseWheelStep` | 0.1 | 鼠标滚轮步进 |

## 具体渲染器

### FWaveformTransformationTrimFadeRenderer

为 `UWaveformTransformationTrimFade` 提供可视化。

**绘制内容：**
- 裁剪手柄（左右两条竖线）
- 淡入曲线（左侧区域）
- 淡出曲线（右侧区域）

**交互模式 (ETrimFadeInteractionType)：**

| 模式 | 说明 |
|---|---|
| ScrubbingLeftHandle | 拖拽左裁剪手柄 |
| ScrubbingRightHandle | 拖拽右裁剪手柄 |
| ScrubbingFadeIn | 拖拽调整淡入曲线 |
| ScrubbingFadeOut | 拖拽调整淡出曲线 |
| RightClickFadeIn | 右键选择淡入模式菜单 |
| RightClickFadeOut | 右键选择淡出模式菜单 |

右键点击淡入/淡出区域会弹出模式选择菜单（Linear/Exponential/Logarithmic/Sigmoid）。

### FWaveformTransformationMarkerRenderer

为 `UWaveformTransformationMarkers` 提供可视化。

**绘制内容：**
- 标记手柄（Cue Points）— 竖线 + 标签
- 循环区域（Loop Regions）— 半透明矩形 + 左右手柄

**交互模式 (EMarkerInteractionType)：**

| 模式 | 说明 |
|---|---|
| ScrubbingMarkerHandleRight/Left | 拖拽循环区域的左右手柄 |
| LoopHandle | 拖拽循环区域移动 |
| MarkerHandle | 拖拽标记位置 |
| RightClickMarker | 右键上下文菜单 |
| DeselectRegion | 取消选择区域 |

**特性：**
- 标记和循环区域使用可配置的颜色（通过 Settings）
- 支持循环区域预览（在编辑器内播放循环区域）
- 右键菜单支持将标记转换为循环区域

### FWaveformTransformationDurationRenderer

显示变换后波形的有效时长高亮。用半透明矩形标记被裁剪掉的区域。

## 注册系统

### FWaveformTransformationRendererMapper

单例映射器，维护 `UClass*` → `FWaveformTransformRendererInstantiator` 的映射。

```cpp
// 注册渲染器
FWaveformTransformationRendererMapper::Get().RegisterRenderer<FWaveformTransformationTrimFadeRenderer>(
    UWaveformTransformationTrimFade::StaticClass());

// 查找渲染器
auto* Instantiator = FWaveformTransformationRendererMapper::Get().RendererFor(MyTransformationClass);
```

## 模块初始化

`FWaveformTransformationsWidgetsModule` 在 `StartupModule()` 中：
1. 初始化 `FWaveformTransformationRendererMapper`
2. 注册内置渲染器（TrimFade、Markers、Duration）

## 依赖模块

| 模块 | 用途 |
|---|---|
| `WaveformTransformations` | 变换 UObject 类型 |
| `AudioWidgets` | 音频 UI 样式类型 |
| `PropertyEditor` | 属性编辑器（已部分废弃） |
| `Slate` / `SlateCore` | Slate UI 框架 |
| `UMG` | UMG 框架 |
| `SignalProcessing` | 信号处理 |
