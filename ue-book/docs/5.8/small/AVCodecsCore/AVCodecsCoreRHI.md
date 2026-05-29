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

AVCodecsCore 插件为 Unreal Engine 提供了一个统一的、跨平台的音频和视频编解码框架。它解决了以下核心问题：

1.  **抽象编解码器接口**：定义了 `TVideoEncoder`、`TVideoDecoder` 等模板基类，将编码和解码的通用逻辑与具体平台实现（如 D3D11、D3D12、Vulkan、Metal）分离。
2.  **统一 RHI 资源处理**：通过 `FVideoResourceRHI` 等类，为不同图形 API (RHI) 创建的纹理资源提供了统一的包装和操作接口（如 `CopyFrom`、`TransformResource`），简化了跨平台资源管理。
3.  **提供蓝图友好的简化层**：通过 `USimpleVideoEncoder`、`USimpleVideoDecoder` 和 `USimpleAudioEncoder` 等蓝图类，封装了复杂的底层操作，使得在蓝图中也能方便地进行音视频编解码。
4.  **支持异步操作**：编码器和解码器可以配置为异步模式，在后台线程处理帧数据和数据包，避免阻塞游戏线程。

该插件是其他更具体编解码器插件（如 NVENC、Vulkan 编码器等）的基石，它们需要基于 AVCodecsCore 提供的框架和 `FVideoResourceRHI` 来实现具体的编解码功能。

## 使用场景

- **游戏内录像/回放**：需要将游戏画面（Render Target 或 Texture）实时编码为视频流（如 H.264/H.265）并保存或推流。
- **实时视频流推送**：在直播或网络视频通话场景中，将捕获的视频帧编码后通过网络发送。
- **VR/360 视频播放**：解码预录制的视频流并将其映射到天空盒或 360 度全景球上。
- **音频录制与处理**：将麦克风或其他音频源捕获的 PCM 数据实时编码为 AAC 等格式。
- **跨平台多媒体应用开发**：开发需要同时在 PC、主机和移动设备上运行的音视频处理功能，利用此插件屏蔽底层图形 API 差异。

## 蓝图用法

### 核心节点（视频）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open (Video)` | 使用指定的编解码器和配置打开视频编码器，支持异步模式。 | `USimpleVideoEncoder` |
| `Close (Video)` | 关闭视频编码器，释放资源。 | `USimpleVideoEncoder` |
| `Send Frame (Render Target)` | 将 `UTextureRenderTarget2D` 作为一帧发送给编码器。 | `USimpleVideoEncoder` |
| `Send Frame (Texture)` | 将 `UTexture2D` 作为一帧发送给编码器。 | `USimpleVideoEncoder` |
| `Receive Packet` | 尝试从编码器接收一个编码后的视频数据包。 | `USimpleVideoEncoder` |
| `Receive Packets` | 尝试从编码器接收所有可用的视频数据包。 | `USimpleVideoEncoder` |
| `Get Codec` | 获取当前编码器使用的编解码器类型。 | `USimpleVideoEncoder` |
| `Get Config` / `Set Config` | 获取或设置编码器配置（如分辨率、帧率、码率）。 | `USimpleVideoEncoder` |

### 核心节点（音频）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open (Audio)` | 使用指定的编解码器和配置打开音频编码器。 | `USimpleAudioEncoder` |
| `Close (Audio)` | 关闭音频编码器。 | `USimpleAudioEncoder` |
| `Send Frame (PCM16)` | 发送浮点 PCM 音频数据进行编码。 | `USimpleAudioEncoder` |
| `Receive Packet` | 接收一个编码后的音频数据包。 | `USimpleAudioEncoder` |

### 使用示例（蓝图描述）

**视频编码流程**：
1.  创建一个 `USimpleVideoEncoder` 对象。
2.  调用 `Open` 节点，选择 `ESimpleVideoCodec::H264`，配置 `FSimpleVideoEncoderConfig`（可设置宽、高、帧率、码率），并选择是否异步。
3.  在游戏循环中，当有新的渲染帧准备好时，调用 `Send Frame (Render Target)` 节点，传入当前帧的 `UTextureRenderTarget2D` 资源和时间戳。
4.  调用 `Receive Packet` 或 `Receive Packets` 节点获取编码后的 `FSimpleVideoPacket`，可用于后续保存或网络发送。
5.  结束时调用 `Close` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "SimpleVideo.h"
#include "Video/Encoders/SimpleVideoEncoder.h"
```

### 基本用法

**使用简化视频编码器进行编码**
（示例逻辑基于 `Public/Video/Encoders/SimpleVideoEncoder.h` 中定义的接口）

```cpp
// 创建编码器实例
USimpleVideoEncoder* VideoEncoder = NewObject<USimpleVideoEncoder>();

// 配置编码参数
FSimpleVideoEncoderConfig Config;
Config.Width = 1920;
Config.Height = 1080;
Config.TargetFramerate = 30;
Config.TargetBitrate = 5000000; // 5 Mbps
Config.MaxBitrate = 8000000;    // 8 Mbps

// 打开编码器，使用 H.264 编码，启用异步模式
bool bSuccess = VideoEncoder->Open(ESimpleVideoCodec::H264, Config, true);

if (bSuccess)
{
    // 假设你有一个有效的 UTextureRenderTarget2D* 指针 (RenderTarget)
    UTextureRenderTarget2D* RenderTarget = /* ... */;
    double Timestamp = /* 当前时间 */;

    // 发送一帧进行编码
    bool bFrameSent = VideoEncoder->SendFrameRenderTarget(RenderTarget, Timestamp, false);

    // 在后续逻辑中（如 Tick），尝试接收编码后的数据包
    FSimpleVideoPacket OutPacket;
    if (VideoEncoder->ReceivePacket(OutPacket))
    {
        // 处理 OutPacket.RawPacket (FVideoPacket) 中的数据
        // 例如：写入文件或发送到网络
    }

    // ... 更多帧的编码与接收 ...

    // 编码完成后关闭
    VideoEncoder->Close();
}
```

### 进阶用法

**直接操作底层 RHI 资源进行编码**
（适用于需要更精细控制纹理资源的场景，接口基于 `Public/Video/Resources/VideoResourceRHI.h`）

```cpp
#include "Video/Resources/VideoResourceRHI.h"

// 获取当前 RHI 设备
TSharedRef<FAVDevice> AVDevice = /* 从某个上下文获取 FAVDevice */;

// 假设你有一个 FTextureRHIRef TextureRHI
FTextureRHIRef TextureRHI = /* ... */;

// 通过静态方法创建 FVideoResourceRHI 包装器
TSharedPtr<FVideoResourceRHI> VideoResource = FVideoResourceRHI::Create(AVDevice.ToSharedPtr(), 
    FVideoResourceRHI::GetDescriptorFrom(AVDevice, TextureRHI));

if (VideoResource.IsValid())
{
    // 可以对资源进行验证、锁定、数据拷贝等操作
    FAVResult ValidateResult = VideoResource->Validate();
    if (ValidateResult == EAVResult::Success)
    {
        // 锁定资源（根据具体平台实现）
        VideoResource->Lock();

        // 也可以从其他资源拷贝数据，例如：
        // TArray<uint8> SomeData;
        // VideoResource->CopyFrom(SomeData);
        
        // 然后可以将此 VideoResource 传递给底层的 TVideoEncoder<FVideoResourceRHI, TConfig> 实例
        // 这是 AVCodecsCore 为具体平台编码器插件（如 NVENC）定义的接口。
    }
}
```

## Demo 示例

一个最小的视频编码示例，将一帧静态画面编码并接收数据包。

**MyVideoEncoderActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SimpleVideo.h"
#include "Video/Encoders/SimpleVideoEncoder.h"
#include "MyVideoEncoderActor.generated.h"

UCLASS()
class AMyVideoEncoderActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVideoEncoderActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    USimpleVideoEncoder* VideoEncoder;

    int32 FrameCount;
    FSimpleVideoEncoderConfig EncoderConfig;
};
```

**MyVideoEncoderActor.cpp**
```cpp
#include "MyVideoEncoderActor.h"
#include "Engine/TextureRenderTarget2D.h"

AMyVideoEncoderActor::AMyVideoEncoderActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyVideoEncoderActor::BeginPlay()
{
    Super::BeginPlay();

    FrameCount = 0;
    VideoEncoder = NewObject<USimpleVideoEncoder>();

    // 配置编码器
    EncoderConfig.Width = 640;
    EncoderConfig.Height = 480;
    EncoderConfig.TargetFramerate = 30;
    EncoderConfig.TargetBitrate = 2000000;
    EncoderConfig.MaxBitrate = 3000000;

    // 打开编码器（同步模式以便于示例）
    if (VideoEncoder->Open(ESimpleVideoCodec::H264, EncoderConfig, false))
    {
        UE_LOG(LogTemp, Log, TEXT("Video Encoder opened successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Video Encoder."));
    }
}

void AMyVideoEncoderActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!VideoEncoder || !VideoEncoder->IsOpen())
    {
        return;
    }

    // 模拟一个简单的渲染目标（实际应用中应使用真实的 RT）
    // 注意：此示例简化了 RT 的创建和绘制，仅展示编码器 API 调用。
    UTextureRenderTarget2D* RenderTarget = NewObject<UTextureRenderTarget2D>();
    RenderTarget->InitAutoFormat(640, 480); // 创建一个临时 RT

    // 发送帧到编码器
    double Timestamp = GetWorld()->GetTimeSeconds();
    if (VideoEncoder->SendFrameRenderTarget(RenderTarget, Timestamp))
    {
        FrameCount++;
        UE_LOG(LogTemp, Log, TEXT("Sent frame %d"), FrameCount);
    }

    // 尝试接收编码后的数据包
    FSimpleVideoPacket ReceivedPacket;
    if (VideoEncoder->ReceivePacket(ReceivedPacket))
    {
        UE_LOG(LogTemp, Log, TEXT("Received encoded packet, raw size: %d"), ReceivedPacket.RawPacket.Data.Num());
        // 在这里处理编码后的数据，例如写入文件
    }
}

void AMyVideoEncoderActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (VideoEncoder && VideoEncoder->IsOpen())
    {
        VideoEncoder->Close();
        UE_LOG(LogTemp, Log, TEXT("Video Encoder closed."));
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 提供 `FTextureRHIRef`、`FRHICommandListImmediate` 等 RHI 基础设施。 |
| `RHI` | 定义 `ERHIInterfaceType`、`GDynamicRHI` 等全局 RHI 信息。 |
| `AVCodecsCore` | 提供核心的编解码器基类、资源描述符、设备/实例抽象等（`AVCodecsCoreRHI` 模块依赖它）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量转换为浮点时产生的警告。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间保持一致。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出垃圾的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化说明符：当参数为64位时使用32位说明符（反之亦然）的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF。 |

### 维护评价

- **年龄与状态**：插件创建于 2023 年初，目前约 3 年历史。从最近的 Git 记录看，它仍在被积极维护，主要集中在**编译器警告修复、代码可移植性和日志标准化**等方面。
- **更新频率**：近期的更新密集（2026年4月-5月），虽然大多是底层改进而非新功能，但这表明 Epic 内部在持续使用和打磨该框架。
- **实验性警告**：插件明确标记为 **实验性 (IsExperimentalVersion = true)** 且**默认禁用 (EnabledByDefault = false)**。这意味着其 API 可能不稳定，不适合直接用于最终发布的项目。
- **推荐度**：**推荐用于研究、学习和内部工具开发**。对于需要在 UE 中实现自定义编解码功能的开发者，它是极佳的参考和基础框架。但对于生产项目，应谨慎评估其稳定性，或等待其脱离实验状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- [官方文档] (无)
- [测试用例] (未在提供的信息中找到明确路径，可能需要在 UE 源码中搜索 `AVCodecsCoreRHI` 相关的自动化测试。)