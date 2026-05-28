# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据流处理管道） |
| 模块 | `MetaHumanPipeline` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2013-02-12 |
| 年龄标签 | 🏛️ 文物（约 14 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHuman Pipeline` 是 MetaHuman Animator 插件的核心模块，提供了一个灵活的 **数据流处理管道（Pipeline）框架**。它并非直接提供动画功能，而是定义了一套标准化的节点（`FNode`）和数据（`FPipelineData`）流转机制。各类面部追踪、深度生成、语音转动画等具体功能被封装为不同类型的节点，并通过这个管道框架进行组合、调度和执行。其核心价值在于解决了实时或离线面部动画处理中的**数据流调度、并发控制和节点化组合**问题，使得复杂的工作流程（如从 iPhone 视频到最终动画数据的全链路处理）能够被清晰、高效地构建和执行。

## 使用场景

- 你需要从 iPhone 录制的视频中实时提取面部动画数据（使用 `FFaceTrackerIPhoneNode`）。
- 你需要从立体相机（Stereo）的视频流中计算面部深度图并进行追踪（使用 `FDepthGenerateNode` 和 `FFaceTrackerStereoNode`）。
- 你需要根据音频文件（如 WAV）自动生成面部口型和表情动画（使用 `FSpeechToAnimNode`）。
- 你需要构建一个包含多个处理步骤（如追踪、后处理、滤波、动画合并）的自定义动画处理流程。
- 你需要对动画数据进行批量处理、测试或导出到 JSON 文件（使用 `FJsonTrackerNode`, `FSaveContoursToJsonNode`）。

## 蓝图用法

本模块主要是 C++ 框架，但其中一些节点（如 `FSpeechToAnimNode`）的配置参数在更上层的编辑器工具（如 MetaHuman Performance 工具）中暴露给蓝图和编辑器 UI。直接在蓝图中构建 `MetaHumanPipeline` 管道较为复杂，通常由 C++ 驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetTrackers` | 为 HyprSense 人脸追踪节点设置具体的 NNE 神经网络模型实例。 | `FHyprsenseNode`, `FHyprsenseSparseNode` |
| `LoadModels` | 为语音转动画节点加载所需的音频驱动动画模型。 | `FSpeechToAnimNode` |
| `SetMood` | 设置语音驱动动画的目标情绪（如开心、悲伤）。 | `FSpeechToAnimNode` |
| `SetMoodIntensity` | 设置情绪的强度。 | `FSpeechToAnimNode` |
| `SetOutputControls` | 设置语音动画的输出范围（全脸或仅口型）。 | `FSpeechToAnimNode` |

### 使用示例（蓝图描述）

虽然不能直接在蓝图中拖拽连接 `FNode`，但可以通过理解数据流来使用。例如，一个典型的处理流程可以被想象为：

1.  **数据源**：一个 `FFaceTrackerIPhoneNode` 节点从视频文件中读取图像帧。
2.  **主处理**：该图像数据被送入一个 `FHyprsenseNode`（或 `FHyprsenseSparseNode`），它使用预先加载的 NNE 模型（通过 `SetTrackers` 设置）来提取面部特征点。
3.  **后处理**：特征点数据可能被送入一个 `FFaceTrackerPostProcessingNode` 进行平滑和优化。
4.  **输出**：最终的动画数据（`FFrameAnimationData`）可以被收集、保存，或送入 `FSaveContoursToJsonNode` 转换为 JSON 文件。

整个流程由一个 `FPipeline` 对象管理，它负责按顺序或并发地执行这些节点。

## C++ 用法

### 头文件引入

```cpp
// 引入管道核心
#include "MetaHumanPipeline/Public/MetaHumanPipeline.h"
// 引入你需要使用的具体节点，例如：
#include "MetaHumanPipeline/Public/Nodes/FaceTrackerNode.h"
#include "MetaHumanPipeline/Public/Nodes/HyprsenseNode.h"
#include "MetaHumanPipeline/Public/Nodes/SpeechToAnimNode.h"
#include "MetaHumanPipeline/Public/Nodes/TestNodes.h" // 用于测试示例
```

### 基本用法

以下示例基于 `TestNodes.h` 中的节点，展示一个最简单的数据处理管道，模拟整数累加。

```cpp
// 文件：MetaHumanPipeline/Tests/MetaHumanPipelineTest.cpp (简化版)
void CreateSimpleSumPipeline()
{
    // 1. 创建管道数据容器
    TSharedPtr<FPipelineData> PipelineData = MakeShared<FPipelineData>();

    // 2. 创建节点
    TSharedPtr<FIntSrcNode> SrcNode = MakeShared<FIntSrcNode>(TEXT("Source"));
    SrcNode->Value = 5;
    SrcNode->NumberOfFrames = 3; // 生成3帧数据

    TSharedPtr<FIntIncNode> IncNode = MakeShared<FIntIncNode>(TEXT("Increment"));
    TSharedPtr<FIntSumNode> SumNode = MakeShared<FIntSumNode>(TEXT("Sum"));
    TSharedPtr<FIntLogNode> LogNode = MakeShared<FIntLogNode>(TEXT("Log"));

    // 3. 定义处理顺序（简单串联）
    TArray<TSharedPtr<FNode>> Nodes;
    Nodes.Add(SrcNode);
    Nodes.Add(IncNode);
    Nodes.Add(SumNode);
    Nodes.Add(LogNode);

    // 4. 执行管道
    FPipeline Pipeline;
    Pipeline.SetNodes(Nodes);
    Pipeline.Start(PipelineData); // 初始化所有节点

    for (int32 Frame = 0; Frame < SrcNode->NumberOfFrames; ++Frame)
    {
        Pipeline.Process(PipelineData); // 处理一帧
        // 此时，LogNode 可能已经将每一帧递增后的结果输出到日志
    }

    Pipeline.End(PipelineData); // 清理所有节点
}
```

### 进阶用法

使用 `FAsyncNode` 实现并行处理，结合混合数据类型节点。

```cpp
void CreateAsyncAndMixedPipeline()
{
    // 创建混合数据源节点（同时产生整数和浮点数）
    TSharedPtr<FMixSrcNode> MixSrc = MakeShared<FMixSrcNode>(TEXT("MixSource"));
    MixSrc->NumberOfFrames = 5;

    // 创建一个异步节点，它内部会并发运行多个 FIntIncNode 实例
    // 参数 3 表示内部创建 3 个实例并发工作
    TSharedPtr<FAsyncNode<FIntIncNode>> AsyncInc = MakeShared<FAsyncNode<FIntIncNode>>(3, TEXT("AsyncInc"));
    TSharedPtr<FMixLogNode> MixLog = MakeShared<FMixLogNode>(TEXT("MixLog"));

    TArray<TSharedPtr<FNode>> Nodes;
    Nodes.Add(MixSrc);
    Nodes.Add(AsyncInc);
    Nodes.Add(MixLog);

    TSharedPtr<FPipelineData> PipelineData = MakeShared<FPipelineData>();
    FPipeline Pipeline;
    Pipeline.SetNodes(Nodes);

    Pipeline.Start(PipelineData);
    for (int32 i = 0; i < 10; ++i) // 处理多帧，演示异步缓冲
    {
        Pipeline.Process(PipelineData);
    }
    Pipeline.End(PipelineData);
}
```

## Demo 示例

一个完整的、可编译的 C++ 类，演示如何创建一个执行整数加法并输出日志的最小管道。

**头文件 (MySimplePipeline.h)**
```cpp
// MySimplePipeline.h
#pragma once
#include "CoreMinimal.h"

// 前向声明
namespace UE::MetaHuman { namespace Pipeline { class FPipeline; class FPipelineData; class FNode; } }

class FMySimplePipeline
{
public:
    FMySimplePipeline();
    ~FMySimplePipeline();

    /** 执行一次演示性的管道处理 */
    void RunDemo();

private:
    void SetupNodes();

    TSharedPtr<UE::MetaHuman::Pipeline::FPipeline> Pipeline;
    TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData> PipelineData;
    TArray<TSharedPtr<UE::MetaHuman::Pipeline::FNode>> Nodes;
};
```

**实现文件 (MySimplePipeline.cpp)**
```cpp
// MySimplePipeline.cpp
#include "MySimplePipeline.h"
#include "MetaHumanPipeline/Public/MetaHumanPipeline.h"
#include "MetaHumanPipeline/Public/Nodes/TestNodes.h" // 使用测试节点

FMySimplePipeline::FMySimplePipeline()
{
    Pipeline = MakeShared<UE::MetaHuman::Pipeline::FPipeline>();
    PipelineData = MakeShared<UE::MetaHuman::Pipeline::FPipelineData>();
    SetupNodes();
}

FMySimplePipeline::~FMySimplePipeline()
{
    if (Pipeline.IsValid())
    {
        Pipeline->End(PipelineData); // 确保清理
    }
}

void FMySimplePipeline::SetupNodes()
{
    using namespace UE::MetaHuman::Pipeline;

    // 1. 创建一个整数源节点，从10开始，生成2帧
    TSharedPtr<FIntSrcNode> Source = MakeShared<FIntSrcNode>(TEXT("MySource"));
    Source->Value = 10;
    Source->NumberOfFrames = 2;

    // 2. 创建一个整数递增节点
    TSharedPtr<FIntIncNode> Increment = MakeShared<FIntIncNode>(TEXT("MyIncrement"));

    // 3. 创建一个整数求和节点 (累加)
    TSharedPtr<FIntSumNode> Summator = MakeShared<FIntSumNode>(TEXT("MySummator"));

    // 4. 创建一个日志节点，输出结果
    TSharedPtr<FIntLogNode> Logger = MakeShared<FIntLogNode>(TEXT("MyLogger"));

    // 5. 设置执行顺序：Source -> Increment -> Summator -> Logger
    Nodes.Add(Source);
    Nodes.Add(Increment);
    Nodes.Add(Summator);
    Nodes.Add(Logger);

    Pipeline->SetNodes(Nodes);
}

void FMySimplePipeline::RunDemo()
{
    // 初始化
    Pipeline->Start(PipelineData);

    // 处理每一帧（模拟）
    for (int32 Frame = 0; Frame < 2; ++Frame)
    {
        UE_LOG(LogTemp, Log, TEXT("--- Processing Frame %d ---"), Frame);
        Pipeline->Process(PipelineData);
    }

    // 清理
    Pipeline->End(PipelineData);
    UE_LOG(LogTemp, Log, TEXT("Pipeline demo finished."));
}
```

## 模块依赖

要使用 `MetaHumanPipeline` 模块，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `NNE` | 用于加载和运行神经网络推理模型（NNE Models），是 `HyprsenseNode` 等追踪节点的核心。 |
| `MetaHumanSpeech2Face` | 用于加载和执行音频驱动的面部动画模型（S2F），是 `SpeechToAnimNode` 的核心。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 身体上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤掉用于可视化的辅助对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增功能：可以为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了与 Sequencer（序列器）相关的缓存问题。 |

### 维护评价

- **活跃维护**：插件创建于 2013 年，历史悠久，但最近的提交记录显示仍在 2026 年 5 月持续更新，专注于修复渲染问题、优化功能并添加新特性（如身体追踪兼容、导出功能）。
- **核心组件**：`MetaHuman Pipeline` 是 MetaHuman 动画功能的基础框架，其稳定性和性能至关重要。从提交历史看，维护重点在于完善功能（如身体追踪集成）和修复具体问题（渲染、缓存），表明它仍处于积极开发和维护中。
- **推荐使用**：作为 Epic Games 官方数字人工具套件的核心组成部分，此模块是进行程序化面部动画处理和构建自定义动画工作流的首选基础。虽然底层实现复杂，但遵循其框架可以高效构建可靠的处理管道。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPipeline)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPipeline/Tests)