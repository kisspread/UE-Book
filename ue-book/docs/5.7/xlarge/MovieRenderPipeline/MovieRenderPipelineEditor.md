# Movie Render Pipeline Editor

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI、配置资产工厂、执行器、蓝图库） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline (MRQ) 是一个完整的、可扩展的电影渲染管线系统，旨在取代和增强传统的 Sequencer 渲染功能。它解决了传统渲染管线在控制力、灵活性和批量处理方面的限制。

**核心功能包括：**
1.  **队列化渲染**：允许用户将多个渲染任务（作业）组织到一个队列中，进行批量渲染。
2.  **可配置的渲染管线**：通过 `UMoviePipelinePrimaryConfig` 和 `UMovieGraphConfig`（节点图）提供高度可定制的渲染设置，包括输出格式、分辨率、渲染通道、后期处理等。
3.  **多种执行器**：提供不同的执行策略，如在当前编辑器进程中（PIE）、在新的外部进程中、或在远程机器上执行渲染。
4.  **编辑器集成**：提供完整的编辑器UI（队列窗口、配置编辑器）、资产工厂和蓝图库，方便用户在编辑器内设置和管理渲染任务。
5.  **快速渲染**：提供 `UMovieGraphQuickRenderSubsystem`，允许用户从当前视口快速发起渲染，无需繁琐的队列设置。

## 使用场景

-   **制作过场动画**：你需要从 Sequencer 中渲染出高质量的视频文件，用于游戏内播放或后期合成。
-   **产品/建筑可视化**：你需要批量渲染一系列镜头或不同配置的渲染图，用于制作宣传视频或效果图。
-   **自动化渲染流程**：你需要通过脚本（Python/蓝图）自动创建渲染队列并启动渲染，集成到你的自动化工具链中。
-   **自定义渲染管线**：你需要实现特殊的渲染逻辑或输出格式，可以通过继承 `UMoviePipelineBase` 或 `UMoviePipelineExecutorBase` 来扩展 MRQ。
-   **快速预览渲染**：你想快速查看当前视口或选定序列的渲染效果，用于动画审核或效果确认。

## 蓝图用法

MRQ 提供了丰富的蓝图 API，主要集中在 `UMoviePipelineEditorBlueprintLibrary` 和 `UMoviePipelineQueueSubsystem` 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetQueue` | 获取当前编辑器中的渲染队列实例。 | `UMoviePipelineQueueSubsystem` |
| `RenderQueueWithExecutor` | 使用指定的执行器类启动当前队列的渲染。 | `UMoviePipelineQueueSubsystem` |
| `IsRendering` | 检查当前是否正在渲染。 | `UMoviePipelineQueueSubsystem` |
| `CreateJobFromSequence` | 从关卡序列资产创建一个新的渲染作业并添加到队列。 | `UMoviePipelineEditorBlueprintLibrary` |
| `ExportConfigToAsset` | 将渲染配置导出为可复用的资产。 | `UMoviePipelineEditorBlueprintLibrary` |
| `SaveQueueToManifestFile` | 将队列保存为清单文件，用于远程渲染或命令行渲染。 | `UMoviePipelineEditorBlueprintLibrary` |
| `BeginQuickRender` | 使用快速渲染子系统，根据指定模式和设置开始渲染。 | `UMovieGraphQuickRenderSubsystem` |

### 使用示例（蓝图描述）

**示例1：通过蓝图启动队列渲染**
1.  使用 `Get Queue` 节点获取 `MoviePipelineQueueSubsystem` 的队列。
2.  使用 `Add Job to Queue` 节点（来自 `MoviePipelineQueue`）向队列添加作业，并设置其关卡序列。
3.  使用 `Render Queue With Executor` 节点，选择 `MoviePipelinePIEExecutor` 作为执行器类，即可在编辑器中启动渲染。

**示例2：快速渲染当前视口**
1.  获取 `MovieGraphQuickRenderSubsystem` 子系统实例。
2.  创建一个 `MovieGraphQuickRenderModeSettings` 对象，设置渲染模式（如 `CurrentViewport`）。
3.  调用 `Begin Quick Render` 节点，传入模式和设置对象。

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipelineQueueSubsystem.h"
#include "MoviePipelineEditorBlueprintLibrary.h"
#include "MovieRenderPipelineSettings.h"
#include "MoviePipelinePIEExecutor.h"
```

### 基本用法

**1. 通过代码启动队列渲染**
```cpp
// 来源: 基于 MoviePipelineQueueSubsystem.h 和 MoviePipelinePIEExecutor.h 的用法推断
#include "MoviePipelineQueueSubsystem.h"
#include "MoviePipelinePIEExecutor.h"

void StartRenderQueue()
{
    // 获取编辑器子系统
    UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    if (!QueueSubsystem) return;

    // 获取当前队列
    UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();
    if (!Queue || Queue->GetJobs().Num() == 0) return;

    // 使用PIE执行器启动渲染
    UMoviePipelineExecutorBase* Executor = QueueSubsystem->RenderQueueWithExecutor(UMoviePipelinePIEExecutor::StaticClass());
    if (Executor)
    {
        // 可以订阅执行器的委托来监听进度和完成事件
        Executor->OnExecutorFinished().AddLambda([](bool bSuccess){
            UE_LOG(LogTemp, Log, TEXT("Render finished. Success: %s"), bSuccess ? TEXT("true") : TEXT("false"));
        });
    }
}
```

**2. 从代码创建作业并配置**
```cpp
// 来源: 基于 MoviePipelineEditorBlueprintLibrary.h 和 MovieRenderPipelineSettings.h 的用法推断
#include "MoviePipelineEditorBlueprintLibrary.h"
#include "MovieRenderPipelineSettings.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineOutputSetting.h"

void CreateAndConfigureJob()
{
    UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();

    // 假设我们有一个关卡序列资产
    ULevelSequence* MySequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MySequence.MySequence"));
    if (!MySequence) return;

    // 从序列创建作业
    UMoviePipelineExecutorJob* NewJob = UMoviePipelineEditorBlueprintLibrary::CreateJobFromSequence(Queue, MySequence);

    // 获取或创建配置
    UMoviePipelinePrimaryConfig* Config = NewJob->GetConfiguration();
    if (!Config)
    {
        Config = NewObject<UMoviePipelinePrimaryConfig>();
        NewJob->SetConfiguration(Config);
    }

    // 修改输出设置
    UMoviePipelineOutputSetting* OutputSetting = Config->FindSetting<UMoviePipelineOutputSetting>();
    if (OutputSetting)
    {
        OutputSetting->OutputDirectory.Path = TEXT("/Game/MovieRenders");
        OutputSetting->FileNameFormat = TEXT("{sequence_name}_{frame_number}");
    }
}
```

### 进阶用法

**自定义执行器和项目设置**
```cpp
// 来源: 基于 MovieRenderPipelineSettings.h 和 MoviePipelinePIEExecutor.h 的用法推断
#include "MovieRenderPipelineSettings.h"

void ConfigureProjectDefaults()
{
    // 获取项目设置
    UMovieRenderPipelineProjectSettings* ProjectSettings = GetMutableDefault<UMovieRenderPipelineProjectSettings>();

    // 设置默认的本地执行器（可以是你自己继承的类）
    ProjectSettings->DefaultLocalExecutor = UMoviePipelinePIEExecutor::StaticClass()->GetClassPathName();

    // 设置默认的作业设置类，这些设置会自动添加到新创建的作业中
    ProjectSettings->DefaultClasses.Add(UMoviePipelineOutputSetting::StaticClass()->GetClassPathName());
    ProjectSettings->DefaultClasses.Add(UMoviePipelineDeferredPassBase::StaticClass()->GetClassPathName()); // 假设的渲染通道类

    // 保存配置
    ProjectSettings->TryUpdateDefaultConfigFile();
}
```

## Demo 示例

以下是一个完整的 C++ 示例，演示如何通过代码创建一个简单的渲染作业并启动渲染。

**MyRenderHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyRenderHelper
{
public:
    static void RenderCurrentLevelSequence();
};
```

**MyRenderHelper.cpp**
```cpp
#include "MyRenderHelper.h"
#include "MoviePipelineQueueSubsystem.h"
#include "MoviePipelineEditorBlueprintLibrary.h"
#include "MoviePipelinePIEExecutor.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineOutputSetting.h"
#include "LevelSequence.h"
#include "Engine/World.h"

void FMyRenderHelper::RenderCurrentLevelSequence()
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World) return;

    // 1. 获取队列子系统
    UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    if (!QueueSubsystem) return;

    // 2. 清空当前队列（可选）
    UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();
    Queue->DeleteAllJobs();

    // 3. 假设我们有一个关卡序列资产路径
    FString SequencePath = TEXT("/Game/Cinematics/DefaultSequence.DefaultSequence");
    ULevelSequence* Sequence = LoadObject<ULevelSequence>(nullptr, *SequencePath);
    if (!Sequence)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load level sequence: %s"), *SequencePath);
        return;
    }

    // 4. 从序列创建作业
    UMoviePipelineExecutorJob* Job = UMoviePipelineEditorBlueprintLibrary::CreateJobFromSequence(Queue, Sequence);
    if (!Job) return;

    // 5. 配置作业设置
    UMoviePipelinePrimaryConfig* Config = Job->GetConfiguration();
    if (Config)
    {
        // 设置输出目录
        UMoviePipelineOutputSetting* OutputSetting = Config->FindSetting<UMoviePipelineOutputSetting>();
        if (OutputSetting)
        {
            OutputSetting->OutputDirectory.Path = FPaths::ProjectSavedDir() / TEXT("MovieRenders");
            OutputSetting->FileNameFormat = TEXT("{sequence_name}");
        }
    }

    // 6. 启动渲染（使用PIE执行器）
    UMoviePipelineExecutorBase* Executor = QueueSubsystem->RenderQueueWithExecutor(UMoviePipelinePIEExecutor::StaticClass());
    if (Executor)
    {
        UE_LOG(LogTemp, Log, TEXT("Started rendering job for sequence: %s"), *Sequence->GetName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConsoleVariablesEditor` | 用于在编辑器中编辑控制台变量，可能被渲染设置UI使用。 |

## 维护状态

### 近期更新

-   eb6966880a2d MoviePipeline: Fixed an issue in the queue that could cause a job to lose focus when the job selection changes (a regression from 45937938). This change fixes the regression, and also addresses the original reason for 45937938 (ensuring that job variable values are committed properly when job selection state changes).
-   99c1eb1dd798 MoviePipeline: Disable window input in Local Execution. Related to crash fix for Remote Execution from CL 45851164
-   8b90b6f833e0 MoviePipeline: Fixed an issue where job variable values set in the queue may not be committed properly if another job is selected before the widget loses focus.

### 维护评价

Movie Render Pipeline 是 Unreal Engine 中用于高质量离线渲染的核心系统，自 2019 年引入以来持续得到维护和增强。从最近的提交记录看，团队仍在积极修复问题（如UI焦点、输入处理）并优化用户体验。虽然插件默认未启用（`EnabledByDefault: false`），但其功能完整且稳定，是制作过场动画和渲染内容的推荐方案。鉴于其重要性和持续的维护，**推荐使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/movie-render-pipeline-in-unreal-engine/) (UE5 官方文档链接)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests) (如果存在)