# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产定义、处理工具、UI） |
| 模块 | `MetaHumanPerformance` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanToolkit` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 高级动画工作流程工具集。它不仅仅是一个简单的动画导入工具，而是一个**完整的端到端解决方案**，用于将来自真实世界表演的捕捉数据（如 iPhone 面部深度视频、音频或单目摄像头视频）转换为高质量的 MetaHuman 面部和身体动画数据。

该插件解决的核心问题是：**如何高效、自动化地将复杂的捕捉源数据转化为可直接用于 Unreal Engine 中 MetaHuman 角色的动画资产**。它通过集成多种专有算法（面部轮廓跟踪、动画求解、音频驱动等）和工作流工具，让用户无需手动逐帧调整，即可从原始素材生成可用于最终产品的动画序列或关卡序列。

## 使用场景

- **你是一位动捕艺术家或技术美术，使用 iPhone 带 LiDAR 的设备拍摄了演员的面部表演** → 使用 `Depth Footage` 模式，将深度视频和身份网格导入，自动生成高保真的面部 Control Rig 动画。
- **你有一段配音音频，希望为角色自动生成同步的口型和面部表情** → 使用 `Audio` 模式，通过 `Speech2Face` 技术直接从音频驱动面部动画。
- **你只有普通的单目摄像头拍摄的视频（如网络摄像头或手机视频），希望快速生成动画预览** → 使用 `Monocular Footage` 模式，进行快速的单目面部和可选身体追踪。
- **你需要将生成的动画批量应用于一个或多个 MetaHuman 角色** → 使用 `MetaHumanBatchProcessor` 模块进行批量处理。
- **你希望将整个动画流程（包括原始素材、中间数据和最终动画）打包成一个 Level Sequence 用于 Sequencer 编辑** → 使用 `Export Level Sequence` 功能。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Pipeline` | 启动处理流程。根据 `InputType` 设置的输入类型和相应参数，开始对数据进行分析、跟踪和求解。 | `UMetaHumanPerformance` |
| `Cancel Pipeline` | 取消正在进行的处理流程。 | `UMetaHumanPerformance` |
| `Is Processing` | 检查当前是否有处理流程正在运行。 | `UMetaHumanPerformance` |
| `Can Process` | 检查当前资产配置是否满足开始处理的条件（例如，是否设置了必需的身份或音频数据）。 | `UMetaHumanPerformance` |
| `Set Input Type` | 设置数据输入类型（`DepthFootage`, `Audio`, `MonoFootage`）。切换类型会清理旧模式的相关状态。 | `UMetaHumanPerformance` |
| `Set Footage Capture Data` | 设置用于处理的视频素材数据资产。 | `UMetaHumanPerformance` |
| `Set Audio` | 设置用于音频驱动模式的音频资产。 | `UMetaHumanPerformance` |
| `Set Identity` | 设置用于深度视频模式的 MetaHuman Identity 资产。 | `UMetaHumanPerformance` |
| `Set Processing Range` | 设置需要处理的起始和结束帧。 | `UMetaHumanPerformance` |
| `Export Animation Sequence` | 使用默认或自定义的导出设置，将处理结果导出为一个 `AnimSequence` 资产。 | `UMetaHumanPerformanceExportUtils` |
| `Export Level Sequence` | 使用默认或自定义的导出设置，将处理结果（包括动画、媒体、相机等）导出为一个 `LevelSequence` 资产。 | `UMetaHumanPerformanceExportUtils` |
| `Get Export Animation Sequence Settings` | 获取一个基于当前 Performance 资产配置预填充的 `ExportAnimationSettings` 对象，用于蓝图中的导出控制。 | `UMetaHumanPerformanceExportUtils` |
| `Get Export Level Sequence Settings` | 获取一个基于当前 Performance 资产配置预填充的 `ExportLevelSequenceSettings` 对象，用于蓝图中的导出控制。 | `UMetaHumanPerformanceExportUtils` |
| `Diagnostics Indicates Processing Issue` | 运行后处理诊断，检查是否存在可能影响质量的问题（如深度覆盖不足、比例差异等）。 | `UMetaHumanPerformance` |

### 使用示例（蓝图描述）

1.  **处理一段深度视频并导出动画**：
    - 创建一个 `MetaHumanPerformance` 资产。
    - 在蓝图中，获取该资产引用。
    - 调用 `Set Input Type` 节点，选择 `DepthFootage`。
    - 调用 `Set Footage Capture Data` 节点，传入你的 `FootageCaptureData` 资产。
    - 调用 `Set Identity` 节点，传入对应的 `MetaHumanIdentity` 资产。
    - 调用 `Set Processing Range` 设置你想处理的帧范围（可选）。
    - 调用 `Start Pipeline` 节点开始处理。
    - 监听 `On Processing Finished Dynamic` 动态多播委托，在处理完成后执行后续逻辑。
    - 在回调中，调用 `Export Animation Sequence` 节点，将结果保存为动画序列。

2.  **使用自定义设置批量导出**：
    - 调用 `Get Export Animation Sequence Settings` 获取设置对象。
    - 修改设置对象上的属性（如 `bEnableHeadMovement`, `ExportRange` 等）。
    - 调用 `Export Animation Sequence` 节点，并将修改后的设置对象作为参数传入。

## C++ 用法

### 头文件引入

```cpp
#include “MetaHumanPerformance.h”
#include “MetaHumanPerformanceExportUtils.h”
```

### 基本用法

以下代码展示了如何在 C++ 中控制一个 MetaHuman Performance 资产的处理流程。

*来源：基于 `UMetaHumanPerformance` 公共接口推断。*

```cpp
// 假设我们有一个 UMetaHumanPerformance* PerformanceAsset 指针
void ProcessPerformanceCapture()
{
    // 1. 设置输入类型为深度视频
    PerformanceAsset->SetInputType(EDataInputType::DepthFootage);

    // 2. 关联素材和身份资产
    UFootageCaptureData* MyCaptureData = LoadObject<UFootageCaptureData>(nullptr, TEXT(“/Game/MyCaptureData”));
    UMetaHumanIdentity* MyIdentity = LoadObject<UMetaHumanIdentity>(nullptr, TEXT(“/Game/MyIdentity”));
    PerformanceAsset->SetFootageCaptureData(MyCaptureData);
    PerformanceAsset->SetIdentity(MyIdentity);

    // 3. 设置处理范围（例如，处理前100帧）
    PerformanceAsset->SetProcessingRange(0, 100);

    // 4. 检查是否可以开始处理
    if (PerformanceAsset->CanProcess())
    {
        // 5. 启动非阻塞式处理流程
        EStartPipelineErrorType Error = PerformanceAsset->StartPipeline(false);
        if (Error == EStartPipelineErrorType::None)
        {
            // 6. 绑定完成委托（假设在某个对象中）
            PerformanceAsset->OnProcessingFinished().AddUObject(this, &UMyClass::OnProcessingComplete);
        }
    }
}

void UMyClass::OnProcessingComplete(TSharedPtr<const UE::MetaHuman::Pipeline::FPipelineData> InPipelineData)
{
    // 7. 处理完成后，可以调用导出功能
    UMetaHumanPerformanceExportAnimationSettings* ExportSettings = NewObject<UMetaHumanPerformanceExportAnimationSettings>();
    ExportSettings->ExportRange = EPerformanceExportRange::WholeSequence;
    ExportSettings->bExportFace = true;

    UAnimSequence* ExportedAnim = UMetaHumanPerformanceExportUtils::ExportAnimationSequence(PerformanceAsset, ExportSettings);
    if (ExportedAnim)
    {
        UE_LOG(LogTemp, Log, TEXT(“Successfully exported animation: %s”), *ExportedAnim->GetName());
    }
}
```

### 进阶用法：监听逐帧处理进度

通过绑定 `OnFrameProcessed` 委托，可以监控处理进度并实现实时预览。

*来源：基于 `FOnFrameProcessed` 委托和 `FMetaHumanPerformanceEditorToolkit` 中的处理逻辑推断。*

```cpp
// 在处理开始前绑定帧处理委托
PerformanceAsset->OnFrameProcessed().AddUObject(this, &UMyClass::OnFrameProcessed);
PerformanceAsset->OnStageProcessingFinished().AddUObject(this, &UMyClass::OnStageFinished);

void UMyClass::OnFrameProcessed(int32 InFrameNumber)
{
    UE_LOG(LogMetaHumanPerformance, Verbose, TEXT(“Processing frame: %d”), InFrameNumber);
    // 可以在这里更新UI进度条或触发实时预览的刷新
}

void UMyClass::OnStageFinished(int32 InCurrentStage)
{
    UE_LOG(LogMetaHumanPerformance, Log, TEXT(“Stage %d finished.”), InCurrentStage);
    // 处理是分阶段进行的（例如，轮廓跟踪、动画求解），此委托在每个主要阶段结束时触发
}
```

## Demo 示例

一个最小的、可编译的 C++ 示例，演示如何创建并启动一个 MetaHuman Performance 的处理流程。

*注意：此示例假设你已经有一个正确设置的项目，并且 MetaHuman 插件已启用。*

```cpp
// MyMetaHumanDemoActor.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MetaHumanPerformance.h”
#include “MetaHumanPerformanceExportUtils.h”
#include “MyMetaHumanDemoActor.generated.h”

UCLASS()
class MYPROJECT_API AMyMetaHumanDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanDemoActor();

    // 在编辑器中或运行时调用此函数以开始处理
    UFUNCTION(BlueprintCallable, Category = “MetaHuman Demo”)
    void StartDemoProcessing();

protected:
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void OnProcessingComplete(TSharedPtr<const UE::MetaHuman::Pipeline::FPipelineData> InPipelineData);

    UPROPERTY(EditAnywhere, Category = “MetaHuman Demo”)
    TObjectPtr<UMetaHumanPerformance> PerformanceAsset;

    UPROPERTY(EditAnywhere, Category = “MetaHuman Demo”)
    TObjectPtr<UFootageCaptureData> CaptureDataAsset;

    UPROPERTY(EditAnywhere, Category = “MetaHuman Demo”)
    TObjectPtr<UMetaHumanIdentity> IdentityAsset;
};

// MyMetaHumanDemoActor.cpp
#include “MyMetaHumanDemoActor.h”
#include “Engine/World.h”

AMyMetaHumanDemoActor::AMyMetaHumanDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanDemoActor::BeginPlay()
{
    Super::BeginPlay();
    // 通常在编辑器中操作资产，在运行时可以在此处动态创建或加载
    if (!PerformanceAsset)
    {
        PerformanceAsset = NewObject<UMetaHumanPerformance>();
        // 这里需要将资产保存到磁盘或作为瞬态对象处理，仅为演示
    }
}

void AMyMetaHumanDemoActor::StartDemoProcessing()
{
    if (!PerformanceAsset || !CaptureDataAsset || !IdentityAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT(“Missing required assets for MetaHuman demo.”));
        return;
    }

    // 配置性能资产
    PerformanceAsset->SetInputType(EDataInputType::DepthFootage);
    PerformanceAsset->SetFootageCaptureData(CaptureDataAsset);
    PerformanceAsset->SetIdentity(IdentityAsset);
    PerformanceAsset->SetProcessingRange(0, 50); // 处理前50帧作为演示

    if (PerformanceAsset->CanProcess())
    {
        // 绑定完成回调
        PerformanceAsset->OnProcessingFinished().AddUObject(this, &AMyMetaHumanDemoActor::OnProcessingComplete);

        // 启动处理（非阻塞）
        EStartPipelineErrorType Error = PerformanceAsset->StartPipeline(false);
        if (Error == EStartPipelineErrorType::None)
        {
            UE_LOG(LogTemp, Log, TEXT(“MetaHuman processing started.”));
        }
    }
}

void AMyMetaHumanDemoActor::OnProcessingComplete(TSharedPtr<const UE::MetaHuman::Pipeline::FPipelineData> InPipelineData)
{
    UE_LOG(LogTemp, Log, TEXT(“MetaHuman processing complete.”));

    // 导出动画序列
    UMetaHumanPerformanceExportAnimationSettings* Settings = NewObject<UMetaHumanPerformanceExportAnimationSettings>();
    Settings->ExportRange = EPerformanceExportRange::ProcessingRange; // 只导出我们处理的范围
    Settings->bAutoSaveAnimSequence = false; // 示例中不自动保存

    UAnimSequence* AnimSequence = UMetaHumanPerformanceExportUtils::ExportAnimationSequence(PerformanceAsset, Settings);
    if (AnimSequence)
    {
        UE_LOG(LogTemp, Log, TEXT(“Exported animation sequence asset: %s”), *AnimSequence->GetPathName());
        // 在这里可以将 AnimSequence 应用到场景中的 SkeletalMeshComponent 上
    }

    // 解除委托绑定
    PerformanceAsset->OnProcessingFinished().RemoveAll(this);
}
```

## 模块依赖

要使用 `MetaHumanPerformance` 模块，你的模块需要依赖以下独特模块（除了标准的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureUtils` | 提供底层的捕捉数据处理工具和接口。 |
| `MetaHumanPipeline` | 定义和处理动画生成的数据处理流水线。 |
| `MetaHumanFaceContourTracker` | 实现面部轮廓的跟踪算法。 |
| `MetaHumanFaceAnimationSolver` | 将跟踪到的轮廓数据求解为面部动画控制曲线。 |
| `MetaHumanDepthGenerator` | 从单目视频估计深度信息。 |
| `MetaHumanSpeech2Face` | 从音频生成面部动画。 |
| `MetaHumanCore` | MetaHuman 系统的核心功能和类型定义。 |
| `MetaHumanIdentity` | 存储和管理 MetaHuman 的数字替身身份数据。 |
| `MetaHumanFaceFittingSolver` | 将身份网格与表演数据进行拟合。 |
| `ControlRig` / `ControlRigDeveloper` | 用于定义和驱动 MetaHuman 的控制装备。 |
| `MovieScene` / `LevelSequence` | 用于将动画结果录制到关卡序列中。 |
| `IKRetargeter` | 用于在不同骨骼间重定向身体动画。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体跟踪时禁用关卡序列导出功能，避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染时出现的伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体跟踪模式下过滤可视觉化对象，优化显示。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持将动画序列导出到已存在的网格体上。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

- **活跃维护**：从 git 历史看，该模块在**2026年5月**仍有频繁的功能性更新和错误修复，表明它处于**非常活跃的维护状态**。
- **核心功能**：作为 MetaHuman 工具链的核心组件，其重要性高，Epic Games 有持续投入的动机。
- **已知限制**：根据代码，一些高级功能（如特定的解算类型、身体跟踪）仍在发展中，可能需要搭配最新版本的引擎和 MetaHuman 作品使用。
- **推荐使用**：对于所有需要从真实表演数据生成 MetaHuman 动画的项目，**强烈推荐使用**此模块。它是官方支持的工作流程，稳定性和功能性在持续提升。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/MetaHuman/MetaHumanAnimator/index.html)（包含 MetaHuman Animator 整体工作流）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Private/Tests)