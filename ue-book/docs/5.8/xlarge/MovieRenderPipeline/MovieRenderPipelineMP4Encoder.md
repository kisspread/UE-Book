# Movie Render Pipeline MP4 Encoder

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 电影渲染MP4编码器 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieRenderPipelineMP4Encoder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

---

## 用途

本模块是 **Movie Render Pipeline (MRQ)** 插件的 MP4/H.264 视频编码子模块，为电影渲染队列提供将渲染帧序列实时编码为 H.264 MP4 视频文件的能力。

**解决的核心问题**：UE 的电影渲染管线默认输出逐帧图像序列（EXR/PNG），需要额外的后期合成软件才能合并为视频文件。本模块通过内置的 H.264 编码器，让渲染管线可以直接输出带音频的 MP4 视频文件，省去了后期转码步骤。

**技术实现**：
- **Windows 平台**：使用 Windows Media Foundation (`IMFSinkWriter`) 进行 H.264 硬件/软件编码
- **其他平台**：提供桩实现（Stub），调用时会打印错误日志，**不支持编码**
- 支持两种 Pipeline 架构：
  - **新 MovieGraph 系统**：`UMovieGraphMP4EncoderNode`（图节点式配置）
  - **旧版 Pipeline**：`UMoviePipelineMP4EncoderOutput`（传统设置式配置）

**为什么需要手动启用**：此插件 `EnabledByDefault=false`，因为 H.264 编码依赖平台特定库（Windows MF），且对大多数专业影视制作流程来说，逐帧 EXR 输出 + 外部合成工具链是更常见的选择。

---

## 使用场景

- **快速预览/原型**：渲染一段 Sequencer 过场动画，直接得到可播放的 MP4 文件用于内部审片
- **社交媒体内容**：为游戏预告片、短视频等内容平台快速导出 H.264 视频
- **Motion Design 工作流**：配合 MRQ 的图节点系统，将运动设计项目直接编码为 MP4
- **带音频的完整视频**：渲染画面的同时录制音频轨道（支持 48kHz 双声道）
- **自定义码率/质量控制**：通过 CRF 或 VBR 模式精确控制输出文件大小和画质
- **OCIO 色彩管理**：在编码前应用 OpenColorIO 色彩转换，确保输出色彩正确

---

## 蓝图用法

### 核心枚举

| 枚举 | 说明 | 可用值 |
|---|---|---|
| `EMoviePipelineMP4EncodeRateControlMode` | 码率控制模式 | `Quality`（质量优先）、`VariableBitRate`（可变码率）、`ConstantBitRate`（恒定码率，隐藏） |
| `EMoviePipelineMP4EncodeProfile` | H.264 编码配置 | `Baseline`、`Main`、`High` |
| `EMoviePipelineMP4EncodeLevel` | 编码级别 | `Auto`、`Level1` ~ `Level5_2`（共 18 级） |

### MovieGraph 节点配置（UMovieGraphMP4EncoderNode）

这是新 MovieGraph 系统中的 MP4 编码节点，通过属性覆盖（Override）机制支持图层级别的参数控制。

| 属性 | 类型 | 说明 |
|---|---|---|
| `EncodingRateControl` | `EMoviePipelineMP4EncodeRateControlMode` | 码率控制模式 |
| `AverageBitrateInMbps` | `float` | 平均码率（Mbps），如 1080p30 建议 8，4K 建议 45 |
| `MaxBitrateInMbps` | `float` | 最大码率（Mbps），仅限 Constrained 模式 |
| `ConstantRateFactor` | `int32` | CRF 值（16-51），16 最高质量，51 最低质量 |
| `EncodingProfile` | `EMoviePipelineMP4EncodeProfile` | H.264 Profile |
| `EncodingLevel` | `EMoviePipelineMP4EncodeLevel` | H.264 Level |
| `bIncludeAudio` | `bool` | 是否包含音频轨道 |
| `OCIOConfiguration` | `FOpenColorIODisplayConfiguration` | OCIO 色彩配置 |
| `OCIOContext` | `TMap<FString, FString>` | OCIO 上下文键值对（支持 `{shot_name}` 等格式标记） |
| `bEnableBurnIn` | `bool` | 是否生成 Burn-in 水印 |
| `BurnInClass` | `FSoftClassPath` | Burn-in Widget 类 |
| `bCompositeOntoFinalImage` | `bool` | 是否将 Burn-in 合成到最终图像上 |

### 旧版 Pipeline 配置（UMoviePipelineMP4EncoderOutput）

旧版管线的 MP4 输出设置，属性与 Graph 节点类似但更简单：

| 属性 | 类型 | 说明 |
|---|---|---|
| `EncodingRateControl` | `EMoviePipelineMP4EncodeRateControlMode` | 默认 `Quality`（与 Graph 节点默认 `VariableBitRate` 不同） |
| `AverageBitrateInMbps` | `float` | 平均码率（Mbps） |
| `MaxBitrateInMbps` | `float` | 最大码率（Mbps） |
| `ConstantRateFactor` | `int32` | CRF 值（16-51） |
| `EncodingProfile` | `EMoviePipelineMP4EncodeProfile` | H.264 Profile |
| `EncodingLevel` | `EMoviePipelineMP4EncodeLevel` | H.264 Level |
| `bIncludeAudio` | `bool` | 是否包含音频 |

### 使用示例（蓝图描述）

**MovieGraph 系统中添加 MP4 编码输出**：
1. 在 MovieGraph 编辑器中，右键 → Add Output → H.264 MP4
2. 选中新创建的 MP4 编码节点
3. 在 Details 面板中设置 `EncodingRateControl` 为 `Quality`
4. 设置 `ConstantRateFactor` 为 18（近无损质量）
5. 勾选 `bIncludeAudio` 以包含音频
6. 如需 OCIO 色彩管理，勾选 `bOverride_OCIOConfiguration` 并配置 OCIO 设置
7. 通过图层覆盖（Override）机制，可为不同分支（Branch）设置不同的编码参数

---

## C++ 用法

### 头文件引入

```cpp
// MovieGraph 节点
#include "Graph/MovieGraphMP4EncoderNode.h"

// 旧版 Pipeline 输出
#include "MoviePipelineMP4EncoderOutput.h"

// 通用枚举和选项结构（Private，如需直接使用底层编码器）
#include "MoviePipelineMP4EncoderCommon.h"
```

### 基本用法（MovieGraph 系统）

使用 `UMovieGraphMP4EncoderNode` 配置图节点式的 MP4 输出：

```cpp
#include "Graph/MovieGraphMP4EncoderNode.h"

void ConfigureMP4Output(UMovieGraphEvaluatedConfig* EvaluatedConfig)
{
    // 获取或创建 MP4 编码节点
    UMovieGraphMP4EncoderNode* MP4Node = NewObject<UMovieGraphMP4EncoderNode>();
    
    // 启用参数覆盖
    MP4Node->bOverride_EncodingRateControl = true;
    MP4Node->EncodingRateControl = EMoviePipelineMP4EncodeRateControlMode::Quality;
    
    MP4Node->bOverride_ConstantRateFactor = true;
    MP4Node->ConstantRateFactor = 18;  // 近无损质量 (16-51)
    
    MP4Node->bOverride_bIncludeAudio = true;
    MP4Node->bIncludeAudio = true;
    
    MP4Node->bOverride_AverageBitrateInMbps = true;
    MP4Node->AverageBitrateInMbps = 12.f;  // 12 Mbps
    
    // 配置 OCIO（可选）
    MP4Node->bOverride_OCIOConfiguration = true;
    // MP4Node->OCIOConfiguration = ...;
}
```

### 基本用法（旧版 Pipeline）

使用 `UMoviePipelineMP4EncoderOutput` 配置传统管线的 MP4 输出：

```cpp
#include "MoviePipelineMP4EncoderOutput.h"
#include "MoviePipeline.h"

void SetupMP4Output(UMoviePipeline* Pipeline)
{
    // 获取输出设置容器
    UMoviePipelineOutputBase* OutputSetting = Pipeline->FindOrAddSettingForShot<UMoviePipelineMP4EncoderOutput>(nullptr);
    UMoviePipelineMP4EncoderOutput* MP4Output = Cast<UMoviePipelineMP4EncoderOutput>(OutputSetting);
    
    if (MP4Output)
    {
        MP4Output->EncodingRateControl = EMoviePipelineMP4EncodeRateControlMode::VariableBitRate;
        MP4Output->AverageBitrateInMbps = 8.f;
        MP4Output->bIncludeAudio = true;
    }
}
```

### 进阶用法（底层编码器直接调用）

在 Windows 平台上直接使用 `FMoviePipelineMP4Encoder` 进行视频编码（非管线集成场景）：

```cpp
#include "MoviePipelineMP4EncoderCommon.h"

#if PLATFORM_WINDOWS
#include "Windows/MoviePipelineMP4Encoder.h"
#else
#include "GenericPlatform/MoviePipelineMP4Encoder.h"
#endif

void DirectMP4Encoding()
{
    // 配置编码选项
    FMoviePipelineMP4EncoderOptions Options;
    Options.OutputFilename = FPaths::ProjectSavedDir() / TEXT("Output/test.mp4");
    Options.Width = 1920;
    Options.Height = 1080;
    Options.FrameRate = FFrameRate(30, 1);
    Options.bIncludeAudio = true;
    Options.AudioChannelCount = 2;
    Options.AudioSampleRate = 48000;
    Options.EncodingRateControl = EMoviePipelineMP4EncodeRateControlMode::Quality;
    Options.CommonConstantRateFactor = 18;
    Options.EncodingProfile = EMoviePipelineMP4EncodeProfile::High;
    Options.EncodingLevel = EMoviePipelineMP4EncodeLevel::Auto;
    
    // 创建编码器实例
    FMoviePipelineMP4Encoder Encoder(Options);
    
    // 初始化（Windows 平台使用 Media Foundation）
    if (Encoder.Initialize())
    {
        // 写入帧数据（RGB 格式，每像素 3 字节）
        TArray<uint8> FrameData;
        FrameData.SetNumUninitialized(Options.Width * Options.Height * 3);
        
        // ... 填充帧数据 ...
        
        Encoder.WriteFrame(FrameData.GetData());
        
        // 写入音频样本
        TArray<int16> AudioSamples;
        AudioSamples.SetNumUninitialized(2048);
        // ... 填充音频数据 ...
        
        Encoder.WriteAudioSample(AudioSamples);
        
        // 完成编码并写入文件
        Encoder.Finalize();
    }
    else
    {
        // 非 Windows 平台会在此处失败并打印错误日志
        UE_LOG(LogMovieRenderPipeline, Error, TEXT("Failed to initialize MP4 encoder."));
    }
}
```

> **注意**：底层 `FMoviePipelineMP4Encoder` 在非 Windows 平台返回 Stub 实现，所有操作均为无效操作并返回 `false`。

---

## Demo 示例

### 自定义 MP4 编码输出节点（MovieGraph）

```cpp
// MyCustomMP4Node.h
#pragma once

#include "Graph/MovieGraphMP4EncoderNode.h"
#include "MyCustomMP4Node.generated.h"

/**
 * 自定义 MP4 编码节点，预设了特定的编码参数。
 * 可直接作为图节点使用，无需手动配置各项参数。
 */
UCLASS(BlueprintType)
class UMyCustomMP4Node : public UMovieGraphMP4EncoderNode
{
    GENERATED_BODY()

public:
    UMyCustomMP4Node()
    {
        // 预设编码参数
        bOverride_EncodingRateControl = true;
        EncodingRateControl = EMoviePipelineMP4EncodeRateControlMode::Quality;
        
        bOverride_ConstantRateFactor = true;
        ConstantRateFactor = 18;
        
        bOverride_bIncludeAudio = true;
        bIncludeAudio = true;
        
        bOverride_bEnableBurnIn = true;
        bEnableBurnIn = true;
        bCompositeOntoFinalImage = true;
    }

#if WITH_EDITOR
    virtual FText GetNodeTitle(const bool bGetDescriptive = false) const override
    {
        return NSLOCTEXT("MyCustomMP4", "NodeTitle", "Custom H.264 MP4");
    }
#endif
};
```

### 通过 Python 脚本批量配置 MP4 输出

```cpp
// 在编辑器工具中通过 C++ 调用脚本化配置
#include "MoviePipelineQueueSubsystem.h"
#include "MoviePipelineOutputSetting.h"
#include "MoviePipelineMP4EncoderOutput.h"

void BatchConfigureMP4Jobs(UMoviePipelineQueue* Queue)
{
    for (UMoviePipelineExecutorJob* Job : Queue->GetJobs())
    {
        UMoviePipeline* Pipeline = Job->GetConfiguration();
        if (!Pipeline) continue;
        
        // 添加 MP4 输出
        UMoviePipelineMP4EncoderOutput* MP4Output = Cast<UMoviePipelineMP4EncoderOutput>(
            Pipeline->FindOrAddSettingForShot<UMoviePipelineMP4EncoderOutput>(nullptr)
        );
        
        if (MP4Output)
        {
            // 根据分辨率自动设置码率
            UMoviePipelineOutputSetting* OutputSetting = Pipeline->FindSetting<UMoviePipelineOutputSetting>();
            if (OutputSetting)
            {
                int32 Width = OutputSetting->OutputResolution.X;
                
                if (Width >= 3840)  // 4K
                {
                    MP4Output->AverageBitrateInMbps = 45.f;
                }
                else if (Width >= 1920)  // 1080p
                {
                    MP4Output->AverageBitrateInMbps = 8.f;
                }
                else  // 720p or lower
                {
                    MP4Output->AverageBitrateInMbps = 4.f;
                }
            }
        }
    }
}
```

---

## 模块依赖

MovieRenderPipelineMP4Encoder 的关键依赖（从代码结构推断）：

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | 基础管线框架，提供 `UMoviePipelineVideoOutputBase`、`IVideoCodecWriter` 等基类 |
| `MovieRenderPipelineRenderPasses` | MovieGraph 节点基类 `UMovieGraphVideoOutputNode`、`IMovieGraphEvaluationNodeInjector` |
| `MediaFoundation` (Windows SDK) | 底层 H.264 编码器实现，通过 `IMFSinkWriter` 进行视频/音频编码 |

> **平台限制**：H.264 编码仅在 Windows 平台可用，依赖 Windows Media Foundation。其他平台的 `FMoviePipelineMP4Encoder` 为空桩实现。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 添加 EXR 多图层支持 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复 Graph 中图层预热导致骨骼网格体异常的问题 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回退信封比（Letterboxing）相关改动 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe | 为 Deferred 渲染器的 Basic 配置添加抗锯齿方法属性 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在运动设计 Rundown Page 中添加 MRQ 分析统计 |

> **注意**：以上 commit 涉及整个 MovieRenderPipeline 插件目录，并非全部针对 MP4 编码器模块。MP4 编码器模块本身更新频率较低，核心编码逻辑已趋稳定。

### 维护评价

- **创建时间**：2019 年 10 月，作为 MRQ 初始版本的一部分引入
- **维护状态**：**活跃维护中** — 整个 MovieRenderPipeline 插件持续收到功能性更新（最近一次 2026-05-26），包括 MovieGraph 系统的持续完善
- **编码器稳定性**：MP4 编码器核心逻辑成熟稳定，底层依赖 Windows Media Foundation，较少需要修改
- **已知限制**：
  - 仅支持 Windows 平台编码，其他平台为桩实现
  - 仅输出 8-bit H.264（类名 `H.264 MP4 [8bit]`），不支持 HDR/10-bit 输出
  - 旧版 `UMoviePipelineMP4EncoderOutput` 和新版 `UMovieGraphMP4EncoderNode` 两套 API 并存，部分属性默认值不同
- **推荐使用**：✅ 推荐。适合需要快速导出可播放视频的场景，但专业影视制作建议使用 EXR 序列 + 外部合成工具

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline/Source/MovieRenderPipelineMP4Encoder)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/MovieRenderPipeline/)（MRQ 整体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests)（插件级测试目录，如存在）