# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AMD AMF 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AMFCodecs` (Runtime), `AMFCodecsRHI` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 👴 老古董（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途
AMFCodecs 是 UE5 媒体框架 `AVCodecs` 的一个底层扩展插件，其主要作用是**集成 AMD 的 Advanced Media Framework (AMF) SDK**。它为 UE5 提供了一套利用 AMD GPU（VCE/VCN 引擎）进行硬件加速视频编码（H.264/H.265）和解码的能力。
该插件本身不提供用户友好的高层功能，而是作为编解码器实现，供 `AVCodecs` 等更高层次的媒体插件调用。其存在意义在于让需要高性能、低延迟硬件编解码的项目（如云游戏、实时视频处理）能够充分利用 AMD 硬件资源。

## 使用场景
- 你需要在使用 AMD GPU 的硬件上，对 H.264 或 H.265 视频流进行**硬件加速编码**，例如用于低延迟的游戏串流或视频录制。
- 你需要**解码**来自硬件源（如摄像头、采集卡）或网络流的 H.264/H.265 视频，并希望利用 GPU 加速解码过程以降低 CPU 负担。
- 你正在开发与 `AVCodecs` 媒体框架集成的自定义视频管线，并希望为 AMD 硬件用户提供优化的编解码器路径。

**重要提示**：此插件为**实验性**（`IsExperimentalVersion=true`），且**默认不启用**。主要用于开发者研究和实验，不建议直接在生产项目中使用。

## 蓝图用法
经分析源码，本插件**没有暴露任何蓝图可调用的节点**（未发现 `UFUNCTION(BlueprintCallable)` 或 `BlueprintReadWrite` 的 `UPROPERTY`）。其所有功能均通过 C++ 模板类和结构体提供，属于底层编解码器实现。

## C++ 用法
该插件的核心是 C++ 模板类 `TVideoEncoderAMF` 和 `TVideoDecoderAMF`，以及配置结构体 `FVideoEncoderConfigAMF` / `FVideoDecoderConfigAMF`。

### 头文件引入
```cpp
#include "AMF.h"
#include "Video/Encoders/VideoEncoderAMF.h"
#include "Video/Encoders/Configs/VideoEncoderConfigAMF.h"
#include "Video/Decoders/VideoDecoderAMF.h"
#include "Video/Decoders/Configs/VideoDecoderConfigAMF.h"
```

### 基本用法
首先需要初始化 AMF 工厂（`FAMF`），这是整个插件的基础。

```cpp
// 来源: Public/AMF.h
// 获取全局 AMF 工厂实例
FAMF& AMFFactory = FAMF::Get();

// 检查 AMF 是否初始化成功且系统有兼容的 GPU
if (AMFFactory.IsValid())
{
    // 可以获取底层的 AMFFactory 指针用于更高级的 AMF 操作
    amf::AMFFactory* Factory = AMFFactory.GetFactory();
}
```

### 进阶用法：视频编码
以下示例展示了如何使用 `TVideoEncoderAMF` 模板类（以 `FVideoResourceVulkan` 为例）进行视频编码。

```cpp
// 假设已包含必要的头文件，并已定义 TResource 类型，例如 FVideoResourceVulkan
using FMyEncoder = TVideoEncoderAMF<FVideoResourceVulkan>;

// 1. 创建编码器实例
TSharedRef<FMyEncoder> Encoder = MakeShared<FMyEncoder>();

// 2. 打开编码器，关联到设备和实例
TSharedRef<FAVDevice> Device = /* ... */;
TSharedRef<FAVInstance> Instance = /* ... */;
FAVResult OpenResult = Encoder->Open(Device, Instance);
if (OpenResult.IsNotSuccess())
{
    // 处理错误
}

// 3. 配置编码参数
FVideoEncoderConfigAMF Config;
Config.CodecType = FVideoEncoderConfigAMF::CodecTypeH264; // 或 H265
Config.Width = 1920;
Config.Height = 1080;
Config.SetProperty(AMF_VIDEO_ENCODER_QUALITY_PRESET, AMF_VIDEO_ENCODER_QUALITY_PRESET_SPEED);

// 应用配置
Encoder->ApplyConfig();

// 4. 发送视频帧进行编码
TSharedPtr<FVideoResourceVulkan> InputResource = /* ... 获取或创建一帧 GPU 资源 ... */;
uint32 Timestamp = /* ... */;
bool bForceKeyframe = false;
FAVResult SendResult = Encoder->SendFrame(InputResource, Timestamp, bForceKeyframe);

// 5. 接收编码后的数据包（非阻塞）
FVideoPacket Packet;
FAVResult ReceiveResult = Encoder->ReceivePacket(Packet);
if (ReceiveResult.IsSuccess())
{
    // Packet.Data 包含编码后的 H.264/H.265 NALUs
    // Packet.Timestamp 包含时间戳
}

// 6. 完成后关闭编码器
Encoder->Close();
```

## Demo 示例
一个基于 Vulkan 资源的 H.264 编码器最小示例。

**MyAMFEncoder.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "VideoResourceVulkan.h" // 假设资源类型已定义

class FMyAMFExample
{
public:
    void RunEncodingExample();
};
```

**MyAMFEncoder.cpp**
```cpp
#include "MyAMFEncoder.h"
#include "AMF.h"
#include "Video/Encoders/VideoEncoderAMF.h"
#include "Video/Encoders/Configs/VideoEncoderConfigAMF.h"

void FMyAMFExample::RunEncodingExample()
{
    // 1. 检查 AMF 可用性
    FAMF& AMFFactory = FAMF::Get();
    if (!AMFFactory.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("AMF is not available or no compatible GPU found."));
        return;
    }

    // 2. 定义编码器类型 (以 Vulkan 资源为例)
    using FMyEncoder = TVideoEncoderAMF<FVideoResourceVulkan>;

    // 3. 创建并配置编码器
    TSharedRef<FMyEncoder> Encoder = MakeShared<FMyEncoder>();

    // 4. 准备设备和实例 (需要根据实际情况获取)
    // TSharedRef<FAVDevice> Device = ...;
    // TSharedRef<FAVInstance> Instance = ...;
    // FAVResult Result = Encoder->Open(Device, Instance);

    // 5. 设置 H.264 编码参数
    FVideoEncoderConfigAMF Config;
    Config.CodecType = FVideoEncoderConfigAMF::CodecTypeH264;
    Config.Width = 1280;
    Config.Height = 720;
    // 使用 AMF SDK 的枚举设置参数
    Config.SetProperty(AMF_VIDEO_ENCODER_USAGE, AMF_VIDEO_ENCODER_USAGE_TRANSCONDING);
    Config.SetProperty(AMF_VIDEO_ENCODER_QUALITY_PRESET, AMF_VIDEO_ENCODER_QUALITY_PRESET_SPEED);

    // ... (Open, ApplyConfig, SendFrame, ReceivePacket 循环) ...
    // Encoder->Close();
}
```

## 模块依赖
从 `AMFCodecs.Build.cs` 和 `AMFCodecsRHI.Build.cs` 分析，使用此插件需要以下**独特**依赖：

| 模块 | 用途 |
|---|---|
| `Vulkan` | 提供 Vulkan RHI 支持，用于在 Vulkan 后端上运行 AMF 编解码器 |
| `AVCodecs` | 提供本插件所实现的编解码器基类和接口（如 `TVideoEncoder`， `FAVConfig`）。使用本插件的项目通常也需要引用此模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中使用的 scoped enum 导致输出垃圾值的 bug |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 继续修复上一次错误的查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 51314860 的修改 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registry | 修复了因引擎初始化委托获取方式变更导致的注册缺失问题 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的构建版本设置 |

### 维护评价
该插件创建于 2023 年初，**近期（2026 年）仍有维护活动**，主要集中在 bug 修复和引擎接口适配上。结合其 `IsExperimentalVersion=true` 和 `EnabledByDefault=false` 的特性，可以判断它目前处于**实验性维护阶段**。
- **优点**：仍在被 Epic Games 工程师维护，以适应引擎内部 API 的变化。
- **限制**：是实验性插件，API 可能不稳定，功能可能不完整（例如 H.265 编码支持在代码中被注释掉）。
- **建议**：**不建议**用于生产项目。适用于想要研究 UE5 与 AMF SDK 集成、或为 AMD 硬件开发定制媒体管线的开发者。使用时应密切关注其 API 变更。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- [官方文档](https://gpuopen.com/amf/) (AMD AMF SDK 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs/Tests) (如果存在，通常在此路径下)