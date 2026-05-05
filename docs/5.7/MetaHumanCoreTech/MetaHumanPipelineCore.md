# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 MetaHuman 生态系统的底层技术基石。它并非一个面向最终用户的独立功能插件，而是为 MetaHuman Creator（用于创建高保真数字人）和 MetaHuman Animator（用于将表演捕捉数据驱动到数字人）提供核心算法、数据处理框架和运行时支持。

其核心功能是提供一个**可扩展、高性能的数据处理流水线（Pipeline）框架**。该框架用于处理复杂的、多阶段的 MetaHuman 工作流，例如：
1.  **面部捕捉与追踪**：从视频流中实时检测面部、追踪关键点、估算头部姿态。
2.  **动画生成**：将音频或视频捕捉数据转换为面部动画曲线。
3.  **数据转换与优化**：处理图像、深度图、音频等多种数据类型，并进行平滑、重采样等操作。

简而言之，这个插件解决了“如何高效、可靠地处理创建和驱动数字人所需的海量复杂数据”这一核心问题。

## 使用场景

-   **你正在使用 MetaHuman Creator 创建或编辑数字人资产** → 该插件在后台提供核心的面部网格生成、纹理处理等算法。
-   **你正在使用 MetaHuman Animator 从 iPhone 或其他设备录制的表演中生成面部动画** → 该插件负责处理视频流、运行面部追踪模型、生成动画数据。
-   **你需要在运行时实时驱动 MetaHuman 角色的面部表情** → 该插件提供了实时面部追踪（Hyprsense）和音频驱动动画（Speech-to-Anim）的节点。
-   **你需要构建自定义的 MetaHuman 数据处理流程** → 你可以利用其提供的 Pipeline 框架，组合不同的处理节点（Node）来创建自己的工作流。

## 蓝图用法

该插件主要通过其 Pipeline 框架中的各种 **Node** 来暴露功能。这些节点通常不直接作为蓝图节点使用，而是被更高级的 MetaHuman 插件（如 MetaHuman Animator）封装和调用。然而，一些节点提供了可配置的参数，这些参数可以通过蓝图进行设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDebugImage` | 设置 Hyprsense 实时节点输出的调试可视化图像类型（如输入视频、面部检测框、追踪点等）。 | `FHyprsenseRealtimeNode` |
| `SetFocalLength` | 设置用于头部姿态估算的相机焦距。 | `FHyprsenseRealtimeNode` |
| `SetHeadStabilization` | 启用或禁用头部运动稳定化。 | `FHyprsenseRealtimeNode` |
| `SetMood` | 设置音频驱动动画节点的情绪状态（如中性、快乐、悲伤等）。 | `FRealtimeSpeechToAnimNode` |
| `SetMoodIntensity` | 设置情绪的强度。 | `FRealtimeSpeechToAnimNode` |
| `SetLookahead` | 设置音频驱动动画的预测帧数（Lookahead），影响动画的流畅度和延迟。 | `FRealtimeSpeechToAnimNode` |
| `SetAngle` | 设置图像旋转节点的旋转角度。 | `FUEImageRotateNode` |

### 使用示例（蓝图描述）

由于这些节点是 C++ 类，通常在蓝图中通过 **MetaHuman Animator** 等高级插件提供的组件或函数库进行间接控制。例如，在一个自定义的动画蓝图中，你可能会通过一个“MetaHuman Animator”组件来访问其内部的 Pipeline，并间接设置 `Mood` 或 `Lookahead` 参数。直接实例化和连接这些底层节点通常在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "Pipeline/Pipeline.h"
#include "Pipeline/Node.h"
#include "Nodes/HyprsenseRealtimeNode.h"
#include "Nodes/RealtimeSpeechToAnimNode.h"
```

### 基本用法

以下示例展示了如何创建一个简单的 Pipeline 并添加一个节点。

```cpp
// 来源: 基于 Pipeline.h 和 Node.h 的 API 设计
using namespace UE::MetaHuman::Pipeline;

// 1. 创建 Pipeline 实例
TSharedPtr<FPipeline> Pipeline = MakeShared<FPipeline>();

// 2. 创建一个节点实例 (例如，一个图像加载节点)
TSharedPtr<FUEImageLoadNode> ImageLoadNode = MakeShared<FUEImageLoadNode>(TEXT("MyImageLoader"));

// 3. 将节点添加到 Pipeline
Pipeline->AddNode(ImageLoadNode);

// 4. 配置运行参数
FPipelineRunParameters RunParams;
RunParams.SetMode(EPipelineMode::PushAsync); // 设置为异步推送模式
RunParams.SetStartFrame(0);
RunParams.SetEndFrame(100);

// 5. 运行 Pipeline (通常需要提供数据源和连接)
// Pipeline->Run(RunParams);
```

### 进阶用法

以下示例展示了如何连接两个节点，形成一个简单的处理链。

```cpp
// 来源: 基于 Pipeline.h, Connection.h, Pin.h 的 API 设计
using namespace UE::MetaHuman::Pipeline;

// 假设已有 Pipeline 和两个节点: LoadNode 和 ResizeNode
TSharedPtr<FUEImageLoadNode> LoadNode = MakeShared<FUEImageLoadNode>(TEXT("Load"));
TSharedPtr<FUEImageResizeNode> ResizeNode = MakeShared<FUEImageResizeNode>(TEXT("Resize"));

Pipeline->AddNode(LoadNode);
Pipeline->AddNode(ResizeNode);

// 创建连接：将 LoadNode 的输出图像 Pin 连接到 ResizeNode 的输入图像 Pin
// 注意：Pin 的名称和类型需要匹配，这里仅为示意
TSharedPtr<FConnection> Connection = MakeShared<FConnection>(
    LoadNode,   // From Node
    ResizeNode, // To Node
    0,          // From Pin Group (通常为0)
    0           // To Pin Group (通常为0)
);
Pipeline->AddConnection(Connection);

// 设置 ResizeNode 的参数
ResizeNode->MaxSize = 512;

// 现在运行 Pipeline，数据将从 LoadNode 流向 ResizeNode 进行处理。
```

## Demo 示例

一个最小化的、可编译的示例，演示如何创建 Pipeline 并添加一个自定义节点。

**MyCustomNode.h**
```cpp
#pragma once
#include "Pipeline/Node.h"
#include "Pipeline/PipelineData.h"

namespace UE::MetaHuman::Pipeline
{
class FMyCustomNode : public FNode
{
public:
    FMyCustomNode(const FString& InName) : FNode(TEXT("MyCustomNode"), InName) {}

    virtual bool Process(const TSharedPtr<FPipelineData>& InPipelineData) override
    {
        // 在这里处理数据
        // 例如，从输入 Pin 读取数据，处理后写入输出 Pin
        UE_LOG(LogTemp, Log, TEXT("Processing frame %d"), InPipelineData->GetFrameNumber());
        return true;
    }
};
}
```

**MyPipelineExample.cpp**
```cpp
#include "Pipeline/Pipeline.h"
#include "MyCustomNode.h"

void RunSimplePipeline()
{
    using namespace UE::MetaHuman::Pipeline;

    // 创建 Pipeline
    TSharedPtr<FPipeline> Pipeline = MakeShared<FPipeline>();

    // 创建并添加自定义节点
    TSharedPtr<FMyCustomNode> MyNode = MakeShared<FMyCustomNode>(TEXT("Processor"));
    Pipeline->AddNode(MyNode);

    // 配置并运行
    FPipelineRunParameters Params;
    Params.SetMode(EPipelineMode::PushSync);
    Params.SetStartFrame(0);
    Params.SetEndFrame(10);

    // 创建初始的 PipelineData
    TSharedPtr<FPipelineData> InitialData = MakeShared<FPipelineData>();
    InitialData->SetFrameNumber(0);

    // 手动触发一次处理 (在实际应用中，数据会通过连接流入)
    MyNode->Start(InitialData);
    MyNode->Process(InitialData);
    MyNode->End(InitialData);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenCVHelper` | 提供 OpenCV 与 UE 类型之间的转换工具。 |
| `OpenCV` | 提供计算机视觉库，用于图像处理、特征检测等核心算法。 |
| `UnrealEd` | 提供编辑器功能，可能用于资产处理或编辑器内预览。 |

## 维护状态

### 近期更新

```
- fb15849136ed 2025-01-20 Audio solver mood refactoring
- 71c0fdfd700c 2025-01-20 [Backout] - CL46056783 [FYI] jon.cook #rnx Original CL Desc ----------------------------------------------------------------- Audio solver mood refactoring #rb jack.taylor
- 5d5578dda2a9 2025-01-20 Audio solver mood refactoring #rb jack.taylor
```

### 维护评价

**活跃维护**。该插件创建时间非常近（2025年1月），且最近的提交记录显示 Epic 工程师正在积极进行功能重构（音频求解器情绪重构）。作为 MetaHuman 技术栈的核心，它必然会随着 MetaHuman Creator 和 Animator 的更新而持续维护和演进。由于其底层和核心的性质，它通常被认为是稳定可靠的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- 官方文档：无
- 测试用例：无（未在提供的路径中发现）