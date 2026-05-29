# Hardware Encoders

> Adds support of hardware encoders to AVEncoder

| 属性 | 值 |
|---|---|
| 中文名 | 硬件编码器 |
| 分类 | Encoders |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EncoderAMF` (Runtime), `EncoderNVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HardwareEncoders) | |

## 用途

HardwareEncoders 插件为虚幻引擎的 `AVEncoder` (Audio/Video Encoder) 框架提供了硬件（GPU）视频编码的集成支持。它解决的核心问题是：将计算密集的视频编码任务从 CPU 转移到 GPU，以显著提升编码效率、降低 CPU 占用，并实现实时视频处理（如推流、录制）。

该插件通过集成主流的硬件编码技术，使得 `AVEncoder` 能够利用特定厂商的显卡硬件编码器。它本身不提供独立的使用接口，而是作为 `AVEncoder` 的后端编码器模块被加载和调用。

## 使用场景

-   你在使用 **Pixel Streaming** 功能，需要将游戏画面实时编码为视频流并推送到客户端。
-   你正在开发一个**游戏内视频录制**或**直播推流**功能，希望获得高性能、低延迟的编码体验。
-   你需要处理**视频文件转码**任务，希望利用 GPU 加速来缩短处理时间。
-   你的项目目标平台包含 **Windows 64位** 系统，并希望支持 AMD 或 NVIDIA 的显卡硬件编码。

## 蓝图用法

此插件不提供直接的蓝图节点。其主要作用是为底层的 `AVEncoder` 系统注册硬件编码器后端。在蓝图层面，用户通常通过其他依赖 `AVEncoder` 的功能模块（如 `MediaFrameworkUtilities`）间接使用硬件编码能力。具体可用的蓝图功能取决于调用编码功能的上层模块。

## C++ 用法

此插件的核心是作为 `AVEncoder` 的编码器实现模块被使用。在 C++ 层面，使用流程通常是：

1.  在项目中启用此插件。
2.  通过 `AVEncoder` 的接口请求或配置一个编码器实例。
3.  `AVEncoder` 内部会根据当前环境和设置，选择合适的已注册编码器（可能包含 `EncoderAMF` 或 `EncoderNVENC` 提供的实例）。

### 头文件引入

由于其作为“服务”模块的特性，通常不需要直接包含此插件的头文件。依赖项是 `AVEncoder` 模块。

```cpp
// 如果需要在特定场景下检查或操作编码器，可能需要包含相关头文件
#include "VideoEncoderFactory.h"
```

### 基本用法

一个编码器的生命周期由 `AVEncoder` 系统管理。以下是一个概念性的示例，展示了 `AVEncoder` 如何发现并使用硬件编码器。

```cpp
// 示例：AVEncoder 内部可能的工作逻辑 (概念性代码)
#include "AVEncoder.h"
#include "VideoEncoder.h"
#include "VideoEncoderFactory.h"

// 获取 AVEncoder 模块实例
IAVEncoderModule& AVEncoderModule = IAVEncoderModule::Get();

// 获取已注册的编码器工厂列表
TArray<TSharedPtr<FVideoEncoderFactory>> Factories = AVEncoderModule.GetEncoderFactories();

// 遍历工厂，找到一个支持硬件编码的实例
for (const auto& Factory : Factories)
{
    if (Factory && Factory->SupportsHardwareEncoding())
    {
        // 使用该工厂创建硬件编码器实例
        TSharedPtr<FVideoEncoder> HardwareEncoder = Factory->CreateEncoder(EncoderSettings);
        if (HardwareEncoder.IsValid())
        {
            // 使用 HardwareEncoder 进行编码
            HardwareEncoder->Encode(FrameData, ...);
        }
        break;
    }
}
```

### 进阶用法

在某些情况下，可能需要针对特定硬件进行微调。`EncoderAMF` 和 `EncoderNVENC` 模块内部实现了 `FVideoEncoderFactory` 接口，并可能暴露特定于硬件的配置选项。这些配置通常通过 `AVEncoder` 的 `FVideoEncoderSettings` 结构体传递。

```cpp
// 示例：配置可能包含硬件特定参数 (概念性)
FVideoEncoderSettings Settings;
Settings.Width = 1920;
Settings.Height = 1080;
Settings.Bitrate = 8000000; // 8 Mbps
// 以下参数可能被特定的硬件编码器工厂识别并应用
Settings.EncoderSpecific["NVENC_Preset"] = "low_latency_hq"; // NVIDIA 特定预设
Settings.EncoderSpecific["AMF_Usage"] = "transcoding";       // AMD 特定用途
```

## Demo 示例

以下示例展示了如何在一个模块中尝试获取一个已注册的硬件编码器。**注意**：实际使用通常由 `AVEncoder` 上层系统封装，此示例仅用于说明插件模块的工作原理。

**HardwareEncoderTest.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FHardwareEncoderTestModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void TryGetHardwareEncoder();
};
```

**HardwareEncoderTest.cpp**
```cpp
#include "HardwareEncoderTest.h"
#include "AVEncoder.h"
#include "VideoEncoderFactory.h"
#include "VideoEncoder.h"

#define LOCTEXT_NAMESPACE "FHardwareEncoderTestModule"

void FHardwareEncoderTestModule::StartupModule()
{
    // 模块启动后可以尝试获取编码器
    TryGetHardwareEncoder();
}

void FHardwareEncoderTestModule::ShutdownModule()
{
}

void FHardwareEncoderTestModule::TryGetHardwareEncoder()
{
    // 检查 AVEncoder 模块是否已加载
    IAVEncoderModule* AVEncoderModule = FModuleManager::GetModulePtr<IAVEncoderModule>("AVEncoder");
    if (!AVEncoderModule)
    {
        UE_LOG(LogTemp, Warning, TEXT("AVEncoder module is not loaded."));
        return;
    }

    // 获取所有编码器工厂
    TArray<TSharedPtr<FVideoEncoderFactory>> Factories = AVEncoderModule->GetEncoderFactories();
    UE_LOG(LogTemp, Log, TEXT("Found %d encoder factories."), Factories.Num());

    // 寻找硬件编码器
    for (const auto& Factory : Factories)
    {
        if (Factory.IsValid() && Factory->SupportsHardwareEncoding())
        {
            UE_LOG(LogTemp, Log, TEXT("Found hardware encoder factory: %s"), *Factory->GetName());
            // 在这里可以进一步用工厂创建编码器实例进行测试
            break;
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FHardwareEncoderTestModule, HardwareEncoderTest)
```

## 模块依赖

要使用此插件，你的项目模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | AVEncoder 框架的基础媒体工具模块。 |
| `AVEncoder` | 提供视频编码的抽象接口和管理框架，是此插件的核心目标。 |
| `RenderCore` | 提供与渲染管线交互的基础能力，硬件编码器需要访问渲染资源。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版 `UE_LOGF`，属于代码现代化更新。 |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | 移除了插件启动时不再需要手动加载的 Vulkan 扩展，优化初始化。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复前一次错误的查找替换操作后的重试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的一次提交 (CL51314860)。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复了一个在引擎初始化期间因委托注册顺序导致的潜在问题。 |

### 维护评价

HardwareEncoders 插件创建于 2021 年，标记为 **Beta 版本**且 **默认未启用**，表明它仍处于实验性阶段。从提交历史看，直到 2026 年初仍有活跃的提交，主要是进行编译适配、代码现代化和底层依赖调整。**最近一年内**有实质性更新，说明它仍在被维护以确保与新版引擎（UE5.8）兼容。

**综合评价**：
- **维护状态**: **活跃维护中**。代码与最新引擎版本保持同步。
- **稳定性**: 作为 Beta 插件，可能存在未发现的 Bug 或 API 变更，不建议用于生产环境的关键路径。
- **推荐度**: 如果你需要在支持的硬件上实现高性能视频编码（特别是 Pixel Streaming 等官方功能依赖此功能），可以**谨慎启用并进行充分测试**。它提供了官方级别的硬件编码支持，但需接受其实验性状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HardwareEncoders)
- [EncoderAMF 子模块文档](EncoderAMF.md)
- [EncoderNVENC 子模块文档](EncoderNVENC.md)