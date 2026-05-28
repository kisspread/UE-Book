# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画资产、音频处理资产等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 角色提供的官方动画工具包。它提供了一套完整的解决方案，用于从音频驱动（Speech-to-Face）或手动关键帧为 MetaHuman 角色生成逼真的面部动画。该插件支持从音频文件（如 SoundWave 资产）批量生成动画性能（Performance），并可以将处理后的动画导出为 AnimSequence 或 LevelSequence。

其核心价值在于将复杂且耗时的面部动画制作流程自动化，允许艺术家和开发者快速为 MetaHuman 角色创建基于语音的口型同步动画，并支持批量处理，极大地提升了制作效率。

## 使用场景

- 你正在为 MetaHuman 角色制作对话场景 → 使用 Speech-to-Face 功能从配音音频自动生成面部动画。
- 你需要为大量 MetaHuman 对话生成口型同步动画 → 使用批量处理器（Batch Processor）一次性处理多个音频文件。
- 你希望将生成的动画导出为通用的动画序列资产，以便在其他项目或动画蓝图中使用 → 使用导出功能生成 AnimSequence 或 LevelSequence。
- 你需要自定义面部动画的细节，如眨眼、头部运动等 → 在处理设置中调整各项参数。

## 蓝图用法

本插件主要提供编辑器内工具和批处理功能，蓝图节点主要用于配置和触发批处理流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RunProcess` | 根据提供的上下文执行从音频到动画的完整批处理流程 | `UMetaHumanBatchOperation` |

### 使用示例（蓝图描述）

1.  **创建批处理上下文**：在蓝图中创建一个 `FMetaHumanBatchOperationContext` 结构体变量。设置 `AssetsToProcess`（要处理的音频资产数组）、`BatchStepsFlags`（要执行的步骤，如 `SoundWaveToPerformance | ProcessPerformance`）、`ProcessingSettings`（如是否生成眨眼、音频通道混合设置）以及 `ExportSettings`（如导出目标骨骼、曲线插值模式）。
2.  **配置导出路径**：使用 `SMetaHumanBatchExportPathDialog` 控件（通常通过编辑器扩展调用）或直接设置上下文中的 `PerformanceNameRule` 和 `ExportedAssetNameRule` 来定义输出资产的命名和路径规则。
3.  **执行批处理**：创建一个 `UMetaHumanBatchOperation` 对象，并调用其 `RunProcess` 函数，传入配置好的上下文。该操作会在编辑器中运行，处理所有指定的音频资产，并根据设置生成性能资产、处理动画，最终导出动画序列。
4.  **监控进度与结果**：批处理过程会显示进度条，并在完成后通过通知报告成功或失败的结果。如果处理被取消，已创建的临时资产会被自动清理。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"
```

### 基本用法

以下示例展示了如何在 C++ 中配置并运行一个基本的批量处理任务。
**来源文件**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanBatchProcessor/Private/MetaHumanBatchOperation.cpp` (推断逻辑)

```cpp
// 创建批处理操作对象
UMetaHumanBatchOperation* BatchOperation = NewObject<UMetaHumanBatchOperation>();

// 配置上下文
FMetaHumanBatchOperationContext Context;
// 1. 设置要处理的音频资产（假设已经获取了资产引用）
TArray<TWeakObjectPtr<UObject>> AudioAssets;
AudioAssets.Add(MakeWeakObjectPtr(SoundWaveAsset1));
AudioAssets.Add(MakeWeakObjectPtr(SoundWaveAsset2));
Context.AssetsToProcess = AudioAssets;

// 2. 设置要执行的步骤：创建性能 -> 处理性能 -> 导出动画序列
Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance |
                          EBatchOperationStepsFlags::ProcessPerformance |
                          EBatchOperationStepsFlags::ExportAnimSequence;

// 3. 配置处理选项
Context.bGenerateBlinks = true;
Context.bMixAudioChannels = true;
Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;

// 4. 配置导出选项
Context.bOverwriteAssets = false; // 不覆盖现有资产，自动生成新名称
Context.TargetSkeletonOrSkeletalMesh = MakeSoftObjectPtr(TargetSkeletalMesh);
Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Cubic;
Context.bRemoveRedundantKeys = true;

// 5. 配置命名规则（简化示例，通常需要用户交互设置）
Context.PerformanceNameRule.BaseName = TEXT("Perf_");
Context.ExportedAssetNameRule.BaseName = TEXT("Anim_");
Context.ExportedAssetNameRule.Suffix = TEXT("_Facial");

// 执行处理
BatchOperation->RunProcess(Context);
```

### 进阶用法

可以更精细地控制处理流程，例如仅为音频创建性能资产，但不立即处理或导出，或者只导出为关卡序列。
**组合逻辑来源**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanBatchProcessor/Public/MetaHumanBatchOperation.h`

```cpp
// 示例：仅从音频创建性能资产，不进行处理和导出
FMetaHumanBatchOperationContext ContextOnlyCreate;
ContextOnlyCreate.AssetsToProcess = AudioAssets;
ContextOnlyCreate.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance; // 仅创建
// ... 其他命名设置 ...

UMetaHumanBatchOperation::Get()->RunProcess(ContextOnlyCreate);

// 示例：从音频创建性能、处理，并导出为关卡序列
FMetaHumanBatchOperationContext ContextToLevelSequence;
ContextToLevelSequence.AssetsToProcess = AudioAssets;
ContextToLevelSequence.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance |
                                         EBatchOperationStepsFlags::ProcessPerformance |
                                         EBatchOperationStepsFlags::ExportLevelSequence;
// ... 配置 LevelSequence 导出选项 ...
ContextToLevelSequence.bExportAudioTrack = true;
ContextToLevelSequence.bExportCamera = true;
ContextToLevelSequence.TargetMetaHuman = MakeSoftObjectPtr(MetaHumanBlueprint);

UMetaHumanBatchOperation::Get()->RunProcess(ContextToLevelSequence);
```

## Demo 示例

一个最小的可编译示例，展示如何使用 MetaHumanBatchProcessor 模块从单个音频资产创建动画。

**MetaHumanBatchProcessorDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MetaHumanBatchProcessorDemo.generated.h"

UCLASS()
class UMetaHumanBatchProcessorDemo : public UEditorSubsystem
{
	GENERATED_BODY()

public:
	/** 从指定的SoundWave资产创建并处理面部动画 */
	UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
	void ProcessSingleAudioToAnimation(USoundWave* InSoundWave);
};
```

**MetaHumanBatchProcessorDemo.cpp**
```cpp
#include "MetaHumanBatchProcessorDemo.h"
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"
#include "Engine/SkeletalMesh.h"

void UMetaHumanBatchProcessorDemo::ProcessSingleAudioToAnimation(USoundWave* InSoundWave)
{
	if (!InSoundWave)
	{
		return;
	}

	// 创建批处理操作对象
	UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();

	// 配置上下文
	FMetaHumanBatchOperationContext Context;
	Context.AssetsToProcess.Add(MakeWeakObjectPtr(InSoundWave));

	// 设置处理步骤：创建性能 -> 处理 -> 导出动画序列
	Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance |
	                          EBatchOperationStepsFlags::ProcessPerformance |
	                          EBatchOperationStepsFlags::ExportAnimSequence;

	// 配置处理设置
	Context.bGenerateBlinks = true;
	Context.bMixAudioChannels = true; // 混合音频通道

	// 配置导出设置
	Context.bOverwriteAssets = true; // 如果存在同名资产则覆盖
	// 假设已经有一个目标骨骼网格体资产
	// Context.TargetSkeletonOrSkeletalMesh = YourSkeletalMeshAsset;
	Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
	Context.bRemoveRedundantKeys = true;

	// 配置命名规则（使用简单名称）
	Context.PerformanceNameRule.BaseName = InSoundWave->GetName() + TEXT("_Perf");
	Context.PerformanceNameRule.bAutoName = true; // 使用资产名生成
	Context.ExportedAssetNameRule.BaseName = InSoundWave->GetName() + TEXT("_Anim");
	Context.ExportedAssetNameRule.bAutoName = true;

	// 执行处理
	BatchOp->RunProcess(Context);
}
```

## 模块依赖

以下模块是 MetaHumanBatchProcessor 模块运行所依赖的**特有**或**不常见**模块。要使用此模块，你的模块需要在 `.Build.cs` 文件中添加这些依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanPerformance` | 处理 MetaHuman 性能资产（Performance）的核心逻辑 |
| `MetaHumanSpeech2Face` | 实现从音频（语音）驱动面部动画的核心算法 |
| `MetaHumanCaptureDataEditor` | 提供捕获数据编辑器的基础设施 |
| `MetaHumanImageViewerEditor` | 提供图像查看器编辑器组件 |
| `EditorAnimUtils` | 提供编辑器动画工具函数（如资产重命名规则） |
| `AssetTools` | 编辑器内资产创建、重命名、移动等操作 |

**注意**：此插件整体还依赖其他 MetaHuman 相关模块（如 MetaHumanCore, MetaHumanIdentity 等），但上述列表是 MetaHumanBatchProcessor 模块直接或间接依赖的关键特有模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

根据提供的 git 历史，MetaHuman Animator 插件在**2026年5月**仍有密集的更新（5次提交），这些更新主要集中在功能修复（渲染瑕疵、缓存问题）、功能增强（为现有网格导出动画）以及工作流优化（身体追踪相关）上。这表明该插件处于**活跃维护**状态，并且是 MetaHuman 工作流的核心部分，由 Epic Games 持续投入开发。

**推荐使用**：对于任何涉及 MetaHuman 角色动画制作的项目，该插件都是官方推荐的核心工具。它自动化了繁琐的面部动画流程，特别是口型同步，能显著提升生产效率。需要注意的是，它是一个功能强大且复杂的工具，需要一定的学习成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (待补充)
- [测试用例]() (测试用例路径待确认)