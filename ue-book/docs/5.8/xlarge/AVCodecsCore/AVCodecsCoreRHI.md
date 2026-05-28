# AVCodecs Core

> Core Plugin for various Audio/Video codecs

| 属性 | 值 |
|---|---|
| 中文名 | 音视频编解码核心 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AVCodecsCore` (Runtime), `AVCodecsCoreRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore) | |

## 用途

这个插件的核心目的是提供一个跨平台、跨图形 API 的音视频编解码器抽象框架。它不是某个具体的编解码器实现（如硬件H264编码），而是一个基础架构。

**核心价值**：它解决了在不同图形 API (DirectX, Vulkan, Metal) 和不同平台 (Windows, Linux, Android, iOS) 上，对 GPU 纹理资源进行音视频编解码时，接口不统一的问题。插件定义了一套标准接口（`TVideoEncoder`, `TVideoDecoder`, `FVideoResource`），具体的编解码器实现（如 NVIDIA NVENC, Apple VideoToolbox, Vulkan Video）可以通过这套接口进行封装，从而为上层应用提供一致的调用方式。

## 使用场景

- **游戏内录制与回放**：你需要将游戏画面（渲染目标）高效地编码为 H.264/H.265 视频流，用于回放或直播推流。
- **实时视频处理**：你需要接收解码后的视频帧（例如来自摄像头或网络流），并将其应用到游戏内的纹理上。
- **跨平台媒体处理**：你的游戏需要在 PC (D3D12/Vulkan)、主机和移动平台 (Metal/ES) 上运行，并希望使用同一套代码处理音视频编解码，而无需关心底层图形 API 的差异。
- **开发新的编解码器**：你想为 UE5 封装一个新的硬件或软件音视频编解码器，需要一个稳定且结构清晰的基类框架。

## 蓝图用法

该插件提供了 `USimpleVideoEncoder`, `USimpleVideoDecoder`, `USimpleAudioEncoder` 等蓝图友好的类，用于简化音视频编解码操作。

### 核心节点

#### 视频编码 (`USimpleVideoEncoder`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 打开编码器，指定编解码器和配置。支持同步或异步模式。 | `USimpleVideoEncoder` |
| `Close` | 关闭编码器，释放资源。 | `USimpleVideoEncoder` |
| `SendFrame (Render Target)` | 将 `UTextureRenderTarget2D` 发送到编码器进行编码。 | `USimpleVideoEncoder` |
| `SendFrame (Texture)` | 将 `UTexture2D` 发送到编码器进行编码。 | `USimpleVideoEncoder` |
| `ReceivePacket` | 尝试从编码器接收一个编码完成的视频数据包。 | `USimpleVideoEncoder` |
| `ReceivePackets` | 从编码器接收所有可用的编码视频数据包。 | `USimpleVideoEncoder` |

#### 视频解码 (`USimpleVideoDecoder`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 打开解码器，指定编解码器。支持同步或异步模式。 | `USimpleVideoDecoder` |
| `Close` | 关闭解码器。 | `USimpleVideoDecoder` |
| `SendPacket` | 向解码器发送一个待解码的视频数据包。 | `USimpleVideoDecoder` |
| `ReceiveFrame` | 尝试从解码器接收一帧解码后的图像，并将其应用到提供的 `UTextureRenderTarget2D`。 | `USimpleVideoDecoder` |

#### 音频编码 (`USimpleAudioEncoder`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 打开音频编码器。 | `USimpleAudioEncoder` |
| `SendFrame (PCM16)` | 发送 PCM 浮点音频数据进行编码。 | `USimpleAudioEncoder` |
| `ReceivePacket` | 接收编码后的音频数据包。 | `USimpleAudioEncoder` |

### 使用示例（蓝图描述）

**编码游戏画面为 H.264 视频流**：
1. 创建一个 `USimpleVideoEncoder` 对象。
2. 调用 `Open` 节点，选择 `ESimpleVideoCodec::H264`，配置 `FSimpleVideoEncoderConfig`（宽、高、帧率、码率），并设置 `bAsynchronous` 为 `true` 以使用异步编码。
3. 在游戏逻辑中（如 Tick 事件），调用 `SendFrame (Render Target)` 节点，将当前游戏的 `UTextureRenderTarget2D` 和时间戳发送给编码器。
4. 通过 `ReceivePackets` 芯片持续轮询编码完成的 `FSimpleVideoPacket`，可用于写入文件或发送到网络。

## C++ 用法

核心 C++ 接口分为两层：
1.  **抽象层 (`AVCodecsCore` 模块)**：定义编解码器和资源的核心接口 (`TVideoEncoder`, `TVideoDecoder`, `FVideoResource`)。
2.  **RHI 实现层 (`AVCodecsCoreRHI` 模块)**：提供面向 RHI 资源（如 `FTextureRHIRef`）的实现，并负责根据当前运行的图形 API 动态选择底层平台编解码器。

### 头文件引入

```cpp
// 使用 RHI 视频资源和编码器
#include “Video/Resources/VideoResourceRHI.h”
#include “Video/Encoders/VideoEncoderRHI.h”
// 使用简化的蓝图友好接口
#include “Video/Encoders/SimpleVideoEncoder.h”
#include “Video/Decoders/SimpleVideoDecoder.h”
```

### 基本用法 (C++ 同步编码)

此示例展示了如何使用 `USimpleVideoEncoder` 的 C++ 等价物进行同步编码。

```cpp
// 来自 Public/Video/Encoders/SimpleVideoEncoder.h 和相关实现
// 创建编码器配置
FSimpleVideoEncoderConfig EncoderConfig;
EncoderConfig.Width = 1920;
EncoderConfig.Height = 1080;
EncoderConfig.TargetFramerate = 60;
EncoderConfig.TargetBitrate = 8000000; // 8 Mbps

// 创建编码器实例
USimpleVideoEncoder* VideoEncoder = NewObject<USimpleVideoEncoder>();

// 打开编码器 (同步模式)
bool bSuccess = VideoEncoder->Open(ESimpleVideoCodec::H264, EncoderConfig, false);
if (bSuccess)
{
    // 获取一帧游戏画面 (假设我们有一个有效的 FTextureRHIRef)
    FTextureRHIRef GameFrameTexture = /* ... 从渲染目标获取 ... */;
    double Timestamp = FPlatformTime::Seconds();

    // 发送帧进行编码
    bSuccess = VideoEncoder->SendFrame(GameFrameTexture, Timestamp, true /* bForceKeyframe */);
    if (bSuccess)
    {
        // 接收编码后的数据包
        FSimpleVideoPacket EncodedPacket;
        if (VideoEncoder->ReceivePacket(EncodedPacket))
        {
            // 处理 EncodedPacket.RawPacket 中的数据
            // ... 写入文件或发送到网络 ...
        }
    }
    VideoEncoder->Close();
}
```

### 进阶用法 (使用底层模板接口)

对于需要更精细控制的场景，可以直接使用底层模板类。

```cpp
// 来自 Public/Video/Encoders/VideoEncoderRHI.h 和 Video/Resources/VideoResourceRHI.h
// 1. 获取或创建 RHI 视频资源
FAVDeviceRef Device = /* ... 获取当前 RHI 设备 ... */;
FVideoDescriptor Descriptor = FVideoResourceRHI::GetDescriptorFrom(Device, MyTextureRef);
TSharedPtr<FVideoResourceRHI> VideoResource = FVideoResourceRHI::Create(Device, Descriptor);

// 2. 填充资源数据 (从 CPU 内存拷贝或直接引用 GPU 资源)
VideoResource->CopyFrom(MyPixelData);

// 3. 创建并配置底层 RHI 编码器
// 实际实现由平台特定模块 (如 AVCodecsH264) 提供，这里以接口演示
TSharedPtr<TVideoEncoder<FVideoResourceRHI, FVideoEncoderConfig>> PlatformEncoder = /* ... */;
PlatformEncoder->Open(Device, Instance);
PlatformEncoder->SetPendingConfig(Config);
PlatformEncoder->ApplyConfig();

// 4. 发送资源进行编码
FAVResult Result = PlatformEncoder->SendFrame(VideoResource, Timestamp, false);
if (Result.IsSuccess())
{
    // 5. 接收编码包
    FVideoPacket Packet;
    Result = PlatformEncoder->ReceivePacket(Packet);
    // ... 处理 Packet ...
}
```

## Demo 示例

一个最小化的 C++ 类，演示如何使用 `USimpleVideoEncoder` 编码一个渲染目标。

**MyVideoCaptureComponent.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “Components/ActorComponent.h”
#include “MyVideoCaptureComponent.generated.h”

class USimpleVideoEncoder;
class UTextureRenderTarget2D;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyVideoCaptureComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyVideoCaptureComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, Category = “Video Capture”)
    int32 VideoWidth = 1280;

    UPROPERTY(EditAnywhere, Category = “Video Capture”)
    int32 VideoHeight = 720;

private:
    UPROPERTY()
    USimpleVideoEncoder* VideoEncoder;

    UPROPERTY()
    UTextureRenderTarget2D* RenderTarget;

    double CaptureStartTime;
};
```

**MyVideoCaptureComponent.cpp**
```cpp
#include “MyVideoCaptureComponent.h”
#include “Video/Encoders/SimpleVideoEncoder.h”
#include “Engine/TextureRenderTarget2D.h”

UMyVideoCaptureComponent::UMyVideoCaptureComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyVideoCaptureComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建渲染目标
    RenderTarget = NewObject<UTextureRenderTarget2D>(this);
    RenderTarget->InitAutoFormat(VideoWidth, VideoHeight);
    RenderTarget->UpdateResourceImmediate(true);

    // 创建并打开编码器 (同步模式)
    VideoEncoder = NewObject<USimpleVideoEncoder>(this);
    FSimpleVideoEncoderConfig Config;
    Config.Width = VideoWidth;
    Config.Height = VideoHeight;
    Config.TargetFramerate = 30;
    Config.TargetBitrate = 5000000;

    if (VideoEncoder->Open(ESimpleVideoCodec::H264, Config, false))
    {
        UE_LOG(LogTemp, Log, TEXT(“Video encoder opened successfully.”));
        CaptureStartTime = FPlatformTime::Seconds();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to open video encoder.”));
    }
}

void UMyVideoCaptureComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (VideoEncoder)
    {
        VideoEncoder->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void UMyVideoCaptureComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (VideoEncoder && VideoEncoder->IsOpen())
    {
        // 假设你已经将游戏画面渲染到了 RenderTarget (例如通过 SceneCaptureComponent2D)
        // 将渲染目标发送给编码器
        double CurrentTime = FPlatformTime::Seconds() - CaptureStartTime;
        bool bSuccess = VideoEncoder->SendFrameRenderTarget(RenderTarget, CurrentTime);

        if (bSuccess)
        {
            // 尝试接收编码包
            FSimpleVideoPacket Packet;
            while (VideoEncoder->ReceivePacket(Packet))
            {
                // 在这里处理编码后的数据包 Packet.RawPacket
                // 例如，写入到文件或通过网络发送
                UE_LOG(LogTemp, Verbose, TEXT(“Received video packet, size: %d”), Packet.RawPacket.Data.Num());
            }
        }
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块（除了常见的 Core/Engine 模块）：

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | 提供音视频编解码的核心抽象接口和类型定义。 |
| `AVCodecsCoreRHI` | 提供基于 RHI 资源的编解码器实现和资源管理。 |
| `RHI` | 提供 RHI 资源类型（如 `FTextureRHIRef`）和图形 API 抽象。 |
| `MediaUtils` | 提供一些媒体相关的工具类和接口。 |
| `RenderCore` | 提供渲染核心功能，与纹理资源交互相关。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 的编译警告。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间保持一致。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的枚举作用域问题，避免了可能产生的垃圾输出。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32 位格式说明符在参数为 64 位时（以及反之）的使用问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 宏。 |

### 维护评价

- **状态**：**维护中，但不活跃**。
- **分析**：该插件创建于 2023 年初，是一个实验性插件。从最近的提交记录看，近几个月仍有维护活动，但主要集中在**修复编译警告、代码规范统一和小错误修复**上，没有重大的功能更新或架构变化。
- **风险**：作为实验性插件，其 API 和行为在未来版本中可能发生不兼容的变化。依赖此插件进行核心功能开发需谨慎。
- **建议**：**推荐用于实验和原型开发**，特别是需要快速验证跨平台音视频处理概念的项目。对于需要稳定生产环境的项目，建议等待其正式发布或自行封装特定平台的编解码器。如果使用，需密切关注 UE 版本更新日志中关于此插件的变更说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- [官方文档]（无）
- [测试用例]（未在源码信息中提供具体路径，通常位于 `Engine/Plugins/Experimental/AVCodecs/AVCodecsCore/Tests` 或 `Engine/Tests` 下）