# Full Body IK

> （.uplugin 中的 Description 为空）

| 属性 | 值 |
|---|---|
| 中文名 | 全身逆向运动学 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Control Rig 蓝图资产） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

`FullBodyIK` 插件实现了一个基于位置的全身逆向运动学求解器。它主要用于解决复杂角色骨架在受到多个目标点（效应器）约束时的姿态计算问题。与传统的末端执行器 IK 不同，该求解器能够处理整个骨架树的连锁运动，特别适用于需要自然、物理可信的角色动画效果，如角色抓取物体、攀爬、与环境互动或进行复杂姿势表演。其核心模块 `PBIK` 依赖 `ControlRig` 框架，作为 `RigUnit` 集成，允许用户在 Control Rig 蓝图中直观地使用和调试。

## 使用场景

- 你需要让角色的手或脚精准地触碰到场景中的特定目标点。
- 你在制作一个攀爬系统，需要角色的手脚自动适配不同形状的岩石表面。
- 你希望角色在搬运重物或做出格斗动作时，身体各部位（如脊柱、肩部）能自然、协调地联动。
- 你需要为动画重定向或动捕数据清理提供一个可控的、带约束的全身姿态校正工具。

## 蓝图用法

该插件的核心是一个名为 `Full Body IK` 的 `RigUnit`，通过 Control Rig 的图表进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Full Body IK` | 全身逆向运动学主节点。设置根骨骼、效应器目标、骨骼约束和求解器参数。 | `FRigUnit_PBIK` |

### 使用示例（蓝图描述）

1.  在你的 `Control Rig` 资产中，添加一个 `Full Body IK` 节点。
2.  连接 `Root` 输入引脚到你希望作为解算根骨骼的骨骼名（例如 `pelvis` 或 `spine_01`）。
3.  构造一个 `FPBIKEffector` 结构体数组，通过 `Effectors` 引脚输入。为每个需要控制的末端骨骼（如 `hand_r`, `foot_l`）设置目标 `Transform`（位置和旋转）。
4.  通过 `BoneSettings` 引脚输入一个 `FPBIKBoneSetting` 数组，为特定骨骼（如肘部、膝盖）添加关节限制、刚度或首选角度，以引导其弯曲方向。
5.  调整 `Settings` 引脚中的 `FPBIKSolverSettings` 结构体，控制迭代次数（`Iterations`）、根骨骼行为（`RootBehavior`）和全局质量（`MassMultiplier`）。
6.  将动画输入或上一个节点的输出连接到 `Get Initial Pose` 上下文节点，为求解器提供初始姿态。
7.  在 `Forwards Solve` 中执行该 `Full Body IK` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "PBIKSolver.h"
#include "PBIK_Shared.h"
#include "RigUnit_PBIK.h"
```

### 基本用法

以下示例展示了如何在 C++ 中直接创建和使用一个简单的 PBIK 求解器。请注意，通常这会封装在 Control Rig 的 RigUnit 内部，但此处演示了底层 API 的调用方式。

```cpp
// 来源参考: Public/Core/PBIKSolver.h 和 Public/RigUnit_PBIK.h

#include "PBIKSolver.h"
#include "PBIK_Shared.h"

// 创建一个求解器实例
FPBIKSolver MySolver;

// 1. 添加骨骼以构建骨架结构
// 假设有一个简单的三骨骼链：Root -> Shoulder -> Hand
int32 RootBoneIndex = MySolver.AddBone(
    FName("Root"), -1, FVector(0, 0, 100), FQuat::Identity, true);
int32 ShoulderBoneIndex = MySolver.AddBone(
    FName("Shoulder"), RootBoneIndex, FVector(0, 0, 100), FQuat::Identity, false);
int32 HandBoneIndex = MySolver.AddBone(
    FName("Hand"), ShoulderBoneIndex, FVector(0, 50, 100), FQuat::Identity, false);

// 2. 初始化求解器（建立内部刚体、约束等）
MySolver.Initialize();

// 3. 设置求解器参数
FPBIKSolverSettings SolverSettings;
SolverSettings.Iterations = 15;
SolverSettings.RootBehavior = EPBIKRootBehavior::PinToInput;

// 4. 添加效应器并设置目标
int32 EffectorIndex = MySolver.AddEffector(FName("Hand"));
PBIK::FEffectorSettings EffectorSettings; // 此处可设置效应器特定属性
MySolver.SetEffectorGoal(
    EffectorIndex,
    FVector(100, 0, 100), // 目标位置
    FQuat::Identity,      // 目标旋转
    EffectorSettings);

// 5. 执行求解
MySolver.Solve(SolverSettings);

// 6. 获取结果
FTransform HandResultTransform;
MySolver.GetBoneGlobalTransform(HandBoneIndex, HandResultTransform);
// HandResultTransform 现在包含了受 IK 影响后的手部变换
```

### 进阶用法

进阶用法通常涉及通过 `FRigUnit_PBIK` 的实例，在 Control Rig 的执行上下文中操作。这包括：
- 动态修改 `Effectors` 数组（例如，通过蓝图或代码更新目标位置）。
- 根据游戏状态动态调整 `BoneSettings`，例如在角色受伤时增加某根骨头的 `RotationStiffness`。
- 结合 `FPBIKDebug` 结构体在编辑器中可视化调试约束和效应器。

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何在自定义的 `UObject` 或 `AActor` 中使用 `FPBIKSolver`。

```cpp
// MyIKSolver.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PBIKSolver.h"
#include "PBIK_Shared.h"
#include "MyIKSolver.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyIKSolver : public UObject
{
    GENERATED_BODY()

public:
    UMyIKSolver();

    /** 初始化求解器，构建简单的三骨骼链 */
    UFUNCTION(BlueprintCallable, Category="IK")
    void Initialize();

    /** 求解到指定的目标位置 */
    UFUNCTION(BlueprintCallable, Category="IK")
    void SolveToTarget(const FVector& TargetLocation);

    /** 获取末端骨骼（Hand）解算后的变换 */
    UFUNCTION(BlueprintCallable, Category="IK")
    FTransform GetSolvedHandTransform() const;

private:
    FPBIKSolver Solver;
    int32 HandBoneIndex = INDEX_NONE;
    int32 HandEffectorIndex = INDEX_NONE;

    FPBIKSolverSettings SolverSettings;
};
```

```cpp
// MyIKSolver.cpp
#include "MyIKSolver.h"

UMyIKSolver::UMyIKSolver()
{
    // 配置求解器设置
    SolverSettings.Iterations = 20;
    SolverSettings.RootBehavior = EPBIKRootBehavior::PinToInput;
}

void UMyIKSolver::Initialize()
{
    // 假设初始姿态下的骨骼位置
    const FVector RootPos(0, 0, 0);
    const FVector ShoulderPos(0, 0, 100);
    const FVector HandPos(0, 50, 100);

    // 添加骨骼
    int32 RootIndex = Solver.AddBone(FName("Pelvis"), -1, RootPos, FQuat::Identity, true);
    int32 ShoulderIndex = Solver.AddBone(FName("Shoulder"), RootIndex, ShoulderPos, FQuat::Identity, false);
    HandBoneIndex = Solver.AddBone(FName("Hand"), ShoulderIndex, HandPos, FQuat::Identity, false);

    // 初始化求解器
    Solver.Initialize();

    // 为手部添加一个效应器
    HandEffectorIndex = Solver.AddEffector(FName("Hand"));

    // 可选：为肘部添加首选角度，引导其向正确的方向弯曲
    PBIK::FBoneSettings* ShoulderSettings = Solver.GetBoneSettings(ShoulderIndex);
    if (ShoulderSettings)
    {
        ShoulderSettings->bUsePreferredAngles = true;
        // 假设肘部首选弯曲方向为局部 Y 轴
        ShoulderSettings->PreferredAngles = FRotator(0, 45, 0); // Pitch=0, Yaw=45, Roll=0
    }
}

void UMyIKSolver::SolveToTarget(const FVector& TargetLocation)
{
    if (!Solver.IsReadyToSimulate() || HandEffectorIndex == INDEX_NONE)
    {
        return;
    }

    // 更新效应器目标
    PBIK::FEffectorSettings EffectorSettings;
    Solver.SetEffectorGoal(HandEffectorIndex, TargetLocation, FQuat::Identity, EffectorSettings);

    // 执行求解
    Solver.Solve(SolverSettings);
}

FTransform UMyIKSolver::GetSolvedHandTransform() const
{
    FTransform Result;
    if (Solver.IsReadyToSimulate() && HandBoneIndex != INDEX_NONE)
    {
        Solver.GetBoneGlobalTransform(HandBoneIndex, Result);
    }
    return Result;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供运行时 Control Rig 框架和 RigUnit 基础架构。 |
| `ControlRigDeveloper` | Control Rig 编辑器开发支持，用于创建和调试资产。 |
| `RigVMDeveloper` | RigVM（Control Rig 的虚拟机）开发工具。 |

**注意**：`PBIK` 模块的 `Build.cs` 中还列出了 `Engine`, `AssetTools`, `UnrealEd`, `RigVMEditor` 等模块，但这些属于编辑器/开发工具链依赖，对于纯运行时使用，使用者通常只需依赖 `ControlRig`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | [FBIK] 添加了之前被移除的调试属性。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码清理，将析构函数统一改为 `= default` 写法。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎范围代码清理，统一析构函数写法。 |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | [FBIK] 修复了在分叉关节上使用中间效应器时导致的崩溃 Bug。 |

### 维护评价

- **创建时间**：2020年9月，已存在约5年。
- **最近更新**：最近一次实质性功能/修复更新在 **2025年10月21日**（修复崩溃），最近一次常规维护在 **2026年4月**（日志宏迁移）。更新频率稳定。
- **活跃维护**：是。Epic Games 团队仍在维护此插件，有 Bug 修复和内部代码清理。
- **已知限制**：插件路径仍位于 `Experimental` 文件夹下，表明其 API 或功能在未来版本中可能发生变化。依赖于 `ControlRig` 生态。
- **推荐使用**：**推荐**。对于需要在 Control Rig 中实现高质量全身 IK 的动画项目，这是一个官方提供的、功能完整且得到维护的解决方案。但由于其“实验性”标签，在生产环境中使用需关注版本更新日志，以防 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [官方文档](https://docs.unrealengine.com/)（请在此链接中搜索 “Full Body IK” 或 “Control Rig”）