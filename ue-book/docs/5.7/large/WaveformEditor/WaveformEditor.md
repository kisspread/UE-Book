# WaveformEditor 模块

> 核心编辑器模块，提供波形编辑器的主框架、工具栏命令、音频播放控制及波形导出功能。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| LoadingPhase | Default |

## 概述

`WaveformEditor` 是整个插件的核心模块，基于 `FAssetEditorToolkit` 构建了完整的 SoundWave 资产编辑器。它协调了波形显示、音频回放、变换操作和导出等所有子系统。

该模块将编辑器注册为 USoundWave 的自定义资产编辑器，用户可以在内容浏览器中右键点击音频资产直接打开波形编辑器。

## 核心类

### FWaveformEditor

继承自 `FAssetEditorToolkit`、`FEditorUndoClient`、`FGCObject`、`FNotifyHook`，是编辑器的主入口类。

**职责：**
- 初始化编辑器布局（3 个标签页：属性面板、变换面板、波形显示）
- 管理音频组件（UAudioComponent）的生命周期
- 协调播放控制器（TransportController）、缩放控制器（ZoomManager）
- 处理变换链（TrimFade、Markers 等）的增删改
- 处理撤销/重做（FEditorUndoClient）
- 支持波形导出到新资产

**关键方法：**

| 方法 | 说明 |
|---|---|
| `Init()` | 初始化编辑器，传入要编辑的 USoundWave |
| `ExportWaveform()` | 导出变换后的波形 |
| `OnAssetReimport()` | 处理资产重新导入事件 |
| `NotifyPostChange()` | 属性变更后的回调，触发变换重新计算 |

**内部子系统：**

| 成员 | 类型 | 说明 |
|---|---|---|
| `WaveformView` | `FTransformedWaveformView` | 波形视图（Widget + 数据提供者） |
| `TransportController` | `FWaveformEditorTransportController` | 音频播放控制 |
| `ZoomManager` | `FWaveformEditorZoomController` | 缩放控制 |
| `WaveWriter` | `FWaveformEditorWaveWriter` | 波形导出写入器 |

### FWaveformEditorTransportController

管理 USoundWave 的音频播放状态。

| 方法 | 说明 |
|---|---|
| `Play()` / `Play(StartTime)` | 播放音频 |
| `Pause()` | 暂停 |
| `Stop()` | 停止 |
| `TogglePlayback()` | 切换播放/暂停 |
| `Seek(SeekTime)` | 跳转到指定时间 |
| `CacheStartTime()` | 缓存起始时间 |
| `CanPlay()` / `IsPlaying()` | 状态查询 |

### FWaveformEditorCommands

定义所有工具栏命令（快捷键绑定）：

- **播放控制**：Play、Pause、Stop、TogglePlayback、ReturnToStart
- **缩放**：ZoomIn、ZoomOut
- **导出**：ExportWaveform、ExportFormatMono/Stereo
- **重新导入**：ReimportAsset、ReimportModeSameFile/Overwrite/NewFile
- **淡入/淡出**：ToggleFadeIn/Out、FadeIn/OutLinear/Exponential/Logarithmic/Sigmoid
- **裁剪边界**：LeftBoundsIncrease/Decrease、RightBoundsIncrease/Decrease、ZeroCrossing 系列
- **标记**：CreateMarker、CreateLoopRegion、DeleteMarker、SkipToNextMarker

### FWaveformEditorModule / IWaveformEditorModule

模块接口和实现，负责注册内容浏览器扩展，使 USoundWave 的右键菜单中出现"Waveform Editor"选项。

### IWaveformEditorInstantiator

接口类，定义了波形编辑器的创建入口：
- `ExtendContentBrowserSelectionMenu()` — 扩展内容浏览器菜单
- `RegisterAsSoundwaveEditor()` — 注册为 SoundWave 编辑器
- `CreateWaveformEditor()` — 创建编辑器实例

### FWaveformEditorWaveWriter (Private)

负责将变换后的波形数据导出为新的音频文件。支持：
- Mono/Stereo 通道格式选择
- 混缩/上混通道转换
- 归一化处理

### UWaveformEditorTransformationsSettings (Private)

`UDeveloperSettings` 子类，配置编辑器启动时的默认变换链和零交叉检测的噪声阈值。

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `LaunchTransformations` | 启动时自动添加的变换类型集合 | 空 |
| `NoiseThreshold` | 零交叉检测噪声阈值 (dB) | -60.0 |

### FWaveformTransformationsDetailsCustomization (Private)

IDetailCustomization 实现，自定义变换属性面板的显示布局。

## 重导入模式

编辑器支持 3 种重导入模式（EWaveEditorReimportMode）：

| 模式 | 说明 |
|---|---|
| SameFile | 从原文件重新导入，保留变换 |
| SameFileOverwrite | 从原文件重新导入，覆盖变换 |
| SelectFile | 选择新文件导入 |

## 依赖模块

| 模块 | 用途 |
|---|---|
| `WaveformEditorWidgets` | 波形视图控件 |
| `WaveformTransformations` | 音频变换算法 |
| `WaveformTransformationsWidgets` | 变换可视化渲染器 |
| `AudioExtensions` | 音频扩展接口 |
| `AudioSynesthesiaCore` | 音频分析核心 |
| `AudioWidgets` | 音频 UI 控件 |
| `SignalProcessing` | 信号处理 |
| `ToolMenus` | 工具菜单系统 |
| `UnrealEd` | 编辑器框架 |
| `AssetDefinition` | 资产定义（Private） |
| `AudioEditor` | 音频编辑器（Private） |
