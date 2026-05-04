# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、配置文件） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包，旨在解决从视频捕获数据（如 iPhone 深度摄像头或专业动作捕捉设备）创建高保真数字人类（MetaHuman）并驱动其面部动画的完整管线问题。它不仅仅是一个简单的导入工具，而是一个包含面部追踪、动画求解、性能优化、批量处理和深度集成的综合性创作环境。该插件的核心价值在于将复杂的面部动画制作流程自动化、标准化，并深度集成到 Unreal Engine 的编辑器和 Sequencer 中，使开发者能够高效地为游戏角色、虚拟制片或实时应用创建逼真的数字人类表演。

## 使用场景

-   **游戏开发**：你需要为游戏中的主角或重要 NPC 创建基于真人演员表演的逼真面部动画。使用 iPhone 或其他设备录制演员的面部表演视频，通过 MetaHuman Animator 处理并驱动 MetaHuman 角色。
-   **虚拟制片**：在虚拟制片项目中，需要将现场演员的实时或离线表演快速映射到虚拟角色上，用于预览或最终合成。
-   **数字人应用**：开发虚拟主播、数字客服或培训模拟器，需要基于音频或视频快速生成自然的面部动画。
-   **批量内容生产**：拥有大量表演数据（如对话、表情包），需要批量处理并生成对应的 MetaHuman 动画资产。

## 蓝图用法

该插件的蓝图 API 主要集中在 `MetaHumanPerformance` 和 `MetaHumanPipeline` 等模块中，用于控制动画处理流程和查询状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Processing` | 启动对指定捕获数据的面部动画处理流程。 | `UMetaHumanPerformance` |
| `Stop Processing` | 停止当前正在进行的处理流程。 | `UMetaHumanPerformance` |
| `Get Processing State` | 获取当前处理流程的状态（如未开始、处理中、完成、错误）。 | `UMetaHumanPerformance` |
| `Get Output Animation` | 处理完成后，获取生成的动画序列或 Control Rig 资产。 | `UMetaHumanPerformance` |
| `Set Input Media` | 设置用于处理的输入媒体源（视频文件、图像序列等）。 | `UMetaHumanPerformance` |
| `Set Target MetaHuman` | 指定要驱动的目标 MetaHuman 角色或其 Control Rig。 | `UMetaHumanPerformance` |
| `Create Pipeline` | 创建一个用于自定义处理流程的 MetaHuman Pipeline 实例。 | `UMetaHumanPipeline` |
| `Add Stage` | 向 Pipeline 中添加一个处理阶段（如面部追踪、动画求解）。 | `UMetaHumanPipeline` |
| `Execute Pipeline` | 执行配置好的 Pipeline。 | `UMetaHumanPipeline` |

### 使用示例（蓝图描述）

1.  **基本处理流程**：
    *   在蓝图中创建一个 `MetaHumanPerformance` 组件或对象。
    *   使用 `Set Input Media` 节点，连接一个 `File Media Source` 资产，指向你的表演视频文件。
    *   使用 `Set Target MetaHuman` 节点，指定场景中的 MetaHuman 角色 Actor。
    *   调用 `Start Processing` 节点启动处理。
    *   使用 `Get Processing State` 节点轮询状态，当状态变为 `Completed` 时，调用 `Get Output Animation` 获取结果。

2.  **自定义管线**：
    *   使用 `Create Pipeline` 创建一个新管线。
    *   依次调用 `Add Stage` 添加 `FaceContourTracker`、`FaceAnimationSolver` 等阶段。
    *   配置每个阶段的参数（通过阶段对象的属性）。
    *   调用 `Execute Pipeline` 运行自定义流程。

## C++ 用法

### 头文件引入

```cpp
// 核心功能
#include "MetaHumanPerformance.h"
#include "MetaHumanPipeline.h"

// 面部追踪与求解
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanFaceFittingSolver.h"

// 数据与资产
#include "MetaHumanIdentity.h"
#include "MetaHumanCaptureSource.h"

// 编辑器集成（仅在编辑器模块中使用）
#include "MetaHumanToolkit.h"
```

### 基本用法

以下示例展示了如何在 C++ 中启动一个 MetaHuman 性能处理任务。

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Private/MetaHumanPerformance.cpp (推断用法)
#include "MetaHumanPerformance.h"

void AMyActor::StartMetaHumanAnimation()
{
    // 创建一个 MetaHuman Performance 实例
    UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>(this);

    // 配置输入源（假设已有一个 UFileMediaSource* MediaSource）
    Performance->SetInputMedia(MediaSource);

    // 配置目标 MetaHuman（假设已有一个 AActor* MetaHumanActor）
    Performance->SetTargetMetaHuman(MetaHumanActor);

    // 绑定处理完成的委托
    Performance->OnProcessingCompleted.AddDynamic(this, &AMyActor::OnAnimationReady);

    // 启动处理
    Performance->StartProcessing();
}

void AMyActor::OnAnimationReady(UMetaHumanPerformance* CompletedPerformance, UAnimationAsset* OutputAnimation)
{
    // 处理完成，获取输出动画
    if (OutputAnimation)
    {
        // 将动画应用到角色的骨骼网格体组件
        // ...
    }
}
```

### 进阶用法

使用 `MetaHumanPipeline` API 构建一个自定义的、多阶段的处理流程。

```cpp
// 来源: 综合 MetaHumanPipeline 和各 Solver 模块的用法
#include "MetaHumanPipeline.h"
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanFaceAnimationSolver.h"

void AMyActor::RunCustomPipeline()
{
    // 创建管线
    UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();

    // 添加面部轮廓追踪阶段
    UMetaHumanFaceContourTrackerStage* TrackerStage = NewObject<UMetaHumanFaceContourTrackerStage>(Pipeline);
    TrackerStage->SetInputVideoPath(TEXT("/Game/Captures/MyVideo.mp4"));
    Pipeline->AddStage(TrackerStage);

    // 添加面部动画求解阶段，并将上一阶段的输出作为输入
    UMetaHumanFaceAnimationSolverStage* SolverStage = NewObject<UMetaHumanFaceAnimationSolverStage>(Pipeline);
    SolverStage->SetInputContourData(TrackerStage->GetOutputContourData()); // 假设的接口
    Pipeline->AddStage(SolverStage);

    // 绑定管线完成委托
    Pipeline->OnPipelineCompleted.AddDynamic(this, &AMyActor::OnCustomPipelineDone);

    // 执行管线
    Pipeline->Execute();
}

void AMyActor::OnCustomPipelineDone(UMetaHumanPipeline* CompletedPipeline, const FMetaHumanPipelineResult& Result)
{
    // 处理自定义管线的输出结果
    // ...
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建并启动一个 `MetaHumanPerformance` 组件。

**MyMetaHumanController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanPerformance.h"
#include "MyMetaHumanController.generated.h"

UCLASS()
class MYPROJECT_API AMyMetaHumanController : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanController();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    UFileMediaSource* InputMedia;

    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    AActor* TargetMetaHumanActor;

private:
    UPROPERTY()
    UMetaHumanPerformance* PerformanceComponent;

    UFUNCTION()
    void OnProcessingCompleted(UMetaHumanPerformance* Performance, UAnimationAsset* Animation);
};
```

**MyMetaHumanController.cpp**
```cpp
#include "MyMetaHumanController.h"
#include "MediaSource.h"

AMyMetaHumanController::AMyMetaHumanController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanController::BeginPlay()
{
    Super::BeginPlay();

    if (InputMedia && TargetMetaHumanActor)
    {
        // 创建性能处理组件
        PerformanceComponent = NewObject<UMetaHumanPerformance>(this, TEXT("MHPerformance"));
        PerformanceComponent->SetInputMedia(InputMedia);
        PerformanceComponent->SetTargetMetaHuman(TargetMetaHumanActor);

        // 绑定完成回调
        PerformanceComponent->OnProcessingCompleted.AddDynamic(this, &AMyMetaHumanController::OnProcessingCompleted);

        // 开始处理
        PerformanceComponent->StartProcessing();
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Animation Processing Started."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("InputMedia or TargetMetaHumanActor is not set."));
    }
}

void AMyMetaHumanController::OnProcessingCompleted(UMetaHumanPerformance* Performance, UAnimationAsset* Animation)
{
    if (Animation)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Animation Processing Completed. Animation asset: %s"), *Animation->GetName());
        // 在这里可以将 Animation 应用到目标角色
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHuman Animation Processing Failed."));
    }
}
```

## 模块依赖

该插件由大量内部模块组成，模块间依赖关系复杂。作为插件使用者，你的项目模块通常只需要依赖 `MetaHumanCore` 和 `MetaHumanPerformance` 等少数几个核心运行时模块。以下列出了一些关键的、非通用的依赖模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层算法和数据结构。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，用于资产管理和导入。 |
| `ControlRigDeveloper` | 用于创建和编辑驱动 MetaHuman 面部动画的 Control Rig。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |
| `MediaUtils` | 处理媒体文件（视频、图像序列）的输入输出。 |
| `ImageWriteQueue` | 用于异步写入图像文件，常用于导出处理结果。 |

## 维护状态

### 近期更新

```
- 9803c443cfab 为包含对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏。（使用 UnrealCodeFixup 工具应用）
- 99e36a1ffc6a [UEMHC] 内容浏览器-添加按钮-MetaHuman：解锁的工具提示需要收集
- 2a7f797f2bdd [MH-Plugin] 将动画师插件从受限区域迁移出来 #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

MetaHuman Animator 是一个相对较新的插件（创建于 2024 年初），但作为 Epic Games 官方 MetaHuman 工具链的核心部分，它得到了**积极维护**。从提交历史看，近期有代码优化（如添加内联宏）、编辑器体验改进（内容浏览器集成）以及重要的架构调整（从受限区域迁移）。这表明该插件仍在活跃开发中，功能在不断完善。

**优势**：
-   官方支持，与 Unreal Engine 版本同步更新。
-   功能全面，覆盖从捕获到最终动画的完整流程。
-   深度集成编辑器和 Sequencer，工作流顺畅。

**注意事项**：
-   由于功能复杂，模块众多，学习曲线可能较陡峭。
-   部分高级功能（如自定义 Pipeline）可能需要深入理解其内部架构。
-   依赖特定的输入数据格式和硬件（如 iPhone 的 TrueDepth 摄像头）。

**推荐**：对于需要创建高质量、基于表演的 MetaHuman 面部动画的项目，**强烈推荐使用**。它是目前 Unreal Engine 生态中解决此类问题的最官方、最完整的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (暂无特定文档链接，通常可在 Unreal Engine 官方文档的 MetaHuman 部分找到相关信息)