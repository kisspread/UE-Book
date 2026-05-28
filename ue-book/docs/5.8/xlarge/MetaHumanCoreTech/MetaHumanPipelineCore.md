# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 核心技术 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHuman Core Tech 是 MetaHuman Creator（用于创建逼真数字人类）和 MetaHuman Animator（用于从视频捕获面部动画）的底层核心库。它提供了一套模块化的图像处理、AI 推理、音频处理和实时动画管道系统，专注于面部追踪、动画解算和图像处理任务。

这个插件的存在是为 MetaHuman 生态系统提供基础运行时和算法支持，将复杂的人工智能和计算机视觉任务封装成可重用的管道节点，使 MetaHuman Creator 和 Animator 插件能够专注于业务逻辑，而不必从零实现底层技术。

## 使用场景

- **MetaHuman 创建与动画**：在 MetaHuman Creator 中生成角色时，使用其面部检测和追踪算法。
- **实时面部动画**：在 MetaHuman Animator 中，从单目摄像头视频实时驱动 MetaHuman 的面部动画。
- **音频驱动动画**：从音频输入生成面部动画数据，用于口型同步。
- **图像/深度处理**：在面部捕捉数据处理管线中，执行图像加载、保存、缩放、裁剪等操作。
- **构建自定义处理管线**：利用其管道系统（Pipeline System）组合不同的处理节点，创建自定义的面部数据处理流程。

## 蓝图用法

根据提供的源码，当前模块 `MetaHumanPipelineCore` 是一个 **Runtime** 模块，主要提供 C++ 管道节点和数据类型。它没有暴露 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 给蓝图系统。其设计是作为底层 C++ 库，供其他上层插件（如 MetaHuman Creator/Animator）在 C++ 层调用。

因此，**该模块没有直接的蓝图用法**。其功能通过上层插件间接提供给蓝图。

## C++ 用法

### 头文件引入

```cpp
// 引入管道核心
#include "Pipeline/Pipeline.h"
// 引入具体节点（例如图像处理、音频处理、面部追踪等）
#include "Nodes/ImageUtilNodes.h"
#include "Nodes/AudioUtilNodes.h"
#include "Nodes/HyprsenseRealtimeNode.h"
#include "Nodes/RealtimeSpeechToAnimNode.h"
```

### 基本用法：创建一个简单的图像处理管道

以下示例展示如何使用 `FPipeline` 和几个图像处理节点，从文件加载图像、调整大小并保存。

*来源：基于 `Public/Pipeline/Pipeline.h` 和 `Public/Nodes/ImageUtilNodes.h` 中的 API 推断。*

```cpp
#include "Pipeline/Pipeline.h"
#include "Nodes/ImageUtilNodes.h"

void RunSimpleImagePipeline()
{
    using namespace UE::MetaHuman::Pipeline;

    // 1. 创建管道实例
    FPipeline Pipeline;

    // 2. 创建节点
    TSharedPtr<FUEImageLoadNode> LoadNode = Pipeline.MakeNode<FUEImageLoadNode>(TEXT("LoadImage"));
    TSharedPtr<FUEImageResizeNode> ResizeNode = Pipeline.MakeNode<FUEImageResizeNode>(TEXT("ResizeImage"));
    TSharedPtr<FUEImageSaveNode> SaveNode = Pipeline.MakeNode<FUEImageSaveNode>(TEXT("SaveImage"));

    // 3. 配置节点参数
    LoadNode->FramePathResolver = MakeUnique<SomePathResolver>(); // 需要实现帧路径解析器
    LoadNode->bFailOnMissingFile = true;

    ResizeNode->MaxSize = 512; // 缩放至最大边 512 像素

    SaveNode->FilePath = TEXT("/Game/Processed/frame_%04d.png"); // 输出路径格式
    SaveNode->FrameNumberOffset = 0;

    // 4. 连接节点：Load -> Resize -> Save
    Pipeline.MakeConnection(LoadNode, ResizeNode);
    Pipeline.MakeConnection(ResizeNode, SaveNode);

    // 5. 设置管道运行参数
    FPipelineRunParameters RunParameters;
    RunParameters.SetMode(EPipelineMode::PushSync); // 同步模式
    RunParameters.SetStartFrame(0);
    RunParameters.SetEndFrame(100); // 处理第 0 到 100 帧

    RunParameters.SetOnProcessComplete(FProcessComplete::CreateLambda([](TSharedPtr<FPipelineData> InPipelineData)
    {
        if (InPipelineData->GetExitStatus() == EPipelineExitStatus::Ok)
        {
            UE_LOG(LogTemp, Log, TEXT("图像处理管道完成。"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("管道错误: %s"), *InPipelineData->GetErrorMessage());
        }
    }));

    // 6. 运行管道
    Pipeline.Run(RunParameters);
}
```

### 进阶用法：构建面部追踪管道

以下示例展示如何组合面部检测、追踪和解算节点，创建一个简化的实时面部动画管道。

*来源：基于 `Public/Nodes/HyprsenseRealtimeNode.h` 和 `Public/Pipeline/Pipeline.h` 的 API。*

```cpp
#include "Pipeline/Pipeline.h"
#include "Nodes/HyprsenseRealtimeNode.h"
#include "Nodes/HyprsenseRealtimeSmoothingNode.h"

void SetupRealtimeFacialAnimationPipeline()
{
    using namespace UE::MetaHuman::Pipeline;

    FPipeline Pipeline;

    // 创建面部追踪节点
    TSharedPtr<FHyprsenseRealtimeNode> FaceTrackerNode = Pipeline.MakeNode<FHyprsenseRealtimeNode>(TEXT("FaceTracker"));

    // 创建平滑节点
    TSharedPtr<FHyprsenseRealtimeSmoothingNode> SmoothingNode = Pipeline.MakeNode<FHyprsenseRealtimeSmoothingNode>(TEXT("Smoothing"));

    // 配置面部追踪节点
    FMonocularAnimationPipelineModels TrackerModels;
    // ... 设置模型路径 (FaceDetector, FaceHeadPoseTracker, FaceSolver)
    TrackerModels.NNEBackend = TEXT("NNERuntimeORTCpu"); // 使用 ONNX Runtime CPU 后端
    FaceTrackerNode->SetModels(TrackerModels);

    // 配置追踪参数
    FaceTrackerNode->SetDebugImage(EHyprsenseRealtimeNodeDebugImage::None);
    FaceTrackerNode->SetFocalLength(50.0f); // 假设焦距
    FaceTrackerNode->SetHeadStabilization(true);
    FaceTrackerNode->SetHeadAllowedRotation(true, 45.0f, 30.0f); // 限制头部旋转
    FaceTrackerNode->SetHeadRotationErrorHandler(EFaceUnsolvedFrameBehavior::NeutralPose);

    // 配置平滑节点
    // FMetaHumanRealtimeSmoothingParam 可以通过 TMap 配置各个动画曲线的平滑参数
    FMetaHumanRealtimeSmoothingParam SmoothingParam;
    SmoothingParam.bEnabled = true;
    SmoothingParam.SmoothingFactor = 0.5f;
    SmoothingNode->Parameters.Add(FName("EyeBlink_L"), SmoothingParam);
    // ... 为其他曲线设置平滑参数

    // 连接节点：FaceTracker -> Smoothing
    Pipeline.MakeConnection(FaceTrackerNode, SmoothingNode);

    // 设置运行参数
    FPipelineRunParameters RunParams;
    RunParams.SetMode(EPipelineMode::PushAsync); // 异步模式，适合实时处理
    RunParams.SetOnFrameComplete(FFrameComplete::CreateLambda([](TSharedPtr<FPipelineData> InPipelineData)
    {
        // 每帧回调：可以获取面部动画数据
        if (InPipelineData->HasData<FUEImageDataType>(TEXT("OutputVideoFrame")))
        {
            // 获取带追踪结果的视频帧
        }
        if (InPipelineData->HasData<FFrameAnimationData>(TEXT("Animation")))
        {
            // 获取面部动画数据，可用于驱动 MetaHuman 骨骼
        }
    }));

    // 启动管道（例如在收到新视频帧时）
    // Pipeline.Run(RunParams);
    // 然后循环调用 Push 方法将输入数据（图像）推入管道
}
```

## Demo 示例

一个最小的可编译示例，展示如何定义一个自定义的管道节点。

*CustomNode.h*
```cpp
#pragma once

#include "Pipeline/Node.h"
#include "Pipeline/PipelineData.h"

namespace UE::MetaHuman::Pipeline
{
    // 一个简单的自定义节点：将输入的整数值加倍
    class FDoublingNode : public FNode
    {
    public:
        FDoublingNode(const FString& InName)
            : FNode(TEXT("DoublingNode"), InName)
        {
            // 定义一个输入引脚和一个输出引脚，类型都是 Int
            Pins.Add(FPin(TEXT("InputValue"), EPinDirection::Input, EPinType::Int));
            Pins.Add(FPin(TEXT("OutputValue"), EPinDirection::Output, EPinType::Int));
        }

        virtual bool Process(const TSharedPtr<FPipelineData>& InPipelineData) override
        {
            // 从输入引脚获取数据
            const int32& InputValue = InPipelineData->GetData<int32>(TEXT("InputValue"));

            // 计算
            const int32 OutputValue = InputValue * 2;

            // 将结果设置到输出引脚
            InPipelineData->SetData<int32>(TEXT("OutputValue"), OutputValue);

            return true;
        }
    };
}
```

*Main.cpp (使用示例)*
```cpp
#include "Pipeline/Pipeline.h"
#include "CustomNode.h" // 自定义节点头文件

void RunCustomNodeDemo()
{
    using namespace UE::MetaHuman::Pipeline;

    FPipeline Pipeline;

    // 创建并配置自定义节点
    TSharedPtr<FDoublingNode> Doubler = Pipeline.MakeNode<FDoublingNode>(TEXT("MyDoubler"));

    // 管道运行参数
    FPipelineRunParameters Params;
    Params.SetMode(EPipelineMode::PushSync);
    Params.SetOnProcessComplete(FProcessComplete::CreateLambda([&Doubler](TSharedPtr<FPipelineData> InData)
    {
        // 管道运行完毕后，从输出引脚读取结果
        // 注意：在实际中，数据是通过管道连接流动的，这里为演示直接读取
        if (InData->HasData<int32>(TEXT("OutputValue")))
        {
            const int32 Result = InData->GetData<int32>(TEXT("OutputValue"));
            UE_LOG(LogTemp, Log, TEXT("加倍结果: %d"), Result);
        }
    }));

    // 运行管道前，需要手动设置输入数据（因为这是一个单节点示例）
    // 在复杂管道中，数据会从上游节点流入。
    // 我们创建一个初始的 PipelineData 并设置输入值。
    TSharedPtr<FPipelineData> InitialData = MakeShared<FPipelineData>();
    InitialData->SetData<int32>(TEXT("InputValue"), 21);

    // 将数据推入管道（Push 模式）
    // 在实际使用中，管道通常由多个节点组成，并通过连接自动传递数据。
    // 此示例仅为演示节点的 Process 方法。
    Doubler->Process(InitialData); // 直接调用节点的 Process

    UE_LOG(LogTemp, Log, TEXT("输入: 21, 输出: %d"), InitialData->GetData<int32>(TEXT("OutputValue")));
    // 应该输出: 输入: 21, 输出: 42
}
```

## 模块依赖

从 `MetaHumanPipelineCore.Build.cs` 提取。

| 模块 | 用途 |
|---|---|
| `OpenCV` | 计算机视觉库，用于图像处理和分析（如人脸检测、追踪） |
| `OpenCVHelper` | UE 的 OpenCV 封装层，简化 OpenCV 在 UE 中的使用 |
| `UnrealEd` | 编辑器功能（可能用于节点开发、调试或编辑器内预览） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman Titan 系统版本更新至 9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman Titan 系统版本更新至 9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | MetaHuman Titan 系统版本更新至 9.0.6 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 为 MetaHuman 身体追踪器添加脚部锁定开关功能 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复 MetaHuman Creator 在组装带身体表现时发生的崩溃问题 |

### 维护评价

**活跃维护**。根据近期的 Git 提交记录（显示日期为 2026 年，可能为未来版本或内部版本），该插件正处于频繁更新和迭代中。近期提交包含了多个版本发布（Titan v9.0.x）和重要的功能改进（如身体追踪中的脚部锁定）以及 Bug 修复。作为 MetaHuman 核心技术的一部分，它持续得到 Epic Games 的支持和更新，是 MetaHuman 生态系统健康、活跃的关键组件。

**推荐使用**：如果你需要在项目中实现高级的面部追踪、动画解算或处理 MetaHuman 数据，这个插件是官方推荐的核心底层库。尽管它默认不启用，且主要供其他 MetaHuman 插件内部使用，但其提供的管道系统和节点具有很高的参考和扩展价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [官方文档]() (暂无直接文档链接)
- [测试用例]() (测试文件路径未在提供的信息中明确)