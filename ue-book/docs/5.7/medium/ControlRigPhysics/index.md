# ControlRigPhysics

> Support for physics simulation in control rig

| 属性 | 值 |
|---|---|
| 中文名 | 控制骨骼物理 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图、编辑器资源） |
| 模块 | `ControlRigPhysics` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlRigPhysics) | |

## 用途

`ControlRigPhysics` 插件在 Control Rig 框架内集成了物理模拟能力。它允许用户为 Control Rig 层级中的骨骼（或其他元素）附加物理体（Body）、物理关节（Joint）和物理控制器（Control），并通过求解器（Solver）进行驱动。

传统上，Control Rig 的动画是通过纯逻辑（约束、数学计算、曲线等）驱动骨骼，而该插件将 Chaos 物理引擎引入 Rig 中，使得骨骼可以拥有动态、碰撞、约束等物理行为。它解决了在 Control Rig 中实现物理布娃娃、悬挂系统、碰撞响应、混合动画-物理控制等场景的需求。

该插件是实验性的，旨在提供一种声明式的方式来定义物理组件，并在 Rig 的构造事件（Construction Event）中创建它们，然后在运行时更新。

## 使用场景

- **角色布娃娃 / 被动物理**：为角色的某一部分（如尾巴、头发、衣物）添加物理体，使其自然摆动、碰撞，同时保留主骨架的控制。
- **物理交互**：当角色与环境物体碰撞时，利用物理控制器驱动骨骼，产生真实的力学反馈。
- **混合动画与物理**：通过物理控制器（`PhysicsControl`）设定目标姿态，让物理体通过约束驱动接近动画目标，同时保持物理特性（惯性、碰撞）。
- **关节约束模拟**：为肢体添加带有限制和驱动的关节，模拟真实的铰链、弹簧等行为。

## 蓝图用法

插件中的物理节点主要在 Control Rig 的 **Event** 图中使用，通常放置于 **Construction Event**（创建组件）和 **Update** 事件（设置参数、启用/禁用）中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Physics Solver` | 在指定元素上创建物理求解器组件（必须优先创建） | `FRigUnit_AddPhysicsSolver` |
| `Spawn Physics Body` | 在指定元素上创建物理体组件（动态/运动学/碰撞） | `FRigUnit_AddPhysicsBody` |
| `Spawn Physics Joint` | 在指定元素上创建物理关节组件（连接两个体） | `FRigUnit_AddPhysicsJoint` |
| `Spawn Physics Control` | 在指定元素上创建物理控制组件（驱动体的运动） | `FRigUnit_AddPhysicsControl` |
| `Instantiate physics` | 显式实例化物理世界（自动在第一次步进时执行） | `FRigUnit_InstantiatePhysics` |
| `Calculate Physics Collision` | 自动根据骨骼位置计算物理体的碰撞形状（盒体） | `FRigUnit_HierarchyAutoCalculateCollision` |
| `Set Physics Body Enabled` | 启用/禁用物理体 | `FRigUnit_HierarchySetBodyEnabled` |
| `Set Physics Body Kinematic Target` | 设置运动学体的目标变换 | `FRigUnit_HierarchySetBodyKinematicTarget` |
| `Set Physics Joint Properties` | 设置关节的属性和驱动参数 | `FRigUnit_HierarchySetJointData` |
| `Set Physics Control Enabled` | 启用/禁用物理控制 | `FRigUnit_HierarchySetControlEnabled` |
| `Set Physics Control Target` | 设置物理控制的目标（位置/旋转/速度等） | `FRigUnit_HierarchySetControlTarget` |

### 使用示例（蓝图描述）

在 **Construction Event** 中：
1. 拖出 `Spawn Physics Solver`，将 `Owner` 连接到根骨骼（如 `root`），输出 `PhysicsSolverComponentKey`。
2. 拖出 `Spawn Physics Body`，将 `Owner` 连接到需要物理模拟的骨骼（如 `spine_03`），并将 `Solver` 的 `PhysicsSolverComponentKey` 连接到上一步的输出。设置 `Dynamics` 和 `Collision`。
3. 拖出 `Spawn Physics Joint`，将 `Owner` 连接到同一骨骼，设置 `ParentBodyComponentKey` 和 `ChildBodyComponentKey`（可选，可自动搜索）。
4. 拖出 `Spawn Physics Control`，设置 `ChildBodyComponentKey` 为刚创建的物理体，设定 `ControlData` 的初始强度，并将 `ControlTarget` 连接到驱动目标（如控制器的当前位置）。

在 **Update** 事件中，可拖出 `Set Physics Control Target` 来实时更新目标值，或使用 `Set Physics Body Kinematic Target` 混合动画。

> **注意**：这些节点仅在 **Construction Event** 中执行一次，除非标记为 `Varying`（变化节点）可在运行中修改。设置类节点（如 `Set Physics Body Enabled`）可以在任何事件中执行。

## C++ 用法

### 头文件引入

```cpp
#include "RigPhysicsExecution.h"        // 基类节点
#include "RigPhysicsBodyExecution.h"    // 物理体节点
#include "RigPhysicsControlExecution.h" // 物理控制节点
#include "RigPhysicsJointExecution.h"   // 物理关节节点
```

### 基本用法

在自定义的 Control Rig 单元（RigUnit）中，可以直接使用这些物理节点，或者通过操控层级组件（`URigHierarchy`）添加组件。

以下示例展示了如何在 C++ 中创建物理求解器和物理体，并设置参数（参考自 `RigPhysicsExecution.cpp` 和 `RigPhysicsBodyExecution.cpp`）：

```cpp
// 文件: ControlRigPhysics/Source/ControlRigPhysics/Private/RigPhysicsExecution.cpp (部分)
void FRigUnit_AddPhysicsSolver::Execute()
{
    // 获取 ControlRig 上下文
    if (const URigHierarchy* Hierarchy = ExecuteContext.Hierarchy)
    {
        // 创建求解器组件并附加到 Owner 元素
        // 内部调用 FControlRigPhysicsModule::AddComponentToElement(...)
    }
}

// 在自定义 RigUnit 中手动添加组件
void UMyRigUnit_Setup::Execute()
{
    URigHierarchy* Hierarchy = ExecuteContext.Hierarchy;
    if (!Hierarchy) return;
    
    // 在骨骼 "spine_03" 上创建物理求解器组件
    FRigElementKey SolverOwnerKey(ERigElementType::Bone, "spine_03");
    TUniquePtr<FRigPhysicsSolverComponent> SolverComponent = MakeUnique<FRigPhysicsSolverComponent>();
    // 设置求解器参数
    SolverComponent->SolverSettings = MySolverSettings;
    // 添加到层级
    Hierarchy->AddComponent(SolverOwnerKey, SolverComponent.Release());
}
```

### 进阶用法

组合使用多个物理组件实现复杂模拟。

```cpp
// 假设已在骨骼 "pelvis" 上创建了求解器组件 (FRigPhysicsSolverComponent)

// 在 "pelvis" 上创建物理体
FRigElementKey BodyOwnerKey(ERigElementType::Bone, "pelvis");
TUniquePtr<FRigPhysicsBodyComponent> Body = MakeUnique<FRigPhysicsBodyComponent>();
Body->BodySolverSettings.SolverComponentKey = FPhysicsSolverComponentKey(/* 之前创建的求解器组件键 */);
Body->Dynamics = FDynamics(/* 质量、阻尼等 */);
Body->Collision = FCollision(/* 碰撞形状 */);
Hierarchy->AddComponent(BodyOwnerKey, Body.Release());

// 创建关节连接 "pelvis" 和 "hip"
FRigElementKey JointOwnerKey(ERigElementType::Bone, "hip");
TUniquePtr<FRigPhysicsJointComponent> Joint = MakeUnique<FRigPhysicsJointComponent>();
Joint->ParentBodyComponentKey = FRigComponentKey(BodyOwnerKey, FRigPhysicsBodyComponent::GetDefaultName());
Joint->ChildBodyComponentKey = FRigComponentKey(JointOwnerKey, FRigPhysicsBodyComponent::GetDefaultName());  // 假设 hip 也有体
Joint->JointData = FJointData(/* 限制 */);
Joint->DriveData = FDriveData(/* 驱动 */);
Hierarchy->AddComponent(JointOwnerKey, Joint.Release());
```

## Demo 示例

以下是一个完整的 C++ Control Rig 单元，它在构造事件中为指定的骨骼添加物理模拟：

**MyPhysicsRigUnit.h**
```cpp
#pragma once

#include "Rigs/RigUnit.h"
#include "RigPhysicsExecution.h"
#include "RigPhysicsBodyExecution.h"
#include "RigPhysicsJointExecution.h"
#include "MyPhysicsRigUnit.generated.h"

/**
 * 演示：在根骨骼上创建物理求解器，并在指定骨骼上创建物理体
 */
USTRUCT(meta=(DisplayName="My Physics Setup", Keywords="Physics"))
struct FRigUnit_MyPhysicsSetup : public FRigUnit_PhysicsBaseMutable
{
    GENERATED_BODY()

    UPROPERTY(meta=(Input, BoneName))
    FRigElementKey RootBone;

    UPROPERTY(meta=(Input, BoneName))
    FRigElementKey SimulatedBone;

    UPROPERTY(meta=(Input))
    FRigPhysicsSolverSettings SolverSettings;

    UPROPERTY(meta=(Input))
    FRigPhysicsDynamics BodyDynamics;

    RIGVM_METHOD()
    virtual void Execute() override;
};
```

**MyPhysicsRigUnit.cpp**
```cpp
#include "MyPhysicsRigUnit.h"
#include "RigPhysicsBodyComponent.h"
#include "RigPhysicsSolverComponent.h"
#include "Rigs/RigHierarchy.h"
#include "Rigs/RigHierarchyController.h"

void FRigUnit_MyPhysicsSetup::Execute()
{
    // 仅允许在构造事件中运行
    if (!ExecuteContext.Hierarchy || !ExecuteContext.Controller) return;

    URigHierarchy* Hierarchy = ExecuteContext.Hierarchy;
    URigHierarchyController* Controller = ExecuteContext.Controller;

    // 在 RootBone 上创建物理求解器组件
    FRigComponentKey SolverKey;
    {
        TUniquePtr<FRigPhysicsSolverComponent> Solver = MakeUnique<FRigPhysicsSolverComponent>();
        Solver->SolverSettings = SolverSettings;
        SolverKey = Controller->AddComponent(RootBone, Solver.Release());
    }

    // 在 SimulatedBone 上创建物理体组件，并关联到求解器
    {
        TUniquePtr<FRigPhysicsBodyComponent> Body = MakeUnique<FRigPhysicsBodyComponent>();
        Body->BodySolverSettings.SolverComponentKey = SolverKey;
        Body->Dynamics = BodyDynamics;
        // 自动计算碰撞形状（可选）
        // Body->AutoCalculateCollision(Hierarchy);
        Controller->AddComponent(SimulatedBone, Body.Release());
    }
}
```

将此 RigUnit 添加到 Control Rig 的 `Construction Event` 中，并连接 `RootBone` 和 `SimulatedBone` 即可。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | Control Rig 框架核心（层级、单位、执行） |
| `PhysicsControl` | 物理控制数据结构（`PhysicsControlData.h`） |
| `Chaos` | 物理模拟核心（刚体、关节、碰撞） |
| `ImmediatePhysics` | 即时模式物理模拟（`ImmediatePhysicsSimulation`） |

> **注意**：`Core`, `Engine`, `Slate` 等标准依赖已省略。

## 维护状态

### 近期更新

- 2025-10-03 `081f8822`  — Control Rig Physics: Initialise data - fixes compiler warnings
- 2025-09-23 `b6e501bf`  — Minor fixes
- 2025-09-23 `f76fb35f`  — Physics Control: Align the KinematicTargetSpace usage
- 2025-09-08 `5d911b32`  — Control Rig Physics: Expose option to create controls relative to the parent vs world
- 2025-08-27 `af83ee57`  — Control Rig Physics: Expose enable/disable on the physics joints

### 维护评价

该插件为 **实验性**（实验标记为 `true`），创建于 2025 年 8 月，至今约 2 个月。从提交记录看，更新频率高（几乎每月都有功能添加和修复），且每次提交都是实质性修改（非仅编译修复）。目前处于积极开发阶段，推荐在需要物理集成的 Control Rig 项目中使用，但需注意 API 可能随版本变化。

## 相关链接

- [源码仓库](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlRigPhysics)
- [官方文档](https://docs.unrealengine.com/5.7/ControlRigPhysics)（暂时为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ControlRigPhysics/Source/ControlRigPhysics/Private/RigPhysicsSimulation.h)（主要代码位于此）