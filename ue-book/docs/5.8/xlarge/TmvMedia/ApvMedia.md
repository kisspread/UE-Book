# Tiled Mipmap Video Player

> Framework for tiled-mipmap video (TMV) playback, includes transcoding tools.
Implemented using Advanced Professional Video (APV) codec.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApvMedia` (Runtime), `TmvMedia` (Runtime), `TmvMediaEditor` (Runtime), `TmvMediaMp4Utils` (Runtime), `TmvMediaShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMedia) | |

## 用途

TmvMedia 插件为 Unreal Engine 提供了一套用于播放和转码 **Tiled Mipmap Video (TMV)** 格式视频的完整框架。TMV 是一种专为超高分辨率（如 8K 及以上）和高动态范围（HDR）视频内容设计的格式，其核心思想是将视频帧分割成多个独立的图块（Tile），并为每个图块生成多级渐进纹理（Mipmap）。

**解决的问题**：
1.  **超高分辨率视频的实时播放**：传统视频格式在解码 8K 等超高分辨率视频时，对 CPU 和内存带宽要求极高。TMV 通过分块和 Mipmap 技术，允许播放器仅解码和渲染当前视口所需的图块和 Mipmap 级别，从而大幅降低资源消耗，实现流畅播放。
2.  **随机访问与高效编辑**：由于视频被分割成独立的图块，可以实现对视频任意区域、任意 Mipmap 级别的快速随机访问，这对于视频编辑、特效合成等场景非常有利。
3.  **专业视频工作流集成**：插件集成了 **Advanced Professional Video (APV)** 编解码器（通过 `UEOpenAPV` 模块），支持 10/12 位色深、4:2:2/4:4:4 等专业色彩空间，满足影视级制作需求。

**为什么存在**：该插件是 Epic Games 为应对下一代沉浸式媒体内容（如虚拟制片、大型开放世界场景预览）对视频播放性能和质量提出的更高要求而开发的底层技术解决方案。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 墙上播放用于环境光照和背景的超高分辨率（8K+）视频时，使用 TMV 格式可以确保实时播放性能，并支持摄像机视锥体内的局部高清渲染。
-   **大型场景预览与审阅**：在建筑可视化或影视预览中，需要查看巨幅全景视频的特定区域细节时，TMV 的分块 Mipmap 结构允许快速聚焦和清晰显示。
-   **专业视频编辑与合成**：在非线性编辑（NLE）或合成软件中，需要对视频的特定区域进行频繁的随机访问和处理时，TMV 格式能提供比传统格式更高的效率。
-   **需要 HDR 和广色域支持的媒体应用**：播放使用专业色彩空间（如 Rec.2020, PQ/HLG 传输函数）制作的视频内容。

## 蓝图用法

当前 `ApvMedia` 模块主要提供底层的编解码器实现和数据结构，其核心 API 以 C++ 接口和工厂模式暴露。在蓝图层面，更上层的 `TmvMedia` 模块（未在当前分析范围内）可能会提供媒体播放器组件和蓝图友好的控制节点。

在 `ApvMedia` 模块中，以下结构体可在蓝图中作为配置数据使用：

### 核心配置结构体

| 结构体 | 说明 | 所在类 |
|---|---|---|
| `FApvMediaTmvEncoderOptions` | APV 编码器的详细配置选项，包括色彩空间、编码预设、分块大小等。 | `FApvMediaTmvEncoderOptions` |

### 使用示例（蓝图描述）

1.  **创建编码器选项**：在蓝图中创建一个 `FApvMediaTmvEncoderOptions` 结构体变量。
2.  **配置参数**：通过蓝图节点设置其属性，例如：
    -   `Profile`: 设置为 `YCbCr422_10` 以使用 4:2:2 10位色彩。
    -   `TileSize`: 设置为 `(512, 512)` 以定义图块大小。
    -   `Preset`: 设置为 `Medium` 以平衡编码速度与质量。
    -   `Band`: 设置为 `Band2` 以控制码率范围。
3.  **传递给编码器**：将配置好的结构体传递给上层的 TMV 编码器创建函数（具体节点取决于 `TmvMedia` 模块的蓝图接口）。

## C++ 用法

`ApvMedia` 模块的核心是提供 `ITmvMediaEncoder` 和 `ITmvMediaDecoder` 接口的 APV 实现，以及相关的工厂类。通常，使用者会通过工厂来创建编解码器实例。

### 头文件引入

```cpp
// 引入编码器选项和类型
#include "ApvMediaTmvEncoderOptions.h"
#include "ApvMediaTypes.h"

// 引入工厂（用于创建编码器/解码器）
#include "ApvMediaTmvEncoderFactory.h"
#include "ApvMediaTmvDecoderFactory.h"
```

### 基本用法（创建编码器）

以下代码展示了如何配置并创建一个 APV TMV 编码器实例。

```cpp
// 来源: 基于 ApvMediaTmvEncoderFactory.h 和 ApvMediaTmvEncoderOptions.h 推断
#include "ApvMediaTmvEncoderOptions.h"
#include "ApvMediaTmvEncoderFactory.h"
#include "Encoder/ITmvMediaEncoder.h"

void CreateApvEncoderExample()
{
    // 1. 配置编码器选项
    FApvMediaTmvEncoderOptions EncoderOptions;
    EncoderOptions.Profile = EApvMediaProfile::YCbCr422_10; // 4:2:2 10-bit
    EncoderOptions.TileSize = FIntPoint(256, 256);
    EncoderOptions.Preset = EApvMediaPreset::Medium;
    EncoderOptions.Band = EApvMediaBand::Band2;
    EncoderOptions.bEnableColorManagement = true;
    EncoderOptions.DestinationColorSpace = ETextureColorSpace::TCS_sRGB;

    // 2. 获取编码器工厂
    FApvMediaTmvEncoderFactory EncoderFactory;

    // 3. 使用工厂创建编码器实例
    // 注意：CreateEncoder 通常需要指定编解码器格式字符串（如 “apv1”）和选项
    TSharedPtr<ITmvMediaEncoder, ESPMode::ThreadSafe> ApvEncoder = 
        EncoderFactory.CreateEncoder(TEXT(“apv1”), FInstancedStruct::Make(EncoderOptions));

    if (ApvEncoder.IsValid())
    {
        // 4. 使用编码器进行编码（需要提供访问单元、Mip请求等）
        // ETmvMediaEncoderResult Result = ApvEncoder->Encode(...);
    }
}
```

### 进阶用法（解码与选择性 Mip 请求）

TMV 的一个关键特性是支持选择性解码。以下代码展示了如何创建解码器并请求特定 Mip 级别的数据。

```cpp
// 来源: 基于 ApvMediaTmvDecoderFactory.h 和 ITmvMediaDecoder.h 推断
#include "ApvMediaTmvDecoderFactory.h"
#include "Decoder/ITmvMediaDecoder.h"

void SelectiveDecodeExample()
{
    // 1. 获取解码器工厂
    FApvMediaTmvDecoderFactory DecoderFactory;

    // 2. 创建解码器实例（可指定解码线程数）
    TSharedPtr<ITmvMediaDecoder, ESPMode::ThreadSafe> ApvDecoder = 
        DecoderFactory.CreateDecoder(TEXT(“apv1”), TMap<FString, FVariant>());

    if (ApvDecoder.IsValid())
    {
        // 3. 准备一个访问单元（包含压缩的视频数据块）
        // ITmvMediaDecoderAccessUnit* AccessUnit = ...;

        // 4. 定义 Mip 请求：只解码 Mip 级别 0 和 1
        TArray<FTmvMediaDecoderMipRequest> MipRequests;
        MipRequests.Add({0, true}); // 请求 Mip 0
        MipRequests.Add({1, true}); // 请求 Mip 1

        // 5. 执行解码
        // ETmvMediaDecoderResult Result = ApvDecoder->Decode(*AccessUnit, MipRequests);
        // 解码后，可以通过访问单元获取指定 Mip 级别的像素数据
    }
}
```

## Demo 示例

一个最小化的示例，展示如何初始化 APV 编码器选项并查询其基本属性。

**ApvMediaDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ApvMediaTmvEncoderOptions.h"

class FApvMediaDemo
{
public:
    static void RunDemo();
};
```

**ApvMediaDemo.cpp**
```cpp
#include "ApvMediaDemo.h"
#include "ApvMediaTypes.h"

void FApvMediaDemo::RunDemo()
{
    // 创建并配置编码器选项
    FApvMediaTmvEncoderOptions Options;
    Options.Profile = EApvMediaProfile::YCbCr444_12; // 4:4:4 12-bit 高质量
    Options.TileSize = FIntPoint(512, 512);
    Options.Preset = EApvMediaPreset::Slow; // 慢速预设，追求更高质量
    Options.Band = EApvMediaBand::Band3; // 最高码率档位
    Options.NumThreads = 8; // 使用8个线程进行编码

    // 查询配置信息
    UE_LOG(LogTemp, Log, TEXT(“APV Encoder Demo”));
    UE_LOG(LogTemp, Log, TEXT(“  Profile: %s”), *UEnum::GetValueAsString(Options.Profile));
    UE_LOG(LogTemp, Log, TEXT(“  Tile Size: %s”), *Options.TileSize.ToString());
    UE_LOG(LogTemp, Log, TEXT(“  Preset: %s”), *UEnum::GetValueAsString(Options.Preset));
    UE_LOG(LogTemp, Log, TEXT(“  Band: %s”), *UEnum::GetValueAsString(Options.Band));
    UE_LOG(LogTemp, Log, TEXT(“  Chroma Format: %s”), *UEnum::GetValueAsString(Options.GetChromaFormat()));
    UE_LOG(LogTemp, Log, TEXT(“  Bit Depth: %d”), Options.GetBitDepth());
    UE_LOG(LogTemp, Log, TEXT(“  Encoder Name: %s”), *Options.GetEncoderName().ToString());
    UE_LOG(LogTemp, Log, TEXT(“  File Extension: %s”), *Options.GetFileSequenceExtension());
}
```

## 模块依赖

要使用 `ApvMedia` 模块的功能，你的模块需要依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `UEOpenAPV` | Advanced Professional Video (APV) 编解码器的底层实现库，提供编码、解码核心功能。 |
| `ApvMedia` | 本模块，提供 UE 与 OpenAPV 之间的封装层、工厂和配置类型。 |

## 维护状态

### 近期更新

（无法从提供的信息中获取 git log，以下为基于创建时间的推测）
- 2026-04-18 初始提交，创建插件框架和 `ApvMedia` 模块。

### 维护评价

-   **创建时间**：2026-04-18（未来时间，可能为占位符或开发中版本）。
-   **维护状态**：**实验性/开发中**。插件默认未启用（`EnabledByDefault: false`），且创建时间在未来，表明它很可能是一个处于早期开发或实验阶段的新功能。
-   **已知限制**：
    1.  依赖外部的 `UEOpenAPV` 模块，该模块的可用性和稳定性是前提。
    2.  TMV 是一种相对新颖的格式，生态工具链（如独立的转码器、播放器）可能尚不完善。
    3.  文档和示例可能较少。
-   **推荐使用**：目前**不推荐**在生产环境中使用。建议关注其后续版本更新，待其成熟并标记为稳定后再进行评估。适合对前沿视频技术进行研究和原型开发的团队试用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMedia)
-   [官方文档]() (暂无)
-   [测试用例]() (暂未发现)