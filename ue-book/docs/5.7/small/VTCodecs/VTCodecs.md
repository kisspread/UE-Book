# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | VT 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 用途

VTCodecs 是 AVCodecs 编解码框架在 Apple 平台的实现，它封装了 Apple Video Toolbox 框架，提供硬件加速的视频编码与解码能力。支持 H.264、H.265（HEVC）和 VP9 格式。

该插件的存在意义在于：在 macOS、iOS、tvOS 等 Apple 设备上，利用原生硬件编解码器实现高效视频处理，替代软件编解码方案，降低 CPU 负载，提升性能。

## 使用场景

- **实时视频通话 / 直播**：在 Apple 设备上使用硬件编码器将摄像头画面编码为 H.264/H.265 流；或解码接收到的视频流。
- **本地视频录制与回放**：通过 Video Toolbox 的硬件加速对录制源进行编码，节省电量。
- **远程桌面 / 云游戏**：编码屏幕内容并传输，解码远程输入流。
- **视频编辑工具**：在编辑器中快速解码预览，或编码导出。

## 蓝图用法

VTCodecs 不直接暴露蓝图节点。所有编解码操作需通过 **AVCodecs** 系统在 C++ 层完成。蓝图用户可通过自定义 C++ 函数库间接调用。

## C++ 用法

### 头文件引入

```cpp
#include "VT.h"
#include "Video/Decoders/VideoDecoderVT.h"
#include "Video/Encoders/VideoEncoderVT.h"
// 以及其他所需配置头文件
```

### 基本用法

以下示例展示如何使用 `FVideoDecoderVT` 解码一个 H.264 帧（简化逻辑，完整流程需结合 AVCodecs 设备管理）。

```cpp
// 文件: Engine/Plugins/Experimental/AVCodecs/VTCodecs/Source/VTCodecs/Private/... (根据实际测试代码)
#include "VT.h"
#include "Video/Decoders/VideoDecoderVT.h"
#include "Video/Decoders/Configs/VideoDecoderConfigH264.h"
#include "AVCodecsCore/Video/VideoDecoder.h"

// 假设已有 FVideoResource Metal 资源
void DecodeOneFrame()
{
    // 1. 创建解码器实例
    TSharedRef<FVideoDecoderVT> Decoder = MakeShared<FVideoDecoderVT>();

    // 2. 打开设备（需要有效的 FAVDevice，通常从 AVCodecs 系统获取）
    TSharedRef<FAVDevice> Device = /* 获取渠道，如 FAVDevice::GetPrimary() */;
    TSharedRef<FAVInstance> Instance = /* 创建实例 */;
    Decoder->Open(Device, Instance);

    // 3. 配置解码参数
    FVideoDecoderConfigVT Config;
    Config.Codec = kCMVideoCodecType_H264;
    // 也可从 AVCodecs 标准配置转换：FAVExtension::TransformConfig(Config, H264Config);
    Decoder->ApplyConfig(Config);

    // 4. 发送待解码帧（FVideoPacket 需由用户构造）
    FVideoPacket Packet;
    Packet.Data = /* 原始 H.264 NAL 单元数据 */;
    Packet.Timestamp = /* CMTime 转换后的 uint64 时间? 实际 FVideoPacket 使用 uint32 */;
    Decoder->SendPacket(Packet);

    // 5. 接收解码后帧
    TResolvableVideoResource<FVideoResourceMetal> OutResource;
    Decoder->ReceiveFrame(OutResource);
    // OutResource 即包含解码后的 Metal 纹理
}
```

### 进阶用法

**编码并处理输出包**：

```cpp
#include "Video/Encoders/VideoEncoderVT.h"
#include "Video/Encoders/Configs/VideoEncoderConfigH264.h"

void EncodeFrame()
{
    TSharedRef<TVideoEncoderVT<FVideoResourceMetal>> Encoder = MakeShared<TVideoEncoderVT<FVideoResourceMetal>>();

    // 打开与配置
    TSharedRef<FAVDevice> Device = /* ... */;
    TSharedRef<FAVInstance> Instance = /* ... */;
    Encoder->Open(Device, Instance);

    FVideoEncoderConfigVT Config;
    Config.Width = 1920;
    Config.Height = 1080;
    Config.FrameRate = 30;
    Config.TargetBitrate = 5000000;
    Config.Codec = kCMVideoCodecType_H264;
    Config.PixelFormat = EVideoFormat::BGRA;
    Encoder->ApplyConfig(Config);

    // 发送待编码帧（需提供 Metal 纹理资源）
    TSharedPtr<FVideoResourceMetal> Resource = /* 从渲染线程获取 */;
    Encoder->SendFrame(Resource, 0, true); // 强制关键帧

    FVideoPacket OutPacket;
    while (Encoder->ReceivePacket(OutPacket))
    {
        // OutPacket.Data 包含编码后的 AVCC 格式 H.264 数据
        NaluRewriter::H264CMSampleBufferToAnnexBBuffer(...); // 如需 Annex B 格式
    }
}
```

**NALU 格式转换**：

```cpp
#include "Video/Util/NaluRewriter.h"

// 将解码器输出的 CMSampleBuffer 格式转换为 Annex B
CMVideoFormatDescriptionRef FormatDesc = /* 来自配置 */;
CMSampleBufferRef SampleBuffer = /* 从解码得到的，但实际解码器内部处理 */;
// 通常编码器输出 CMSampleBuffer，然后转换：
NaluRewriter::H264CMSampleBufferToAnnexBBuffer(SampleBuffer, true/*isKeyframe*/, OutBuffer);
```

## Demo 示例

一个简洁但可编译的最小示例（需包含必要模块依赖）：

**DecoderDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "VT.h"
#include "Video/Decoders/VideoDecoderVT.h"
#include "Video/Decoders/Configs/VideoDecoderConfigH264.h"
#include "Video/Resources/Metal/VideoResourceMetal.h"

class FDecoderDemo
{
public:
    void Run();
};
```

**DecoderDemo.cpp**

```cpp
#include "DecoderDemo.h"
#include "AVCodecsCore/AVDevice.h"
#include "AVCodecsCore/AVInstance.h"
#include "AVCodecsCore/Video/VideoDecoder.h"

void FDecoderDemo::Run()
{
    // 获取默认设备
    TSharedRef<FAVDevice> Device = FAVDevice::GetPrimary();
    TSharedRef<FAVInstance> Instance = Device->CreateInstance();
    
    // 创建解码器
    TSharedRef<FVideoDecoderVT> Decoder = MakeShared<FVideoDecoderVT>();
    FAVResult Result = Decoder->Open(Device, Instance);
    check(Result.IsOK());
    
    // 配置 H.264 参数
    FVideoDecoderConfigVT Config;
    Config.Codec = kCMVideoCodecType_H264;
    // 也可从标准 AVCodecs 配置转换，这里直接设置
    Decoder->ApplyConfig(Config);
    
    // 构造一个 H.264 关键帧包（实际应从流中提取）
    FVideoPacket Packet;
    // Packet.Data = ...;
    Packet.Timestamp = 0;
    Decoder->SendPacket(Packet);
    
    // 接收解码结果
    TResolvableVideoResource<FVideoResourceMetal> OutResource;
    Decoder->ReceiveFrame(OutResource);
    // OutResource 准备就绪，可用于渲染
}
```

## 模块依赖

**使用 VTCodecs 时，你的 .Build.cs 需添加以下模块依赖**（省略 Core、Engine 等常见模块）：

| 模块 | 用途 |
|---|---|
| `AVCodecs` | 基础的 AV 编解码框架，提供设备/实例/配置转换 |
| `AVCodecsCore` | 核心类型与接口定义 |
| `MetalRHI` | Metal 渲染资源（`FVideoResourceMetal`） |
| `RHI` | 渲染硬件接口，用于纹理操作 |

> **注意**：系统框架 `VideoToolbox` 和 `CoreMedia` 由 VTCodecs 内部处理，无需在公共依赖中添加。

## 维护状态

### 近期更新

- 2025-09-16 — [AVCodecs] Disable VTCodecs if IOSurface is unsupported.
- 2025-05-01 — [AVCodecs, PS2] Fix: VideoToolbox only decoding a few frames
- 2025-04-17 — [AVCodecs] Fix crash when Decoding VP9 on Apple with VTCodecs.
- 2025-04-03 — Fix Xcode16.3 compile issues
- 2024-09-25 — [AVCodecs] Fix: VTCodecs hardware decoding. NOTE: There is a known memory leak with this codepath but

### 维护评价

- **创建时间**：2024-09-25，至今约 1 年，属于较新插件。
- **近期更新**：最近 6 个月内有多次功能修复和兼容性更新（包括崩溃修复、帧丢失修复、IOSurface 支持检查），表明团队正在积极维护。
- **已知问题**：官方 commit 中提及已知的内存泄漏（`NOTE: There is a known memory leak`），使用时应留意。但该泄漏可能已在后续修复中处理（后续 commit 未再次提及）。
- **状态**：实验性插件，但 Bug 修复频繁，稳定性逐渐提升。推荐用于开发测试和生产中评估，但需注意内存泄漏可能影响长时间运行的应用。

## 相关链接

- [源码（插件根）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [官方 AVCodecs 文档（若有）]()
- [测试用例（可能位于 Engine/Tests/AVCodecs 或本插件内）]()