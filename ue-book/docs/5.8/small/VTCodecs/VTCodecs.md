# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | VideoToolbox 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

---

## 用途

VTCodecs 插件将 Apple 的 VideoToolbox 框架集成到 UE 的 AVCodecs 体系中，为 macOS 平台提供硬件加速的视频编解码能力。  

VideoToolbox 是 Apple 原生框架，可调用 GPU/媒体引擎实现 H.264、H.265、VP9 的编解码。该插件通过封装 VideoToolbox 的 C API（`VTDecompressionSession`、`VTCompressionSession`、`CMSampleBuffer` 等），使得 UE 的 `TVideoDecoder` 和 `TVideoEncoder` 模板能够在 Metal 资源上工作。  

解决什么问题：  
- 在 macOS 上获得原生硬件加速视频编解码性能，避免纯软件编解码的 CPU 瓶颈  
- 与 UE 现有的 AVCodecs 生态（`AVExtension`、`VideoResource`、`FAPI`）无缝集成  
- 支持多平台编解码器统一接口，开发者可用相同的 `FVideoDecoder`/`FVideoEncoder` API 操作不同平台后端  

---

## 使用场景

- **实时视频通话/流媒体**：在 macOS 客户端从网络接收 H.264/H.265 流，硬件解码后送入 Metal 纹理渲染  
- **离线视频处理**：利用 VideoToolbox 编码器将 GPU 渲染帧（如录屏、回放）硬件编码为压缩视频  
- **跨平台多媒体播放器**：在 Mac 端统一使用 AVCodecs 框架，底层自动使用 VideoToolbox 而非软件解码器  

---

## 蓝图用法

该插件**不暴露任何蓝图可调用节点**（`UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`）。编解码器操作需要在 C++ 中完成。  

---

## C++ 用法

### 头文件引入

```cpp
#include "VT.h"
#include "Video/Decoders/VideoDecoderVT.h"
#include "Video/Encoders/VideoEncoderVT.h"
#include "Video/Decoders/Configs/VideoDecoderConfigVT.h"
#include "Video/Encoders/Configs/VideoEncoderConfigVT.h"
#include "Video/Util/NaluRewriter.h"
#include "Video/Util/VTSessionHelpers.h"
```

### 基本用法：硬件解码 H.264

```cpp
// 1. 创建解码器实例
TSharedRef<FAVDevice> Device = FAVDevice::GetDefault<EVideoContextType::Metal>();
TSharedRef<FAVInstance> Instance = Device->GetOrCreateInstance(EVideoContextType::Metal);

FVideoDecoderVT Decoder;
FAVResult Result = Decoder.Open(Device, Instance);
check(Result.IsSuccess());

// 2. 配置解码参数（从 H.264 SPS/PPS 生成 CMVideoFormatDescription）
FVideoDecoderConfigVT Config;
Config.Codec = kCMVideoCodecType_H264;
// 通常使用 NaluRewriter::H264AnnexBBufferToCMSampleBuffer 生成格式描述
// 或者通过 FAVExtension::TransformConfig 从标准配置转换
Result = Decoder.SetConfig(Config);
check(Result.IsSuccess());

// 3. 送入视频包（Annex B 格式 NAL 单元）
FVideoPacket Packet;
Packet.Data = ...;          // uint8* 指向 H.264 Annex B 数据
Packet.DataSize = ...;
Packet.Timestamp = ...;
Decoder.SendPacket(Packet);

// 4. 接收解码后的 Metal 纹理
TResolvableVideoResource<FVideoResourceMetal> OutResource;
Decoder.ReceiveFrame(OutResource);
// 此时 OutResource 持有 CVPixelBuffer 包装的 Metal 纹理
```
*来源：`Video/Decoders/VideoDecoderVT.h` 及 `Video/Util/NaluRewriter.h`*

### 基本用法：硬件编码 H.264

```cpp
// 1. 创建编码器
TVideoEncoderVT<FVideoResourceMetal> Encoder;
Encoder.Open(Device, Instance);

// 2. 配置编码参数
FVideoEncoderConfigVT Config;
Config.Width = 1920;
Config.Height = 1080;
Config.FrameRate = 30;
Config.TargetBitrate = 5000000; // 5 Mbps
Config.Codec = kCMVideoCodecType_H264;
Config.RateControlMode = ERateControlMode::CBR;
Encoder.ApplyConfig();

// 3. 送入 Metal 纹理帧
TSharedPtr<FVideoResourceMetal> FrameResource = ...; // 从渲染目标或视频源获取
Encoder.SendFrame(FrameResource, 0, false);

// 4. 取出编码后的视频包
FVideoPacket OutPacket;
Encoder.ReceivePacket(OutPacket);
// OutPacket.Data 包含 H.264 Annex B 格式的数据
```
*来源：`Video/Encoders/VideoEncoderVT.h`*

### 进阶用法：Annex B ↔ AVCC 转换（用于 RTP 传输）

```cpp
// 编码器输出为 AVCC 格式，需转为 Annex B 用于 RTP
CMSampleBufferRef AvccSample = ...;
TArray<uint8> AnnexBData;
NaluRewriter::H264CMSampleBufferToAnnexBBuffer(AvccSample, true, AnnexBData);

// 从 RTP 接收 Annex B 数据，转为 AVCC 格式供解码器
CMSampleBufferRef DecoderSample = nullptr;
NaluRewriter::H264AnnexBBufferToCMSampleBuffer(AnnexBData.GetData(), AnnexBData.Num(), VideoFormat, &DecoderSample, MemoryPool);
```
*来源：`Video/Util/NaluRewriter.h`*

---

## Demo 示例

以下为一个完整的最小测试程序（仅 C++，需在 macOS 平台编译）：

**MyVideoTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "VT.h"
#include "Video/VideoDecoder.h"
#include "Video/Decoders/VideoDecoderVT.h"
#include "Video/Decoders/Configs/VideoDecoderConfigVT.h"
#include "Video/Util/NaluRewriter.h"

class FMyVideoTest
{
public:
    static void RunTest();
};
```

**MyVideoTest.cpp**
```cpp
#include "MyVideoTest.h"
#include "Video/Resources/Metal/VideoResourceMetal.h"

void FMyVideoTest::RunTest()
{
    // 初始化 AVCodecs 环境
    TSharedRef<FAVDevice> Device = FAVDevice::GetDefault<EVideoContextType::Metal>();
    TSharedRef<FAVInstance> Instance = Device->GetOrCreateInstance(EVideoContextType::Metal);

    // 创建 VideoToolbox 解码器
    FVideoDecoderVT Decoder;
    FAVResult Result = Decoder.Open(Device, Instance);
    check(Result.IsSuccess());

    // 构造 H.264 SPS/PPS 并生成格式描述（示例：使用 NaluRewriter 从 Annex B 创建）
    const uint8 AnnexBData[] = {
        0x00, 0x00, 0x00, 0x01, 0x67, 0x42, 0x00, 0x1e, 0x99, 0xa0, 0x0b, 0x0b, 0xa0, 0x50, 0x00, 0x00,
        0x00, 0x01, 0x68, 0xce, 0x38, 0x80
    };
    CMVideoFormatDescriptionRef VideoFormat = NaluRewriter::CreateH264VideoFormatDescription(AnnexBData, sizeof(AnnexBData));
    check(VideoFormat != nullptr);
    
    // 配置解码器
    FVideoDecoderConfigVT Config;
    Config.Codec = kCMVideoCodecType_H264;
    Config.SetVideoFormat(VideoFormat);
    CFRelease(VideoFormat);
    
    Result = Decoder.SetConfig(Config);
    check(Result.IsSuccess());

    // 模拟送入一个 I 帧（简化：仅演示流程，实际需要完整 H.264 数据）
    FVideoPacket Packet;
    // Packet 填充略
    // Decoder.SendPacket(Packet);
    
    // 关闭
    Decoder.Close();
}
```
*此示例展示基本初始化和配置流程，完整运行需配合实际视频数据。*

---

## 模块依赖

**使用 VTCodecs 插件，需要在您的 `Build.cs` 中添加以下依赖（仅 macOS 平台）：**

| 模块 | 用途 |
|---|---|
| `AVCodecs` | AV 编解码基础设施（`FAVDevice`、`FAVInstance`、`TVideoDecoder` 等） |
| `AVCodecsRHI` | RHI 资源抽象（`VideoResourceMetal`） |
| `MetalRHI` | Metal 渲染接口，用于纹理互操作 |
| `RHI` | 通用渲染资源接口 |

**系统框架**：编译时自动链接 `VideoToolbox.framework` 和 `CoreMedia.framework`。

---

## 维护状态

### 近期更新

- 2026-02-27 `ae4a826a` 二次修复错误的查找替换
- 2026-02-27 `6759aa54` [回退] CL51314860
- 2026-02-27 `7723864b` 将 `FCoreDelegates::OnPostEngineInit` 迁移到 `GetOnPostEngineInit()` 修复注册顺序
- 2026-01-24 `e793e61e` 修复可移植工具链下的编译错误
- 2026-01-22 `ad8a0de1` 更新过时的 BuildVersionSettings

### 维护评价

- **创建时间**：2026-01-22，非常新的插件（不足 1 年）
- **近期更新**：最近 1 个月有多次提交，但主要是编译修复和基础设施迁移，**缺少功能性更新**（如新增 VP9 编码支持、优化解码队列等）
- **实验性**：`IsExperimentalVersion=true`，表明尚未稳定，可能 API 会变化
- **平台限制**：仅 macOS，不包含 iOS（与 `AudioToolbox` 不同）
- **已知问题**：需要 Apple Silicon 或 Intel Mac，且要求 macOS 10.13+；部分编解码格式（如 VP9 解码）依赖系统版本
- **推荐使用**：⚠️ 实验性阶段，如仅在 macOS 上进行硬件编解码且愿意跟进 API 变更，可以试用；不建议用于生产环境。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [VideoToolbox 官方文档](https://developer.apple.com/documentation/videotoolbox)
- [AVCodecs 官方文档（UE 内部）](https://docs.unrealengine.com/5.8/API/Plugins/AVCodecs/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs/Tests)