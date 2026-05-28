# Full Body IK

> （描述字段为空，根据源码分析补充：一个基于位置的动力学（PBD）的全身逆向运动学（IK）求解器，作为 Control Rig 的节点提供，用于驱动角色骨骼以精确到达多个目标点。）

| 属性 | 值 |
|---|---|
| 中文名 | 全身IK求解器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图资产） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

FullBodyIK 插件提供了一套高性能的全身逆向运动学（IK）求解器。它主要解决角色动画中的姿态修正问题，例如当角色需要用手抓住一个移动的把手或脚踩到起伏的地面时，通过设置手或脚的“效果器”（Effector）目标点，求解器会实时计算出整个骨架的合理姿态，使目标骨骼能够到达指定位置，同时保持骨骼层级间的物理约束和姿态的自然性。

其核心是 `PBIK` 模块中的 `FPBIKSolver`，一个基于位置的动力学（PBD）求解器。它通过迭代计算骨骼（刚体）之间的关节约束和引脚约束来实现 IK。`FullBodyIK` 模块将其封装为一个 `Control Rig` 节点 `FRigUnit_PBIK`，便于在动画蓝图和 Control Rig 蓝图中直接使用。

该插件默认未启用（`Installed: false`），是一个需要手动启用的实验性功能模块。

## 使用场景

- **第三人称角色的脚部 IK**：让角色的脚在不平的地形上自动适应地表高度，防止脚部穿模或悬浮。
- **手部与物体交互 IK**：在角色抓握门把手、武器或攀爬时，精确驱动手部到达目标位置。
- **动画后处理**：在现有动画基础上，对特定骨骼（如头部、脊柱）进行微调，使其朝向某个目标。
- **需要根骨骼运动调整的 IK**：当四肢被拉伸得很远时，求解器可以通过 `RootBehavior` 设置（如 `PrePull`）自动移动整个骨架的根部，以更好地收敛到目标姿态。
- **需要物理合理性的 IK**：通过 `BoneSettings` 设置骨骼的旋转限制（`Rotation Limit`）、首选角度（`Preferred Angles`）和刚度（`Stiffness`），确保 IK 结果不会产生违反解剖学或物理规律的扭曲。

## 蓝图用法

此插件主要通过 Control Rig 的节点在蓝图中使用。核心节点是 `Full Body IK`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Full Body IK` | 全身IK求解器节点，配置效果器、骨骼约束和求解设置，输出修正后的骨骼姿态。 | `FRigUnit_PBIK` |

### 使用示例（蓝图描述）

1.  在你的动画蓝图或 Control Rig 蓝图中，添加一个 **`Full Body IK`** 节点。
2.  **`Root`** 引脚：连接到你希望作为 IK 层级根部的骨骼名称（通常是 `pelvis` 或 `spine_01`）。
3.  **`Effectors`** 引脚：创建一个 `FPBIKEffector` 结构体数组。为每个需要 IK 控制的末端骨骼（如 `hand_r`, `foot_l`）创建一个元素。
    -   设置每个元素的 **`Bone`** 为目标骨骼名。
    -   将 **`Transform`** 引脚连接到你希望该骨骼到达的世界空间目标变换（可以从场景中的物体或计算得出）。
    -   可通过 `StrengthAlpha`, `PositionAlpha`, `RotationAlpha` 等调整每个效果器的影响强度。
4.  **`BoneSettings`** 引脚：创建一个 `FPBIKBoneSetting` 结构体数组。为需要特殊约束的骨骼（如肘部、膝盖）创建元素。
    -   设置 `Bone` 为骨骼名。
    -   通过 `X`, `Y`, `Z` 设置其各轴向的旋转限制（`Free`, `Limited`, `Locked`）。
    -   启用 `bUsePreferredAngles` 并设置 `PreferredAngles`，以强制肘关节在压缩时向后弯曲，膝盖向前弯曲。
5.  **`Settings`** 引脚：配置 `FPBIKSolverSettings`，如 `Iterations`（迭代次数，影响精度和性能）、`RootBehavior`（根骨骼行为）、`bAllowStretch`（是否允许骨骼拉伸）。
6.  节点的输出是修正后的骨骼变换，需要将其应用回骨骼。

## C++ 用法

在C++中，你可以直接使用 `PBIK` 模块中的 `FPBIKSolver` 进行底层控制。

### 头文件引入

```cpp
#include "Core/PBIKSolver.h"
#include "PBIK_Shared.h"
```

### 基本用法

以下代码展示了如何设置和运行一次简单的 PBIK 求解。
（基于 `FPBIKSolver` 公共接口推断的典型用法）

```cpp
// 创建一个 PBIK 求解器实例
FPBIKSolver Solver;

// 1. 初始化求解器结构（通常基于角色的骨骼引用姿势）
// 假设我们从骨骼网格体组件获取骨骼信息
FReferenceSkeleton RefSkeleton = SkeletalMeshComponent->GetSkeletalMeshAsset()->GetRefSkeleton();
for (int32 i = 0; i < RefSkeleton.GetNum(); ++i)
{
    FName BoneName = RefSkeleton.GetBoneName(i);
    int32 ParentIndex = RefSkeleton.GetParentIndex(i);
    FTransform BoneTransform = SkeletalMeshComponent->GetBoneTransform(i); // 或使用参考姿势
    bool bIsRoot = (i == 0); // 根据你的需求设置哪个骨骼是求解器的根

    // 将骨骼添加到求解器
    Solver.AddBone(BoneName, ParentIndex, BoneTransform.GetLocation(), BoneTransform.GetRotation(), bIsRoot);
}

// 为需要控制的末端骨骼添加效果器
int32 EffectorIndex = Solver.AddEffector(TEXT("hand_r"));

// 2. 初始化求解器（分配内存，构建约束等）
Solver.Initialize();

// 3. 运行时：每帧更新并求解
// 3.1 设置当前帧的输入骨骼姿态（来自动画或上一帧结果）
for (int32 i = 0; i < Solver.GetNumBones(); ++i)
{
    FTransform CurrentBoneTransform = SkeletalMeshComponent->GetBoneTransform(i);
    Solver.SetBoneTransform(i, CurrentBoneTransform);
}

// 3.2 设置效果器的目标位置和旋转
FVector GoalPosition = SomeTargetActor->GetActorLocation();
FQuat GoalRotation = SomeTargetActor->GetActorQuat();
PBIK::FEffectorSettings EffectorSettings; // 可配置强度等
Solver.SetEffectorGoal(EffectorIndex, GoalPosition, GoalRotation, EffectorSettings);

// 3.3 配置求解参数
FPBIKSolverSettings SolverSettings;
SolverSettings.Iterations = 10;
SolverSettings.RootBehavior = EPBIKRootBehavior::PrePull;

// 3.4 执行求解
Solver.Solve(SolverSettings);

// 3.5 获取求解后的骨骼变换并应用
for (int32 i = 0; i < Solver.GetNumBones(); ++i)
{
    FTransform SolvedTransform;
    Solver.GetBoneGlobalTransform(i, SolvedTransform);
    SkeletalMeshComponent->SetBoneTransformByName(Solver.GetBoneIndex(/*...*/), SolvedTransform, EBoneSpaces::WorldSpace);
}
```

### 进阶用法

在 Control Rig 中使用时，通常不需要直接操作 `FPBIKSolver`，而是通过 `FRigUnit_PBIK` 结构体。以下是一个简化的 Control Rig 单元执行逻辑的模拟：

```cpp
// 模拟 FRigUnit_PBIK::Execute() 的核心逻辑
void ExecutePBIKRigUnit()
{
    // 获取或初始化 WorkData 中的 FPBIKSolver
    if (WorkData.bNeedsInit || WorkData.HashInitializedWith != CurrentBoneHash)
    {
        // 从当前 Control Rig 的骨骼层级重建求解器
        RebuildSolverFromHierarchy(WorkData.Solver, BoneHierarchy);
        WorkData.Solver.Initialize();
        WorkData.bNeedsInit = false;
        WorkData.HashInitializedWith = CurrentBoneHash;
    }

    FPBIKSolver& Solver = WorkData.Solver;

    // 同步当前输入姿态
    for (int32 i = 0; i < Solver.GetNumBones(); ++i)
    {
        FTransform BoneTransform = GetBoneTransform(i);
        Solver.SetBoneTransform(i, BoneTransform);
    }

    // 同步效果器目标（来自 Effectors 数组）
    for (const FPBIKEffector& EffectorInput : Effectors)
    {
        int32 SolverBoneIndex = FindSolverBoneIndex(EffectorInput.Bone);
        if (SolverBoneIndex != INDEX_NONE)
        {
            PBIK::FEffectorSettings Settings;
            Settings.StrengthAlpha = EffectorInput.StrengthAlpha;
            // ... 设置其他 Settings
            Solver.SetEffectorGoal(SolverBoneIndex, EffectorInput.Transform.GetLocation(), EffectorInput.Transform.GetRotation(), Settings);
        }
    }

    // 应用 BoneSettings（旋转限制、首选角度等）
    for (const FPBIKBoneSetting& BoneSettingInput : BoneSettings)
    {
        int32 SolverBoneIndex = FindSolverBoneIndex(BoneSettingInput.Bone);
        if (SolverBoneIndex != INDEX_NONE)
        {
            PBIK::FBoneSettings* SolverBoneSettings = Solver.GetBoneSettings(SolverBoneIndex);
            if (SolverBoneSettings)
            {
                BoneSettingInput.CopyToCoreStruct(*SolverBoneSettings);
            }
        }
    }

    // 排除骨骼
    // ... 通过某种机制标记 ExcludedBones 中的骨骼

    // 执行求解
    Solver.Solve(Settings);

    // 将求解结果写回 Control Rig
    for (int32 i = 0; i < Solver.GetNumBones(); ++i)
    {
        FTransform SolvedTransform;
        Solver.GetBoneGlobalTransform(i, SolvedTransform);
        SetBoneTransform(i, SolvedTransform);
    }
}
```

## Demo 示例

以下是一个最小的可运行示例，演示如何用 C++ 代码驱动一个简单的两骨链进行 IK 求解。

### PBIKDemoActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Core/PBIKSolver.h"
#include "PBIKDemoActor.generated.h"

UCLASS()
class APBIKDemoActor : public AActor
{
    GENERATED_BODY()

public:
    APBIKDemoActor();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

private:
    // 模拟一个简单的两骨骼链：Root -> Bone1
    FPBIKSolver Solver;
    bool bSolverInitialized = false;

    // 效果器目标（一个在场景中移动的 Actor）
    UPROPERTY(EditAnywhere, Category="PBIK Demo")
    AActor* TargetActor;

    void InitializeSolver();
};
```

### PBIKDemoActor.cpp
```cpp
#include "PBIKDemoActor.h"

APBIKDemoActor::APBIKDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void APBIKDemoActor::BeginPlay()
{
    Super::BeginPlay();
    InitializeSolver();
}

void APBIKDemoActor::InitializeSolver()
{
    // 定义骨骼：Root (Index 0) 和 Bone1 (Index 1)
    // 假设初始姿态：Root在原点，Bone1在(100, 0, 0)
    Solver.AddBone(TEXT("Root"), -1, FVector::ZeroVector, FQuat::Identity, true);
    Solver.AddBone(TEXT("Bone1"), 0, FVector(100.f, 0.f, 0.f), FQuat::Identity, false);

    // 为 Bone1 添加效果器
    Solver.AddEffector(TEXT("Bone1"));

    // 初始化求解器
    if (Solver.Initialize())
    {
        bSolverInitialized = true;
    }
}

void APBIKDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bSolverInitialized || !TargetActor)
    {
        return;
    }

    // 1. 设置当前输入姿态 (假设从初始参考姿势开始，实际中可能来自动画)
    //    这里为了演示，我们每帧都重置为初始姿态
    Solver.SetBoneTransform(0, FTransform(FQuat::Identity, FVector::ZeroVector));
    Solver.SetBoneTransform(1, FTransform(FQuat::Identity, FVector(100.f, 0.f, 0.f)));

    // 2. 设置效果器目标为 TargetActor 的位置
    int32 EffectorIndex = 0; // Bone1 的效果器索引
    FVector GoalLocation = TargetActor->GetActorLocation();
    FQuat GoalRotation = FQuat::Identity;
    PBIK::FEffectorSettings EffectorSettings;
    EffectorSettings.StrengthAlpha = 1.0f;
    Solver.SetEffectorGoal(EffectorIndex, GoalLocation, GoalRotation, EffectorSettings);

    // 3. 配置并执行求解
    FPBIKSolverSettings SolverSettings;
    SolverSettings.Iterations = 5;
    SolverSettings.RootBehavior = EPBIKRootBehavior::PinToInput; // 锁定根骨骼
    Solver.Solve(SolverSettings);

    // 4. 获取并可视化结果（在此示例中，我们仅绘制调试线）
    FTransform RootTransform, Bone1Transform;
    Solver.GetBoneGlobalTransform(0, RootTransform);
    Solver.GetBoneGlobalTransform(1, Bone1Transform);

    DrawDebugLine(GetWorld(), RootTransform.GetLocation(), Bone1Transform.GetLocation(), FColor::Green, false, -1.f, 0, 2.f);
    DrawDebugSphere(GetWorld(), Bone1Transform.GetLocation(), 10.f, 12, FColor::Red);
}
```

## 模块依赖

使用此插件需要你的项目或模块依赖以下特有模块：

| 模块 | 用途 |
|---|---|
| `ControlRig` | FullBodyIK 节点 (`FRigUnit_PBIK`) 的宿主框架，提供动画求值和节点图系统。 |
| `ControlRigDeveloper` / `ControlRigEditor` | 用于 Control Rig 资产的开发、编辑器集成和蓝图节点注册。 |
| `RigVMDeveloper` / `RigVMEditor` | Control Rig 底层虚拟机（RigVM）的开发和编辑器支持。 |
| `Engine` | 核心引擎模块，提供 `USkeletalMeshComponent`、`FTransform` 等基础类型。 |
| `AssetTools` | 用于创建和管理 Control Rig 等资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 宏。 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 重新添加了之前移除的调试属性。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码规范化，将空析构函数改为 `= default`。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎范围的代码规范化，与上一条同类。 |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复了在分叉关节处使用中间效果器导致的崩溃 Bug。 |

### 维护评价

- **创建时间**：该插件创建于 2020 年 9 月，已有约 5 年历史。
- **最近更新**：最近的提交记录显示，该插件在 **2025 年 10 月和 11 月** 仍有**功能性的修复和更新**（修复崩溃、恢复调试功能），说明它仍然处于**活跃维护**状态，并非被废弃的旧代码。
- **状态**：尽管路径中包含“Experimental”，但 `.uplugin` 的 `IsExperimentalVersion` 为 `false`，且近期有实质性更新。它是一个成熟且仍在维护的**实验性启用模块**。
- **推荐使用**：对于需要复杂全身 IK 解决方案的项目，这是一个强大的选择。由于它是 Epic Games 官方维护的模块，并且近期仍有 Bug 修复，其稳定性和可靠性有保障。推荐在需要角色与环境进行精确、物理合理的交互时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [官方文档]() （当前无官方文档链接）
- [测试用例]() （未提供测试用例路径，但可参考源码中的 `RigUnit_PBIK` 使用方式）