# Trajectory Tools

> Workflows for gameplay trajectories, such as extracting them from recordings.

| 属性 | 值 |
|---|---|
| 分类 | Animation (Experimental) |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | `TrajectoryTools` (Editor, PostEngineInit) |
| 创建时间 | 2025-02-19 |
| 年龄标签 | 🆕 (~1 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/TrajectoryTools) | |

## 用途

TrajectoryTools 是一个编辑器扩展，集成在 **Rewind Debugger** 中，用于从 Trace 录制会话（Trace Session）中提取角色的运行时轨迹数据，并将其烘焙（Bake Out）为 `UAnimSequence` 资产。

核心工作流程：
1. 使用 Rewind Debugger 录制一段游戏运行时数据
2. 在 Rewind Debugger 工具栏中打开 Trajectory Tools 面板
3. 可视化查看各角色的运动轨迹
4. 选择一条轨迹，配置导出设置（帧率、时间范围、原点偏移等）
5. 将轨迹烘焙为动画序列资产，可在 Sequencer 或其他系统中使用

**为什么存在？** 在角色动画开发中，经常需要把实际游戏中的运动轨迹数据提取出来，用于匹配动画、Motion Matching 数据集构建、或 Motion Trajectory 验证等工作。手动录制并转换非常繁琐，此插件将该流程自动化。

## 使用场景

- 你在使用 **Motion Matching / PoseSearch**，需要从实际游戏录制中提取轨迹 → 用 TrajectoryTools
- 你需要将运行时的 **SkeletalMeshComponent 世界变换**导出为动画序列 → 用 TrajectoryTools
- 你在调试 **MotionTrajectory** 插件的行为，需要查看实际轨迹数据 → 用 TrajectoryTools
- 你需要从 Trace 录制中批量提取多角色的运动数据 → 用 TrajectoryTools

> ⚠️ **前置条件**：必须启用 `GameplayInsights` 插件（在 `.uplugin` 中声明为依赖）以及 `RewindDebugger` 插件。

## 蓝图用法

**无蓝图接口。** 此插件的所有功能均在编辑器 C++ 层面实现，不暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。

唯一的 UObject 类型 `UTrajectoryExportOperation` 在其 `ExportTrajectory` 静态方法上有注释：

```cpp
// @todo: After having a general trajectory type, expose this to blueprint...
static void ExportTrajectory(FGameplayTrajectory* InTrajectory, ...);
```

说明 Epic 计划在未来版本中将该接口暴露给蓝图，但当前版本尚未实现。

## C++ 用法

### 头文件引入

```cpp
#include "TrajectoryLibrary.h"
#include "TrajectoryExportOperation.h"
```

### 核心数据结构：FGameplayTrajectory

所有轨迹操作都围绕 `FGameplayTrajectory` 结构展开：

```cpp
USTRUCT()
struct FGameplayTrajectory
{
    struct FSample
    {
        double Time = 0;                  // 采样时间（相对于轨迹起点）
        FVector Position = FVector::ZeroVector;  // 世界坐标位置
        FQuat Orientation = FQuat::Identity;     // 世界坐标朝向
    };

    TArray<FSample> Samples;              // 轨迹采样点序列
    TArray<TArray<FTransform>> Poses;     // 每个采样点对应的 ComponentSpace 骨骼 Pose
    FTraceRangedBuffers TraceInfo;        // Trace 区间与骨骼网格信息
};
```

**关键关系**：`Samples[i]` 和 `Poses[i]` 一一对应，分别存储第 i 帧的根节点世界变换和全身骨骼 Pose。

### 轨迹查询工具 (FTrajectoryToolsLibrary)

```cpp
// 在轨迹中按时间插值获取 Transform
FTransform OutTransform;
bool bFound = FTrajectoryToolsLibrary::GetTransformAtTimeInTrajectory(
    Trajectory, /*RequestedTime=*/1.5, OutTransform);

// 在轨迹中按时间插值获取全身 Pose
TArray<FTransform> OutPose;
bool bFound = FTrajectoryToolsLibrary::GetPoseAtTimeInTrajectory(
    Trajectory, /*RequestedTime=*/1.5, OutPose);

// 将轨迹重采样到目标帧率
FGameplayTrajectory Resampled;
FTrajectoryToolsLibrary::TransformTrajectoryToMatchFrameRate(
    Trajectory, FFrameRate(30, 1), Resampled);
```

### 导出轨迹为 AnimSequence

```cpp
// 配置导出设置
FTrajectoryExportSettings Settings;
Settings.FrameRate = FFrameRate(30, 1);
Settings.Range = {0.0, 5.0};             // 导出前5秒
Settings.bShouldForceOrigin = true;       // 强制原点
Settings.OriginTime = 2.5;               // 原点位于2.5秒处
Settings.bShouldExportOnlyAnimatedBones = true;

// 配置资产信息
FTrajectoryExportAssetInfo AssetInfo;
AssetInfo.AssetName = "ExtractedTrajectory";
AssetInfo.FolderPath.Path = "/Game/Animations";
AssetInfo.Skeleton = FSoftObjectPath("/Game/Characters/MySkeleton.MySkeleton");
AssetInfo.SkeletalMesh = FSoftObjectPath("/Game/Characters/MyMesh.MyMesh");

// 执行导出（创建 UAnimSequence 资产）
UTrajectoryExportOperation::ExportTrajectory(
    &Trajectory, Settings, AssetInfo, "SourceObjectName");
```

## 编辑器工作流（Rewind Debugger 扩展）

### 启用插件

1. 打开 **Edit → Plugins**
2. 搜索 "Trajectory Tools"
3. 启用插件并重启编辑器
4. 确保同时启用了 **GameplayInsights** 和 **RewindDebugger** 插件

### 录制轨迹

1. 打开 **Tools → Trace → Start Trace Recording**
2. 运行 PIE 或连接到远程目标
3. 让角色在场景中移动
4. 停止录制

### 可视化轨迹

1. 打开 Rewind Debugger 窗口
2. 在工具栏中找到 **Trajectories** 子菜单
3. 点击 **Toggle debug draw** 选择要可视化的角色轨迹
4. 轨迹以彩色线条绘制在视口中，每 10 帧标注时间戳

### 导出轨迹

1. 在 Rewind Debugger 工具栏中点击 **Bake out...**
2. 打开 "Bake Out Trajectories" 窗口
3. 左侧为预览视口（可拖动时间轴查看骨骼姿态）
4. 右侧为配置面板：
   - **Trajectory to export**：选择要导出的角色轨迹
   - **Export Settings**：
     - `FrameRate`：目标帧率（默认 30fps）
     - `Range`：导出的时间范围（秒）
     - `Force Origin`：是否将某帧的位置设为原点
     - `Overwrite Existing Files`：是否覆盖已有资产
     - `Export Only Animated Bones`：仅导出有动画的骨骼
   - **Output Asset**：
     - `AssetName`：输出资产名称
     - `FolderPath`：保存目录
     - `Skeleton` / `SkeletalMesh`：自动从 Trace 数据中获取
5. 在时间轴上右键可设置导出范围的起止点和原点位置
6. 点击 **Bake Out** 执行导出
7. 导出的 `UAnimSequence` 资产将出现在 Content Browser 中

> **注意**：如果导出范围跨越了不同的骨骼网格区间（bone count 变化），导出按钮会被禁用。需要将范围限制在单个骨骼网格区间内。

## Demo 示例

### 最小可编译示例：从代码中查询轨迹数据

```cpp
// MyTrajectoryHelper.h
#pragma once

#include "CoreMinimal.h"
#include "TrajectoryLibrary.h"

class FMyTrajectoryHelper
{
public:
    // 从轨迹中采样指定时间点的位置
    static FVector SamplePosition(const FGameplayTrajectory& Trajectory, double Time)
    {
        FTransform Transform;
        if (FTrajectoryToolsLibrary::GetTransformAtTimeInTrajectory(Trajectory, Time, Transform))
        {
            return Transform.GetLocation();
        }
        return FVector::ZeroVector;
    }

    // 生成等间隔采样的位置序列
    static TArray<FVector> ResamplePositions(
        const FGameplayTrajectory& Trajectory,
        FFrameRate TargetRate)
    {
        FGameplayTrajectory Resampled;
        FTrajectoryToolsLibrary::TransformTrajectoryToMatchFrameRate(
            Trajectory, TargetRate, Resampled);

        TArray<FVector> Positions;
        for (const auto& Sample : Resampled.Samples)
        {
            Positions.Add(Sample.Position);
        }
        return Positions;
    }
};
```

**Build.cs 依赖**：此插件为 Editor 模块，不建议在 Runtime 模块中直接依赖。如需使用 `FGameplayTrajectory` 和 `FTrajectoryToolsLibrary` 的数据结构，需在 Editor 模块的 Build.cs 中添加对 `TrajectoryTools` 模块的依赖。由于该模块是 `Editor` 类型，打包后的运行时不可用。

## 模块依赖

以下是从 `TrajectoryTools.Build.cs` 中提取的依赖关系：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库（PublicDependency） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `TraceLog` | Trace 日志系统 |
| `TraceAnalysis` | Trace 数据分析 |
| `TraceServices` | Trace 服务层 |
| `TraceInsights` | Insights 分析工具 |
| `GameplayInsights` | Gameplay 分析提供者（IGameplayProvider / IAnimationProvider） |
| `RewindDebugger` | Rewind Debugger 核心（IRewindDebugger） |
| `RewindDebuggerInterface` | Rewind Debugger 扩展接口（IRewindDebuggerExtension） |
| `PropertyEditor` | 属性编辑器 UI |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |
| `InputCore` | 输入系统 |
| `ToolMenus` | 编辑器工具菜单系统 |
| `ToolWidgets` / `EditorWidgets` | 编辑器控件 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GameplayInsights` | 提供 GameplayProvider 和 AnimationProvider 数据源 |

## 维护状态

### 近期更新

| 日期 | Commit | 内容 | 解读 |
|---|---|---|---|
| 2026-04-15 | `3137aa4` | Fix crash while changing levels due to invalid WorldToVisualize | 修复了一个在关卡切换时崩溃的 Bug —— `WorldToVisualize` 指针失效 |
| 2026-04-13 | `35e60df` | Migrate UE_LOG to UE_LOGF | 日志系统从 UE_LOG 迁移到结构化日志 UE_LOGF，属于全局重构 |
| 2026-04-07 | `e16f6f0` | Replace FAnalysisSessionReadScope with granular provider-level locking | 改进锁粒度，从会话级锁改为 Provider 级锁，防止死锁 |

### 维护评价

- **创建时间**：2025-02-19（约 1 年前）
- **最近活跃度**：非常活跃。2026 年至今（4 个月）已有 8+ 次提交，包含功能改进（UI 重构、自动选择骨骼网格）、Bug 修复（崩溃修复、死锁修复）和代码质量改进（日志迁移、锁优化）
- **维护状态**：🟢 **活跃维护中**
- **已知限制**：
  - 跨骨骼网格区间的导出范围不被支持（按钮会被禁用）
  - 没有蓝图接口（代码中有 @todo 计划暴露）
  - 多处 `@todo` 注释表明仍在快速迭代中
- **推荐使用**：✅ 如果你在使用 Rewind Debugger + Motion Matching 工作流，这个插件非常有用。但作为 Experimental 插件，API 和功能可能在后续版本中有较大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/TrajectoryTools)
- [官方文档]() — 无官方文档页面（.uplugin 中 DocsURL 为空）
- [相关插件: MotionTrajectory](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/MotionTrajectory) — 运行时轨迹组件，TrajectoryTools 是其配套的编辑器工具
- [相关插件: PoseSearch](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch) — Motion Matching 系统，轨迹数据常用于此
