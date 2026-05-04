# AVCodecs Core

> Core Plugin for various Audio/Video codecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AVCodecsCore` (Runtime), `AVCodecsCoreRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore) | |

## 用途

AVCodecs Core 是一个底层的音视频编解码框架插件，旨在为 Unreal Engine 提供统一、可扩展的音视频编解码抽象层。它解决的核心问题是：为不同平台（CPU、GPU）和不同编解码器（H.264、H.265、VP8、VP9、AV1）提供一套标准化的接口和资源管理机制。

该插件本身不包含具体的编解码器实现（如 NVENC、VAAPI），而是定义了编解码器、资源、设备上下文等基础抽象。具体编解码器的实现（如 `AVCodecsH264`、`AVCodecsNVENC`）作为独立插件存在，依赖于此核心框架。这使得上层应用（如 Pixel Streaming、媒体播放器）可以通过统一的 API 进行音视频处理，而无需关心底层硬件和编解码器的差异。

## 使用场景

- **实时音视频通信**：需要将游戏画面和音频编码为 H.264/VP9 等格式进行网络传输。
- **视频编辑与后期**：需要解码特定格式的视频文件进行处理或合成。
- **游戏内视频播放**：需要解码并播放预渲染的过场动画或用户生成内容。
- **跨平台媒体处理**：需要一套代码同时在 Windows (D3D11/D3D12)、Linux (Vulkan) 和 macOS (Metal) 上运行音视频编解码任务。
- **可伸缩视频编码 (SVC)**：需要为视频会议或自适应流媒体生成具有空间/时间可伸缩性的视频流。

## 蓝图用法

该插件主要面向 C++ 开发者，提供的蓝图暴露 API 非常有限，主要是一些配置相关的枚举和结构体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EVideoCodec` | 枚举，定义支持的视频编解码器类型（H264, H265, VP8, VP9, AV1）。 | `UENUM` |
| `EAVPreset` | 枚举，定义编码质量预设（UltraLowQuality 到 Lossless）。 | `UENUM` |
| `EAVLatencyMode` | 枚举，定义延迟模式（UltraLowLatency 到 Default）。 | `UENUM` |

### 使用示例（蓝图描述）

在蓝图中，你主要会使用这些枚举来配置编解码器参数。例如，在一个“创建视频编码器”的蓝图函数中，你可能会将一个 `EVideoCodec` 枚举变量连接到编码器配置的 `Codec` 输入引脚上。这些枚举通常作为其他蓝图函数（可能来自上层插件如 Pixel Streaming）的输入参数。

## C++ 用法

### 头文件引入

```cpp
// 核心框架
#include "AVDevice.h"
#include "AVInstance.h"
#include "AVResource.h"
#include "AVPacket.h"

// 视频相关
#include "Video/VideoEncoder.h"
#include "Video/VideoDecoder.h"
#include "Video/VideoResource.h"
#include "Video/VideoConfig.h"

// 音频相关
#include "Audio/AudioEncoder.h"
#include "Audio/AudioDecoder.h"
#include "Audio/AudioResource.h"

// 具体编解码器配置（示例）
#include "Video/Encoders/Configs/VideoEncoderConfigH264.h"
#include "Video/Decoders/Configs/VideoDecoderConfigH264.h"
```

### 基本用法

以下示例展示了如何使用核心框架创建设备、实例和资源。来源文件：`Engine/Plugins/Experimental/AVCodecs/AVCodecsCore/Source/AVCodecsCore/Public/AVDevice.h`, `AVInstance.h`, `Video/Resources/VideoResourceCPU.h`。

```cpp
// 1. 获取或创建设备（硬件或软件）
TSharedRef<FAVDevice> HardwareDevice = FAVDevice::GetHardwareDevice(0);
TSharedRef<FAVDevice> SoftwareDevice = FAVDevice::GetSoftwareDevice();

// 2. 创建一个编解码器实例
TSharedRef<FAVInstance> EncoderInstance = MakeShared<FAVInstance>();

// 3. 创建一个 CPU 视频资源（例如，用于存储原始帧数据）
TSharedRef<FAVDevice> Device = FAVDevice::GetSoftwareDevice();
TSharedPtr<uint8> RawFrameData = MakeShared<uint8>(/* 分配内存 */);
FAVLayout Layout(Width * BytesPerPixel, 0, Width * Height * BytesPerPixel); // Stride, Offset, Size
FVideoDescriptor Descriptor(Width, Height, EVideoFormat::BGRA); // 假设格式

TSharedRef<FVideoResourceCPU> CPUResource = MakeShared<FVideoResourceCPU>(Device, RawFrameData, Layout, Descriptor);

// 4. 验证资源
FAVResult ValidationResult = CPUResource->Validate();
if (!ValidationResult)
{
    UE_LOG(LogTemp, Error, TEXT("Resource validation failed: %s"), *ValidationResult.GetMessage());
}
```

### 进阶用法

以下示例展示了如何配置并使用一个 H.264 编码器。这通常需要结合具体的编码器实现插件（如 `AVCodecsH264`）。来源文件：`Engine/Plugins/Experimental/AVCodecs/AVCodecsCore/Source/AVCodecsCore/Public/Video/VideoEncoder.h`, `Video/Encoders/Configs/VideoEncoderConfigH264.h`。

```cpp
// 假设我们有一个具体的 H.264 编码器类 FH264VideoEncoder，它继承自 TVideoEncoder<FVideoResourceCPU>
// 1. 创建编码器实例
TSharedPtr<TVideoEncoder<FVideoResourceCPU>> H264Encoder = MakeShared<FH264VideoEncoder>();

// 2. 打开编码器并关联设备和实例
TSharedRef<FAVDevice> Device = FAVDevice::GetHardwareDevice(0);
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();
FAVResult OpenResult = H264Encoder->Open(Device, Instance);
if (!OpenResult) { /* 处理错误 */ }

// 3. 配置编码器
FVideoEncoderConfigH264 EncoderConfig;
EncoderConfig.Preset = EAVPreset::HighQuality;
EncoderConfig.Profile = EH264Profile::Main;
EncoderConfig.Width = 1920;
EncoderConfig.Height = 1080;
EncoderConfig.MaxFramerate = 60;
EncoderConfig.TargetBitrate = 8000000; // 8 Mbps

H264Encoder->SetConfig(EncoderConfig);
FAVResult ApplyResult = H264Encoder->ApplyConfig();
if (!ApplyResult) { /* 处理错误 */ }

// 4. 编码一帧
// 假设 FrameResource 是一个有效的 FVideoResourceCPU
TSharedRef<FVideoResourceCPU> FrameResource = /* ... */;
FAVResult EncodeResult = H264Encoder->Encode(FrameResource);
if (EncodeResult)
{
    // 5. 获取编码后的数据包
    FVideoPacket EncodedPacket;
    if (H264Encoder->ReceivePacket(EncodedPacket))
    {
        // 使用 EncodedPacket.DataPtr 和 EncodedPacket.DataSize
        // EncodedPacket 包含 QP、是否关键帧等信息
    }
}

// 6. 关闭编码器
H264Encoder->Close();
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何使用 CPU 资源进行视频编码（概念性，需配合具体编码器插件）。

**MyAVCodecDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AVDevice.h"
#include "AVInstance.h"
#include "Video/VideoEncoder.h"
#include "Video/Resources/VideoResourceCPU.h"

class FMyAVCodecDemo
{
public:
    void Initialize();
    void EncodeFrame(const TArray<uint8>& RawBGRAData, int32 Width, int32 Height);
    void Shutdown();

private:
    TSharedPtr<FAVDevice> Device;
    TSharedPtr<FAVInstance> EncoderInstance;
    // 假设使用一个具体的编码器，这里用基类指针示意
    TSharedPtr<TVideoEncoder<FVideoResourceCPU>> VideoEncoder;
};
```

**MyAVCodecDemo.cpp**
```cpp
#include "MyAVCodecDemo.h"
// 引入具体的编码器头文件，例如：
// #include "H264VideoEncoder.h"

void FMyAVCodecDemo::Initialize()
{
    // 1. 获取软件设备（CPU）
    Device = FAVDevice::GetSoftwareDevice();
    
    // 2. 创建编码器实例
    EncoderInstance = MakeShared<FAVInstance>();
    
    // 3. 创建具体的编码器（示例，实际需替换为真实类）
    // VideoEncoder = MakeShared<FH264VideoEncoder>();
    
    // 4. 打开编码器
    if (VideoEncoder.IsValid())
    {
        FAVResult Result = VideoEncoder->Open(Device.ToSharedRef(), EncoderInstance.ToSharedRef());
        if (!Result)
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open encoder: %s"), *Result.GetMessage());
            return;
        }
        
        // 5. 配置编码器
        FVideoEncoderConfig Config;
        Config.Width = 1920;
        Config.Height = 1080;
        Config.MaxFramerate = 30;
        Config.TargetBitrate = 4000000; // 4 Mbps
        VideoEncoder->SetConfig(Config);
        VideoEncoder->ApplyConfig();
    }
}

void FMyAVCodecDemo::EncodeFrame(const TArray<uint8>& RawBGRAData, int32 Width, int32 Height)
{
    if (!VideoEncoder.IsValid() || !VideoEncoder->IsOpen())
    {
        return;
    }
    
    // 1. 创建 CPU 资源包装原始数据
    TSharedPtr<uint8> DataPtr = MakeShared<uint8>(RawBGRAData.GetData());
    FAVLayout Layout(Width * 4, 0, RawBGRAData.Num()); // Stride = Width * 4 bytes (BGRA)
    FVideoDescriptor Descriptor(Width, Height, EVideoFormat::BGRA);
    
    TSharedRef<FVideoResourceCPU> FrameResource = MakeShared<FVideoResourceCPU>(
        Device.ToSharedRef(), DataPtr, Layout, Descriptor);
    
    // 2. 编码
    FAVResult Result = VideoEncoder->Encode(FrameResource);
    if (Result)
    {
        // 3. 获取编码后的包
        FVideoPacket Packet;
        if (VideoEncoder->ReceivePacket(Packet))
        {
            // 处理编码后的数据包，例如发送到网络或写入文件
            UE_LOG(LogTemp, Log, TEXT("Encoded packet: Size=%llu, Keyframe=%d, QP=%u"),
                Packet.DataSize, Packet.bIsKeyframe, Packet.QP);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Encode failed: %s"), *Result.GetMessage());
    }
}

void FMyAVCodecDemo::Shutdown()
{
    if (VideoEncoder.IsValid())
    {
        VideoEncoder->Close();
        VideoEncoder.Reset();
    }
    EncoderInstance.Reset();
    Device.Reset();
}
```

## 模块依赖

从 `AVCodecsCore.Build.cs` 和 `AVCodecsCoreRHI.Build.cs` 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `CUDA` | NVIDIA CUDA 支持，用于 GPU 加速编解码。 |
| `VulkanRHI` | Vulkan 图形 API 支持，用于跨平台 GPU 资源管理。 |
| `D3D11RHI` | Direct3D 11 支持，用于 Windows 平台 GPU 资源。 |
| `D3D12RHI` | Direct3D 12 支持，用于 Windows 平台 GPU 资源。 |
| `MetalRHI` | Metal 图形 API 支持，用于 macOS/iOS 平台 GPU 资源。 |
| `MediaUtils` | 媒体工具函数，可能用于时间戳、格式转换等。 |
| `PixelStreaming2` | 与 Pixel Streaming 2 插件集成，用于实时流媒体场景。 |

## 维护状态

### 近期更新

```
- d7a4d1607bdc [AVCodecs, PixelStreaming2] Fixes: - Fix: Crash when calling PushAudio - Fix: Stream state set to connecting when no url is set - Fix: Input handler not unregistering - Fix: Crash when getting window title during a MRQ render - Fix: Crash when PropertyChangedEvent.Property is nullptr - Fix: Downgrade warning to log for build health
- 20ee5e0e8b39 The source files included were modified by the UnrealCodeFixup tool so that they can pass the -mergemodules compilation. *This CL must be submitted before integrating PixelStreaming2 into RemoteSession plugin.
- 796c0dd834b8 [AVCodecs] Fix PVS warning about shifting with a negative number.
```

### 维护评价

- **创建时间**：2023年1月，相对较新。
- **最近更新**：最近的提交（2024年）主要是针对 Pixel Streaming 2 集成的错误修复和代码工具调整，没有新的核心功能添加。
- **活跃度**：作为实验性插件，其开发与 Pixel Streaming 2 等上层应用紧密相关。核心框架本身可能已趋于稳定，但仍在根据上层需求进行维护和修复。
- **已知限制**：标记为实验性 (`IsExperimentalVersion=true`)，且默认未启用 (`EnabledByDefault=false`)。API 可能发生变化，不建议在生产环境中直接依赖。
- **推荐使用**：如果你正在开发需要深度定制音视频编解码管线的功能（如自定义 Pixel Streaming 编码器、媒体处理工具），并且愿意承担实验性 API 变化的风险，可以研究和使用。对于常规的媒体播放或简单的流媒体需求，建议使用 UE 内置的更高级别的媒体框架。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Performance/AVCodecs)