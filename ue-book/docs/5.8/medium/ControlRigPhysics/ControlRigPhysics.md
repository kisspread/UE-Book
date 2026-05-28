# Control Rig Physics

> Support for physics simulation in control rig

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定物理 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ControlRigPhysics` (Runtime), `ControlRigPhysicsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigPhysics) | |

## 用途

该插件在 ControlRig 动画系统中内嵌了一套完整的刚体物理模拟管线。它解决的核心问题是：**如何在动画图（RigVM Graph）中直接运行物理模拟，同时保持与骨骼层级的双向数据交换**。

它并非一个通用物理引擎，而是将 Chaos Immediate Physics 封装为 ControlRig 组件系统，使得用户可以通过蓝图节点在骨骼上创建物理体（Body）、关节（Joint）、控制（Control）和求解器（Solver），并在每帧的 ControlRig 求值中驱动模拟。典型应用场景包括布娃娃、次级运动（secondary motion）、物理驱动的头发/衣物/挂件，以及角色对环境的物理响应。

该插件最初是 PhysicsControl 插件的一部分，2025 年 6 月被拆分为独立插件（首条 commit 记录了这次迁移）。

## 使用场景

- 你在用 ControlRig 做角色动画，需要让某些骨骼在播放动画的同时产生物理晃动 → 用此插件创建 Physics Body + Physics Control
- 你需要让角色的头发/尾巴/挂件跟随动画骨骼运动，同时受重力和碰撞影响 → 用 `Instantiate From Physics Asset` 批量从物理资产创建
- 你需要角色在站立时有次级运动效果，但在摔倒时切换为完全布娃娃 → 用 `Step Physics Solver` 的 `Alpha` 参数在动画与物理之间平滑混合
- 你需要让物理模拟跟随角色移动而不产生相对速度偏移 → 将 SimulationSpace 设为 Component 或 Bone 而非 World
- 你需要精细控制物理体之间的碰撞关系 → 用 `Disable Collision Between` 节点
- 你需要在蓝图中查询物理体的速度/质心等状态 → 用 `Get Physics Body Linear Velocity` 等查询节点

## 蓝图用法

该插件的所有功能均通过 ControlRig RigVM 节点（USTRUCT with RIGVM_METHOD）暴露，而非传统蓝图节点。以下按功能分组。

### 求解器（Solver）节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Physics Solver` | 在骨骼上创建物理求解器组件，配置碰撞、空间设置等 | `FRigUnit_SpawnPhysicsSolver` |
| `Get Physics Solver Exists` | 检查指定 Solver 是否存在 | `FRigUnit_GetPhysicsSolverExists` |
| `Instantiate Physics` | 手动触发求解器实例化（通常自动发生） | `FRigUnit_InstantiatePhysics` |
| `Step Physics Solver` | 推进一帧物理模拟，控制 Alpha 混合与可视化 | `FRigUnit_StepPhysicsSolver1` |
| `Get Physics Solver Space Data` | 获取模拟空间的速度/加速度/重力数据 | `FRigUnit_GetPhysicsSolverSpaceData` |
| `Set Physics Solver Allow CCD` | 启用/禁用求解器的连续碰撞检测 | `FRigUnit_HierarchySetPhysicsSolverAllowCCD` |
| `Set Physics Solver Space Motion` | 设置模拟空间运动参数（速度/加速度限制、惯性力） | `FRigUnit_SetPhysicsSolverSpaceMotion` |
| `Set Physics Solver Teleport Detection` | 设置传送检测阈值 | `FRigUnit_SetPhysicsSolverTeleportDetection` |
| `Set Physics Solver World Collision` | 设置世界碰撞类型（无/静态/动态/全部） | `FRigUnit_SetPhysicsSolverWorldCollision` |
| `Set Physics Solver Collision Material` | 设置求解器级别的碰撞材质 | `FRigUnit_SetPhysicsSolverCollisionMaterial` |
| `Set Physics Solver Settings` | 设置求解器参数（重力、迭代次数等） | `FRigUnit_SetPhysicsSolverSettings` |
| `Reset Physics` | 重置求解器状态到动画姿态 | `FRigUnit_ResetPhysics` |
| `Track Input Pose` | 在仿真暂停后恢复时跟踪输入姿态若干帧 | `FRigUnit_TrackInputPose` |

### 物理体（Body）节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Physics Body` | 创建物理体组件（碰撞+动力学属性） | `FRigUnit_AddPhysicsBody` |
| `Get Physics Body Exists` | 检查物理体是否存在 | `FRigUnit_GetPhysicsBodyExists` |
| `Calculate Physics Collision` | 根据关节位置自动计算碰撞形状 | `FRigUnit_HierarchyAutoCalculateCollision` |
| `Set Physics Body Solver Settings` | 设置物理体的求解器关联（构造期） | `FRigUnit_HierarchySetBodySolverSettings` |
| `Set Physics Body Dynamics Properties` | 设置质量/惯性等动力学属性（构造期） | `FRigUnit_HierarchySetDynamics` |
| `Set Physics Body Collision Properties` | 设置碰撞形状（构造期） | `FRigUnit_HierarchySetCollision` |
| `Set Physics Body Material` | 设置碰撞材质（构造期） | `FRigUnit_HierarchySetPhysicsBodyMaterial` |
| `Set Physics Body Movement Mode` | 设置运动模式（Simulated/Kinematic） | `FRigUnit_HierarchySetPhysicsBodyMovementType` |
| `Set Physics Body Collision Mode` | 设置碰撞模式 | `FRigUnit_HierarchySetPhysicsBodyCollisionType` |
| `Set Physics Body Gravity Multiplier` | 设置重力倍率 | `FRigUnit_HierarchySetPhysicsBodyGravityMultiplier` |
| `Set Physics Body Physics Blend Weight` | 设置物理混合权重（每个体独立的 Alpha） | `FRigUnit_HierarchySetPhysicsBodyPhysicsBlendWeight` |
| `Set Physics Body Source Bone` | 设置动画源骨骼（运动学目标） | `FRigUnit_HierarchySetPhysicsBodySourceBone` |
| `Set Physics Body Target Bone` | 设置输出目标骨骼（构造期） | `FRigUnit_HierarchySetPhysicsBodyTargetBone` |
| `Set Physics Body Kinematic Target` | 设置运动学目标变换 | `FRigUnit_HierarchySetPhysicsBodyKinematicTarget` |
| `Set Physics Body Kinematic Target Space` | 设置运动学目标空间 | `FRigUnit_HierarchySetPhysicsBodyKinematicTargetSpace` |
| `Set Physics Body Include In Checks For Reset` | 设置是否参与重置检查 | `FRigUnit_HierarchySetPhysicsBodyIncludeInChecksForReset` |
| `Disable Collision Between` | 禁用两个物理体之间的碰撞（构造期） | `FRigUnit_HierarchyDisableCollisionBetween` |
| `Set Physics Body CoM Transform` | 获取物理体质心变换 | `FRigUnit_HierarchyGetPhysicsBodyCoMTransform` |
| `Get Physics Body Linear Velocity` | 获取物理体线速度 | `FRigUnit_HierarchyGetPhysicsBodyLinearVelocity` |
| `Get Physics Body Angular Velocity` | 获取物理体角速度 | `FRigUnit_HierarchyGetPhysicsBodyAngularVelocity` |
| `Get Physics Body Point Velocity` | 获取物理体某点速度 | `FRigUnit_HierarchyGetPhysicsBodyPointVelocity` |

### 关节（Joint）节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Physics Joint` | 创建物理关节组件 | `FRigUnit_AddPhysicsJoint` |
| `Get Physics Joint Exists` | 检查关节是否存在 | `FRigUnit_GetPhysicsJointExists` |
| `Set Physics Joint Properties` | 设置关节数据（限制/驱动） | `FRigUnit_HierarchySetJointData` |
| `Get Physics Joint Properties` | 获取关节数据 | `FRigUnit_HierarchyGetJointData` |
| `Set Physics Joint Linear Constraint Limit` | 设置线性约束限制 | `FRigUnit_HierarchySetJointLinearLimit` |
| `Set Physics Joint Cone Constraint Limit` | 设置锥形限制 | `FRigUnit_HierarchySetJointConeLimit` |
| `Set Physics Joint Twist Constraint Limit` | 设置扭转限制 | `FRigUnit_HierarchySetJointTwistLimit` |
| `Set Physics Joint Enabled` | 启用/禁用关节 | `FRigUnit_HierarchySetJointEnabled` |
| `Set Physics Joint Drive Properties` | 设置关节驱动属性 | `FRigUnit_HierarchySetJointDriveData` |
| `Get Physics Joint Drive Properties` | 获取关节驱动属性 | `FRigUnit_HierarchyGetJointDriveData` |
| `Set Physics Joint Drive Use Skeletal Animation` | 设置驱动是否跟踪动画姿态 | `FRigUnit_HierarchySetJointDriveUseSkeletalAnimation` |
| `Make Articulation Joint Data` | 快捷创建关节限制数据 | `FRigUnit_MakeArticulationJointData` |
| `Make Articulation Drive Data` | 快捷创建关节驱动数据 | `FRigUnit_MakeArticulationDriveData` |
| `Make Drive Data` | 快捷创建完整驱动数据 | `FRigUnit_MakeDriveData` |

### 控制（Control）节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Physics Control` | 创建物理控制组件 | `FRigUnit_AddPhysicsControl` |
| `Get Physics Control Exists` | 检查控制是否存在 | `FRigUnit_GetPhysicsControlExists` |
| `Set Physics Control Enabled` | 启用/禁用控制 | `FRigUnit_HierarchySetControlEnabled` |
| `Set Physics Control Custom Control Point` | 设置自定义控制点 | `FRigUnit_HierarchySetControlCustomControlPoint` |
| `Set Physics Control Data` | 设置控制强度等数据 | `FRigUnit_HierarchySetControlData` |
| `Get Physics Control Data` | 获取控制数据 | `FRigUnit_HierarchyGetControlData` |
| `Set Physics Control Linear Strength` | 设置线性强度 | `FRigUnit_HierarchySetControlLinearStrength` |
| `Set Physics Control Linear Damping Ratio` | 设置线性阻尼比 | `FRigUnit_HierarchySetControlLinearDampingRatio` |
| `Set Physics Control Angular Strength` | 设置角强度 | `FRigUnit_HierarchySetControlAngularStrength` |
| `Set Physics Control Angular Damping Ratio` | 设置角阻尼比 | `FRigUnit_HierarchySetControlAngularDampingRatio` |
| `Set Physics Control Target Velocity Multipliers` | 设置目标速度倍率 | `FRigUnit_HierarchySetControlTargetVelocityMultipliers` |
| `Set Physics Control Multiplier` | 设置控制乘子（各方向微调） | `FRigUnit_HierarchySetControlMultiplier` |
| `Set Physics Control Data And Multiplier` | 同时设置控制数据和乘子 | `FRigUnit_HierarchySetControlDataAndMultiplier` |
| `Set Physics Control Target` | 设置控制目标 | `FRigUnit_HierarchySetControlTarget` |
| `Update Physics Control Target` | 更新目标并自动计算目标速度 | `FRigUnit_HierarchyUpdateControlTarget` |

### 批量创建/导入节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Physics Components` | 一次性创建 Body + Joint + Controls | `FRigUnit_AddPhysicsComponents` |
| `Import Collision From Physics Asset` | 从物理资产导入碰撞形状并创建新骨骼 | `FRigUnit_HierarchyImportCollisionFromPhysicsAsset` |
| `Instantiate From Physics Asset` | 从物理资产批量创建完整物理组件集 | `FRigUnit_HierarchyInstantiateFromPhysicsAsset` |

### 使用示例（蓝图描述）

**基础用法：为单个骨骼添加物理晃动**

1. 在 Construction Event 中：放置 `Spawn Physics Solver` 节点，Owner 设为 Root 骨骼，获取 `PhysicsSolverComponentKey` 输出
2. 放置 `Spawn Physics Body` 节点，Owner 设为需要物理化的骨骼，将 Solver 引脚连接到步骤 1 的 Solver 输出
3. 放置 `Spawn Physics Control` 节点，Child Body 连接到步骤 2 的 Body，Parent Body 留空以使用默认全局控制
4. 在 Forwards Solve 中：放置 `Step Physics Solver` 节点，连接 Solver Component Key，Alpha 设为 1.0

**从物理资产批量创建（推荐方式）**

1. Construction Event 中：放置 `Spawn Physics Solver`，获取 Solver Key
2. 放置 `Instantiate From Physics Asset` 节点，Physics Solver Component Key 连接步骤 1 的输出，Physics Asset 选择你的 UPhysicsAsset，勾选 `bAddSimSpaceControl` 和/或 `bAddParentSpaceControl`
3. Forwards Solve 中：放置 `Step Physics Solver`

**暂停/恢复模拟**

1. 将 `Step Physics Solver` 的 `Alpha` 引脚连接到一个变量（0.0 = 暂停，1.0 = 恢复）
2. 当 Alpha 从 0 恢复时，`bTrackVelocitiesDuringPassThrough` 为 true 可以平滑恢复（持续跟踪速度），为 false 则执行短暂运动学预热

## C++ 用法

该插件的核心运行时逻辑在 `FRigPhysicsSolver` 中，但对插件使用者而言，主要的 C++ 交互方式是通过 ControlRig 组件系统读写物理组件数据。

### 头文件引入

```cpp
#include "RigPhysicsBodyComponent.h"
#include "RigPhysicsJointComponent.h"
#include "RigPhysicsControlComponent.h"
#include "RigPhysicsSolverComponent.h"
#include "RigPhysicsHelpers.h"
```

### 基本用法：获取物理组件

```cpp
// 基于 Private/RigPhysicsHelpers.h 的辅助函数

// 获取物理体组件
FRigPhysicsBodyComponent* BodyComp = GetPhysicsBody(Hierarchy, BodyComponentKey);
if (BodyComp)
{
    // 读取当前线速度
    FVector LinVel = BodyComp->LinearVelocity;
    // 读取质心变换
    FTransform CoM = BodyComp->CoMTransform;
    // 施加力（在下一帧被消费并清空）
    BodyComp->ForceAndTorques.Add(
        FPhysicsControlNamedForceAndTorqueData(FName("Wind"), Force, Torque));
}

// 获取物理关节组件
const FRigPhysicsJointComponent* JointComp = GetPhysicsJoint(Hierarchy, JointComponentKey);
if (JointComp)
{
    const FRigPhysicsJointData& JointData = JointComp->JointData;
    // 读取锥形限制
    const FConeConstraint& Cone = JointData.ConeConstraint;
}

// 获取物理控制组件
FRigPhysicsControlComponent* ControlComp = GetPhysicsControl(Hierarchy, ControlComponentKey);
if (ControlComp)
{
    // 读取控制强度
    FPhysicsControlData& Data = ControlComp->ControlData;
    Data.LinearStrength = 5.0f;
    ControlComp->DirtyFlags = ERigPhysicsControlComponentDirtyFlags::All; // 标记需同步
}
```

来源文件：`Engine/Plugins/Experimental/ControlRigPhysics/Source/ControlRigPhysics/Private/RigPhysicsHelpers.h`

### 进阶用法：操作求解器

```cpp
// 通过 SolverComponent 获取内部求解器实例
FRigPhysicsSolverComponent* SolverComp = Cast<FRigPhysicsSolverComponent>(
    Hierarchy.FindComponent(SolverComponentKey));
if (SolverComp)
{
    FRigPhysicsSolver* Solver = SolverComp->GetPhysicsSolver();
    if (Solver)
    {
        // 获取上一帧的模拟空间数据
        const FRigPhysicsSolver::FSimulationSpaceData& SpaceData = Solver->GetSimulationSpaceData();
        FVector SimLinearVel = SpaceData.LinearVelocity;
        FVector SimGravity = SpaceData.Gravity;
        
        // 获取求解器关联的组件 Key
        const FRigComponentKey& Key = Solver->GetSolverComponentKey();
    }
}
```

来源文件：`Engine/Plugins/Experimental/ControlRigPhysics/Source/ControlRigPhysics/Private/RigPhysicsSolver.h`

### 进阶用法：带缓存的组件查询

```cpp
// 使用 FCachedRigComponent 避免每帧 TMap 查找开销
// （RigPhysicsHelpers.h 中提供了缓存版本的 GetPhysicsBody/GetPhysicsJoint/GetPhysicsControl）
static FCachedRigComponent CachedBodyComponent;

// 带缓存的可变查询
FRigPhysicsBodyComponent* Body = GetPhysicsBody(Hierarchy, CachedBodyComponent);
if (Body)
{
    // 获取组件所有元素的全局变换（跳过 Key 查找）
    FTransform GlobalTM = GetGlobalTransform(Hierarchy, CachedBodyComponent);
}
```

来源文件：`Engine/Plugins/Experimental/ControlRigPhysics/Source/ControlRigPhysics/Private/RigPhysicsHelpers.h`

## Demo 示例

```cpp
// MyPhysicsRigUnit.h
#pragma once

#include "Units/RigUnit.h"
#include "RigPhysicsBodyComponent.h"
#include "RigPhysicsSolverComponent.h"
#include "RigPhysicsHelpers.h"

USTRUCT(meta = (DisplayName = "My Physics Demo", Category = "RigPhysics"))
struct FRigUnit_MyPhysicsDemo : public FRigUnitMutable
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;

    // 连接到 Solver 组件
    UPROPERTY(meta = (Input))
    FRigComponentKey SolverComponentKey;

    // 连接到 Body 组件
    UPROPERTY(meta = (Input))
    FRigComponentKey BodyComponentKey;

    // 输出当前线速度
    UPROPERTY(meta = (Output))
    FVector CurrentVelocity = FVector::ZeroVector;
};
```

```cpp
// MyPhysicsRigUnit.cpp
#include "MyPhysicsRigUnit.h"
#include "RigPhysicsSolver.h"
#include "RigHierarchy.h"

void FRigUnit_MyPhysicsDemo::Execute()
{
    FRigUnitMutable::Execute();
    URigHierarchy& Hierarchy = ExecuteContext.GetHierarchy();
    
    // 从 Body 组件读取线速度
    const FRigPhysicsBodyComponent* Body = GetPhysicsBody(Hierarchy, BodyComponentKey);
    if (Body)
    {
        CurrentVelocity = Body->LinearVelocity;
    }
    
    // 从 Solver 组件获取模拟空间信息
    const FRigPhysicsSolverComponent* SolverComp = 
        Cast<FRigPhysicsSolverComponent>(Hierarchy.FindComponent(SolverComponentKey));
    if (SolverComp)
    {
        FRigPhysicsSolver* Solver = SolverComp->GetPhysicsSolver();
        if (Solver)
        {
            const auto& SpaceData = Solver->GetSimulationSpaceData();
            // SpaceData.LinearVelocity  — 模拟空间线速度
            // SpaceData.Gravity         — 模拟空间重力
        }
    }
}
```

## 模块依赖

从 Build.cs 提取的依赖（仅列出独特/非常见依赖）：

| 模块 | 用途 |
|---|---|
| `ControlRig` | ControlRig 核心框架，提供 URigHierarchy、FRigVMExecuteContext、RigUnit 基类等 |
| `ControlRigDynamics` | ControlRig 动力学辅助模块 |
| `PhysicsControl` | 物理控制系统，提供 FPhysicsControlData、FPhysicsControlModifierData 等数据结构和底层物理控制 API |
| `ImmediatePhysics` | Chaos 即时物理库，用于在动画帧中执行物理模拟 |
| `Chaos` | Chaos 物理引擎核心，提供 FPBDJointSolverSettings 等关节求解参数 |
| `ChaosCore` | Chaos 核心类型定义 |
| `RigVM` | RigVM 虚拟机，驱动所有 RigUnit 节点的执行 |

> 编辑器模块 `ControlRigPhysicsEditor` 依赖 `ControlRigEditor`、`SkeletalMeshEditor`、`Kismet` 等编辑器模块，提供组件图标和编辑器集成。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `0fc3e074` | Anim In Engine: Run CR physics collisions on game thread, if we are currently on the game thread. This is needed as... | 修复游戏线程下物理碰撞检测，避免线程安全问题 |
| 2026-05-26 | `81eec0eb` | Fix for missing control rig physics version - fixes assert on loading older control rigs that don't have the ver... | 修复旧版 ControlRig 加载时缺少版本号导致的断言错误 |
| 2026-05-14 | `c6a1ed72` | Control rig physics - Remove SolverSettings.WorldCollisionExpiryFrames as a value of 1 is the only reasonable val... | 移除 WorldCollisionExpiryFrames 参数，因为唯一合理值是 1 |
| 2026-05-14 | `15fdc3a0` | Control rig physics - more uses of the cached components | 扩展组件缓存的使用范围，减少 TMap 查找开销 |
| 2026-05-14 | `c48042d4` | Control rig physics - use caching. Very simple change mirroring what we do in Control Rig Dynamics, for all the p... | 引入组件缓存机制（对标 ControlRigDynamics 的做法），优化物理组件查询性能 |

### 维护评价

**状态：活跃维护**

- 该插件创建于 2025 年 6 月，至今约 1 年，属于较新的实验性插件
- 最近更新集中在 2026 年 5 月，频繁进行性能优化（缓存机制）、API 清理（移除废弃参数）和兼容性修复（版本序列化）
- 标记为 `IsBetaVersion = true`，API 可能有 breaking changes
- 依赖 PhysicsControl 插件，存在多处 `Deprecated="5.8"` 的节点（如旧版 `FRigUnit_AddPhysicsSolver` 和 `FRigUnit_StepPhysicsSolver`），提供了升级路径（`GetUpgradeInfo`）
- 首条 commit 从 PhysicsControl 插件拆分而来，说明正在经历架构重组
- **推荐使用**用于实验性项目或内部原型；生产环境建议关注 API 稳定性，部分节点已被标记为废弃并提供替代节点

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigPhysics)
- [官方文档]()（暂无）
- [测试用例]()（未在源码中发现独立测试文件）