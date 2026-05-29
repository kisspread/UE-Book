# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | 电磁采样工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (Runtime), `ElectraSamples` (Runtime), `ElectraHTTPStream` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 并非一个独立的媒体播放器插件，而是 **Electra 媒体播放器框架的基础组件库**。它提供了用于媒体播放过程中处理采样数据（视频纹理、音频、字幕、元数据）的核心类、接口和平台特定的GPU缓冲区管理工具。

这个插件存在的根本原因是为 Electra 播放器提供：
1.  **标准化的采样数据接口**：定义了 `IElectraTextureSampleBase`、`FElectraAudioSample` 等基类，统一了跨平台（Windows, Mac, iOS, Android, Linux）的采样数据格式。
2.  **平台特定的GPU资源优化**：例如，在 Windows 平台（DX11/DX12）上，提供了高效的纹理上传和内存管理机制（`FElectraMediaDecoderOutputBufferPool_DX12`），以减少解码到渲染的延迟。
3.  **色彩空间与元数据处理**：包含对 HDR、色彩空间转换、时间码等媒体元数据的支持。
4.  **可复用的工具集**：供 Epic Games 的其他媒体相关插件（如 Electra Player）依赖和使用。

简单来说，它是 Electra 媒体播放技术栈的“地基”和“工具箱”。

## 使用场景

-   你在项目中使用或计划使用 **Electra 媒体播放器**（`ElectraPlayer` 插件）进行高质量的媒体播放（如 4K/HDR 视频、流媒体）。
-   你需要处理来自 **自定义解码器** 或 **第三方媒体源** 的采样数据，并希望将其无缝集成到 Unreal Engine 的媒体框架和渲染管线中。
-   你在开发 **平台特定的媒体功能**，需要对 GPU 缓冲区（特别是 DX12 资源池）进行精细管理以优化性能。

## 蓝图用法

经过对插件公共头文件的搜索，**ElectraUtil 插件本身没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图接口**。

它的所有核心类和功能（如 `FElectraTextureSamplePool`, `FElectraAudioSample`）都是纯粹的 C++ 接口，主要供其他 C++ 模块（如 `ElectraPlayer`）内部使用。普通开发者通过蓝图使用媒体播放功能时，通常是在操作上层的 `MediaPlayer` 和 `MediaTexture` 资产，而 `ElectraUtil` 的复杂采样处理逻辑在后台自动运行。

## C++ 用法

该插件为 C++ 开发者提供了与媒体采样数据交互的底层接口。

### 头文件引入

```cpp
// 核心采样接口
#include “IElectraTextureSample.h”
#include “IElectraAudioSample.h”
#include “IElectraSubtitleSample.h”

// 采样池（用于高效内存管理）
#include “ElectraTextureSample.h” // 注意：路径会根据平台变化
// 或
#include “IElectraTextureSampleEncoding.h”
```

### 基本用法：创建纹理采样池与获取采样

以下代码展示了如何创建一个纹理采样池，并从解码器输出中获取一个采样。这是媒体播放器内部处理帧数据的典型模式。
（**来源**：基于 `FElectraTextureSamplePool` 类设计推导）

```cpp
#include “ElectraTextureSample.h”

// 假设在一个媒体解码器类中
class FMyMediaDecoder
{
public:
    FMyMediaDecoder()
    {
        // 创建纹理采样对象池，用于高效分配和复用采样对象
        TextureSamplePool = MakeShared<FElectraTextureSamplePool>();
    }

    // 模拟解码器输出一帧时，获取一个采样对象
    FElectraTextureSamplePtr GetNewTextureSample()
    {
        if (TextureSamplePool.IsValid())
        {
            // 从池中分配一个新的采样对象
            return TextureSamplePool->AcquireShared();
        }
        return nullptr;
    }

    // 使用采样（例如，设置其内部数据）
    void UseSample(FElectraTextureSamplePtr InSample)
    {
        if (InSample.IsValid())
        {
            // 在此设置采样数据（例如，从解码缓冲区拷贝），具体API由平台特定的FElectraTextureSample实现决定。
            // 例如，设置缓冲区指针、步长、像素格式等。
            // InSample->SetBuffer(...);
            // InSample->SetDim(FIntPoint(1920, 1080));
            // InSample->SetTime(FMediaTimeStamp(...));
        }
    }

private:
    TSharedPtr<FElectraTextureSamplePool> TextureSamplePool;
};
```

### 进阶用法：采样转换与色彩管理

采样对象的核心功能之一是通过 `Convert` 方法将自身包含的数据（可能是缓冲区、共享纹理等）转换并上传到渲染线程的目标纹理中。这个过程通常发生在渲染线程。
（**来源**：`IMediaTextureSampleConverter` 接口及各平台 `FElectraTextureSample` 实现）

```cpp
// 在渲染线程中，获取采样并进行转换
void FMyMediaRenderer::ConvertSampleToTexture(FRHICommandListImmediate& RHICmdList, const FElectraTextureSampleRef& InSample, FTextureRHIRef& InOutDstTexture)
{
    // 检查采样是否支持GPU转换
    IMediaTextureSampleConverter* Converter = InSample->GetMediaTextureSampleConverter();
    if (Converter)
    {
        // 构造转换提示信息
        FConversionHints Hints;
        Hints.bSRGB = InOutDstTexture->GetDesc().bSRGB; // 根据目标纹理是否为sRGB设置提示

        // 调用采样的转换函数，将解码数据高效转移到GPU纹理
        // 这个过程可能涉及DX11共享表面拷贝、DX12资源屏障与拷贝命令、或Vulkan纹理导入等平台特定逻辑
        bool bSuccess = Converter->Convert(RHICmdList, InOutDstTexture, Hints);
        if (!bSuccess)
        {
            UE_LOG(LogTemp, Warning, TEXT(“Texture sample conversion failed.”));
        }
    }

    // 此外，可以从采样中获取色彩空间信息，用于后续的渲染管线设置
    const UE::Color::FColorSpace& SourceColorSpace = InSample->GetSourceColorSpace();
    UE::Color::EEncoding EncodingType = InSample->GetEncodingType();
    // ... 使用这些信息配置材质参数或后处理设置
}
```

## Demo 示例

一个展示如何创建和使用 `FElectraTextureSamplePool` 及 `FElectraTextureSample` 的最小 C++ 示例。

### MyMediaConsumer.h
```cpp
#pragma once

#include “CoreMinimal.h”
// 引入采样相关头文件（路径根据模块名调整）
#include “IElectraTextureSample.h”

// 前向声明
class FElectraTextureSample;
class FElectraTextureSamplePool;

class FMyMediaConsumer
{
public:
    FMyMediaConsumer();
    ~FMyMediaConsumer();

    // 模拟媒体管线：获取一个空采样，填充数据，然后“输出”
    void SimulateMediaPipeline();

private:
    // 纹理采样对象池
    TSharedPtr<FElectraTextureSamplePool> TextureSamplePool;
};
```

### MyMediaConsumer.cpp
```cpp
#include “MyMediaConsumer.h”
// 包含平台特定的采样实现（需要根据目标平台在Build.cs中链接正确模块）
// 例如，在Windows上，这会解析到 Windows/ElectraTextureSample.h
#include “ElectraTextureSample.h” 

FMyMediaConsumer::FMyMediaConsumer()
{
    // 初始化采样池
    TextureSamplePool = MakeShared<FElectraTextureSamplePool>();
}

FMyMediaConsumer::~FMyMediaConsumer()
{
    // 采样池会被智能指针自动管理
}

void FMyMediaConsumer::SimulateMediaPipeline()
{
    if (!TextureSamplePool.IsValid())
    {
        return;
    }

    // 1. 从池中获取一个可复用的采样对象
    FElectraTextureSamplePtr CurrentSample = TextureSamplePool->AcquireShared();
    if (!CurrentSample.IsValid())
    {
        return;
    }

    // 2. 模拟填充采样数据 (实际由解码器完成)
    // 这里仅示意，真实数据来自视频解码器。
    // 具体函数如 SetBuffer, SetDim, SetTime 等需要参考平台实现。
    // CurrentSample->SetDim(FIntPoint(1920, 1080));
    // CurrentSample->SetTime(FMediaTimeStamp(FTimespan::FromSeconds(1.0)));
    // CurrentSample->SetDuration(FTimespan::FromSeconds(1.0 / 30.0));

    // 3. 采样对象现在可以被传递给渲染器。
    // 在渲染线程的 ConvertSampleToTexture 类似函数中，调用其 Convert 方法。
    // 渲染完成后，采样对象会被归还到池中（通过其内部的 ReleaseDelegate）。

    UE_LOG(LogTemp, Log, TEXT(“Acquired a texture sample from the pool. It will be used by the renderer.”));
}
```

## 模块依赖

`ElectraSamples` 模块的 Build.cs 依赖如下：

| 模块 | 用途 |
|---|---|
| `DirectX` | 提供 Direct3D 11/12 的头文件和库支持，用于 Windows 平台的高效 GPU 资源管理 |

*（注：`Engine` 是标准依赖，已省略。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务器构建添加存根方法，防止意外链接时出错 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复HDR归一化因子，解决媒体切换时亮度不正确的问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，使其更易于其他客户端使用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复从MPEG定义创建时间码时亚帧精度丢失的问题 |

### 维护评价

-   **创建时间**：约5年前（2021年1月），属于较老的插件。
-   **更新频率**：**活跃维护中**。最近半年有持续更新，最近一次提交在2026年5月。
-   **更新内容**：最近的更新集中在 **Bug修复**（HDR亮度、时间码精度）、**兼容性改进**（服务器构建）和**现代化重构**（解码器工厂）。这表明插件仍在被Epic Games内部依赖和积极维护。
-   **结论**：虽然插件本身“默认不启用”，且作为基础组件不直接面向普通用户，但它是 **Electra 播放器技术栈的核心且仍在活跃维护的部分**。如果你正在或计划使用 Electra 相关功能，这是一个可靠的基础依赖。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
-   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview) (媒体框架概述，非该插件专属)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) (插件目录内未发现独立测试模块，其测试可能集成在依赖它的插件或引擎测试中)