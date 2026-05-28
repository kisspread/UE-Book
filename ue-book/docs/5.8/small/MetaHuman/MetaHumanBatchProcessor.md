# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、UI 面板、管线配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
MetaHuman Animator 插件是一个完整的端到端工具集，旨在将真实世界的面部捕捉数据（来自 iPhone、专业头盔摄像机或音频）驱动到 Unreal Engine 中的 MetaHuman 角色上。它不仅仅是一个简单的动画导入工具，而是一个涵盖了数据捕获、面部追踪、动画求解、性能调整和最终序列化导出的综合工作流。插件通过模块化设计，提供了从底层捕获协议处理（`MetaHumanCaptureProtocolStack`）、面部网格追踪与点云数据处理（`MeshTrackerInterface`）到高层动画求解器（`MetaHumanFaceAnimationSolver`）和集成的 Sequencer 工具（`MetaHumanSequencer`）等功能。其核心目的是简化将高保真面部动画集成到 UE 项目中的复杂流程，特别是针对使用 MetaHuman 角色的项目。

## 使用场景
- 你是一位动画师或技术美术，拥有来自专业面部动作捕捉系统的数据，并希望将其无缝驱动到你的 MetaHuman 角色上，同时需要精细控制求解过程和输出质量。
- 你的项目需要批量处理大量音频文件，以自动生成对应的 MetaHuman 面部动画（如对话、播客可视化），这时可以使用 `MetaHumanBatchProcessor` 模块。
- 你正在开发一个实时应用程序，需要利用 iPhone 的 TrueDepth 摄像头数据或音频流来实时驱动虚拟角色的面部表情。
- 你需要为 MetaHuman 角色创建并管理基于物理的性能数据（Performance），这些数据可以在 Sequencer 中进一步编辑和混合。

## 蓝图用法
插件主要通过编辑器工具和数据资产进行配置。基于提供的源码分析，蓝图可直接交互的暴露节点较少，核心功能通过 `MetaHumanPerformance`、`MetaHumanCaptureSource` 等资产类型以及编辑器专用面板来驱动。设置和导出选项通过特定的 UObject 结构体在编辑器 UI 中配置。

### 核心设置结构体
以下结构体可在蓝图或编辑器属性面板中配置，用于控制批量处理等流程。

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `bGenerateBlinks` | 是否生成眨眼动画 | `FMetaHumanSpeechProcessingSettings` |
| `bMixAudioChannels` | 是否在处理前将音频混合为单声道 | `FMetaHumanSpeechProcessingSettings` |
| `OutputControls` | 指定是处理全脸还是特定的控制子集 | `FMetaHumanSpeechProcessingSettings` |
| `SolveOverrides` | 覆盖默认的求解器参数 | `FMetaHumanSpeechProcessingSettings` |
| `bEnableHeadMovement` | 是否在导出时启用头部运动 | `FMetaHumanSpeechProcessingSettings` |
| `TargetSkeletonOrSkeletalMesh` | 导出动画序列时使用的目标骨架或骨骼网格体 | `FExportAnimSequenceSettings` |
| `CurveInterpolation` | 关键帧之间的插值方式 | `FExportAnimSequenceSettings` / `FExportLevelSequenceSettings` |
| `bExportAudioTrack` | 导出关卡序列时是否包含音轨 | `FExportLevelSequenceSettings` |
| `bExportCamera` | 导出关卡序列时是否包含摄像机轨道 | `FExportLevelSequenceSettings` |
| `TargetMetaHumanClass` | 导出的关卡序列中要生成的目标 MetaHuman 蓝图类 | `FExportLevelSequenceSettings` |

### 使用示例（蓝图描述）
这些设置通常不直接在蓝图图表中以节点形式使用，而是通过以下方式应用：
1.  创建或编辑 `MetaHumanPerformance` 资产时，其细节面板中会使用 `FMetaHumanSpeechProcessingSettings` 来配置音频处理参数。
2.  在 `MetaHumanBatchProcessor` 模块提供的导出向导或批量处理对话框中，你会配置 `FExportAnimSequenceSettings` 或 `FExportLevelSequenceSettings` 来定义导出规则。这些对话框是 `SMetaHumanBatchExportPathDialog` 和 `SMetaHumanSpeechToAnimProcessingSettings` 等 Slate 控件，其背后的数据模型就是上述结构体。

## C++ 用法
重点从提供的头文件结构推断用法，核心类是配置和驱动处理流程的 `UObject` 派生类。

### 头文件引入
```cpp
#include "MetaHumanBatchProcessor/MetaHumanBatchOperation.h"
#include "MetaHumanBatchProcessor/MetaHumanSpeechProcessingSettings.h"
```

### 基本用法
配置一个批量处理上下文 (`FMetaHumanBatchOperationContext`)，并用它来驱动一个批量操作。此示例展示了如何程序化地创建一个批量处理任务。
```cpp
// 来源于 MetaHumanBatchOperation.h 的结构定义和使用模式
#include "MetaHumanBatchProcessor/MetaHumanBatchOperation.h"

void RunABatchSpeechToAnimation()
{
    // 1. 准备源音频资产
    TArray<TWeakObjectPtr<UObject>> SourceAssets;
    // ... 从某处获取要处理的 USoundWave 资产 ...
    // SourceAssets.Add(MySoundWaveAsset);

    // 2. 配置批量处理上下文
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = SourceAssets;
    // 设置要执行的步骤：创建性能 -> 处理性能 -> 导出动画序列
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                             | EBatchOperationStepsFlags::ProcessPerformance
                             | EBatchOperationStepsFlags::ExportAnimSequence;

    // 配置处理选项
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;
    Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;

    // 配置导出选项
    Context.bEnableHeadMovement = true;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
    Context.bRemoveRedundantKeys = true;
    // ... 设置 TargetSkeletonOrSkeletalMesh 和其他导出路径规则 ...

    // 3. 创建并运行批量操作对象
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
    // RunProcess 将根据 Context 的配置，依次创建性能资产、处理它、并导出最终的动画序列。
}
```

### 进阶用法
直接操作单个 `UMetaHumanPerformance` 资产的属性，并可能使用更底层的求解器模块（例如 `MetaHumanFaceAnimationSolver`，尽管其具体 API 未在提供的片段中）。进阶用法可能涉及钩入 `MetaHumanPipeline` 进行自定义处理步骤，但这需要更深入的源码分析。

## Demo 示例
一个展示如何配置批量处理上下文并调用批量操作的最小 C++ 示例。
```cpp
// MyMetaHumanBatchProcessHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyMetaHumanBatchProcessHelper.generated.h"

UCLASS()
class UMyMetaHumanBatchProcessHelper : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    // 在编辑器工具中或通过控制台命令调用此函数
    UFUNCTION(Exec, Category = "MetaHuman")
    void DebugRunSimpleBatch();

private:
    void PopulateContext(FMetaHumanBatchOperationContext& InOutContext);
};
```
```cpp
// MyMetaHumanBatchProcessHelper.cpp
#include "MyMetaHumanBatchProcessHelper.h"
#include "MetaHumanBatchProcessor/MetaHumanBatchOperation.h"
#include "Engine/AssetManager.h"

void UMyMetaHumanBatchProcessHelper::DebugRunSimpleBatch()
{
    FMetaHumanBatchOperationContext Context;
    PopulateContext(Context);

    // 验证配置
    if (!Context.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Batch operation context is invalid. Aborting."));
        return;
    }

    // 执行批量操作
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
}

void UMyMetaHumanBatchProcessHelper::PopulateContext(FMetaHumanBatchOperationContext& InOutContext)
{
    // 这是一个示例，实际中应从用户选择或配置文件加载资产
    // 这里我们假设已经加载了一个名为 "/Game/Audio/TestDialogue" 的声波资产
    static ConstructorHelpers::FObjectFinder<USoundWave> SoundWaveFinder(TEXT("/Game/Audio/TestDialogue"));
    if (SoundWaveFinder.Succeeded())
    {
        InOutContext.AssetsToProcess.Add(SoundWaveFinder.Object);
    }

    // 配置批量步骤：从音频创建性能，然后处理，最后导出关卡序列
    InOutContext.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                                 | EBatchOperationStepsFlags::ProcessPerformance
                                 | EBatchOperationStepsFlags::ExportLevelSequence;

    // 处理设置
    InOutContext.bGenerateBlinks = true;
    InOutContext.bMixAudioChannels = false; // 不混合，使用特定通道
    InOutContext.AudioChannelIndex = 0;
    InOutContext.bEnableHeadMovement = true;

    // 导出设置（针对关卡序列）
    InOutContext.bExportAudioTrack = true;
    InOutContext.bExportCamera = true;

    // 命名规则（简化示例）
    InOutContext.PerformanceNameRule.NewName = TEXT("Perf_%1%");
    InOutContext.PerformanceNameRule.bUsePrefix = true;
    InOutContext.PerformanceNameRule.NewNamePrefix = TEXT("BatchPerf_");

    InOutContext.bOverrideAssets = false; // 不覆盖现有资产，生成新名称
}
```
**注意**: 此示例使用了硬编码路径，仅用于演示。在实际使用中，`AssetsToProcess` 通常来自编辑器中的资产选择或一个队列系统。

## 模块依赖
从提供的模块依赖列表分析，`MetaHumanBatchProcessor` 模块直接依赖于 `UnrealEd`，表明其核心功能（批量处理、导出向导）是编辑器专用的功能。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器子系统、资产操作、UI（Slate）、动画重命名规则等编辑器核心功能。 |
| `MetaHumanCoreTechLib` (来自 `MetaHumanConfig`) | 提供 MetaHuman 底层的技术库支持，被配置模块依赖。 |
| `MetaHumanSDKEditor` (来自 `MetaHumanIdentity`) | 提供与 MetaHuman SDK 交互的编辑器工具。 |
| `ControlRigDeveloper` (来自 `MetaHumanIdentity`) | 用于开发 Control Rig 蓝图，可能与面部控制绑定相关。 |
| `SkeletalMeshUtilitiesCommon` (来自 `MetaHumanIdentity`) | 提供骨骼网格体处理的通用工具。 |

**总结**：要使用 `MetaHumanBatchProcessor` 模块的功能，你的编辑器模块需要依赖 `UnrealEd`。完整的插件工作流会涉及众多相互依赖的模块，建议直接依赖整个 `MetaHumanAnimator` 插件。

## 维护状态
由于插件创建时间未知，无法计算准确年龄。但从模块数量和功能完整性来看，这是一个大型的、功能性的插件。

### 近期更新
基于提供的 git 历史（最近5条提交）：

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价
- **活跃维护**：最近的提交（2026年5月）密集且包含功能调整和 Bug 修复，表明该插件处于活跃开发维护状态。
- **功能完整**：作为一个包含28个模块的官方工具集，其功能覆盖了完整的动画生产流程。
- **潜在复杂性**：模块众多，内部依赖关系复杂，对于初学者或需要深度定制的开发者可能有较高的学习曲线。
- **实验性标记**：`.uplugin` 显示 `IsExperimentalVersion: false`，但整个 MetaHuman 项目及其 Animator 工具链在行业应用中仍可视为“前沿”或“实验性”技术，使用时需关注未来版本可能的 API 变化。
- **推荐使用**：**推荐**使用。对于从事 MetaHuman 项目开发并需要专业面部动画流程的团队来说，这是不可或缺的官方工具集。保持对更新日志的关注，以获取新功能和稳定性改进。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （根据 .uplugin，DocsURL 为空）
- [测试用例]() （提供的模块列表中包含 `MetaHumanControlsConversionTest`，路径可能为 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/`，但具体测试文件位置需确认）