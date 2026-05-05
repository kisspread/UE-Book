# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 分类 | Codecs |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AMFCodecs (Runtime), AMFCodecsRHI (Runtime) |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途

AMFCodecs 将 AMD 的 [Advanced Media Framework (AMF)](https://github.com/GPUOpen-LibrariesAndSDKs/AMF) SDK 集成到 UE5 的 AVCodecs 框架中，提供基于 AMD GPU 硬件加速的视频编码和解码能力。

具体来说，它通过 AMF SDK 访问 AMD 显卡上的专用硬件编解码器：
- **编码器**：使用 AMF 的 VCE (Video Coding Engine) 组件，支持 H.264/AVC 硬件编码
- **解码器**：使用 AMF 的 UVD (Unified Video Decoder) 组件，支持 H.264/AVC 和 H.265/HEVC 硬件解码

该插件是 AVCodecs 框架的后端实现之一，与 NvCodecs (NVIDIA)、VideoToolbox (Apple) 并列，为 AMD GPU 用户提供硬件编解码支持。**当前主要用于 Pixel Streaming 场景**，在 AMD GPU 上实现低延迟视频编码。

## 使用场景

- 你在做 Pixel Streaming，运行环境是 AMD GPU → 启用 AMFCodecs 获得硬件加速编码
- 你需要在 AMD GPU 上进行低延迟 H.264 视频编码 → 使用 AMF 编码器后端
- 你的应用需要解码 H.264/H.265 视频流且运行在 AMD 硬件上 → 使用 AMF 解码器后端（注意：解码器当前被禁用，见下方限制）

## 蓝图用法

**无蓝图 API。** AMFCodecs 是纯 C++ 编解码器后端，不暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它通过 AVCodecs 框架的注册机制自动被上层系统（如 Pixel Streaming）使用。

## C++ 用法

AMFCodecs 不提供直接的用户级 API。它是 AVCodecs 框架的编解码器后端，通过 `FVideoEncoder::RegisterPermutationsOf` 注册编码器/解码器排列组合，上层代码通过 AVCodecs 的统一接口（`TVideoEncoder` / `TVideoDecoder`）使用。

### 头文件引入

```cpp
// 编码器
#include "Video/Encoders/VideoEncoderAMF.h"
#include "Video/Encoders/Configs/VideoEncoderConfigAMF.h"

// 解码器
#include "Video/Decoders/VideoDecoderAMF.h"
#include "Video/Decoders/Configs/VideoDecoderConfigAMF.h"

// AMF 核心
#include "AMF.h"
```

### 基本用法 — 检查 AMF 可用性

```cpp
// 检查当前系统是否支持 AMF（需要 AMD GPU + AMF DLL）
// 来源: AMFCodecsRHIModule.cpp
if (FAPI::Get<FAMF>().IsValid())
{
    // AMF 可用，编码器/解码器已自动注册
}
```

### 基本用法 — 编码器配置

```cpp
// 来源: VideoEncoderConfigAMF.cpp - TransformConfig
FVideoEncoderConfigAMF Config;

// 设置编解码器类型
Config.CodecType = FVideoEncoderConfigAMF::CodecTypeH264;  // H.264/AVC
// Config.CodecType = FVideoEncoderConfigAMF::CodecTypeH265;  // H.265/HEVC（当前禁用）

// 设置分辨率
Config.Width = 1920;
Config.Height = 1080;

// 通过 AMF 属性系统配置编码参数
Config.SetProperty(AMF_VIDEO_ENCODER_USAGE, AMF_VIDEO_ENCODER_USAGE_LOW_LATENCY);
Config.SetProperty(AMF_VIDEO_ENCODER_TARGET_BITRATE, 5000000);  // 5 Mbps
Config.SetProperty(AMF_VIDEO_ENCODER_QUALITY_PRESET, AMF_VIDEO_ENCODER_QUALITY_PRESET_QUALITY);
Config.SetProperty(AMF_VIDEO_ENCODER_IDR_PERIOD, 60);  // 关键帧间隔

// 码率控制
Config.SetProperty(AMF_VIDEO_ENCODER_RATE_CONTROL_METHOD,
    AMF_VIDEO_ENCODER_RATE_CONTROL_METHOD_CBR);  // CBR
```

### 基本用法 — 编码流程

```cpp
// 来源: VideoEncoderAMF.hpp
TVideoEncoderAMF<FVideoResourceD3D11> Encoder;

// 1. 打开编码器（创建 AMF Context 并初始化 GPU 上下文）
FAVResult Result = Encoder.Open(Device, Instance);

// 2. 发送帧进行编码
//    Resource 是 GPU 纹理资源，Timestamp 是时间戳
Result = Encoder.SendFrame(Resource, Timestamp, bForceKeyframe);

// 3. 接收编码后的数据包
FVideoPacket Packet;
Result = Encoder.ReceivePacket(Packet);
// Packet.DataPtr - 编码后的数据
// Packet.DataSize - 数据大小
// Packet.Timestamp - 时间戳
// Packet.FrameCount - 帧序号
// Packet.QP - 量化参数
// Packet.IsKeyFrame - 是否为关键帧

// 4. 关闭编码器
Encoder.Close();
```

### 基本用法 — 解码流程

```cpp
// 来源: VideoDecoderAMF.hpp
TVideoDecoderAMF<FVideoResourceD3D11> Decoder;

// 1. 打开解码器
FAVResult Result = Decoder.Open(Device, Instance);

// 2. 发送编码数据包
Result = Decoder.SendPacket(Packet);

// 3. 接收解码后的帧
TResolvableVideoResource<FVideoResourceD3D11> Resource;
Result = Decoder.ReceiveFrame(Resource);
// 解码后的帧以 NV12 格式输出

// 4. 关闭解码器
Decoder.Close();
```

### 进阶用法 — 动态重配置

```cpp
// 来源: VideoEncoderAMF.hpp - ApplyConfig
// 编码器支持运行时动态修改部分参数（无需重建编码器）
// 可热更新的参数包括：码率、QP 范围、帧率等
// 不可热更新的参数（需要重建编码器）包括：分辨率、Profile、Level 等

// 修改码率
FVideoEncoderConfigAMF NewConfig = Encoder.GetPendingConfig();
NewConfig.SetProperty(AMF_VIDEO_ENCODER_TARGET_BITRATE, 8000000);  // 8 Mbps
Encoder.SetConfig(NewConfig);
// 下次 SendFrame 时自动应用
```

### 进阶用法 — 强制关键帧

```cpp
// 来源: VideoEncoderAMF.hpp - SendFrame
// 强制插入 IDR 关键帧
Encoder.SendFrame(Resource, Timestamp, /*bForceKeyframe=*/ true);

// 如果配置了 RepeatSPSPPS，还会在关键帧前插入 SPS/PPS
```

## Demo 示例

AMFCodecs 作为底层编解码器后端，不直接使用。以下是最小使用示例（需要在已有 AVCodecs 框架中）：

### Build.cs 依赖

```csharp
// 你的模块 Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "RenderCore",
    "AVCodecsCore",
    "AMFCodecs"
});
```

### 最小编码示例

```cpp
// MyVideoEncoder.h
#pragma once
#include "Video/Encoders/VideoEncoderAMF.h"

class FMyVideoEncoder
{
public:
    void InitEncoder(TSharedRef<FAVDevice> Device, TSharedRef<FAVInstance> Instance)
    {
        // 检查 AMF 是否可用
        if (!FAPI::Get<FAMF>().IsValid())
        {
            UE_LOG(LogTemp, Warning, TEXT("AMF not available - no compatible AMD GPU"));
            return;
        }

        // 打开编码器
        FAVResult Result = Encoder.Open(Device, Instance);
        if (Result.IsNotSuccess())
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open AMF encoder"));
            return;
        }
    }

    void EncodeFrame(TSharedPtr<FVideoResourceD3D11> Resource, uint32 Timestamp)
    {
        FVideoPacket Packet;
        
        // 发送帧
        FAVResult SendResult = Encoder.SendFrame(Resource, Timestamp);
        
        // 接收编码数据
        while (Encoder.ReceivePacket(Packet) == EAVResult::Success)
        {
            // 处理编码后的 Packet
            ProcessEncodedPacket(Packet);
        }
    }

    void Shutdown()
    {
        Encoder.Close();
    }

private:
    TVideoEncoderAMF<FVideoResourceD3D11> Encoder;
};
```

## 模块依赖

### AMFCodecs 模块

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `RenderCore` | 渲染核心 |
| `Engine` | 引擎核心（私有依赖） |
| `AVCodecsCore` | AVCodecs 框架核心（私有依赖） |
| `Amf` | AMD AMF SDK 三方库（私有依赖） |
| `Vulkan` | Vulkan 图形 API 支持 |
| `DX11` | DirectX 11 支持（仅 Windows） |
| `DX12` | DirectX 12 支持（仅 Windows） |

### AMFCodecsRHI 模块

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `RenderCore` | 渲染核心 |
| `Engine` | 引擎核心（私有依赖） |
| `AVCodecsCore` | AVCodecs 框架核心（私有依赖） |
| `AMFCodecs` | AMFCodecs 编解码模块（私有依赖） |
| `Amf` | AMD AMF SDK 三方库（私有依赖） |
| `RHI` | 渲染硬件接口（私有依赖） |
| `VulkanRHI` | Vulkan RHI 实现（私有依赖） |
| `Vulkan` | Vulkan 图形 API |
| `D3D11RHI` | D3D11 RHI 实现（仅 Windows，私有依赖） |
| `D3D12RHI` | D3D12 RHI 实现（仅 Windows，私有依赖） |
| `DX11` | DirectX 11 支持（仅 Windows） |
| `DX12` | DirectX 12 支持（仅 Windows） |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `AVCodecsCore` | AVCodecs 框架核心插件 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `20ee5e0e` | UnrealCodeFixup tool 修改以支持 mergemodules 编译 | 工具链自动修改，非功能性变更。为 PixelStreaming2 集成到 RemoteSession 插件做准备 |
| 2025-02-04 | `9c257b98` | 移除 AMF 的 H.265 编码以修复 Horde 构建问题 | H.265/HEVC 编码支持被禁用，因间歇性构建失败 (UE-239424) |
| 2024-10-01 | `e6ec3fc0` | 修复 AMF 无限 KeyFrameLength 导致的错误消息 | Bug 修复：解决了关键帧间隔为 0xFFFFFFFF 时 AMF 报错的问题 |
| 2024-08-12 | `21c0704e` | AVCodecs 枚举暴露到编辑器菜单；QP 改为 Quality | 功能改进：码率控制参数从 QP 改为 Quality 百分比，更用户友好 |
| 2023-11-14 | `f0b7e7ed` | 添加 VideoToolbox 编解码器到 AVCodecs | 此提交不直接涉及 AMFCodecs，是 AVCodecs 框架的扩展 |

### 维护评价

- **创建时间**：2023-01-25，约 3 年历史
- **维护状态**：**维护中** — 最近一次实质更新在 2025-02-04（约 1 年前），最近的 2025-09-08 变更是编译适配
- **活跃度**：中等。2024 年有多次 Bug 修复和功能改进，2025 年主要是构建修复
- **已知限制**：
  - ⚠️ **H.265/HEVC 编码已禁用**：因间歇性构建失败 (UE-239424)，H.265 编码的 TransformConfig 被注释掉
  - ⚠️ **解码器未注册**：`AMFCodecsModule.cpp` 中解码器的注册代码被完全注释掉，注释说明 "H265 decoding doesn't currently work with AMD"
  - ⚠️ **Vulkan 不支持**：RHI 模块中 Vulkan 被标记为不兼容，`bHasCompatibleGPU` 设为 false
  - ⚠️ **仅支持 D3D11/D3D12**：且仅在 Windows 平台上，且仅在 AMD GPU 上
  - ⚠️ **D3D12 解码 Surface 拷贝未实现**：`CopySurface<FVideoResourceD3D12>` 返回 `FatalUnsupported`
- **实验性标记**：`IsExperimentalVersion: true`，`EnabledByDefault: false`
- **推荐使用**：仅推荐在 Pixel Streaming 等需要 AMD GPU 硬件编码的场景中使用。作为通用编解码器，功能不完整（解码器禁用、H.265 编码禁用）。生产环境使用需充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- [AMD AMF SDK 文档](https://github.com/GPUOpen-LibrariesAndSDKs/AMF/blob/master/amf/doc/AMF_Video_Encode_API.md)
- [AMD AMF SDK GitHub](https://github.com/GPUOpen-LibrariesAndSDKs/AMF)
- [AVCodecsCore 插件](../AVCodecsCore/)（框架核心，AMFCodecs 的依赖）
