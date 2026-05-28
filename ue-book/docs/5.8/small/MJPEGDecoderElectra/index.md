# MotionJPEG Decoder for Electra

> Implements video playback of MotionJPEG encoded video files

| 属性 | 值 |
|---|---|
| 中文名 | MJPEG解码器插件 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MJPEGDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MJPEGDecoderElectra) | |

## 用途

该插件为UE5的 **Electra 媒体播放器**提供 **MotionJPEG (MJPEG)** 视频格式的解码支持。MJPEG是一种将视频的每一帧独立压缩为JPEG图像的编码格式，常用于监控摄像头、医疗设备和某些网络视频流。此插件的存在弥补了UE5内置Electra播放器默认不支持MJPEG格式的空缺，允许开发者在应用程序中播放来自特定设备或源的MJPEG视频。

## 使用场景

- 你的应用程序需要接入并实时显示来自IP摄像头的监控视频流。
- 你需要播放预先录制的MJPEG格式视频文件，用于回放或教学演示。
- 你在开发媒体相关的应用，需要测试或支持基于MotionJPEG编码的媒体源。

## 蓝图用法

此插件主要作为Electra媒体框架的解码器模块运行，其核心逻辑在内部注册并被Electra播放器调用，**未直接暴露任何可在蓝图中调用的节点**。用户通过常规的Electra媒体播放API（如`OpenUrl`， `Media Source`资产）加载MJPEG格式的媒体文件或流，解码过程将由本插件自动完成。

## C++ 用法

本插件的核心是向Electra解码器系统注册一个MJPEG解码器工厂。对于大多数使用者，它作为Electra播放器的底层依赖透明工作。若需要进行底层集成或调试，可以参考以下用法。

### 头文件引入

```cpp
// 主要使用模块的注册/注销功能
#include "MJPEGDecoderElectraModule.h"
```

### 基本用法

插件的启动与关闭会自动处理MJPEG解码器的注册与注销。手动操作通常不需要，但在特定场景下可以显示调用。

```cpp
// 在模块启动时（通常自动完成）
#include "MJPEGDecoder/ElectraMediaMJPEGDecoder.h"

// 注册MJPEG解码器到Electra解码器系统
FElectraMediaMJPEGDecoder::Startup();

// 在模块关闭时（通常自动完成）
FElectraMediaMJPEGDecoder::Shutdown();
```
*来源: `Source/MJPEGDecoderElectra/Private/MJPEGDecoder/ElectraMediaMJPEGDecoder.h`*

### 进阶用法

作为Electra媒体播放器的底层组件，其API相对简单。更复杂的使用涉及通过Electra播放器API加载媒体源。插件的依赖 `ElectraCodecs` 提供了更广泛的编解码器管理接口。

## Demo 示例

本示例演示如何将此解码器插件集成到一个自定义模块中，并确保其生命周期管理正确。

```cpp
// MyGameMediaModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameMediaModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyGameMediaModule.cpp
#include "MyGameMediaModule.h"
#include "MJPEGDecoder/ElectraMediaMJPEGDecoder.h"

#define LOCTEXT_NAMESPACE "FMyGameMediaModule"

void FMyGameMediaModule::StartupModule()
{
    // 启动时注册MJPEG解码器
    FElectraMediaMJPEGDecoder::Startup();
    UE_LOG(LogTemp, Log, TEXT("MJPEG Decoder for Electra has been registered."));
}

void FMyGameMediaModule::ShutdownModule()
{
    // 关闭时注销MJPEG解码器
    FElectraMediaMJPEGDecoder::Shutdown();
    UE_LOG(LogTemp, Log, TEXT("MJPEG Decoder for Electra has been unregistered."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGameMediaModule, MyGameMedia)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供Electra解码器框架和编解码器管理接口，是本插件功能的基石。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化了解码器工厂接口，提升与其他客户端的兼容性。 |
| 2025-11-27 | `001a0b88` | ElectraCodecs: change mjpeg decoder to use ImageUtils instead of ImageWrapper. | 将MJPEG解码器的图像处理依赖从ImageWrapper改为ImageUtils。 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 为解码器实现添加了信息标识，便于调试和识别。 |
| 2025-08-07 | `a902b75` | ElectraDecoders: Added an MJPEG decoder for Electra | 初始提交，为Electra添加了MJPEG解码器支持。 |

### 维护评价

- **活跃维护**: 该插件创建于2025年8月，近一年内有多次实质性功能更新和维护，包括接口现代化和依赖优化，表明仍在活跃维护中。
- **实验性/状态**: `.uplugin`中 `EnabledByDefault=false` 且 `IsBetaVersion=false`，表明它是一个稳定但非默认启用的功能插件。
- **推荐使用**: 如果你的项目需要播放MJPEG视频并使用Electra媒体播放器，**推荐使用**此插件。它由Epic Games官方提供和维护，能够与UE5的媒体系统无缝集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MJPEGDecoderElectra)
- [官方文档](https://docs.unrealengine.com) (通用媒体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MJPEGDecoderElectra/Tests)