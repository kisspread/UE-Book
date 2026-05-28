# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | 苹果视频工具箱编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 用途

`VTCodecs` 插件是 UE5 `AVCodecs` 框架的一部分，它为 Apple 平台（macOS, iOS）提供了基于 `VideoToolbox` 硬件加速框架的 H.264、H.265 (HEVC) 和 VP9 视频编解码器实现。该插件的核心价值在于利用 Apple 设备的专用硬件（如 Apple Silicon 的媒体引擎或 Intel 的 Quick Sync Video）进行高效的视频编码和解码，从而显著降低 CPU 负载并提升性能，尤其适用于实时视频流处理、云游戏串流、或需要高性能视频处理的应用。

它解决了在 UE5 的统一视频框架（`AVCodecs`）下，无法直接调用 Apple 平台原生硬件编解码器的问题，并负责处理 VideoToolbox 特有的数据格式（如 AVCC/HVCC）与 RTP 传输标准（如 Annex B）之间的转换。

## 使用场景

- 你正在为 macOS 或 iOS 开发一个需要实时视频编码（如屏幕录制、摄像头捕获后推流）或解码（如播放网络视频流、接收远程视频）的应用。
- 你需要在 Apple 设备上获得最优的视频处理性能，避免使用纯软件编解码器带来的高 CPU 占用。
- 你的项目需要处理来自 RTP 或 WebRTC 流的 H.264/H.265 数据，需要进行格式转换。

## 蓝图用法

`VTCodecs` 主要提供 C++ API，未直接暴露 `BlueprintCallable` 节点。其核心功能通过 `AVCodecs` 框架的接口（如 `FAVDevice`, `FAVInstance`）在运行时使用。开发者通常在 C++ 中创建和管理编码器/解码器实例。

## C++ 用法

### 头文件引入

```cpp
// 检查并初始化 VideoToolbox 能力
#include "VT.h"

// 编码器相关
#include "Video/Encoders/VideoEncoderVT.h"
#include "Video/Encoders/Configs/VideoEncoderConfigVT.h"

// 解码器相关
#include "Video/Decoders/VideoDecoderVT.h"
#include "Video/Decoders/Configs/VideoDecoderConfigVT.h"

// NALU 格式转换工具
#include "Video/Util/NaluRewriter.h"
```

### 基本用法

**1. 初始化与能力检查**
```cpp
// 来自 VT.h
FVT VToolboxAPI;
if (VToolboxAPI.IsValid() && VToolboxAPI.bHasCompatibleGPU)
{
    UE_LOG(LogTemp, Log, TEXT("VideoToolbox is available and has compatible GPU."));
}
```

**2. 创建并配置编码器**
```cpp
// 创建一个输出到 Metal 资源的编码器实例
TSharedPtr<TVideoEncoderVT<FVideoResourceMetal>> Encoder = MakeShared<TVideoEncoderVT<FVideoResourceMetal>>();

// 配置编码参数
FVideoEncoderConfigVT Config;
Config.Width = 1920;
Config.Height = 1080;
Config.FrameRate = 30;
Config.TargetBitrate = 8000000; // 8 Mbps
Config.Codec = kCMVideoCodecType_H264; // 或 kCMVideoCodecType_HEVC
Config.PixelFormat = EVideoFormat::BGRA;

// 转换为编码器内部配置并应用
FVideoEncoderConfigVT InternalConfig;
FAVExtension::TransformConfig(InternalConfig, Config);
Encoder->SetConfig(InternalConfig);
```

**3. 打开编码器并编码一帧**
```cpp
// 假设已拥有有效的 Device 和 Instance
TSharedRef<FAVDevice> Device = ...;
TSharedRef<FAVInstance> Instance = ...;

FAVResult Result = Encoder->Open(Device, Instance);
if (Result.IsNotSuccess()) { /* 处理错误 */ }

// 发送一帧 (Resource 为包含视频数据的 Metal 资源)
TSharedPtr<FVideoResourceMetal> Resource = ...; // 例如从渲染目标创建
uint32 Timestamp = ...; // 帧时间戳
bool bForceKeyframe = true; // 是否强制为关键帧
Result = Encoder->SendFrame(Resource, Timestamp, bForceKeyframe);

// 异步接收编码后的包
FVideoPacket EncodedPacket;
while (Encoder->ReceivePacket(EncodedPacket).IsSuccess())
{
    // 处理编码后的 NALU 数据，EncodedPacket 中的数据通常是 AVCC 格式。
    // 可能需要使用 NaluRewriter 进行格式转换。
}
```

### 进阶用法

**NALU 格式转换（用于网络传输）**
```cpp
// 假设我们有一个从编码器得到的 CMSampleBufferRef (avcc 格式)
CMSampleBufferRef AVCCSampleBuffer = ...;
TArray<uint8> AnnexBBuffer;

// 将 AVCC 转换为 Annex B 格式 (适用于 RTP)
bool bIsKeyframe = true; // 根据实际情况设置
if (NaluRewriter::H264CMSampleBufferToAnnexBBuffer(AVCCSampleBuffer, bIsKeyframe, AnnexBBuffer))
{
    // 现在 AnnexBBuffer 包含了可以放入 RTP 包的数据
    // ... 发送数据
}

// 反向操作：从网络接收 Annex B 数据，准备送给解码器
const uint8* ReceivedAnnexBData = ...;
size_t DataSize = ...;
CMVideoFormatDescriptionRef VideoFormat = NaluRewriter::CreateH264VideoFormatDescription(ReceivedAnnexBData, DataSize);
CMSampleBufferRef SampleBufferForDecoder = nullptr;
CMMemoryPoolRef MemPool = CMMemoryPoolCreate(nullptr);
if (NaluRewriter::H264AnnexBBufferToCMSampleBuffer(ReceivedAnnexBData, DataSize, VideoFormat, &SampleBufferForDecoder, MemPool))
{
    // 将 SampleBufferForDecoder 发送给解码器
    // ... 使用解码器解码
    if(SampleBufferForDecoder) CFRelease(SampleBufferForDecoder);
}
CFRelease(VideoFormat);
CFRelease(MemPool);
```

## Demo 示例

以下是一个最小可运行的编码器设置与数据接收示例。

**VideoToolboxDemo.h**
```cpp
#pragma once
#include "VT.h"
#include "Video/Encoders/VideoEncoderVT.h"
#include "Video/Encoders/Configs/VideoEncoderConfigVT.h"

class FVideoToolboxDemo
{
public:
    void Initialize();
    void EncodeFrame();
    void Shutdown();

private:
    TSharedPtr<TVideoEncoderVT<FVideoResourceMetal>> HardwareEncoder;
    TSharedRef<FAVDevice> Device;
    TSharedRef<FAVInstance> Instance;
    uint32 FrameIndex = 0;
};
```

**VideoToolboxDemo.cpp**
```cpp
#include "VideoToolboxDemo.h"

void FVideoToolboxDemo::Initialize()
{
    // 1. 检查硬件
    FVT VToolbox;
    if (!VToolbox.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("VideoToolbox API is not available."));
        return;
    }

    // 2. 获取设备和实例 (具体实现依赖于你的应用上下文)
    Device = MakeShared<FAVDevice>();
    Instance = MakeShared<FAVInstance>();

    // 3. 创建编码器
    HardwareEncoder = MakeShared<TVideoEncoderVT<FVideoResourceMetal>>();

    // 4. 配置
    FVideoEncoderConfigVT Config;
    Config.Width = 1280;
    Config.Height = 720;
    Config.Codec = kCMVideoCodecType_H264;
    Config.TargetBitrate = 5000000; // 5 Mbps
    Config.FrameRate = 30;

    HardwareEncoder->SetConfig(Config);

    // 5. 打开编码会话
    FAVResult Result = HardwareEncoder->Open(Device, Instance);
    if (Result.IsNotSuccess())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open encoder: %s"), *Result.GetErrorMessage());
        HardwareEncoder.Reset();
    }
}

void FVideoToolboxDemo::EncodeFrame()
{
    if (!HardwareEncoder || !HardwareEncoder->IsOpen())
    {
        return;
    }

    // 6. 模拟创建一个视频资源 (实际应从渲染管线获取)
    TSharedPtr<FVideoResourceMetal> Resource = ...;

    // 7. 发送帧进行编码
    FAVResult Result = HardwareEncoder->SendFrame(Resource, FrameIndex++, false);
    if (Result.IsNotSuccess())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to send frame: %s"), *Result.GetErrorMessage());
    }

    // 8. 轮询接收编码完成的包
    FVideoPacket Packet;
    while (HardwareEncoder->ReceivePacket(Packet).IsSuccess())
    {
        // 9. 处理编码后的数据 (Packet.Data 是 AVCC 格式的 NALU)
        // 可以在此处使用 NaluRewriter 转换格式，或直接写入文件/发送网络。
        UE_LOG(LogTemp, Log, TEXT("Received encoded packet, size: %d bytes"), Packet.Data.Num());
    }
}

void FVideoToolboxDemo::Shutdown()
{
    // 10. 安全关闭并释放资源
    if (HardwareEncoder)
    {
        HardwareEncoder->Close();
        HardwareEncoder.Reset();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AVCodecs` | 提供统一的音视频编解码框架和接口（`FAVDevice`, `FAVInstance`, `TVideoEncoder` 等） |
| `MetalRHI` / `MetalShaderFormat` | VTCodecsRHI 模块依赖，用于支持 Metal 纹理资源 |
| `VideoToolbox` (系统框架) | Apple 提供的硬件视频编解码核心框架 |
| `CoreMedia` (系统框架) | 处理媒体数据类型（如 `CMSampleBufferRef`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举可能导致的输出错误 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了上次错误的查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了 CL51314860 的改动 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修改了引擎初始化委托的获取方式以修复注册缺失问题 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复了使用可移植工具链时的更多编译错误 |

### 维护评价

`VTCodecs` 是一个相对较新（创建于 2023 年底）但更新活跃的实验性插件。从 git 历史看，最近的提交集中在 2026 年初至年中，主要以**编译错误修复、代码回滚和平台兼容性调整**为主，表明该插件仍在积极维护中以适应 UE5 主分支的持续变化。然而，其作为 `Experimental` 版本且默认禁用 (`EnabledByDefault: false`) 的状态，意味着 Epic 可能不保证其 API 的长期稳定性，且可能存在未发现的缺陷。

**推荐使用建议**：
- ✅ **适合**：在 macOS/iOS 平台上，对视频编解码性能有明确要求，且愿意承担实验性 API 可能变动风险的开发项目。
- ⚠️ **注意**：在使用前务必在目标设备上进行充分测试。建议将其作为特定平台的优化选项，而非项目的唯一编解码方案。由于是实验性插件，关注其随 UE 版本更新的变动日志至关重要。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [官方文档](https://developer.apple.com/documentation/videotoolbox) (Apple VideoToolbox 框架文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs/Tests) (如果存在)