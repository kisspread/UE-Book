# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | AMD编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AMFCodecs` (Runtime), `AMFCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途

本插件将 **AMD Advanced Media Framework (AMF)** 的硬件编解码能力集成到 Unreal Engine 5 的 `AVCodecs` 框架中。其核心目的是为使用 AMD 显卡的开发者提供一个标准化的接口，以利用 GPU 硬件加速进行高性能的视频编码（例如 H.264， H.265/HEVC）和解码。它解决了在 UE 中直接调用特定厂商硬件加速编解码器 API 复杂且平台相关的问题，将其封装为引擎内统一的音视频处理管线的一部分。

## 使用场景

*   你的项目需要进行**高质量、低延迟的视频录制或推流**，并且目标用户的硬件以 AMD 显卡为主，希望利用其硬件编码器以降低 CPU 负载。
*   你正在开发视频处理相关的工具或功能，需要在运行时对视频流进行**硬件加速的编码或解码**。
*   你正在构建一个基于 `AVCodecs` 框架的跨平台媒体处理系统，并需要为 AMD 平台提供特定的高性能实现。

## 蓝图用法

根据提供的源码文件分析，该插件主要为 C++ 层提供底层编解码器实现。它作为 `AVCodecs` 框架的后端，其核心功能通常由更上层的媒体框架（如 `MediaPlayer`、`MovieSceneCapture` 或自定义的 `AVContext`）在内部调用。**当前版本未发现提供额外的、可直接在蓝图中调用的公开函数或属性**。开发者主要通过配置和使用标准的 UE 媒体播放或捕获系统来间接受益于该插件提供的硬件加速能力。

## C++ 用法

### 头文件引入

该插件提供了两个模块。要使用 AMF 的编解码器，主要引入 `AMFCodecs` 模块的头文件。

```cpp
#include "AMFCodecs/AMFCodec.h"
// 或根据具体的编码器/解码器类型引入
#include "AMFCodecs/AMFH264Encoder.h"
```

### 基本用法

该插件的设计是作为 `AVCodecs` 框架的组成部分，通常不会被直接实例化和调用，而是由引擎的媒体子系统在后台使用。一个更可能的使用模式是通过 `FVideoEncoder` 或 `FVideoDecoder` 的工厂接口来请求一个特定格式（如 H.264）的编解码器实例，引擎会根据平台和硬件能力自动选择使用 AMF 还是其他后端。

### 进阶用法

对于深度定制，开发者可能需要直接与 AMF 的上下文和表面对象交互。这通常涉及：
1.  获取或创建一个 `IAMFEncoder` 或 `IAMFDecoder` 接口。
2.  配置编码/解码参数（如分辨率、比特率、帧率、Profile/Level）。
3.  将 `FMediaTextureSample` 或 `FVideoBuffer` 提交给编码器，或从解码器中获取解码后的帧数据。
4.  处理异步操作和回调。

## Demo 示例

以下是一个概念性的示例，展示如何在 C++ 中可能通过 `AVCodecs` 框架请求一个使用 AMF 后端的 H.264 编码器。

**MyAMFEncoderUser.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FAMFEncoderWrapper;

class FMyAMFEncoderUser
{
public:
    void InitializeEncoder(int32 Width, int32 Height, int32 Bitrate);
    void EncodeFrame(const void* FrameData, int32 FrameSize);
    void Shutdown();

private:
    TUniquePtr<FAMFEncoderWrapper> Encoder;
};
```

**MyAMFEncoderUser.cpp**
```cpp
#include "MyAMFEncoderUser.h"
#include "Video/VideoEncoder.h" // 假设的AVCodecs视频编码器接口
#include "HAL/PlatformMisc.h"

// 注意：以下代码为基于框架设计的推断示例，具体API需参照UE5 AVCodecs最新文档。
void FMyAMFEncoderUser::InitializeEncoder(int32 Width, int32 Height, int32 Bitrate)
{
    // 通过AVCodecs框架请求一个H.264编码器实例，引擎可能会自动选择AMF后端（如果硬件支持）
    // FVideoEncoderInfo EncoderInfo;
    // EncoderInfo.Codec = EVideoCodec::H264;
    // EncoderInfo.Width = Width;
    // EncoderInfo.Height = Height;
    // EncoderInfo.Bitrate = Bitrate;
    //
    // // 获取编码器工厂并创建实例
    // IVideoEncoderFactory* EncoderFactory = GetVideoEncoderFactory();
    // if (EncoderFactory)
    // {
    //     Encoder = EncoderFactory->CreateEncoder(EncoderInfo);
    // }
}

void FMyAMFEncoderUser::EncodeFrame(const void* FrameData, int32 FrameSize)
{
    if (Encoder)
    {
        // 创建帧数据描述
        // FVideoFrame InputFrame;
        // InputFrame.Data = FrameData;
        // InputFrame.Size = FrameSize;
        //
        // // 提交编码
        // Encoder->Encode(InputFrame);
    }
}

void FMyAMFEncoderUser::Shutdown()
{
    Encoder.Reset();
}
```

## 模块依赖

该插件本身依赖关系相对简单，主要与图形和硬件抽象层相关。

| 模块 | 用途 |
|---|---|
| `Vulkan` | 提供底层图形和计算API，用于与AMD GPU的AMF硬件编解码器进行交互。 |
| `AVCodecs` | 提供上层音视频编解码框架接口，本插件作为其硬件后端之一。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举可能导致的输出错误 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复前次错误的查找替换后的第二次提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了编号为51314860的改动 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化委托改为函数调用形式以修复注册问题 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新过时的构建版本设置 |

### 维护评价

*   **状态**: **实验性但活跃维护中**。
*   **分析**: 插件创建于2023年，年龄尚浅。最近一次更新在2026年4月，修复了代码层面的问题，并且在过去三个月内有多次提交，表明仍在积极维护和适配引擎更新。其 `IsExperimentalVersion` 标志和 `EnabledByDefault=false` 的设置明确了其实验性质。
*   **推荐**: **谨慎推荐用于实验和原型开发**。由于是实验性插件，API 和功能可能会发生变化，不建议直接用于最终发行版的生产环境。对于需要 AMD 硬件编码支持的项目，它是当前 UE5 内置的官方集成方案，值得关注和测试，但需准备好应对潜在的变动或限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- [官方文档](https://gpuopen.com/amf/) （AMD AMF SDK 官方站点，非UE文档）