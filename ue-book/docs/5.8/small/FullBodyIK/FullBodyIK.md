# Full Body IK

> 

| 属性 | 值 |
|---|---|
| 中文名 | 全身逆运动学 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ControlRig 节点资产） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

FullBodyIK 是一个基于雅可比矩阵（Jacobian）方法的全身逆运动学求解器，集成于 ControlRig 框架中。它解决的核心问题是：**给定一个角色骨骼的根节点和多个末端执行器（End Effector）的目标位置/旋转，自动计算所有中间骨骼关节的旋转，使末端到达目标位置**。

与简单的 TwoBoneIK（只处理单条链如手臂/腿）不同，FullBodyIK 可以同时求解**多条骨骼链共享同一根节点**的 IK 问题，适用于：

- 全身接触地面的适配（不同地形高度）
- 双手抓取物体时的全身协调
- 交互式 IK（角色一只手扶墙，另一只手拿道具，同时保持平衡）

底层提供两种雅可比求解算法：
1. **Jacobian Pseudo Inverse Damped Least Square (JPIDLS)** — 默认，精度更高但计算开销更大
2. **Jacobian Transpose** — 更廉价，适合对性能敏感的场景

> **注意**：此插件中的 `FRigUnit_FullbodyIK` 已在 UE 5.0 标记为 `Deprecated`，推荐使用 ControlRig 内置的更新版 FullBodyIK 节点。

## 使用场景

- 你需要让角色在不平整地面上自然地调整全身姿态 → 用 FullBodyIK
- 你需要让角色双手同时抓握两个不同位置的物体 → 用 FullBodyIK 的多执行器支持
- 你只需要简单的手臂/腿 IK → 不需要此插件，用 TwoBoneIK 即可
- 你需要基于 ControlRig 的动画蓝图工作流 → 此插件提供对应的 RigUnit

## 蓝图用法

FullBodyIK 通过 ControlRig 的 `FRigUnit_FullbodyIK` 节点在动画蓝图中使用。该节点不是标准蓝图节点，而是在 ControlRig 图表中使用的 RigUnit。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fullbody IK` | 全身 IK 求解器节点（已废弃，5.0 后） | `FRigUnit_FullbodyIK` |

### 控制参数

#### FSolverInput（求解器参数）

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `LinearMotionStrength` | float | 3.0 | 线性运动强度，影响末端执行器对骨骼链的拉力 |
| `MinLinearMotionStrength` | float | 2.0 | 最小线性运动强度，用于沿链深度衰减 |
| `AngularMotionStrength` | float | 3.0 | 角度运动强度 |
| `MinAngularMotionStrength` | float | 2.0 | 最小角度运动强度 |
| `DefaultTargetClamp` | float | 0.2 | 目标钳制缩放（0-0.7），越小越稳定但收敛越慢 |
| `Precision` | float | 0.1 | 收敛精度阈值 |
| `Damping` | float | 30.0 | 阻尼值，减少振荡但增加迭代次数 |
| `MaxIterations` | int32 | 30 | 最大迭代次数（通常 4-16） |
| `bUseJacobianTranspose` | bool | false | 使用更廉价的 Jacobian Transpose 算法 |

#### FFBIKEndEffector（末端执行器）

| 属性 | 类型 | 说明 |
|---|---|---|
| `Item` | FRigElementKey | 链末端骨骼名 |
| `Position` | FVector | 目标世界位置 |
| `PositionAlpha` | float | 位置影响力（0-1） |
| `PositionDepth` | int32 | 位置影响沿链的深度 |
| `Rotation` | FQuat | 目标旋转 |
| `RotationAlpha` | float | 旋转影响力（0-1） |
| `RotationDepth` | int32 | 旋转影响沿链的深度 |
| `Pull` | float | 目标钳制缩放，防止奇异点 |

#### FFBIKConstraintOption（约束选项）

| 属性 | 类型 | 说明 |
|---|---|---|
| `Item` | FRigElementKey | 约束目标骨骼 |
| `bEnabled` | bool | 是否启用 |
| `LinearStiffness` | FVector | 线性刚度（XYZ，0-1），1=完全不动 |
| `AngularStiffness` | FVector | 角度刚度（Twist/Swing1/Swing2，0-1） |
| `bUseAngularLimit` | bool | 是否使用角度限制 |
| `AngularLimit` | FFBIKBoneLimit | 各轴角度限制类型与范围 |
| `bUsePoleVector` | bool | 是否使用极向量 |
| `PoleVector` | FVector | 极向量方向或位置 |
| `PoleVectorOption` | EPoleVectorOption | 极向量模式（局部方向/全局位置） |
| `OffsetRotation` | FRotator | 构建局部坐标系时的偏移旋转 |

### 使用示例（ControlRig 图表描述）

在 ControlRig 图表中：

1. 添加 `Fullbody IK` 节点
2. 设置 `Root` 为角色的根骨骼（如 `pelvis`）
3. 在 `Effectors` 数组中添加执行器：
   - 执行器 0：`Item` = `hand_r`，`Position` = 右手目标位置
   - 执行器 1：`Item` = `hand_l`，`Position` = 左手目标位置
4. 可选：在 `Constraints` 中为特定骨骼添加约束（如肘部的极向量、肩膀的角度限制）
5. 调整 `SolverProperty` 中的 `MaxIterations` 和 `Damping` 以平衡性能与精度

## C++ 用法

### 头文件引入

```cpp
#include "JacobianSolver.h"
#include "JacobianIK.h"
#include "FBIKConstraint.h"
```

### 基本用法

最简单的雅可比 IK 求解调用（来源：`Public/JacobianSolver.h`）：

```cpp
#include "JacobianSolver.h"
#include "JacobianIK.h"

using namespace JacobianIK;

// 准备骨骼链数据
TArray<FFBIKLinkData> LinkData;
// ... 填充 LinkData，每个代表一个关节

// 设置末端执行器目标
TMap<int32, FFBIKEffectorTarget> EndEffectors;
FFBIKEffectorTarget EffTarget;
EffTarget.bPositionEnabled = true;
EffTarget.Position = FVector(100.f, 0.f, 50.f); // 目标位置
EffTarget.LinearMotionStrength = 0.8f;
EffTarget.AngularMotionStrength = 0.5f;
EffTarget.ConvergeScale = 0.5f;
EndEffectors.Add(LinkData.Num() - 1, EffTarget); // 最后一个 link 作为末端

// 配置求解器参数
FSolverParameter SolverParam;
SolverParam.DampingValue = 10.f;
SolverParam.JacobianSolver = EJacobianSolver::JacobianPIDLS;
SolverParam.bClampToTarget = true;

// 创建求解器并求解
FJacobianSolver_PositionTarget_3DOF Solver;
bool bConverged = Solver.SolveJacobianIK(
    LinkData,
    EndEffectors,
    SolverParam,
    30,    // 最大迭代次数
    1.f    // 容差
);
```

### 进阶用法

使用约束系统配合求解器（来源：`Public/FBIKConstraintLib.h`、`Public/FBIKConstraint.h`）：

```cpp
#include "JacobianSolver.h"
#include "FBIKConstraint.h"
#include "FBIKConstraintLib.h"

// 构建约束
TArray<FFBIKConstraintOption> ConstraintOptions;
FFBIKConstraintOption ElbowConstraint;
ElbowConstraint.Item = FRigElementKey(TEXT("lowerarm_r"), ERigElementType::Bone);
ElbowConstraint.bUsePoleVector = true;
ElbowConstraint.PoleVectorOption = EPoleVectorOption::Direction;
ElbowConstraint.PoleVector = FVector::ForwardVector; // 极向量朝前
ElbowConstraint.bUseAngularLimit = true;
ElbowConstraint.AngularLimit.LimitType_Y = EFBIKBoneLimitType::Limit;
ElbowConstraint.AngularLimit.Limit.Y = 90.f; // 屈伸限制 90 度
ConstraintOptions.Add(ElbowConstraint);

// 使用后处理委托在每次迭代后应用约束
FJacobianSolver_PositionTarget_3DOF Solver;
Solver.SetPostProcessDelegateForIteration(
    FPostProcessDelegateForIteration::CreateLambda(
        [&LinkData, &Constraints](TArray<FFBIKLinkData>& InOutLinkData)
        {
            FBIKConstraintLib::ApplyConstraint(InOutLinkData, &Constraints);
        })
);

// 求解
Solver.SolveJacobianIK(LinkData, EndEffectors, SolverParam, 30, 1.f);
```

### 求解器选择指南

| 求解器类 | 目标类型 | 自由度 | 适用场景 |
|---|---|---|---|
| `FJacobianSolver_PositionTarget_3DOF` | 位置 | 3DOF 旋转 | 手臂/腿 IK |
| `FJacobianSolver_PositionTarget_Quat` | 位置 | 四元数旋转 | 更平滑的位置 IK |
| `FJacobianSolver_RotationTarget_3DOF` | 旋转 | 3DOF 旋转 | 注视/朝向控制 |
| `FJacobianSolver_RotationTarget_Quat` | 旋转 | 四元数旋转 | 更平滑的旋转目标 |
| `FJacobianSolver_PositionRotationTarget_3DOF` | 位置+旋转 | 3DOF 旋转 | 完整末端定位 |
| `FJacobianSolver_PositionRotationTarget_Quat` | 位置+旋转 | 四元数旋转 | 高精度末端定位 |
| `FJacobianSolver_PositionTarget_3DOF_Translation` | 位置 | 3DOF 平移 | 平移关节（非旋转） |
| `FJacobianSolver_PositionRotationTarget_LocalFrame` | 位置+旋转 | 自定义坐标系 | 自定义刚度方向 |

## Demo 示例

以下是一个最小可编译的 FullBodyIK 使用示例：

```cpp
// MyIKComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "JacobianSolver.h"
#include "JacobianIK.h"
#include "FBIKConstraint.h"
#include "MyIKComponent.generated.h"

using namespace JacobianIK;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyIKComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyIKComponent();

    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    FVector TargetPosition;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    float Damping = 10.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    int32 MaxIterations = 15;

protected:
    virtual void BeginPlay() override;

private:
    void InitializeLinkData();

    TArray<FFBIKLinkData> LinkData;
    TMap<int32, FFBIKEffectorTarget> EndEffectors;
    FJacobianSolver_PositionTarget_3DOF Solver;
};
```

```cpp
// MyIKComponent.cpp
#include "MyIKComponent.h"

UMyIKComponent::UMyIKComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyIKComponent::BeginPlay()
{
    Super::BeginPlay();
    InitializeLinkData();
}

void UMyIKComponent::InitializeLinkData()
{
    // 构建 3 关节链：根 → 中间 → 末端
    LinkData.SetNum(3);

    // 根关节
    LinkData[0].ParentLinkIndex = INDEX_NONE;
    LinkData[0].Length = 0.f;
    LinkData[0].SetTransform(FTransform::Identity);
    LinkData[0].AddMotionBase(FMotionBase(FVector(0, 0, 1))); // Z 轴旋转
    LinkData[0].AddMotionBase(FMotionBase(FVector(0, 1, 0))); // Y 轴旋转
    LinkData[0].AddMotionBase(FMotionBase(FVector(1, 0, 0))); // X 轴旋转

    // 中间关节
    LinkData[1].ParentLinkIndex = 0;
    LinkData[1].Length = 50.f;
    LinkData[1].SetTransform(FTransform(FRotator::ZeroRotator, FVector(0, 0, 50)));
    LinkData[1].AddMotionBase(FMotionBase(FVector(0, 0, 1)));
    LinkData[1].AddMotionBase(FMotionBase(FVector(0, 1, 0)));
    LinkData[1].AddMotionBase(FMotionBase(FVector(1, 0, 0)));

    // 末端关节
    LinkData[2].ParentLinkIndex = 1;
    LinkData[2].Length = 50.f;
    LinkData[2].SetTransform(FTransform(FRotator::ZeroRotator, FVector(0, 0, 50)));
    LinkData[2].AddMotionBase(FMotionBase(FVector(0, 0, 1)));
    LinkData[2].AddMotionBase(FMotionBase(FVector(0, 1, 0)));
    LinkData[2].AddMotionBase(FMotionBase(FVector(1, 0, 0)));

    // 末端执行器指向最后一个 link
    FFBIKEffectorTarget EffTarget;
    EffTarget.bPositionEnabled = true;
    EffTarget.Position = FVector(100.f, 0.f, 80.f);
    EffTarget.LinearMotionStrength = 0.8f;
    EffTarget.AngularMotionStrength = 0.5f;
    EffTarget.ConvergeScale = 0.5f;
    EndEffectors.Add(2, EffTarget);

    TargetPosition = EffTarget.Position;
}

void UMyIKComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 更新末端目标位置
    if (FFBIKEffectorTarget* Eff = EndEffectors.Find(2))
    {
        Eff->Position = TargetPosition;
    }

    // 配置求解器参数
    FSolverParameter SolverParam;
    SolverParam.DampingValue = Damping;
    SolverParam.JacobianSolver = EJacobianSolver::JacobianPIDLS;
    SolverParam.bClampToTarget = true;
    SolverParam.bUpdateClampMagnitude = true;

    // 执行 IK 求解
    Solver.SolveJacobianIK(
        LinkData,
        EndEffectors,
        SolverParam,
        MaxIterations,
        0.1f  // 容差
    );

    // LinkData 中的变换现在包含求解后的结果
    // 可以将结果写回骨骼组件
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | ControlRig 运行时框架，提供 RigUnit 基类和骨骼层级访问 |
| `ControlRigDeveloper` | ControlRig 开发者工具（PBIK 模块） |
| `RigVMDeveloper` | RigVM 虚拟机开发工具（PBIK 模块） |
| `Eigen` | 第三方线性代数库，用于雅可比矩阵运算（通过 ThirdParty 引入） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 日志宏 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复之前被移除的调试属性 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 将析构函数改为默认实现 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 将析构函数改为默认实现 |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复分叉关节中间执行器导致的崩溃 |

### 维护评价

- **创建时间**：2020 年 9 月，约 5 年历史
- **维护状态**：**维护中**。最近一次更新（2026-04）是全引擎范围的日志宏迁移；2025-11 和 2025-10 有实质性 bug 修复和功能恢复
- **废弃警告**：`FRigUnit_FullbodyIK` 在 UE 5.0 已标记 `Deprecated`，说明 Epic 可能正在将功能合并到 ControlRig 主模块中，或已有替代方案
- **实验性**：虽然文件位于 `Experimental` 目录，但 .uplugin 中 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 false
- **建议**：如果你需要基础的雅可比 IK 求解器库（纯 C++，不依赖 ControlRig），可以直接使用 `JacobianSolver.h` 和 `JacobianIK.h` 中的类。如果需要在 ControlRig 中使用全身 IK，建议检查 ControlRig 主模块是否已内置更新版的实现

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [RigUnit 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/FullBodyIK/Source/FullBodyIK/Private/RigUnit_FullbodyIK.h)