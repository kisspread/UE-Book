# LibVpxCodecs

> Adds codecs from LibVpx to AVCodecs

| 属性 | 值 |
|---|---|
| 分类 | Codecs |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | LibVpxCodecs (Runtime) |
| 创建时间 | 2024-06-18 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/LibVpxCodecs) | |

## 用途

LibVpxCodecs 是 UE5 AVCodecs 框架下的 VP8/VP9 视频编解码器实现，基于 Google 的开源 [libvpx](https://chromium.googlesource.com/webm/libvpx) 库。它为 UE5 的 `AVCodecsCore` 提供了 VP8 和 VP9 格式的硬件无关（纯 CPU）软编解码/编码能力。

该 plugin 解决的问题：在不依赖平台特定硬件编码器的情况下，提供跨平台的 VP8/VP9 编解码支持。VP8/VP9 是 WebRTC 和 WebM 容器中广泛使用的视频编码格式，在实时通信、屏幕共享、视频录制等场景中至关重要。

## 使用场景

- 你需要在项目中编码/解码 VP8 或 VP9 视频流（如 WebRTC 通信）
- 你需要一个不依赖硬件编码器的跨平台视频编解码方案
- 你在构建视频录制或屏幕捕获功能，需要 CPU 端的 VP8/VP9 编码
- 你需要 SVC（可伸缩视频编码）支持，用于自适应质量的实时视频流

## 蓝图用法

本 plugin 不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是一个纯 C++ Runtime 模块，通过 AVCodecsCore 的编码器/解码器注册机制与上层框架集成。

## C++ 用法

### 头文件引入

```cpp
// 编码器
#include "Video/Encoders/VideoEncoderLibVpxVP8.h"
#include "Video/Encoders/VideoEncoderLibVpxVP9.h"
#include "Video/Encoders/Configs/VideoEncoderConfigLibVpx.h"

// 解码器
#include "Video/Decoders/VideoDecoderLibVpxVP8.h"
#include "Video/Decoders/VideoDecoderLibVpxVP9.h"
#include "Video/Decoders/Configs/VideoDecoderConfigLibVpx.h"
```

### 基本用法 — VP8 编码

```cpp
// 创建 VP8 编码器（资源类型为 CPU）
TVideoEncoderLibVpxVP8<FVideoResourceCPU> Encoder;

// 配置编码参数
FVideoEncoderConfigLibVpx Config;
Config.Width = 1920;
Config.Height = 1080;
Config.Framerate = 30;
Config.TargetBitrate = 4000000;   // 4 Mbps
Config.MaxBitrate = 8000000;
Config.MinBitrate = 1000000;
Config.KeyframeInterval = 300;

// 打开编码器
TSharedRef<FAVDevice> Device = MakeShared<FAVDevice>();
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();
FAVResult Result = Encoder.Open(Device, Instance);

// 发送帧进行编码（Resource 为 FVideoResourceCPU 类型的帧数据）
FAVResult SendResult = Encoder.SendFrame(Resource, Timestamp, /*bForceKeyframe=*/false);

// 接收编码后的数据包
FVideoPacket Packet;
FAVResult RecvResult = Encoder.ReceivePacket(Packet);
```

### 基本用法 — VP9 解码

```cpp
// 创建 VP9 解码器
TVideoDecoderLibVpxVP9<FVideoResourceCPU> Decoder;

// 配置解码参数
FVideoDecoderConfigLibVpx DecConfig;
DecConfig.MaxOutputWidth = 1920;
DecConfig.MaxOutputHeight = 1080;

// 打开解码器
Decoder.Open(Device, Instance);

// 发送编码数据包
Decoder.SendPacket(Packet);

// 接收解码帧
TResolvableVideoResource<FVideoResourceCPU> OutResource;
Decoder.ReceiveFrame(OutResource);
```

### 进阶用法 — VP9 SVC 可伸缩编码

VP9 编码器支持 SVC（Scalable Video Coding），通过 `FVideoEncoderConfigLibVpx` 配置：

```cpp
FVideoEncoderConfigLibVpx Config;
Config.NumberOfSpatialLayers = 3;
Config.NumberOfTemporalLayers = 3;
Config.ScalabilityMode = EScalabilityMode::L3T3;  // 3 空间层 + 3 时间层
Config.bFlexibleMode = true;
Config.InterLayerPrediction = EInterLayerPrediction::On;

// 为每个空间层配置分辨率和码率
Config.SpatialLayers[0] = {640, 360, 60, 600000};
Config.SpatialLayers[1] = {1280, 720, 60, 1500000};
Config.SpatialLayers[2] = {1920, 1080, 60, 3000000};
```

## Demo 示例

### 最小 VP8 编码示例

```cpp
// MyVideoEncoder.h
#pragma once

#include "Video/Encoders/VideoEncoderLibVpxVP8.h"
#include "Video/Resources/VideoResourceCPU.h"

class FMyVideoEncoder
{
public:
    void Init();
    void EncodeFrame(const uint8* RawYUV, uint32 Width, uint32 Height);
    void Shutdown();

private:
    TVideoEncoderLibVpxVP8<FVideoResourceCPU> Encoder;
    uint32 FrameIndex = 0;
};

// MyVideoEncoder.cpp
#include "MyVideoEncoder.h"

void FMyVideoEncoder::Init()
{
    auto Device = MakeShared<FAVDevice>();
    auto Instance = MakeShared<FAVInstance>();
    
    Encoder.Open(Device, Instance);
    
    FVideoEncoderConfigLibVpx Config;
    Config.Width = 1280;
    Config.Height = 720;
    Config.Framerate = 30;
    Config.TargetBitrate = 2000000;
    Config.MaxBitrate = 4000000;
    Config.MinBitrate = 500000;
    Encoder.ApplyConfig();
}

void FMyVideoEncoder::EncodeFrame(const uint8* RawYUV, uint32 Width, uint32 Height)
{
    // 将原始 YUV 数据包装为 FVideoResourceCPU
    TSharedPtr<FVideoResourceCPU> Resource = MakeShared<FVideoResourceCPU>(RawYUV, Width, Height);
    
    Encoder.SendFrame(Resource, FrameIndex++);
    
    FVideoPacket Packet;
    while (Encoder.ReceivePacket(Packet) == FAVResult::Success)
    {
        // 处理编码后的 VP8 数据包
    }
}

void FMyVideoEncoder::Shutdown()
{
    Encoder.Close();
}
```

### Build.cs 依赖

```csharp
public class MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "AVCodecsCore",
            "LibVpxCodecs",
            "RenderCore",
            "Core"
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AVCodecsCore` | 编解码器框架核心，提供 `TVideoEncoder`/`TVideoDecoder` 基类和编解码器注册机制 |
| `LibVpx` | Google libvpx 第三方库的 UE 封装，提供 VP8/VP9 编解码的底层 C API |
| `RenderCore` | 渲染核心模块，提供视频资源相关的渲染支持 |
| `Engine` | UE 引擎核心（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase\<T\> | UE 核心 API 重构的批量适配，非功能性变更 |
| 2026-01-21 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 构建系统配置更新，非功能性变更 |
| 2026-01-20 | `0e6a982e` | [AVCodecs] Add: Support for iOS and Android | 为 AVCodecs 整体添加 iOS/Android 平台支持 |

### 维护评价

- **创建时间**: 2024-06-18（约 1.8 年前），是一个相对较新的 plugin
- **实验性标记**: `.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`
- **维护状态**: 最近更新在 2026 年 1-2 月，维护较为活跃
- **平台支持**: Win64、Linux、Mac（.uplugin 中 PlatformAllowList 限定）
- **注意事项**: 作为 Experimental plugin，API 可能随版本变化。该 plugin 不支持 Server 目标（TargetDenyList 包含 Server）
- **推荐**: 如果你需要 VP8/VP9 软编解码，这是 UE5 中唯一官方的 libvpx 集成方案，推荐在实验项目中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/LibVpxCodecs)
- [AVCodecsCore plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)（父框架）
- [LibVpx 第三方库模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/ThirdParty/libvpx)（libvpx 二进制依赖）
