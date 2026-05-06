# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | 苹果视频编解码器插件 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 用途

VTCodecs 是 UE5 AVCodecs 框架的 Apple 平台编解码器实现。它封装了 Apple 的 VideoToolbox 框架，在 macOS 和 iOS 设备上提供硬件加速的 H.264、H.265/HEVC 视频编码与解码能力。该插件解决了跨平台视频编解码中 Apple 平台特殊 API 的适配问题，使得上层 AVCodecs 用户无需关心平台差异即可利用原生硬件编解码器。

## 使用场景

- 你需要对 iOS 或 macOS 上的视频流进行实时硬件编码（如推流、录制）
- 你希望在 Apple 设备上使用最高效的 H.264/H.265 解码以播放视频
- 你在开发基于 AVCodecs 的媒体处理管线，需要无缝支持 Apple 平台

## 蓝图用法

VTCodecs 不直接暴露蓝图可调用节点。所有编解码器操作通过 C++ 的 AVCodecs 接口完成。蓝图用户可通过**媒体播放器**、**媒体捕获**等高级别蓝图节点间接使用，但底层编解码器选择由系统自动切换。

若需要在蓝图中触发特定编解码器配置，建议通过自定义 C++ 蓝图函数库封装 AVCodecs 调用。

## C++ 用法

### 头文件引入

```cpp
#include "AVCodecsCore.h"        // 基类
#include "VideoToolboxCodec.h"   // VTCodecs 提供的编解码器实现
```

### 基本用法

以下示例展示如何通过 AVCodecs 框架创建一个 H.264 编码器，并利用 VTCodecs 提供的 Apple 实现。

```cpp
// 来源：基于 AVCodecs 测试用例（相似逻辑存在于 AVCodecsCore 测试中）
#include "AVCodecsCore.h"
#include "VideoToolboxCodec.h"

void EncodeFrameWithVTCodecs()
{
    // 1. 获取编解码器配置
    FVideoEncoderConfig Config;
    Config.Width = 1920;
    Config.Height = 1080;
    Config.FrameRate = 30;
    Config.Bitrate = 5000000;  // 5 Mbps
    Config.CodecType = ECodecType::H264;

    // 2. 创建编码器（AVCodecs 会自动选择平台最佳实现，macOS/iOS 上为 VTCodecs）
    TUniquePtr<FVideoEncoder> Encoder = FVideoEncoder::Create(Config);
    check(Encoder.IsValid());

    // 3. 输入帧（假设已有 RGBA 像素数据）
    FVideoFrame InputFrame;
    InputFrame.Width = 1920;
    InputFrame.Height = 1080;
    InputFrame.Data = /* 你的数据指针 */;
    InputFrame.Stride = 1920 * 4;

    // 4. 编码
    bool bEncoded = Encoder->Encode(InputFrame);
    ensure(bEncoded);

    // 5. 获取编码后的数据通过回调（通常在编码器创建时设置回调）
    // 实际使用需设置 FVideoEncoderConfig::OnEncodedFrame 等回调
}
```

### 进阶用法

多编解码器切换与配置：

```cpp
// 动态选择 H.265 硬件编码器（若设备支持）
FVideoEncoderConfig Config;
Config.CodecType = ECodecType::H265;
// VTCodecs 会尝试创建 VideoToolbox 的 HEVC 编码器
TUniquePtr<FVideoEncoder> Encoder = FVideoEncoder::Create(Config);
```

解码器使用类似：

```cpp
TUniquePtr<FVideoDecoder> Decoder = FVideoDecoder::Create(FVideoDecoderConfig());
// 输入H.264/H.265 NAL单元进行解码
```

## Demo 示例

以下是一个完整的 C++ 类，展示如何在游戏模块中使用 VTCodecs 进行视频帧编码：

```cpp
// MyCodecDemo.h
#pragma once
#include "CoreMinimal.h"
#include "AVCodecsCore.h"

class FMyCodecDemo
{
public:
    void Run();
};
```

```cpp
// MyCodecDemo.cpp
#include "MyCodecDemo.h"
#include "VideoToolboxCodec.h"
#include "Containers/Array.h"

void FMyCodecDemo::Run()
{
    // 配置编码器
    FVideoEncoderConfig Config;
    Config.Width = 640;
    Config.Height = 480;
    Config.FrameRate = 30;
    Config.Bitrate = 2000000;
    Config.CodecType = ECodecType::H264;

    // 创建编码器
    TUniquePtr<FVideoEncoder> Encoder = FVideoEncoder::Create(Config);
    if (!Encoder)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create video encoder (may not be supported on this platform)"));
        return;
    }

    // 模拟编码一帧
    TArray<uint8> PixelData;
    PixelData.SetNum(640 * 480 * 4); // RGBA
    FMemory::Memset(PixelData.GetData(), 128);

    FVideoFrame Frame;
    Frame.Width = 640;
    Frame.Height = 480;
    Frame.Data = PixelData.GetData();
    Frame.Stride = 640 * 4;

    bool bSuccess = Encoder->Encode(Frame);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Frame encoded successfully via VTCodecs (Apple VideoToolbox)"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | AVCodecs 框架核心基类与工厂接口 |
| `RHI` | 渲染硬件接口，用于与 GPU 纹理交互（VTCodecsRHI 模块依赖） |
| `ApplePlatform` | Apple 平台特性支持（隐式依赖） |

其他依赖均为标准 `Core`、`Engine`、`CoreUObject` 等，未特殊列出。

## 维护状态

### 近期更新

- 2026-02-27	ae4a826	Take two after fixing bad find-and-replace.
- 2026-02-27	6759aa54	[Backout] - CL51314860
- 2026-02-27	7723864b	Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist
- 2026-01-24	e793e61e	Fixed more compile errors when using portable toolchain
- 2026-01-22	ad8a0de1	Update BuildVersionSettings that are out of date

### 维护评价

VTCodecs 是一个**实验性**插件，创建于 2026 年初，至今约 1 年。最近的更新集中在编译错误修复和代码迁移（如委托注册方式），**没有功能性更新**。目前插件基本可用，但以下问题需要注意：

- 该插件需要手动启用（`EnabledByDefault: false`）
- 实验性版本可能缺少部分编解码器特性（如 B 帧、NV12 支持等）
- 仅适用于 Apple 平台（macOS、iOS、tvOS）

对于需要在 Apple 设备上使用硬件编解码的开发者，该插件是推荐的解决方案。但由于其实验性状态，建议在发布前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/avcodecs-in-unreal-engine/)（AVCodecs 框架通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/Tests)