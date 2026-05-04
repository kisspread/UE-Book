# Control Rig Dynamics

> Support for simple dynamics/cosmetic simulation in control rig

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ControlRigDynamics` (Runtime), `ControlRigDynamicsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlRigDynamics) | |

## 用途

ControlRigDynamics 为 Control Rig 提供了一套**轻量级的粒子动力学模拟系统**，用于实现骨骼链的"装饰性"物理效果——如头发飘动、尾巴摇摆、衣物摆动、饰品晃动等。它不是完整的物理引擎替代方案，而是专注于在动画蓝图的 Control Rig 图中直接进行简单的动力学求解。

该插件解决的核心问题是：**在不依赖完整物理资产和物理模拟管线的情况下，让动画师和 Technical Artist 能够在 Control Rig 中快速添加基于物理的二级运动（secondary motion）**。它通过在 Rig 层级中添加"粒子（Particle）"组件来标记需要动力学驱动的骨骼，然后通过求解器（Solver）在每一帧进行模拟，最终将结果写回层级。

与传统物理资产方案相比，它的优势在于：
- 完全在 Control Rig VM 中运行，无需额外的物理资产和物理场景
- 支持碰撞器（Collider）、约束（Constraint）、锥形限制（Cone Limit）、围栏（Confiner）等丰富的动力学元素
- 提供曲线乘数（Chain Curves），可以沿骨骼链平滑地调整物理属性
- 支持模拟空间（Simulation Space）配置，适应不同角色运动场景

## 使用场景

- 你在做一个角色的头发/尾巴/披风需要自然飘动效果 → 用 ControlRigDynamics 在 Control Rig 中添加粒子链
- 你需要角色身上的饰品、武器挂件有轻微晃动 → 用 Spawn Dynamics Particle 为对应骨骼添加动力学粒子
- 你需要限制动力学骨骼的摆动角度，防止穿模 → 用 Cone Limit 和 Collider 组件
- 你需要让粒子保持在某个区域内（如衣服不超出身体轮廓） → 用 Confiner 组件
- 你想要沿骨骼链渐变调整物理参数（如发根硬、发梢软） → 用 ParticleChainCurves

## 蓝图用法

本插件的所有节点均为 **RigVM 节点**（USTRUCT with RIGVM_METHOD），在 Control Rig 蓝图编辑器中使用。节点分为可变（Mutable）和只读两类，可变节点需要连接到 Construction Event 或 Forward Solve 执行链。

### 核心节点

#### 求解器管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Dynamics Solver` | 在骨骼上创建动力学求解器组件（仅 Construction Event） | `FRigUnit_SpawnDynamicsSolver` |
| `Instantiate Dynamics` | 显式实例化动力学世界（可选，首次模拟会自动触发） | `FRigUnit_InstantiateDynamics` |
| `Step Dynamics Solver` | 推进一帧动力学模拟 | `FRigUnit_StepDynamicsSolver` |

#### 粒子管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Dynamics Particle` | 在骨骼上创建动力学粒子（仅 Construction Event） | `FRigUnit_SpawnDynamicsParticle` |
| `Disable Dynamics Collision With Collider` | 禁用粒子与指定碰撞器的碰撞 | `FRigUnit_HierarchyDisableDynamicsCollisionWithCollider` |
| `Allow Dynamics Collision With Collider` | 恢复粒子与指定碰撞器的碰撞 | `FRigUnit_HierarchyAllowDynamicsCollisionWithCollider` |
| `Set Dynamics Particle No-Collision Colliders` | 替换粒子的无碰撞碰撞器列表 | `FRigUnit_HierarchySetDynamicsParticleNoCollisionColliders` |

#### 碰撞器管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Dynamics Collider` | 在骨骼上创建碰撞器组件（仅 Construction Event） | `FRigUnit_SpawnDynamicsCollider` |
| `Set Dynamics Collider Box` | 设置碰撞器上的盒体形状属性 | `FRigUnit_HierarchySetDynamicsColliderBox` |
| `Set Dynamics Collider Capsule` | 设置碰撞器上的胶囊体形状属性 | `FRigUnit_HierarchySetDynamicsColliderCapsule` |
| `Set Dynamics Collider Plane` | 设置碰撞器上的平面形状属性 | `FRigUnit_HierarchySetDynamicsColliderPlane` |

#### 约束管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Dynamics Constraint` | 创建两个粒子间的距离约束（仅 Construction Event） | `FRigUnit_SpawnDynamicsConstraint` |
| `Set Dynamics Constraint Strength` | 设置约束的强度 | `FRigUnit_HierarchySetDynamicsConstraintStrength` |
| `Get Dynamics Constraint Strength` | 获取约束的强度 | `FRigUnit_HierarchyGetDynamicsConstraintStrength` |

#### 锥形限制管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Dynamics Cone Limit` | 创建三个粒子间的锥形角度限制（仅 Construction Event） | `FRigUnit_SpawnDynamicsConeLimit` |
| `Set Dynamics Cone Limit Strength` | 设置锥形限制的强度 | `FRigUnit_HierarchySetDynamicsConeLimitStrength` |
| `Get Dynamics Cone Limit Strength` | 获取锥形限制的强度 | `FRigUnit_HierarchyGetDynamicsConeLimitStrength` |

#### 围栏管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Dynamics Confiner` | 创建围栏组件，将粒子限制在形状内（仅 Construction Event） | `FRigUnit_SpawnDynamicsConfiner` |
| `Set Dynamics Confiner Box` | 设置围栏上的盒体形状属性 | `FRigUnit_HierarchySetDynamicsConfinerBox` |
| `Set Dynamics Confiner Capsule` | 设置围栏上的胶囊体形状属性 | `FRigUnit_HierarchySetDynamicsConfinerCapsule` |

### 使用示例（蓝图描述）

**基本头发动力学设置：**

1. 在 Control Rig 的 **Construction Event** 中，依次连接以下节点：
   - `Spawn Dynamics Solver` → Owner 设为 `Root` 骨骼，配置 Settings（重力、迭代次数等）
   - `Spawn Dynamics Particle` → Owner 设为每根头发链的根骨骼，DynamicsSolverComponentKey 连接上一步输出，配置 ParticleProperties（Radius=2, Mass=0.5, Strength=5, DampingRatio=0.7）
   - 对头发链的每个子骨骼重复 Spawn Dynamics Particle

2. 在 **Forward Solve** 中：
   - `Step Dynamics Solver` → 连接 Solver Component Key，Alpha 设为 1.0

**带碰撞的设置：**

1. 在 Construction Event 中额外添加：
   - `Spawn Dynamics Collider` → Owner 设为头部骨骼，添加一个 Capsule 形状包裹头部
   - 对每个头发粒子调用 `Allow Dynamics Collision With Collider`（或在 Spawn 时默认开启碰撞）

**沿链渐变参数：**

使用 `FParticleChainCurves` 结构中的曲线：
- `StrengthMultiplier`：从根到梢从 1.0 降到 0.3（发梢更软）
- `DampingRatioMultiplier`：从根到梢从 0.5 升到 1.0（发梢阻尼更大）

## C++ 用法

### 头文件引入

```cpp
#include "RigDynamicsSolverComponent.h"
#include "RigDynamicsParticleComponent.h"
#include "RigDynamicsColliderComponent.h"
#include "RigDynamicsConstraintComponent.h"
#include "RigDynamicsConeLimitComponent.h"
#include "RigDynamicsConfinerComponent.h"
#include "RigDynamicsSolver.h"
#include "RigDynamicsHelpers.h"
```

### 基本用法

从 `RigDynamicsSolver.h` 提取的求解器核心用法：

```cpp
// 创建求解器实例
FRigDynamicsSolver Solver(FName("MyDynamicsSolver"));

// 实例化：从层级中读取组件配置，创建模拟对象
Solver.Instantiate(ExecuteContext, Hierarchy, SolverComponent);

// 每帧推进模拟
// DeltaTimeOverride: >0 使用指定值，=0 使用执行上下文时间，<0 不推进
// Alpha: 模拟结果与原始动画的混合权重，<=0 时为纯跟踪模式
Solver.StepSimulation(
    ExecuteContext,
    Hierarchy,
    SolverComponent,
    OwningActorPtr,
    DeltaTimeOverride,      // 0.0f = 使用上下文时间
    SimSpaceDeltaTimeOverride, // 0.0f = 使用模拟 delta time
    Alpha,                  // 1.0f = 完全使用模拟结果
    bTrackVelocitiesDuringPassThrough
);

// 绘制调试形状
Solver.Draw(DrawInterface, Hierarchy, DebugWorld, VisualizationSettings);
```

### 进阶用法

**从层级中获取组件（使用 Helper 函数）：**

```cpp
// 来源: Private/RigDynamicsHelpers.h

// 获取粒子组件（带缓存）
const FRigDynamicsParticleComponent* Particle = GetParticle(Hierarchy, CachedComponent);

// 获取求解器组件
const FRigDynamicsSolverComponent* SolverComp = GetSolver(Hierarchy, ComponentKey);

// 获取碰撞器组件
const FRigDynamicsColliderComponent* Collider = GetCollider(Hierarchy, ComponentKey);

// 获取约束组件
const FRigDynamicsConstraintComponent* Constraint = GetConstraint(Hierarchy, ComponentKey);

// 获取锥形限制组件
const FRigDynamicsConeLimitComponent* ConeLimit = GetConeLimit(Hierarchy, ComponentKey);

// 获取围栏组件
const FRigDynamicsConfinerComponent* Confiner = GetConfiner(Hierarchy, ComponentKey);
```

**配置粒子属性：**

```cpp
// 来源: Public/RigDynamicsParticleComponent.h
FRigDynamicsParticleProperties Props;
Props.Radius = 5.0f;              // 碰撞半径（厘米）
Props.Mass = 1.0f;                // 质量（千克）
Props.MovementType = ERigParticleSimulationMovementType::Simulated;
Props.GravityMultiplier = 1.0f;   // 重力缩放
Props.Strength = 2.0f;            // 跟踪目标的强度（赫兹，振荡频率）
Props.DampingRatio = 0.5f;        // 阻尼比
Props.ExtraDamping = 0.0f;        // 额外阻尼（赫兹）
Props.Drag = 0.0f;                // 以太阻力（1/时间）
Props.TargetVelocityInfluence = 1.0f; // 目标速度对阻尼的影响
Props.TargetMode = 0.5f;          // 0=绝对跟踪, 1=方向跟踪, 中间值混合
Props.AngleLimit = 0.0f;          // 角度限制（度），0=不限制
Props.AngleLimitStrength = 0.0f;  // 角度限制强度（赫兹）
Props.bCollideWithColliders = true;
```

**配置碰撞形状：**

```cpp
// 来源: Public/RigDynamicsData.h
FRigDynamicsShapeCollection Shapes;

// 添加盒体
FRigDynamicsShapeBox Box(FName("HeadBox"), FTransform::Identity, FVector(20.f, 20.f, 25.f));
Shapes.Boxes.Add(Box);

// 添加胶囊体
FRigDynamicsShapeCapsule Capsule(FName("NeckCapsule"), FTransform::Identity, 8.f, 15.f);
Shapes.Capsules.Add(Capsule);

// 添加平面
FRigDynamicsShapePlane Plane(FName("Floor"), FTransform::Identity, FVector2D(100.f, 100.f));
Shapes.Planes.Add(Plane);
```

**模拟空间管理：**

```cpp
// 来源: Public/RigDynamicsSimulationSpace.h
FRigDynamicsSimulationSpaceState SpaceState;

// 更新模拟空间（DeltaTime > 0 时计算速度/加速度）
SpaceState.Update(Settings, ComponentTM, SimulationSpaceTM, DeltaTime);

// 坐标转换
FSimVector SimPos = SpaceState.ConvertComponentSpacePositionToSimSpace(ComponentPos);
FVector CompPos = SpaceState.ConvertSimSpacePositionToComponentSpace(SimPos);

// 获取模拟空间运动数据（用于传递给底层模拟）
FSimulationSpaceMotion Motion = SpaceState.CalculateMotion(Settings, DragSettings, AbsoluteTime);

// 检测传送（teleport）
bool bTeleported = SpaceState.WasTeleportDetectedInLastUpdate();
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何在自定义 RigVM 单元中使用动力学求解器：

```cpp
// MyDynamicsExample.h
#pragma once

#include "RigDynamicsSolverComponent.h"
#include "RigDynamicsParticleComponent.h"
#include "RigDynamicsSolver.h"
#include "RigDynamicsExecution.h"

#include "MyDynamicsExample.generated.h"

USTRUCT(meta = (DisplayName = "My Custom Dynamics Step"))
struct FMyRigUnit_CustomDynamicsStep : public FRigUnit_DynamicsBaseMutable
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;

    // 输入：求解器组件 Key
    UPROPERTY(meta = (Input, DisplayName = "Solver Component Key"))
    FRigComponentKey DynamicsSolverComponentKey;

    // 输入：混合权重
    UPROPERTY(meta = (Input, ClampMin = "0.0", ClampMax = "1.0"))
    float Alpha = 1.0f;
};
```

```cpp
// MyDynamicsExample.cpp
#include "MyDynamicsExample.h"
#include "RigDynamicsHelpers.h"
#include "Units/RigUnitContext.h"

void FMyRigUnit_CustomDynamicsStep::Execute()
{
    // 获取求解器组件
    const FRigDynamicsSolverComponent* SolverComp = 
        GetSolver(*ExecuteContext.Hierarchy, DynamicsSolverComponentKey);
    
    if (!SolverComp)
    {
        UE_CONTROLRIG_RIGUNIT_LOG_ERROR(TEXT("Invalid solver component key"));
        return;
    }

    // 获取底层求解器并推进一步
    FRigDynamicsSolver* Solver = SolverComp->GetDynamicsSolver();
    if (Solver)
    {
        Solver->StepSimulation(
            ExecuteContext,
            *ExecuteContext.Hierarchy,
            *SolverComp,
            nullptr,    // OwningActorPtr
            0.0f,       // DeltaTimeOverride (0 = use context time)
            0.0f,       // SimulationSpaceDeltaTimeOverride
            Alpha,
            false       // bTrackVelocitiesDuringPassThrough
        );
    }
}
```

## 模块依赖

从插件的 `.uplugin` 和源码 include 分析：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，提供 Rig 层级、组件系统、RigVM 执行框架 |
| `PhysicsControl` | 提供物理控制相关的底层支持 |
| `RigVM` | RigVM 虚拟机，执行 Control Rig 图 |
| `AnimationCore` | 动画核心数学工具 |

> 注：实际 Build.cs 未提供完整内容，以上依赖从 `.uplugin` 的 Plugins 字段和源码 include 推断。标准 Core/Engine/Slate 等依赖已省略。

## 维护状态

### 近期更新

由于该插件位于 `Engine/Plugins/Experimental/` 目录且为实验性插件，无法从提供的信息中获取具体 git log。基于源码版本历史（`FRigDynamicsObjectVersion`）可以看出该插件经历了大量迭代：

```
版本演进（从 FRigDynamicsObjectVersion 推断）：
- FirstVersion → ParticleExtraDamping → DynamicsTargetMode → GravityMultiplier
- PlaneDefinition → PlaneExtents → Constraints → HelperStructs
- BonePositionAndOrientationSetting → NoCollisionColliders → CollisionParticles
- TargetModeFloat → SimulationSpace → ConeLimits → AngleLimit
- ResetDetection → ParticleValueDisplay → ConstraintVisualization
- AngleLimitVisualization → CollideWithColliders → ParticleDrag
- DragSettings → Confiners → RemoveSolverLevelColliders
```

共 **24 个版本迭代**，说明该插件经历了持续的功能开发和重构。

### 维护评价

- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **代码成熟度**：24 个序列化版本说明经历了大量迭代，代码结构清晰，组件化设计良好
- **功能完整度**：支持粒子、碰撞器、约束、锥形限制、围栏等完整的动力学元素体系
- **已知限制**：
  - 碰撞器跟踪输入姿态而非模拟姿态，模拟骨骼上的碰撞器效果可能不理想
  - 仅支持简单的装饰性模拟，不适合替代完整物理引擎
  - 实验性插件，API 可能在未来版本中发生变化
- **推荐程度**：如果你需要在 Control Rig 中快速添加二级运动效果，这是一个非常实用的实验性插件。但需要注意实验性状态，生产环境使用需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ControlRigDynamics)
- [ControlRig 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)
- [PhysicsControl 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl)