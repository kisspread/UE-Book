# MetaHuman Batch Processor

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 批量处理器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器菜单扩展、处理对话框） |
| 模块 | `MetaHumanBatchProcessor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHumanBatchProcessor 是 MetaHuman Animator 插件中的**批量处理模块**，专门解决"大量音频文件转动画"的生产力问题。

在实际的 MetaHuman 动画制作流程中，美术或动画师通常需要将数十甚至上百条配音音频（SoundWave 资产）转化为 MetaHuman 面部动画。如果每条音频都手动执行"创建 Performance → Speech2Face 处理 → 导出动画序列"，效率极低。该模块将这一流程封装为**一键批量操作**，支持：

- **SoundWave → MetaHuman Performance**：自动从音频资产创建表演资产
- **Performance 处理**：基于语音驱动的面部动画求解（Speech2Face），支持眨眼生成、音频通道混合、头部运动等
- **导出动画序列**：批量导出 AnimSequence 到指定骨骼/网格体
- **导出关卡序列**：批量导出 LevelSequence，包含音频轨道和摄像机轨道

核心价值：**将单条音频的 3 步手动流程，扩展为支持任意数量资产的自动化管线**。

## 使用场景

- 你有一个配音包，包含 50 条 SoundWave 资产，需要全部转化为 MetaHuman 面部动画 → 使用批量处理
- 你在做游戏过场动画，需要将对话音频批量绑定到 MetaHuman 角色并导出 LevelSequence → 使用批量导出
- 你需要为同一个角色的大量对白统一配置 Speech2Face 参数（如是否生成眨眼、头部运动等） → 通过批量设置面板统一配置
- 你想要覆盖已有的动画资产或生成新资产（带编号后缀） → 通过命名规则控制

## 蓝图用法

### 核心数据结构

该模块提供的 `BlueprintType` 结构体和类均可在蓝图中使用，主要用于配置批量处理参数。

#### 处理设置

| 结构体/类 | 说明 |
|---|---|
| `FMetaHumanSpeechProcessingSettings` | 语音处理参数（眨眼、音频通道、处理遮罩、求解覆盖、头部运动） |
| `UMetaHumanSpeechToPerformance` | 从 SoundWave 创建 Performance 的完整配置对象 |
| `UMetaHumanSpeechToAnimSequenceProcessingSettings` | 语音→AnimSequence 的完整处理+导出配置 |
| `UMetaHumanSpeechToLevelSequenceSettings` | 语音→LevelSequence 的完整处理+导出配置 |

#### 导出设置

| 结构体/类 | 说明 |
|---|---|
| `FExportAnimSequenceSettings` | AnimSequence 导出参数（目标骨骼、曲线插值、冗余关键帧剔除） |
| `FExportLevelSequenceSettings` | LevelSequence 导出参数（音频轨道、摄像机、MetaHuman 蓝图类） |
| `UMetaHumanExportAnimSequenceSettings` | AnimSequence 导出设置的 UObject 包装 |
| `UMetaHumanExportLevelSequenceSettings` | LevelSequence 导出设置的 UObject 包装 |

### 关键属性

#### FMetaHumanSpeechProcessingSettings

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bGenerateBlinks` | `bool` | `true` | 是否自动生成眨眼动画 |
| `bMixAudioChannels` | `bool` | `true` | 是否将多通道音频混合为单通道 |
| `AudioChannelIndex` | `int32` | `0` | 多通道音频时使用的通道索引（0-64） |
| `OutputControls` | `EAudioDrivenAnimationOutputControls` | `FullFace` | 处理全脸还是特定控件子集 |
| `SolveOverrides` | `FAudioDrivenAnimationSolveOverrides` | — | 求解器覆盖参数 |
| `bEnableHeadMovement` | `bool` | `true` | 是否启用头部运动 |

#### FExportAnimSequenceSettings

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOverwriteAssets` | `bool` | `false` | 是否覆盖已有资产 |
| `TargetSkeletonOrSkeletalMesh` | `TSoftObjectPtr<UObject>` | — | 导出所用的目标骨架或骨骼网格体 |
| `CurveInterpolation` | `ERichCurveInterpMode` | `Linear` | 关键帧之间的插值模式 |
| `bRemoveRedundantKeys` | `bool` | `true` | 是否移除冗余关键帧 |

#### FExportLevelSequenceSettings

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOverwriteAssets` | `bool` | `false` | 是否覆盖已有资产 |
| `CurveInterpolation` | `ERichCurveInterpMode` | `Linear` | 关键帧之间的插值模式 |
| `bRemoveRedundantKeys` | `bool` | `true` | 是否移除冗余关键帧 |
| `TargetMetaHumanClass` | `TSoftObjectPtr<UBlueprint>` | — | 导出关卡序列中生成的目标 MetaHuman 蓝图类 |
| `bExportAudioTrack` | `bool` | `true` | 是否在关卡序列中导出音频轨道 |
| `bExportCamera` | `bool` | `true` | 是否在关卡序列中导出摄像机轨道 |

### 使用示例（蓝图描述）

1. **右键菜单快速批量处理**：在内容浏览器中选中多个 SoundWave 资产 → 右键 → MetaHuman 菜单中选择批量处理选项 → 弹出配置对话框 → 设置处理参数和导出路径 → 点击处理
2. **从蓝图创建批量配置对象**：使用 `Create Object` 节点创建 `UMetaHumanSpeechToAnimSequenceProcessingSettings` → 设置其 `ProcessingSettings` 和 `ExportSettings` 属性 → 将配置传递给批量处理逻辑

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"
```

### 基本用法：构建批量处理上下文并执行

```cpp
// 构建批量处理上下文
FMetaHumanBatchOperationContext Context;

// 设置待处理的音频资产（可以是多个 SoundWave）
Context.AssetsToProcess.Add(MySoundWave1);
Context.AssetsToProcess.Add(MySoundWave2);

// 指定要执行的步骤：创建 Performance → 处理 → 导出 AnimSequence
Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                        | EBatchOperationStepsFlags::ProcessPerformance
                        | EBatchOperationStepsFlags::ExportAnimSequence;

// 配置处理参数
Context.bGenerateBlinks = true;
Context.bMixAudioChannels = true;
Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;
Context.bEnableHeadMovement = true;

// 配置导出参数
Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
Context.bRemoveRedundantKeys = true;
Context.bOverwriteAssets = false;

// 设置目标骨架
Context.TargetSkeletonOrSkeletalMesh = MySkeletonSoftPtr;

// 设置命名规则
Context.PerformanceNameRule.Prefix = TEXT("PERF_");
Context.PerformanceNameRule.Suffix = TEXT("");
Context.ExportedAssetNameRule.Prefix = TEXT("ANIM_");

// 验证上下文有效性
if (Context.IsValid())
{
    // 创建批量操作对象并执行
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
}
```

### 进阶用法：仅导出 LevelSequence

```cpp
// 如果已经有处理好的 Performance，可以只执行导出步骤
FMetaHumanBatchOperationContext Context;
Context.AssetsToProcess.Add(MySoundWave);
Context.BatchStepsFlags = EBatchOperationStepsFlags::ExportLevelSequence;

// 配置 LevelSequence 导出参数
Context.bExportAudioTrack = true;
Context.bExportCamera = true;
Context.TargetMetaHuman = MyMetaHumanBlueprint;
Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Cubic;

UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
BatchOp->RunProcess(Context);
```

### 进阶用法：使用标志位组合灵活控制流程

```cpp
// EBatchOperationStepsFlags 支持位运算组合
using Flags = EBatchOperationStepsFlags;

// 只创建 Performance，不处理也不导出
Flags Step1 = Flags::SoundWaveToPerformance;

// 创建并处理，但不导出
Flags Step2 = Flags::SoundWaveToPerformance | Flags::ProcessPerformance;

// 全流程
Flags Full = Flags::SoundWaveToPerformance
           | Flags::ProcessPerformance
           | Flags::ExportAnimSequence
           | Flags::ExportLevelSequence;

// 也可以直接用位或操作
Context.BatchStepsFlags = static_cast<Flags>(
    static_cast<uint8>(Flags::SoundWaveToPerformance) |
    static_cast<uint8>(Flags::ProcessPerformance)
);
```

## Demo 示例

```cpp
// MetaHumanBatchProcessorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"

class FMetaHumanBatchProcessorDemo
{
public:
    /**
     * 演示如何批量处理多个 SoundWave 资产并导出 AnimSequence
     * @param InSoundWaves 待处理的音频资产列表
     * @param InTargetSkeleton 目标骨架
     */
    static void ProcessMultipleSoundWaves(
        const TArray<TWeakObjectPtr<UObject>>& InSoundWaves,
        TSoftObjectPtr<UObject> InTargetSkeleton
    );

    /**
     * 演示如何只导出 LevelSequence（假设 Performance 已处理完成）
     * @param InSoundWaves 已处理的音频资产
     * @param InMetaHumanBlueprint 目标 MetaHuman 蓝图
     */
    static void ExportLevelSequencesOnly(
        const TArray<TWeakObjectPtr<UObject>>& InSoundWaves,
        TSoftObjectPtr<UBlueprint> InMetaHumanBlueprint
    );
};
```

```cpp
// MetaHumanBatchProcessorDemo.cpp
#include "MetaHumanBatchProcessorDemo.h"

void FMetaHumanBatchProcessorDemo::ProcessMultipleSoundWaves(
    const TArray<TWeakObjectPtr<UObject>>& InSoundWaves,
    TSoftObjectPtr<UObject> InTargetSkeleton)
{
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = InSoundWaves;

    // 完整流程：创建 Performance → 处理 → 导出 AnimSequence
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                            | EBatchOperationStepsFlags::ProcessPerformance
                            | EBatchOperationStepsFlags::ExportAnimSequence;

    // 语音处理设置
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;
    Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;
    Context.bEnableHeadMovement = true;

    // 导出设置
    Context.TargetSkeletonOrSkeletalMesh = InTargetSkeleton;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
    Context.bRemoveRedundantKeys = true;
    Context.bOverwriteAssets = false;

    // 命名规则
    Context.PerformanceNameRule.Prefix = TEXT("MH_Perf_");
    Context.ExportedAssetNameRule.Prefix = TEXT("MH_Anim_");

    if (Context.IsValid())
    {
        UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
        BatchOp->RunProcess(Context);
    }
}

void FMetaHumanBatchProcessorDemo::ExportLevelSequencesOnly(
    const TArray<TWeakObjectPtr<UObject>>& InSoundWaves,
    TSoftObjectPtr<UBlueprint> InMetaHumanBlueprint)
{
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = InSoundWaves;

    // 仅导出 LevelSequence
    Context.BatchStepsFlags = EBatchOperationStepsFlags::ExportLevelSequence;

    // LevelSequence 导出设置
    Context.TargetMetaHuman = InMetaHumanBlueprint;
    Context.bExportAudioTrack = true;
    Context.bExportCamera = true;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Cubic;
    Context.bRemoveRedundantKeys = true;

    if (Context.IsValid())
    {
        UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
        BatchOp->RunProcess(Context);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanPerformance` | MetaHuman 表演资产核心逻辑，批量处理器从 SoundWave 创建 Performance |
| `MetaHumanSpeech2Face` | 语音驱动面部动画求解器，用于处理 Performance 中的音频数据 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器，转换语音特征为面部控件曲线 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器支持 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器支持 |
| `MetaHumanSequencer` | Sequencer 集成，支持 LevelSequence 的导出 |
| `MetaHumanPipeline` | 处理管线框架 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：以上依赖关系基于模块命名推断。该模块的 `.build.cs` 未在提供的信息中完整列出依赖项，实际使用时请检查 `MetaHumanBatchProcessor.build.cs` 中的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时禁用 LevelSequence 导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已存在的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关问题 |

### 维护评价

- **活跃维护**：最近 5 天内有 5 次功能性更新和 bug 修复，更新频率非常高
- MetaHuman Animator 是 Epic 的核心角色技术管线，属于长期重点维护项目
- 近期更新涉及身体追踪集成、渲染修复、导出功能增强等，表明该模块正在持续演进
- 作为 Runtime 模块标记但实际提供编辑器功能（菜单扩展、对话框），可能需要配合对应的 Editor 模块使用
- **强烈推荐使用**：这是 Epic 官方的 MetaHuman 批量处理方案，与 MetaHuman 生态深度集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanBatchProcessor)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman/)（MetaHuman 总体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)