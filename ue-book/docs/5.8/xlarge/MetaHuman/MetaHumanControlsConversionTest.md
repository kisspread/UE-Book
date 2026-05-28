# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman资产、配置、动画序列） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanToolkit` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanPlatform` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-02-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的、用于从真实演员的面部表演视频（Performance Capture）生成高质量 MetaHuman 角色面部动画的端到端解决方案。它解决了将单目视频输入转换为可驱动数字角色骨骼控制器（Rig）的关键帧数据这一复杂问题。

此插件的核心作用并非简单的资产导入工具，而是一个完整的、集成的处理管线（Pipeline），用于实现“视频到动画”的转换。它包含了从视频数据摄入、面部特征点追踪、3D 面部拟合、动画控制器解算、到最终在 Sequencer 中应用动画的全流程工具和算法。

## 使用场景

-   **影视与游戏过场动画制作**：你需要为大量 MetaHuman 角色快速生成基于真人表演的口型和表情动画，用于高质量的过场动画或虚拟制作。
-   **虚拟人直播/VTuber**：你希望利用摄像头实时或准实时捕捉主播的面部动作，并驱动一个高保真的 MetaHuman 虚拟形象。
-   **快速原型与预览**：在正式动捕或手调动画之前，你需要一个快速的方法来验证角色面部表演的情绪和节奏。
-   **批量处理与自动化**：你拥有一批演员的表演视频素材，需要通过命令行或自动化脚本批量转换为动画序列。

## 蓝图用法

基于插件的通用设计，以下为推测的核心蓝图节点类别。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetPerformance` | 设置一个性能捕捉资产供管线处理 | `UMetaHumanPerformance` |
| `ImportTake` | 从文件路径导入一个视频/图像序列作为拍摄素材 | `UMetaHumanCaptureSource` |
| `StartPipelineProcessing` | 启动完整的 MetaHuman Animator 管线处理流程 | `UMetaHumanPipeline` |
| `GetSolveControls` | 获取解算后的动画控制器数值映射表 | `UMetaHumanFaceAnimationSolver` |
| `ApplyAnimationToSkeletalMesh` | 将解算出的关键帧数据应用到 MetaHuman 骨骼网格体上 | `UMetaHumanPerformance` |
| `ExportAnimationSequence` | 将生成的动画导出为 UAnimationSequence 资产 | `UMetaHumanSequencer` |

### 使用示例（蓝图描述）

1.  **创建性能资产**：在内容浏览器中右键，创建 `MetaHuman Performance` 资产。
2.  **配置输入**：在 Performance 资产的细节面板中，指定输入的视频文件或图像序列路径。
3.  **关联角色**：将 Performance 资产与场景中已放置的、带有对应 Face Rig 的 MetaHuman 角色关联。
4.  **运行解算**：在工具栏或资产右键菜单中，点击“处理”或“解算”。插件将执行从特征追踪到控制器解算的全过程。
5.  **预览与调整**：在 Sequencer 中播放，查看生成的动画。可以通过 Performance 资产或直接在 Control Rig 中微调解算出的控制器值。
6.  **导出**：将 Sequencer 中的动画轨道导出为独立的 `AnimationSequence` 资产，供游戏或其他流程使用。

## C++ 用法

以下代码展示了如何使用核心的 `MetaHumanPipeline` 模块来驱动解算流程，并基于测试数据验证控制器映射的正确性。

### 头文件引入

```cpp
#include "MetaHumanPipeline.h"
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

从测试用例中，我们可以看到 `SolveControlsTestData` 定义了输入解算器名称（如 `CTRL_L_brow_down.ty`）与期望的骨骼控制器名称（如 `CTRL_expressions_browDownL`）之间的映射。以下代码演示了如何验证这个映射。

*来源文件: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/Private/Tests/ControlsTestData.h`*

```cpp
#include "MetaHumanFaceAnimationSolver.h"

// 假设已经通过某个方式获取到了输入控制器数据和期望的输出
const TMap<FString, float>& InputSolveControls = SolveControlsTestData::InputSolveControls;
const TMap<FString, float>& ExpectedRigControls = SolveControlsTestData::ExpectedRigControls;

// 创建或获取面部动画解算器实例
UMetaHumanFaceAnimationSolver* AnimationSolver = GetWorld()->GetSubsystem<UMetaHumanFaceAnimationSubsystem>()->GetAnimationSolver();

// 执行控制器转换
TMap<FString, float> ActualRigControls;
AnimationSolver->ConvertSolveControlsToRigControls(InputSolveControls, ActualRigControls);

// 验证结果是否符合预期（用于自动化测试）
for (const auto& ExpectedPair : ExpectedRigControls)
{
    if (const float* ActualValuePtr = ActualRigControls.Find(ExpectedPair.Key))
    {
        float ActualValue = *ActualValuePtr;
        // 使用 FMath::IsNearlyEqual 等函数进行浮点数比较
        // 如果 ActualValue 与 ExpectedPair.Value 超出容差，则测试失败
    }
    else
    {
        // 测试失败：期望的控制器在实际输出中缺失
    }
}
```

### 进阶用法

结合管线模块，可以编程方式执行完整的处理流程。

*概念性代码，基于模块结构推断*

```cpp
#include "MetaHumanPipeline.h"

void ProcessPerformanceAsset(UMetaHumanPerformance* PerformanceAsset)
{
    // 1. 获取或创建管线对象
    UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();

    // 2. 配置管线输入
    Pipeline->SetPerformanceAsset(PerformanceAsset);
    // 可以进一步配置管线的各个阶段，如追踪器、解算器的参数

    // 3. 绑定完成委托
    Pipeline->OnPipelineCompleted.AddDynamic(this, &UMyClass::OnPipelineFinished);
    Pipeline->OnPipelineFailed.AddDynamic(this, &UMyClass::OnPipelineFailed);

    // 4. 启动管线
    Pipeline->StartProcessing();
}

void UMyClass::OnPipelineFinished(UMetaHumanPipeline* Pipeline)
{
    // 管线处理完成，可以访问 PerformanceAsset 中生成的关键帧数据
    // 可以将其应用到 Sequencer 中的轨道，或导出为动画资产
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Pipeline processing completed successfully."));
}

void UMyClass::OnPipelineFailed(UMetaHumanPipeline* Pipeline, const FString& ErrorMessage)
{
    // 处理失败，记录错误信息
    UE_LOG(LogTemp, Error, TEXT("MetaHuman Pipeline failed: %s"), *ErrorMessage);
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何实例化并启动一个简单的 MetaHuman 处理管线。

### MyMetaHumanProcessor.h
```cpp
// MyMetaHumanProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanPipeline.h" // 包含管线模块头文件
#include "MyMetaHumanProcessor.generated.h"

UCLASS(BlueprintType)
class UMyMetaHumanProcessor : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void StartProcessingFromPerformance(UMetaHumanPerformance* InPerformanceAsset);

private:
    UPROPERTY()
    UMetaHumanPipeline* ActivePipeline;

    UFUNCTION()
    void HandlePipelineCompleted(UMetaHumanPipeline* Pipeline);

    UFUNCTION()
    void HandlePipelineFailed(UMetaHumanPipeline* Pipeline, const FString& Error);
};
```

### MyMetaHumanProcessor.cpp
```cpp
// MyMetaHumanProcessor.cpp
#include "MyMetaHumanProcessor.h"
#include "MetaHumanPerformance.h" // 确保包含性能资产的头文件

void UMyMetaHumanProcessor::StartProcessingFromPerformance(UMetaHumanPerformance* InPerformanceAsset)
{
    if (!InPerformanceAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid Performance Asset provided."));
        return;
    }

    // 清理之前的管线（如果有）
    if (ActivePipeline)
    {
        ActivePipeline->CancelProcessing();
    }

    // 创建新管线
    ActivePipeline = NewObject<UMetaHumanPipeline>(this);
    ActivePipeline->SetPerformanceAsset(InPerformanceAsset);

    // 绑定回调
    ActivePipeline->OnPipelineCompleted.AddDynamic(this, &UMyMetaHumanProcessor::HandlePipelineCompleted);
    ActivePipeline->OnPipelineFailed.AddDynamic(this, &UMyMetaHumanProcessor::HandlePipelineFailed);

    // 开始处理
    ActivePipeline->StartProcessing();
    UE_LOG(LogTemp, Log, TEXT("MetaHuman processing pipeline started for asset: %s"), *InPerformanceAsset->GetName());
}

void UMyMetaHumanProcessor::HandlePipelineCompleted(UMetaHumanPipeline* Pipeline)
{
    if (Pipeline == ActivePipeline)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman pipeline finished successfully."));
        // 此处可以添加后续逻辑，如将结果应用到 Sequencer
        ActivePipeline = nullptr;
    }
}

void UMyMetaHumanProcessor::HandlePipelineFailed(UMetaHumanPipeline* Pipeline, const FString& Error)
{
    if (Pipeline == ActivePipeline)
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHuman pipeline failed: %s"), *Error);
        ActivePipeline = nullptr;
    }
}
```

## 模块依赖

要在你的模块中使用 MetaHuman Animator 的功能，需要在你的模块的 `Build.cs` 文件中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanPipeline` | 核心处理管线的框架和基类 |
| `MetaHumanFaceAnimationSolver` | 面部动画控制器解算的核心算法 |
| `MetaHumanPerformance` | 表示一次表演捕捉数据的资产类 |
| `MetaHumanIdentity` | 管理 MetaHuman 角色身份和拓扑关系 |
| `MetaHumanCaptureSource` | 处理输入视频/图像序列 |
| `MetaHumanSequencer` | 与 Sequencer 集成，处理动画关键帧 |
| `ControlRigDeveloper` | 用于操作和驱动 MetaHuman 的 Control Rig |
| `MetaHumanSDKEditor` | （编辑器时）MetaHuman 资产相关的编辑器工具 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体相关的通用工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复在启用身体追踪时禁止导出关卡序列的问题。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增为已有的网格体导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存导致的问题。 |

### 维护评价

MetaHuman Animator 是一个**处于活跃维护状态**的核心官方插件。
- **活跃度高**：最近一次提交在 2026 年 5 月，且近期提交频繁（过去几天内有多次提交），表明 Epic 团队正在持续开发和修复。
- **功能更新与 Bug 修复并重**：近期的提交既包含新功能（如为现有网格体导出动画），也包含重要的 Bug 修复（如渲染瑕疵、缓存问题）。
- **稳定性保障**：包含专门的测试模块（如 `MetaHumanControlsConversionTest`），用于验证核心数据转换的准确性。
- **建议**：由于该插件仍在快速迭代，建议用户始终使用与引擎版本匹配的官方版本，并关注更新日志以了解行为变更。

**结论**：强烈推荐在需要从视频生成高质量 MetaHuman 面部动画的项目中使用此插件。其官方地位、活跃的维护以及端到端的解决方案使其成为该领域的标杆工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/Animation/MetaHuman/MetaHuman-Animator/)