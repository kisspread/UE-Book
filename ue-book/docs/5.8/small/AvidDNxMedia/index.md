# Avid DNxHR/DNxMXF Media Plugin

> Implements video export using Avid DNx Codecs.

| 属性 | 值 |
|---|---|
| 中文名 | Avid DNx 编解码器插件 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvidDNxMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvidDNxMedia) | |

## 用途

该插件为 Unreal Engine 提供了使用 Avid DNxHR 和 DNxMXF 编解码器进行专业视频输出的能力。其核心功能是将引擎渲染出的图像帧（sRGB 8-bit RGBA 或 16-bit 颜色数据）实时编码为 Avid DNxHR（高效压缩）或 DNxMXF（行业标准 MXF 容器）格式的视频文件。

该插件解决了专业影视后期制作工作流中的关键需求：生成与 Avid Media Composer 等专业非线性编辑软件无缝兼容的高质量、高压缩比的代理文件或最终输出文件。它是电影渲染管线（Movie Render Pipeline）和旧版电影渲染管线（Movie Pipeline）的重要组成部分。

## 使用场景

- 你正在使用 Movie Render Pipeline（MRG）或旧版电影渲染管线（Movie Pipeline）进行影视级别渲染，需要输出与 Avid 工作流兼容的 DNxHR 或 DNxMXF 格式视频文件。
- 你需要生成不同质量等级（如 HQ、SQ、LB）的视频代理文件，用于快速预览或在线编辑。
- 你需要在 Windows 64 位平台上进行视频编码输出（不支持 ARM64 和服务器目标）。

## 蓝图用法

该插件主要通过电影渲染管线的输出节点在蓝图中使用，用户可以通过在渲染配置中添加特定节点来启用 DNx 编码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Movie Graph Avid DNxHR Node` | 用于新版电影渲染图（MRG）的 DNxHR 视频输出节点。提供质量、OCIO、Burn-in 等配置。 | `UMovieGraphAvidDNxHRNode` |
| `Movie Pipeline Avid DNx Output` | 用于旧版电影管线（Movie Pipeline）的 DNx 输出节点。 | `UMoviePipelineAvidDNxOutput` |

### 使用示例（蓝图描述）

1. **使用新版电影渲染图 (MRG)**：
   - 在渲染配置的 `Output` 分支下，添加一个 `Movie Graph Avid DNxHR Node`。
   - 在节点细节面板中，可以覆盖 `Quality` 属性（如 `DNxHR HQ 8-bit`）。
   - 配置 `Burn In` 和 `OCIO`（色彩管理）等可选设置。
   - 该节点会自动处理与 Avid DNx 编码器和 MXF 容器写入器的交互。

2. **使用旧版电影管线 (Movie Pipeline)**：
   - 在渲染设置中，添加一个 `Movie Pipeline Avid DNx Output` 设置。
   - 在细节面板中，设置 `Use Compression` 是否启用压缩，以及 `Number of Encoding Threads`（编码线程数）。
   - 输出的文件扩展名自动设置为 `.mxf`。

## C++ 用法

该插件的核心 C++ API 是 `FAvidDNxEncoder` 类，用于直接控制视频编码过程。

### 头文件引入

```cpp
#include "AvidDNxEncoder/AvidDNxEncoder.h"
```

### 基本用法

以下示例展示了如何使用 `FAvidDNxEncoder` 将单帧图像编码并写入 MXF 文件。

```cpp
// 来自 FAvidDNxEncoder 的构造函数和公共接口
#include "AvidDNxEncoder/AvidDNxEncoder.h"

void EncodeSingleFrame()
{
    // 1. 配置编码选项
    FAvidDNxEncoderOptions Options;
    Options.OutputFilename = TEXT("C:\\Output\\MyVideo.mxf");
    Options.Width = 1920;
    Options.Height = 1080;
    Options.Quality = EAvidDNxEncoderQuality::HQ_8bit; // DNxHR HQ 8-bit
    Options.FrameRate = FFrameRate(24, 1); // 24 fps
    Options.bCompress = true;
    Options.NumberOfEncodingThreads = 4;
    Options.bDropFrameTimecode = false;
    Options.StartTimecode = FTimecode(0, 0, 0, 0, false);

    // 2. 创建编码器并初始化
    FAvidDNxEncoder Encoder(Options);
    if (!Encoder.Initialize())
    {
        UE_LOG(LogAvidDNxMedia, Error, TEXT("Failed to initialize Avid DNx encoder."));
        return;
    }

    // 3. 准备一帧图像数据 (8-bit sRGB RGBA)
    // 假设 FrameData 是一个指向 1920*1080*4 字节 RGBA 数据的指针
    const uint8* FrameData = /* ... */;

    // 4. 写入该帧
    if (!Encoder.WriteFrame(FrameData))
    {
        UE_LOG(LogAvidDNxMedia, Error, TEXT("Failed to write frame."));
    }

    // 5. 编码器会在析构时自动调用 Finalize()，将文件写入磁盘。
    // 也可以显式调用 Encoder.Finalize(); 来提前完成。
}
```

### 进阶用法

以下示例展示了如何写入 16-bit 浮点颜色数据（例如来自 HDR 渲染），以及如何处理更复杂的配置。

```cpp
// 假设我们有一帧 16-bit 浮点颜色数据 (FFloat16Color 数组)
TArray<FFloat16Color> HDRFrameData;
HDRFrameData.SetNum(1920 * 1080); // 填充数据...

// 配置选项，可能使用更高质量的 RGB 444 设置
FAvidDNxEncoderOptions Options;
Options.OutputFilename = TEXT("C:\\Output\\HDR_Output.mxf");
Options.Width = 1920;
Options.Height = 1080;
Options.Quality = EAvidDNxEncoderQuality::RGB444_12bit; // DNxHR RGB 444 12-bit
Options.FrameRate = FFrameRate(24, 1);
Options.bCompress = true;
Options.NumberOfEncodingThreads = 8; // 使用更多线程加速编码
Options.bConvertToSrgb = true; // 在编码前将线性颜色转换为 sRGB

FAvidDNxEncoder Encoder(Options);
if (Encoder.Initialize())
{
    // 写入 16-bit 帧数据
    if (!Encoder.WriteFrame_16bit(HDRFrameData.GetData()))
    {
        UE_LOG(LogAvidDNxMedia, Error, TEXT("Failed to write 16-bit frame."));
    }
    // 循环写入更多帧...
}
```

**重要提示**：`FAvidDNxEncoder` 目前**不支持音频**写入。MXF 容器写入器仅处理视频轨道。

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建一个自定义的 Movie Pipeline 输出设置，使用 Avid DNx 编码器。

**MyDNxOutputSetting.h**
```cpp
// MyDNxOutputSetting.h
#pragma once

#include "MoviePipelineVideoOutputBase.h"
#include "AvidDNxEncoder/AvidDNxEncoder.h"
#include "MyDNxOutputSetting.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyDNxOutputSetting : public UMoviePipelineVideoOutputBase
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    EAvidDNxEncoderQuality Quality = EAvidDNxEncoderQuality::HQ_8bit;

protected:
    // UMoviePipelineVideoOutputBase Interface
    virtual TUniquePtr<MovieRenderPipeline::IVideoCodecWriter> Initialize_GameThread(const FString& InFileName, FIntPoint InResolution, EImagePixelType InPixelType, ERGBFormat InPixelFormat, uint8 InBitDepth, uint8 InNumChannels) override;
    virtual bool Initialize_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter) override;
    virtual void WriteFrame_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter, FImagePixelData* InPixelData, TArray<MoviePipeline::FCompositePassInfo>&& InCompositePasses) override;
    virtual void BeginFinalize_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter);
    virtual void Finalize_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter);
    virtual const TCHAR* GetFilenameExtension() const override { return TEXT("mxf"); }
    virtual bool IsAudioSupported() const { return false; }
    // ~UMoviePipelineVideoOutputBase Interface

private:
    struct FMyDNxWriter : public MovieRenderPipeline::IVideoCodecWriter
    {
        TUniquePtr<FAvidDNxEncoder> Encoder;
    };
};
```

**MyDNxOutputSetting.cpp**
```cpp
// MyDNxOutputSetting.cpp
#include "MyDNxOutputSetting.h"
#include "AvidDNxMediaModule.h"

TUniquePtr<MovieRenderPipeline::IVideoCodecWriter> UMyDNxOutputSetting::Initialize_GameThread(const FString& InFileName, FIntPoint InResolution, EImagePixelType InPixelType, ERGBFormat InPixelFormat, uint8 InBitDepth, uint8 InNumChannels)
{
    // 在游戏线程准备 Writer 对象
    FAvidDNxEncoderOptions Options;
    Options.OutputFilename = InFileName;
    Options.Width = InResolution.X;
    Options.Height = InResolution.Y;
    Options.Quality = Quality;
    Options.FrameRate = GetPipeline()->GetMovieScene()->GetDisplayRate();
    Options.bCompress = true;
    Options.NumberOfEncodingThreads = 4;

    TUniquePtr<FMyDNxWriter> Writer = MakeUnique<FMyDNxWriter>();
    Writer->Encoder = MakeUnique<FAvidDNxEncoder>(Options);
    return Writer;
}

bool UMyDNxOutputSetting::Initialize_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter)
{
    // 在编码线程初始化编码器
    FMyDNxWriter* MyWriter = static_cast<FMyDNxWriter*>(InWriter);
    return MyWriter->Encoder->Initialize();
}

void UMyDNxOutputSetting::WriteFrame_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter, FImagePixelData* InPixelData, TArray<MoviePipeline::FCompositePassInfo>&& InCompositePasses)
{
    FMyDNxWriter* MyWriter = static_cast<FMyDNxWriter*>(InWriter);
    // 根据像素数据类型调用对应的写入函数
    // 此处需要根据 InPixelData 的格式进行适配
    // 示例：假设为8-bit RGBA
    if (InPixelData->GetType() == EImagePixelType::Color)
    {
        const FColor* ColorData = static_cast<const FColor*>(InPixelData->GetRawData());
        MyWriter->Encoder->WriteFrame(reinterpret_cast<const uint8*>(ColorData));
    }
}

void UMyDNxOutputSetting::BeginFinalize_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter)
{
    // 编码完成前的准备，可能用于刷新缓冲区
}

void UMyDNxOutputSetting::Finalize_EncodeThread(MovieRenderPipeline::IVideoCodecWriter* InWriter)
{
    FMyDNxWriter* MyWriter = static_cast<FMyDNxWriter*>(InWriter);
    // 显式完成编码器，将文件写入磁盘
    MyWriter->Encoder->Finalize();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | 新版电影渲染图（MRG）的核心框架，是本插件输出节点的基类。 |
| `MovieRenderPipelineCore` | 旧版电影管线（Movie Pipeline）的核心框架。 |
| `OpenColorIO` | 用于支持 OCIO（Open Color IO）色彩管理功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `d3e56b35` | MoviePipeline: Updated icons for MRG. | 更新了电影渲染图中使用的图标。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF。 |
| 2026-04-09 | `65101e2d` | MoviePipeline: Updated core MRG output nodes with a new GetBasicConfigShortDisplayName() method in p | 为核心 MRG 输出节点添加了新的 GetBasicConfigShortDisplayName() 方法。 |
| 2025-10-30 | `c19ee15b` | MoviePipeline: Updated the autocomplete used in MRG to the one used in CAT in order to support MRG t | 更新了 MRG 中的自动补全功能，以支持 MRG 标记。 |
| 2025-08-07 | `ee53759d` | MoviePipeline: Updated the UX for burn-ins in MRG (each output node can individually opt in or out o | 更新了 MRG 中 Burn-in 的用户体验（每个输出节点可独立选择启用或禁用）。 |

### 维护评价

该插件**维护状态良好，处于活跃开发中**。从提交历史看，它随着电影渲染管线（MRG）的演进而持续更新，主要围绕集成新的 MRG 功能（如节点接口、Burn-in 配置、OCIO 支持）和进行底层优化（日志迁移）。

**优势**：
- 作为 Epic 官方提供的专业媒体输出插件，与 MRG 深度集成，功能稳定。
- 持续获得更新，以匹配引擎核心渲染管线的新特性。

**限制与注意事项**：
- 该插件**默认未启用** (`EnabledByDefault: false`)，需要在项目设置或 .uproject 文件中手动启用。
- **平台限制**：仅支持 Windows 64 位系统（排除 ARM64 架构），并且不支持服务器目标 (`TargetDenyList: Server`)。
- **无音频支持**：当前 MXF 容器写入器不支持音频轨道，因此无法输出带声音的视频。

**推荐使用**：如果你的工作流依赖 Avid DNx 编解码器，并且使用 Unreal 的电影渲染管线进行输出，那么强烈推荐启用此插件。它提供了专业的、经过引擎官方集成的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvidDNxMedia)