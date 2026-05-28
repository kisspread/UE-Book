# Full Body IK

> *(Description 字段为空，基于源码分析)* 全身逆运动学（Full Body IK）求解器，基于雅可比矩阵（Jacobian）方法实现多链多效应器逆运动学，集成 ControlRig 系统，用于角色动画的逆运动学求解。

| 属性 | 值 |
|---|---|
| 中文名 | 全身逆运动学 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

FullBodyIK 是一个基于**雅可比矩阵**（Jacobian Matrix）的全身逆运动学求解器插件。它解决的核心问题是：给定角色骨骼链的末端目标位置/旋转，自动计算所有中间关节的旋转，使末端到达目标。

该插件提供两大核心能力：

1. **多链多效应器 IK 求解**：支持从单个根骨骼出发，同时求解多个末端效应器（如左右手、左右脚），适用于角色全身动画（如角色抓握、脚踩地面等场景）。
2. **多种雅可比求解器变体**：内置支持位置目标、旋转目标、组合目标的多种求解器，支持 3DOF（三自由度）和四元数（Quaternion）两种工作模式，可在精度和性能之间灵活权衡。

插件深度集成 ControlRig 系统，作为 ControlRig 的自定义 RigUnit 使用，直接在动画蓝图的 ControlRig 图表中操作骨骼层级。

**注意**：`FRigUnit_FullbodyIK` 已在 UE 5.0 中标记为 `Deprecated`，官方已推荐使用 PBIK 模块（Physic Based IK）作为替代方案。

## 使用场景

- 你需要角色双手同时抓握不同物体的全身 IK → 用 FullBodyIK 的多效应器设置
- 你需要角色脚部精确踩在不平坦地形上 → 用位置效应器（Position Effector）约束脚部位置
- 你需要角色转身时头部始终面向某个方向 → 用旋转效应器（Rotation Effector）约束头部朝向
- 你需要在 ControlRig 图表中实现全身动画混合 → 用 `FRigUnit_FullbodyIK` 节点
- 你需要对关节施加僵硬度约束（如肘部/膝盖不容易侧弯） → 用 `FFBIKConstraintOption` 配合极向量（Pole Vector）

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fullbody IK` | 全身 IK 求解主节点（ControlRig RigUnit） | `FRigUnit_FullbodyIK` |

### 关键输入参数

`FRigUnit_FullbodyIK` 通过 ControlRig 图表暴露以下输入：

| 参数 | 类型 | 说明 |
|---|---|---|
| `Root` | `FRigElementKey` | 骨骼链的根骨骼 |
| `Effectors` | `TArray<FFBIKEndEffector>` | 末端效应器列表，每个包含目标骨骼、位置/旋转目标、强度、深度 |
| `Constraints` | `TArray<FFBIKConstraintOption>` | 约束配置列表，每个骨骼可设置僵硬度、角度限制、极向量 |
| `SolverProperty` | `FSolverInput` | 求解器参数：迭代次数、阻尼、精度等 |
| `MotionProperty` | `FMotionProcessInput` | 运动处理参数：是否强制旋转目标等 |
| `bPropagateToChildren` | `bool` | 是否将变换传播到子骨骼 |
| `DebugOption` | `FFBIKDebugOption` | 调试绘制选项 |

### FFBIKEndEffector 效应器配置

每个效应器可配置：

- **Item**：目标骨骼名称
- **Position / PositionAlpha / PositionDepth**：位置目标、位置混合权重、影响深度
- **Rotation / RotationAlpha / RotationDepth**：旋转目标、旋转混合权重、影响深度
- **Pull**：拉力系数（0-1），控制效应器到目标的最大距离缩放，防止奇异点

### FFBIKConstraintOption 约束配置

每个骨骼的约束可配置：

- **LinearStiffness / AngularStiffness**：线性/角度僵硬度（0-1），限制关节移动自由度
- **bUseAngularLimit / AngularLimit**：是否启用角度限制及限制值
- **bUsePoleVector / PoleVector**：极向量，用于控制关节平面朝向（如膝盖朝向）

### 使用示例（ControlRig 图表描述）

在 ControlRig 图表中使用 FullBodyIK 的典型工作流：

1. 添加 `Fullbody IK` 节点到图表
2. 设置 `Root` 为角色的髋部骨骼（如 `pelvis`）
3. 配置 `Effectors` 数组：
   - 左手效应器：Item = `hand_l`，Position = 目标抓取位置，PositionAlpha = 1.0
   - 右手效应器：Item = `hand_r`，Position = 目标抓取位置，PositionAlpha = 1.0
   - 左脚效应器：Item = `foot_l`，Position = 地面接触点
   - 右脚效应器：Item = `foot_r`，Position = 地面接触点
4. 配置 `Constraints` 数组：
   - 膝盖骨骼（`calf_l`）设置极向量 `PoleVector = (1, 0, 0)` 引导膝盖朝前
   - 肘部骨骼设置 `AngularStiffness = (0, 0.8, 0.8)` 限制侧弯
5. 调整 `SolverProperty`：`MaxIterations = 10`，`Precision = 0.1`，`Damping = 30`

## C++ 用法

### 头文件引入

```cpp
#include "RigUnit_FullbodyIK.h"
#include "JacobianSolver.h"
#include "JacobianIK.h"
#include "FBIKConstraint.h"
#include "FBIKShared.h"
#include "FBIKConstraintOption.h"
```

### 基本用法

使用底层雅可比求解器直接求解 IK（不依赖 ControlRig）：

```cpp
// 来源: Public/JacobianSolver.h, Public/JacobianIK.h

// 1. 构建骨骼链数据
TArray<FFBIKLinkData> LinkData;
// ... 初始化 LinkData，设置 ParentLinkIndex, Length, Transform, MotionBaseAxes 等

// 2. 设置末端效应器目标
using namespace JacobianIK;
TMap<int32, FFBIKEffectorTarget> EndEffectors;
FFBIKEffectorTarget Effector;
Effector.bPositionEnabled = true;
Effector.Position = FVector(100.f, 0.f, 150.f);  // 目标位置
Effector.LinearMotionStrength = 0.8f;
Effector.ConvergeScale = 0.5f;
EndEffectors.Add(5, Effector);  // 链索引 5 为目标效应器

// 3. 配置求解器参数
JacobianIK::FSolverParameter SolverParam;
SolverParam.DampingValue = 10.f;
SolverParam.JacobianSolver = JacobianIK::EJacobianSolver::JacobianPIDLS;
SolverParam.bClampToTarget = true;
SolverParam.bUpdateClampMagnitude = true;

// 4. 创建求解器并执行
FJacobianSolver_PositionTarget_3DOF Solver;
TArray<FJacobianDebugData> DebugData;
bool bSuccess = Solver.SolveJacobianIK(
    LinkData,
    EndEffectors,
    SolverParam,
    30,       // 迭代次数
    1.0f,     // 容差
    &DebugData
);
```

### 进阶用法

使用自定义后处理委托（PostProcessDelegate）在每次迭代后应用约束：

```cpp
// 来源: Public/JacobianSolver.h

FJacobianSolver_PositionTarget_3DOF Solver;

// 设置迭代后处理回调 - 在每次求解迭代后应用约束
Solver.SetPostProcessDelegateForIteration(
    FPostProcessDelegateForIteration::CreateLambda(
        [](TArray<FFBIKLinkData>& InOutLinkData)
        {
            // 在这里应用自定义约束
            // 例如：限制关节角度、应用极向量约束等
            for (FFBIKLinkData& Link : InOutLinkData)
            {
                // 限制旋转幅度
                // ...
            }
        }
    )
);

// 执行求解
Solver.SolveJacobianIK(LinkData, EndEffectors, SolverParam);

// 用完后清理
Solver.ClearPostProcessDelegateForIteration();
```

## Demo 示例

基于 ControlRig 的最小使用示例（自定义 RigUnit 中调用 FullBodyIK）：

```cpp
// MyIKUnit.h
#pragma once

#include "CoreMinimal.h"
#include "Units/RigUnit.h"
#include "RigUnit_FullbodyIK.h"

USTRUCT(meta=(DisplayName="My Custom IK", Category="Custom"))
struct FMyIKUnit : public FRigUnit_HighlevelBaseMutable
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;

    UPROPERTY(meta = (Input, Constant, CustomWidget = "BoneName"))
    FRigElementKey RootBone;

    UPROPERTY(meta = (Input))
    TArray<FFBIKEndEffector> Effectors;

    UPROPERTY(transient)
    FRigUnit_FullbodyIK_WorkData WorkData;
};
```

```cpp
// MyIKUnit.cpp
#include "MyIKUnit.h"

void FMyIKUnit::Execute()
{
    // 该示例展示如何在自定义 RigUnit 中复用 FullBodyIK 的底层求解器
    // 实际使用建议直接使用 ControlRig 图表中的 Fullbody IK 节点

    // 1. 准备求解器
    WorkData.IKSolver = FJacobianSolver_FullbodyIK();

    // 2. 配置效应器（简化示意）
    WorkData.EffectorTargets.Reset();
    for (int32 i = 0; i < Effectors.Num(); ++i)
    {
        JacobianIK::FFBIKEffectorTarget Target;
        Target.bPositionEnabled = true;
        Target.Position = Effectors[i].Position;
        Target.LinearMotionStrength = Effectors[i].PositionAlpha;
        Target.bRotationEnabled = (Effectors[i].RotationAlpha > 0.f);
        Target.Rotation = Effectors[i].Rotation;
        WorkData.EffectorTargets.Add(i, Target);
    }

    // 3. 求解
    JacobianIK::FSolverParameter SolverParam;
    SolverParam.DampingValue = 30.f;
    SolverParam.JacobianSolver = JacobianIK::EJacobianSolver::JacobianPIDLS;

    WorkData.IKSolver.SolveJacobianIK(
        WorkData.LinkData,
        WorkData.EffectorTargets,
        SolverParam,
        10,   // 迭代次数
        0.1f  // 容差
    );

    // 4. 将结果写回骨骼层级
    // ... 通过 URigHierarchy 更新骨骼变换
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心动画蓝图集成框架（插件依赖） |
| `ControlRigDeveloper` | ControlRig 开发者工具（PBIK 模块） |
| `RigVMDeveloper` | RigVM 虚拟机开发者接口 |
| `Eigen` | 第三方线性代数库，用于雅可比矩阵计算（通过 ThirdPartyInclude 引入） |

## 求解器类层次

以下是 FullBodyIK 模块内置的雅可比求解器变体，按目标类型和运动自由度分类：

```
FJacobianSolverBase
├── FJacobianSolver_PositionTarget_3DOF          // 位置目标 + 3自由度旋转
│   ├── FJacobianSolver_RotationTarget_3DOF       // 旋转目标 + 3自由度
│   ├── FJacobianSolver_PositionRotationTarget_3DOF  // 位置+旋转目标 + 3自由度
│   └── FJacobianSolver_PositionTarget_3DOF_Translation  // 位置目标 + 平移关节
├── FJacobianSolver_PositionTarget_Quat           // 位置目标 + 四元数旋转
│   └── FJacobianSolver_PositionRotationTarget_Quat  // 位置+旋转目标 + 四元数
├── FJacobianSolver_RotationTarget_Quat           // 旋转目标 + 四元数
└── FJacobianSolver_PositionRotationTarget_LocalFrame  // 位置+旋转目标 + 自定义坐标系
```

**选择建议**：
- 一般骨骼链 IK → `PositionTarget_3DOF`（最常用）
- 需要头部朝向控制 → `PositionRotationTarget_3DOF`
- 对精度要求高、关节使用四元数表示 → 使用 `Quat` 变体
- 需要自定义关节局部坐标系（如特定僵硬度方向）→ `LocalFrame` 变体
- 性能敏感场景 → 使用 Jacobian Transpose 求解（`bUseJacobianTranspose = true`），代价是精度较低

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复之前被移除的调试属性 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 全局代码规范化：析构函数改用 = default |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码规范化：析构函数改用 = default |
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复分叉关节中间效应器导致的崩溃 bug |

### 维护评价

- **活跃程度**：维护不活跃。最近的实质性功能性更新（崩溃修复）在 2025-10-21，此后仅有代码规范化和日志迁移等机械性改动。
- **实验性状态**：位于 `Experimental` 目录下，虽 `IsExperimentalVersion=false`，但核心 RigUnit 已在 UE 5.0 标记为 `Deprecated`，官方推荐使用 PBIK 模块替代。
- **技术债务**：依赖第三方 Eigen 库进行线性代数计算，增加了编译复杂度。
- **建议**：⚠️ **不推荐用于新项目**。该插件的 `FRigUnit_FullbodyIK` 已废弃，建议使用 PBIK 模块。如需在此基础上做自定义开发，底层的 `FJacobianSolverBase` 类层次仍可参考，但需注意可能随版本移除。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- 测试用例：未在插件目录内发现独立测试文件