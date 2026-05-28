# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDIMedia 插件实现了基于 NDI (Network Device Interface) 协议的媒体源（Media Source）和媒体输出（Media Output）。NDI 是一种广泛应用于专业视频制作和直播行业的网络视频传输协议，它允许在局域网内以高质量、低延迟传输视频和音频流。

该插件的核心价值在于将 Unreal Engine 无缝接入 NDI 生态系统，使引擎既能作为**NDI流的接收端**（用于监看、合成外部视频源），也能作为**NDI流的发送端**（将引擎实时渲染画面推送到导播台、其他软件或硬件设备）。这解决了专业虚拟制片、实时渲染合成和现场直播工作流中的关键互操作性问题。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `NDIMedia` | Runtime | 核心运行时模块，实现NDI协议的媒体源、播放器和输出功能 |
| `NDIMediaEditor` | Editor | 编辑器支持模块，提供相关的资产编辑器和设置界面 |
| `NDIMediaRendering` | Runtime | 渲染集成模块，负责将引擎渲染内容高效编码为NDI流输出 |
| `NDISDK` | External | 第三方NDI SDK封装，提供底层的NDI接口 |

## 使用场景

- **虚拟制片（Virtual Production）**：将UE引擎实时渲染的Final Pixel画面通过NDI发送给现场的视频切换台（如vMix， ATEM），与摄像机实拍画面进行实时合成。
- **多机位直播与导播**：在直播或活动现场，将多个UE场景（如不同视角）作为NDI源提供给导播软件进行切换。
- **实时渲染合成**：将UE输出的带有Alpha通道的NDI流，导入到后期合成软件（如After Effects）或其他支持NDI的渲染器中进行最终合成。
- **监看与调试**：在开发过程中，将编辑器或运行时的游戏视图以NDI流形式发送到其他显示器或设备进行监看，无需复杂的硬件设置。

## 蓝图用法

插件主要通过媒体播放器（Media Player）和媒体输出（Media Output）系统在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 使用配置好的`NDIMediaSource`资产打开一个NDI流进行播放 | `UMediaPlayer` |
| `Set Media Output` | 将媒体输出设置为`NDIMediaOutput`，用于定义NDI发送参数 | `UMediaTexture` / `UTextureRenderTarget2D` |
| `Get Available Sources` | 动态枚举当前网络中所有可用的NDI源名称 | `UNDIMediaFunctionLibrary` |

### 使用示例（蓝图描述）
1. **接收NDI流**：在蓝图中创建一个`MediaPlayer`组件，对其调用`Open Source`节点，并关联一个配置了目标NDI源名称的`NDIMediaSource`资产。将该`MediaPlayer`连接到一个`MediaTexture`以在场景中显示。
2. **发送NDI流**：创建一个`NDIMediaOutput`资产，配置输出名称。在蓝图中获取要发送的渲染目标（如场景捕获组件的输出），调用`Set Media Output`节点并传入该输出资产，即可将画面作为NDI流广播到网络。

## C++ 用法

### 头文件引入
```cpp
#include "NDIMediaModule.h"
// 根据具体功能引入：
#include "NDIMediaSource.h"
#include "NDIMediaOutput.h"
```

### 基本用法
动态发现并连接到一个NDI源。
```cpp
// 获取NDI媒体模块单例
INDIMediaModule* NDIMediaModule = FModuleManager::GetModulePtr<INDIMediaModule>(TEXT("NDIMedia"));

if (NDIMediaModule)
{
    // 枚举网络中所有可用的NDI源
    TArray<FNDIMediaSourceInfo> Sources;
    NDIMediaModule->FindAvailableSources(Sources);
    
    if (Sources.Num() > 0)
    {
        // 创建媒体源实例并连接到第一个发现的源
        UNDIMediaSource* MediaSource = NewObject<UNDIMediaSource>();
        MediaSource->SetSourceName(Sources[0].SourceName);
        
        // 使用MediaPlayer打开源（略去MediaPlayer获取代码）
        MediaPlayer->OpenSource(MediaSource);
    }
}
```
*(此代码逻辑基于模块提供的接口推断)*

### 进阶用法
通过C++创建并配置NDI媒体输出。
```cpp
// 创建一个NDI媒体输出对象
UNDIMediaOutput* NDIOutput = NewObject<UNDIMediaOutput>();
NDIOutput->SetOutputName(TEXT("MyUE5Output"));

// 将引擎的渲染输出附加到此NDI输出（需要先获取有效的UTextureRenderTarget2D）
if (RenderTarget)
{
    UMediaCapture* MediaCapture = UMediaCapture::CreateMediaCapture();
    MediaCapture->CaptureTextureRenderTarget2D(RenderTarget, NDIOutput);
    MediaCapture->StartCapture();
}
```
*(此代码逻辑基于媒体捕获系统与NDI输出的集成推断)*

## Demo 示例

一个最小化的NDI流发送示例。
*(由于此为汇总页，不展示完整Demo代码。详细示例请参考各子模块文档或测试用例)*

## 模块依赖

使用本插件，你的项目或模块通常需要依赖以下系统：

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 媒体IO基础框架，提供媒体源/输出/捕获的核心抽象 |
| `MediaAssets` | 媒体资产模块，处理媒体纹理、播放器等 |
| `MediaUtils` | 媒体工具函数库 |
| `RHICore` | 渲染硬件接口核心，用于高效的渲染目标纹理访问（NDIMediaRendering模块需要） |

*注：NDIMedia插件自身已包含并管理了对第三方NDI SDK (`NDISDK`模块) 的依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复了NDI和ImgMedia播放器报告错误“SourceOpened”分析事件的问题 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为NDI等媒体播放器及捕获系统添加了额外的引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 重新分类了虚拟制片相关资产（可能涉及NDI相关资产的分类调整） |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为媒体源和媒体输出的子类（包括NDI相关的）添加了缺失的资产定义条目 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复了媒体系统中HDR归一化因子的问题，可能影响NDI流的亮度 |

### 维护评价

NDIMedia插件创建于2024年，距今约2年。从近期的Git提交记录（2026年5月）来看，**插件仍在积极维护中**。最近的更新主要集中在：
1.  **功能完善与Bug修复**：修复了分析事件和HDR亮度相关的问题。
2.  **系统集成**：加强了与引擎分析系统、资产系统的集成。
3.  **虚拟制片工作流优化**：作为虚拟制片工具链的一部分进行资产管理的改进。

该插件被标记为**实验性**且**默认未启用**，表明它可能尚未达到完全稳定的状态，或主要面向特定专业工作流。但由于Epic Games仍在持续更新，并且它是实现与专业视频设备互操作的关键插件，对于需要NDI集成的项目，**推荐在了解其实验状态的前提下使用**。它被视为连接UE5与专业视频制作基础设施的重要桥梁。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia)
- [官方文档](https://docs.unrealengine.com/) (请在官方文档站内搜索“NDI Media”获取最新指南)