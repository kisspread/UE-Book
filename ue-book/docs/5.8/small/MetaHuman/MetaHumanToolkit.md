# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产， 材质模板， 配置文件， 测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 核心工具集，旨在简化从原始面部捕捉数据（视频）创建高品质、可用于生产的 MetaHuman 角色面部动画的全流程。它不是一个单一功能的插件，而是一个完整的工具箱，整合了面部轮廓追踪、深度图生成、动画解算、面部模型拟合、性能捕捉、语音驱动动画等多个复杂的技术栈，让用户能够在 Unreal Editor 内完成从数据导入到最终动画序列输出的完整工作流。

## 使用场景

- **虚拟角色创建**：你需要为一个需要高质量面部动画的电影、游戏或虚拟制作项目创建一个数字人。
- **数字化身驱动**：你有一段演员的表演视频（或深度相机数据），需要将其驱动到 MetaHuman 角色模型上。
- **批量处理与流水线集成**：你需要在一个自动化流水线中批量处理大量面部捕捉数据，将其转换为可用的动画资产。
- **语音驱动表情**：你只有角色的语音音轨，希望自动生成对应的面部口型动画。

## 蓝图用法

由于 `MetaHumanAnimator` 是一个由多个模块组成的大型工具集，其核心蓝图功能通常通过编辑器工具（如 `MetaHumanCreator`， `MetaHumanAnimator` 面板）和资产编辑器（如 `MetaHumanIdentity` 资产， `MetaHumanPerformance` 资产）来呈现。以下是基于模块结构推断的核心工作流节点/功能：

### 核心节点

| 节点 | 说明 | 所在类/资产 |
|---|---|---|
| `Create New MetaHuman` | 从一张或多张照片创建一个新的 MetaHuman 基础资产。 | 编辑器工具 |
| `Add Tracking Data` | 向一个 MetaHuman 性能资产中添加视频序列或深度序列数据。 | `UMetaHumanPerformance` |
| `Solve Animation` | 对已导入的追踪数据运行面部动画解算，生成基础动画曲线。 | `UMetaHumanPerformance` |
| `Fit to Mesh` | 将解算出的动画应用到具体的 MetaHuman 面部网格体上。 | `UMetaHumanIdentity` |
| `Export Animation Sequence` | 将最终的面部动画导出为可在 Sequencer 中使用的动画序列资产。 | `UMetaHumanPerformance` |
| `Batch Process` | 使用批处理器对多个性能资产执行相同的操作（如解算、导出）。 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

1.  **创建 MetaHuman 身份**：在内容浏览器中右键创建 `MetaHuman Identity` 资产，打开后导入一张或多张正面人脸照片，插件会自动运行面部追踪和网格体拟合。
2.  **准备动画表演**：创建一个 `MetaHuman Performance` 资产，通过拖拽或资产对话框导入一段视频文件或包含视频和深度图的图像序列。
3.  **解算与预览**：在 Performance 资产编辑器中，点击 “Solve” 按钮。插件会运行 `MetaHumanFaceAnimationSolver` 和 `MetaHumanFaceContourTracker` 模块，在视口实时预览解算效果。
4.  **应用到角色**：在解算满意后，点击 “Apply to Identity” 按钮。插件会调用 `MetaHumanFaceFittingSolver`，将动画数据适配到你在第一步创建的 MetaHuman 身份所对应的面部骨骼和变形目标上。
5.  **导出与使用**：点击 “Export Animation Sequence” 按钮，生成的动画序列资产可以直接拖拽到 Sequencer 时间线上，驱动你的 MetaHuman 角色。

## C++ 用法

`MetaHumanToolkit` 模块本身可能作为上层工具的协调层。更底层的用法涉及直接调用 `MetaHumanPipeline`、`MetaHumanFaceAnimationSolver` 等模块的 API。

### 头文件引入

```cpp
#include “MetaHumanToolkit.h”
// 通常更核心的功能在以下模块中
#include “MetaHumanCore/Public/MetaHumanPerformance.h”
#include “MetaHumanFaceAnimationSolver/Public/FaceAnimationSolver.h”
```

### 基本用法

以下是一个概念性的代码片段，展示如何通过代码驱动解算流程。实际API可能更复杂，需参考具体头文件。

```cpp
// 来源: MetaHumanPipeline 模块流程管理概念
#include “MetaHumanPipeline/Pipeline.h”
#include “MetaHumanFaceAnimationSolver/FaceAnimationSolver.h”

// 假设你已经有一个加载了视频数据的 MetaHumanPerformance 对象 (PerformanceAsset)
UMetaHumanPerformance* PerformanceAsset = GetMyPerformanceAsset();

// 1. 获取或创建一个 Pipeline 实例
UMetaHumanPipeline* Pipeline = UMetaHumanPipeline::CreatePipeline(PerformanceAsset);

// 2. 配置解算器 (示例)
UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();
// 对 Solver 进行各种参数设置...
Pipeline->SetStage(Solver);

// 3. 运行 Pipeline
Pipeline->Run();

// 4. 监听完成回调（通常在 Actor 或 EditorSubsystem 中）
Pipeline->OnPipelineCompleted.AddDynamic(this, &AMyActor::OnAnimationSolved);
```

### 进阶用法

批处理模块 `MetaHumanBatchProcessor` 可以用来处理大量资产。

```cpp
// 来源: MetaHumanBatchProcessor 模块用法
#include “MetaHumanBatchProcessor/BatchProcessor.h”

// 收集要处理的 Performance 资产
TArray<UMetaHumanPerformance*> PerformancesToProcess;
// ... 从磁盘加载或从其他逻辑获取 ...

// 创建批处理任务
UMetaHumanBatchProcessingTask* Task = NewObject<UMetaHumanBatchProcessingTask>();
Task->SetPerformances(PerformancesToProcess);
Task->SetTaskType(EMetaHumanBatchTaskType::SolveAndExport); // 设置任务类型

// 启动批处理
UMetaHumanBatchProcessor::Get()->StartTask(Task);

// 批处理会在后台线程运行，并触发进度和完成事件
```

## Demo 示例

以下示例展示如何创建一个简单的 Actor，在开始运行时加载一个预设的 Performance 资产并触发解算（概念性演示）。

**MyMetaHumanAnimatorActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MyMetaHumanAnimatorActor.generated.h”

class UMetaHumanPerformance;

UCLASS()
class MYPROJECT_API AMyMetaHumanAnimatorActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanAnimatorActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category=“MetaHuman”)
    TSoftObjectPtr<UMetaHumanPerformance> PerformanceAssetToLoad;

    UPROPERTY()
    UMetaHumanPerformance* LoadedPerformance;

    UFUNCTION()
    void OnPerformanceLoaded();
    UFUNCTION()
    void OnSolvingComplete(bool bSuccess);
};
```

**MyMetaHumanAnimatorActor.cpp**
```cpp
#include “MyMetaHumanAnimatorActor.h”
#include “MetaHumanCore/Public/MetaHumanPerformance.h”
#include “Engine/StreamableManager.h”

AMyMetaHumanAnimatorActor::AMyMetaHumanAnimatorActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanAnimatorActor::BeginPlay()
{
    Super::BeginPlay();

    if (PerformanceAssetToLoad.IsValid())
    {
        // 异步加载 Performance 资产
        FStreamableManager& StreamableManager = UAssetManager::GetStreamableManager();
        StreamableManager.RequestAsyncLoad(
            PerformanceAssetToLoad.ToSoftObjectPath(),
            FStreamableDelegate::CreateUObject(this, &AMyMetaHumanAnimatorActor::OnPerformanceLoaded)
        );
    }
}

void AMyMetaHumanAnimatorActor::OnPerformanceLoaded()
{
    LoadedPerformance = PerformanceAssetToLoad.Get();
    if (LoadedPerformance)
    {
        // 为演示目的，这里直接绑定事件并开始解算。
        // 实际使用中，解算可能由编辑器工具触发。
        LoadedPerformance->OnSolveCompleted.AddDynamic(this, &AMyMetaHumanAnimatorActor::OnSolvingComplete);
        // 假设存在一个开始解算的函数
        // LoadedPerformance->BeginSolve();
        UE_LOG(LogTemp, Log, TEXT(“MetaHuman Performance Asset loaded and ready.”));
    }
}

void AMyMetaHumanAnimatorActor::OnSolvingComplete(bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT(“MetaHuman Animation Solving Completed Successfully!”));
        // 在这里可以导出动画或执行其他操作
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“MetaHuman Animation Solving Failed.”));
    }
    // 清除绑定
    if (LoadedPerformance)
    {
        LoadedPerformance->OnSolveCompleted.RemoveDynamic(this, &AMyMetaHumanAnimatorActor::OnSolvingComplete);
    }
}
```

## 模块依赖

使用 `MetaHumanAnimator` 中的模块，你的模块需要依赖其子模块。以下是 `MetaHumanToolkit` 本身的一些关键依赖，以及整个插件的核心依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 系统的核心类型定义， 如 `UMetaHumanPerformance`。 |
| `MetaHumanCaptureUtils` | 提供面部捕捉数据处理的通用工具函数。 |
| `MetaHumanFaceAnimationSolver` | 提供将追踪数据解算为动画曲线的核心算法。 |
| `MetaHumanFaceContourTracker` | 提供从视频帧中检测和追踪面部轮廓点的功能。 |
| `MetaHumanPipeline` | 提供处理流程（Pipeline）的框架， 用于串联不同的处理阶段。 |
| `MetaHumanIdentity` | 提供 MetaHuman 身份数据资产的定义和管理。 |
| `MetaHumanSequencer` | 提供将 MetaHuman 动画与 Sequencer 集成的扩展。 |
| `ControlRig` | UE 内置的动画控制系统， MetaHuman 面部动画最终通过 ControlRig 驱动。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 的**核心战略产品**，其维护状态极其活跃。从近期提交记录可以看出，几乎每天都有更新，且包含重要的功能修复（如序列导出兼容性、渲染瑕疵）和新功能（为现有网格体导出动画）。虽然插件创建时间未明确，但作为 MetaHuman 生态的支柱，它持续受到高强度投入。

**综合评价**：
- **维护等级**：活跃维护，核心产品。
- **推荐度**：强烈推荐。对于任何涉及 MetaHuman 角色的面部动画制作项目，这是官方且功能最全面的解决方案。
- **注意事项**：该插件依赖复杂的算法和庞大的资产库，学习曲线较陡。建议配合 Epic Games 官方的 MetaHuman 文档和教程进行学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （通常可在 Unreal Engine 官网 MetaHuman 板块找到， 但此字段在 .uplugin 中为空）
- [测试用例]() （具体路径需在源码仓库内搜索， 通常位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/` 下的 `Tests` 目录）