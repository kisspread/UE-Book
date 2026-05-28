# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画工具箱 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、测试资源） |
| 模块 | `MetaHumanPerformance` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPerformanceEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具套件。它解决的核心问题是将原始的表演捕捉数据（如视频或音频）高效、高质量地转换为可用于 MetaHuman 角色的动画序列。

其存在价值在于提供了一套完整的、深度集成的流程，让艺术家能够：
1.  **处理原始数据**：从深度视频、单目视频或纯音频输入中提取面部（和身体）动画数据。
2.  **驱动控制绑定**：将提取的数据烘焙到标准的 MetaHuman 面部和身体 Control Rig 上，实现精确控制。
3.  **集成与导出**：将生成的动画无缝集成到 Sequencer 中，并导出为标准的动画序列资产，用于最终渲染或实时应用。

该插件是一套庞大的、模块化的系统，其中 `MetaHumanPerformance` 模块是核心，负责管理“表演”资产、配置处理参数、启动处理管线并输出最终结果。

## 使用场景

-   **您拥有演员的深度摄像头拍摄视频**：使用 `EDataInputType::DepthFootage` 模式，结合一个 MetaHuman Identity 资产，将表演转换为高保真面部动画。
-   **您只有单目摄像头拍摄的视频**：使用 `EDataInputType::MonoFootage` 模式，无需深度数据，可直接从单视图视频中解算面部和身体动画。
-   **您只有音频文件**：使用 `EDataInputType::Audio` 模式，通过音频驱动生成对应的口型和面部表情动画。
-   **您需要将生成的动画应用到其他 MetaHuman 或骨骼网格体**：使用导出工具将动画序列重定向到不同的骨架。
-   **您需要在一个镜头内同时处理视频和音频**：将音频与视频素材关联，实现音画同步的动画生成。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartPipeline` | 启动处理管线，开始从输入数据生成动画。返回错误类型指示是否成功启动。 | `UMetaHumanPerformance` |
| `CancelPipeline` | 取消当前正在进行的处理。 | `UMetaHumanPerformance` |
| `IsProcessing` | 检查是否正在处理中。 | `UMetaHumanPerformance` |
| `CanProcess` | 检查当前状态是否允许开始处理。 | `UMetaHumanPerformance` |
| `SetInputType` | 设置数据输入类型（深度视频、音频、单目视频）。 | `UMetaHumanPerformance` |
| `SetFootageCaptureData` | 设置要处理的视频捕获数据资产。 | `UMetaHumanPerformance` |
| `SetAudio` | 设置音频数据源（用于音频模式）。 | `UMetaHumanPerformance` |
| `SetIdentity` | 设置用于处理的 MetaHuman Identity。 | `UMetaHumanPerformance` |
| `SetProcessingRange` | 设置处理的起始和结束帧范围。 | `UMetaHumanPerformance` |
| `ExportAnimationSequence` | 将处理结果导出为动画序列资产。 | `UMetaHumanPerformanceExportUtils` |
| `ExportLevelSequence` | 将处理结果导出为关卡序列，包含完整的场景设置。 | `UMetaHumanPerformanceExportUtils` |
| `GetExportAnimationSequenceSettings` | 获取默认的动画序列导出设置对象，以便进行自定义。 | `UMetaHumanPerformanceExportUtils` |
| `GetExportLevelSequenceSettings` | 获取默认的关卡序列导出设置对象，以便进行自定义。 | `UMetaHumanPerformanceExportUtils` |
| `DiagnosticsIndicatesProcessingIssue` | 检查处理诊断是否提示存在问题（如深度图覆盖不足）。 | `UMetaHumanPerformance` |

### 使用示例（蓝图描述）

1.  **创建并配置一个 Performance 资产**：在内容浏览器中右键创建 `MetaHumanPerformance` 资产。在资产编辑器或蓝图中，设置 `InputType` 为 `MonoFootage`，关联您的 `FootageCaptureData` 资产。
2.  **启动处理**：在蓝图中，获取该 `UMetaHumanPerformance` 对象的引用，调用 `StartPipeline` 节点。可以监听 `OnProcessingFinishedDynamic` 委托来得知处理完成。
3.  **导出动画**：处理完成后，调用 `GetExportAnimationSequenceSettings` 节点获取默认设置。如果需要，修改设置中的 `ExportRange` 或 `bExportBody` 等属性。然后调用 `ExportAnimationSequence` 节点，传入 Performance 和设置对象，指定保存路径，即可生成 `UAnimSequence` 资产。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPerformance.h"
#include "MetaHumanPerformanceExportUtils.h"
```

### 基本用法

从 `MetaHumanPerformance` 类的公有接口可以看出，其设计是“声明式”的：先配置好所有参数，然后启动处理。
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Public/MetaHumanPerformance.h`）

```cpp
// 假设已经拥有一个 UMetaHumanPerformance* Performance 对象
// 1. 配置输入类型和数据源
Performance->SetInputType(EDataInputType::MonoFootage);
Performance->SetFootageCaptureData(MyFootageCaptureData);

// 2. 设置处理范围 (可选)
Performance->SetProcessingRange(0, 100);

// 3. 启动处理
EStartPipelineErrorType Error = Performance->StartPipeline(false); // false 表示非脚本化，允许UI交互
if (Error == EStartPipelineErrorType::None)
{
    // 处理已开始，可以绑定委托监听完成事件
    Performance->OnProcessingFinishedDynamic.AddDynamic(this, &UMyClass::OnPerformanceFinished);
}

// 4. 在回调中检查状态
void UMyClass::OnPerformanceFinished()
{
    if (Performance && Performance->CanExportAnimation())
    {
        // 准备导出
    }
}
```

### 进阶用法

使用 `UMetaHumanPerformanceExportUtils` 进行精细控制的导出。
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Public/MetaHumanPerformanceExportUtils.h`）

```cpp
// 1. 获取并自定义导出设置
UMetaHumanPerformanceExportAnimationSettings* ExportSettings = UMetaHumanPerformanceExportUtils::GetExportAnimationSequenceSettings(Performance);
if (ExportSettings)
{
    ExportSettings->ExportRange = EPerformanceExportRange::ProcessingRange;
    ExportSettings->bExportFace = true;
    ExportSettings->bExportBody = true; // 如果启用了身体追踪
    ExportSettings->bRemoveRedundantCurveKeys = true;
}

// 2. 执行导出
UAnimSequence* AnimSeq = UMetaHumanPerformanceExportUtils::ExportAnimationSequence(Performance, ExportSettings);
if (AnimSeq)
{
    // 导出成功，AnimSeq 是生成的动画序列资产指针
    UE_LOG(LogTemp, Log, TEXT("Animation Sequence exported: %s"), *AnimSeq->GetName());
}

// 3. 检查骨架兼容性 (用于重定向到其他骨架时)
TArray<FString> MissingCurves;
bool bCompatible = ExportSettings->IsTargetSkeletonCompatible(RequiredCurveNames, MissingCurves);
if (!bCompatible)
{
    UE_LOG(LogTemp, Warning, TEXT("Target skeleton is missing %d curves."), MissingCurves.Num());
}
```

## Demo 示例

一个最小的、可编译的 C++ 示例，演示如何配置并启动 MetaHuman Performance 处理。需要配合编辑器中的 Performance 资产使用。

```cpp
// MyMetaHumanProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMetaHumanProcessor.generated.h"

class UMetaHumanPerformance;
class UFootageCaptureData;

UCLASS()
class MYGAME_API UMyMetaHumanProcessor : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void StartProcessingPerformance(UMetaHumanPerformance* Performance, UFootageCaptureData* Footage);

private:
    UFUNCTION()
    void OnProcessingFinished();

    UPROPERTY()
    TWeakObjectPtr<UMetaHumanPerformance> CurrentPerformance;
};

// MyMetaHumanProcessor.cpp
#include "MyMetaHumanProcessor.h"
#include "MetaHumanPerformance.h"

void UMyMetaHumanProcessor::StartProcessingPerformance(UMetaHumanPerformance* Performance, UFootageCaptureData* Footage)
{
    if (!Performance || !Footage) return;

    CurrentPerformance = Performance;
    Performance->SetInputType(EDataInputType::MonoFootage);
    Performance->SetFootageCaptureData(Footage);

    // 绑定完成回调
    Performance->OnProcessingFinishedDynamic.AddDynamic(this, &UMyMetaHumanProcessor::OnProcessingFinished);

    // 启动处理 (非阻塞)
    Performance->StartPipeline(false);
}

void UMyMetaHumanProcessor::OnProcessingFinished()
{
    if (UMetaHumanPerformance* Perf = CurrentPerformance.Get())
    {
        if (Perf->CanExportAnimation())
        {
            UE_LOG(LogTemp, Display, TEXT("MetaHuman Performance processing finished. Ready to export."));
            // 这里可以调用导出功能
        }
    }
    // 解绑
    if (UMetaHumanPerformance* Perf = CurrentPerformance.Get())
    {
        Perf->OnProcessingFinishedDynamic.RemoveDynamic(this, &UMyMetaHumanProcessor::OnProcessingFinished);
    }
    CurrentPerformance = nullptr;
}
```

## 模块依赖

要使用 `MetaHumanPerformance` 模块（或整个插件），你的模块需要依赖以下独特的模块（已在插件的 Build.cs 中列出）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供 MetaHuman 核心技术算法库，是处理管线的底层依赖。 |
| `UnrealEd` | 用于编辑器扩展，如资产工厂、自定义细节面板等。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |
| `ControlRigDeveloper` | 用于与 Control Rig 系统集成，编辑和驱动动画。 |
| `MetaHumanCaptureDataEditor` | 处理捕捉数据资产的编辑器功能。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分。 |

**注意**：该插件模块众多且相互依赖，实际开发中很可能需要根据你使用的具体功能，依赖一个或多个上层模块（如 `MetaHumanPipeline`, `MetaHumanIdentity`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：从 Git 历史看，最近一周内（2026-05-20 至 2026-05-22）有多次功能性更新和缺陷修复，表明该插件仍在被 Epic Games 积极维护和迭代。
- **功能密集且不断进化**：最近的提交涉及导出功能的增强（支持现有网格体）、渲染问题修复以及身体追踪功能的优化，显示出该插件正在完善功能、提升稳定性和用户体验。
- **实验性状态**：虽然 `.uplugin` 中 `IsExperimentalVersion` 为 `false`，但其功能复杂且模块庞大，部分功能（如身体追踪）可能仍在快速迭代中。近期更新频繁也佐证了这一点。
- **使用推荐**：**推荐使用**。作为 Epic 官方工具，它与 UE5 和 MetaHuman 生态系统深度集成，是生成 MetaHuman 角色动画的标准且高效的解决方案。建议关注官方更新日志以获取最新功能和修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](http://epicgames.com)（链接待补充）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Private/Tests)