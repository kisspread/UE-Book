# LibVpxCodecs

> Adds codecs from LibVpx to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | LibVpx编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LibVpxCodecs` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/LibVpxCodecs) | |

## 用途

该插件将开源的 `libvpx` 库（用于 VP8 和 VP9 视频编解码）集成到 Unreal Engine 的 `AVCodecs` 框架中。它解决了在 UE 项目中使用软件实现的 VP8/VP9 编解码器的需求，为实时视频通信、流媒体或视频处理等功能提供了跨平台的编解码能力。这对于不支持硬件 VP8/VP9 编解码的平台或需要特定软件编解码行为的场景尤其重要。

## 使用场景

- 你需要在项目中实现基于 VP9 的实时视频通话或直播推流功能。
- 你的目标平台（如某些移动设备或旧硬件）缺乏 VP9 硬件编解码支持，需要软件实现作为后备。
- 你正在开发一个需要高度可配置 VP8/VP9 编码参数（如 SVC 可伸缩视频编码、多码率控制）的视频处理管线。
- 你希望利用 `AVCodecs` 框架统一管理不同的编解码器实现。

## 蓝图用法

根据源码分析，该插件主要提供 C++ 模板类和接口，**未发现**暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。其设计是面向底层编解码管线的，因此主要通过 C++ 代码进行调用和控制。

## C++ 用法

### 头文件引入

使用编码器时：
```cpp
#include "Video/Encoders/VideoEncoderLibVpxVP9.h"
// 或
#include "Video/Encoders/VideoEncoderLibVpxVP8.h"
```

使用解码器时：
```cpp
#include "Video/Decoders/VideoDecoderLibVpxVP9.h"
// 或
#include "Video/Decoders/VideoDecoderLibVpxVP8.h"
```

### 基本用法

以下代码演示了如何创建一个 VP9 编码器并发送一帧进行编码（概念性示例，具体资源类型需根据实际 `TResource` 模板参数确定）：

```cpp
#include "Video/Encoders/VideoEncoderLibVpxVP9.h"
#include "Video/Encoders/Configs/VideoEncoderConfigLibVpx.h"

// 假设我们使用 CPU 资源
using FMyVP9Encoder = TVideoEncoderLibVpxVP9<FVideoResourceCPU>;

void EncodeOneFrame()
{
    // 1. 创建编码器实例
    TSharedRef<FMyVP9Encoder> Encoder = MakeShared<FMyVP9Encoder>();

    // 2. 配置编码器参数
    FVideoEncoderConfigLibVpx Config;
    Config.Width = 1920;
    Config.Height = 1080;
    Config.Framerate = 30;
    Config.TargetBitrate = 5000000; // 5 Mbps
    Config.KeyframeInterval = 300;  // 每300帧一个关键帧
    Config.NumberOfSpatialLayers = 1; // 单层（SVC）
    Config.NumberOfTemporalLayers = 1;

    // 3. 打开编码器（需要有效的 Device 和 Instance）
    TSharedRef<FAVDevice> Device = /* ... */;
    TSharedRef<FAVInstance> Instance = /* ... */;
    if (Encoder->Open(Device, Instance) != EAVResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open VP9 encoder."));
        return;
    }

    // 4. 应用配置
    if (Encoder->ApplyConfig(Config) != EAVResult::Success)
    {
        UE_LOG(LogTemp, Error, Text("Failed to apply config to VP9 encoder."));
        return;
    }

    // 5. 发送一帧数据（假设有有效的 CPU 图像资源 Resource）
    TSharedPtr<FVideoResourceCPU> Resource = /* ... */;
    uint32 Timestamp = /* 当前帧的时间戳 */;
    if (Encoder->SendFrame(Resource, Timestamp) == EAVResult::Success)
    {
        // 6. 接收编码后的数据包
        FVideoPacket Packet;
        while (Encoder->ReceivePacket(Packet) == EAVResult::Success)
        {
            // 处理编码后的 Packet (例如发送到网络或写入文件)
            ProcessEncodedPacket(Packet);
        }
    }

    // 7. 关闭编码器
    Encoder->Close();
}
```

### 进阶用法

`FVideoEncoderConfigLibVpx` 结构体提供了非常丰富的参数，用于控制 VP9 的高级特性，如 SVC（可伸缩视频编码）和性能标志。以下是一个配置双空间层（Spatial Layer）的示例：

```cpp
FVideoEncoderConfigLibVpx Config;
// ... 设置基础参数 ...

// 启用 SVC 并配置两个空间层
Config.NumberOfSpatialLayers = 2;
Config.ScalabilityMode = EScalabilityMode::L2T2; // 示例：2层2层时间可伸缩
Config.SpatialLayers[0].Width = 1280;
Config.SpatialLayers[0].Height = 720;
Config.SpatialLayers[0].TargetBitrate = 2500000;
Config.SpatialLayers[1].Width = 1920;
Config.SpatialLayers[1].Height = 1080;
Config.SpatialLayers[1].TargetBitrate = 5000000;
// 可以为每一层设置独立的码率、帧率等
```

## Demo 示例

以下是一个最小化、可编译的 VP8 解码器使用示例：

```cpp
// MyVideoProcessor.h
#pragma once
#include "CoreMinimal.h"
#include "Video/Decoders/VideoDecoderLibVpxVP8.h"

class FMyVideoProcessor
{
public:
    void ProcessVP8Stream(const TArray<uint8>& CompressedData);

private:
    // 使用 CPU 资源的 VP8 解码器
    TUniquePtr<TVideoDecoderLibVpxVP8<FVideoResourceCPU>> Decoder;
};
```

```cpp
// MyVideoProcessor.cpp
#include "MyVideoProcessor.h"
#include "Video/Decoders/Configs/VideoDecoderConfigLibVpx.h"
#include "AVCodecsCore/Public/Resources/VideoResourceCPU.h"

void FMyVideoProcessor::ProcessVP8Stream(const TArray<uint8>& CompressedData)
{
    if (!Decoder)
    {
        Decoder = MakeUnique<TVideoDecoderLibVpxVP8<FVideoResourceCPU>>();
        // 打开解码器
        TSharedRef<FAVDevice> Device = MakeShared<FAVDevice>();
        TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();
        if (Decoder->Open(Device, Instance) != EAVResult::Success)
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open VP8 decoder."));
            return;
        }
    }

    // 发送压缩数据包
    FVideoPacket Packet;
    Packet.Data = CompressedData;
    if (Decoder->SendPacket(Packet) != EAVResult::Success)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to send packet to VP8 decoder."));
        return;
    }

    // 接收并处理解码后的帧
    TSharedPtr<FVideoResourceCPU> DecodedResource;
    while (Decoder->ReceiveFrame(DecodedResource) == EAVResult::Success && DecodedResource.IsValid())
    {
        // 在这里处理解码后的图像资源（DecodedResource）
        // 例如，可以将其更新到纹理或进行其他处理
        HandleDecodedFrame(DecodedResource);
        DecodedResource.Reset();
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖 `AVCodecsCore` 以及此插件的 `LibVpxCodecs` 模块。`libvpx` 库本身作为第三方依赖已包含在引擎中。

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | 提供基础的音视频编解码框架和接口 |
| `LibVpxCodecs` | 提供 VP8/VP9 的具体编解码实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32/64 位格式说明符不匹配的问题，增强了代码的健壮性。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 进行了代码重构，移除了不必要的构造函数，可能涉及内存优化或编译改进。 |
| 2026-01-21 | `0e6a982e` | [AVCodecs] Add: Support for iOS and Android | 重要更新：为 iOS 和 Android 平台添加了支持，扩大了插件的适用范围。 |
| 2025-09-18 | `49fd637a` | The source files included were modified by the UnrealCodeFixup tool so that they can pass the -merge | 使用代码修正工具自动修改了部分源文件，以符合代码规范或解决合并冲突。 |

### 维护评价

**推荐使用，但需注意其“实验性”状态。**

- **年龄与状态**：插件创建于 2024 年中，约有 2 年历史，属于较新的实验性插件。
- **维护活跃度**：近期（2026 年）仍有更新，特别是增加了对移动平台（iOS/Android）的支持，表明 Epic 仍在积极维护和完善此插件。
- **内容与稳定性**：作为 `AVCodecs` 框架的一部分，其架构相对成熟。但 `IsExperimentalVersion: true` 和 `EnabledByDefault: false` 表明 Epic 尚未将其标记为稳定版本，API 和功能在未来版本中可能发生变化。
- **建议**：适合在需要 VP8/VP9 软件编解码的实验性项目或原型开发中使用。在生产环境中使用时，需密切关注引擎更新日志，并准备应对可能的 API 调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/LibVpxCodecs)
- (无特定官方文档链接)
- (插件本身未包含独立测试用例目录)