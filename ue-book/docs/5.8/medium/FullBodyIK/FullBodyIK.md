# Full Body IK

> （基于源码分析）这是一个基于雅可比矩阵的全身逆运动学（IK）解算器。它旨在为复杂的角色动画提供精确、可控的全身IK解决方案，特别是当需要同时控制多个末端执行器（如双手、双脚）并受到各种物理约束时。

| 属性 | 值 |
|---|---|
| 中文名 | 全身IK |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（控制绑定节点） |
| 模块 | `FullBodyIK` (Runtime), `PBIK` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK) | |

## 用途

`FullBodyIK` 是一个专业的、基于雅可比矩阵的逆运动学（IK）求解器，专为复杂角色动画设计。与简单的两骨IK或FABRIK不同，它能够处理具有多个末端执行器（Effectors）的全身骨骼链，并在迭代求解过程中综合考虑位置、旋转目标和各种关节约束（如角度限制、极向量等）。

该插件的核心价值在于：
1.  **多链求解**：能够从一个根骨骼（Root）开始，同时求解连接到多个末端执行器的整个骨骼层级。
2.  **精确控制**：通过雅可比伪逆阻尼最小二乘法（JPIDLS）或雅可比转置等算法，实现精确的位置和旋转目标跟随。
3.  **丰富的约束**：支持关节角度限制、线性/角刚度、极向量约束等，用于模拟真实的物理限制和动画意图。
4.  **与Control Rig深度集成**：作为 `ControlRig` 插件的扩展，其主要使用方式是通过 `RigUnit` 节点在动画蓝图或Control Rig图表中使用，便于集成到现有动画流程。

它主要解决高级角色动画中的问题，例如：精确地将角色的手或脚放到指定位置（如攀爬、抓取），同时确保身体其他部分自然协调，并且关节不会反向弯曲。

## 使用场景

- 你需要一个角色精确地抓取场景中的物体，同时保持身体平衡。
- 你在制作电影级过场动画，需要角色的手脚精确地与环境互动（如扶墙、踩台阶）。
- 你在开发 VR 应用，需要根据用户手柄位置实时驱动虚拟化身的手部，同时考虑肘部和肩膀的物理约束。
- 你需要为游戏中的AI角色实现动态的、基于物理的攀爬或互动动画。

## 蓝图用法

此插件主要通过 `ControlRig` 暴露给蓝图。在 Control Rig 图表或动画蓝图的 `Control Rig` 节点中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fullbody IK` | 全身IK解算主节点。输入根骨骼、多个末端执行器和约束，输出求解后的骨骼姿态。 | `FRigUnit_FullbodyIK` |

### 使用示例（蓝图描述）

1.  **在Control Rig图表中**：从节点面板拖入 `Fullbody IK` 节点。
2.  **配置根骨骼**：将 `Root` 输入引脚连接到你的角色骨架的根骨骼（如 `pelvis` 或 `root`）。
3.  **配置末端执行器**：在 `Effectors` 数组中添加元素。每个元素代表一个IK目标（如右手、左脚）。为每个执行器：
    *   设置 `Item` 为对应的骨骼名称（如 `hand_r`）。
    *   将 `Position` 和 `Rotation` 连接到代表目标位置和旋转的变量或计算节点。
    *   调整 `PositionAlpha` 和 `RotationAlpha` 来混合原始动画与IK结果。
    *   调整 `Pull` 来影响IK拉力。
4.  **配置约束（可选）**：在 `Constraints` 数组中为特定骨骼添加约束。例如，为膝盖骨骼添加 `Angular Limit` 来防止反向弯曲。
5.  **调整求解器参数**：通过 `SolverProperty` 和 `MotionProperty` 调整迭代次数、阻尼、是否强制旋转等，以获得理想的解算效果和性能。
6.  **连接输出**：节点的输出可以直接用于更新角色姿态。

## C++ 用法

此插件的核心算法以C++实现，主要通过 `FRigUnit_FullbodyIK` 结构体与 `ControlRig` 系统交互。

### 头文件引入

```cpp
#include "ControlRig.h" // 因为 FullBodyIK 依赖并扩展 ControlRig
#include "Units/Highlevel/RigUnit_FullbodyIK.h" // 如果需要直接操作底层结构体
```

### 基本用法

底层使用通常发生在自定义 `RigUnit` 或需要直接调用IK解算器的高级场景。基础类是 `FJacobianSolverBase`。
*（注：以下为简化示例，实际使用需构造完整的 `FFBIKLinkData` 和 `FFBIKEffectorTarget` 数据）*

```cpp
// 假设我们已经构建好了骨骼链数据和末端执行器目标
TArray<FFBIKLinkData> LinkData; // 包含所有关节信息
TMap<int32, FFBIKEffectorTarget> EndEffectors; // 键是 LinkData 索引，值是目标
JacobianIK::FSolverParameter SolverParam; // 求解器参数

// 选择一个求解器，例如位置+旋转目标的3DOF版本
FJacobianSolver_PositionRotationTarget_3DOF Solver;
Solver.SetPostProcessDelegateForIteration(MyConstraintDelegate); // 可选：设置每轮迭代后的约束处理委托

// 执行求解
bool bSuccess = Solver.SolveJacobianIK(LinkData, EndEffectors, SolverParam, 30, 0.1f);

if (bSuccess)
{
    // 求解成功，LinkData 中的 Transform 已被更新
}
```
*（来源：基于 `Public/JacobianSolver.h` 中类结构的推断用法）*

### 进阶用法

结合约束系统，可以构建更完整的求解流程。

```cpp
#include "FBIKConstraintLib.h"

// 1. 构建约束数据（通常从资产或配置读取）
TArray<ConstraintType> Constraints;
const URigHierarchy* Hierarchy = /* ... 获取骨骼层级 ... */;
TMap<int32, FRigElementKey> LinkDataToHierarchyIndices; // 需要建立索引映射
TMap<FRigElementKey, int32> HierarchyToLinkDataMap;
FBIKConstraintLib::BuildConstraints(ConstraintOptions, Constraints, Hierarchy, LinkData, LinkDataToHierarchyIndices, HierarchyToLinkDataMap);

// 2. 在求解器的迭代委托中应用约束
Solver.SetPostProcessDelegateForIteration(FPostProcessDelegateForIteration::CreateLambda(
    [&Constraints](TArray<FFBIKLinkData>& InOutLinkData)
    {
        FBIKConstraintLib::ApplyConstraint(InOutLinkData, &Constraints);
    }
));

// 3. 执行求解
Solver.SolveJacobianIK(...);
```
*（来源：综合 `Public/FBIKConstraintLib.h` 和 `JacobianSolver.h` 的用法）*

## Demo 示例

以下是一个基于 `FRigUnit_FullbodyIK` 的最小使用示例，展示了如何在你的代码中构造并调用这个Rig Unit。

```cpp
// MyFullBodyIKExample.h
#pragma once
#include "Units/Highlevel/RigUnit_FullbodyIK.h" // 包含核心结构体定义

class FMyFullBodyIKProcessor
{
public:
    void ProcessAnimation(USkeletalMeshComponent* MeshComponent);

private:
    FRigUnit_FullbodyIK FullbodyIKUnit;
    FRigUnit_FullbodyIK_WorkData WorkData;
};
```

```cpp
// MyFullBodyIKExample.cpp
#include "MyFullBodyIKExample.h"
#include "RigVMFunctions/Math/RigVMFunction_MathTransform.h" // 用于坐标变换

void FMyFullBodyIKProcessor::ProcessAnimation(USkeletalMeshComponent* MeshComponent)
{
    if (!MeshComponent || !MeshComponent->GetSkeletalMeshAsset())
        return;

    // 假设你已经有了目标位置和旋转
    FVector RightHandTargetPos = FVector(100.f, 50.f, 120.f);
    FQuat RightHandTargetRot = FQuat::Identity;

    // 1. 配置 RigUnit
    FullbodyIKUnit.Root = FRigElementKey(FName("pelvis"), ERigElementType::Bone);
    
    // 配置右手末端执行器
    FFBIKEndEffector& RightHandEff = FullbodyIKUnit.Effectors.AddDefaulted_GetRef();
    RightHandEff.Item = FRigElementKey(FName("hand_r"), ERigElementType::Bone);
    RightHandEff.Position = RightHandTargetPos;
    RightHandEff.Rotation = RightHandTargetRot;
    RightHandEff.PositionAlpha = 1.f; // 100% 向目标移动
    RightHandEff.RotationAlpha = 1.f; // 100% 向目标旋转

    // 2. 配置约束（可选，此处省略详细配置）
    // FullbodyIKUnit.Constraints.Add(...);

    // 3. 配置求解器参数
    FullbodyIKUnit.SolverProperty.MaxIterations = 15;
    FullbodyIKUnit.SolverProperty.Precision = 0.5f;

    // 4. 执行（在实际应用中，这通常在动画更新回调中，通过RigVM执行）
    // 注意：直接调用 Execute() 需要正确的上下文。更常见的用法是在Control Rig图表中。
    // 这里仅为演示数据结构的使用。
    FullbodyIKUnit.WorkData = WorkData; // 传入工作数据以复用内存
    // FullbodyIKUnit.Execute(); // 实际执行需要RigVM上下文

    // 5. 从 WorkData 中获取结果用于调试或其他处理
    // for (const FFBIKLinkData& Link : WorkData.LinkData)
    // {
    //     // Link.GetTransform() 包含了求解后的骨骼变换
    // }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供骨骼层级、Rig Unit 框架和动画蓝图集成接口。 |
| `AnimationCore` | 提供基础的动画数据类型（如 `FTransform`, `FQuat`）和约束系统基础。 |
| `RigVM` | Rig Unit 的虚拟机执行环境。 |

*注：`PBIK` 模块的具体依赖在提供的信息中不完整，但其功能可能与物理驱动的IK相关，作为 `FullBodyIK` 的补充或变体。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-21 | `8555965b` | [FBIK] Fixed crash bug from intermediate effectors on fork joints. | 修复了在分叉关节处使用中间末端执行器时发生的崩溃问题。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 将析构函数从空函数体改为 `= default`，属于代码现代化清理。 |
| 2025-11-21 | `3c12f7ef` | [FBIK] Added back previously removed debug properties. | 恢复了之前移除的调试属性，改善了调试功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移到 `UE_LOGF`，可能涉及日志格式或宏的更新。 |

### 维护评价

- **维护状态**：**维护中**。
- **年龄**：约6年，属于成熟的插件。
- **更新频率**：近期（6个月内）仍有实质性更新，包括关键的崩溃修复和功能恢复，表明 Epic 仍在积极维护和修复问题。
- **已知限制**：
    1.  `FRigUnit_FullbodyIK` 结构体在源码中标记为 `Deprecated = “5.0”`，意味着它可能在未来版本中被替代或重构。
    2.  作为 `Experimental` 目录下的插件，其 API 和功能的稳定性可能低于正式插件，使用时需关注版本更新日志。
- **推荐使用**：对于需要专业、可控全身IK的项目（特别是使用 Control Rig 工作流），这是一个非常强大和推荐的选择。尽管有废弃标记，但在当前版本（UE5）中仍然是功能完整且被维护的。建议关注其后续版本，以了解是否有新的替代方案（如增强的 `FullBodyIK` 模块或新的 `ControlRig` 节点）出现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FullBodyIK/Tests) (假设存在，路径需确认)