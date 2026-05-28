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

AVCodecsCore 是一个**音视频编解码器框架**，它本身不提供任何具体的编码/解码实现，而是为硬件和软件编解码器提供统一的基础设施。类似于 Unreal 的 `FAudioDevice` 或 `FRenderCommandFence` 抽象了底层音频/渲染系统，AVCodecsCore 抽象了底层编解码器系统。

该插件的核心价值：

1. **统一编码器/解码器接口**：通过模板化设计 `TAVCoder` → `TVideoEncoder` / `TVideoDecoder` / `TAudioEncoder` / `TAudioDecoder`，所有编解码器实现共享相同的工作流（Open → SendFrame → ReceivePacket）
2. **工厂注册系统**：编解码器按设备（GPU/CPU）、资源类型（D3D12/Vulkan/Metal）、配置类型（H264/H265）自动注册和匹配，调用方无需关心底层具体实现
3. **多平台资源抽象**：统一管理 D3D11、D3D12、Vulkan、Metal、CPU 的视频资源，支持跨 API 资源转换
4. **码流解析工具**：内置 H.264、H.265、VP8、VP9 码流解析器和参数集（SPS/PPS/VPS）结构体
5. **SVC（可伸缩视频编码）**：提供完整的空间/时间可伸缩编码框架，支持 WebRTC 风格的分层编码

**为什么存在？** Epic 需要一个不绑定特定硬件厂商的编解码器抽象层。不同厂商的编解码器插件（如 NVIDIA 的 NVENC）只需注册到这个框架，即可被上层系统（如 Pixel Streaming、Media Framework）统一调用。

## 使用场景

- 你在做 **Pixel Streaming**，需要将游戏画面实时编码为 H.264/H.265 流 → 使用此框架的 `TVideoEncoder`
- 你在做 **视频录制/导出**功能，需要硬件加速编码 → 注册到工厂系统的编码器会自动匹配可用硬件
- 你在做 **视频播放/解码**功能，需要处理 H.264/H.265 码流 → 使用 `TVideoDecoder`，框架自动创建合适的解码器
- 你需要解析 H.264 SPS/PPS 或 H.265 VPS/SPS/PPS → 使用 `CodecUtilsH264` / `CodecUtilsH265` 工具
- 你需要实现 **WebRTC SVC** 可伸缩编码 → 使用 `FScalabilityStructureFullSvc` 等结构
- 你需要在 D3D11、D3D12、Vulkan、Metal 之间共享视频资源 → 使用 `FVideoResource*` 资源系统
- 你需要自定义音频编码（如 AAC）→ 使用 `TAudioEncoder` 框架

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    TAVCoder<TDomain>                         │
│              (泛型编码器/解码器基类 + 工厂)                    │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ TVideoEncoder│ TVideoDecoder│ TAudioEncoder│ TAudioDecoder  │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                     FAVResource                              │
│          (设备资源抽象：D3D11/12/Vulkan/Metal/CPU)            │
├─────────────────────────────────────────────────────────────┤
│     FAVDevice (物理设备)    │    FAVInstance (配置实例)       │
├─────────────────────────────┴───────────────────────────────┤
│                  FAVExtension (类型转换)                      │
│                  FAVResult (错误处理)                         │
│                  FTypeID / TTypeMap (类型擦除)                │
└─────────────────────────────────────────────────────────────┘
```

## 蓝图用法

此插件是纯 C++ 框架，**不暴露蓝图接口**。所有 API 均为 C++ 模板和类接口。

## C++ 用法

### 核心概念

#### 1. 编码器/解码器工厂系统

该框架的核心是基于工厂模式的编解码器注册系统。编解码器按三个维度注册：
- **Domain（领域）**：`TVideoEncoder` / `TVideoDecoder` / `TAudioEncoder` / `TAudioDecoder`
- **Resource（资源类型）**：`FVideoResourceD3D12` / `FVideoResourceVulkan` / `FVideoResourceCPU` 等
- **Config（配置类型）**：`FVideoEncoderConfig` / `FVideoDecoderConfigH264` / `FVideoDecoderConfigH265` 等

创建编码器时，框架遍历所有已注册的工厂，找到兼容的实现并实例化。

#### 2. 配置管理（Pending/Applied 模式）

配置分为两阶段：
- **Pending Config**：通过 `SetPendingConfig()` / `EditPendingConfig()` 设置，存储在 `FAVInstance` 中
- **Applied Config**：通过 `ApplyConfig()` 将 Pending 配置应用到硬件，存储在 `AppliedConfig` 中

这种设计允许批量修改多个配置参数后一次性应用，避免频繁的硬件状态切换。

### 基本用法：创建视频编码器

```cpp
// 来源: Public/Video/VideoEncoder.h
#include "Video/VideoEncoder.h"
#include "AVDevice.h"
#include "AVInstance.h"

// 1. 获取硬件设备
TSharedRef<FAVDevice> Device = FAVDevice::GetHardwareDevice(0);

// 2. 创建实例并配置编码参数
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

// 3. 创建编码器（框架自动匹配可用的硬件编码器）
//    TResource = FVideoResourceD3D12 表示输入资源类型
//    TConfig = FVideoEncoderConfig 表示配置类型
TSharedPtr<TVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfig>> Encoder =
    TVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfig>::Create(Device, Instance);

if (!Encoder.IsValid())
{
    // 没有找到兼容的编码器（可能缺少厂商插件如 NVCodec）
    UE_LOG(LogAVCodecs, Error, TEXT("No compatible encoder found"));
    return;
}

// 4. 配置编码参数
FVideoEncoderConfig& Config = Encoder->EditPendingConfig();
Config.Width = 1920;
Config.Height = 1080;
Config.TargetBitrate = 5000000;  // 5 Mbps
Config.TargetFramerate = 60;
Config.RateControlMode = ERateControlMode::CBR;
Config.KeyframeInterval = 60;

// 5. 应用配置
Encoder->ApplyConfig();

// 6. 编码帧
TSharedPtr<FVideoResourceD3D12> FrameResource = /* 从渲染管线获取 */;
FAVResult Result = Encoder->SendFrame(FrameResource, Timestamp, /*bForceKeyframe=*/false);
if (Result.IsSuccess())
{
    // 7. 收取编码后的数据包
    FVideoPacket Packet;
    while (Encoder->ReceivePacket(Packet).IsSuccess())
    {
        // 处理编码后的数据包
        ProcessEncodedPacket(Packet);
    }
}
```

### 基本用法：创建视频解码器

```cpp
// 来源: Public/Video/VideoDecoder.h
#include "Video/VideoDecoder.h"
#include "AVDevice.h"

TSharedRef<FAVDevice> Device = FAVDevice::GetHardwareDevice(0);
TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();

// 创建解码器（指定输出资源类型和配置类型）
auto Decoder = TVideoDecoder<FVideoResourceD3D12, FVideoDecoderConfigH264>::Create(
    Device, Instance);

if (!Decoder.IsValid())
{
    UE_LOG(LogAVCodecs, Error, TEXT("No compatible H264 decoder found"));
    return;
}

// 发送编码数据包
FVideoPacket EncodedPacket = /* 从网络/文件获取 */;
FAVResult Result = Decoder->SendPacket(EncodedPacket);

// 接收解码帧（延迟资源解析）
TResolvableVideoResource<FVideoResourceD3D12> OutputFrame;
while (Decoder->ReceiveFrame(OutputFrame).IsSuccess())
{
    if (OutputFrame.Resolve(Device, FVideoDescriptor(EVideoFormat::BGRA, 1920, 1080)))
    {
        TSharedPtr<FVideoResourceD3D12> Frame = OutputFrame.Get();
        // 使用解码后的帧
    }
}
```

### 进阶用法：检查编码器支持

```cpp
// 来源: Public/AVCoder.h

// 检查是否有任何编码器支持指定的资源和配置类型
bool bSupported = TVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfig>::IsSupported();

// 检查特定设备上是否有兼容的编码器
bool bDeviceSupported = TVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfig>::IsSupported(
    Device, Instance);

// 获取兼容编码器数量
int32 Count = TVideoEncoder<FVideoResourceD3D12, FVideoEncoderConfig>::CountSupported(
    Device, Instance);
```

### 进阶用法：H.264 码流解析

```cpp
// 来源: Public/Video/CodecUtils/CodecUtilsH264.h, Public/Video/Decoders/Configs/VideoDecoderConfigH264.h
#include "Video/CodecUtils/CodecUtilsH264.h"
#include "Video/Decoders/Configs/VideoDecoderConfigH264.h"

// 解析 H.264 配置
FVideoDecoderConfigH264 H264Config;
TArray<UE::AVCodecCore::H264::Slice_t> Slices;

FAVResult ParseResult = H264Config.Parse(Packet, Slices);
if (ParseResult.IsSuccess())
{
    // 访问 SPS 参数
    for (auto& [ID, SPS] : H264Config.SPS)
    {
        UE::AVCodecCore::H264::EH264Profile Profile = SPS.GetProfile();
        uint32 Width = (SPS.pic_width_in_mbs_minus1 + 1) * 16;
        uint32 Height = (SPS.pic_height_in_map_units_minus1 + 1) * 16 * (2 - SPS.frame_mbs_only_flag);
        
        UE_LOG(LogAVCodecs, Log, TEXT("Profile: %d, Resolution: %dx%d"), 
            (int)Profile, Width, Height);
    }
    
    // 获取最后一个 Slice 的 QP 值
    TOptional<int> LastQP = H264Config.GetLastSliceQP(Slices);
}

// 直接查找 NAL 单元
TArray<UE::AVCodecCore::H264::FNaluH264> Nalus;
FAVResult FindResult = UE::AVCodecCore::H264::FindNALUs(Packet, Nalus);
for (auto& Nalu : Nalus)
{
    switch (Nalu.Type)
    {
    case UE::AVCodecCore::H264::ENaluType::SequenceParameterSet:
        // 处理 SPS
        break;
    case UE::AVCodecCore::H264::ENaluType::PictureParameterSet:
        // 处理 PPS
        break;
    case UE::AVCodecCore::H264::ENaluType::SliceIdrPicture:
        // 处理 IDR 帧
        break;
    }
}
```

### 进阶用法：流式解码器（自动检测编解码器）

```cpp
// 来源: Public/Video/Decoders/StreamVideoDecoder.h
#include "Video/Decoders/StreamVideoDecoder.h"

// TStreamVideoDecoder 会自动检测码流格式（H.264 或 H.265），
// 并在收到第一个包时自动创建对应的子解码器
auto StreamDecoder = MakeShared<TStreamVideoDecoder<FVideoResourceCPU>>();
StreamDecoder->Open(Device, Instance);

// 发送任意 H.264 或 H.265 数据包，解码器自动适配
FVideoPacket Packet = /* 任意格式的码流数据 */;
FAVResult Result = StreamDecoder->SendPacket(Packet);

if (StreamDecoder->IsInitialized())
{
    // 解码器已根据码流格式自动创建
    TResolvableVideoResource<FVideoResourceCPU> Frame;
    StreamDecoder->ReceiveFrame(Frame);
}
```

### 进阶用法：使用 SVC 可伸缩编码

```cpp
// 来源: Public/Video/Encoders/SVC/ScalabilityStructureFull.h, 
//       Public/Video/Encoders/SVC/ScalableVideoController.h
#include "Video/Encoders/SVC/ScalabilityStructureFull.h"
#include "Video/Encoders/SVC/VideoBitrateAllocatorSVC.h"

// 创建 2 层空间 + 2 层时间的可伸缩编码控制器
auto Controller = MakeShared<FScalabilityStructureL2T2>();

// 获取流配置
FScalableVideoController::FStreamLayersConfig Config = Controller->StreamConfig();
// Config.NumSpatialLayers = 2
// Config.NumTemporalLayers = 2
// Config.ScalingFactors[0] = {1, 1}  // 原始分辨率
// Config.ScalingFactors[1] = {1, 2}  // 半分辨率

// 获取依赖结构（用于 RTP 依赖描述符扩展）
FFrameDependencyStructure DepStructure = Controller->DependencyStructure();

// 获取下一帧的编码配置
TArray<FScalableVideoController::FLayerFrameConfig> FrameConfigs = 
    Controller->NextFrameConfig(false);

for (auto& FrameConfig : FrameConfigs)
{
    int32 SpatialId = FrameConfig.GetSpatialId();
    int32 TemporalId = FrameConfig.GetTemporalId();
    bool bKeyframe = FrameConfig.GetIsKeyframe();
    
    // 使用 FrameConfig 编码对应层...
}

// 编码完成后通知控制器
FGenericFrameInfo GenericInfo = Controller->OnEncodeDone(FrameConfigs[0]);

// 更新比特率分配
FVideoBitrateAllocation BitrateAllocation;
BitrateAllocation.SetBitrate(0, 0, 2000000);  // 空间层 0, 时间层 0: 2Mbps
BitrateAllocation.SetBitrate(1, 0, 4000000);  // 空间层 1, 时间层 0: 4Mbps
Controller->OnRatesUpdated(BitrateAllocation);
```

### 进阶用法：跨平台资源管理

```cpp
// 来源: Public/Video/Resources/D3D/VideoResourceD3D.h, 
//       Public/Video/Resources/Vulkan/VideoResourceVulkan.h,
//       Public/Video/Resources/Metal/VideoResourceMetal.h

// D3D11 资源
auto D3D11Device = /* 获取 ID3D11Device */;
auto D3D11Context = MakeShared<FVideoContextD3D11>(D3D11Device);
auto D3D11Resource = MakeShared<FVideoResourceD3D11>(
    Device, D3D11Texture, FAVLayout(0, TextureSize, TextureStride));

// D3D12 资源（支持共享句柄和 Fence 同步）
FVideoResourceD3D12::FRawD3D12 RawD3D12;
RawD3D12.D3DResource = D3D12Resource;
RawD3D12.D3DFence = D3D12Fence;
RawD3D12.FenceValue = CurrentFenceValue;
auto D3D12Resource = MakeShared<FVideoResourceD3D12>(Device, RawD3D12, Layout);

// Vulkan 资源
auto VulkanContext = MakeShared<FVideoContextVulkan>(
    VkInstance, VkDevice, VkPhysicalDevice, vkGetDeviceProcAddrFunc);
auto VulkanResource = MakeShared<FVideoResourceVulkan>(
    Device, VkDeviceMemory, Layout, Descriptor);

// CPU 资源
auto CPUResource = MakeShared<FVideoResourceCPU>(
    Device, RawDataPtr, Layout, 
    FVideoDescriptor(EVideoFormat::BGRA, 1920, 1080));
```

### Demo 示例

```cpp
// AvCodecsDemo.h
#pragma once
#include "CoreMinimal.h"

class FAvCodecsDemo
{
public:
    static void RunEncodingDemo();
};
```

```cpp
// AvCodecsDemo.cpp
#include "AvCodecsDemo.h"
#include "AVDevice.h"
#include "AVInstance.h"
#include "Video/VideoEncoder.h"
#include "Video/VideoResource.h"
#include "Video/Resources/VideoResourceCPU.h"

void FAvCodecsDemo::RunEncodingDemo()
{
    // 获取硬件设备
    TSharedRef<FAVDevice> Device = FAVDevice::GetHardwareDevice(0);
    
    // 创建实例并配置
    TSharedRef<FAVInstance> Instance = MakeShared<FAVInstance>();
    
    // 使用类型擦除的编码器接口尝试创建
    TSharedPtr<FVideoEncoder> Encoder = 
        FVideoEncoder::Create<FVideoResourceCPU, FVideoEncoderConfig>(Device, Instance);
    
    if (!Encoder.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No compatible encoder found. "
            "Ensure a vendor codec plugin (e.g., NVCodec) is enabled."));
        return;
    }
    
    // 配置
    FVideoEncoderConfig Config;
    Config.Width = 1280;
    Config.Height = 720;
    Config.TargetBitrate = 3000000;
    Config.TargetFramerate = 30;
    Config.RateControlMode = ERateControlMode::CBR;
    Encoder->SetMinimalConfig(Config);
    
    // 模拟编码
    for (uint32 FrameIndex = 0; FrameIndex < 10; ++FrameIndex)
    {
        // 创建模拟帧资源（实际中从渲染管线获取）
        TSharedPtr<uint8> FrameData = MakeShared<uint8>(/* ... */);
        auto FrameResource = MakeShared<FVideoResourceCPU>(
            Device, FrameData,
            FAVLayout(0, 1280 * 720 * 4, 1280 * 4),
            FVideoDescriptor(EVideoFormat::BGRA, 1280, 720));
        
        // 发送帧
        Encoder->SendFrame(FrameResource, FrameIndex * 33); // ~30fps
        
        // 收取编码包
        FVideoPacket Packet;
        while (Encoder->ReceivePacket(Packet).IsSuccess())
        {
            UE_LOG(LogTemp, Log, TEXT("Encoded packet: %lld bytes, QP=%u, Keyframe=%d"),
                Packet.DataSize, Packet.QP, Packet.bIsKeyframe);
        }
    }
    
    // 刷新并收取剩余包
    TArray<FVideoPacket> FinalPackets;
    Encoder->FlushAndReceivePackets(FinalPackets);
}
```

## 模块依赖

### AVCodecsCore

| 模块 | 用途 |
|---|---|
| `RHI` | 渲染硬件接口抽象，用于跨平台资源管理 |
| `MediaUtils` | 媒体工具函数 |

### AVCodecsCoreRHI

依赖与 AVCodecsCore 相同，额外加载阶段更早（PostConfigInit），以确保 RHI 上下文在其他模块之前初始化。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 间保持一致 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致的乱码输出问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位格式说明符与 64 位参数不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

### 维护评价

- **活跃维护中**：最近的更新（2026 年 5 月）集中在编译器兼容性和代码质量改进，表明该插件正在向更稳定的状态演进
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，API 可能在未来版本中发生变化
- **功能完整**：框架设计完整，涵盖了编解码器抽象的方方面面（工厂模式、资源管理、配置管理、错误处理、SVC）
- **依赖厂商插件**：作为框架层，实际的编解码能力依赖于第三方厂商插件（如 NVCodec、AMFCodec 等），单独启用此插件无法完成实际编解码
- **推荐度**：如果你需要在 UE5 中进行硬件加速音视频编解码，这是唯一的官方框架。但由于实验性状态，建议密切关注 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- 官方文档：无