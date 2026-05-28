# Movie Render Queue

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 影片渲染队列 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Python 示例、材质模板） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline (MRP) 是 UE 中用于高质量离线渲染影片的完整管线系统。它解决了游戏引擎实时渲染与影视级输出之间的鸿沟，提供了：

1. **基于 Sequencer 的渲染队列**：从关卡序列（Level Sequence）中提取镜头（Shot），按队列批量渲染，支持逐镜头配置不同的渲染参数
2. **时间采样与运动模糊**：通过多时间子采样（Temporal Sub-Samples）实现真实的运动模糊效果，而非引擎默认的单帧快照
3. **空间采样与抗锯齿**：支持多空间采样（Spatial Samples）进行超采样抗锯齿
4. **高分辨率平铺渲染**：将超大分辨率图像分割为多个瓦片（Tile）分别渲染后拼合，突破 GPU 内存和纹理尺寸限制
5. **多输出格式**：支持 EXR、PNG、JPG 等图像序列，以及通过命令行编码器输出 MP4、WebM 等视频格式
6. **Burn-in 叠加层**：在渲染画面上叠加帧号、时间码、镜头信息等元数据
7. **命令行无人值守渲染**：支持通过 `-MoviePipelineLocal` 等命令行参数在不打开编辑器 UI 的情况下进行自动化渲染

从 UE 5.4 起，插件引入了 **Movie Graph** 系统（节点化配置），将传统的线性设置列表替换为可编程的图形节点网络，支持更灵活的渲染管线组合、条件分支和渲染层（Render Layers）。

## 使用场景

- 你需要为游戏制作高质量过场动画视频 → 使用 Movie Render Queue 渲染 Level Sequence
- 你需要输出带 Alpha 通道的分层 EXR 用于后期合成 → 配置多层 EXR 输出节点
- 你需要渲染 8K 以上的超大分辨率图像 → 使用 High Resolution Tiling 设置
- 你需要在渲染农场上批量处理渲染任务 → 使用命令行渲染模式 + 自定义 Executor
- 你需要在运行时（Shipping 构建）中渲染视频 → 使用 `UMoviePipelineQueueEngineSubsystem`
- 你需要为每个镜头自定义不同的渲染设置（如不同的光追采样数） → 使用 Movie Graph 或 Shot Override
- 你需要通过 Python 脚本自动化批量渲染 → 使用 `UMovieGraphExecuteScriptNode`
- 你需要快速预览当前视角的渲染结果 → 使用 Quick Render 功能

## 蓝图用法

本插件提供了两套蓝图 API：**传统管线**（`UMoviePipelineBlueprintLibrary`）和 **Movie Graph 管线**（`UMovieGraphBlueprintLibrary`）。Movie Graph 是新系统，建议新项目使用。

### 核心节点 — Movie Graph Library

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetEffectiveFrameRate` | 获取考虑输出设置覆盖后的实际帧率 | `UMovieGraphBlueprintLibrary` |
| `ResolveFilenameFormatArguments` | 将 `{token}` 格式字符串解析为最终文件路径 | `UMovieGraphBlueprintLibrary` |
| `GetDesiredOutputResolution` | 获取用户指定的目标输出分辨率（不含超扫描） | `UMovieGraphBlueprintLibrary` |
| `GetOverscannedResolution` | 获取包含超扫描（Overscan）的输出分辨率 | `UMovieGraphBlueprintLibrary` |
| `GetBackbufferResolution` | 获取实际渲染帧的后缓冲分辨率（含超扫描和分块） | `UMovieGraphBlueprintLibrary` |
| `GetOverscanCropRectangle` | 获取用于裁剪超扫描区域的矩形 | `UMovieGraphBlueprintLibrary` |
| `GetCompletionPercentage` | 获取管线完成百分比（0-1） | `UMovieGraphBlueprintLibrary` |
| `GetOverallOutputFrames` | 获取当前帧号和总帧数 | `UMovieGraphBlueprintLibrary` |
| `GetEstimatedTimeRemaining` | 获取预估剩余渲染时间 | `UMovieGraphBlueprintLibrary` |
| `GetPipelineState` | 获取管线当前状态（Uninitialized/ProducingFrames/Finalize/Export） | `UMovieGraphBlueprintLibrary` |
| `GetCurrentSegmentName` | 获取当前正在渲染的镜头名称 | `UMovieGraphBlueprintLibrary` |
| `GetRootTimecode` / `GetRootFrameNumber` | 获取根序列级别的时间码/帧号 | `UMovieGraphBlueprintLibrary` |
| `GetCurrentShotTimecode` / `GetCurrentShotFrameNumber` | 获取当前镜头级别的时间码/帧号 | `UMovieGraphBlueprintLibrary` |
| `GetCurrentFocusDistance` / `GetCurrentFocalLength` / `GetCurrentAperture` | 获取当前相机的焦距/光圈参数 | `UMovieGraphBlueprintLibrary` |
| `GetCurrentCineCamera` | 获取当前使用的 CineCamera 组件 | `UMovieGraphBlueprintLibrary` |
| `GetCurrentPlayWorld` | 获取当前的 PIE 或 Game 世界 | `UMovieGraphBlueprintLibrary` |
| `NamedResolutionFromProfile` | 从命名分辨率配置文件创建命名分辨率 | `UMovieGraphBlueprintLibrary` |
| `ResolveVersionNumber` | 解析输出文件的版本号 | `UMovieGraphBlueprintLibrary` |

### 核心节点 — 运行时渲染子系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AllocateJob` | 从 Level Sequence 创建渲染任务 | `UMoviePipelineQueueEngineSubsystem` |
| `RenderJob` | 渲染指定的任务 | `UMoviePipelineQueueEngineSubsystem` |
| `RenderQueueWithExecutor` | 使用指定 Executor 类渲染整个队列 | `UMoviePipelineQueueEngineSubsystem` |
| `SetConfiguration` | 设置渲染进度控件和视口行为 | `UMoviePipelineQueueEngineSubsystem` |
| `IsRendering` | 查询是否正在渲染 | `UMoviePipelineQueueEngineSubsystem` |
| `GetQueue` | 获取渲染队列 | `UMoviePipelineQueueEngineSubsystem` |

### 核心节点 — 配置管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindOrAddSettingByClass` | 查找或添加指定类型的设置 | `UMoviePipelineConfigBase` |
| `FindSettingByClass` | 查找指定类型的设置 | `UMoviePipelineConfigBase` |
| `RemoveSetting` | 移除一个设置实例 | `UMoviePipelineConfigBase` |
| `CopyFrom` | 从另一个配置复制设置 | `UMoviePipelineConfigBase` |

### 核心节点 — 渲染层系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddRenderLayer` | 注册一个渲染层 | `UMovieGraphRenderLayerSubsystem` |
| `SetActiveRenderLayerByName` | 按名称激活渲染层 | `UMovieGraphRenderLayerSubsystem` |
| `ClearActiveRenderLayer` | 清除活跃渲染层并撤销修改 | `UMovieGraphRenderLayerSubsystem` |
| `Reset` | 清除所有已跟踪的渲染层和集合 | `UMovieGraphRenderLayerSubsystem` |

### 使用示例（蓝图描述）

**场景：在运行时渲染一段 Level Sequence**

1. 使用 `Get Game Instance Subsystem` 节点获取 `MoviePipeline Runtime Subsystem`
2. 调用 `Allocate Job` 节点，传入你的 `ULevelSequence` 资产
3. 在返回的 `Job` 上调用 `Find Or Add Setting By Class`，添加 `UMovieGraphDeferredPass_Node`（延迟渲染通道）
4. 同样添加输出格式节点，如 `UMovieGraphImageSequenceOutputNode_PNG`
5. 添加 `UMovieGraphGlobalOutputSettingNode` 并设置输出目录
6. 绑定 `OnRenderFinished` 委托来处理渲染完成后的逻辑
7. 调用 `Render Job` 开始渲染

**场景：查询渲染进度**

1. 使用 `Get Completion Percentage` 获取 0-1 的完成百分比
2. 使用 `Get Overall Output Frames` 获取当前帧号和总帧数
3. 使用 `Get Estimated Time Remaining` 获取预估剩余时间
4. 使用 `Get Current Segment Name` 获取当前镜头名称

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipeline.h"
#include "MovieGraphPipeline.h"
#include "MoviePipelineBlueprintLibrary.h"
#include "MovieGraphBlueprintLibrary.h"
#include "MoviePipelineQueueEngineSubsystem.h"
#include "MovieGraphConfig.h"
#include "MoviePipelineExecutor.h"
```

### 基本用法 — 运行时渲染

```cpp
// 来源: Public/MoviePipelineQueueEngineSubsystem.h
// 在 Shipping 构建中运行时渲染 Level Sequence

// 获取运行时子系统
UMoviePipelineQueueEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMoviePipelineQueueEngineSubsystem>();

// 从 Level Sequence 创建任务
ULevelSequence* MySequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MySequence"));
UMoviePipelineExecutorJob* Job = Subsystem->AllocateJob(MySequence);

// 添加渲染设置
UMovieGraphDeferredPass_Node* RenderPass = Cast<UMovieGraphDeferredPass_Node>(
    Job->GetConfiguration()->FindOrAddSettingByClass(UMovieGraphDeferredPass_Node::StaticClass()));

UMovieGraphGlobalOutputSettingNode* OutputSetting = Cast<UMovieGraphGlobalOutputSettingNode>(
    Job->GetConfiguration()->FindOrAddSettingByClass(UMovieGraphGlobalOutputSettingNode::StaticClass()));
OutputSetting->OutputDirectory.Path = TEXT("/Game/RenderOutput");

// 绑定完成回调
Subsystem->OnRenderFinished.AddDynamic(this, &UMyClass::OnRenderFinished);

// 开始渲染
Subsystem->RenderJob(Job);
```

### 基本用法 — Movie Graph Pipeline

```cpp
// 来源: Public/Graph/MovieGraphPipeline.h
// 使用 Movie Graph Pipeline 进行更灵活的渲染

// 初始化 Graph Pipeline
UMovieGraphPipeline* GraphPipeline = NewObject<UMovieGraphPipeline>();

FMovieGraphInitConfig InitConfig;
InitConfig.RendererClass = UMovieGraphDefaultRenderer::StaticClass();
InitConfig.DataSourceClass = UMovieGraphSequenceDataSource::StaticClass();
InitConfig.bRenderViewport = false;

GraphPipeline->Initialize(MyJob, InitConfig);

// 监听完成事件
GraphPipeline->OnMoviePipelineWorkFinished.AddLambda(
    [](FMoviePipelineOutputData OutputData)
    {
        UE_LOG(LogTemp, Log, TEXT("Render finished: %s"), OutputData.bSuccess ? TEXT("Success") : TEXT("Failed"));
    });
```

### 进阶用法 — 自定义脚本回调

```cpp
// 来源: Public/Graph/Nodes/MovieGraphExecuteScriptNode.h
// 实现自定义 MovieGraphScriptBase 用于生命周期回调

UCLASS()
class UMyRenderScript : public UMovieGraphScriptBase
{
    GENERATED_BODY()

public:
    virtual void OnJobStart_Implementation(UMoviePipelineExecutorJob* InJobCopy) override
    {
        // 渲染开始前的准备工作
        UE_LOG(LogTemp, Log, TEXT("Job Started: %s"), *InJobCopy->JobName);
    }

    virtual void OnJobFinished_Implementation(UMoviePipelineExecutorJob* InJobCopy, 
        const FMoviePipelineOutputData& InOutputData) override
    {
        // 渲染完成后的后处理
        if (InOutputData.bSuccess)
        {
            for (const auto& Pair : InOutputData.JobOutputData)
            {
                UE_LOG(LogTemp, Log, TEXT("Generated file: %s"), *Pair.Key);
            }
        }
    }

    virtual void OnShotStart_Implementation(UMoviePipelineExecutorJob* InJobCopy,
        UMoviePipelineExecutorShot* InShotCopy) override
    {
        UE_LOG(LogTemp, Log, TEXT("Shot Started: %s"), *InShotCopy->OuterName);
    }

    virtual bool IsPerShotCallbackNeeded_Implementation() const override
    {
        return true; // 需要每个镜头的回调
    }
};
```

### 进阶用法 — 条件组查询与渲染层

```cpp
// 来源: Public/Graph/MovieGraphRenderLayerSubsystem.h
// 使用渲染层子系统管理渲染层

UMovieGraphRenderLayerSubsystem* LayerSubsystem = 
    UMovieGraphRenderLayerSubsystem::GetFromWorld(GetWorld());

// 创建渲染层并添加修改器
UMovieGraphRenderLayer* MyLayer = NewObject<UMovieGraphRenderLayer>();
MyLayer->SetRenderLayerName(FName(TEXT("LightsOnly")));

// 激活渲染层
LayerSubsystem->AddRenderLayer(MyLayer);
LayerSubsystem->SetActiveRenderLayerByName(FName(TEXT("LightsOnly")));

// 使用完毕后清除
LayerSubsystem->ClearActiveRenderLayer();
```

### 进阶用法 — 命令行编码器

```cpp
// 来源: Public/Graph/Nodes/MovieGraphCommandLineEncoderNode.h
// 通过命令行编码器在渲染后自动生成视频

// 在 Movie Graph 配置中添加命令行编码器节点
UMovieGraphCommandLineEncoderNode* EncoderNode = 
    Graph->CreateNodeByClass<UMovieGraphCommandLineEncoderNode>();

// 配置编码参数
EncoderNode->VideoCodec = TEXT("libx264");
EncoderNode->AudioCodec = TEXT("aac");
EncoderNode->OutputFileExtension = TEXT("mp4");
EncoderNode->CommandLineFormat = TEXT("ffmpeg {VideoInputs} {AudioInputs} {OutputPath}");
```

## Demo 示例

以下示例展示如何创建一个最小的运行时渲染脚本：

```cpp
// MyMovieRenderManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MoviePipelineExecutor.h"
#include "MyMovieRenderManager.generated.h"

UCLASS()
class UMyMovieRenderManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 启动一个简单的影片渲染
    UFUNCTION(BlueprintCallable, Category = "Render")
    void RenderSequence(ULevelSequence* InSequence, const FString& InOutputDirectory);

    // 渲染完成回调
    UFUNCTION()
    void OnRenderFinished(FMoviePipelineOutputData InOutputData);
};
```

```cpp
// MyMovieRenderManager.cpp
#include "MyMovieRenderManager.h"
#include "MoviePipelineQueueEngineSubsystem.h"
#include "MovieGraphGlobalOutputSettingNode.h"
#include "LevelSequence.h"

void UMyMovieRenderManager::RenderSequence(ULevelSequence* InSequence, const FString& InOutputDirectory)
{
    if (!InSequence)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid Level Sequence"));
        return;
    }

    UMoviePipelineQueueEngineSubsystem* Subsystem = 
        GEngine->GetEngineSubsystem<UMoviePipelineQueueEngineSubsystem>();

    if (Subsystem->IsRendering())
    {
        UE_LOG(LogTemp, Warning, TEXT("Already rendering"));
        return;
    }

    // 创建渲染任务
    UMoviePipelineExecutorJob* Job = Subsystem->AllocateJob(InSequence);

    // 配置输出目录
    UMovieGraphGlobalOutputSettingNode* OutputSetting = Cast<UMovieGraphGlobalOutputSettingNode>(
        Job->GetConfiguration()->FindOrAddSettingByClass(
            UMovieGraphGlobalOutputSettingNode::StaticClass()));

    if (OutputSetting)
    {
        OutputSetting->OutputDirectory.Path = InOutputDirectory;
        OutputSetting->bOverwriteExistingOutput = true;
    }

    // 绑定完成回调并渲染
    Subsystem->OnRenderFinished.AddDynamic(this, &UMyMovieRenderManager::OnRenderFinished);
    Subsystem->RenderJob(Job);
}

void UMyMovieRenderManager::OnRenderFinished(FMoviePipelineOutputData InOutputData)
{
    UMoviePipelineQueueEngineSubsystem* Subsystem = 
        GEngine->GetEngineSubsystem<UMoviePipelineQueueEngineSubsystem>();

    // 解除绑定
    Subsystem->OnRenderFinished.RemoveDynamic(this, &UMyMovieRenderManager::OnRenderFinished);

    if (InOutputData.bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Render completed successfully!"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Render failed!"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块，提供 Level Sequence 和轨道支持 |
| `LevelSequence` | 关卡序列资产和播放器 |
| `CinematicCamera` | 提供 `UCineCameraComponent` 和电影级相机参数 |
| `MovieSceneCapture` | 旧版影片捕获基础设施（兼容性） |
| `ImageWriteQueue` | 异步图像写入队列 |
| `OpenEXR` | EXR 文件格式读写支持 |
| `Json` | 清单文件（Manifest）序列化 |
| `Networking` | Executor 的 Socket 通信支持 |
| `HTTP` | Executor 的 HTTP 请求支持 |
| `ConsoleVariablesEditor` | 仅 `MovieRenderPipelineSettings` 模块依赖，用于 CVar 预设管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 添加 EXR 多图层支持 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复 Graph 中渲染层预热导致部分骨骼网格体异常的问题 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回退字母框相关改动以修复兼容性问题 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe Basic 配置 | 为 Basic 配置模式的延迟渲染器添加抗锯齿方法属性 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在 Motion Design 使用 Rundown 页面设置时添加 MRQ 分析埋点 |

### 维护评价

**活跃维护** — Movie Render Pipeline 是 UE 影视管线的核心组件，由 Epic 专人团队持续维护。最近的更新表明以下活跃方向：

1. **Movie Graph 系统持续演进**：不断添加新的节点类型、改进图评估逻辑、增强渲染层系统
2. **nDisplay 集成深化**：EXR 多图层支持等面向虚拟制片场景的增强
3. **Basic 配置模式**：为不熟悉 Movie Graph 的用户提供简化配置入口
4. **bug 修复和稳定性改进**：字母框、骨骼网格体预热等问题的及时修复

该插件自 2019 年创建以来持续活跃更新，从传统管线到 Movie Graph 的迁移表明 Epic 对其长期投入的决心。**强烈推荐使用**，尤其是基于 Movie Graph 的新项目。

> ⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置或 .uproject 中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/movie-render-queue-in-unreal-engine)