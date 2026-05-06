# Apple ProRes Media

> Implements video playback and the export of the Apple ProRes Codec.  Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | Apple ProRes 媒体支持 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia) | |

## 用途

Apple ProRes Media 插件为 Unreal Engine 提供了对 Apple ProRes 编解码器的原生支持。ProRes 是一种高质量、有损的视频压缩格式，广泛应用于影视后期制作、广播和高端视频内容生产领域。

该插件主要解决两个核心问题：

- **视频导出**：允许在 Movie Render Pipeline (MRP) 和 Movie Render Graph (MRG) 中直接输出 Apple ProRes 格式的 `.mov` 文件。这是影视级渲染输出必不可少的环节，使得 UE 渲染的内容能够无缝接入主流的后期制作工作流（如 DaVinci Resolve, Final Cut Pro, Adobe Premiere 等）。
- **视频播放**：通过 Windows 平台上的 WMF (Windows Media Foundation) 解码器，实现对 Apple ProRes 视频文件的原生回放能力。

简单来说，这个插件是 UE 与专业影视后期生态之间的桥梁。如果没有它，用户将无法直接输出 / 预览 ProRes 这类广播级格式，必须依赖额外的转码工具，增加工作流复杂度。

## 使用场景

- **影视级离线渲染**：你正在使用 Movie Render Pipeline (MRP) 或 Movie Render Graph (MRG) 渲染最终交付的镜头。客户的交付规范要求视频必须为 Apple ProRes 4444 XQ 或 422 HQ 格式，并包含 Alpha 通道。
- **广播级内容制作**：你的项目需要输出符合广播标准的视频素材（如 Rec. 709 色彩空间、特定帧率），并且需要进行后续在线编辑和调色。
- **需要透明通道的输出**：你需要导出带有 Alpha 通道的视频素材，用于后期合成。ProRes 4444 和 4444 XQ 支持高精度 Alpha 通道。
- **实时预览与素材管理**：你的项目资源中包含大量 Apple ProRes 格式的源素材，需要在引擎内直接播放和预览，而无需转码为其他格式。

## 蓝图用法

Apple ProRes Media 插件的核心功能通过 C++ 集成在 Movie Render Pipeline/Movie Render Graph 系统中，蓝图可以直接配置其设置和属性，无需编写 C++ 代码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Apple ProRes Encoder` | 创建一个 Apple ProRes 编码器实例，并设置输出文件名、分辨率、帧率等参数。该节点是蓝图直接使用编码器的基础入口。 | `UAppleProResEncoder` |
| `Initialize` | 初始化编码器，准备写入文件。在开始编码任何帧之前必须调用。 | `UAppleProResEncoder` |
| `Write Frame` | 向输出文件写入一帧视频数据。需要提供图像像素数据。 | `UAppleProResEncoder` |
| `Finalize` | 完成编码并关闭输出文件。写入所有帧后必须调用。 | `UAppleProResEncoder` |

### 使用示例（蓝图描述）

以 Movie Pipeline 输出配置为例（最常用）：

1. 在 MRP 主序列配置中添加 `UMoviePipelineAppleProResOutput` 设置。
2. 在细节面板中，设置 `Codec` 为你需要的 ProRes 格式（如 `ProRes_4444XQ`）。
3. （可选）启用 `bIncludeAudio` 包含音轨。设置 `bDropFrameTimecode` 适配 29.97fps 时间码。
4. 如果需要控制编码线程数，启用 `bOverrideMaximumEncodingThreads` 并设置 `MaxNumberOfEncodingThreads`（0 表示自动）。

对于 MRG 流程，同理添加 `UMovieGraphAppleProResNode` 节点并配置。

## C++ 用法

### 头文件引入

```cpp
#include "AppleProResEncoder/AppleProResEncoder.h"
#include "Misc/FrameRate.h"
```

### 基本用法

以下代码演示如何使用 `FAppleProResEncoder` 直接将 RGB 帧编码为 ProRes `.mov` 文件。

```cpp
// Source: Engine/Plugins/Media/AppleProResMedia/Source/AppleProResMedia/Private/AppleProResEncoderProtocol.cpp

// 1. 配置编码器选项
FAppleProResEncoderOptions Options;
Options.OutputFilename = FPaths::ProjectSavedDir() / TEXT("Output.mov");
Options.Width = 1920;
Options.Height = 1080;
Options.FrameRate = FFrameRate(24, 1);
Options.Codec = EAppleProResEncoderCodec::ProRes_4444XQ; // 高质 + Alpha
Options.ColorPrimaries = EAppleProResEncoderColorPrimaries::CD_HDREC709;
Options.ScanMode = EAppleProResEncoderScanMode::IM_PROGRESSIVE_SCAN;
Options.bWriteAlpha = true; // 包含 Alpha 通道

// 2. 创建编码器并初始化
TUniquePtr<FAppleProResEncoder> Encoder = MakeUnique<FAppleProResEncoder>();
if (!Encoder->Initialize(Options))
{
    // 处理初始化失败（如无法创建文件、解码器加载失败）
    // ...
}

// 3. 写入帧数据
// 假设你已经从渲染目标或其他来源获取了 FImagePixelData
TUniquePtr<FImagePixelData> PixelData = ...;
uint32 FrameIndex = 0;
Encoder->WriteFrame(PixelData.Get(), FrameIndex++);

// 4. 完成编码
Encoder->Finalize();
```

### 进阶用法

对于集成到 Movie Pipeline 或 Movie Graph 的情况，使用 `UMoviePipelineAppleProResOutput` 的内置逻辑。以下展示了如何在自定义渲染管线的 `ProcessFrame` 中利用编码器协议：

```cpp
// Source: Engine/Plugins/Media/AppleProResMedia/Source/AppleProResMedia/Private/AppleProResEncoderProtocol.cpp

// 在 UAppleProResEncoderProtocol::ProcessFrame 内部，可以看到完整的帧处理流程：
void UAppleProResEncoderProtocol::ProcessFrame(FCapturedFrameData InFrame)
{
    // 1. 获取帧载荷中存储的编码选项（包含 Codec、ColorPrimaries 等）
    // 2. 将 FColor 数据转换为特定像素格式（如 RGBA 4444）
    // 3. 调用 CreateProResFile() 创建/复用 ProResFileWriter
    // 4. 使用 ProRes Toolbox SDK 提交帧数据
    // 5. 处理 Alpha 通道（如果启用）
    // 6. 写入时间码轨道
}
```

## Demo 示例

以下 C++ 示例演示了如何使用 `FAppleProResEncoder` 的完整接口，从帧数据生成到编码输出。假设已有 `TArray<FColor>` 形式的图像数据。

**EncoderDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "AppleProResEncoder/AppleProResEncoder.h"
#include "Misc/FrameRate.h"

/**
 * 一个简单的用于测试 ProRes 编码的控制台命令。
 * 用法：在控制台输入 TestProResEncoder 1920 1080 24 100 (宽 高 帧率 帧数)
 */
void RunProResEncoderDemo(uint32 Width, uint32 Height, uint32 FrameRate, uint32 NumFrames);
```

**EncoderDemo.cpp**

```cpp
#include "EncoderDemo.h"

static FAutoConsoleCommand TestProResEncoderCmd(
    TEXT("TestProResEncoder"),
    TEXT("Test ProRes Encoder. Usage: TestProResEncoder 1920 1080 24 100"),
    FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
    {
        if (Args.Num() < 4) return;
        uint32 Width = FCString::Atoi(*Args[0]);
        uint32 Height = FCString::Atoi(*Args[1]);
        uint32 FrameRate = FCString::Atoi(*Args[2]);
        uint32 NumFrames = FCString::Atoi(*Args[3]);
        RunProResEncoderDemo(Width, Height, FrameRate, NumFrames);
    })
);

void RunProResEncoderDemo(uint32 Width, uint32 Height, uint32 FrameRate, uint32 NumFrames)
{
    // 1. 准备测试帧数据（纯色渐变）
    TArray<FColor> FrameBuffer;
    FrameBuffer.SetNum(Width * Height);
    for (uint32 Y = 0; Y < Height; ++Y)
    {
        for (uint32 X = 0; X < Width; ++X)
        {
            FrameBuffer[Y * Width + X] = FColor(
                (uint8)(X * 255 / Width),
                (uint8)(Y * 255 / Height),
                128, 255);
        }
    }

    // 2. 配置编码器选项
    FAppleProResEncoderOptions Options;
    Options.OutputFilename = FPaths::ProjectSavedDir() / TEXT("ProResOutput.mov");
    Options.Width = Width;
    Options.Height = Height;
    Options.FrameRate = FFrameRate(FrameRate, 1);
    Options.Codec = EAppleProResEncoderCodec::ProRes_422HQ;
    Options.ColorPrimaries = EAppleProResEncoderColorPrimaries::CD_HDREC709;
    Options.ScanMode = EAppleProResEncoderScanMode::IM_PROGRESSIVE_SCAN;
    Options.bIncludeAudio = false;
    Options.bWriteAlpha = false;

    // 3. 创建编码器并初始化
    TUniquePtr<FAppleProResEncoder> Encoder = MakeUnique<FAppleProResEncoder>();
    if (!Encoder->Initialize(Options))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize ProRes encoder."));
        return;
    }

    // 4. 写入帧
    for (uint32 Idx = 0; Idx < NumFrames; ++Idx)
    {
        // 模拟动态帧：随时间变化颜色
        for (uint32 Y = 0; Y < Height; ++Y)
        {
            for (uint32 X = 0; X < Width; ++X)
            {
                float Phase = (float)Idx / (float)NumFrames;
                FrameBuffer[Y * Width + X] = FColor(
                    (uint8)(X * 255 / Width),
                    (uint8)(Y * 255 / Height),
                    (uint8)(128 + 127 * FMath::Sin(Phase * PI * 2.0f)),
                    255);
            }
        }

        // 将 FColor 数组包装为 FImagePixelData
        TUniquePtr<TImagePixelData<FColor>> PixelData = MakeUnique<TImagePixelData<FColor>>(
            FIntPoint(Width, Height), FrameBuffer, EImagePixelType::Color);

        if (!Encoder->WriteFrame(PixelData.Get(), Idx))
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to write frame %u."), Idx);
        }
    }

    // 5. 完成编码
    if (!Encoder->Finalize())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to finalize ProRes encoder."));
    }
    else
    {
        UE_LOG(LogTemp, Display, TEXT("ProRes output saved to %s"), *Options.OutputFilename);
    }
}
```

```cpp
// 在你的模块的 .Build.cs 中：
PublicDependencyModuleNames.AddRange(new string[] {
    "AppleProResMedia",
    "ImageWriteQueue"  // 为 FImagePixelData 类型
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 提供 Windows 平台的 WMF 媒体解码器支持，Apple ProRes 解码器继承自 `WmfMediaDecoder`。 |
| `MovieRenderPipeline` | 集成到 MRP 系统中，提供 `UMoviePipelineAppleProResOutput` 输出设置。 |
| `MovieRenderGraph` | 集成到 MRG 系统中，提供 `UMovieGraphAppleProResNode` 输出节点。 |
| `ProResToolbox` | 第三方库封装，提供核心的 Apple ProRes 编码/解码 SDK 接口。这是功能实现的底层依赖。 |

## 维护状态

### 近期更新

- 2025-09-29 `b41cef35` 修复错误处理和潜在内存泄漏 —— 提高稳定性
- 2025-09-26 `6f67c4c3` 优化编辑器加载时间：实现 ProResToolbox 的按需加载 —— 减少启动性能开销
- 2025-09-26 `95d77a2a` 回退变更 —— 回滚 CL46266885
- 2025-09-26 `438a85e5` 优化编辑器加载时间：实现 ProResToolbox 的按需加载 —— 与上一次提交同内容
- 2025-08-07 `ee53759d` MoviePipeline: 更新 MRG 的 Burn-In UI（每个输出节点可单独选择是否启用）—— 用户体验改进

### 维护评价

- **状态**：🟢 活跃维护
- **评价**：该插件是一个较新的插件（约 0 年），但得到了较为积极的维护。近期更新（2025年9月）涉及关键的性能优化（按需加载第三方库）、内存泄漏修复和用户体验改进。虽然创建时间很短，但质量较好，没有发现弃用信号。
- **推荐度**：**强烈推荐**用于需要 Apple ProRes 输出的专业影视制作工作流。插件 APIs 成熟，集成良好，且与 MRP/MRG 系统深度绑定。
- **已知限制**：
  - 播放端仅支持 Windows 平台（通过 WMF），Mac 平台虽列在 `PlatformAllowList` 但解码器实现可能不完全相同。
  - 编码端不支持 Windows ARM64。
  - 不支持服务器目标。
  - 需要主动在项目设置中启用插件（默认禁用）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia)
- [官方文档（可能位于 Epic 文档站点）](https://dev.epicgames.com/documentation/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia/Source/AppleProResMedia)