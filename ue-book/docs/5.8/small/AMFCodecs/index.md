# AMFCodecs

> Adds codecs from the AMD Advanced Media Framework SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | AMF编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AMFCodecs` (Runtime), `AMFCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs) | |

## 用途

此插件为引擎的 **AVCodecs（音视频编解码）框架** 提供了基于 **AMD Advanced Media Framework (AMF) SDK** 的硬件加速编解码器实现。它允许 UE5 利用 AMD 显卡的专用硬件单元进行高效的视频编码（如录制、串流）和解码（如播放），从而降低 CPU 负载并提升性能。

## 使用场景

- **游戏录制与直播**：当使用 OBS 等软件或 UE5 内置录制功能时，可选用 AMF 编码器（如 H.264/H.265）进行硬件加速编码。
- **游戏内视频播放**：播放高分辨率游戏内过场动画或用户生成内容时，使用 AMF 解码器进行硬件加速解码。
- **编辑器视频预览**：在编辑器中预览序列器时间线中的视频片段时，提升预览流畅度。
- **云游戏与串流**：为基于 UE5 的云游戏或应用提供低延迟的硬件编码支持。

## 蓝图用法

本插件主要为底层 `UAVCodec` / `UAVDecoder` 系统提供 AMF 实现，蓝图节点通常通过 `UAVCodecBPLibrary` 等上层库暴露。以下为核心概念性节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Encoder` / `Create Decoder` | 通过上层蓝图库创建基于 AMF 的编码器或解码器实例。 | `UAVCodecBPLibrary` (通常) |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用 AMF 模块，而是通过 `AVCodecs` 框架的通用接口进行操作。例如，先获取一个编码器实例，然后指定格式（如 `H264`），系统会自动选择可用的 AMF 后端（如果 AMD GPU 可用）。

## C++ 用法

### 头文件引入

```cpp
#include "AMFCodecsModule.h"
```

### 基本用法

获取 AMF 编解码器工厂并创建编码器实例。

```cpp
// 来源: 测试用例或引擎内部使用示例
#include "Codecs/AVCodec.h"
#include "Codecs/AVDecoder.h"

// 获取 AMF 编码器工厂（系统会自动注册）
TArray<FAVInstance> Encoders = FAVCodec::FindEncoder(EAVCodec::H264, FAMFCodecsModule::Get().GetHardwareID());
if (Encoders.Num() > 0)
{
    // 创建编码器实例
    TSharedRef<FAVEncoder> AMFEncoder = Encoders[0].CreateEncoder();
    // 配置并开始编码...
}
```

### 进阶用法

同时创建编码器和解码器，并处理回调，用于典型的录制-回放流程。

```cpp
// 伪代码，展示交互流程
// 1. 创建编码器
TSharedRef<FAVEncoder> Encoder = FAVCodec::CreateEncoder(...);
Encoder->OnEncoded.AddLambda([](FAVPacket& Packet) {
    // 将编码后的 Packet 发送至网络或写入文件
});

// 2. 创建解码器
TSharedRef<FAVDecoder> Decoder = FAVCodec::CreateDecoder(...);
Decoder->OnDecoded.AddLambda([](UTexture2D* Texture) {
    // 将解码后的纹理显示在 UI 上
});

// 3. 从网络或文件接收数据，喂给解码器
FAVPacket ReceivedPacket;
Decoder->Receive(ReceivedPacket);
```

## Demo 示例

一个最小的 C++ 示例，展示如何检查 AMF 可用性并获取编码器。

```cpp
// AMFCodecsDemo.h
#pragma once
#include "CoreMinimal.h"

class FAMFDemo
{
public:
    static void CheckAMFAvailability();
    static void CreateEncoder();
};
```

```cpp
// AMFCodecsDemo.cpp
#include "AMFCodecsDemo.h"
#include "AMFCodecsModule.h"
#include "Codecs/AVCodec.h"

void FAMFDemo::CheckAMFAvailability()
{
    const FAMFCodecsModule& AMFModule = FAMFCodecsModule::Get();
    if (AMFModule.IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("AMF Codecs are available. Hardware ID: %s"), *AMFModule.GetHardwareID());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("AMF Codecs are not available. Check for AMD GPU drivers."));
    }
}

void FAMFDemo::CreateEncoder()
{
    // 查找支持 H.264 编码的 AMF 实例
    TArray<FAVInstance> EncoderInstances = FAVCodec::FindEncoder(EAVCodec::H264, FAMFCodecsModule::Get().GetHardwareID());
    if (EncoderInstances.Num() > 0)
    {
        TSharedRef<FAVEncoder> Encoder = EncoderInstances[0].CreateEncoder();
        UE_LOG(LogTemp, Log, TEXT("Successfully created AMF H.264 encoder: %s"), *Encoder->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("No AMF H.264 encoder found."));
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Vulkan` | 与 AMD GPU 通信的底层图形 API，AMF 依赖于它。 |
| `MediaUtils` | 提供媒体框架的通用工具类。 |
| `AVCodecsCore` | 核心的音视频编解码框架，本插件为其提供后端实现。 |
| `RHI` | 渲染硬件接口，用于与 GPU 资源交互。 |

**注意**：虽然 `Core`, `Engine` 等是基础依赖，但上表列出了此插件**特有**的、必须显式添加到你的 `Build.cs` 中的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中作用域枚举可能导致输出乱码的问题 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了上一次错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的提交 CL51314860。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将委托调用改为 Get 函数形式，以修复缺失注册的问题。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的构建版本设置。 |

### 维护评价

**实验性但仍在维护**。该插件创建于约 3 年前，且最近（2026年4月）仍有针对编译和运行时问题的修复提交，表明它处于**活跃维护**状态。然而，它仍被标记为实验性且默认未启用，这意味着其 API 可能不完善或存在限制，不建议在生产环境中作为唯一或主要的编解码方案。推荐作为测试或特定场景下的备用硬件加速方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AMFCodecs)
- [官方文档](https://gpuopen.com/advanced-media-framework/) (AMD AMF SDK 官方文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/AVCodecs) (可能存在)