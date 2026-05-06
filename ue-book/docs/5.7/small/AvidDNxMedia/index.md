# Avid DNxHR/DNxMXF Media Plugin

> Implements video export using Avid DNx Codecs.

| 属性 | 值 |
|---|---|
| 中文名 | Avid DNx 编码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvidDNxMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvidDNxMedia) | |

## 用途

Avid DNxHR/DNxMXF Media Plugin 提供了将虚幻引擎渲染输出编码为 **Avid DNxHR** 或 **DNxMXF** 格式视频的能力。该格式广泛用于影视后期制作（如 Avid Media Composer），支持多种质量和色深（8-bit 到 12-bit、YUV 4:2:2 或 RGB 4:4:4）。插件通过 **Movie Render Pipeline (MRQ)** 和 **Movie Graph (MRG)** 系统集成，允许用户在渲染设置中选择 DNx 输出，并控制压缩/未压缩、线程数等参数。

该插件解决的核心问题：在需要以非压缩或轻度压缩的高质量格式（如 DNxHR）交付渲染片段时，直接导出 MXF 容器文件，避免二次转码，保证颜色精度和编辑兼容性。

## 使用场景

- 你在制作影视级短片或广告，需要输出 DNxHR 编码的 MXF 文件用于后期调色和剪辑。
- 使用 Movie Render Queue（MRQ）批量渲染镜头，希望得到专业后期格式，而非 H.264/H.265。
- 使用 Movie Graph（MRG）构建脚本化渲染管线，需要支持 DNx 输出的节点。
- 需要高色深（10-bit 或 12-bit）编码以保留更多色彩信息。

## 蓝图用法

插件主要通过 **MRQ 输出设置** 和 **MRG 节点** 暴露配置，很少有须要蓝图手动调用的底层 API。你可以在蓝图或关卡蓝图中引用 `UMoviePipelineAvidDNxOutput` 或 `UMovieGraphAvidDNxHRNode` 类型，但通常不需要编写逻辑，只需在渲染设置中勾选并调整参数。

### 蓝图可访问属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bUseCompression` | 是否使用有损压缩（为 true 时使用 DNxHR 压缩编码，false 时输出未压缩数据） | `UMoviePipelineAvidDNxOutput` |
| `NumberOfEncodingThreads` | 编码线程数（1-64，默认 4） | `UMoviePipelineAvidDNxOutput` |
| `Quality` | 编码质量（见下方枚举值） | `UMovieGraphAvidDNxHRNode`（通过重载的 Overrides） |
| `bUncompressed` | 是否输出未压缩的 RGB 或 YUV 数据（仅用于旧式 `UAvidDNxEncoderProtocol`） | `UAvidDNxEncoderProtocol` |

### 编码质量枚举

| 枚举值 | 显示名称 | 说明 |
|---|---|---|
| `DNxHR RGB 444 12-bit` | 4:4:4 RGB 12-bit，画质最高 | 对应 `EAvidDNxEncoderQuality::RGB444_12bit` |
| `DNxHR HQX 10-bit` | 4:2:2 YCbCr 10-bit | 对应 `EAvidDNxEncoderQuality::HQX_10bit` |
| `DNxHR HQ 8-bit` | 4:2:2 YCbCr 8-bit（默认） | 对应 `EAvidDNxEncoderQuality::HQ_8bit` |
| `DNxHR SQ 8-bit` | 标准质量 4:2:2 8-bit | 对应 `EAvidDNxEncoderQuality::SQ_8bit` |
| `DNxHR LB 8-bit` | 低带宽 4:2:2 8-bit | 对应 `EAvidDNxEncoderQuality::LB_8bit` |

## C++ 用法

### 头文件引入

```cpp
// 使用 FAvidDNxEncoder 核心编码类
#include "AvidDNxEncoder/AvidDNxEncoder.h"

// 使用 MRQ 输出类
#include "MoviePipelineAvidDNxOutput.h"

// 使用 MRG 输出节点
#include "MovieGraphAvidDNxHRNode.h"
```

### 基本用法

#### 直接使用 FAvidDNxEncoder 编码（无管道脚本）

此方式适用于需要在代码中手动编码帧序列的场景。

```cpp
// 来源: Plugins/Media/AvidDNxMedia/Source/AvidDNxMedia/Private/AvidDNxEncoder.cpp

// 1. 创建选项结构体
FAvidDNxEncoderOptions Options;
Options.OutputFilename = FPaths::ProjectSavedDir() / TEXT("Output.mxf");
Options.Width = 1920;
Options.Height = 1080;
Options.Quality = EAvidDNxEncoderQuality::HQ_8bit;
Options.FrameRate = FFrameRate(24, 1);
Options.bCompress = true;
Options.NumberOfEncodingThreads = 4;

// 2. 创建编码器
TUniquePtr<FAvidDNxEncoder> Encoder = MakeUnique<FAvidDNxEncoder>(Options);

// 3. 初始化
if (Encoder->Initialize())
{
    // 4. 逐帧写入（假设你有 TArray<FColor> 的像素数据）
    TArray<FColor> Pixels; // 1920*1080 大小
    // ... 填充像素数据
    Encoder->WriteFrame(Pixels.GetData());

    // 5. 完成
    Encoder->Finalize();
}
```

#### 在 MRQ 自定义管线中使用 `UMoviePipelineAvidDNxOutput`

通常你直接通过蓝图或配置添加此输出，但也可以通过 C++ 自定义设置：

```cpp
// 假设你有 UMoviePipeline* Pipeline
UMoviePipelineAvidDNxOutput* OutputNode = Pipeline->FindSetting<UMoviePipelineAvidDNxOutput>();
if (OutputNode)
{
    OutputNode->bUseCompression = true;
    OutputNode->NumberOfEncodingThreads = 8;
}
```

### 进阶用法

#### 结合 Movie Graph 定制节点

`UMovieGraphAvidDNxHRNode` 继承自 `UMovieGraphVideoOutputNode`，并实现了 `IMovieGraphEvaluationNodeInjector`。你可以通过重载其虚函数来定制初始化、帧写入和最终化逻辑。例如，在自定义节点中读取特定像素数据并传递给编码器：

```cpp
// 来自 MovieGraphAvidDNxHRNode.cpp 的简化示例
void UMovieGraphAvidDNxHRNode::WriteFrame_EncodeThread(
    MovieRenderGraph::IVideoCodecWriter* InWriter,
    FImagePixelData* InPixelData,
    TArray<FMovieGraphPassData>&& InCompositePasses,
    TObjectPtr<UMovieGraphEvaluatedConfig> InEvaluatedConfig,
    const FString& InBranchName)
{
    FAvidWriter* AvidWriter = static_cast<FAvidWriter*>(InWriter);
    check(AvidWriter);

    // 将像素数据转换为编码器需要的格式
    TUniquePtr<FImagePixelData> ConvertedPixelData = PreprocessPixelData(InPixelData);
    void* RawData = ConvertedPixelData->GetData();

    AvidWriter->Writer->WriteFrame((uint8*)RawData);
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，使用 Movie Render Pipeline (MRQ) 输出 DNxHR 编码的 MXF 文件。

### .h 文件（YourRenderSubsystem.h）

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MoviePipeline.h"
#include "MoviePipelineAvidDNxOutput.h"
#include "YourRenderSubsystem.generated.h"

UCLASS()
class UYourRenderSubsystem : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Render")
    void StartAvidDNxRender();
};
```

### .cpp 文件（YourRenderSubsystem.cpp）

```cpp
#include "YourRenderSubsystem.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineImageSequenceOutput.h"
#include "MoviePipelineAvidDNxOutput.h"
#include "MoviePipelineOutputSetting.h"

void UYourRenderSubsystem::StartAvidDNxRender()
{
    // 1. 创建队列和任务
    UMoviePipelineQueue* Queue = NewObject<UMoviePipelineQueue>();
    UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob(UMoviePipelineExecutorJob::StaticClass());
    Job->Map = FSoftObjectPath(TEXT("/Game/YourLevel.YourLevel"));
    Job->Author = TEXT("YourName");

    // 2. 创建主配置
    UMoviePipelinePrimaryConfig* Config = NewObject<UMoviePipelinePrimaryConfig>();
    // 输出设置：分辨率、帧率等
    UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSetting<UMoviePipelineOutputSetting>();
    OutputSetting->OutputResolution = FIntPoint(1920, 1080);
    OutputSetting->OutputFrameRate = FFrameRate(24, 1);
    OutputSetting->bUseCustomPlaybackRange = false;

    // 3. 添加 Avid DNx 输出
    UMoviePipelineAvidDNxOutput* AvidOutput = Config->FindOrAddSetting<UMoviePipelineAvidDNxOutput>();
    AvidOutput->bUseCompression = true;
    AvidOutput->NumberOfEncodingThreads = 4;

    // 4. 将配置应用到任务
    Job->SetConfiguration(Config);
    Queue->SetJobs({ Job });

    // 5. 启动渲染
    // 注意：你需要一个 UMoviePipelineExecutor 对象来执行队列
    // 此处简化，直接获取默认执行器
    if (UMoviePipelineExecutorBase* Executor = UMoviePipelineEditorBlueprintLibrary::CreateExecutor(GetWorld()))
    {
        Executor->Execute(Queue);
    }
}
```

> **注意**：上述示例假设你有合适的 `UMoviePipelineEditorBlueprintLibrary` 和默认执行器。实际使用时需要根据项目配置调整。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | MRQ 核心管线，提供输出设置基类、队列执行等 |
| `AVIDDNXCODEC`（第三方） | 编码器 SDK，处理视频压缩/未压缩编码（自动引用） |

**其他常见依赖**（无需额外列出）：`Core`, `CoreUObject`, `Engine`, `MediaUtils`, `ImageWriteQueue` 等。

## 维护状态

### 近期更新

- 2025-08-07 ee53759d — MoviePipeline: Updated the UX for burn-ins in MRG (each output node can individually opt in or out of burn-ins)
- 2025-06-18 d3ddbc1a — MoviePipeline: Fixed several OCIO issues across MRQ and MRG.
- 2025-06-03 942a4020 — Disable DNxSDK on Windows Arm64 (平台兼容性修复)
- 2024-11-26 7c7c5114 — MoviePipeline: Fixed issue that caused the "Avid DNxHR/DNxMXF Media" plugin to not compile properly (编译修复)
- 2024-11-05 150ded3f — MovieRenderPipeline: Added functionality to crop overscan from non-exr output formats. (初始功能添加)

### 维护评价

插件创建于 2024 年 11 月，随 UE 5.5 发布。当前仍处于早期维护阶段，近几个月持续有功能性更新（烧录、OCIO、平台禁用 Arm64 等）。没有发现废弃或停滞迹象。项目积极适配 MRQ 和 MRG 两个管线，推荐在需要 DNx 输出时使用。**注意事项**：
- 当前仅支持 Windows x64 平台（并且明确禁止 Arm64 和 Server 目标）。
- 必须依赖第三方 Avid DNx SDK（自动包含，无需手动安装）。
- 默认启用为 false，需在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvidDNxMedia)
- [官方文档（MRQ 概述）](https://docs.unrealengine.com/5.4/en-US/movie-render-queue-in-unreal-engine/)（插件自身无独立文档，请参考 MRQ 视频输出章节）