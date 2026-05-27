# Full Body IK

> 

| 属性 | 值 |
|---|---|
| 中文名 | 全身逆向运动学 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ControlRig 节点资产） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

FullBodyIK 提供一个基于位置的全身逆向运动学（PBIK, Position Based Inverse Kinematics）求解器，作为 ControlRig 的一个 Rig Unit 节点使用。它解决的核心问题是：给定一个根骨骼（如骨盆/臀部）和多个效应器（Effector，如手、脚的目标位置），自动计算整个骨骼链的合理姿势。

与传统两骨骼 IK 不同，PBIK 可以同时处理多条骨骼链之间的耦合关系——例如当一只手被拉高时，整个躯干和另一只手会自然地跟随调整。求解器支持关节限制（旋转/位置自由度锁定或受限）、首选角度（让膝盖和肘部朝正确的方向弯曲）、刚度控制、子链预求解等高级功能。

## 使用场景

- 你需要角色的手或脚精确到达目标位置，同时保持全身姿态自然 → 使用 Full Body IK 的 Effectors
- 你在做 VR 全身追踪，需要将多个追踪点映射到骨骼 → 配置多个 Effectors 对应追踪点
- 你需要让角色适应不同高度的抓取或攀爬动作 → 设置 Effectors 的 PositionAlpha/StrengthAlpha 混合
- 你希望膝盖和肘部始终朝正确方向弯曲 → 使用 PreferredAngles 而非 RotationLimits
- 你需要处理部分身体的 IK（如仅上半身），同时锁定下半身 → 设置 RootBehavior 为 PinToInput 并排除下半身骨骼

## 蓝图用法

此插件主要通过 ControlRig 图表使用，而非传统蓝图。核心节点为 `FRigUnit_PBIK`，在 ControlRig 的 Rig Graph 中以 "Full Body IK" 节点呈现。

### 核心结构体

| 结构体 | 说明 |
|---|---|
| `FRigUnit_PBIK` | 主求解节点，配置根骨骼、效应器、骨骼设置和求解参数 |
| `FPBIKEffector` | 效应器定义，指定目标骨骼、目标变换、拉力强度和链深度 |
| `FPBIKBoneSetting` | 单根骨骼的约束设置，包括刚度、旋转限制和首选角度 |
| `FPBIKSolverSettings` | 全局求解器设置，包括迭代次数、质量乘数、根行为等 |
| `FRootPrePullSettings` | 根骨骼预拉伸设置，控制求解前的整体偏移 |
| `FPBIKDebug` | 调试绘制设置 |

### 核心枚举

| 枚举 | 说明 |
|---|---|
| `EPBIKRootBehavior` | 根骨骼行为：PrePull（预拉伸）、PinToInput（锁定输入姿势）、Free（自由运动） |
| `EPBIKLimitType` | 旋转限制类型：Free（自由）、Limited（受限范围）、Locked（锁定） |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Full Body IK` | 主求解节点，计算全身 IK 姿势 | `FRigUnit_PBIK` |

### 使用示例（ControlRig 图表描述）

1. 在 ControlRig 资产中添加 **Full Body IK** 节点
2. 设置 **Root** 为角色的根骨骼（如 `pelvis` 或 `spine_01`）
3. 在 **Effectors** 数组中添加效应器：
   - 设置 `Bone` 为目标骨骼名（如 `hand_r`、`foot_l`）
   - 设置 `Transform` 为目标世界变换
   - 调整 `PositionAlpha`（0=忽略目标位置，1=完全跟随目标位置）
   - 调整 `RotationAlpha`（0=忽略目标旋转，1=完全跟随目标旋转）
   - 调整 `StrengthAlpha`（控制效应器拉力强度）
4. 在 **BoneSettings** 中为需要约束的骨骼添加设置：
   - 为膝盖/肘部设置 `bUsePreferredAngles = true` 并指定弯曲方向
   - 为脊椎设置 `RotationStiffness` 防止过度扭曲
5. 调整 **Settings** 中的 `Iterations`（默认 20，复杂情况可提高）和 `RootBehavior`
6. 连接输入骨骼变换（来自动画姿势）和输出骨骼变换（用于最终渲染）

## C++ 用法

### 头文件引入

```cpp
#include "RigUnit_PBIK.h"
#include "PBIKSolver.h"
#include "PBIK_Shared.h"
```

### 基本用法

以下示例展示如何在 C++ 中直接使用 PBIK 求解器：

```cpp
// 来源: Public/Core/PBIKSolver.h
#include "PBIKSolver.h"

// 创建求解器实例
FPBIKSolver Solver;

// 添加骨骼到求解器（从根节点开始，按层级顺序）
int32 PelvisIdx = Solver.AddBone(
    FName("pelvis"),
    -1,                              // -1 表示根节点
    FVector(0, 0, 100),              // 初始位置
    FQuat::Identity,                 // 初始旋转
    true                             // 标记为求解器根
);

int32 SpineIdx = Solver.AddBone(
    FName("spine_01"),
    PelvisIdx,                       // 父骨骼索引
    FVector(0, 0, 120),
    FQuat::Identity,
    false
);

int32 HandRIdx = Solver.AddBone(
    FName("hand_r"),
    SpineIdx,
    FVector(50, 0, 130),
    FQuat::Identity,
    false
);

// 添加效应器（指定要被拉动的骨骼名）
int32 EffectorIdx = Solver.AddEffector(FName("hand_r"));

// 初始化求解器
Solver.Initialize();

// 设置每根骨骼的输入变换（通常来自动画姿势）
Solver.SetBoneTransform(PelvisIdx, PelvisTransform);
Solver.SetBoneTransform(SpineIdx, SpineTransform);
Solver.SetBoneTransform(HandRIdx, HandRTransform);

// 设置效应器目标
PBIK::FEffectorSettings EffSettings;
Solver.SetEffectorGoal(
    EffectorIdx,
    TargetPosition,                  // 目标位置
    TargetRotation,                  // 目标旋转
    EffSettings
);

// 配置求解器参数
FPBIKSolverSettings Settings;
Settings.Iterations = 20;
Settings.RootBehavior = EPBIKRootBehavior::PrePull;

// 执行求解
Solver.Solve(Settings);

// 获取求解结果
FTransform OutputTransform;
Solver.GetBoneGlobalTransform(PelvisIdx, OutputTransform);
```

### 进阶用法

以下示例展示如何在 ControlRig 中使用 PBIK Rig Unit，以及如何配置骨骼约束和首选角度：

```cpp
// 来源: Public/PBIK_Shared.h + Public/RigUnit_PBIK.h

// 配置骨骼约束 - 为膝盖设置首选角度和旋转限制
FPBIKBoneSetting KneeSetting;
KneeSetting.Bone = FName("calf_l");
KneeSetting.bUsePreferredAngles = true;
KneeSetting.PreferredAngles = FVector(0.f, -90.f, 0.f);  // 膝盖向后弯曲
KneeSetting.RotationStiffness = 0.1f;

// 限制 X 轴旋转范围
KneeSetting.X = EPBIKLimitType::Limited;
KneeSetting.MinX = -10.f;
KneeSetting.MaxX = 120.f;

// 锁定 Y/Z 轴旋转（防止膝盖侧弯）
KneeSetting.Y = EPBIKLimitType::Locked;
KneeSetting.Z = EPBIKLimitType::Locked;

// 配置效应器
FPBIKEffector FootEffector;
FootEffector.Bone = FName("foot_l");
FootEffector.Transform = FTransform(TargetRotation, TargetPosition);
FootEffector.PositionAlpha = 1.0f;    // 完全跟随目标位置
FootEffector.RotationAlpha = 0.5f;    // 部分跟随目标旋转
FootEffector.StrengthAlpha = 1.0f;    // 完整拉力
FootEffector.PullChainAlpha = 0.5f;   // 子链预旋转，加速收敛
FootEffector.PinRotation = 1.0f;      // 固定末端旋转
FootEffector.ChainDepth = 3;          // 显式指定链深度（3 根骨骼）

// 在 FRigUnit_PBIK 中组合使用
FRigUnit_PBIK PBIKNode;
PBIKNode.Root = FName("pelvis");
PBIKNode.Effectors.Add(FootEffector);
PBIKNode.BoneSettings.Add(KneeSetting);

// 配置全局求解器参数
PBIKNode.Settings.Iterations = 30;
PBIKNode.Settings.SubIterations = 5;         // 子链额外迭代，改善收敛
PBIKNode.Settings.MassMultiplier = 2.0f;     // 更高刚度
PBIKNode.Settings.bAllowStretch = false;     // 禁止骨骼拉伸
PBIKNode.Settings.RootBehavior = EPBIKRootBehavior::PrePull;
PBIKNode.Settings.PrePullRootSettings.RotationAlpha = 0.5f;
PBIKNode.Settings.PrePullRootSettings.PositionAlpha = 0.8f;
PBIKNode.Settings.GlobalPullChainAlpha = 0.7f;
PBIKNode.Settings.MaxAngle = 30.f;
PBIKNode.Settings.OverRelaxation = 1.3f;

// 排除不需要参与求解的骨骼（如手指）
PBIKNode.ExcludedBones.Add(FName("thumb_01_l"));
PBIKNode.ExcludedBones.Add(FName("index_01_l"));

// 启用调试绘制
PBIKNode.Debug.bDrawDebug = true;
PBIKNode.Debug.DrawScale = 1.0f;
```

## Demo 示例

以下为在自定义模块中集成 PBIK 求解器的最小示例：

```cpp
// MyPBIKComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PBIKSolver.h"
#include "PBIK_Shared.h"
#include "MyPBIKComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyPBIKComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyPBIKComponent();

    UPROPERTY(EditAnywhere, Category = "PBIK")
    FName RootBoneName = FName("pelvis");

    UPROPERTY(EditAnywhere, Category = "PBIK")
    TArray<FPBIKEffector> Effectors;

    UPROPERTY(EditAnywhere, Category = "PBIK")
    TArray<FPBIKBoneSetting> BoneSettings;

    UPROPERTY(EditAnywhere, Category = "PBIK")
    FPBIKSolverSettings SolverSettings;

    /** 手动构建并求解 IK */
    UFUNCTION(BlueprintCallable, Category = "PBIK")
    void SolveIK(const TArray<FTransform>& InputBoneTransforms, TArray<FTransform>& OutBoneTransforms);

protected:
    virtual void BeginPlay() override;

private:
    FPBIKSolver Solver;
    bool bInitialized = false;
    TMap<FName, int32> BoneNameToIndex;
};
```

```cpp
// MyPBIKComponent.cpp
#include "MyPBIKComponent.h"

UMyPBIKComponent::UMyPBIKComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    SolverSettings.Iterations = 20;
}

void UMyPBIKComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UMyPBIKComponent::SolveIK(const TArray<FTransform>& InputBoneTransforms, TArray<FTransform>& OutBoneTransforms)
{
    if (!bInitialized && InputBoneTransforms.Num() > 0)
    {
        // 构建骨骼层级（简化示例：假设已知骨骼顺序和父子关系）
        struct FBoneDef { FName Name; int32 ParentIndex; bool bIsRoot; };
        TArray<FBoneDef> BoneDefs;
        BoneDefs.Add({ RootBoneName, -1, true });
        // ... 添加其他骨骼定义

        for (int32 i = 0; i < BoneDefs.Num(); ++i)
        {
            int32 Idx = Solver.AddBone(
                BoneDefs[i].Name,
                BoneDefs[i].ParentIndex,
                InputBoneTransforms.IsValidIndex(i) ? InputBoneTransforms[i].GetLocation() : FVector::ZeroVector,
                InputBoneTransforms.IsValidIndex(i) ? InputBoneTransforms[i].GetRotation() : FQuat::Identity,
                BoneDefs[i].bIsRoot
            );
            BoneNameToIndex.Add(BoneDefs[i].Name, Idx);
        }

        // 添加效应器
        for (const FPBIKEffector& Eff : Effectors)
        {
            Solver.AddEffector(Eff.Bone);
        }

        if (Solver.Initialize())
        {
            bInitialized = true;
        }
    }

    if (!bInitialized) return;

    // 设置输入变换
    for (int32 i = 0; i < InputBoneTransforms.Num(); ++i)
    {
        Solver.SetBoneTransform(i, InputBoneTransforms[i]);
    }

    // 设置效应器目标
    int32 EffIdx = 0;
    for (const FPBIKEffector& Eff : Effectors)
    {
        PBIK::FEffectorSettings EffSettings;
        Solver.SetEffectorGoal(EffIdx, Eff.Transform.GetLocation(), Eff.Transform.GetRotation(), EffSettings);
        EffIdx++;
    }

    // 求解
    Solver.Solve(SolverSettings);

    // 收集输出
    OutBoneTransforms.SetNum(Solver.GetNumBones());
    for (int32 i = 0; i < Solver.GetNumBones(); ++i)
    {
        Solver.GetBoneGlobalTransform(i, OutBoneTransforms[i]);
    }
}
```

## 模块依赖

PBIK 模块依赖了 ControlRig 生态系统的多个模块。你需要在自己的 Build.cs 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `FullBodyIK` | 全身 IK 求解器核心模块 |
| `PBIK` | PBIK 求解器实现模块 |
| `ControlRig` | ControlRig 框架（运行时依赖，通过插件依赖自动引入） |

PBIK 模块的 Build.cs 中声明了对 `ControlRigDeveloper`、`ControlRigEditor`、`RigVMDeveloper`、`RigVMEditor` 的依赖，但这些主要是编辑器/开发工具依赖。作为使用者，你只需依赖 `FullBodyIK` 和 `PBIK` 模块即可。实际运行时所需的 ControlRig 依赖会通过插件依赖链自动解析（.uplugin 声明了对 ControlRig 插件的依赖）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复此前移除的调试属性 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码风格修正：析构函数改为 = default |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码风格修正：析构函数改为 = default |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复分叉关节上中间效应器导致的崩溃 |

### 维护评价

FullBodyIK 自 2020 年创建以来持续维护，虽然位于 `Experimental` 目录下，但 `.uplugin` 中 `IsExperimentalVersion` 和 `IsBetaVersion` 均为 `false`，说明 Epic 认为其已达到可用状态。近期更新主要是 bug 修复和代码风格维护，没有重大功能变更。插件作为 ControlRig 生态系统的核心 IK 求解方案之一，不太可能被废弃。推荐在需要全身 IK 的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [ControlRig 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-in-unreal-engine)