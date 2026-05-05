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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline (MRP) 是一个专业级的渲染解决方案，用于从 Unreal Engine 中生成高质量的最终渲染视频。它解决了传统实时渲染在输出电影级质量视频时面临的诸多挑战，例如：
- **高分辨率与高帧率输出**：支持远超显示器分辨率的渲染（如 8K），并能以任意帧率输出。
- **精确的时间采样**：通过多时间采样（Temporal Sampling）实现高质量的运动模糊和抗锯齿，消除实时渲染中的闪烁和噪点。
- **多通道渲染**：能够同时输出多个渲染通道（如基础颜色、法线、深度、自定义通道等），便于后期合成。
- **确定性渲染**：确保每次渲染的结果完全一致，不受实时运行状态影响。
- **自动化与批处理**：支持通过队列和执行器自动化处理多个渲染任务，适合无人值守的渲染农场。
- **高级色彩管理**：集成 OpenColorIO (OCIO) 进行精确的色彩空间转换和管理。

该插件包含两套系统：传统的 **Movie Render Queue (MRQ)** 和更新的、更灵活的基于节点图的 **Movie Render Graph (MRG)**。MRG 允许用户通过可视化节点图来构建和配置复杂的渲染管线。

## 使用场景

- **游戏过场动画**：为游戏制作电影级质量的过场动画序列。
- **产品可视化**：渲染高质量的产品展示视频或动画。
- **建筑可视化**：生成逼真的建筑漫游和室内设计展示视频。
- **虚拟制片**：为虚拟制片流程提供高质量的渲染输出。
- **游戏预告片与宣传片**：制作用于市场营销的高质量游戏视频。
- **技术演示与艺术创作**：任何需要从 UE 场景中提取高质量视频素材的场合。

## 蓝图用法

MRP 提供了丰富的蓝图 API，主要集中在执行器、配置和调试方面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 使用指定的执行器开始渲染队列中的所有作业。 | `UMoviePipelineExecutorBase` |
| `ExecuteDelayed` | (Python 宿主执行器) 延迟执行，用于 Python 脚本集成。 | `UMoviePipelinePythonHostExecutor` |
| `CancelAllJobs` | 取消当前执行器正在处理的所有作业。 | `UMoviePipelineExecutorBase` |
| `CancelCurrentJob` | 取消当前正在渲染的单个作业。 | `UMoviePipelineExecutorBase` |
| `IsRendering` | 查询执行器当前是否正在渲染。 | `UMoviePipelineExecutorBase` |
| `SetSubGraphAsset` | (MRG) 设置子图节点引用的图资产。 | `UMovieGraphSubgraphNode` |
| `GetSubgraphAsset` | (MRG) 获取子图节点引用的图资产。 | `UMovieGraphSubgraphNode` |
| `SetPinProperties` | (MRG) 设置重路由节点的引脚属性。 | `UMovieGraphRerouteNode` |
| `ClearParameterValues` | (MRG) 清除材质参数集合修改器中设置的参数值。 | `UMovieGraphMaterialParameterCollectionModifier` |

### 使用示例（蓝图描述）

1.  **基本渲染**：
    *   创建一个 `UMoviePipelineQueue` 资产，并添加一个或多个 `UMoviePipelineExecutorJob`。
    *   在蓝图中，获取 `UMoviePipelineInProcessExecutor` 的实例（或创建一个）。
    *   调用 `Execute` 节点，传入队列对象。渲染将在当前进程中开始。
    *   监听 `OnIndividualJobFinished` 或 `OnExecutorFinished` 委托来获取渲染完成通知。

2.  **使用 Python 宿主执行器**：
    *   创建一个继承自 `UMoviePipelinePythonHostExecutor` 的 Python 类。
    *   在蓝图中，设置该执行器的 `ExecutorClass` 属性为你的 Python 类。
    *   调用 `Execute`。引擎会加载关卡，然后调用你的 Python 类的 `ExecuteDelayed` 方法，你可以在其中编写自定义的渲染逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipeline.h"
#include "MoviePipelineInProcessExecutor.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutorJob.h"
```

### 基本用法

以下代码演示了如何在 C++ 中启动一个简单的渲染任务。

```cpp
// 来源：基于 MoviePipelineInProcessExecutor 的典型用法
void StartMovieRender()
{
    // 1. 创建或获取一个渲染队列
    UMoviePipelineQueue* Queue = NewObject<UMoviePipelineQueue>();
    
    // 2. 向队列中添加一个作业
    UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob();
    Job->SetSequence(FSoftObjectPath("/Game/Cinematics/MySequence.MySequence"));
    Job->Map = FSoftObjectPath("/Game/Maps/MyLevel.MyLevel");
    
    // 3. 创建一个进程内执行器
    UMoviePipelineInProcessExecutor* Executor = NewObject<UMoviePipelineInProcessExecutor>();
    
    // 4. 绑定完成回调
    Executor->OnIndividualJobFinished().AddLambda([](FMoviePipelineOutputData OutputData)
    {
        UE_LOG(LogTemp, Log, TEXT("渲染作业完成: %s"), *OutputData.Job->JobName);
    });
    
    // 5. 开始执行
    Executor->Execute(Queue);
}
```

### 进阶用法

结合 `MovieRenderGraph` 系统，可以通过代码动态构建渲染图。

```cpp
// 来源：基于 MovieGraphConfig 和节点的用法
void SetupMovieRenderGraph()
{
    // 1. 创建一个新的图配置
    UMovieGraphConfig* GraphConfig = NewObject<UMovieGraphConfig>();
    
    // 2. 添加一个输出节点（通常自动创建）
    UMovieGraphOutputNode* OutputNode = GraphConfig->GetOutputNode();
    
    // 3. 添加一个设置节点，例如设置输出分辨率
    UMovieGraphSettingNode* ResolutionNode = GraphConfig->ConstructRuntimeNode<UMovieGraphSettingNode>();
    // ... 配置分辨率节点的属性 ...
    
    // 4. 连接节点
    UMovieGraphPin* OutputPin = ResolutionNode->GetOutputPin(/* PinName */);
    UMovieGraphPin* InputPin = OutputNode->GetInputPin(/* PinName */);
    GraphConfig->CreateEdge(OutputPin, InputPin);
    
    // 5. 将此图配置应用到渲染作业中
    // Job->SetGraphPreset(GraphConfig);
}
```

## Demo 示例

一个最小的可编译示例，展示如何从 C++ 启动渲染。

**MyMovieRenderActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMovieRenderActor.generated.h"

class UMoviePipelineQueue;
class UMoviePipelineInProcessExecutor;

UCLASS()
class AMyMovieRenderActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyMovieRenderActor();
    
    UFUNCTION(BlueprintCallable, Category = "Movie Render")
    void StartRender();
    
private:
    UPROPERTY()
    TObjectPtr<UMoviePipelineQueue> RenderQueue;
    
    UPROPERTY()
    TObjectPtr<UMoviePipelineInProcessExecutor> Executor;
    
    UFUNCTION()
    void OnRenderFinished(FMoviePipelineOutputData OutputData);
};
```

**MyMovieRenderActor.cpp**
```cpp
#include "MyMovieRenderActor.h"
#include "MoviePipeline.h"
#include "MoviePipelineInProcessExecutor.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutorJob.h"

AMyMovieRenderActor::AMyMovieRenderActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMovieRenderActor::StartRender()
{
    if (!RenderQueue)
    {
        RenderQueue = NewObject<UMoviePipelineQueue>(this);
    }
    
    // 清空旧作业
    RenderQueue->DeleteAllJobs();
    
    // 添加一个新作业
    UMoviePipelineExecutorJob* NewJob = RenderQueue->AllocateNewJob();
    NewJob->SetSequence(FSoftObjectPath("/Game/Cinematics/MySequence.MySequence"));
    NewJob->Map = FSoftObjectPath("/Game/Maps/MyLevel.MyLevel");
    NewJob->JobName = TEXT("MyFirstRender");
    
    if (!Executor)
    {
        Executor = NewObject<UMoviePipelineInProcessExecutor>(this);
    }
    
    // 绑定回调
    Executor->OnIndividualJobFinished().AddDynamic(this, &AMyMovieRenderActor::OnRenderFinished);
    
    // 开始渲染
    Executor->Execute(RenderQueue);
    UE_LOG(LogTemp, Log, TEXT("电影渲染已启动。"));
}

void AMyMovieRenderActor::OnRenderFinished(FMoviePipelineOutputData OutputData)
{
    if (OutputData.bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("渲染成功完成！输出路径: %s"), *OutputData.FilePaths[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("渲染失败。"));
    }
    
    // 解绑回调
    Executor->OnIndividualJobFinished().RemoveDynamic(this, &AMyMovieRenderActor::OnRenderFinished);
}
```

## 模块依赖

要使用此插件，你的模块通常需要依赖 `MovieRenderPipelineCore`。根据具体功能，可能还需要其他依赖。

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | 核心运行时逻辑，包含所有基础类和接口。 |
| `OpenColorIO` | 用于 OpenColorIO 色彩管理集成。 |
| `RenderCore` | 底层渲染核心功能。 |
| `ImageWriteQueue` | 用于将渲染的图像数据异步写入磁盘。 |
| `MediaAssets` | 用于 MP4 等媒体格式的编码输出。 |
| `LevelSequence` | 用于驱动过场动画序列。 |
| `ConsoleVariablesEditor` | (仅 `MovieRenderPipelineSettings` 模块) 用于控制台变量预设编辑器集成。 |

## 维护状态

### 近期更新

```
- df9f487361af MoviePipeline: Fixed a bug that caused the multilayer EXR node to generate invalid/empty files if 1) the burn-in is enabled, 2) multipart is enabled, and 3) more than one layer is being rendered.
- ca49e32b07e3 MoviePipeline: Fixed cvars not being set correctly in some locations within MRG and MRQ after some recent changes to the engine were made. In some scenarios, cvars could be set with ECVF_SetByConstructor priority, which is no longer allowed.
- a245f0506548 MoviePipeline: Fixed a bug that could cause small seams in panoramic renders when rendering at very high resolutions.
```

### 维护评价

Movie Render Pipeline 是 Unreal Engine 中**核心且活跃维护**的插件。
- **创建时间**：约 5 年前，已相当成熟。
- **近期更新**：最近的提交集中在**修复关键 Bug**（如多层 EXR 输出、CVar 设置、全景渲染接缝），表明 Epic Games 持续关注其稳定性和正确性。
- **功能演进**：插件内部正在从传统的 Movie Render Queue 向更灵活的 Movie Render Graph 系统过渡，后者提供了更强大的节点化配置能力。
- **推荐度**：**强烈推荐**用于任何需要高质量、可控视频输出的项目。它是 UE 官方提供的专业渲染解决方案，功能全面，文档和社区支持相对较好。需要注意的是，它默认未启用，需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/RenderingAndGraphics/MovieRenderPipeline/)