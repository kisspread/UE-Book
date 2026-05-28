# Apple ProRes Media

> Implements video playback and the export of the Apple ProRes Codec.  Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | ProRes编解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-16 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia) | |

## 用途

该插件为 Unreal Engine 提供了对 Apple ProRes 视频编解码器的完整支持。它主要解决了在游戏引擎内部进行高质量视频后期制作和渲染输出的需求。具体来说，它包含两个核心功能：
1.  **编码与导出**：允许用户将引擎渲染的图像序列（如过场动画、影视渲染输出）编码为 .mov 格式的 Apple ProRes 视频文件。ProRes 以其高画质和在非线性编辑软件中的优秀性能而闻名。
2.  **解码与播放**：允许引擎通过 Windows Media Foundation (WMF) 播放使用 Apple ProRes 编码的视频文件。

由于该插件默认未启用 (`EnabledByDefault = false`)，并且主要为专业的视频后期流程服务，因此它通常与 `MovieRenderPipeline` 和 `WmfMedia` 等插件协同工作。

## 使用场景

-   **电影与过场动画渲染输出**：当你需要使用 Movie Render Queue 或 Movie Render Graph 输出一帧帧的高质量视频素材，并交付给后期制作团队时，选择 Apple ProRes 作为输出格式。
-   **高质量游戏录制**：如果你希望录制游戏过程并保留最高的画面质量以进行后期编辑，可以使用该插件提供的 `FAppleProResEncoder` API。
-   **引擎内视频播放**：在你的游戏或应用中需要播放由专业影视设备拍摄的、以 ProRes 格式编码的视频文件。

## 蓝图用法

该插件主要为 **Movie Render Pipeline** 提供输出节点，其核心配置均通过蓝图属性进行设置。

### 核心节点与属性

主要的可配置节点和属性来自两个类：用于新版 Movie Render Graph 的 `UMovieGraphAppleProResNode` 和用于旧版 Movie Pipeline 的 `UMoviePipelineAppleProResOutput`。

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `Quality` | 选择使用的 ProRes 编解码器类型，从 Proxy 到 4444 XQ，质量和文件大小递增。 | `UMovieGraphAppleProResNode` |
| `bIncludeAudio` | 是否在输出的视频文件中包含音频轨道。 | `UMovieGraphAppleProResNode` |
| `OCIOConfiguration` | 配置 Open Color IO 设置，用于在编码前应用专业的颜色空间转换。 | `UMovieGraphAppleProResNode` |
| `bEnableBurnIn` / `BurnInClass` | 配置是否在视频上叠加渲染元数据（如时间码、帧计数等）的“灼伤”效果。 | `UMovieGraphAppleProResNode` |
| `Codec` | 功能与 `Quality` 类似，用于旧版 Movie Pipeline 的编解码器选择。 | `UMoviePipelineAppleProResOutput` |
| `bDropFrameTimecode` | 是否使用掉帧时间码格式（主要针对 29.97fps 或 59.94i 的视频）。 | `UMoviePipelineAppleProResOutput` |
| `MaxNumberOfEncodingThreads` | 限制编码器使用的最大 CPU 线程数（0 表示自动）。 | `UMoviePipelineAppleProResOutput` |

### 使用示例（蓝图描述）

1.  **在 Movie Render Graph 中使用**：
    *   在你的 Movie Render Graph 资产中，从节点列表添加一个 “Apple ProRes Output Node”。
    *   在该节点的细节面板中，根据需要启用并设置 `Quality`、`bIncludeAudio` 等属性。
    *   将此节点连接到 Graph 的输出分支。执行渲染时，视频将被编码为 ProRes 格式的 .mov 文件。

2.  **在旧版 Movie Pipeline 设置中使用**：
    *   在你的 Movie Pipeline Primary Config 中，添加一个 “Movie Pipeline Apple ProRes Output” 设置。
    *   在设置细节面板中，配置 `Codec`、`bDropFrameTimecode` 等属性。
    *   运行渲染作业，即可输出 ProRes 视频。

## C++ 用法

插件的核心编码能力通过 `FAppleProResEncoder` 类提供，主要用于编写自定义的视频输出流程。

### 头文件引入

```cpp
#include "AppleProResEncoder/AppleProResEncoder.h"
```

### 基本用法

使用 `FAppleProResEncoder` 编码一帧数据的基本流程。

```cpp
// 基于 Private/AppleProResMediaModule.h 和 Public/AppleProResEncoder/AppleProResEncoder.h 推断
#include "AppleProResEncoder/AppleProResEncoder.h"
#include "ImagePixelData.h" // FImagePixelData 的来源

// 1. 配置编码选项
FAppleProResEncoderOptions EncoderOptions;
EncoderOptions.OutputFilename = TEXT("/Game/Output/MyVideo.mov");
EncoderOptions.Width = 1920;
EncoderOptions.Height = 1080;
EncoderOptions.FrameRate = FFrameRate(24, 1);
EncoderOptions.Codec = EAppleProResEncoderCodec::ProRes_422HQ;
EncoderOptions.bIncludeAudio = true;

// 2. 创建并初始化编码器
FAppleProResEncoder Encoder(EncoderOptions);
if (!Encoder.Initialize())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to initialize ProRes encoder."));
    return;
}

// 3. 逐帧写入视频数据 (假设你有一个生成 FImagePixelData 的流程)
for (int32 FrameIndex = 0; FrameIndex < TotalFrames; ++FrameIndex)
{
    // 获取或生成当前帧的像素数据
    TUniquePtr<FImagePixelData> PixelData = GenerateFramePixelData(FrameIndex);
    if (PixelData)
    {
        Encoder.WriteFrame(PixelData.Get());
    }
}

// 4. 写入音频数据 (可选，如果 bIncludeAudio 为 true)
TArray<int16> AudioSamples = GetAudioSamplesForCurrentFrame();
Encoder.WriteAudioSample(AudioSamples);

// 5. 完成编码并释放资源 (析构函数会自动调用 Finalize，但显式调用更清晰)
Encoder.Finalize();
```

### 进阶用法

集成 OCIO 颜色管理并用于 Movie Render Graph 的自定义输出节点。

```cpp
// 基于 Private/MovieGraphAppleProResNode.h 推断
#include "MovieGraphAppleProResNode.h"
#include "OpenColorIO/OpenColorIO.h" // OCIO 相关

// 假设你正在实现一个继承自 UMovieGraphVideoOutputNode 的自定义类
void UMyCustomGraphProResNode::WriteFrame_EncodeThread(
    MovieRenderGraph::IVideoCodecWriter* InWriter,
    FImagePixelData* InPixelData,
    /* ... */)
{
    FProResWriter* ProResWriter = static_cast<FProResWriter*>(InWriter);
    if (ProResWriter && ProResWriter->Writer && InPixelData)
    {
        // 应用 OCIO 颜色转换 (如果配置了且没有跳过)
        if (!ProResWriter->bSkipColorConversions && OCIOConfiguration.IsValid())
        {
            // 这里应该有将像素数据转换为 Rec709 线性空间的代码
            // FImagePixelData* TransformedData = ApplyOCIO(InPixelData, OCIOConfiguration, OCIOContext);
            // ProResWriter->Writer->WriteFrame(TransformedData);
        }
        else
        {
            ProResWriter->Writer->WriteFrame(InPixelData);
        }
    }
}
```

## Demo 示例

一个使用 `FAppleProResEncoder` 输出单帧测试图像的最小控制台命令示例。

**ProResDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

DECLARE_LOG_CATEGORY_EXTERN(LogProResDemo, Log, All);
```

**ProResDemo.cpp**
```cpp
#include "ProResDemo.h"
#include "AppleProResEncoder/AppleProResEncoder.h"
#include "ImageUtils.h"
#include "IImageWrapperModule.h"
#include "HAL/IConsoleManager.h"

DEFINE_LOG_CATEGORY(LogProResDemo);

// 创建一个简单的纯色测试图像作为 FImagePixelData
static TUniquePtr<FImagePixelData> CreateTestPixelData(int32 Width, int32 Height, FColor Color)
{
    TArray<FColor> ColorBuffer;
    ColorBuffer.SetNumUninitialized(Width * Height);
    for (FColor& C : ColorBuffer) { C = Color; }

    // 使用 FImageUtils 创建兼容的 FImagePixelData (假设为 BGRA8 格式)
    return FImageUtils::CreateImagePixelData(Width, Height, ERGBFormat::BGRA, ERawImageFormat::BGRA8, ColorBuffer.GetData());
}

static void ProResDemoCommand(const TArray<FString>& Args)
{
    UE_LOG(LogProResDemo, Log, TEXT("Starting Apple ProRes Demo..."));

    const int32 DemoWidth = 1280;
    const int32 DemoHeight = 720;

    // 配置
    FAppleProResEncoderOptions Options;
    Options.OutputFilename = FPaths::ProjectSavedDir() / TEXT("ProResDemo.mov");
    Options.Width = DemoWidth;
    Options.Height = DemoHeight;
    Options.FrameRate = FFrameRate(30, 1);
    Options.Codec = EAppleProResEncoderCodec::ProRes_422LT;
    Options.bIncludeAudio = false; // 演示不包含音频

    FAppleProResEncoder Encoder(Options);
    if (!Encoder.Initialize())
    {
        UE_LOG(LogProResDemo, Error, TEXT("Encoder initialization failed!"));
        return;
    }

    // 写入30帧纯色测试数据 (红色)
    for (int32 i = 0; i < 30; ++i)
    {
        TUniquePtr<FImagePixelData> RedFrame = CreateTestPixelData(DemoWidth, DemoHeight, FColor::Red);
        if (!Encoder.WriteFrame(RedFrame.Get()))
        {
            UE_LOG(LogProResDemo, Error, TEXT("Failed to write frame %d"), i);
            break;
        }
        UE_LOG(LogProResDemo, Log, TEXT("Wrote frame %d"), i);
    }

    // 完成编码
    Encoder.Finalize();
    UE_LOG(LogProResDemo, Log, TEXT("Demo finished. File saved to: %s"), *Options.OutputFilename);
}

// 注册控制台命令
static FAutoConsoleCommand ProResDemoCmd(
    TEXT("ProRes.Demo"),
    TEXT("Writes a 30-frame solid red video using Apple ProRes LT codec"),
    FConsoleCommandWithArgsDelegate::CreateStatic(&ProResDemoCommand)
);
```

## 模块依赖

插件的核心模块 `AppleProResMedia` 依赖于 `WmfMedia` 模块以实现视频播放功能。在你的 `.Build.cs` 文件中，如果需要使用此插件提供的解码能力（播放 ProRes 视频），则需要添加此依赖。

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 依赖此模块实现通过 Windows Media Foundation 播放 Apple ProRes 视频文件的功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `d3e56b35` | MoviePipeline: Updated icons for MRG. | 为 Movie Render Graph 更新了相关图标。 |
| 2026-05-14 | `546ea87d` | MoviePipeline: Fixed several audio present in MRG. | 修复了 Movie Render Graph 中的多个音频相关问题。 |
| 2026-05-12 | `3af0fac2` | MoviePipeline: Added some telemetry for newly-added graph features, and existing MRQ/MRG features. | 为新增和现有的 Movie Render Graph 功能添加了遥测数据。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa. | 修复了格式化字符串中32位与64位参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

该插件自2019年创建以来，作为 Epic Games 官方维护的媒体和渲染管线组件，保持着**稳定维护**的状态。
-   **活跃性**：从近期提交记录看，更新持续且频繁，主要围绕 Movie Render Graph (MRG) 新功能的集成、bug 修复和代码质量改进。
-   **功能性**：作为专业影视工作流的一部分，其功能（编码、解码、管线集成）已趋于成熟和完善。
-   **平台支持**：明确支持 Windows 和 Mac 平台，但要注意 `Win64:arm64` 架构被排除。
-   **推荐使用**：**强烈推荐**给所有需要引擎内高质量视频输出（特别是与后期软件协作）或播放专业视频格式的用户。这是一个稳定、官方维护且功能完整的解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/) （请在官方文档中搜索“Apple ProRes Media”或“Movie Render Pipeline”获取使用指南）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia/Tests) （路径为推断，实际测试可能位于其他位置）