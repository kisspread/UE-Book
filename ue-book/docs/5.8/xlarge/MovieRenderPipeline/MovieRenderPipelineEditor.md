# Movie Render Pipeline

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 影片渲染队列 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设配置资产） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline（简称 MRQ，编辑器内名为 "Movie Render Queue"）是 UE5 中用于高质量影片渲染的现代化管线系统，替代了旧版的 Movie Scene Capture 系统。它解决了以下核心问题：

- **高质量离线渲染**：支持逐帧精确渲染，可输出电影级质量的图像序列和视频文件
- **批量渲染管理**：通过"队列"机制管理多个渲染任务，支持序列化保存/加载队列预设
- **节点化管线配置**：引入基于节点图（Graph）的渲染配置方式，取代线性设置列表，支持分支、变量、条件组合等高级工作流
- **多格式输出**：支持 EXR、PNG、JPEG 等图像序列，以及 Apple ProRes、Avid DNxHR、MP4 等视频编码
- **渲染通道分离**：可分别输出 Beauty、Object ID、World Normal、Depth 等各种通道（Render Pass）
- **远程渲染**：支持将渲染任务分发到远程机器执行
- **控制台变量管理**：允许在渲染时覆盖控制台变量以调整渲染设置

## 使用场景

- 你需要为过场动画生成高质量渲染输出 → 使用 MRQ 渲染 Sequencer 中的镜头序列
- 你需要同时渲染多个镜头并统一管理 → 将镜头添加到渲染队列批量处理
- 你需要输出多通道（Beauty + ObjectID + WorldNormal 等）用于后期合成 → 使用 Graph 配置多个输出节点
- 你需要快速预览当前视角或序列的渲染效果 → 使用 Quick Render（快速渲染）
- 你需要为远程农场渲染打包渲染任务 → 使用远程渲染执行器（Remote Executor）
- 你需要自定义渲染管线逻辑 → 继承 `UMoviePipelineExecutorBase` 或 `UMoviePipelineBase` 实现自定义执行器/管线

## 蓝图用法

### 核心节点

**队列管理（Movie Pipeline Queue Subsystem）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetQueue` | 获取当前渲染队列 | `UMoviePipelineQueueSubsystem` |
| `LoadQueue` | 加载队列到子系统，可选是否提示替换脏队列 | `UMoviePipelineQueueSubsystem` |
| `IsQueueDirty` | 检查队列是否被修改过 | `UMoviePipelineQueueSubsystem` |
| `GetActiveExecutor` | 获取当前活动的执行器实例（可用于订阅渲染事件） | `UMoviePipelineQueueSubsystem` |
| `IsRendering` | 是否正在渲染中 | `UMoviePipelineQueueSubsystem` |
| `RenderQueueWithExecutor` | 使用指定执行器类开始渲染当前队列 | `UMoviePipelineQueueSubsystem` |
| `RenderQueueInstanceWithExecutor` | 使用指定执行器类渲染指定队列实例 | `UMoviePipelineQueueSubsystem` |
| `RenderQueueWithExecutorInstance` | 使用已有执行器实例开始渲染当前队列 | `UMoviePipelineQueueSubsystem` |

**编辑器工具库（Movie Pipeline Editor Blueprint Library）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateJobFromSequence` | 从关卡序列创建渲染任务 | `UMoviePipelineEditorBlueprintLibrary` |
| `ExportConfigToAsset` | 将配置导出为资产 | `UMoviePipelineEditorBlueprintLibrary` |
| `SaveQueueToManifestFile` | 将队列保存为清单文件（用于远程渲染） | `UMoviePipelineEditorBlueprintLibrary` |
| `ConvertManifestFileToString` | 将清单文件转为字符串（用于 HTTP 请求） | `UMoviePipelineEditorBlueprintLibrary` |
| `IsMapValidForRemoteRender` | 检查任务指向的地图是否适用于远程渲染 | `UMoviePipelineEditorBlueprintLibrary` |
| `WarnUserOfUnsavedMap` | 弹出未保存地图的警告对话框 | `UMoviePipelineEditorBlueprintLibrary` |
| `ApplyDefaultConfigurationTypeToJob` | 为任务应用默认配置类型 | `UMoviePipelineEditorBlueprintLibrary` |
| `AssignDefaultGraphPresetToJob` | 为任务分配默认 Graph 预设并切换到 Graph 模式 | `UMoviePipelineEditorBlueprintLibrary` |
| `EnsureJobHasDefaultSettings` | 确保任务具有项目设置指定的默认设置（幂等操作） | `UMoviePipelineEditorBlueprintLibrary` |
| `GetDisplayOutputPathFromJob` | 获取任务的显示用输出路径 | `UMoviePipelineEditorBlueprintLibrary` |
| `ResolveOutputDirectoryFromJob` | 解析任务的完整输出目录路径 | `UMoviePipelineEditorBlueprintLibrary` |
| `SaveBasicConfigAsGraphConfig` | 将 Basic 配置转换为 Graph 配置并保存 | `UMoviePipelineEditorBlueprintLibrary` |

**快速渲染（Quick Render Subsystem）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginQuickRender` | 使用指定模式和设置开始快速渲染 | `UMovieGraphQuickRenderSubsystem` |
| `PlayLastRender` | 播放上次快速渲染的结果 | `UMovieGraphQuickRenderSubsystem` |
| `CanPlayLastRender` | 检查是否可以播放上次渲染结果 | `UMovieGraphQuickRenderSubsystem` |
| `OpenOutputDirectory` | 打开快速渲染的输出目录 | `UMovieGraphQuickRenderSubsystem` |

**PIE 执行器（PIE Executor）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIsRenderingOffscreen` | 设置是否在无 UI 模式下渲染 | `UMoviePipelinePIEExecutor` |
| `IsRenderingOffscreen` | 查询是否在无 UI 模式下渲染 | `UMoviePipelinePIEExecutor` |
| `SetInitializationTime` | 设置自定义初始化时间 | `UMoviePipelinePIEExecutor` |
| `SetAllowUsingUnsavedLevels` | 允许使用未保存的关卡进行渲染 | `UMoviePipelinePIEExecutor` |

**PIE 执行器事件（BlueprintAssignable）**

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnIndividualJobWorkFinished` | 单个任务完成后触发 | `UMoviePipelinePIEExecutor` |
| `OnIndividualShotWorkFinished` | 单个镜头完成后触发（需启用 `bFlushDiskWritesPerShot`） | `UMoviePipelinePIEExecutor` |
| `OnIndividualJobStarted` | 单个任务初始化前触发（最后修改任务属性的机会） | `UMoviePipelinePIEExecutor` |

### 使用示例（蓝图描述）

**基本渲染流程**：
1. 从 `GameplayStatics` 或编辑器子系统获取 `UMoviePipelineQueueSubsystem`
2. 调用 `GetQueue` 获取当前队列
3. 调用 `CreateJobFromSequence` 从关卡序列创建任务
4. 调用 `ApplyDefaultConfigurationTypeToJob` 应用默认配置
5. 调用 `RenderQueueWithExecutor` 并传入 `UMoviePipelinePIEExecutor` 类启动渲染
6. 订阅返回的执行器上的 `OnIndividualJobWorkFinished` 事件监听完成回调

**快速渲染流程**：
1. 获取 `UMovieGraphQuickRenderSubsystem`
2. 调用 `BeginQuickRender` 传入渲染模式（如 `CurrentViewport` 或 `CurrentSequence`）和设置
3. 渲染完成后调用 `PlayLastRender` 播放结果

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipelineQueueSubsystem.h"         // 队列子系统
#include "MoviePipelineEditorBlueprintLibrary.h"  // 编辑器工具库
#include "Graph/MovieGraphQuickRender.h"           // 快速渲染子系统
#include "MoviePipelinePIEExecutor.h"              // PIE 执行器
#include "MovieRenderPipelineSettings.h"           // 项目设置
#include "MoviePipelineOutputData.h"               // 输出数据结构
```

### 基本用法

**通过代码启动渲染队列**

```cpp
// 来源: MoviePipelineQueueSubsystem.h

// 获取编辑器子系统
UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();

// 创建渲染任务
UMoviePipelineEditorBlueprintLibrary::CreateJobFromSequence(Queue, LevelSequence);

// 使用 PIE 执行器启动渲染
UMoviePipelineExecutorBase* Executor = QueueSubsystem->RenderQueueWithExecutor(UMoviePipelinePIEExecutor::StaticClass());

// 监听任务完成事件
Executor->OnIndividualJobWorkFinished.AddLambda(
    [](FMoviePipelineOutputData OutputData)
    {
        // OutputData 包含输出的文件路径等信息
        UE_LOG(LogTemp, Log, TEXT("Job finished, output files: %d"), OutputData.FilePaths.Num());
    }
);
```

**从 Python 脚本启动渲染**

```cpp
// 来源: MoviePipelinePIEExecutor.h, MovieRenderPipelineSettings.h

// 配置执行器设置
UMoviePipelinePIEExecutor* Executor = NewObject<UMoviePipelinePIEExecutor>();
Executor->SetIsRenderingOffscreen(true);       // 无 UI 渲染
Executor->SetAllowUsingUnsavedLevels(false);   // 禁止使用未保存关卡
Executor->SetInitializationTime(FDateTime::Now());

// 监听单镜头完成事件（需在输出设置中启用 bFlushDiskWritesPerShot）
Executor->OnIndividualShotWorkFinished().AddLambda(
    [](FMoviePipelineOutputData InOutputData)
    {
        // 每个镜头渲染完成后的回调
    }
);
```

### 进阶用法

**使用项目设置自定义渲染行为**

```cpp
// 来源: MovieRenderPipelineSettings.h

// 获取项目设置
UMovieRenderPipelineProjectSettings* Settings = GetMutableDefault<UMovieRenderPipelineProjectSettings>();

// 可以自定义：
// - DefaultPipeline: 默认管线类型（继承自 MoviePipelineBase）
// - DefaultLocalExecutor: 本地渲染执行器
// - DefaultRemoteExecutor: 远程渲染执行器
// - DefaultExecutorJob: 默认任务类型
// - DefaultGraph: 新建 Graph 资产的基础模板
// - DefaultQuickRenderGraph: 快速渲染使用的 Graph
// - PresetSaveDir: 预设保存目录
// - DefaultClasses: 自动添加到新任务的默认设置类
```

**快速渲染高级用法**

```cpp
// 来源: Graph/MovieGraphQuickRender.h

UMovieGraphQuickRenderSubsystem* QuickRender = GEditor->GetEditorSubsystem<UMovieGraphQuickRenderSubsystem>();

// 获取快速渲染设置
const UMovieGraphQuickRenderModeSettings* Settings = GetDefault<UMovieGraphQuickRenderModeSettings>();

// 开始快速渲染（支持多种模式：CurrentViewport, CurrentSequence, UseViewportCameraInSequence 等）
QuickRender->BeginQuickRender(EMovieGraphQuickRenderMode::CurrentViewport, Settings);

// 检查并播放上次渲染结果
if (QuickRender->CanPlayLastRender())
{
    QuickRender->PlayLastRender();
}

// 打开输出目录
QuickRender->OpenOutputDirectory(Settings);
```

**测试基类用法**

```cpp
// 来源: Private/MoviePipelineFunctionalTestBase.h

// 继承功能测试基类实现自动化渲染测试
UCLASS(Blueprintable)
class AMyMoviePipelineTest : public AMoviePipelineFunctionalTestBase
{
    GENERATED_BODY()
    
public:
    // 设置要测试的队列预设（在编辑器中配置）
    // QueuePreset 属性: TSoftObjectPtr<UMoviePipelineQueue>
    
    // 设置图像容差级别
    // ImageToleranceLevel: EImageTolerancePreset
    
    // 启用像素对比
    // bPerformDiff: bool
    
    // 测试流程：PrepareTest -> IsReady -> StartTest
    // 渲染完成后自动调用 CompareRenderOutputToGroundTruth 对比输出与基准图像
};
```

## Demo 示例

```cpp
// MoviePipelineDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MoviePipelineDemo.generated.h"

class UMoviePipelineQueue;
class UMoviePipelineExecutorJob;
class ULevelSequence;

UCLASS()
class UMoviePipelineDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 创建一个简单的渲染任务并启动渲染 */
    UFUNCTION(BlueprintCallable, Category = "MRQ Demo")
    void DemoRenderSequence(ULevelSequence* InSequence);

    /** 演示队列管理 */
    UFUNCTION(BlueprintCallable, Category = "MRQ Demo")
    void DemoQueueManagement();

private:
    void OnJobFinished(FMoviePipelineOutputData InOutputData);
};

// MoviePipelineDemo.cpp
#include "MoviePipelineDemo.h"
#include "MoviePipelineQueueSubsystem.h"
#include "MoviePipelineEditorBlueprintLibrary.h"
#include "MoviePipelinePIEExecutor.h"
#include "MoviePipelineQueue.h"
#include "LevelSequence.h"

void UMoviePipelineDemoSubsystem::DemoRenderSequence(ULevelSequence* InSequence)
{
    if (!InSequence)
    {
        UE_LOG(LogTemp, Warning, TEXT("DemoRenderSequence: InSequence is null"));
        return;
    }

    // 获取队列子系统
    UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();

    // 从关卡序列创建任务
    UMoviePipelineExecutorJob* NewJob = UMoviePipelineEditorBlueprintLibrary::CreateJobFromSequence(Queue, InSequence);

    // 应用默认配置
    UMoviePipelineEditorBlueprintLibrary::ApplyDefaultConfigurationTypeToJob(NewJob);
    UMoviePipelineEditorBlueprintLibrary::AssignDefaultGraphPresetToJob(NewJob);

    // 启动渲染（PIE 模式）
    UMoviePipelineExecutorBase* Executor = QueueSubsystem->RenderQueueWithExecutor(UMoviePipelinePIEExecutor::StaticClass());

    // 监听完成事件
    Executor->OnIndividualJobWorkFinished.AddDynamic(this, &UMoviePipelineDemoSubsystem::OnJobFinished);

    UE_LOG(LogTemp, Log, TEXT("Rendering started for sequence: %s"), *InSequence->GetName());
}

void UMoviePipelineDemoSubsystem::DemoQueueManagement()
{
    UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();

    // 保存队列为清单文件
    FString ManifestPath;
    UMoviePipelineQueue* SavedQueue = UMoviePipelineEditorBlueprintLibrary::SaveQueueToManifestFile(Queue, ManifestPath);

    if (!ManifestPath.IsEmpty())
    {
        // 将清单文件内容转为字符串（可用于远程渲染 HTTP 请求）
        FString ManifestString = UMoviePipelineEditorBlueprintLibrary::ConvertManifestFileToString(ManifestPath);
        UE_LOG(LogTemp, Log, TEXT("Manifest saved to: %s"), *ManifestPath);
    }

    // 检查队列脏状态
    if (QueueSubsystem->IsQueueDirty())
    {
        UE_LOG(LogTemp, Warning, TEXT("Queue has unsaved changes!"));
    }
}

void UMoviePipelineDemoSubsystem::OnJobFinished(FMoviePipelineOutputData InOutputData)
{
    UE_LOG(LogTemp, Log, TEXT("Job completed. Success: %s"), InOutputData.bSuccess ? TEXT("Yes") : TEXT("No"));

    for (const FString& FilePath : InOutputData.FilePaths)
    {
        UE_LOG(LogTemp, Log, TEXT("  Output: %s"), *FilePath);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConsoleVariablesEditor` | 控制台变量编辑器集成（MovieRenderPipelineSettings 模块依赖，用于 CVar 管理 UI） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 添加 EXR 多图层支持 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复 Graph 中层预热导致部分骨骼网格体异常的问题 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回退了之前关于黑边（letterboxing）的修改 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe | 为 Basic 配置类型添加了"抗锯齿方法"属性 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 Rundown Page 设置添加 MRQ 分析事件 |

### 维护评价

Movie Render Pipeline 是 UE5 中**核心渲染基础设施**之一，由 Epic Games 官方团队持续维护。

- **活跃维护**：最近更新集中在 2026 年 5 月，更新频率极高（几乎每天都有提交），包含功能增强（nDisplay EXR 多图层）、bug 修复和新属性添加
- **成熟稳定**：创建于 2019 年，已历经约 7 年的迭代开发，架构成熟
- **持续进化**：Graph 节点化配置系统是近年来的重大升级，取代了旧的线性配置方式；Quick Render 功能持续增强
- **默认禁用**：`EnabledByDefault=false`，需要在项目设置中手动启用。这是合理的设计，因为并非所有项目都需要离线渲染功能
- **规模庞大**：400+ 源文件，6 个模块，是 UE5 中最大的官方插件之一
- **推荐使用**：这是 Epic 官方推荐的高质量渲染方案，适合所有需要离线渲染输出的项目。建议使用 Graph 配置模式（而非旧版 Basic 模式）以获得最佳功能支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/cinematics-and-movie-tool-in-unreal-engine/)（UE 官方影片工具文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests)（引擎自动化测试目录）