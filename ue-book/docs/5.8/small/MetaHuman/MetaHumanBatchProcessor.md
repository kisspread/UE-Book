# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、工具、流程） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
`MetaHuman Animator` 是 Epic Games 为 MetaHuman 角色打造的官方动画工具集。它旨在简化 MetaHuman 角色的动画制作流程，特别是从现实世界数据（如音频、视频、动作捕捉）驱动面部和身体动画的流程。该插件集成了多个子模块，覆盖了从原始数据捕获、处理、到动画求解和最终导出的完整生产流水线。其核心价值在于将复杂的面部动画制作过程标准化和自动化，让开发者能专注于创意而非技术实现。

## 使用场景
- **语音驱动动画**：为游戏过场动画、虚拟主播或任何基于对话的内容，批量将大量音频文件（`SoundWave`）转换为逼真的 MetaHuman 面部动画。
- **性能/动画导出**：将处理好的 MetaHuman Performance 导出为标准的 `AnimationSequence` 或包含演员、摄像机、音频的 `LevelSequence`，方便集成到游戏或影片制作管线中。
- **批处理工作流**：当需要处理数十甚至上百个音频片段时，使用批处理功能自动化整个流程，避免手动重复操作，显著提升生产效率。
- **视频捕获驱动**：配合其他捕获模块，使用视频或专业设备捕获演员表演，并将其映射到 MetaHuman 模型上。

## 蓝图用法
本模块（`MetaHumanBatchProcessor`）提供的蓝图 API 主要集中在 **配置结构体** 和 **批处理操作设置**，核心处理逻辑通常由编辑器工具或自定义 C++ 逻辑调用。

### 核心配置结构体

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FMetaHumanSpeechProcessingSettings` | 配置音频驱动动画的核心参数，如是否生成眨眼、混合音频通道、头部运动等。 | `FMetaHumanSpeechProcessingSettings` |
| `FExportAnimSequenceSettings` | 配置导出 `AnimationSequence` 的参数，如目标骨架、曲线插值、是否删除冗余关键帧。 | `FExportAnimSequenceSettings` |
| `FExportLevelSequenceSettings` | 配置导出 `LevelSequence` 的参数，如目标MetaHuman蓝图、是否包含音频/摄像机轨道。 | `FExportLevelSequenceSettings` |

### 使用示例（蓝图描述）
1.  **创建设置对象**：在蓝图中创建一个 `UMetaHumanSpeechToAnimSequenceProcessingSettings` 或 `UMetaHumanSpeechToLevelSequenceSettings` 类型的变量。这些 UObject 封装了上述结构体，并暴露为蓝图可编辑属性。
2.  **配置参数**：在该变量的详细面板中，展开 `Processing Settings` 和 `Export Settings` 分类，根据需求调整各项参数（如勾选 `bGenerateBlinks`，选择目标骨架等）。
3.  **传递给批处理器**：虽然 `UMetaHumanBatchOperation::RunProcess` 不是蓝图可调用函数，但你可以创建一个 `FMetaHumanBatchOperationContext` 结构体，将你的设置填入其中，然后将其传递给使用此插件的自定义蓝图函数库或编辑器工具按钮。

## C++ 用法
核心的批处理逻辑通过 `UMetaHumanBatchOperation` 类执行，该类封装了从音频到动画的完整流程。

### 头文件引入
```cpp
#include "MetaHumanBatchOperation.h"
```

### 基本用法
以下示例展示了如何设置一个批处理上下文并执行从音频到动画序列的流程。
```cpp
// 假设我们已经有一些 USoundWave 资产
TArray<UObject*> AudioAssets = { SoundWave1, SoundWave2 };

// 1. 构建批处理上下文
FMetaHumanBatchOperationContext Context;
Context.AssetsToProcess = AudioAssets;

// 设置要执行的步骤：创建Performance、处理、导出动画序列
Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance | 
                          EBatchOperationStepsFlags::ProcessPerformance | 
                          EBatchOperationStepsFlags::ExportAnimSequence;

// 配置处理参数
Context.bGenerateBlinks = true;
Context.bMixAudioChannels = true;
Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;

// 配置导出参数
Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
Context.bRemoveRedundantKeys = true;
Context.bOverrideAssets = false; // 不覆盖已有资产，而是创建新资产

// 设置资产命名规则
Context.PerformanceNameRule.Prefix = TEXT("PERF_");
Context.ExportedAssetNameRule.Prefix = TEXT("ANIM_");

// 2. 检查上下文是否有效
if (Context.IsValid())
{
    // 3. 创建并执行批处理操作
    UMetaHumanBatchOperation* BatchOperation = NewObject<UMetaHumanBatchOperation>();
    BatchOperation->RunProcess(Context);
}
```

### 进阶用法
对于更精细的控制，可以利用 `FMetaHumanBatchOperationContext` 中更具体的参数，例如：
- **音频通道控制**：通过 `bMixAudioChannels = false` 并设置 `AudioChannelIndex` 来处理特定通道的音频。
- **输出面具**：通过 `AudioDrivenAnimationOutputControls` 枚举（如 `UpperFace`, `LowerFace`）限制动画驱动的面部区域。
- **LevelSequence 导出**：将步骤标志切换为 `ExportLevelSequence`，并配置 `TargetMetaHuman`、`bExportAudioTrack` 和 `bExportCamera` 来生成完整的关卡序列。

## Demo 示例
一个演示如何使用 `FMetaHumanBatchOperationContext` 和 `UMetaHumanBatchOperation` 的最小示例。

**MyMetaHumanBatchProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MetaHumanBatchOperation.h"
#include "MyMetaHumanBatchProcessor.generated.h"

UCLASS()
class UMyMetaHumanBatchProcessor : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** 批量将音频资产转换为动画序列 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Batch")
    static void ConvertAudioToAnimationSequence(const TArray<UObject*>& InAudioAssets, bool bOverrideExisting = false);
};
```

**MyMetaHumanBatchProcessor.cpp**
```cpp
#include "MyMetaHumanBatchProcessor.h"
#include "Engine/StreamableManager.h"
#include "MetaHumanPerformance.h"
#include "Sound/SoundWave.h"

void UMyMetaHumanBatchProcessor::ConvertAudioToAnimationSequence(const TArray<UObject*>& InAudioAssets, bool bOverrideExisting)
{
    // 过滤出有效的 SoundWave 资产
    TArray<TWeakObjectPtr<UObject>> ValidAssets;
    for (UObject* Asset : InAudioAssets)
    {
        if (Cast<USoundWave>(Asset))
        {
            ValidAssets.Add(Asset);
        }
    }

    if (ValidAssets.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No valid SoundWave assets provided for batch processing."));
        return;
    }

    // 构建上下文
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = ValidAssets;
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance | 
                              EBatchOperationStepsFlags::ProcessPerformance | 
                              EBatchOperationStepsFlags::ExportAnimSequence;
    Context.bGenerateBlinks = true;
    Context.bOverrideAssets = bOverrideExisting;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
    Context.bRemoveRedundantKeys = true;
    Context.PerformanceNameRule.Prefix = TEXT("BatchPerf_");
    Context.ExportedAssetNameRule.Prefix = TEXT("BatchAnim_");

    // 创建并执行操作
    UMetaHumanBatchOperation* Operation = NewObject<UMetaHumanBatchOperation>();
    Operation->RunProcess(Context);
    
    // 注意：实际项目中，应在此处添加对 Operation 的强引用以防止被垃圾回收。
}
```

## 模块依赖
该模块（`MetaHumanBatchProcessor`）依赖多个插件内部的 MetaHuman 模块，以及一些引擎模块。对于使用者（即希望调用其功能的外部模块），需要关注以下依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术的低层库，用于音频驱动动画等核心算法。 |
| `MetaHumanCaptureDataEditor` | 提供捕获数据（如音频）的编辑器工具和资产类型。 |
| `MetaHumanImageViewerEditor` | 提供图像查看器编辑器支持。 |

**注**：使用该模块的功能通常需要在你的 `Build.cs` 文件中添加对这些模块的依赖。

## 维护状态

### 近期更新
从提供的 git 历史记录看，该插件处于**活跃维护**状态，近期更新集中于功能改进和 bug 修复。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 启用身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已有的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题 |

### 维护评价
`MetaHuman Animator` 是 Epic Games 的**旗舰级** MetaHuman 工具，从提交记录看，**维护非常活跃**。近期的更新都是实质性的功能增强（如为已有网格导出动画）和关键问题修复（渲染瑕疵、Sequencer 缓存）。作为官方工具套件，其稳定性和与引擎新版本的兼容性有保障。**强烈推荐**给所有使用 MetaHuman 角色并需要高质量面部动画的项目。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （.uplugin 中 DocsURL 为空，请参考 Epic 官网 MetaHuman 部分文档）