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

AVCodecsCore 是一个**音视频编解码框架**，而非具体的编解码器实现。它解决的核心问题是：为 Unreal Engine 提供一套统一的、可扩展的音视频编解码抽象层，使不同的硬件/软件编解码器（如 NVENC、Media Foundation、VideoToolbox 等）能通过统一接口接入引擎。

这个插件之所以存在，是因为：

- **抽象工厂模式**：通过 `TAVCoder` 模板基类和工厂注册机制，允许第三方编解码器插件（如 `NVCodec`）注册自己的实现，核心框架按资源类型、配置类型和设备兼容性自动选择最合适的实现
- **多 GPU 后端支持**：提供 D3D11、D3D12、Vulkan、Metal、CPU 五种后端的资源抽象，实现跨平台资源管理
- **码流工具**：内置 H.264、H.265、VP8、VP9 的比特流解析工具（SPS/PPS/VPS 等参数集解析）
- **SVC（可伸缩视频编码）**：提供多种空间/时间层可伸缩性结构的完整实现，用于 WebRTC 场景
- **类型安全的资源转换**：通过 `FAVExtension` 实现不同资源类型间的安全转换

**注意**：这是一个框架/接口层。要实际使用编解码功能，你还需要启用具体的实现插件（如 NVENC、MediaFoundation 等）。

## 使用场景

- 你需要在应用中进行视频编码（如录制、推流）→ 使用 `TVideoEncoder` 接口，由具体实现插件提供编码器
- 你需要解码 H.264/H.265 视频流 → 使用 `TStreamVideoDecoder` 可自动检测码流格式并创建对应解码器
- 你需要多 GPU 后端的纹理/缓冲区统一管理 → 使用 `FVideoResourceD3D11`、`FVideoResourceVulkan` 等平台资源
- 你需要可伸缩视频编码（SVC）用于 WebRTC → 使用 `FScalableVideoController` 及其各种结构实现
- 你需要解析 H.264/H.265 码流的参数集 → 使用 `CodecUtilsH264`/`CodecUtilsH265` 中的 `ParseSPS`、`ParseVPS` 等函数
- 你需要音频编解码 → 使用 `TAudioEncoder`/`TAudioDecoder` 接口

## 蓝图用法

此插件主要面向 C++ 开发者，公开的蓝图 API 极少。枚举类型 `EH264Profile`、`EScalabilityMode`、`ERateControlMode`、`EMultipassMode` 等使用了 `UENUM()` 标记，在蓝图中可见但仅用于配置。

## C++ 用法

### 头文件引入

```cpp
// 核心框架
#include "AVCoder.h"
#include "AVResult.h"
#include "AVDevice.h"
#include "AVInstance.h"
#include "AVResource.h"
#include "AVExtension.h"

// 视频编解码
#include "Video/VideoEncoder.h"
#include "Video/VideoDecoder.h"
#include "Video/VideoResource.h"
#include "Video/VideoPacket.h"

// 音频编解码
#include "Audio/AudioEncoder.h"
#include "Audio/AudioDecoder.h"
#include "Audio/AudioResource.h"

// 平台资源（按需）
#include "Video/Resources/D3D/VideoResourceD3D.h"
#include "Video/Resources/Vulkan/VideoResourceVulkan.h"
#include "Video/Resources/Metal/VideoResourceMetal.h"
#include "Video/Resources/VideoResourceCPU.h"

// 码流工具（按需）
#include "Video/CodecUtils/CodecUtilsH264.h"
#include "Video/CodecUtils/CodecUtilsH265.h"
```

### 基本用法 — 使用工厂创建编码器

```cpp
// 获取硬件设备（通常是 GPU 0）
TSharedRef<FAVDevice> Device = FAVDevice::GetHardwareDevice(0);

// 创建实例并配置
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();
FVideoEncoderConfig Config;
Config.Width = 1920;
Config.Height = 1080;
Config.TargetBitrate = 5000000;
Config.TargetFramerate = 60;
Config.RateControlMode = ERateControlMode::CBR;
Instance->Set(Config);

// 检查是否有兼容的编码器可用
bool bSupported = FVideoEncoder::IsSupported<FVideoResourceD3D12, FVideoEncoderConfig>(Device, Instance);

// 创建编码器（自动选择最合适的实现）
TSharedPtr<FVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfig>> Encoder =
    FVideoEncoder::Create<FVideoResourceD3D12, FVideoEncoderConfig>(Device, Instance);

if (Encoder.IsValid())
{
    // 发送帧进行编码
    FAVResult Result = Encoder->SendFrame(MyVideoResource, Timestamp, bForceKeyframe);
    
    // 接收编码后的包
    FVideoPacket Packet;
    if (Encoder->ReceivePacket(Packet).IsSuccess())
    {
        // 处理编码后的 Packet
    }
}
```

*来源：基于 `Public/Video/VideoEncoder.h` 和 `Public/AVCoder.h` 中 `TAVCoder::Create` 模板*

### 基本用法 — 使用流式解码器自动检测码流

```cpp
// TStreamVideoDecoder 可自动识别 H.264/H.265 码流并创建对应解码器
TSharedRef<FAVDevice> Device = FAVDevice::GetHardwareDevice(0);
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

auto StreamDecoder = MakeShared<TStreamVideoDecoder<FVideoResourceD3D12>>();
StreamDecoder->Open(Device, Instance);

// 发送码流包，解码器会自动检测格式并初始化
FVideoPacket IncomingPacket(/* data, size, timestamp, index, qp, keyframe */);
FAVResult Result = StreamDecoder->SendPacket(IncomingPacket);

// 接收解码后的帧
TResolvableVideoResource<FVideoResourceD3D12> OutResource;
if (StreamDecoder->ReceiveFrame(OutResource).IsSuccess())
{
    // 使用解码后的资源
}
```

*来源：`Public/Video/Decoders/StreamVideoDecoder.h`*

### 基本用法 — 音频编码

```cpp
TSharedRef<FAVDevice> Device = FAVDevice::GetSoftwareDevice();
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

FAudioEncoderConfig AudioConfig;
AudioConfig.Bitrate = 16000 * 8;  // 128kbps
AudioConfig.Samplerate = 44100;
AudioConfig.NumChannels = 2;
Instance->Set(AudioConfig);

// 创建音频编码器
TSharedPtr<FAudioEncoder<FAudioResourceCPU, FAudioEncoderConfig>> AudioEncoder =
    FAudioEncoder::Create<FAudioResourceCPU, FAudioEncoderConfig>(Device, Instance);

if (AudioEncoder.IsValid())
{
    // 发送音频帧
    AudioEncoder->SendFrame(MyAudioResource, Timestamp);
    
    // 接收编码包
    FAudioPacket AudioPacket;
    if (AudioEncoder->ReceivePacket(AudioPacket).IsSuccess())
    {
        // 处理编码后的音频包
    }
}
```

*来源：`Public/Audio/AudioEncoder.h`*

### 进阶用法 — 注册自定义编解码器实现

```cpp
// 假设你正在实现一个 NVENC 编码器插件
// 需要在模块启动时注册到工厂

#include "AVCoder.h"
#include "Video/VideoEncoder.h"

class FVideoEncoderNVENC : public TVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfigNVENC>
{
public:
    virtual FAVResult SendFrame(TSharedPtr<FVideoResourceD3D12> const& Resource, uint32 Timestamp, bool bForceKeyframe) override;
    virtual FAVResult ReceivePacket(FVideoPacket& OutPacket) override;
    // ...
};

// 在模块 StartupModule 中注册
void FNVENCModule::StartupModule()
{
    // 方法 1：手动注册单个配置
    TVideoEncoder<>::Register<FVideoEncoderNVENC, FVideoResourceD3D12, FVideoEncoderConfigNVENC>(
        [](TSharedRef<FAVDevice> const& Device, TSharedRef<FAVInstance> const& Instance) -> bool
        {
            // 检查设备是否支持 NVENC
            return Device->HasContext<FVideoContextD3D11>() || Device->HasContext<FVideoContextD3D12>();
        }
    );
    
    // 方法 2：使用模板排列组合注册（适用于多种资源/配置组合）
    TVideoEncoder<>::RegisterPermutationsOf<FVideoEncoderNVENC>
        ::With<FVideoResourceD3D11, FVideoResourceD3D12>
        ::And<FVideoEncoderConfig, FVideoEncoderConfigNVENC>();
}
```

*来源：`Public/AVCoder.h` 中 `TAVCoder::Register` 和 `RegisterPermutationsOf`*

### 进阶用法 — 使用 FAVResult 错误处理

```cpp
// FAVResult 会自动在未处理时记录日志
// 可以通过调用 .Handle() 标记为已处理以避免重复日志
FAVResult Result = Encoder->SendFrame(Resource, Timestamp);
if (Result.IsNotSuccess())
{
    // 手动处理错误
    UE_LOG(LogAVCodecs, Warning, TEXT("Encoding failed: %s"), *Result.ToString());
    Result.Handle();  // 标记为已处理，析构时不再自动记录
    
    if (Result.IsError())  // 范围判断
    {
        // 处理错误
    }
    else if (Result.IsPending())
    {
        // 需要更多输入
    }
}

// 使用 TAVResult 返回值和错误码
TAVResult<FVideoPacket> PacketResult = Encoder->ReceivePacket();
if (PacketResult.IsSuccess())
{
    FVideoPacket Packet = PacketResult.ReturnValue;  // 自动转换
}
```

*来源：`Public/AVResult.h`*

### 进阶用法 — 解析 H.264 参数集

```cpp
#include "Video/CodecUtils/CodecUtilsH264.h"

// 解析 H.264 码流中的 NAL 单元
TArray<UE::AVCodecCore::H264::FNaluH264> Nalus;
FAVResult FindResult = UE::AVCodecCore::H264::FindNALUs(InPacket, Nalus);

// 解析 SPS
TMap<uint32, UE::AVCodecCore::H264::SPS_t> MapSPS;
for (auto const& Nalu : Nalus)
{
    if (Nalu.Type == UE::AVCodecCore::H264::ENaluType::SequenceParameterSet)
    {
        FBitstreamReader Reader(Nalu.Data, Nalu.Size);
        UE::AVCodecCore::H264::ParseSPS(Reader, Nalu, MapSPS);
    }
}

// 使用解析结果
for (auto const& [Id, SPS] : MapSPS)
{
    EH264Profile Profile = SPS.GetProfile();
    uint32 Width = (SPS.pic_width_in_mbs_minus1 + 1) * 16;
    uint32 Height = (SPS.pic_height_in_map_units_minus1 + 1) * 16;
}
```

*来源：`Public/Video/CodecUtils/CodecUtilsH264.h`*

## Demo 示例

一个完整的最小示例：创建 CPU 视频资源并使用音频编码器。

**MyAVExample.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "AVDevice.h"
#include "AVInstance.h"
#include "Audio/AudioEncoder.h"
#include "Audio/AudioResource.h"
#include "Audio/Resources/AudioResourceCPU.h"

class FMyAVExample
{
public:
    void Init();
    void EncodeAudioFrame(const float* AudioData, uint32 NumSamples, uint32 Timestamp);
    void FlushAndFinalize();

private:
    TSharedPtr<FAudioEncoder<FAudioResourceCPU, FAudioEncoderConfig>> Encoder;
    TSharedPtr<FAudioResourceCPU> AudioResource;
};
```

**MyAVExample.cpp**

```cpp
#include "MyAVExample.h"

void FMyAVExample::Init()
{
    TSharedRef<FAVDevice> Device = FAVDevice::GetSoftwareDevice();
    TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

    FAudioEncoderConfig Config;
    Config.Bitrate = 20000 * 8;  // 160kbps
    Config.Samplerate = 44100;
    Config.NumChannels = 2;
    Instance->Set(Config);

    Encoder = FAudioEncoder::Create<FAudioResourceCPU, FAudioEncoderConfig>(Device, Instance);
}

void FMyAVExample::EncodeAudioFrame(const float* AudioData, uint32 NumSamples, uint32 Timestamp)
{
    if (!Encoder.IsValid() || !Encoder->IsOpen())
    {
        return;
    }

    // 创建音频资源
    FAVLayout Layout;
    Layout.Size = NumSamples * sizeof(float);
    FAudioDescriptor Descriptor(NumSamples, 1.0f / 44100.0f);

    TSharedRef<FAVDevice> Device = FAVDevice::GetSoftwareDevice();
    TSharedPtr<float> DataCopy(new float[NumSamples], [](float* p) { delete[] p; });
    FMemory::Memcpy(DataCopy.Get(), AudioData, NumSamples * sizeof(float));

    auto Resource = MakeShared<FAudioResourceCPU>(Device, DataCopy, Layout, Descriptor);
    Encoder->SendFrame(Resource, Timestamp);

    // 接收编码包
    FAudioPacket Packet;
    while (Encoder->ReceivePacket(Packet).IsSuccess())
    {
        // 处理编码后的音频数据
        if (!Packet.IsEmpty())
        {
            TArrayView64<uint8> Data = Packet.GetData();
            // ... 发送或保存
        }
    }
}

void FMyAVExample::FlushAndFinalize()
{
    if (Encoder.IsValid())
    {
        TArray<FAudioPacket> RemainingPackets;
        Encoder->FlushAndReceivePackets(RemainingPackets);
        
        for (auto& Packet : RemainingPackets)
        {
            // 处理剩余包
        }
        
        Encoder->Close();
    }
}
```

## 模块依赖

AVCodecsCoreRHI 模块负责平台图形 API 集成，AVCodecsCore 提供核心抽象。根据头文件中的 `#include` 分析，使用者需要的模块依赖：

| 模块 | 用途 |
|---|---|
| `RHI` | 渲染硬件接口，用于纹理格式枚举（`EPixelFormat`）等 |
| `MediaUtils` | 媒体工具函数（音频/视频格式相关） |

> 如果你需要使用 D3D/Vulkan/Metal 平台资源，还需在 `PublicDependencyModuleNames` 中添加对应平台的模块。核心框架本身仅依赖标准引擎模块（Core、CoreUObject、Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 之间保持可移植性 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数位宽不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |

### 维护评价

- **创建时间**：2023 年 1 月，约 3 年前，属于较新的插件
- **近期活跃度**：近期更新集中在编译警告修复和日志宏迁移，属于维护性修复而非功能性更新
- **实验状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明 Epic 仍在积极开发但尚未认为 API 稳定
- **平台支持**：支持 Win64、Linux、Mac、Android、iOS 五大平台
- **推荐程度**：⚠️ **谨慎使用**。这是一个实验性框架，API 可能发生重大变更。适合需要统一音视频编解码抽象层的项目，但不建议在生产环境中直接依赖。如果你只需要特定编解码器，建议关注对应的实现插件（如 NVCodec）是否有独立文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)