# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是 UE5 基于 Chaos 物理引擎的**布料模拟系统**，负责为骨骼网格体（SkeletalMesh）上的布料资产提供实时物理模拟。它取代了旧版的 NvCloth 方案，作为 UE5 Chaos 物理框架的一部分，与 Chaos 刚体、破碎等系统共享同一物理后端。

这个 plugin 解决的核心问题：**角色衣物、旗帜、披风等柔性物体的实时物理模拟**。它提供了一个完整的 cloth 模拟管线——从网格输入、蒙皮、约束求解、碰撞检测到最终渲染数据输出——全部在 Chaos 物理框架内完成。

### 架构概览

ChaosCloth 的模拟管线如下：

```
USkeletalMeshComponent
  → UChaosClothingSimulationFactory (创建模拟实例)
    → FClothingSimulation (模拟管理器)
      → FClothingSimulationSolver (求解器，管理所有布料实例)
        → FClothingSimulationCloth (单个布料实例)
          → FClothingSimulationMesh (网格输入，提供蒙皮后顶点位置)
          → FClothingSimulationCollider (碰撞体)
          → FClothConstraints (各种约束)
```

系统支持两种求解器后端：
- **PBD（Position-Based Dynamics）**：传统的位置动力学求解器，速度快但精度较低
- **Force-based（Evolution）**：基于力的隐式求解器，精度更高，支持更复杂的约束（如 Gauss-Seidel、Corotated Codimensional 等）

### 关键设计特点

1. **Weight Map 系统**：通过 `FChaosClothWeightedValue` 结构，每个约束参数都可以通过 Weight Map（0-1 范围的 per-vertex 权重图）进行空间变化控制。Low 值对应权重 0，High 值对应权重 1。

2. **LOD 支持**：布料模拟完整支持多 LOD，包括 LOD 切换时的形状过渡（WrapDeformLOD）。

3. **Accessory Mesh**：支持附加网格（Accessory Mesh），允许在同一模拟中使用额外的网格数据输入。

4. **ISPC 优化**：关键路径（如 GetSimData、SkinPhysicsMesh）使用 Intel ISPC 进行 SIMD 优化。

## 使用场景

- 你在做一个角色扮演游戏，角色有长袍、披风 → 用 ChaosCloth 模拟衣物物理
- 你需要旗帜、窗帘等环境布料物体 → 用 ChaosCloth 配合固定点约束
- 你希望布料与角色身体正确碰撞 → ChaosCloth 支持从 PhysicsAsset 提取碰撞体
- 你需要在运行时通过蓝图动态调整布料参数 → 用 `UChaosClothingInteractor`
- 你需要将布料模拟结果缓存并回放 → ChaosCloth 集成了 ChaosCaching 系统

## 蓝图用法

ChaosCloth 通过 `UChaosClothingInteractor` 类暴露蓝图接口。获取 interactor 的标准方式是通过 `USkeletalMeshComponent` 的 `GetClothingSimulationInteractor()` 方法。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterial` | 设置边缘/弯曲/面积刚度（带 Low/High 权重范围） | `UChaosClothingInteractor` |
| `SetMaterialLinear` | 设置边缘/弯曲/面积刚度（线性单一值） | `UChaosClothingInteractor` |
| `SetMaterialBuckling` | 设置弯曲屈曲刚度和比率 | `UChaosClothingInteractor` |
| `SetLongRangeAttachment` | 设置长距离附着约束（防止过度拉伸） | `UChaosClothingInteractor` |
| `SetLongRangeAttachmentLinear` | 设置长距离附着（线性单一值） | `UChaosClothingInteractor` |
| `SetCollision` | 设置碰撞厚度、摩擦系数、CCD、自碰撞厚度 | `UChaosClothingInteractor` |
| `SetBackstop` | 启用/禁用背停约束（防止布料穿透身体） | `UChaosClothingInteractor` |
| `SetDamping` | 设置全局和局部阻尼系数 | `UChaosClothingInteractor` |
| `SetWind` | 设置空气动力学参数（阻力、升力、空气密度、风速） | `UChaosClothingInteractor` |
| `SetAerodynamics` | 设置空气动力学（旧接口，推荐用 SetWind） | `UChaosClothingInteractor` |
| `SetPressure` | 设置压力强度（正=向外推，负=向内推） | `UChaosClothingInteractor` |
| `SetGravity` | 设置重力缩放和重力覆盖 | `UChaosClothingInteractor` |
| `SetAnimDrive` | 设置动画驱动刚度和阻尼（布料跟随动画的程度） | `UChaosClothingInteractor` |
| `SetAnimDriveLinear` | 设置动画驱动刚度（线性单一值） | `UChaosClothingInteractor` |
| `SetVelocityScale` | 设置线性/角速度缩放和虚拟角力缩放 | `UChaosClothingInteractor` |
| `SetVelocityClamps` | 设置线性/角速度和加速度的最大值限制 | `UChaosClothingInteractor` |
| `ResetAndTeleport` | 重置布料状态或传送布料 | `UChaosClothingInteractor` |

### 求解器级控制节点（UChaosClothingSimulationInteractor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNumIterations` | 设置求解器迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetMaxNumIterations` | 设置最大迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetNumSubsteps` | 设置子步数 | `UChaosClothingSimulationInteractor` |
| `EnableGravityOverride` | 启用重力覆盖 | `UChaosClothingSimulationInteractor` |
| `DisableGravityOverride` | 禁用重力覆盖 | `UChaosClothingSimulationInteractor` |
| `PhysicsAssetUpdated` | 通知物理资产已更新 | `UChaosClothingSimulationInteractor` |
| `ClothConfigUpdated` | 通知布料配置已更新 | `UChaosClothingSimulationInteractor` |

### 使用示例（蓝图描述）

**运行时调整布料风力效果：**

1. 从 `USkeletalMeshComponent` 节点，调用 `Get Clothing Simulation Interactor`
2. 将返回值 Cast 为 `UChaosClothingInteractor`
3. 调用 `SetWind`，设置 `Drag = (0.07, 0.5)`, `Lift = (0.035, 0.5)`, `AirDensity = 1.225e-6`, `WindVelocity = (100, 0, 0)`

**运行时启用背停约束并设置碰撞：**

1. 获取 `UChaosClothingInteractor`
2. 调用 `SetBackstop`，`bEnabled = true`
3. 调用 `SetCollision`，`CollisionThickness = 1.0`, `FrictionCoefficient = 0.8`, `SelfCollisionThickness = 2.0`

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothModule.h"
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "ChaosCloth/ChaosClothingSimulationSolver.h"
#include "ChaosCloth/ChaosClothingSimulationCloth.h"
#include "ChaosCloth/ChaosClothConfig.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
```

### 基本用法

ChaosCloth 的主要使用方式是通过 ClothingSystem 接口自动集成。当骨骼网格体上挂载了 ClothingAsset 时，`UChaosClothingSimulationFactory` 会自动创建模拟实例。

**获取模拟实例（通过工厂）：**

```cpp
// 来源: ChaosClothingSimulationFactory.h
// 工厂类自动注册，无需手动创建
UChaosClothingSimulationFactory* Factory = GetMutableDefault<UChaosClothingSimulationFactory>();
IClothingSimulationInterface* Simulation = Factory->CreateSimulation();

// 检查是否支持某个资产
bool bSupported = Factory->SupportsAsset(SomeClothingAsset);

// 获取支持的配置类
TArrayView<const TSubclassOf<UClothConfigBase>> ConfigClasses = Factory->GetClothConfigClasses();
```

**通过 Interactor 运行时控制布料：**

```cpp
// 来源: ChaosClothingSimulationInteractor.h
// 获取 interactor
UClothingSimulationInteractor* RawInteractor = SkeletalMeshComponent->GetClothingSimulationInteractor();
UChaosClothingInteractor* ChaosInteractor = Cast<UChaosClothingInteractor>(RawInteractor);

if (ChaosInteractor)
{
    // 设置材质刚度
    ChaosInteractor->SetMaterial(
        FVector2D(1.0, 1.0),   // EdgeStiffness (Low, High)
        FVector2D(0.5, 1.0),   // BendingStiffness (Low, High)
        FVector2D(1.0, 1.0)    // AreaStiffness (Low, High)
    );

    // 设置碰撞
    ChaosInteractor->SetCollision(
        1.0f,    // CollisionThickness
        0.8f,    // FrictionCoefficient
        false,   // bUseCCD
        2.0f     // SelfCollisionThickness
    );

    // 设置风力
    ChaosInteractor->SetWind(
        FVector2D(0.07, 0.5),   // Drag (Low, High)
        FVector2D(0.035, 0.5),  // Lift (Low, High)
        1.225e-6f,              // AirDensity
        FVector(100, 0, 0),     // WindVelocity
        FVector2D(0.07, 0.5),   // OuterDrag
        FVector2D(0.035, 0.5)   // OuterLift
    );

    // 设置动画驱动
    ChaosInteractor->SetAnimDrive(
        FVector2D(0.8, 1.0),  // AnimDriveStiffness (Low, High)
        FVector2D(0.5, 1.0)   // AnimDriveDamping (Low, High)
    );

    // 设置速度缩放
    ChaosInteractor->SetVelocityScale(
        FVector(0.75, 0.75, 0.75),  // LinearVelocityScale
        0.75f,                       // AngularVelocityScale
        1.0f                         // FictitiousAngularScale
    );
}
```

### 进阶用法

**直接操作 Solver 和 Cloth 对象（需要访问内部模拟结构）：**

```cpp
// 来源: ChaosClothingSimulation.h, ChaosClothingSimulationSolver.h
// 注意: FClothingSimulation 在 5.7 中已标记为 deprecated，
// 未来版本将迁移到 IClothingSimulationInterface

namespace Chaos
{
    // 获取求解器
    FClothingSimulationSolver* Solver = Simulation->GetSolver();

    // 获取布料实例
    FClothingSimulationCloth* Cloth = Simulation->GetCloth(0);

    // 获取模拟统计信息
    int32 NumCloths = Simulation->GetNumCloths();
    int32 NumKinematicParticles = Simulation->GetNumKinematicParticles();
    int32 NumDynamicParticles = Simulation->GetNumDynamicParticles();
    float SimTime = Simulation->GetSimulationTime();

    // 求解器级操作
    Solver->SetWindVelocity(TVec3<FRealSingle>(100.f, 0.f, 0.f));
    Solver->SetGravity(TVec3<FRealSingle>(0.f, 0.f, -980.665f));
    Solver->SetLocalSpaceLocation(FVec3(0, 0, 0));
    Solver->SetLocalSpaceScale(1.0f);

    // 获取粒子数据（模拟后）
    TConstArrayView<Softs::FSolverVec3> Positions = Solver->GetParticleXsView(ClothRangeId);
    TConstArrayView<Softs::FSolverVec3> Velocities = Solver->GetParticleVsView(ClothRangeId);
    TConstArrayView<Softs::FSolverVec3> Normals = Solver->GetNormalsView(ClothRangeId);

    // 获取约束数据
    const FClothConstraints& Constraints = Solver->GetClothConstraints(ParticleRangeId);
    auto EdgeSpring = Constraints.GetEdgeSpringConstraints();
    auto BendingElement = Constraints.GetBendingElementConstraints();
    auto LongRange = Constraints.GetLongRangeConstraints();
    auto MaxDistance = Constraints.GetMaximumDistanceConstraints();
    auto Backstop = Constraints.GetBackstopConstraints();
    auto AnimDrive = Constraints.GetAnimDriveConstraints();
    auto SelfCollision = Constraints.GetSelfCollisionConstraints();
}
```

**手动构建布料模拟：**

```cpp
// 来源: ChaosClothingSimulationCloth.h, ChaosClothingSimulationSolver.h
namespace Chaos
{
    // 1. 创建配置
    FClothingSimulationConfig* Config = new FClothingSimulationConfig();
    // Config 可从 UChaosClothConfig 初始化，或直接使用 PropertyCollection

    // 2. 创建求解器
    FClothingSimulationSolver* Solver = new FClothingSimulationSolver(Config);

    // 3. 创建网格（通常由 FClothingSimulationSkeletalMesh 实现）
    FClothingSimulationMesh* Mesh = new FClothingSimulationSkeletalMesh(Asset, SkelComp);

    // 4. 创建碰撞体
    TArray<FClothingSimulationCollider*> Colliders;
    FClothingSimulationCollider* Collider = new FClothingSimulationCollider(PhysicsAsset, RefSkeleton);
    Colliders.Add(Collider);

    // 5. 创建布料实例
    uint32 GroupId = 0;
    FClothingSimulationCloth* Cloth = new FClothingSimulationCloth(Config, Mesh, MoveTemp(Colliders), GroupId);

    // 6. 添加到求解器并模拟
    Solver->AddCloth(Cloth);
    Solver->Update(DeltaTime);  // 推进模拟
}
```

**Debug 可视化（编辑器和开发构建）：**

```cpp
// 来源: ChaosClothingSimulation.h, ChaosClothVisualization.h
#if CHAOS_DEBUG_DRAW
    // 在编辑器 viewport 中绘制调试信息
    Simulation->DebugDrawPhysMeshWired(PDI);           // 物理网格线框
    Simulation->DebugDrawAnimMeshWired(PDI);            // 动画网格线框
    Simulation->DebugDrawCollision(PDI);                // 碰撞体
    Simulation->DebugDrawBackstops(PDI);                // 背停约束
    Simulation->DebugDrawMaxDistances(PDI);             // 最大距离约束
    Simulation->DebugDrawAnimDrive(PDI);                // 动画驱动
    Simulation->DebugDrawEdgeConstraint(PDI);           // 边约束
    Simulation->DebugDrawBendingConstraint(PDI);        // 弯曲约束
    Simulation->DebugDrawLongRangeConstraint(PDI);      // 长距离约束
    Simulation->DebugDrawWindAndPressureForces(PDI);    // 风力和压力
    Simulation->DebugDrawSelfCollision(PDI);             // 自碰撞
    Simulation->DebugDrawBounds(PDI);                    // 边界框
    Simulation->DebugDrawGravity(PDI);                   // 重力方向
    Simulation->DebugDrawLocalSpace(PDI);                // 本地空间
#endif
```

## Demo 示例

### 最小布料模拟示例

```cpp
// ChaosClothExample.h
#pragma once
#include "CoreMinimal.h"
#include "Components/SkeletalMeshComponent.h"
#include "ChaosCloth/ChaosClothModule.h"

// 无需额外头文件——ChaosCloth 通过 ClothingSystem 接口自动集成
// 只需确保 Build.cs 中依赖 ChaosCloth 模块
```

```cpp
// ChaosClothExample.cpp
#include "ChaosClothExample.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
#include "ClothingSimulationInterface.h"

void UMyClothComponent::BeginPlay()
{
    Super::BeginPlay();

    // 布料模拟自动运行，只需通过 Interactor 调整参数
    if (UClothingSimulationInteractor* Interactor = GetClothingSimulationInteractor())
    {
        if (UChaosClothingInteractor* ChaosInteractor = Cast<UChaosClothingInteractor>(Interactor))
        {
            // 启用动画驱动，让布料跟随动画
            ChaosInteractor->SetAnimDrive(FVector2D(0.8, 1.0), FVector2D(0.0, 0.0));

            // 设置碰撞
            ChaosInteractor->SetCollision(1.0f, 0.8f, false, 2.0f);

            // 启用背停
            ChaosInteractor->SetBackstop(true);
        }
    }
}

void UMyClothComponent::SetWindEffect(float Strength)
{
    if (auto* ChaosInteractor = Cast<UChaosClothingInteractor>(GetClothingSimulationInteractor()))
    {
        ChaosInteractor->SetWind(
            FVector2D(0.07 * Strength, 0.5 * Strength),   // Drag
            FVector2D(0.035 * Strength, 0.5 * Strength),  // Lift
            1.225e-6f,                                      // AirDensity
            FVector(0, 0, 0)                                // WindVelocity
        );
    }
}
```

### Build.cs 依赖说明

```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "ChaosCloth",           // 布料模拟运行时
    "ClothingSystemRuntimeCommon",  // 布料系统公共接口
    "ClothingSystemRuntimeInterface" // 布料系统接口
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `ClothingSystemRuntimeCommon` | 布料系统运行时公共代码（FClothingSimulationCommon、UClothConfigCommon 等） |
| `ClothingSystemRuntimeInterface` | 布料系统抽象接口（IClothingSimulationInterface、UClothingAssetBase 等） |
| `Engine` | 引擎核心（USkeletalMeshComponent 等） |
| `Chaos` | Chaos 物理引擎核心（FPBDEvolution、FEvolution、约束求解器等） |
| `ChaosCaching` | Chaos 缓存系统（用于布料模拟的录制和回放） |

### Editor 模块额外依赖

| 模块 | 用途 |
|---|---|
| `ClothingSystemEditorInterface` | 布料编辑器接口 |
| `Persona` | 骨骼网格体编辑器 |
| `SlateCore` / `Slate` | UI 框架 |
| `UnrealEd` | 编辑器框架 |
| `DetailCustomizations` | 属性面板自定义 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ChaosCaching` | 布料模拟缓存（录制/回放模拟数据） |

## 维护状态

### 近期更新

1. **`aae7bcd` 2025-10-01** - Implement ResetRestLengthsWithMorphTarget for all eligible cloth constraint types.
   - 解读：新增了通过 Morph Target 重置约束 rest length 的功能，允许在运行时动态调整布料的静止长度。这是一个功能增强，支持更灵活的布料形变控制。

2. **`98d9917` 2025-09-25** - Cloth - Deprecated the old Clothing Simulation Interface and added a new updated class to replace it.
   - 解读：重大架构变更——旧的 `FClothingSimulation` 类被标记为 deprecated（UE_DEPRECATED(5.7)），新的 `IClothingSimulationInterface` 将取代它。这是一次接口重构，预计在 5.9 版本完成迁移。

3. **`e22e50a` 2025-09-24** - [Backout] - CL46169203 (Cloth - Deprecated the old Clothing Simulation Interface...)
   - 解读：上述重构的回退版本（同一天），说明这个变更经历了一次 revert 再重新提交的过程，表明团队对接口迁移的谨慎态度。

### 维护评价

- **活跃维护** ✅：最近一次实质性更新在 2025 年 10 月，距今约 7 个月
- **持续演进**：正在经历从旧接口到新接口的迁移（5.7 标记 deprecated，5.9 完成）
- **功能丰富**：支持 PBD 和 Force-based 双求解器、Weight Map、LOD、Accessory Mesh、CCD、自碰撞、Chaos 缓存集成等
- **ISPC 优化**：关键路径使用 Intel ISPC SIMD 优化
- **实验性插件已毕业**：ChaosCloth 已从 Experimental 迁移到正式插件目录，表明 Epic 认为其已足够稳定
- **推荐使用**：这是 UE5 的官方布料方案，替代了 NvCloth，推荐所有新项目使用

**注意**：`FClothingSimulation` 类在 5.7 中已标记 deprecated，自定义布料模拟集成代码应关注 `IClothingSimulationInterface` 的迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosCloth)
- [ChaosClothAsset 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAsset) — 布料资产编辑器插件（配合使用）
- [ChaosClothGenerator 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/ChaosClothGenerator) — ML Deformer 的布料数据生成器
- [ClothingSystemRuntimeCommon 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/ClothingSystemRuntimeCommon) — 布料系统公共运行时
- [ClothingSystemRuntimeInterface 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/ClothingSystemRuntimeInterface) — 布料系统接口定义
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/ChaosCloth/Source/ChaosCloth/Private/ChaosCloth/IspcTestChaosClothingSimulationSolver.cpp) — ISPC 优化的 AABB 计算测试
