# AVCodecs Core

> Core Plugin for various Audio/Video codecs

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

AVCodecsCore 是一个用于音频和视频编解码的**核心框架插件**。它并非一个具体的编解码器实现，而是提供了一套统一的、可扩展的抽象层和接口，用于在 Unreal Engine 中集成和管理各种音视频编解码器（Codec）。

该插件解决的核心问题是：为 UE 提供一个标准化的、跨平台的音视频编解码基础设施。它定义了编解码器、资源、设备和实例等核心概念，并通过 RHI（渲染硬件接口）集成层，使得编解码操作能够与 UE 的渲染管线（如 D3D11, D3D12, Vulkan, Metal）高效协同，支持硬件加速。开发者可以基于此框架，为特定平台或需求实现具体的编解码器（如 H.264, H.265, AAC 等）。

## 使用场景

-   你需要在项目中集成**实时视频流处理**（如接收和解码来自网络或摄像头的 H.264/H.265 流）。
-   你需要实现**屏幕录制或游戏画面捕获**功能，并希望使用硬件加速编码（如 NVENC, AMF, VideoToolbox）。
-   你正在开发**视频会议、直播或远程协作**功能，需要处理音视频的编解码。
-   你需要一个**统一的接口**来管理不同平台（Windows, Linux, Mac）的硬件编解码器，避免为每个平台编写重复的胶水代码。
-   你希望构建自定义的媒体管线，需要精细控制编解码过程、资源管理和异步处理。

## 蓝图用法

该插件提供了 `Simple` 系列的蓝图友好类，封装了底层的 C++ 模板类，便于在蓝图中快速使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 以指定的编解码器和配置打开一个视频/音频解码器或编码器。可选择同步或异步模式。 | `USimpleVideoDecoder`, `USimpleVideoEncoder`, `USimpleAudioEncoder` |
| `Close` | 关闭当前打开的解码器或编码器，释放资源。 | `USimpleVideoDecoder`, `USimpleVideoEncoder`, `USimpleAudioEncoder` |
| `IsOpen` | 检查解码器或编码器是否已成功打开。 | `USimpleVideoDecoder`, `USimpleVideoEncoder`, `USimpleAudioEncoder` |
| `IsAsync` | 检查解码器或编码器是否工作在异步模式。 | `USimpleVideoDecoder`, `USimpleVideoEncoder`, `USimpleAudioEncoder` |
| `SendPacket` | 向视频解码器发送一个待解码的数据包（`FSimpleVideoPacket`）。 | `USimpleVideoDecoder` |
| `ReceiveFrame` | 从视频解码器接收一帧解码后的图像，并输出到指定的 `UTextureRenderTarget2D`。 | `USimpleVideoDecoder` |
| `SendFrame` | 向视频编码器发送一帧原始图像（来自 `UTextureRenderTarget2D`）进行编码。 | `USimpleVideoEncoder` |
| `ReceivePacket` | 从视频编码器接收一个编码后的数据包（`FSimpleVideoPacket`）。 | `USimpleVideoEncoder` |
| `SendFrameFloat` | 向音频编码器发送一帧 PCM 浮点音频数据进行编码。 | `USimpleAudioEncoder` |
| `ReceivePacket` | 从音频编码器接收一个编码后的数据包（`FSimpleAudioPacket`）。 | `USimpleAudioEncoder` |
| `ShareRenderTarget2D` | 将一个 `UTextureRenderTarget2D` 的底层 RHI 纹理共享给视频编码管线。 | `USimpleVideoHelper` |

### 使用示例（蓝图描述）

1.  **视频解码流程**：
    *   创建一个 `USimpleVideoDecoder` 对象。
    *   调用 `Open` 节点，选择 `ESimpleVideoCodec::H264`，并设置 `bAsynchronous` 为 `true` 以启用异步解码。
    *   在循环中，将网络或文件读取的压缩数据封装为 `FSimpleVideoPacket`，调用 `SendPacket` 发送给解码器。
    *   调用 `ReceiveFrame` 节点，将一个预先创建好的 `UTextureRenderTarget2D` 资产作为参数传入，解码后的画面将渲染到此 RenderTarget 上。
    *   最后，调用 `Close` 节点释放资源。

2.  **视频编码流程**：
    *   创建一个 `USimpleVideoEncoder` 对象。
    *   配置 `FSimpleVideoEncoderConfig` 结构体（设置宽、高、帧率、码率等）。
    *   调用 `Open` 节点，选择编解码器（如 `ESimpleVideoCodec::H264`）和配置。
    *   调用 `ShareRenderTarget2D` 节点，将你希望编码的 `UTextureRenderTarget2D` 共享给编码器。
    *   在需要编码的时刻（如每帧），调用 `SendFrame` 节点，传入该 RenderTarget 和时间戳。
    *   调用 `ReceivePacket` 节点获取编码后的 `FSimpleVideoPacket`，用于网络发送或文件写入。
    *   最后，调用 `Close` 节点。

## C++ 用法

### 头文件引入

```cpp
// 视频解码
#include "Video/Decoders/SimpleVideoDecoder.h"
// 视频编码
#include "Video/Encoders/SimpleVideoEncoder.h"
// 音频编码
#include "Audio/Encoders/SimpleAudioEncoder.h"
// 视频资源与辅助函数
#include "Video/SimpleVideo.h"
```

### 基本用法

以下示例展示了如何使用 `USimpleVideoDecoder` 同步解码一帧视频。

```cpp
// 假设你已经有一个包含 H264 压缩数据的 FSimpleVideoPacket `InputPacket`
// 和一个用于输出的 UTextureRenderTarget2D* `OutputRenderTarget`

// 1. 创建解码器实例
USimpleVideoDecoder* VideoDecoder = NewObject<USimpleVideoDecoder>();

// 2. 打开解码器（同步模式）
bool bSuccess = VideoDecoder->Open(ESimpleVideoCodec::H264, false); // false 表示同步
if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open video decoder."));
    return;
}

// 3. 发送数据包并接收解码帧
bSuccess = VideoDecoder->SendPacket(InputPacket);
if (bSuccess)
{
    bSuccess = VideoDecoder->ReceiveFrame(OutputRenderTarget);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Frame decoded successfully to RenderTarget."));
    }
}

// 4. 关闭解码器
VideoDecoder->Close();
```

### 进阶用法

以下示例展示了如何使用 `USimpleVideoEncoder` 进行异步编码，并处理资源转换。

```cpp
#include "Video/Resources/VideoResourceRHI.h"
#include "AVExtension.h"

// 假设你有一个 FTextureRHIRef `SourceTexture` (例如来自一个 FRenderTarget)
// 和一个配置好的 FSimpleVideoEncoderConfig `EncoderConfig`

// 1. 创建编码器并配置为异步
USimpleVideoEncoder* VideoEncoder = NewObject<USimpleVideoEncoder>();
bool bSuccess = VideoEncoder->Open(ESimpleVideoCodec::H264, EncoderConfig, true); // true 表示异步
if (!bSuccess) return;

// 2. 将 RHI 纹理转换为编码器所需的 FVideoResourceRHI
// 这通常由 SimpleVideoEncoder 内部处理，但理解其原理很重要
TSharedPtr<FVideoResourceRHI> VideoResource = FVideoResourceRHI::Create(
    GMaxRHIShaderPlatform, // 需要 FAVDevice，此处简化
    FVideoDescriptor(SourceTexture->GetSizeX(), SourceTexture->GetSizeY(), SourceTexture->GetFormat())
);
if (VideoResource.IsValid())
{
    // 从源纹理拷贝数据到编码器资源
    VideoResource->CopyFrom(SourceTexture);
}

// 3. 发送资源进行编码
// 注意：在实际异步编码中，你可能需要管理一个资源池和队列
bSuccess = VideoEncoder->SendFrame(VideoResource, 0.0); // 0.0 是时间戳
if (bSuccess)
{
    // 4. 尝试接收编码后的数据包
    FSimpleVideoPacket OutputPacket;
    bSuccess = VideoEncoder->ReceivePacket(OutputPacket);
    if (bSuccess)
    {
        // 处理编码后的数据包 OutputPacket.RawPacket
    }
}

// 5. 关闭编码器
VideoEncoder->Close();
```

## Demo 示例

一个最小的视频解码示例，演示了从创建解码器到输出一帧的基本流程。

**VideoDecodeDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Video/Decoders/SimpleVideoDecoder.h"
#include "Video/SimpleVideo.h"
#include "VideoDecodeDemo.generated.h"

UCLASS()
class AVideoDecodeDemo : public AActor
{
    GENERATED_BODY()

public:
    AVideoDecodeDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Demo")
    UTextureRenderTarget2D* OutputTarget;

private:
    UPROPERTY()
    USimpleVideoDecoder* Decoder;

    // 模拟一个包含 H264 数据的包
    FSimpleVideoPacket CreateDummyH264Packet();
};
```

**VideoDecodeDemo.cpp**
```cpp
#include "VideoDecodeDemo.h"
#include "Engine/TextureRenderTarget2D.h"

AVideoDecodeDemo::AVideoDecodeDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AVideoDecodeDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!OutputTarget)
    {
        UE_LOG(LogTemp, Warning, TEXT("OutputTarget is not set."));
        return;
    }

    // 创建解码器
    Decoder = NewObject<USimpleVideoDecoder>();

    // 打开解码器 (同步模式)
    if (Decoder->Open(ESimpleVideoCodec::H264, false))
    {
        UE_LOG(LogTemp, Log, TEXT("Video decoder opened successfully."));

        // 创建并发送一个模拟的数据包
        FSimpleVideoPacket Packet = CreateDummyH264Packet();
        if (Decoder->SendPacket(Packet))
        {
            // 接收解码帧到 RenderTarget
            if (Decoder->ReceiveFrame(OutputTarget))
            {
                UE_LOG(LogTemp, Log, TEXT("Dummy frame decoded to RenderTarget."));
            }
        }

        // 关闭解码器
        Decoder->Close();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open video decoder."));
    }
}

FSimpleVideoPacket AVideoDecodeDemo::CreateDummyH264Packet()
{
    // 注意：这是一个极简的、无效的 H264 包，仅用于演示流程。
    // 真实的 H264 流需要正确的 NAL 单元结构。
    FSimpleVideoPacket Packet;
    Packet.RawPacket.Data.AddUninitialized(100); // 填充 100 字节的假数据
    // ... 在真实场景中，这里会填充从网络或文件读取的 H264 数据
    return Packet;
}
```

## 模块依赖

该插件依赖于 UE 的核心渲染和媒体模块，以实现与 RHI 的深度集成。

| 模块 | 用途 |
|---|---|
| `RHI` | 提供渲染硬件接口抽象，用于创建和操作 GPU 资源（纹理、Fence 等）。 |
| `RenderCore` | 提供渲染核心功能，如命令列表、渲染线程同步等。 |
| `MediaUtils` | 提供媒体工具函数和基础类，可能用于时间戳、采样率等处理。 |
| `AVCodecsCore` | 本插件的核心模块，提供编解码器的抽象基类和资源管理。`AVCodecsCoreRHI` 依赖于它。 |

## 维护状态

### 近期更新

```
- 2025-10-03 2205ae004b8f [PS2, EpicRtc] QOL: Update EpicRtc to tagged release version epic-rtc-0.3-ue5.7.0 and update PS2 usage
- 2025-09-15 20ee5e0e8b39 The source files included were modified by the UnrealCodeFixup tool so that they can pass the -mergemodules compilation. *This CL must be submitted before integrating PixelStreaming2 into RemoteSession plugin.
- 2025-08-20 f7e905a6a30c Replace some usages of FORCEINLINE with inline in AVCodec modules.
```

*   `2205ae004b8f`: 更新了 EpicRtc 依赖版本，并调整了 PixelStreaming2 (PS2) 的用法。这表明该插件与 PixelStreaming 功能紧密相关，并且仍在积极适配新的依赖。
*   `20ee5e0e8b39`: 使用 UnrealCodeFixup 工具修改了源文件以通过合并模块编译。这是为了支持将 PixelStreaming2 集成到 RemoteSession 插件所做的准备工作，属于重要的基础设施维护。
*   `f7e905a6a30c`: 将一些 `FORCEINLINE` 替换为 `inline`。这是一个代码质量/编译兼容性的改进。

### 维护评价

**活跃维护**。

该插件创建于 2023 年初，至今约 2 年，属于较新的模块。从最近的提交记录看，**维护非常活跃**。最近的更新（2025年8月-10月）并非简单的编译修复，而是涉及**依赖升级、重大功能集成准备（PixelStreaming2）和代码质量改进**。这表明该插件是 Epic 内部正在积极开发和使用的基础设施，很可能用于支撑 Pixel Streaming 等高级功能。

**注意**：该插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，意味着它仍处于实验阶段，API 可能发生变化，不建议在追求稳定性的生产项目中直接使用，但非常适合用于研究、原型开发或作为自定义媒体管线的基础。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore/Tests) (如果存在)