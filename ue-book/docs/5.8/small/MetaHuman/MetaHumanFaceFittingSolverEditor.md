# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质，数据资产等） |
| 模块 | `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个全面的工具集，旨在将真实世界的人类表演数据转化为高质量的 MetaHuman 数字人资产和动画。它不仅仅是一个简单的工具，而是一个端到端的流水线，解决了从原始数据采集、面部追踪、模型拟合到最终动画驱动的全流程问题。该插件集成了多个独立的技术模块，支持从 iPhone 录制视频、专业面部捕捉设备数据、甚至音频生成面部动画，使创作者能够高效地创建逼真的数字人表演。

## 使用场景

-   **从视频创建数字人**：你使用 iPhone 录制了一段面部表演视频，希望快速生成一个与该表演同步的 MetaHuman 角色动画。
-   **专业动作捕捉集成**：你的团队使用了专业的面部捕捉系统（如通过 `MetaHumanCaptureProtocolStack` 和 `MetaHumanCaptureSource` 模块支持的设备），需要将数据导入 UE5 并驱动 MetaHuman。
-   **音频驱动面部动画**：你有一段语音录音（例如播客、配音），希望让一个 MetaHuman 角色的口型与语音自动同步（使用 `MetaHumanSpeech2Face`）。
-   **资产管理与批处理**：你有大量 MetaHuman 头像或动画序列需要进行统一的参数调整或重新计算（使用 `MetaHumanBatchProcessor`）。

## 蓝图用法

本插件蓝图功能由多个模块提供。以下列出核心的公开功能节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create FaceTracker` | 创建一个面部追踪器实例，用于处理视频帧数据。 | `UMetaHumanFaceContourTracker` (推断) |
| `Run FaceFitting Solver` | 在输入追踪数据上运行面部拟合解算器，生成控制数据。 | `UMetaHumanFaceFittingSolver` (推断) |
| `Convert Controls to Skeletal Mesh` | 将 MetaHuman 面部控制数据转换为可驱动骨骼网格体的动画序列。 | `UMetaHumanControlsConversionTest` (推断) |
| `Import Capture Data` | 导入来自外部捕捉协议栈的原始数据。 | `UMetaHumanCaptureSource` (推断) |
| `Generate Depth Map` | 从单目视频帧估算深度信息，用于提高追踪和拟合精度。 | `UMetaHumanDepthGenerator` (推断) |
| `Process Animation Sequence` | 处理或缓存一个动画序列，用于在 Sequencer 中播放。 | `UMetaHumanSequencer` (推断) |

### 使用示例（蓝图描述）

1.  **创建面部追踪器**：在蓝图中，调用“Create FaceTracker”节点。将视频纹理或图像序列作为输入连接到追踪器。
2.  **运行拟合解算**：将上一步创建的追踪器实例连接到“Run FaceFitting Solver”节点。同时，需要指定一个目标 MetaHuman 面部网格体。该节点输出一个包含面部控制参数的数据资产。
3.  **生成动画**：将“控制数据资产”连接到“Convert Controls to Skeletal Mesh”节点，并关联目标 MetaHuman 的骨骼网格体。最终输出一个可用于 Sequencer 或直接附加到角色的动画资产。

## C++ 用法

### 头文件引入

由于该插件模块化程度高，需根据具体功能引入对应模块的头文件。例如：

```cpp
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanPipeline/SomePipelineNode.h"
```

### 基本用法

以下是一个简化的 C++ 用例，展示如何初始化一个拟合过程。实际实现会更复杂，涉及更多的输入/输出管理。

```cpp
// 来源：基于模块结构推断，无直接单一测试用例
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanFaceContourTracker.h"

// 获取或创建一个面部追踪器实例
UObject* FaceTracker = NewObject<UMetaHumanFaceContourTracker>();

// 配置追踪器参数...
// FaceTracker->SetParameter(...);

// 获取面部拟合解算器
UObject* FittingSolver = NewObject<UMetaHumanFaceFittingSolver>();

// 执行解算，输入追踪结果，输出控制数据
UObject* OutputControls = FittingSolver->RunSolver(FaceTracker->GetTrackedData());

// 将 OutputControls 应用到 MetaHuman 角色上
```

### 进阶用法

进阶用法通常涉及构建一个完整的动画生成管线（`MetaHumanPipeline` 模块），将多个节点串联起来。

```cpp
// 来源：基于模块结构推断
#include "MetaHumanPipeline/Pipeline.h"
#include "MetaHumanPipeline/Nodes/FaceTrackingNode.h"
#include "MetaHumanPipeline/Nodes/FaceFittingNode.h"
#include "MetaHumanPipeline/Nodes/ControlConversionNode.h"

// 创建一个管线实例
UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();

// 构建管线节点链
UNode* TrackingNode = NewObject<UFaceTrackingNode>();
UNode* FittingNode = NewObject<UFaceFittingNode>();
UNode* ConversionNode = NewObject<UControlConversionNode>();

Pipeline->AddNode(TrackingNode);
Pipeline->AddNode(FittingNode);
Pipeline->AddNode(ConversionNode);

// 定义数据流
Pipeline->Connect(TrackingNode->GetOutputPin("TrackedData"), FittingNode->GetInputPin("Input"));
Pipeline->Connect(FittingNode->GetOutputPin("Controls"), ConversionNode->GetInputPin("Input"));

// 设置初始输入（如视频路径）
Pipeline->SetGlobalInput("VideoFilePath", TEXT("/Game/MyVideo.mp4"));

// 执行整个管线
Pipeline->Run();

// 从管线全局输出中获取最终动画资产
UObject* FinalAnimation = Pipeline->GetGlobalOutput("AnimationSequence");
```

## Demo 示例

以下是一个最小化的 C++ 类头文件和实现，展示如何创建一个自定义的 MetaHuman 动画处理组件。

**MyMetaHumanAnimatorComponent.h**
```cpp
// Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolverEditor
#pragma once

#include "Components/ActorComponent.h"
#include "MyMetaHumanAnimatorComponent.generated.h"

class UMetaHumanFaceContourTracker;
class UMetaHumanFaceFittingSolver;

UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyMetaHumanAnimatorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMetaHumanAnimatorComponent();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Animation")
    void StartAnimationFromTexture(UTexture2D* SourceTexture);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    UMetaHumanFaceFittingSolver* FittingSolverAsset;

private:
    UPROPERTY()
    UMetaHumanFaceContourTracker* FaceTracker;
};
```

**MyMetaHumanAnimatorComponent.cpp**
```cpp
// Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolverEditor
#include "MyMetaHumanAnimatorComponent.h"
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanFaceFittingSolver.h"

UMyMetaHumanAnimatorComponent::UMyMetaHumanAnimatorComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    FaceTracker = CreateDefaultSubobject<UMetaHumanFaceContourTracker>(TEXT("FaceTracker"));
}

void UMyMetaHumanAnimatorComponent::StartAnimationFromTexture(UTexture2D* SourceTexture)
{
    if (!SourceTexture || !FittingSolverAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("Missing required inputs for animation."));
        return;
    }

    // 1. 使用追踪器处理纹理
    FaceTracker->ProcessTexture(SourceTexture);

    // 2. 使用拟合解算器处理追踪数据
    UObject* ControlsData = FittingSolverAsset->RunSolver(FaceTracker->GetOutputData());

    // 3. （此处应添加将 ControlsData 应用到 Skeletal Mesh 的逻辑）
    //    例如：将结果保存为动画资产，或通过 Control Rig 驱动组件。
    UE_LOG(LogTemp, Log, TEXT("Animation controls generated successfully."));
}
```

## 模块依赖

使用 MetaHumanAnimator 插件时，你的项目模块需要依赖具体的子模块。以下是该插件的一些**独特**模块依赖示例：

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureDataEditor` | 编辑器功能，用于处理和查看捕捉数据。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器集成部分。 |
| `ControlRigDeveloper` | 用于开发和调试 MetaHuman 使用的 Control Rig。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体操作的通用工具函数。 |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，可能包含底层数学和图像处理算法。 |

*注意：具体依赖关系因使用的子模块而异，请查阅你实际引用的模块对应的 `Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

-   **活跃维护**：从提交历史看，该插件在 2026 年 5 月仍有密集的功能性更新和 Bug 修复（如身体追踪、渲染、序列导出等），表明处于**非常活跃的维护状态**。
-   **核心产品**：作为 Epic Games 的官方 MetaHuman 工具链，它是引擎的重要组成部分，预计会长期支持。
-   **实验性**：`.uplugin` 中 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `false`，表明该版本是稳定的生产版本。
-   **推荐使用**：对于任何涉及创建或驱动 MetaHuman 数字人动画的项目，强烈推荐使用此插件。它是解决相关问题的官方和最完整的方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (示例)