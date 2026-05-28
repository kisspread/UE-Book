# Trajectory Tools

> Workflows for gameplay trajectories, such as extracting them from recordings.

| 属性 | 值 |
|---|---|
| 中文名 | 轨迹工具 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TrajectoryTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/TrajectoryTools) | |

## 用途

TrajectoryTools 是一个与 **Rewind Debugger（回溯调试器）** 紧密集成的动画实验性插件，用于从游戏运行时的 Trace 录制数据中**提取角色运动轨迹**，并将其**导出为动画序列资产（UAnimSequence）**。

核心解决的问题：在调试和迭代动画设计时，开发者往往需要基于真实的游戏运行数据来创建动画。传统做法需要手动调整或依赖美术重制，而 TrajectoryTools 允许开发者直接从 Rewind Debugger 的 Trace 会话中捕获角色的位置、朝向和骨骼姿态数据，配置导出参数（帧率、时间范围、原点偏移等），然后一键导出为可直接使用的动画资产。这对于 Motion Matching、Root Motion 调试、动画与游戏逻辑对齐等工作流非常有价值。

## 使用场景

- 你在使用 **Rewind Debugger** 录制了一段角色跑跳攀爬的游戏过程 → 用 TrajectoryTools 提取轨迹并导出为动画序列
- 你需要为 **Motion Matching** 系统准备离线轨迹数据 → 从多次录制中提取并批量导出
- 你在调试 **Root Motion** 与程序化运动的对齐问题 → 用轨迹预览视口检查导出效果，调整帧率和时间范围后重新导出
- 你需要快速迭代一批动画资产 → 启用"覆盖已有文件"选项进行批量重导出

## 蓝图用法

该插件目前主要面向编辑器和 Rewind Debugger 工作流，不直接暴露蓝图 API。`UTrajectoryExportOperation::ExportTrajectory` 为静态方法但尚未标记 `BlueprintCallable`，源码注释中提到未来计划开放给蓝图使用（`// @todo: After having a general trajectory type, expose this to blueprint`）。

### 核心数据结构

| 结构体 | 说明 |
|---|---|
| `FGameplayTrajectory` | 轨迹数据核心结构，包含采样点（位置+朝向）、骨骼姿态、时间范围信息 |
| `FTrajectoryExportSettings` | 导出配置：帧率、时间范围、原点偏移、是否覆盖文件、是否仅导出动画骨骼 |
| `FTrajectoryExportAssetInfo` | 导出资产信息：资产名、导出路径、关联的 Skeleton 和 SkeletalMesh |

## C++ 用法

### 头文件引入

```cpp
#include "TrajectoryLibrary.h"
#include "TrajectoryExportOperation.h"
```

### 基本用法 — 查询轨迹中的变换

使用 `FTrajectoryToolsLibrary` 静态函数在指定时间点查询轨迹数据。

```cpp
#include "TrajectoryLibrary.h"

// 假设已有一个 FGameplayTrajectory 数据（从 Rewind Debugger 提取或手动构造）
FGameplayTrajectory Trajectory;
// ... 填充 Trajectory 数据 ...

// 查询指定时间点的变换
FTransform OutTransform;
double RequestedTime = 1.5; // 秒
if (FTrajectoryToolsLibrary::GetTransformAtTimeInTrajectory(Trajectory, RequestedTime, OutTransform))
{
    // OutTransform 包含该时间点的插值位置和朝向
    FVector Position = OutTransform.GetLocation();
    FQuat Rotation = OutTransform.GetRotation();
}

// 查询指定时间点的完整骨骼姿态
TArray<FTransform> OutPose;
if (FTrajectoryToolsLibrary::GetPoseAtTimeInTrajectory(Trajectory, RequestedTime, OutPose))
{
    // OutPose 包含该时间点的每个骨骼的变换
    for (const FTransform& BoneTransform : OutPose)
    {
        // 处理每个骨骼变换...
    }
}
```

### 基本用法 — 导出轨迹为动画资产

```cpp
#include "TrajectoryExportOperation.h"

// 配置导出设置
FTrajectoryExportSettings ExportSettings;
ExportSettings.FrameRate = FFrameRate(30, 1); // 30fps
ExportSettings.Range = FFloatInterval(0.0f, 5.0f); // 导出 0-5 秒
ExportSettings.bShouldForceOrigin = true;
ExportSettings.OriginTime = 0.0f; // 将起始位置作为原点
ExportSettings.bShouldExportOnlyAnimatedBones = true;

// 配置导出资产信息
FTrajectoryExportAssetInfo AssetInfo;
AssetInfo.AssetName = TEXT("Run_Start_Trajectory");
AssetInfo.FolderPath.Path = TEXT("/Game/Animations/Exported");
AssetInfo.Skeleton = FSoftObjectPath(TEXT("/Game/Characters/SK_Character.SK_Character_Skeleton"));
AssetInfo.SkeletalMesh = FSoftObjectPath(TEXT("/Game/Characters/SK_Character.SK_Character"));

// 执行导出
FGameplayTrajectory* TrajectoryPtr = &Trajectory; // 已有轨迹数据
UTrajectoryExportOperation::ExportTrajectory(
    TrajectoryPtr,
    ExportSettings,
    AssetInfo,
    TEXT("PlayerCharacter") // 源对象名称
);
```

### 进阶用法 — 帧率匹配与范围重叠检测

```cpp
#include "TrajectoryLibrary.h"

// 将轨迹转换为匹配目标帧率的采样
FGameplayTrajectory FrameMatchedTrajectory;
FFrameRate TargetFrameRate(60, 1); // 60fps
FTrajectoryToolsLibrary::TransformTrajectoryToMatchFrameRate(
    Trajectory, TargetFrameRate, FrameMatchedTrajectory
);

// 将轨迹转换为匹配导出设置（包含范围裁剪、原点偏移等）
FGameplayTrajectory ExportReadyTrajectory;
FTrajectoryExportSettings Settings;
Settings.FrameRate = FFrameRate(30, 1);
Settings.Range = FFloatInterval(1.0f, 4.0f);
FTrajectoryToolsLibrary::TransformTrajectoryToMatchExportSettings(
    Trajectory, Settings, ExportReadyTrajectory
);

// 检测轨迹中指定范围的重叠情况
TRange<int32> SampleRange(10, 50);
FTrajectoryToolsLibrary::FRangeOverlapTestResult OverlapResult;
FTrajectoryToolsLibrary::GetRangeOverlaps(Trajectory, SampleRange, OverlapResult);
if (OverlapResult.bOverlaps)
{
    // OverlapResult.Ranges 包含重叠的范围索引
    for (int RangeIndex : OverlapResult.Ranges)
    {
        // 处理重叠范围...
    }
}
```

## Demo 示例

以下演示如何从代码中构造一个简单的轨迹数据结构并查询其中的变换信息：

### TrajectoryDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "TrajectoryLibrary.h"

class FTrajectoryDemo
{
public:
    /** 构造一条简单的直线运动轨迹用于演示 */
    static FGameplayTrajectory CreateSimpleLinearTrajectory(
        const FVector& StartPos,
        const FVector& EndPos,
        double Duration,
        int32 NumSamples);

    /** 查询并打印轨迹在指定时间点的信息 */
    static void QueryTrajectoryAtTime(
        const FGameplayTrajectory& Trajectory,
        double Time);
};
```

### TrajectoryDemo.cpp

```cpp
#include "TrajectoryDemo.h"
#include "TrajectoryLibrary.h"

FGameplayTrajectory FTrajectoryDemo::CreateSimpleLinearTrajectory(
    const FVector& StartPos,
    const FVector& EndPos,
    double Duration,
    int32 NumSamples)
{
    FGameplayTrajectory Trajectory;
    Trajectory.Samples.Reserve(NumSamples);
    Trajectory.Poses.Reserve(NumSamples);

    const FVector Direction = (EndPos - StartPos).GetSafeNormal();
    const FQuat Orientation = FRotationMatrix::MakeFromX(Direction).ToQuat();

    for (int32 i = 0; i < NumSamples; ++i)
    {
        const double Alpha = static_cast<double>(i) / FMath::Max(NumSamples - 1, 1);
        const double Time = Alpha * Duration;
        const FVector Position = FMath::Lerp(StartPos, EndPos, Alpha);

        FGameplayTrajectory::FSample Sample;
        Sample.Time = Time;
        Sample.Position = Position;
        Sample.Orientation = Orientation;
        Trajectory.Samples.Add(Sample);

        // 每个采样点附带一个简单的单骨骼姿态（根骨骼）
        TArray<FTransform> Pose;
        Pose.Add(FTransform(Orientation, Position));
        Trajectory.Poses.Add(Pose);
    }

    ensure(Trajectory.IsValid());
    return Trajectory;
}

void FTrajectoryDemo::QueryTrajectoryAtTime(
    const FGameplayTrajectory& Trajectory,
    double Time)
{
    // 查询变换
    FTransform OutTransform;
    if (FTrajectoryToolsLibrary::GetTransformAtTimeInTrajectory(
            Trajectory, Time, OutTransform))
    {
        UE_LOG(LogTemp, Log, TEXT("Time %.2f: Position=%s, Rotation=%s"),
            Time,
            *OutTransform.GetLocation().ToString(),
            *OutTransform.GetRotation().ToString());
    }

    // 查询完整骨骼姿态
    TArray<FTransform> OutPose;
    if (FTrajectoryToolsLibrary::GetPoseAtTimeInTrajectory(
            Trajectory, Time, OutPose))
    {
        UE_LOG(LogTemp, Log, TEXT("Time %.2f: Pose has %d bones"),
            Time, OutPose.Num());
    }

    // 查找最匹配的采样索引范围
    TPair<int32, int32> MatchedIndices;
    FTrajectoryToolsLibrary::GetSampleIndicesForMatchedSampleTime(
        Trajectory, Time, MatchedIndices);
    UE_LOG(LogTemp, Log, TEXT("Time %.2f falls between samples [%d, %d]"),
        Time, MatchedIndices.Key, MatchedIndices.Value);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | Rewind Debugger 扩展接口（IRewindDebuggerExtension）和 Trace 数据提供者（IGameplayProvider, IAnimationProvider） |
| `AnimationEditor` | 动画序列资产创建与编辑 |
| `TraceServices` | Trace 会话数据访问 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | Rewind Debugger 工具栏 UX 优化调整 |
| 2026-04-15 | `3137aa4a` | TrajectoryTools - fix for crash while changing levels because of invalid FRewindDebuggerTrajectory:: | 修复切换关卡时因无效的 FRewindDebuggerTrajectory 状态导致的崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-04-07 | `e16f6f01` | [Trajectory Tools] | Trajectory Tools 相关更新（具体信息未说明） |
| 2026-03-30 | `6004f575` | [RewindDebugger] | Rewind Debugger 相关更新（涉及 TrajectoryTools 联动） |

### 维护评价

TrajectoryTools 是一个**活跃维护中的实验性插件**。创建于 2025 年 2 月，至今约 1 年多，最近一次更新在 2026 年 4 月，更新频率稳定（月度级别），包含 bug 修复（崩溃修复）、UX 优化和代码质量改进。

**注意事项**：
- 该插件标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，属于实验性质，API 可能发生变化
- 部分功能（如蓝图暴露）尚未完成，代码中有明确的 `@todo` 标记
- 与 Rewind Debugger 深度绑定，使用前需要熟悉 Trace 录制工作流
- 推荐在需要从 Trace 录制中提取动画数据的场景中使用，生产环境中需谨慎

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/TrajectoryTools)
- 官方文档（暂无）