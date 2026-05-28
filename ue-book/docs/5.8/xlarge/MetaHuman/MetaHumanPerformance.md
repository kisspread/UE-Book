# MetaHuman Animator - 动画表演

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 动画表演 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、处理工具、编辑器UI） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🏛️ 文物（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个复杂的工具集，其核心功能是将真实世界的表演数据（视频或音频）转换为可用于驱动 MetaHuman 角色的动画数据。它解决了从原始采集数据（如深度相机拍摄的视频、音频文件或单目视频）中提取高质量面部、舌头和身体动画的难题。该模块并非单一功能，而是包含了一个完整的流水线，涵盖了数据导入、追踪（面部轮廓、身体）、求解（动画求解器、面部拟合）、深度生成、批量处理以及动画序列的录制与导出。

具体来说，`MetaHumanPerformance` 模块是整个流水线的核心资产和控制器。用户创建一个 `UMetaHumanPerformance` 资产，指定输入数据源（深度视频、音频或单目视频）和一个 `MetaHumanIdentity`（角色数字替身），配置处理参数后，即可启动一个复杂的计算流水线，最终生成可用于 Control Rig 的动画数据。

## 使用场景

*   **你需要将深度相机（如 iPhone LiDAR）拍摄的表演视频转换为高保真面部动画**：使用 `EDataInputType::DepthFootage` 输入类型，结合 MetaHuman Identity 和深度数据，可以获得最精确的面部追踪和动画结果。
*   **你需要根据一段对话音频生成角色的口型动画（Lip Sync）**：使用 `EDataInputType::Audio` 输入类型，无需任何视频素材，即可从音频文件驱动面部动画，甚至能生成眨眼等辅助动画。
*   **你只有一段普通的单目视频（如手机拍摄），希望生成面部或身体动画**：使用 `EDataInputType::MonoFootage` 输入类型，虽然精度可能低于深度数据，但适用性更广。还可以启用身体追踪 (`bBodyTracking`) 来生成全身动画。
*   **你需要批量处理大量的表演素材**：利用 `MetaHumanBatchProcessor` 模块对多个 `UMetaHumanPerformance` 资产进行队列处理。
*   **你需要将处理完成的动画导出为独立的 Animation Sequence 或包含媒体、相机、角色的 Level Sequence**：使用 `UMetaHumanPerformanceExportUtils` 工具类进行灵活的导出设置。

## 蓝图用法

以下节点均位于 `UMetaHumanPerformance` 类中，可通过蓝图编辑器访问。

### 核心控制节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Pipeline` | 启动动画处理流水线。返回 `EStartPipelineErrorType` 表示启动状态（成功、无帧、已禁用）。 | `UMetaHumanPerformance` |
| `Cancel Pipeline` | 取消正在进行的动画处理。 | `UMetaHumanPerformance` |
| `Is Processing` | 查询当前是否正在处理动画数据。 | `UMetaHumanPerformance` |
| `Can Process` | 检查当前配置是否满足启动处理的条件（例如，是否设置了有效的数据源和身份）。 | `UMetaHumanPerformance` |
| `Set Processing Range` | 设置要处理的帧范围（起始帧和结束帧）。 | `UMetaHumanPerformance` |

### 数据配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Input Type` | 设置数据输入类型（深度视频、音频、单目视频）。会清除之前模式的处理状态。 | `UMetaHumanPerformance` |
| `Set Footage Capture Data` | 设置用于深度视频或单目视频输入的视频采集数据资产 (`UFootageCaptureData`)。 | `UMetaHumanPerformance` |
| `Set Audio` | 设置用于音频输入的声音波形资产 (`USoundWave`)。 | `UMetaHumanPerformance` |
| `Set Identity` | 设置用于此表演的 MetaHuman Identity 资产。 | `UMetaHumanPerformance` |
| `Set Control Rig Asset Reference` | 设置用于驱动动画的 Control Rig 资产。 | `UMetaHumanPerformance` |
| `Set Depth Distance Range` | 设置深度生成时有效深度的最小和最大距离（厘米）。 | `UMetaHumanPerformance` |
| `Set Body Tracking` | 启用或禁用身体追踪（仅在单目视频模式下有效）。 | `UMetaHumanPerformance` |

### 导出节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Can Export Animation` | 检查当前性能资产是否已准备好导出动画序列。 | `UMetaHumanPerformance` |
| `Export Animation Sequence` | 使用给定的设置，从性能资产导出一个动画序列 (`UAnimSequence`)。 | `UMetaHumanPerformanceExportUtils` |
| `Export Level Sequence` | 使用给定的设置，从性能资产导出一个关卡序列 (`ULevelSequence`)。 | `UMetaHumanPerformanceExportUtils` |
| `Get Export Animation Sequence Settings` | 根据给定的性能资产，返回一个预配置的导出动画设置对象 (`UMetaHumanPerformanceExportAnimationSettings`)。 | `UMetaHumanPerformanceExportUtils` |
| `Get Export Level Sequence Settings` | 根据给定的性能资产，返回一个预配置的导出关卡序列设置对象 (`UMetaHumanPerformanceExportLevelSequenceSettings`)。 | `UMetaHumanPerformanceExportUtils` |

### 事件节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `On Processing Finished Dynamic` | 当流水线运行完成时触发的动态委托。 | `UMetaHumanPerformance` |

### 使用示例（蓝图描述）

1.  **创建与配置**：
    *   在内容浏览器中右键 -> MetaHuman -> Performance 创建一个新的 `MetaHumanPerformance` 资产。
    *   打开资产编辑器，在细节面板中设置 `Input Type` 为 `Depth Footage`。
    *   设置 `Footage Capture Data` 为你的深度视频资产。
    *   设置 `Identity` 为你创建的对应人物的 `MetaHumanIdentity` 资产。
    *   调整 `Start Frame To Process` 和 `End Frame To Process` 以定义你想要处理的片段范围。

2.  **处理与预览**：
    *   在编辑器工具栏点击“开始处理”按钮（或蓝图中调用 `Start Pipeline` 节点）。
    *   勾选 `Show Frames As They AreProcessed` 可以在处理时实时预览结果。
    *   处理完成后，Sequencer 内会出现动画数据，可以在视口中实时播放预览。

3.  **导出**：
    *   在蓝图中，使用 `Get Export Animation Sequence Settings` 节点获取设置对象。
    *   可以修改设置对象的属性，例如 `bEnableHeadMovement`, `ExportRange`, `CurveInterpolation` 等。
    *   最后调用 `Export Animation Sequence` 节点，传入性能资产和设置对象，即可将动画保存为新的资产。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPerformance.h"
#include "MetaHumanPerformanceExportUtils.h"
```

### 基本用法

以下代码展示了如何以编程方式创建、配置和启动一个 `UMetaHumanPerformance` 资产的处理流程。代码基于 `UMetaHumanPerformance` 类的公共接口构建。

```cpp
// 假设我们已经获取了所需的资产引用
UFootageCaptureData* MyFootageData = ...; // 加载或获取你的视频数据资产
UMetaHumanIdentity* MyIdentity = ...;     // 加载或获取你的 MetaHuman Identity 资产

// 创建新的 Performance 资产
UMetaHumanPerformance* NewPerformance = NewObject<UMetaHumanPerformance>(GetTransientPackage(), FName("MyPerformance"));

// 设置输入类型
NewPerformance->SetInputType(EDataInputType::DepthFootage);

// 设置数据源
NewPerformance->SetFootageCaptureData(MyFootageData);
NewPerformance->SetIdentity(MyIdentity);

// 配置处理范围
NewPerformance->SetProcessingRange(0, 100); // 处理第0到100帧

// 设置一些处理参数
NewPerformance->SolveType = ESolveType::AdditionalTweakers;
NewPerformance->bShowFramesAsTheyAreProcessed = true; // 处理时显示帧

// 检查是否可以处理
if (NewPerformance->CanProcess())
{
    // 启动处理流水线 (bInIsScriptedProcessing = true 表示脚本调用)
    EStartPipelineErrorType StartError = NewPerformance->StartPipeline(true);
    if (StartError == EStartPipelineErrorType::None)
    {
        UE_LOG(LogTemp, Log, TEXT("Performance processing started successfully."));
        // 在实际应用中，你可能需要轮询 IsProcessing() 或监听完成事件
    }
}
```

### 进阶用法

处理完成后，通常需要将动画数据导出。以下代码展示了如何使用 `UMetaHumanPerformanceExportUtils` 导出一个动画序列。

```cpp
// 假设 PerformanceData 是一个已完成处理的 UMetaHumanPerformance 指针
if (PerformanceData && !PerformanceData->IsProcessing())
{
    // 1. 获取默认的导出设置
    UMetaHumanPerformanceExportAnimationSettings* ExportSettings = UMetaHumanPerformanceExportUtils::GetExportAnimationSequenceSettings(PerformanceData);

    // 2. 根据需要修改设置
    if (ExportSettings)
    {
        ExportSettings->ExportRange = EPerformanceExportRange::ProcessingRange; // 只导出处理范围
        ExportSettings->bEnableHeadMovement = true;
        ExportSettings->CurveInterpolation = RCIM_Linear;
        ExportSettings->bRemoveRedundantCurveKeys = true;
        ExportSettings->AssetName = TEXT("ExportedAnim_MyPerformance");
        ExportSettings->PackagePath = TEXT("/Game/Animations/");
        ExportSettings->bShowExportDialog = false; // 禁止弹出保存对话框
    }

    // 3. 执行导出
    UAnimSequence* ExportedAnimSequence = UMetaHumanPerformanceExportUtils::ExportAnimationSequence(PerformanceData, ExportSettings);

    if (ExportedAnimSequence)
    {
        UE_LOG(LogTemp, Log, TEXT("Animation sequence exported: %s"), *ExportedAnimSequence->GetName());
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何在 C++ Actor 中使用 `UMetaHumanPerformance` 进行异步处理。

**MyPerformanceActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanPerformance.h"
#include "MyPerformanceActor.generated.h"

UCLASS()
class AMyPerformanceActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyPerformanceActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    TObjectPtr<UFootageCaptureData> FootageData;

    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    TObjectPtr<UMetaHumanIdentity> IdentityAsset;

    UPROPERTY(VisibleAnywhere, Category = "MetaHuman")
    TObjectPtr<UMetaHumanPerformance> PerformanceAsset;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void StartProcessing();

private:
    UFUNCTION()
    void OnProcessingFinished();

    FDelegateHandle OnProcessingFinishedDelegate;
};
```

**MyPerformanceActor.cpp**
```cpp
#include "MyPerformanceActor.h"
#include "UObject/SavePackage.h"

AMyPerformanceActor::AMyPerformanceActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPerformanceActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建性能资产
    PerformanceAsset = NewObject<UMetaHumanPerformance>(this, TEXT("MyPerformance"));

    // 绑定完成事件
    OnProcessingFinishedDelegate = PerformanceAsset->OnProcessingFinished.AddUObject(this, &AMyPerformanceActor::OnProcessingFinished);
}

void AMyPerformanceActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (PerformanceAsset)
    {
        PerformanceAsset->OnProcessingFinished.Remove(OnProcessingFinishedDelegate);
        if (PerformanceAsset->IsProcessing())
        {
            PerformanceAsset->CancelPipeline();
        }
    }
    Super::EndPlay(EndPlayReason);
}

void AMyPerformanceActor::StartProcessing()
{
    if (!PerformanceAsset || !FootageData || !IdentityAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("Missing required references for processing."));
        return;
    }

    // 配置
    PerformanceAsset->SetInputType(EDataInputType::DepthFootage);
    PerformanceAsset->SetFootageCaptureData(FootageData);
    PerformanceAsset->SetIdentity(IdentityAsset);
    PerformanceAsset->SetProcessingRange(0, 50);

    // 开始处理
    if (PerformanceAsset->CanProcess())
    {
        PerformanceAsset->StartPipeline(true); // true for scripted processing
        UE_LOG(LogTemp, Log, TEXT("Processing started for actor %s"), *GetName());
    }
}

void AMyPerformanceActor::OnProcessingFinished()
{
    UE_LOG(LogTemp, Log, TEXT("Processing finished for actor %s"), *GetName());
    // 这里可以触发后续的导出逻辑
    if (PerformanceAsset->CanExportAnimation())
    {
        UMetaHumanPerformanceExportAnimationSettings* Settings = UMetaHumanPerformanceExportUtils::GetExportAnimationSequenceSettings(PerformanceAsset);
        Settings->bShowExportDialog = false;
        Settings->AssetName = TEXT("Anim_FromActor");
        UAnimSequence* Anim = UMetaHumanPerformanceExportUtils::ExportAnimationSequence(PerformanceAsset, Settings);
        if (Anim)
        {
            UE_LOG(LogTemp, Log, TEXT("Exported animation: %s"), *Anim->GetName());
        }
    }
}
```

## 模块依赖

要使用 `MetaHumanPerformance` 模块及其相关功能，你的模块需要在 `Build.cs` 中添加以下非标准依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanPerformance` | 核心性能资产和处理逻辑 |
| `MetaHumanCore` | MetaHuman 通用核心工具和类型 |
| `MetaHumanCoreTechLib` | 核心技术库（如图像处理、数学算法） |
| `MetaHumanSDKEditor` | 编辑器相关的 SDK 功能 |
| `MetaHumanPipeline` | 处理流水线的定义和运行框架 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪功能 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanSpeech2Face` | 音频驱动面部动画模块 |
| `MetaHumanCaptureData` | 捕获数据（如 FootageCaptureData）的定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关问题。 |

### 维护评价

MetaHuman Animator 是一个**活跃维护**的大型插件。尽管其确切创建时间未知，但从其复杂的架构和近期密集的提交记录（2026年5月有多次功能增强和Bug修复）来看，它仍然是 Epic Games 重点维护的官方工具。

**优点**：
*   **功能强大且完整**：提供从原始数据到最终动画的完整解决方案。
*   **官方支持**：由 Epic Games 官方维护，与 Unreal Engine 版本保持兼容。
*   **持续更新**：近期提交显示团队在不断改进功能（如身体追踪导出）和修复问题（渲染、缓存）。

**注意事项**：
*   **复杂性高**：模块众多，学习和集成曲线陡峭。
*   **默认未启用**：`EnabledByDefault=false`，需要在项目插件设置中手动启用。
*   **部分功能标记为Deprecated**：代码中可见一些 5.1 和 5.8 版本废弃的函数和变量，升级时需注意迁移。

**推荐使用**：如果你需要将真实的表演数据转换为高质量的 MetaHuman 角色动画，MetaHuman Animator 是官方且功能完备的首选方案。尽管学习成本较高，但其生产质量的结果和持续的维护使其值得投入。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
*   [官方文档]() （.uplugin 中未提供 DocsURL）
*   [测试用例]() （源码包中的测试文件路径通常为 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Private/Tests/`，但当前信息中未列出具体测试文件）