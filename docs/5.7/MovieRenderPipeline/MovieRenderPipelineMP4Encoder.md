# Movie Render Pipeline

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline (MRP) 是 UE5 中用于高质量、可控视频渲染的核心系统。它解决了引擎内置渲染功能（如 `Sequencer` 的 `Movie Scene Capture`）在灵活性、可扩展性和专业功能上的不足。其核心目的是提供一个可编程、可配置的渲染管线，允许用户：

1.  **精确控制渲染过程**：通过可组合的“设置”节点（`UMoviePipelineSetting`）来定义渲染的每一个方面，如输出格式、分辨率、抗锯齿、后期处理等。
2.  **支持多通道渲染**：能够同时输出多个渲染通道（如最终图像、法线、深度、自定义通道），并支持将它们合成为最终输出。
3.  **实现复杂的渲染逻辑**：通过“电影图表”（`Movie Graph`）系统，用户可以像搭建蓝图一样，以节点化的方式构建高度定制化的渲染流程。
4.  **集成专业工作流**：内置支持 OCIO（OpenColorIO）色彩管理、Burn-in 信息叠加、以及多种专业视频编码器（如 H.264 MP4）。

简而言之，MRP 是 UE5 中用于生成电影级质量渲染视频的“瑞士军刀”，是游戏过场动画、建筑可视化、虚拟制片等领域的必备工具。

## 使用场景

-   你需要为游戏制作一段 4K、60fps、带有多通道（如景深、运动模糊）的过场动画视频 → 使用 Movie Render Pipeline 配置渲染设置。
-   你需要将渲染输出直接编码为 H.264 MP4 格式，而不是无损的图像序列 → 使用 `MovieRenderPipelineMP4Encoder` 模块。
-   你需要为渲染的每一帧自动叠加时间码、镜头信息等元数据（Burn-in） → 配置 MRP 的 Burn-in 设置。
-   你需要构建一个复杂的渲染流程，例如先渲染一个自定义的深度通道，再将其用于合成最终图像 → 使用 Movie Graph 系统搭建节点。
-   你需要确保渲染输出的颜色与在 DCC 软件（如 Maya, Blender）中看到的完全一致 → 集成 OCIO 配置。

## 蓝图用法

MRP 的蓝图 API 主要围绕配置渲染作业（`UMoviePipelineExecutorJob`）和其下的镜头（`UMoviePipelineExecutorShot`）展开。核心是向作业中添加不同的 `UMoviePipelineSetting` 子类实例来定义渲染行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Movie Pipeline` | 创建一个新的 `UMoviePipeline` 实例，用于执行渲染。 | `UMoviePipelineFunctionLibrary` |
| `Set Configuration` | 为渲染作业设置一个完整的配置资产（`UMoviePipelinePrimaryConfig`）。 | `UMoviePipelineExecutorJob` |
| `Add Setting` | 向配置中动态添加一个渲染设置节点（如输出格式、抗锯齿等）。 | `UMoviePipelinePrimaryConfig` |
| `Set Output Directory` | 设置渲染输出的文件路径。 | `UMoviePipelineExecutorJob` |
| `Set Sequence` | 指定要渲染的关卡序列（`ULevelSequence`）资产。 | `UMoviePipelineExecutorJob` |
| `Set Map` | 指定渲染时要使用的地图（关卡）。 | `UMoviePipelineExecutorJob` |
| `Set Editor Job` | 将作业设置为当前编辑器作业，以便在编辑器中执行。 | `UMoviePipelineEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建并配置一个简单的渲染作业**：
    *   使用 `Create Movie Pipeline` 节点创建一个管线实例。
    *   使用 `Add Job` 节点向管线添加一个作业。
    *   使用 `Set Sequence` 和 `Set Map` 节点为作业指定序列和地图。
    *   使用 `Set Output Directory` 设置输出路径。
    *   使用 `Add Setting` 节点，分别添加 `UMoviePipelineOutputSetting`（设置分辨率、帧率）和 `UMoviePipelineImageSequenceOutput_BMP`（设置输出为BMP序列）。
    *   最后，调用 `Start Pipeline Execution` 节点开始渲染。

2.  **在 Movie Graph 中使用 MP4 输出节点**：
    *   在 Movie Graph 资产中，从右键菜单添加一个 `UMovieGraphMP4EncoderNode`。
    *   在节点的细节面板中，配置 `EncodingRateControl`（编码速率控制模式）、`ConstantRateFactor`（质量因子）或 `AverageBitrateInMbps`（平均比特率）等属性。
    *   将该节点的输出连接到图的最终输出节点。

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipelineMP4EncoderOutput.h"
#include "Graph/MovieGraphMP4EncoderNode.h"
```

### 基本用法

以下代码演示如何在 C++ 中创建并配置一个使用 H.264 MP4 输出的渲染作业。

```cpp
// 来源：基于 MovieRenderPipelineMP4Encoder 模块的公共 API 推断
#include "MoviePipeline.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineMP4EncoderOutput.h"

void SetupMP4RenderJob()
{
    // 1. 创建渲染管线
    UMoviePipeline* Pipeline = NewObject<UMoviePipeline>();

    // 2. 创建一个作业
    UMoviePipelineExecutorJob* Job = Pipeline->GetQueue()->AllocateNewJob(JobName);
    Job->SetSequence(SequenceAsset);
    Job->SetMap(MapAsset);
    Job->SetOutputDirectory(OutputPath);

    // 3. 获取作业的主配置
    UMoviePipelinePrimaryConfig* Config = Job->GetConfiguration();

    // 4. 添加并配置 MP4 输出设置
    UMoviePipelineMP4EncoderOutput* MP4Output = NewObject<UMoviePipelineMP4EncoderOutput>(Config);
    MP4Output->EncodingRateControl = EMoviePipelineMP4EncodeRateControlMode::Quality;
    MP4Output->ConstantRateFactor = 20; // 高质量
    MP4Output->bIncludeAudio = true;
    Config->AddSetting(MP4Output);

    // 5. (可选) 添加其他设置，如分辨率
    UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass(UMoviePipelineOutputSetting::StaticClass());
    OutputSetting->OutputResolution = FIntPoint(1920, 1080);
    OutputSetting->bUseCustomFrameRate = true;
    OutputSetting->OutputFrameRate = FFrameRate(30, 1);

    // 6. 执行渲染（通常通过编辑器或命令行触发）
    // Pipeline->Initialize(Job);
}
```

### 进阶用法

在 Movie Graph 系统中，通过 C++ 创建和注入自定义节点。

```cpp
// 来源：基于 Graph/MovieGraphMP4EncoderNode.h 的接口推断
#include "MovieGraphMP4EncoderNode.h"
#include "MovieGraphPipeline.h"

// 实现一个自定义的评估节点注入器，用于在特定分支注入 MP4 节点
class FMyCustomNodeInjector : public IMovieGraphEvaluationNodeInjector
{
public:
    virtual void InjectNodesPostEvaluation(const FName& InBranchName, UMovieGraphEvaluatedConfig* InEvaluatedConfig, TArray<UMovieGraphSettingNode*>& OutInjectedNodes) override
    {
        // 仅在名为 “FinalOutput” 的分支注入 MP4 节点
        if (InBranchName == FName(“FinalOutput”))
        {
            UMovieGraphMP4EncoderNode* MP4Node = NewObject<UMovieGraphMP4EncoderNode>();
            MP4Node->ConstantRateFactor = 18; // 设置为近乎无损的质量
            MP4Node->bIncludeAudio = true;
            OutInjectedNodes.Add(MP4Node);
        }
    }
};
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个配置了 MP4 输出的渲染管线。

**MyMP4RenderDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMP4RenderDemo.generated.h"

class UMoviePipeline;
class UMoviePipelineExecutorJob;

UCLASS(BlueprintType)
class UMyMP4RenderDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = “Render Demo”)
    void StartMP4Render(ULevelSequence* InSequence, UWorld* InWorld, const FString& InOutputPath);

private:
    UPROPERTY()
    TObjectPtr<UMoviePipeline> CurrentPipeline;
};
```

**MyMP4RenderDemo.cpp**
```cpp
#include “MyMP4RenderDemo.h”
#include “MoviePipeline.h”
#include “MoviePipelineQueue.h”
#include “MoviePipelineMP4EncoderOutput.h”
#include “MoviePipelineOutputSetting.h”
#include “LevelSequence.h”
#include “Engine/World.h”

void UMyMP4RenderDemo::StartMP4Render(ULevelSequence* InSequence, UWorld* InWorld, const FString& InOutputPath)
{
    if (!InSequence || !InWorld)
    {
        UE_LOG(LogTemp, Error, TEXT(“Invalid sequence or world provided.”));
        return;
    }

    // 清理旧的管线
    if (CurrentPipeline)
    {
        CurrentPipeline->Shutdown(true);
        CurrentPipeline = nullptr;
    }

    // 创建新的管线和作业
    CurrentPipeline = NewObject<UMoviePipeline>();
    UMoviePipelineExecutorJob* Job = CurrentPipeline->GetQueue()->AllocateNewJob(FName(“MyMP4Job”));
    Job->SetSequence(InSequence);
    Job->SetMap(InWorld->GetOuter()->GetFName()); // 获取地图包名
    Job->SetOutputDirectory(InOutputPath);

    // 配置输出
    UMoviePipelinePrimaryConfig* Config = Job->GetConfiguration();

    // 设置分辨率和帧率
    UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass(UMoviePipelineOutputSetting::StaticClass());
    OutputSetting->OutputResolution = FIntPoint(1920, 1080);
    OutputSetting->bUseCustomFrameRate = true;
    OutputSetting->OutputFrameRate = FFrameRate(24, 1);

    // 添加 MP4 输出设置
    UMoviePipelineMP4EncoderOutput* MP4Setting = NewObject<UMoviePipelineMP4EncoderOutput>(Config);
    MP4Setting->EncodingRateControl = EMoviePipelineMP4EncodeRateControlMode::Quality;
    MP4Setting->ConstantRateFactor = 22; // 平衡质量与文件大小
    MP4Setting->bIncludeAudio = false; // 本例不包含音频
    Config->AddSetting(MP4Setting);

    // 初始化并开始执行（注意：实际执行通常需要编辑器上下文或命令行）
    CurrentPipeline->Initialize(Job);
    // 在真实场景中，你可能需要监听 `OnMoviePipelineFinished` 委托来获取完成通知。
    UE_LOG(LogTemp, Log, TEXT(“MP4 Render Pipeline Initialized. Execution may require editor context.”));
}
```

## 模块依赖

要使用 `MovieRenderPipelineMP4Encoder` 模块，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | MRP 的核心运行时框架，提供 `UMoviePipeline`, `UMoviePipelineSetting` 等基础类。 |
| `MovieRenderPipelineRenderPasses` | 提供标准的渲染通道实现（如延迟渲染、路径追踪通道），MP4 编码器需要处理这些通道的输出。 |

## 维护状态

### 近期更新

```
- 2025-10-03 ee53759 MoviePipeline: Updated the UX for burn-ins in MRG (each output node can individually opt in or out of burn-ins).
- 2025-09-15 9803c44 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2025-08-20 d3ddbc1 MoviePipeline: Fixed several OCIO issues across MRQ and MRG.
```

### 维护评价

Movie Render Pipeline 是 UE5 中**活跃维护**的核心功能之一。
-   **创建时间**：约 5 年前（2019年），已相对成熟。
-   **更新频率**：近期（2025年）仍有功能性更新（如 Burn-in UX 改进）和重要的 Bug 修复（如 OCIO 问题），表明 Epic 持续投入开发。
-   **功能状态**：该插件是 UE5 影视和过场动画制作流程的基石，功能稳定且不断扩展（如引入 Movie Graph 系统）。
-   **已知限制**：默认未启用（`EnabledByDefault: false`），需要用户手动在插件列表中启用。MP4 编码器目前仅支持 8 位 H.264 输出。
-   **推荐使用**：**强烈推荐**。对于任何需要高质量、可控视频输出的项目，MRP 是官方推荐且功能最强大的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/RenderingAndGraphics/MovieRenderPipeline/) (UE5 官方文档链接，非 .uplugin 内提供)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/RenderCore/MoviePipeline) (测试用例通常位于 Engine/Tests 目录下)