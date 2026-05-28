# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画资产、蓝图、配置文件） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-02-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套完整的工具链，核心目的是将音频驱动（Speech-to-Face）和视频/单目摄像头驱动（Performance Capture）的动画数据，高效地转化为可在 MetaHuman 角色上播放的高质量面部动画。它解决的是从原始媒体（音频、视频）到最终可用游戏/影视资产的自动化流水线问题，特别是针对 MetaHuman 角色的复杂面部绑定和动画系统。

其价值在于：
1.  **音频驱动动画**：通过 AI 模型将音频文件转换为对应的面部 BlendShape 动画数据。
2.  **批量处理**：提供批量处理工具，允许一次性处理大量音频文件，显著提升资产生产效率。
3.  **端到端工具**：提供从数据采集（通过 `MetaHumanCaptureProtocolStack`）、处理、求解到最终在 Sequencer 中预览和导出的完整工作流。

## 使用场景

-   你正在开发一个拥有大量对话的 RPG 或叙事游戏 → 使用 **MetaHuman Batch Processor** 批量将数千条语音对话转换为面部动画序列。
-   你是一名虚拟主播技术开发者，需要为你的虚拟形象生成实时口型同步动画 → 利用其核心的 **Speech-to-Face** 算法。
-   你有一段演员的表演视频，希望为其 MetaHuman 角色制作动画 → 使用 **Performance Capture** 相关模块进行面部追踪和动画求解。
-   你正在构建一个影视预览管线，需要将分镜音频快速转化为带表情的角色动画预览。

## 蓝图用法

此插件的核心是后端处理管线和数据资产，大部分关键函数（如批量处理的 `RunProcess`）是 C++ 的 `UObject` 方法，而非直接暴露给蓝图的节点。但插件定义了大量 `BlueprintType` 的设置结构体和枚举，用于在蓝图中配置处理参数。

### 核心设置类型

| 类型/节点 | 说明 | 所在类/结构体 |
|---|---|---|
| `FMetaHumanSpeechProcessingSettings` | 音频处理核心设置，如是否生成眨眼、音频通道、动画掩码等。 | `FMetaHumanSpeechProcessingSettings` |
| `FExportAnimSequenceSettings` | 导出动画序列的设置，如目标骨架、曲线插值、是否覆盖资产。 | `FExportAnimSequenceSettings` |
| `FExportLevelSequenceSettings` | 导出关卡序列的设置，如目标MetaHuman蓝图、是否导出音轨和摄像机。 | `FExportLevelSequenceSettings` |
| `EBatchOperationStepsFlags` | 批量操作步骤的标志枚举，定义了从“创建性能资产”到“导出关卡序列”的完整流程。 | `EBatchOperationStepsFlags` |

### 使用示例（蓝图描述）

你无法在蓝图中直接调用批量处理函数。通常的做法是：
1.  在蓝图中定义 `FMetaHumanSpeechProcessingSettings` 和 `FExportAnimSequenceSettings` 类型的变量。
2.  通过蓝图节点（如 `Make Literal Struct` 或直接设置成员）来配置这些变量。
3.  这些变量可以被用作某些自定义蓝图节点（如果插件提供了）或被用来初始化一个 `UMetaHumanSpeechToAnimSequenceProcessingSettings` 对象，该对象可以被传递给 C++ 侧的处理逻辑。

## C++ 用法

### 头文件引入

```cpp
// 引入批量处理操作的核心定义
#include "MetaHumanBatchOperation.h"
// 引入设置结构体
#include "MetaHumanSpeechProcessingSettings.h"
```

### 基本用法（来自批量处理逻辑）

以下代码展示了如何构建一个上下文并执行批量音频转动画操作。

```cpp
// 来源于 MetaHumanBatchProcessor 模块内部的典型用法逻辑
void ExampleBatchProcess()
{
    // 1. 准备源资产（例如，从内容浏览器获取的 USoundWave 数组）
    TArray<TWeakObjectPtr<UObject>> SoundWaves; // ... 填充你的音频资产

    // 2. 构建批量处理上下文
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = SoundWaves;
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance | 
                              EBatchOperationStepsFlags::ProcessPerformance |
                              EBatchOperationStepsFlags::ExportAnimSequence;
    // 配置处理参数
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;
    Context.OutputControls = EAudioDrivenAnimationOutputControls::FullFace;
    // 配置导出参数
    Context.bOverwriteAssets = false; // 生成唯一资产名
    Context.TargetSkeletonOrSkeletalMesh = /* 设置你的目标骨架/网格体 TSoftObjectPtr */;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;

    // 3. 创建批量操作对象并执行
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
}
```

### 进阶用法

更复杂的用法可能涉及单独使用管线中的其他模块，例如 `MetaHumanFaceAnimationSolver` 或 `MetaHumanPipeline`，但 `MetaHumanBatchProcessor` 模块本身已经封装了从音频到动画序列导出的完整逻辑，是最高层级的批处理接口。

## Demo 示例

一个展示如何配置并触发批量处理的最小 C++ 示例。

```cpp
// MetaHumanBatchDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanBatchDemo.generated.h"

UCLASS()
class AMetaHumanBatchDemo : public AActor
{
    GENERATED_BODY()
public:
    // 在编辑器中选中此Actor，然后在细节面板中点击“运行批量处理”按钮
    UFUNCTION(CallInEditor, Category = "Demo")
    void RunBatchProcessing();
};
```

```cpp
// MetaHumanBatchDemo.cpp
#include "MetaHumanBatchDemo.h"
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"

void AMetaHumanBatchDemo::RunBatchProcessing()
{
    // 假设你已经在某个地方收集了音频资产指针
    TArray<TWeakObjectPtr<UObject>> MyAudioAssets;
    // ... 例如从资产注册表中查找所有 SoundWave

    if (MyAudioAssets.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No audio assets found to process."));
        return;
    }

    // 构建上下文
    FMetaHumanBatchOperationContext BatchContext;
    BatchContext.AssetsToProcess = MyAudioAssets;
    BatchContext.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance | 
                                  EBatchOperationStepsFlags::ProcessPerformance;
    // 关闭导出，仅生成性能资产（Performance Asset）用于预览
    BatchContext.bGenerateBlinks = true;
    BatchContext.bOverwriteAssets = true; // 覆盖已有的临时资产

    // 创建并运行批处理操作
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(BatchContext);

    UE_LOG(LogTemp, Log, TEXT("Batch processing initiated for %d audio assets."), MyAudioAssets.Num());
}
```

## 模块依赖

使用 `MetaHumanBatchProcessor` 模块，你的项目需要依赖以下插件或模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 系统的核心类型、工具和蓝图接口。 |
| `MetaHumanPerformance` | 提供 `UMetaHumanPerformance` 资产类型，用于存储音频驱动的动画数据。 |
| `MetaHumanPipeline` | 处理管线框架，可能用于编排更复杂的数据处理步骤。 |
| `MetaHumanSpeech2Face` | 包含从音频生成面部动画的核心 AI 模型和算法。 |
| `MetaHumanSequencer` | 用于在 Sequencer 中预览和导出最终动画序列。 |
| `MetaHumanSDKEditor` | 为 MetaHuman 提供编辑器扩展和资产处理工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

**活跃维护**。
`MetaHuman Animator` 是 Epic Games 的核心产品之一，用于支撑其 MetaHuman 技术生态。从近期的提交记录看，开发团队在持续进行功能增强（如身体追踪集成、网格体导出支持）、Bug 修复（渲染瑕疵、Sequencer 问题）和优化。创建时间约为 4 年，属于较新的、仍在快速迭代的插件。虽然其 `Installed` 字段为 `false`，但这通常意味着它需要从 Epic Games Launcher 或源码编译获取，而非免费内置。**强烈推荐**用于任何涉及 MetaHuman 角色动画生产的专业项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-for-unreal-engine/)（MetaHuman Animator官方文档链接，需根据最新版本核实）
- 测试用例：未在给定信息中明确提供路径。