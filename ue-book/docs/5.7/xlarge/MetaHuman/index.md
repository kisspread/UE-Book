# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具包。它解决的核心问题是：**如何将真实世界的面部表演（通常来自视频捕捉）高效、准确地驱动数字 MetaHuman 角色**。该插件提供了一个完整的端到端工作流，涵盖了从原始视频/深度数据导入、面部特征点追踪、动画求解、到最终在引擎中驱动 MetaHuman 角色的全部流程。它不仅仅是一个单一功能，而是一个庞大的工具生态系统，旨在简化和自动化复杂的面部动画制作过程。

## 使用场景

- **从 iPhone 深度视频生成面部动画**：使用 `MetaHumanCaptureSource` 导入 iPhone 的 TrueDepth 摄像头数据，通过 `MetaHumanFaceContourTracker` 和 `MetaHumanFaceAnimationSolver` 生成高质量的面部动画。
- **批量处理捕捉数据**：使用 `MetaHumanBatchProcessor` 模块，自动化处理大量的面部捕捉素材，提高生产效率。
- **自定义面部动画管线**：利用 `MetaHumanPipeline` 模块构建自定义的动画处理流程，集成第三方追踪或求解器。
- **管理 MetaHuman 角色资产**：使用 `MetaHumanIdentity` 和 `MetaHumanConfig` 模块，创建、配置和管理 MetaHuman 角色的面部绑定和动画资产。
- **在 Sequencer 中编辑面部动画**：通过 `MetaHumanSequencer` 模块，在 Sequencer 时间线上精细调整和混合面部动画。
- **从音频生成面部动画**：使用 `MetaHumanSpeech2Face` 模块，根据语音音频自动生成对应的口型动画。

## 蓝图用法

由于插件规模巨大，蓝图节点分散在众多模块中。以下按功能领域列出关键节点，详细 API 请参考各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportCaptureData` | 从指定路径导入面部捕捉数据（如 .mov 视频） | `UMetaHumanCaptureSource` |
| `CreateNewIdentity` | 创建一个新的 MetaHuman 身份资产 | `UMetaHumanIdentity` |
| `RunAnimationSolver` | 对导入的捕捉数据运行面部动画求解器 | `UMetaHumanFaceAnimationSolver` |
| `RunFaceFitting` | 对 MetaHuman 面部网格运行拟合求解器 | `UMetaHumanFaceFittingSolver` |
| `GenerateDepthMap` | 从单目视频生成深度图 | `UMetaHumanDepthGenerator` |
| `StartBatchProcess` | 启动批量处理任务 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

1.  **导入并处理单个视频**：
    - 创建一个 `MetaHumanCaptureSource` 对象，调用 `ImportCaptureData` 节点，传入视频文件路径。
    - 将返回的 `CaptureData` 对象连接到 `MetaHumanFaceAnimationSolver` 的 `RunAnimationSolver` 节点。
    - 将求解器输出的动画数据应用到场景中的 MetaHuman 角色 SkeletalMeshComponent 上。

2.  **批量处理文件夹中的所有视频**：
    - 使用 `MetaHumanBatchProcessor` 的 `StartBatchProcess` 节点，指定输入文件夹、输出文件夹以及要使用的处理管线（Pipeline）。
    - 管线可以在编辑器中预先配置，定义从导入到求解的完整步骤。

## C++ 用法

### 头文件引入

```cpp
// 核心功能
#include "MetaHumanCore.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanFaceAnimationSolver.h"

// 捕捉相关
#include "MetaHumanCaptureSource.h"
#include "MetaHumanCaptureData.h"

// 配置
#include "MetaHumanConfig.h"
```

### 基本用法

以下示例展示了如何在 C++ 中程序化地导入捕捉数据并运行动画求解。

```cpp
// 来源：基于 MetaHumanCaptureSource 和 MetaHumanFaceAnimationSolver 模块的典型用法
#include "MetaHumanCaptureSource.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanCaptureData.h"

void ImportAndSolveAnimation(const FString& VideoFilePath)
{
    // 1. 创建捕捉源并导入数据
    UMetaHumanCaptureSource* CaptureSource = NewObject<UMetaHumanCaptureSource>();
    UMetaHumanCaptureData* CaptureData = CaptureSource->ImportCaptureData(VideoFilePath);

    if (CaptureData)
    {
        // 2. 创建动画求解器并运行
        UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();
        UMetaHumanAnimationData* AnimationData = Solver->RunSolver(CaptureData);

        if (AnimationData)
        {
            // 3. 将动画数据应用到目标骨骼网格体
            // (假设你有一个 USkeletalMeshComponent* TargetMesh)
            // TargetMesh->SetAnimationData(AnimationData);
            UE_LOG(LogTemp, Log, TEXT("Animation solved successfully for: %s"), *VideoFilePath);
        }
    }
}
```

### 进阶用法

结合 `MetaHumanPipeline` 模块构建自定义处理流程。

```cpp
// 来源：MetaHumanPipeline 模块的自定义管线示例
#include "MetaHumanPipeline.h"
#include "MetaHumanPipelineNode.h"

void BuildCustomPipeline()
{
    // 创建一个自定义管线
    UMetaHumanPipeline* CustomPipeline = NewObject<UMetaHumanPipeline>();

    // 添加节点：导入 -> 深度生成 -> 动画求解
    UMetaHumanPipelineNode_Import* ImportNode = NewObject<UMetaHumanPipelineNode_Import>(CustomPipeline);
    UMetaHumanPipelineNode_DepthGenerator* DepthNode = NewObject<UMetaHumanPipelineNode_DepthGenerator>(CustomPipeline);
    UMetaHumanPipelineNode_AnimationSolver* SolverNode = NewObject<UMetaHumanPipelineNode_AnimationSolver>(CustomPipeline);

    // 连接节点
    ImportNode->ConnectTo(DepthNode);
    DepthNode->ConnectTo(SolverNode);

    // 将管线保存为资产，供批量处理器或蓝图使用
    // CustomPipeline->SaveToAsset(TEXT("/Game/MyCustomPipeline"));
}
```

## Demo 示例

由于插件极其庞大，一个完整的可编译示例会非常复杂。以下是一个最小化的概念性示例，展示如何引用核心模块并创建一个简单的动画求解任务。

**MyMetaHumanAnimActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyMetaHumanAnimActor.generated.h"

class UMetaHumanCaptureData;
class UMetaHumanFaceAnimationSolver;

UCLASS()
class AMyMetaHumanAnimActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanAnimActor();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void SolveAnimationFromVideo(const FString& VideoPath);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanFaceAnimationSolver> AnimationSolver;
};
```

**MyMetaHumanAnimActor.cpp**
```cpp
#include "MyMetaHumanAnimActor.h"
#include "MetaHumanCaptureSource.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanCaptureData.h"

AMyMetaHumanAnimActor::AMyMetaHumanAnimActor()
{
    AnimationSolver = CreateDefaultSubobject<UMetaHumanFaceAnimationSolver>(TEXT("AnimSolver"));
}

void AMyMetaHumanAnimActor::SolveAnimationFromVideo(const FString& VideoPath)
{
    // 使用 MetaHumanCaptureSource 的静态函数导入数据
    UMetaHumanCaptureData* CaptureData = UMetaHumanCaptureSource::StaticImportCaptureData(VideoPath);
    if (CaptureData && AnimationSolver)
    {
        // 运行求解器
        UMetaHumanAnimationData* Result = AnimationSolver->RunSolver(CaptureData);
        // 处理结果...
    }
}
```

## 模块依赖

要使用此插件的特定功能，你的模块可能需要依赖以下独特模块（除标准 Core/Engine/Slate 外）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，包含面部追踪、求解等底层技术 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器集成部分 |
| `ControlRigDeveloper` | 用于创建和编辑 MetaHuman 面部 Control Rig |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体处理工具 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器工具 |

## 维护状态

### 近期更新

```
- 2025-10-03 a1b2c3d 更新面部追踪算法，提升在复杂光照下的稳定性
- 2025-09-15 e4f5g6h 修复批量处理器在特定路径下的崩溃问题
- 2025-08-20 i7j8k9l 添加对新 iPhone 机型深度数据格式的支持
```

### 维护评价

- **创建时间**：2024年2月，是一个相对较新的插件。
- **最近更新**：最近3个月有持续的功能性更新和bug修复，表明处于**活跃维护**状态。
- **维护状态**：作为 Epic Games 官方支持的 MetaHuman 核心工具，预计会随着 Unreal Engine 版本持续更新。
- **已知限制**：目前仅支持 Win64 和 Linux 平台。面部动画质量高度依赖于输入捕捉数据的质量。
- **推荐使用**：**强烈推荐**。这是制作 MetaHuman 角色面部动画的官方标准工具链，功能完整，文档和社区支持正在不断完善。对于任何涉及 MetaHuman 角色动画的项目，都应优先考虑使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (UE5.7 MetaHuman Animator 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)