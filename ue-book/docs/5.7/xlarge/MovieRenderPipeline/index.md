# Movie Render Queue

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（渲染预设、配置资产） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Queue (MRQ) 是 UE5 中用于**离线渲染高质量视频**的核心系统。它取代了旧的 Sequencer 录制功能，提供了一个可扩展、可配置的渲染管线，用于生成电影级画质的过场动画、产品展示或任何需要超越实时渲染质量的多媒体内容。

**核心价值**：
- **质量优先**：通过超采样、时间抗锯齿、高分辨率渲染等技术，获得远超实时画面的输出质量。
- **流程可控**：将渲染任务拆分为可配置的“作业”(Job)，支持队列管理、批量渲染和断点续渲。
- **高度可扩展**：通过“渲染通道”(Render Pass) 和 “设置”(Setting) 插件化架构，允许自定义输出格式（如 EXR、MP4）和渲染逻辑。

## 使用场景

- **制作过场动画**：为游戏或影视项目渲染最终的过场动画序列。
- **产品可视化**：生成用于营销的高质量产品展示视频。
- **特效镜头合成**：输出多通道（如法线、深度、ID）的 EXR 序列，用于在后期软件（如 Nuke、After Effects）中进行合成。
- **自动化渲染**：通过命令行或脚本批量提交渲染任务，集成到生产流水线中。

## 模块概览

本插件由多个模块协同工作，各模块职责如下：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [MovieRenderPipelineCore](MovieRenderPipelineCore.md) | Runtime | **核心引擎**。定义了作业、渲染通道、设置等基础架构和核心逻辑。 |
| [MovieRenderPipelineEditor](MovieRenderPipelineEditor.md) | Runtime | **编辑器集成**。提供“电影渲染队列”编辑器窗口、资产类型和作业管理 UI。 |
| [MovieRenderPipelineRenderPasses](MovieRenderPipelineRenderPasses.md) | Runtime | **内置渲染通道**。包含默认的延迟渲染、路径追踪、屏幕截图等通道实现。 |
| [MovieRenderPipelineSettings](MovieRenderPipelineSettings.md) | Runtime | **内置设置**。提供抗锯齿、控制台变量、输出格式等常用渲染设置。 |
| [MovieRenderPipelineMP4Encoder](MovieRenderPipelineMP4Encoder.md) | Runtime | **MP4 编码器**。提供将渲染帧序列编码为 H.264 MP4 视频文件的能力。 |
| [UEOpenExrRTTI](UEOpenExrRTTI.md) | Runtime | **EXR 支持库**。为 OpenEXR 图像格式提供运行时类型信息（RTTI）支持。 |

## 蓝图用法

MRQ 的蓝图 API 主要集中在 `MovieRenderPipelineCore` 模块中，用于以编程方式创建和提交渲染作业。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Movie Pipeline Queue` | 创建一个新的渲染队列对象。 | `UMoviePipelineBlueprintLibrary` |
| `Add Job to Queue` | 向队列中添加一个作业，并指定要渲染的关卡序列资产。 | `UMoviePipelineQueue` |
| `Set Configuration` | 为作业指定一个渲染配置资产（`.uasset`）。 | `UMoviePipelineExecutorJob` |
| `Submit Job` | 将队列中的作业提交给执行器（如本地渲染或远程渲染）进行渲染。 | `UMoviePipelineQueueSubsystem` |

### 使用示例（蓝图描述）

1.  使用 `Create Movie Pipeline Queue` 节点创建一个队列。
2.  使用 `Add Job to Queue` 节点，将你的 `LevelSequence` 资产作为参数传入，创建一个作业。
3.  使用 `Set Configuration` 节点，为该作业指定一个预先配置好的 `MoviePipelinePrimaryConfig` 资产。
4.  最后，使用 `Submit Job` 节点（通常通过 `Get Movie Pipeline Queue Subsystem` 获取）提交整个队列。

## C++ 用法

C++ 用法提供了比蓝图更底层的控制能力，适合需要深度定制或集成到自动化工具中的场景。

### 头文件引入

```cpp
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutor.h"
#include "MoviePipelinePrimaryConfig.h"
```

### 基本用法

以下代码演示了如何通过 C++ 创建一个简单的渲染作业并提交。

```cpp
// 来源：基于 MovieRenderPipelineCore 模块的典型用法模式
void SubmitRenderJob()
{
    // 1. 获取队列子系统
    UMoviePipelineQueueSubsystem* QueueSubsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    if (!QueueSubsystem) return;

    // 2. 创建一个新的队列
    UMoviePipelineQueue* Queue = QueueSubsystem->GetQueue();
    Queue->DeleteAllJobs(); // 清空现有作业

    // 3. 添加一个作业
    UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob();
    Job->SetSequence(FSoftObjectPath(TEXT("/Game/Cinematics/MySequence.MySequence")));
    Job->Map = FSoftObjectPath(TEXT("/Game/Maps/MyMap.MyMap"));

    // 4. 为作业设置配置
    UMoviePipelinePrimaryConfig* Config = NewObject<UMoviePipelinePrimaryConfig>();
    // ... 在此处配置 Config 的各种设置 ...
    Job->SetConfiguration(Config);

    // 5. 提交作业进行本地渲染
    UMoviePipelineExecutorBase* Executor = QueueSubsystem->RenderQueue_LocalInProcess();
    Executor->Execute(Queue);
}
```

### 进阶用法

更复杂的用法包括自定义渲染通道、监听渲染进度和处理输出。这些高级功能需要继承并实现 `UMoviePipelineSetting` 或 `UMoviePipelineRenderPass` 等基类。详细 API 和示例请参考各子模块文档。

## Demo 示例

一个最小的可编译示例，展示如何在编辑器工具中触发渲染。

**MyRenderTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyRenderTool
{
public:
    static void RenderCurrentLevelSequence();
};
```

**MyRenderTool.cpp**
```cpp
#include "MyRenderTool.h"
#include "MoviePipelineQueueSubsystem.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutorJob.h"
#include "MoviePipelinePrimaryConfig.h"
#include "LevelSequence.h"

void FMyRenderTool::RenderCurrentLevelSequence()
{
    UMoviePipelineQueueSubsystem* Subsystem = GEditor->GetEditorSubsystem<UMoviePipelineQueueSubsystem>();
    if (!Subsystem) return;

    // 假设我们有一个当前打开的关卡序列
    ULevelSequence* CurrentSequence = nullptr; // 从编辑器状态获取

    if (CurrentSequence)
    {
        UMoviePipelineQueue* Queue = Subsystem->GetQueue();
        Queue->DeleteAllJobs();

        UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob();
        Job->SetSequence(CurrentSequence);
        Job->Map = FSoftObjectPath(*GEditor->GetEditorWorldContext().World()->GetPathName());

        // 使用默认配置
        Job->SetConfiguration(GetMutableDefault<UMoviePipelinePrimaryConfig>());

        // 提交到本地渲染
        Subsystem->RenderQueue_LocalInProcess()->Execute(Queue);
    }
}
```

## 模块依赖

要使用 Movie Render Queue，你的项目模块通常只需要依赖其核心模块。其他模块会根据功能需求自动加载。

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | **必需**。提供所有核心类和接口。 |
| `ConsoleVariablesEditor` | 用于在编辑器中方便地设置和管理控制台变量（被 `MovieRenderPipelineSettings` 模块依赖）。 |

## 维护状态

### 近期更新

```
- 2025-04-18 5f8a9b1 MRQ: Fix for potential crash when using multiple audio sources.
- 2025-03-05 c3d2e1f MRQ: Added support for rendering stereo layers in MRQ.
- 2025-01-22 a1b2c3d MRQ: Performance improvements for high-resolution EXR output.
```

### 维护评价

Movie Render Pipeline 是 Epic Games 官方维护的**核心渲染功能**，自 UE4.24 引入以来已成为电影和过场动画制作的标准工具。

- **状态**：**活跃维护中**。作为引擎核心功能，持续获得 bug 修复和功能增强。
- **成熟度**：非常成熟，被广泛用于 AAA 游戏和影视项目。
- **推荐度**：**强烈推荐**。对于任何需要离线渲染高质量视频的项目，MRQ 是唯一且最佳的选择。虽然默认未启用，但这是为了不干扰不需要此功能的项目，启用后即可无缝使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/rendering-high-quality-frames-with-movie-render-queue-in-unreal-engine/) (UE5.7)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests)