# docs/xlarge/MetaHumanAnimator/index.md

# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 配置资产、处理预设） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 面部动画制作工具链，提供从面部捕捉数据到最终动画资产的完整生产管线。它解决的核心问题是：**如何将真实世界的面部表演高效地转化为 MetaHuman 角色的面部动画**。

该插件并非简单的单一功能模块，而是一个涵盖多个处理阶段的完整管线：

1. **数据采集**（Capture）：从 iPhone TrueDepth 摄像头、视频素材或专业动捕设备导入面部表演数据
2. **面部追踪**（Contour Tracking）：在视频帧中检测并追踪面部轮廓关键点
3. **面部拟合**（Face Fitting）：将追踪数据拟合到 MetaHuman 面部网格模型
4. **动画求解**（Animation Solving）：从拟合结果生成面部骨骼动画控制数据
5. **音频驱动动画**（Speech-to-Face / Audio Driven Animation）：从音频自动生成面部口型和表情动画
6. **批量处理**（Batch Processing）：对大量音频资产进行自动化管线处理
7. **动画导出**（Export）：将结果导出为 Animation Sequence 或 Level Sequence

## 使用场景

- 你有一段演员面部表演的视频素材 → 用 **MetaHumanCaptureSource** + **MetaHumanFaceContourTracker** + **MetaHumanFaceFittingSolver** 追踪并拟合面部
- 你只有音频文件，需要生成口型同步动画 → 用 **MetaHumanSpeech2Face** 进行音频驱动动画
- 你有大量音频文件需要批量处理为动画 → 用 **MetaHumanBatchProcessor** 进行批量管线处理
- 你需要将处理结果集成到 Sequencer 时间线中 → 用 **MetaHumanSequencer** 模块
- 你需要管理 MetaHuman 角色的身份资产（面部模板、骨骼映射等）→ 用 **MetaHumanIdentity** 模块
- 你需要从 iPhone LiDAR 深度数据辅助面部重建 → 用 **MetaHumanDepthGenerator** 模块

## 模块架构

该插件包含 28 个模块，按功能可分为以下几组：

### 核心基础层
| 模块 | 说明 |
|---|---|
| `MetaHumanCore` | 核心数据类型和工具函数 |
| `MetaHumanCoreEditor` | 编辑器扩展和资产操作 |
| `MetaHumanConfig` | 配置管理（依赖 MetaHumanCoreTechLib） |
| `MetaHumanConfigEditor` | 配置编辑器 UI |
| `MetaHumanPlatform` | 平台抽象层 |
| `MetaHumanPipeline` | 通用处理管线框架 |

### 面部捕捉与追踪层
| 模块 | 说明 |
|---|---|
| `MeshTrackerInterface` | 网格追踪器接口抽象 |
| `MetaHumanCaptureProtocolStack` | 捕捉协议栈（网络通信） |
| `MetaHumanCaptureSource` | 捕捉数据源管理 |
| `MetaHumanCaptureUtils` | 捕捉工具函数 |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器 |
| `MetaHumanFootageIngest` | 视频素材导入处理 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceContourTrackerEditor` | 轮廓追踪编辑器 UI |
| `MetaHumanDepthGenerator` | 深度图生成（LiDAR 辅助） |

### 面部求解层
| 模块 | 说明 |
|---|---|
| `MetaHumanFaceFittingSolver` | 面部网格拟合求解器 |
| `MetaHumanFaceFittingSolverEditor` | 拟合求解器编辑器 UI |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanFaceAnimationSolverEditor` | 动画求解器编辑器 UI |

### 动画与导出层
| 模块 | 说明 |
|---|---|
| `MetaHumanIdentity` | MetaHuman 身份资产管理 |
| `MetaHumanIdentityEditor` | 身份资产编辑器 |
| `MetaHumanPerformance` | 表演数据资产（Performance Asset） |
| `MetaHumanSpeech2Face` | 音频驱动面部动画 |
| `MetaHumanBatchProcessor` | 批量处理管线 |
| `MetaHumanSequencer` | Sequencer 集成 |
| `MetaHumanToolkit` | 综合工具集 |

### UI 与测试
| 模块 | 说明 |
|---|---|
| `MetaHumanImageViewerEditor` | 图像查看器编辑器 |
| `MetaHumanControlsConversionTest` | 控制数据转换测试 |

## 维护状态

### 近期更新

```
- fa740193dd11 [ADA] Fix for localization issues
- 8bd156831c9b [ADA] Reduce redundant keys when exporting an anim sequence or level sequence
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files
```

### 维护评价

- **创建时间**：2024-02-02，约 1.5 年前
- **维护状态**：**活跃维护中**。近期 commit 显示持续的功能改进（减少导出冗余关键帧）和 bug 修复（本地化问题），以及代码质量优化（UE_INLINE_GENERATED_CPP_BY_NAME）
- **开发方**：Epic Games 官方维护，作为 MetaHuman 生态的核心组件
- **平台支持**：Win64、Linux
- **推荐程度**：✅ **强烈推荐**。如果你的项目使用 MetaHuman 角色并需要面部动画制作能力，这是官方推荐的工具链。作为 Epic 官方插件，长期支持有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)

---

# docs/xlarge/MetaHumanAnimator/MetaHumanBatchProcessor.md

# MetaHumanBatchProcessor 模块

> 批量处理模块，将多个音频资产自动化处理为 MetaHuman 面部动画，并导出为 Animation Sequence 或 Level Sequence。

## 模块概述

`MetaHumanBatchProcessor` 是 MetaHuman Animator 插件中的批量处理模块，解决的核心问题是：**当你有大量音频文件需要转化为面部动画时，如何避免逐个手动处理**。

该模块封装了完整的音频到动画管线：
1. **SoundWave → Performance**：从音频资产创建 MetaHuman Performance 资产
2. **Process Performance**：处理 Performance（运行音频驱动动画求解）
3. **Export Anim Sequence**：导出为 Animation Sequence
4. **Export Level Sequence**：导出为 Level Sequence（含音频轨道、摄像机等）

每个步骤都可以通过标志位独立控制，实现灵活的管线配置。

## 蓝图用法

### 核心数据类型

#### EBatchOperationStepsFlags（枚举）

控制批量操作执行哪些步骤的位标志枚举：

| 标志 | 值 | 说明 |
|---|---|---|
| `None` | 0 | 不执行任何步骤 |
| `SoundWaveToPerformance` | 1 | 从 SoundWave 创建 Performance 资产 |
| `ProcessPerformance` | 2 | 处理 Performance（运行动画求解） |
| `ExportAnimSequence` | 4 | 导出 Animation Sequence |
| `ExportLevelSequence` | 8 | 导出 Level Sequence |

支持位运算组合，例如 `SoundWaveToPerformance | ProcessPerformance | ExportAnimSequence` 表示执行完整管线直到导出动画序列。

#### FMetaHumanSpeechProcessingSettings（结构体）

音频处理设置，所有属性均为 `BlueprintReadWrite`：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bGenerateBlinks` | `bool` | `true` | 是否生成眨眼动画 |
| `bMixAudioChannels` | `bool` | `true` | 是否将多声道混音为单声道 |
| `AudioChannelIndex` | `int32` | `0` | 使用的音频通道索引（仅 bMixAudioChannels=false 时生效，范围 0-64） |
| `OutputControls` | `EAudioDrivenAnimationOutputControls` | `FullFace` | 处理遮罩：全脸或特定控制子集 |
| `SolveOverrides` | `FAudioDrivenAnimationSolveOverrides` | - | 求解器覆盖参数 |
| `bEnableHeadMovement` | `bool` | `true` | 是否启用头部运动 |

#### FExportAnimSequenceSettings（结构体）

Animation Sequence 导出设置：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOverwriteAssets` | `bool` | `false` | 是否覆盖已有资产（否则自动追加数字后缀） |
| `TargetSkeletonOrSkeletalMesh` | `TSoftObjectPtr<UObject>` | - | 目标 Skeleton 或 SkeletalMesh |
| `CurveInterpolation` | `ERichCurveInterpMode` | `Linear` | 曲线插值模式 |
| `bRemoveRedundantKeys` | `bool` | `true` | 是否移除冗余关键帧 |

#### FExportLevelSequenceSettings（结构体）

Level Sequence 导出设置：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOverwriteAssets` | `bool` | `false` | 是否覆盖已有资产 |
| `CurveInterpolation` | `ERichCurveInterpMode` | `Linear` | 曲线插值模式 |
| `bRemoveRedundantKeys` | `bool` | `true` | 是否移除冗余关键帧 |
| `TargetMetaHumanClass` | `TSoftObjectPtr<UBlueprint>` | - | 目标 MetaHuman 蓝图类 |
| `bExportAudioTrack` | `bool` | `true` | 是否导出音频轨道 |
| `bExportCamera` | `bool` | `true` | 是否导出摄像机轨道 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RunProcess` | 执行批量处理管线（SoundWave → Performance → Animation） | `UMetaHumanBatchOperation` |

> **注意**：`UMetaHumanBatchOperation::RunProcess` 在当前源码中未标记为 `BlueprintCallable`，主要通过 C++ 调用。蓝图交互主要通过设置结构体配置参数，由编辑器 UI（`SMetaHumanSpeechToAnimProcessingSettings`）驱动。

### 使用示例（蓝图描述）

由于批量处理的核心逻辑通过 C++ 调用，蓝图中的典型工作流为：

1. 在 Content Browser 中选择多个 SoundWave 资产
2. 右键菜单选择 MetaHuman 批量处理选项
3. 在弹出的 `SMetaHumanSpeechToAnimProcessingSettings` 对话框中配置：
   - 勾选"Generate Blinks"启用眨眼
   - 选择"Full Face"或特定面部区域
   - 配置音频通道选项
4. 点击"Process"开始批量处理
5. 处理完成后自动创建 Performance、Animation Sequence 或 Level Sequence 资产

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"
```

### 基本用法

创建批量处理上下文并执行完整管线：

```cpp
// 来源: MetaHumanBatchOperation.h
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"
#include "Sound/SoundWave.h"

void BatchProcessAudioFiles(const TArray<USoundWave*>& InSoundWaves)
{
    // 1. 创建批量操作对象
    UMetaHumanBatchOperation* BatchOperation = NewObject<UMetaHumanBatchOperation>();

    // 2. 配置处理上下文
    FMetaHumanBatchOperationContext Context;

    // 设置要处理的资产
    for (USoundWave* SoundWave : InSoundWaves)
    {
        Context.AssetsToProcess.Add(SoundWave);
    }

    // 配置处理步骤：创建 Performance → 处理 → 导出动画序列
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                             | EBatchOperationStepsFlags::ProcessPerformance
                             | EBatchOperationStepsFlags::ExportAnimSequence;

    // 配置处理选项
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;
    Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;

    // 配置导出选项
    Context.bEnableHeadMovement = false;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
    Context.bRemoveRedundantKeys = true;

    // 配置命名规则
    Context.bOverrideAssets = false;

    // 3. 执行批量处理
    BatchOperation->RunProcess(Context);
}
```

### 进阶用法

仅创建 Performance 资产而不立即处理（适用于需要手动检查后再处理的场景）：

```cpp
// 来源: MetaHumanBatchOperation.h, MetaHumanSpeechProcessingSettings.h

void CreatePerformancesOnly(const TArray<TWeakObjectPtr<UObject>>& InAssets)
{
    UMetaHumanBatchOperation* BatchOperation = NewObject<UMetaHumanBatchOperation>();

    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = InAssets;

    // 仅创建 Performance，不处理、不导出
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance;

    // 配置音频处理参数
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = false;      // 不混音
    Context.AudioChannelIndex = 2;          // 使用第 3 个通道

    // 使用求解器覆盖参数自定义动画风格
    // Context.AudioDrivenAnimationSolveOverrides = ...;

    BatchOperation->RunProcess(Context);
}
```

导出为 Level Sequence（含音频和摄像机轨道）：

```cpp
// 来源: MetaHumanBatchOperation.h

void ExportToLevelSequence(
    const TArray<TWeakObjectPtr<UObject>>& InAssets,
    UBlueprint* InTargetMetaHuman)
{
    UMetaHumanBatchOperation* BatchOperation = NewObject<UMetaHumanBatchOperation>();

    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = InAssets;

    // 完整管线：创建 → 处理 → 导出 Level Sequence
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                             | EBatchOperationStepsFlags::ProcessPerformance
                             | EBatchOperationStepsFlags::ExportLevelSequence;

    // Level Sequence 导出配置
    Context.TargetMetaHuman = InTargetMetaHuman;
    Context.bExportAudioTrack = true;       // 包含音频轨道
    Context.bExportCamera = true;           // 包含摄像机轨道
    Context.bEnableHeadMovement = true;     // 启用头部运动
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Cubic;

    BatchOperation->RunProcess(Context);
}
```

## Demo 示例

以下是一个完整的最小示例，展示如何在编辑器工具中使用 MetaHumanBatchProcessor 进行批量音频处理：

### MetaHumanBatchTool.h

```cpp
// MetaHumanBatchTool.h
#pragma once

#include "CoreMinimal.h"

class USoundWave;

/**
 * 简单的 MetaHuman 批量处理工具
 * 将选中的 SoundWave 资产批量转换为面部动画
 */
class FMetaHumanBatchTool
{
public:
    /** 对指定的音频资产执行完整批量处理管线 */
    static void ProcessAudioAssets(const TArray<USoundWave*>& InSoundWaves);

    /** 仅创建 Performance 资产，不进行处理 */
    static void CreatePerformancesOnly(const TArray<USoundWave*>& InSoundWaves);
};
```

### MetaHumanBatchTool.cpp

```cpp
// MetaHumanBatchTool.cpp
#include "MetaHumanBatchTool.h"
#include "MetaHumanBatchOperation.h"
#include "MetaHumanSpeechProcessingSettings.h"
#include "Sound/SoundWave.h"

void FMetaHumanBatchTool::ProcessAudioAssets(const TArray<USoundWave*>& InSoundWaves)
{
    if (InSoundWaves.Num() == 0)
    {
        return;
    }

    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();

    FMetaHumanBatchOperationContext Context;

    // 填充资产列表
    Context.AssetsToProcess.Reserve(InSoundWaves.Num());
    for (USoundWave* SoundWave : InSoundWaves)
    {
        Context.AssetsToProcess.Add(SoundWave);
    }

    // 执行完整管线：SoundWave → Performance → Process → Export Anim Sequence
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                             | EBatchOperationStepsFlags::ProcessPerformance
                             | EBatchOperationStepsFlags::ExportAnimSequence;

    // 处理设置
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;
    Context.AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;

    // 导出设置
    Context.bEnableHeadMovement = false;
    Context.CurveInterpolation = ERichCurveInterpMode::RCIM_Linear;
    Context.bRemoveRedundantKeys = true;
    Context.bOverrideAssets = false;

    BatchOp->RunProcess(Context);
}

void FMetaHumanBatchTool::CreatePerformancesOnly(const TArray<USoundWave*>& InSoundWaves)
{
    if (InSoundWaves.Num() == 0)
    {
        return;
    }

    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();

    FMetaHumanBatchOperationContext Context;

    for (USoundWave* SoundWave : InSoundWaves)
    {
        Context.AssetsToProcess.Add(SoundWave);
    }

    // 仅创建 Performance，后续可手动处理
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance;

    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;

    BatchOp->RunProcess(Context);
}
```

## 模块依赖

基于源码分析，MetaHumanBatchProcessor 模块依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanPerformance` | Performance 资产类型（`UMetaHumanPerformance`） |
| `MetaHumanSpeech2Face` | 音频驱动动画求解（`FAudioDrivenAnimationSolveOverrides`、`EAudioDrivenAnimationOutputControls`） |
| `MetaHumanPipeline` | 处理管线框架 |
| `AudioDrivenAnimationConfig` | 音频驱动动画配置类型 |

> 使用该模块时，你的 Build.cs 需要添加对 `MetaHumanBatchProcessor` 的依赖，并间接依赖上述模块。

## 内部处理流程

`UMetaHumanBatchOperation::RunProcess` 内部按以下顺序执行：

```
SoundWave 资产列表
    │
    ▼ (SoundWaveToPerformance)
创建 UMetaHumanPerformance 资产
    │  - GetTransientPerformance() 获取或创建临时 Performance
    │  - SetupPerformance() 配置音频源和处理参数
    │
    ▼ (ProcessPerformance)
处理 Performance
    │  - ProcessPerformanceAsset() 运行音频驱动动画求解
    │  - 支持进度条 (FScopedSlowTask)
    │  - 支持用户取消
    │
    ▼ (ExportAnimSequence / ExportLevelSequence)
导出动画
    │  - ExportAnimationSequence() 导出为 AnimSequence
    │  - ExportLevelSequence() 导出为 LevelSequence
    │
    ▼
OverwriteExistingAssets() / NotifyResults()
    - 处理资产覆盖逻辑
    - 通知用户处理结果
    - 如果中途取消，CleanupIfCancelled() 清理已创建资产
```

## UI 组件

`SMetaHumanSpeechToAnimProcessingSettings` 是一个 Slate 复合控件，提供批量处理的设置对话框：

- 接收一个 `UObject*` 类型的 Settings 对象（通常是 `UMetaHumanSpeechProcessingSettings`）
- 提供 `CanProcessConditional` 属性控制"Process"按钮的可用状态
- `ShowModel()` 以模态对话框形式显示，返回用户操作结果（确认/取消）
- 内部管理 `SWindow` 生命周期，支持窗口关闭和取消操作