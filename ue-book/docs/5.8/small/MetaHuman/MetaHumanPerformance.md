# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、处理管线配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-06-07 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic 官方的 MetaHuman 动画工具链，用于将**真实世界的表演素材**转换为 MetaHuman 数字角色的面部和身体动画。它解决的核心问题是：**如何从视频片段、深度数据或音频中自动提取面部表情动画，并驱动 Control Rig 产生可用的动画序列**。

该插件支持三种数据输入模式：

1. **深度视频（Depth Footage）**：使用带深度信息的立体视频素材，结合 MetaHuman Identity 资产中的数字替身，通过面部轮廓追踪和动画求解器生成高质量动画。这是精度最高的工作流。
2. **音频（Audio）**：从音频中驱动面部动画（Speech-to-Face），支持实时和离线两种模式，可以自动生成眨眼和情绪表达。
3. **单目视频（Mono Footage）**：从单个摄像机视角的视频中提取面部和身体动画，无需深度信息，适合消费级设备拍摄的素材。

此外还支持**身体追踪（Body Tracking）**，可以从单目视频中提取身体姿态动画，并通过 IK Retargeter 将动画重定向到不同骨架的角色。

## 使用场景

- 你有一段深度摄像机拍摄的演员表演素材 → 使用 `DepthFootage` 模式配合 MetaHuman Identity 资产生成高保真面部动画
- 你只有音频文件需要驱动数字角色说话 → 使用 `Audio` 模式，支持眨眼生成和情绪检测
- 你用普通手机拍摄了一段单人表演视频 → 使用 `MonoFootage` 模式，同时追踪面部和身体
- 你需要将表演动画导出为 AnimSequence 供游戏运行时播放 → 使用 `ExportAnimationSequence` API
- 你需要将完整的表演（含视频、音频、深度、摄像机）导出为 Level Sequence 用于 Sequencer 编辑 → 使用 `ExportLevelSequence` API
- 你需要批量处理大量表演素材 → 使用 `MetaHumanBatchProcessor` 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputType` | 设置数据输入类型（深度视频/音频/单目视频） | `UMetaHumanPerformance` |
| `SetFootageCaptureData` | 设置视频素材数据源 | `UMetaHumanPerformance` |
| `SetAudio` | 设置音频源 | `UMetaHumanPerformance` |
| `SetIdentity` | 设置 MetaHuman Identity 数字替身 | `UMetaHumanPerformance` |
| `SetProcessingRange` | 设置处理帧范围 | `UMetaHumanPerformance` |
| `SetControlRigAssetReference` | 设置用于驱动动画的 Control Rig | `UMetaHumanPerformance` |
| `SetDepthDistanceRange` | 设置深度有效距离范围（厘米） | `UMetaHumanPerformance` |
| `StartPipeline` | 启动处理管线 | `UMetaHumanPerformance` |
| `CancelPipeline` | 取消正在运行的处理 | `UMetaHumanPerformance` |
| `IsProcessing` | 查询是否正在处理中 | `UMetaHumanPerformance` |
| `CanProcess` | 查询是否满足处理条件 | `UMetaHumanPerformance` |
| `CanExportAnimation` | 查询是否可以导出动画 | `UMetaHumanPerformance` |
| `DiagnosticsIndicatesProcessingIssue` | 检查处理诊断是否发现问题 | `UMetaHumanPerformance` |
| `SetBlockingProcessing` | 设置是否阻塞式处理（脚本化调用时使用） | `UMetaHumanPerformance` |
| `GetExportAnimationSequenceSettings` | 获取基于当前 Performance 配置的动画导出设置 | `UMetaHumanPerformanceExportUtils` |
| `GetExportLevelSequenceSettings` | 获取基于当前 Performance 配置的关卡序列导出设置 | `UMetaHumanPerformanceExportUtils` |
| `ExportAnimationSequence` | 从 Performance 导出动画序列资产 | `UMetaHumanPerformanceExportUtils` |
| `ExportLevelSequence` | 从 Performance 导出关卡序列资产 | `UMetaHumanPerformanceExportUtils` |
| `IsTargetSkeletonCompatible` | 检查目标骨架是否兼容（缺少哪些曲线） | `UMetaHumanPerformanceExportAnimationSettings` |

### 使用示例（蓝图描述）

**场景：从音频驱动面部动画**

1. 创建一个 `UMetaHumanPerformance` 资产
2. 调用 `SetInputType(EDataInputType::Audio)` 设置输入模式为音频
3. 调用 `SetAudio(YourSoundWave)` 加载音频文件
4. 设置 `bRealtimeAudio` 为 `true`（实时模式）或 `false`（离线模式，可生成眨眼）
5. 调用 `StartPipeline()` 开始处理
6. 监听 `OnProcessingFinishedDynamic` 委托等待处理完成
7. 调用 `ExportAnimationSequence()` 导出动画序列

**场景：从单目视频提取面部+身体动画**

1. 调用 `SetInputType(EDataInputType::MonoFootage)`
2. 调用 `SetFootageCaptureData(YourFootageData)` 加载视频素材
3. 设置 `bBodyTracking = true` 启用身体追踪
4. 调用 `SetProcessingRange(StartFrame, EndFrame)` 选择处理范围
5. 调用 `StartPipeline()` 开始处理
6. 处理完成后调用 `GetExportAnimationSequenceSettings()` 获取导出配置
7. 在导出设置中可选择 `ExportSkeleton` 类型（原始骨架或重定向到现有骨架）
8. 调用 `ExportAnimationSequence()` 导出

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPerformance.h"
#include "MetaHumanPerformanceExportUtils.h"
```

### 基本用法

从 `UMetaHumanPerformance` 的 API 和 `UMetaHumanPerformanceExportUtils` 提取：

```cpp
// 创建并配置一个 Performance 资产（通常在编辑器中完成，此处演示脚本化流程）
UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>();

// 设置输入类型
Performance->SetInputType(EDataInputType::Audio);

// 设置音频源
Performance->SetAudio(MySoundWave);

// 设置处理范围
Performance->SetProcessingRange(0, 100);

// 启动阻塞式处理（脚本化调用时使用，会等待处理完成）
Performance->SetBlockingProcessing(true);
EStartPipelineErrorType ErrorType = Performance->StartPipeline(true);

if (ErrorType == EStartPipelineErrorType::None)
{
    // 处理完成，导出动画序列
    UMetaHumanPerformanceExportAnimationSettings* ExportSettings = 
        UMetaHumanPerformanceExportUtils::GetExportAnimationSequenceSettings(Performance);
    
    UAnimSequence* AnimSequence = 
        UMetaHumanPerformanceExportUtils::ExportAnimationSequence(Performance, ExportSettings);
}
```

### 进阶用法

深度视频模式配合 Level Sequence 导出：

```cpp
// 配置深度视频模式
Performance->SetInputType(EDataInputType::DepthFootage);
Performance->SetFootageCaptureData(MyFootageCaptureData);
Performance->SetIdentity(MyMetaHumanIdentity);

// 配置 Control Rig
FControlRigAssetStrongReference CRRef;
CRRef.ResetToDefault(); // 使用默认 MetaHuman Control Rig
Performance->SetControlRigAssetReference(CRRef);

// 配置身体追踪
Performance->SetBodyTracking(true); // 蓝图 setter

// 设置头部运动模式
Performance->HeadMovementMode = EPerformanceHeadMovementMode::ControlRig;
Performance->bAutoChooseHeadMovementReferenceFrame = true;

// 设置深度参数
Performance->SetDepthDistanceRange(10.0f, 25.0f);

// 启动处理
Performance->StartPipeline(true);

// 导出 Level Sequence
UMetaHumanPerformanceExportLevelSequenceSettings* LSSettings = 
    UMetaHumanPerformanceExportUtils::GetExportLevelSequenceSettings(Performance);

// 自定义导出选项
LSSettings->bExportVideoTrack = true;
LSSettings->bExportAudioTrack = true;
LSSettings->bExportIdentity = true;
LSSettings->bExportControlRigTrack = true;
LSSettings->bExportCamera = true;
LSSettings->ExportRange = EPerformanceExportRange::ProcessingRange;

ULevelSequence* LevelSequence = 
    UMetaHumanPerformanceExportUtils::ExportLevelSequence(Performance, LSSettings);
```

## Demo 示例

以下展示如何通过 C++ 脚本化创建一个从音频驱动面部动画的完整流程：

```cpp
// MetaHumanPerformanceDemo.h
#pragma once

#include "CoreMinimal.h"

class UMetaHumanPerformance;
class USoundWave;

class FMetaHumanPerformanceDemo
{
public:
    /** 从音频文件驱动 MetaHuman 面部动画并导出 AnimSequence */
    static bool DemoAudioToAnimation(USoundWave* InAudio, UObject* InOuter);
    
    /** 检查处理诊断信息 */
    static void CheckDiagnostics(const UMetaHumanPerformance* InPerformance);
};
```

```cpp
// MetaHumanPerformanceDemo.cpp
#include "MetaHumanPerformanceDemo.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanPerformanceExportUtils.h"

bool FMetaHumanPerformanceDemo::DemoAudioToAnimation(USoundWave* InAudio, UObject* InOuter)
{
    if (!InAudio || !InOuter)
    {
        return false;
    }

    // 创建 Performance 资产
    UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>(
        InOuter, UMetaHumanPerformance::StaticClass(), 
        FName("DemoPerformance"), RF_Transient);

    // 设置为音频模式
    Performance->SetInputType(EDataInputType::Audio);

    // 设置音频源
    Performance->SetAudio(InAudio);

    // 启用离线音频处理（支持眨眼生成）
    Performance->bRealtimeAudio = false;
    Performance->bGenerateBlinks = true;
    Performance->AudioDrivenAnimationOutputControls = EAudioDrivenAnimationOutputControls::FullFace;

    // 设置处理范围（使用全部音频）
    Performance->SetProcessingRange(0, 1000);

    // 设置阻塞式处理以同步等待结果
    Performance->SetBlockingProcessing(true);

    // 启动处理管线
    EStartPipelineErrorType Error = Performance->StartPipeline(true);
    if (Error != EStartPipelineErrorType::None)
    {
        UE_LOG(LogMetaHumanPerformance, Error, TEXT("Pipeline failed to start, error type: %d"), 
               static_cast<int32>(Error));
        return false;
    }

    // 获取导出设置
    UMetaHumanPerformanceExportAnimationSettings* ExportSettings = 
        UMetaHumanPerformanceExportUtils::GetExportAnimationSequenceSettings(Performance);

    // 自定义导出参数
    ExportSettings->bEnableHeadMovement = true;
    ExportSettings->bAutoSaveAnimSequence = false;
    ExportSettings->ExportRange = EPerformanceExportRange::WholeSequence;
    ExportSettings->CurveInterpolation = RCIM_Linear;
    ExportSettings->bRemoveRedundantCurveKeys = true;
    ExportSettings->bShowExportDialog = false;
    ExportSettings->AssetName = TEXT("DemoAudioAnim");
    ExportSettings->PackagePath = TEXT("/Game/MetaHuman/Demo/");

    // 导出动画序列
    UAnimSequence* AnimSequence = 
        UMetaHumanPerformanceExportUtils::ExportAnimationSequence(Performance, ExportSettings);

    if (AnimSequence)
    {
        UE_LOG(LogMetaHumanPerformance, Log, TEXT("Successfully exported animation: %s"), 
               *AnimSequence->GetName());
        return true;
    }

    return false;
}

void FMetaHumanPerformanceDemo::CheckDiagnostics(const UMetaHumanPerformance* InPerformance)
{
    if (!InPerformance)
    {
        return;
    }

    FText WarningMessage;
    if (InPerformance->DiagnosticsIndicatesProcessingIssue(WarningMessage))
    {
        UE_LOG(LogMetaHumanPerformance, Warning, TEXT("Diagnostics issue: %s"), 
               *WarningMessage.ToString());
    }
    else
    {
        UE_LOG(LogMetaHumanPerformance, Log, TEXT("No diagnostics issues detected."));
    }
}
```

## 模块依赖

MetaHumanPerformance 模块自身 Build.cs 未在列表中显示具体依赖，但从源码头文件和关联模块可以推断出以下关键依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanPipeline` | 底层处理管线框架，用于构建和执行动画求解管线 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪器，用于从视频中检测和追踪面部特征点 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器，将追踪数据转换为 Control Rig 控制值 |
| `MetaHumanDepthGenerator` | 深度图生成器，从立体视频生成深度信息 |
| `MetaHumanSpeech2Face` | 音频驱动面部动画的 AI 模型接口 |
| `MetaHumanIdentity` | MetaHuman Identity 资产管理，提供数字替身和骨架数据 |
| `MetaHumanCaptureDataEditor` | 捕获数据的编辑器支持 |
| `ControlRig` / `ControlRigDeveloper` | Control Rig 运行时和开发支持，驱动动画 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器工具 |
| `Sequencer` / `MovieScene` | Sequencer 时间线和动画数据记录 |
| `IKRetargeter` | IK 重定向器，用于身体动画骨架重定向 |
| `MediaAssets` | 媒体资产支持，处理视频和音频输入 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持将动画导出到现有骨骼网格体 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：最近的提交日期为 2026 年 5 月，距今不到一个月，且持续有功能性更新和 bug 修复
- **代码规模**：544 个源文件，28 个运行时模块，属于大型工程级插件
- **更新频率**：非常活跃，几乎每天都有更新，覆盖新功能、bug 修复、兼容性改进
- **实验性状态**：`IsBetaVersion=false`，`IsExperimentalVersion=false`，已经是正式发布的稳定插件
- **推荐程度**：✅ **强烈推荐使用**。这是 Epic 官方维护的核心 MetaHuman 工具链，是 MetaHuman 数字人动画的标准工作流入口。插件仍在积极开发中，新功能持续迭代（如近期新增的身体动画导出到现有骨架功能）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator-in-unreal-engine/)