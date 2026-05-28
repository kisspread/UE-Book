# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、神经网络模型、配置数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-02-25 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
该插件是 Epic Games 官方提供的 MetaHuman 创作核心工具套件。它解决的核心问题是：**如何将原始的表演捕捉数据（如 iPhone 视频、立体摄像头视频、音频）转化为高质量、逼真的 MetaHuman 面部动画**。它不仅仅是一个单一工具，而是一个完整的处理流水线（Pipeline），涵盖了从数据导入、面部关键点追踪（Hyprsense）、深度图生成、动画求解（Animation Solver）、后处理到最终序列导出的全流程。其存在意义在于为影视、游戏、虚拟人等领域的制作提供一个标准化、自动化且高质量的动画生产管线。

## 使用场景
- 你是一名影视或游戏开发者，拥有一段演员的 iPhone 深感摄像头录制的面部表演视频，希望快速、自动地将其转换为 MetaHuman 角色可用的面部动画序列。
- 你录制了立体（双眼）视频，需要插件中的 `FFaceTrackerStereoNode` 进行深度图计算和面部追踪，以生成更精确的动画数据。
- 你有一段角色说话的音频文件，想要使用 `FSpeechToAnimNode` 来驱动 MetaHuman 的口型和面部表情，实现音频驱动动画。
- 你需要对已有的面部追踪动画数据进行平滑、过滤或后处理（`FFaceTrackerPostProcessingNode`），以修复追踪错误或提升动画质量。
- 你需要批量处理大量表演数据，使用 `MetaHumanBatchProcessor` 模块自动化完成从追踪到导出的整个流程。

## 蓝图用法
该插件主要提供C++ API，其核心功能封装在复杂的 `Pipeline` 节点中，**较少直接暴露给蓝图**。它更多地作为其他 MetaHuman 相关蓝图资产（如 `MetaHumanPerformance`）的底层驱动引擎。用户通常在编辑器中使用 MetaHuman Toolkit 的 UI 来操作，或通过C++代码构建自定义管线。

## C++ 用法
此插件的核心是其模块化的**处理流水线（Pipeline）** 系统。开发者通过组合不同的处理节点（Node）来构建从原始数据到最终动画的转换流程。

### 头文件引入
要使用特定的管线节点，需要引入对应的头文件。例如，使用面部追踪节点：
```cpp
#include "Nodes/FaceTrackerNode.h"
// 或
#include "Nodes/HyprsenseNode.h"
```

### 基本用法
以下是一个简化的概念性代码，展示了如何使用管线节点。实际使用中，节点的配置和连接由 `MetaHumanToolkit` 或更高级的API管理。

```cpp
// 示例：创建并配置一个基于iPhone深度感数据的面部追踪节点
#include "Nodes/FaceTrackerNode.h"

// 假设已通过某种方式获取到必要的配置数据和模型
FString SolverConfigPath = TEXT("/Game/MetaHuman/Config/...");
TArray<uint8> PredictiveSolverData;

// 1. 创建节点实例
UE::MetaHuman::Pipeline::FFaceTrackerIPhoneNode IPhoneTrackerNode(TEXT("MyIPhoneTracker"));

// 2. 配置节点属性（这些数据通常从资产加载）
IPhoneTrackerNode.SolverConfigData = SolverConfigPath;
IPhoneTrackerNode.PredictiveSolvers = PredictiveSolverData;
// ... 设置其他配置，如 Calibrations, DNAReader 等

// 3. 模拟流水线执行
TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData> PipelineData = MakeShared<UE::MetaHuman::Pipeline::FPipelineData>();

// 启动节点（加载模型、初始化）
IPhoneTrackerNode.Start(PipelineData);

// 处理第一帧数据
PipelineData->SetData<UE::MetaHuman::Pipeline::FUEImageDataType>(... /* 包含第一帧图像 */);
IPhoneTrackerNode.Process(PipelineData);

// 从流水线数据中获取结果
const TArray<FFrameTrackingContourData>& TrackingResults = PipelineData->GetData<TArray<FFrameTrackingContourData>>(...);

// 结束节点，清理资源
IPhoneTrackerNode.End(PipelineData);
```

### 进阶用法
进阶用法涉及使用 `FAsyncNode` 进行多线程并行处理，或构建完整的、包含多个节点的复杂流水线。

```cpp
#include "Nodes/AsyncNode.h"
#include "Nodes/FaceTrackerNode.h"

// 创建一个异步版本的iPhone追踪节点，允许并行处理多帧
// 这可以显著提升处理速度
UE::MetaHuman::Pipeline::FAsyncNode<UE::MetaHuman::Pipeline::FFaceTrackerIPhoneNode> AsyncIPhoneTracker(
    /* NumberOfNodes */ 4, // 并行实例数
    /* ConstructorArgs */ TEXT("AsyncIPhoneTracker")
);

// 配置和运行方式与普通节点类似，但其内部管理多个实例进行异步处理
AsyncIPhoneTracker.Start(PipelineData);
// 循环处理帧...
AsyncIPhoneTracker.End(PipelineData);

// 要构建完整管线，需要将多个节点（如 FFmpegMediaReaderNode -> FFaceTrackerIPhoneNode -> FFaceTrackerPostProcessingNode）串联或并联。
// 通常使用 MetaHumanPipeline 或 MetaHumanToolkit 模块提供的更高级封装来实现。
```

## Demo 示例
一个最小的演示，展示如何实例化一个面部追踪节点（概念性）。

```cpp
// MyMetaHumanDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Nodes/HyprsenseNode.h" // 或其他追踪节点头文件

class UMyMetaHumanDemo
{
public:
    void RunDemo();

private:
    // 持有一个Hyprsense追踪节点的实例
    UE::MetaHuman::Pipeline::FHyprsenseNode HyprsenseTracker;
};
```

```cpp
// MyMetaHumanDemo.cpp
#include "MyMetaHumanDemo.h"
#include "Nodes/HyprsenseNode.h"

UMyMetaHumanDemo::UMyMetaHumanDemo()
    : HyprsenseTracker(TEXT("DemoHyprsenseTracker"))
{
}

void UMyMetaHumanDemo::RunDemo()
{
    // 1. 加载必要的神经网络模型 (NNE模型)
    // 这些模型通常是MetaHuman插件资产的一部分
    TSharedPtr<UE::NNE::IModelInstanceRunSync> FaceTrackerModel = /* 从资产加载 */;
    TSharedPtr<UE::NNE::IModelInstanceRunSync> FaceDetectorModel = /* 从资产加载 */;
    // ... 加载其他部件的模型

    // 2. 将模型设置给追踪节点
    HyprsenseTracker.SetTrackers(
        FaceTrackerModel,
        FaceDetectorModel,
        nullptr, // EyebrowTracker
        nullptr, // EyeTracker
        nullptr, // LipsTracker
        nullptr, // LipzipTracker
        nullptr, // NasolabialNoseTracker
        nullptr, // ChinTracker
        nullptr, // TeethTracker
        nullptr  // TeethConfidenceTracker
    );

    // 3. 创建流水线数据容器
    TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData> Data = MakeShared<UE::MetaHuman::Pipeline::FPipelineData>();

    // 4. 模拟处理一帧图像数据
    // UE::MetaHuman::Pipeline::FUEImageDataType ImageData = ...; // 准备图像数据
    // Data->SetData<UE::MetaHuman::Pipeline::FUEImageDataType>(/* Pin */, ImageData);
    //
    // if (HyprsenseTracker.Start(Data))
    // {
    //     if (HyprsenseTracker.Process(Data))
    //     {
    //         // 成功获取追踪结果
    //         const FFrameTrackingContourData& Contours = Data->GetData<FFrameTrackingContourData>(/* OutputPin */);
    //         UE_LOG(LogTemp, Log, TEXT("追踪完成，得到 %d 条曲线"), Contours.Num());
    //     }
    //     HyprsenseTracker.End(Data);
    // }
}
```

## 模块依赖
`MetaHumanAnimator` 插件包含众多模块，它们之间存在依赖关系。以下是 `MetaHumanPipeline` 模块（本文档分析的核心模块）的直接依赖，以及一些关键的外部依赖。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于编辑器扩展和资产访问。MetaHumanPipeline 在编辑器环境下运行依赖此模块。 |
| `NNE` (Neural Network Engine) | 提供加载和运行神经网络模型（如 Hyprsense 面部追踪模型）的接口。这是面部追踪功能的基础。 |
| `Core` / `CoreUObject` / `Engine` | 引擎核心基础模块，所有插件都依赖。 |

**注意**：其他模块（如 `MetaHumanCore`, `MetaHumanSpeech2Face`, `MetaHumanFaceFittingSolver`）也有其自身的依赖链，例如对 `ControlRig`, `MediaUtils`, `Json` 等模块的依赖。完整依赖关系需查阅各模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了MetaHuman角色身上的渲染瑕疵（伪影）。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤掉调试可视化对象，保持视图整洁。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持将动画序列导出到已有的网格体上。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了与Sequencer相关的缓存问题，提升了稳定性。 |

### 维护评价
- **活跃维护**：从近期提交记录看，该插件在**2026年5月**仍有频繁的功能更新和错误修复（如渲染修复、新功能、Sequencer问题修复），表明其处于**非常活跃的维护状态**。
- **核心地位**：作为 Epic Games 官方维护的 MetaHuman 核心创作工具，其长期维护和更新有保障。
- **复杂度高**：插件包含大量模块和复杂的处理流水线，使用门槛较高，主要面向需要深度定制动画流程的开发者或技术美术。
- **实验性功能**：当前版本未标记为实验性或Beta版，表明其主要功能已趋于稳定。
- **推荐使用**：**强烈推荐**所有需要进行基于表演捕捉或音频驱动的 MetaHuman 面部动画制作的团队使用。它是实现高质量、流程化生产的官方标准解决方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (在文档站搜索 “MetaHuman Animator”)