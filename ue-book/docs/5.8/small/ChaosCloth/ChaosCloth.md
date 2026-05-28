# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

Chaos Cloth 是 UE5 Chaos 物理引擎的布料模拟系统，为 SkeletalMesh 提供基于粒子的实时布料物理仿真。它替代了旧版 PhysX 布料求解器，使用 Chaos 自有的 PBD（Position Based Dynamics）和力基（Force-based）双模式求解器来模拟布料的拉伸、弯曲、碰撞、风力、浮力等物理行为。

该插件从 `Engine/Plugins/Experimental` 迁移而来，将原先独立的 Chaos Cloth Editor 插件合并为单一插件，标志着 Chaos 布料系统已达到生产可用状态。插件同时依赖 ChaosCaching（用于录制/回放布料状态）、Buoyancy 和 Water（用于布料与水面交互）。

**核心能力**：
- 材料属性控制：边缘刚度、弯曲刚度、面积保持、体积保持
- 长距离约束（Long Range Attachment）：防止布料过度拉伸
- 碰撞系统：与物理资产碰撞体、自碰撞、连续碰撞检测（CCD）
- 环境交互：风力空气动力学模型（阻力/升力/压力）、重力覆盖
- 动画驱动（Anim Drive）：将布料拉向目标动画姿态
- Weight Map 系统：通过绘制权重贴图实现逐顶点参数控制
- LOD 支持：多级细节切换时平滑过渡
- Morph Target 支持：通过变形目标重置布料静止长度

## 使用场景

- 你在做一个角色驱动的游戏，角色穿着飘动的斗篷、裙子或披风 → 使用 Chaos Cloth
- 你需要模拟旗帜、窗帘、帆布等场景布料物件 → 使用 Chaos Cloth
- 你需要布料与水面交互产生浮力效果 → 使用 Chaos Cloth（配合 Water 插件）
- 你需要通过蓝图在运行时动态调整布料参数（刚度、阻尼、风力等） → 使用 `UChaosClothingInteractor`
- 你需要录制布料动画并在游戏内回放 → 使用 ChaosCaching 配合 Chaos Cloth

## 蓝图用法

`UChaosClothingInteractor` 提供了完整的蓝图接口，通过 `USkeletalMeshComponent` 的布料交互器获取。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterial` | 设置边/弯/面积刚度（Low/High 权重范围） | `UChaosClothingInteractor` |
| `SetMaterialLinear` | 设置边/弯/面积刚度（线性值） | `UChaosClothingInteractor` |
| `SetMaterialBuckling` | 设置屈曲比和屈曲刚度 | `UChaosClothingInteractor` |
| `SetLongRangeAttachment` | 设置长距离约束的系绳刚度和缩放 | `UChaosClothingInteractor` |
| `SetLongRangeAttachmentLinear` | 设置长距离约束（线性值） | `UChaosClothingInteractor` |
| `SetCollision` | 设置碰撞厚度、摩擦系数、CCD、自碰撞厚度 | `UChaosClothingInteractor` |
| `SetBackstop` | 启用/禁用背靠约束 | `UChaosClothingInteractor` |
| `SetDamping` | 设置全局和局部阻尼系数 | `UChaosClothingInteractor` |
| `SetWind` | 设置阻力/升力/气密度/风速/外侧阻力/外侧升力 | `UChaosClothingInteractor` |
| `SetPressure` | 设置压力强度 | `UChaosClothingInteractor` |
| `SetGravity` | 设置重力缩放和重力覆盖 | `UChaosClothingInteractor` |
| `SetAnimDrive` | 设置动画驱动刚度和阻尼 | `UChaosClothingInteractor` |
| `SetAnimDriveLinear` | 设置动画驱动刚度（线性值） | `UChaosClothingInteractor` |
| `SetVelocityScale` | 设置线性/角速度缩放和虚拟力缩放 | `UChaosClothingInteractor` |
| `SetVelocityClamps` | 设置线性/角速度和加速度的上限限制 | `UChaosClothingInteractor` |
| `ResetAndTeleport` | 重置布料或执行传送重置 | `UChaosClothingInteractor` |
| `SetNumIterations` | 设置求解器迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetMaxNumIterations` | 设置最大迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetNumSubsteps` | 设置子步数 | `UChaosClothingSimulationInteractor` |
| `EnableGravityOverride` | 启用求解器级重力覆盖 | `UChaosClothingSimulationInteractor` |
| `DisableGravityOverride` | 禁用求解器级重力覆盖 | `UChaosClothingSimulationInteractor` |

### 使用示例（蓝图描述）

1. **获取布料交互器**：从 SkeletalMeshComponent 获取布料模拟交互器（`GetClothingSimulationInteractor`），然后将其 Cast 为 `UChaosClothingSimulationInteractor`。
2. **修改单个布料的参数**：通过交互器的 `GetClothingInteractor(BoneName)` 获取特定布料的 `UChaosClothingInteractor`。
3. **动态调参**：在 Tick 或事件中调用 `SetWind`、`SetGravity`、`SetCollision` 等节点实时修改布料行为。
4. **传送重置**：角色执行传送时调用 `ResetAndTeleport(true, true)` 防止布料撕裂。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
#include "ChaosCloth/ChaosClothConfig.h"
```

### 基本用法

通过交互器 API 在运行时控制布料模拟参数。

```cpp
// 获取布料模拟交互器
USkeletalMeshComponent* SkeletalMeshComp = /* ... */;
UClothingSimulationInteractor* RawInteractor = SkeletalMeshComp->GetClothingSimulationInteractor();

// Cast 到 Chaos 交互器
if (UChaosClothingSimulationInteractor* ChaosInteractor = Cast<UChaosClothingSimulationInteractor>(RawInteractor))
{
    // 设置求解器迭代次数
    ChaosInteractor->SetNumIterations(3);
    ChaosInteractor->SetNumSubsteps(2);
    
    // 获取特定骨骼上的布料交互器
    if (UChaosClothingInteractor* ClothInteractor = ChaosInteractor->GetClothingInteractor(FName("ClothBone")))
    {
        // 设置材料刚度（Low, High 范围，配合 Weight Map）
        ClothInteractor->SetMaterial(
            FVector2D(0.5f, 1.0f),   // EdgeStiffness
            FVector2D(0.5f, 1.0f),   // BendingStiffness
            FVector2D(0.5f, 1.0f)    // AreaStiffness
        );
        
        // 设置碰撞参数
        ClothInteractor->SetCollision(1.0f, 0.8f, false, 2.0f);
        
        // 设置风力
        ClothInteractor->SetWind(
            FVector2D(0.07f, 0.5f),   // Drag
            FVector2D(0.07f, 0.5f),   // Lift
            1.225e-6f,                 // AirDensity
            FVector(100.f, 0.f, 0.f), // WindVelocity
            FVector2D(0.07f, 0.5f),   // OuterDrag
            FVector2D(0.07f, 0.5f)    // OuterLift
        );
        
        // 设置重力
        ClothInteractor->SetGravity(1.0f, false, FVector::ZeroVector);
    }
}
```

### 进阶用法

直接操作布料模拟底层对象进行高级控制。

```cpp
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "ChaosCloth/ChaosClothingSimulationSolver.h"
#include "ChaosCloth/ChaosClothingSimulationCloth.h"
#include "ChaosCloth/ChaosClothVisualization.h"

// 获取底层模拟对象（需在游戏线程调用）
Chaos::FClothingSimulation* Simulation = /* 通过 SkeletalMeshComponent 的 GetClothingSimulation 获取 */;

// 获取求解器
Chaos::FClothingSimulationSolver* Solver = Simulation->GetSolver();

// 获取布料对象
Chaos::FClothingSimulationCloth* Cloth = Simulation->GetCloth(0);

// 获取调试可视化信息（仅限 Debug 构建）
#if CHAOS_DEBUG_DRAW
const Chaos::FClothVisualizationNoGC* Visualization = Simulation->GetClothVisualization();
// 绘制物理网格线框
Visualization->DrawPhysMeshWired();
// 绘制碰撞体
Visualization->DrawCollision();
#endif

// 获取粒子位置（需在求解器更新后调用）
TConstArrayView<Softs::FSolverVec3> Positions = Cloth->GetParticlePositions(Solver);
TConstArrayView<Softs::FSolverVec3> Velocities = Cloth->GetParticleVelocities(Solver);

// 获取权重图数据
TConstArrayView<FRealSingle> EdgeStiffnessWeights = Cloth->GetWeightMapByProperty(Solver, FName("Edge Stiffness"));
```

## Demo 示例

```cpp
// ChaosClothExample.h
#pragma once
#include "GameFramework/Actor.h"
#include "ChaosClothExample.generated.h"

UCLASS()
class AChaosClothExample : public AActor
{
    GENERATED_BODY()
public:
    AChaosClothExample();

    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* SkeletalMeshComp;

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UClothingSimulationInteractor* SimulationInteractor;

    float ElapsedTime = 0.f;
};

// ChaosClothExample.cpp
#include "ChaosClothExample.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"

AChaosClothExample::AChaosClothExample()
{
    PrimaryActorTick.bCanEverTick = true;
    
    SkeletalMeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMeshComp;
}

void AChaosClothExample::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取 Chaos 布料交互器
    SimulationInteractor = SkeletalMeshComp->GetClothingSimulationInteractor();
}

void AChaosClothExample::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    if (!SimulationInteractor) return;
    
    ElapsedTime += DeltaTime;
    
    // 获取 Chaos 交互器
    if (auto* ChaosInteractor = Cast<UChaosClothingSimulationInteractor>(SimulationInteractor))
    {
        // 设置求解器参数
        ChaosInteractor->SetNumIterations(3);
        ChaosInteractor->SetNumSubsteps(1);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供求解器和碰撞体 |
| `ClothingSystemRuntimeCommon` | 布料系统运行时通用基类（UClothConfigCommon 等） |
| `ChaosCaching` | Chaos 缓存系统，用于录制/回放布料模拟状态 |
| `Buoyancy` | 浮力场，用于布料与水体交互 |
| `Water` | 水面系统，与浮力配合使用 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断为浮点的编译警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制 SolverLOD 范围防止数组越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制小幅改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos 布料相关更新 |

### 维护评价

- **活跃维护**：最近 6 个月内持续有功能性更新和 bug 修复，包括崩溃修复、编译警告修复、调试绘制改进等
- **稳定成熟**：从 Experimental 迁移至正式插件，标记为生产可用，已弃用旧版 PhysX 布料
- **代码质量**：API 稳定，有明确的废弃标记（5.x 版本的 UE_DEPRECATED）和迁移路径
- **推荐使用**：作为 UE5 官方唯一的布料物理方案，是角色布料模拟的首选方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth/Source/ChaosCloth/Tests)