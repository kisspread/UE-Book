# Chaos Cloth

> Adds Chaos Cloth modules.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 布料模拟 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

Chaos Cloth 插件为 Unreal Engine 5 提供了基于 Chaos 物理引擎的下一代布料模拟系统。它旨在替代旧的基于 NVIDIA PhysX 的布料模拟，为开发者提供更强大、更灵活、与 Chaos 物理生态系统深度集成的布料解决方案。该插件主要解决以下问题：
1.  **高性能布料模拟**：支持基于位置的动力学（PBD）和力（Force-based）两种求解器，允许开发者在性能与精度之间做出权衡。
2.  **丰富的物理属性控制**：通过 `UChaosClothConfig` 等类，提供了极其详细的参数，用于精确控制布料的材质属性（边刚度、弯曲刚度、面积保持等）、碰撞、风力、空气动力学、动画驱动、长距离附着（Tether）约束等。
3.  **与 Chaos 物理引擎集成**：作为 Chaos 物理系统的一部分，能够与 Chaos 碰撞体、求解器等无缝交互。
4.  **可视化调试**：提供了 `FClothVisualizationNoGC` 类，包含大量调试绘制方法，用于在编辑器和运行时可视化布料网格、法线、速度、约束、碰撞等。
5.  **高级特性**：支持布料-布料（Cloth-Cloth）交互、自碰撞、形变极限、Morph Target 驱动、Accessory Mesh（附属网格，用于实现如飘带等附加物理效果）、以及通过 Chaos Cache 系统进行模拟数据缓存和回放。

## 使用场景

- 你在制作一个第三人称角色扮演游戏，需要角色身上的斗篷、披风、衣袖能够真实地随风摆动并与角色身体碰撞 → 使用 **Chaos Cloth** 模拟衣物。
- 你正在开发一个开放世界游戏，场景中包含大量需要动态表现的旗帜、窗帘、幕布等物体 → 使用 **Chaos Cloth** 实现这些布料物体的物理效果。
- 你需要实现一个交互式布料物体（如桌布），玩家可以与之互动并产生形变 → 利用 **Chaos Cloth** 的碰撞和材质属性实现交互效果。
- 你希望布料模拟结果能够被录制和回放，用于过场动画或性能分析 → 结合 **Chaos Caching** 插件使用 **Chaos Cloth** 的缓存适配器。
- 你需要在布料上添加额外的物理元素，例如一根绳子末端的坠饰 → 使用 **Accessory Mesh** 功能。

## 蓝图用法

Chaos Cloth 主要通过 `UChaosClothingInteractor` 类提供蓝图交互接口。这些节点允许在运行时动态调整布料的物理参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterial` | 设置布料材质的刚度属性（边缘刚度、弯曲刚度、面积刚度），支持 Low/High 值（用于权重图插值）。 | `UChaosClothingInteractor` |
| `SetMaterialBuckling` | 设置布料的屈曲比和屈曲刚度。 | `UChaosClothingInteractor` |
| `SetLongRangeAttachment` | 设置长距离附着约束（Tether）的刚度和比例，用于控制布料的拉伸范围。 | `UChaosClothingInteractor` |
| `SetCollision` | 设置布料的碰撞属性，包括碰撞厚度、摩擦系数、是否使用连续碰撞检测（CCD）以及自碰撞厚度。 | `UChaosClothingInteractor` |
| `SetDamping` | 设置布料的全局和局部阻尼系数。 | `UChaosClothingInteractor` |
| `SetWind` | 设置风力效果，包括阻力、升力、空气密度、风速以及外向的阻力和升力。 | `UChaosClothingInteractor` |
| `SetPressure` | 设置布料表面的压力强度。 | `UChaosClothingInteractor` |
| `SetGravity` | 设置布料的重力缩放和是否使用重力覆盖。 | `UChaosClothingInteractor` |
| `SetAnimDrive` | 设置动画驱动力，用于将布料拉向目标动画姿势。 | `UChaosClothingInteractor` |
| `SetVelocityScale` | 设置线性/角速度的缩放和虚像力（如离心力）缩放。 | `UChaosClothingInteractor` |
| `SetVelocityClamps` | 设置线性速度、加速度、角速度和角加速度的钳制值。 | `UChaosClothingInteractor` |
| `ResetAndTeleport` | 重置布料模拟状态或强制传送布料到当前动画位置（用于处理瞬移等情况）。 | `UChaosClothingInteractor` |

### 使用示例（蓝图描述）

在角色蓝图中，通常你会拥有一个包含布料组件（如 `SkeletalMeshComponent`）的角色。在角色的 `Event Graph` 中，你可以通过获取 `Clothing Interactor` 来控制布料。
1.  **设置风力**：使用 `Set Wind` 节点，将 `Drag`、`Lift`、`Wind Velocity` 等参数连接起来。例如，你可以将 `Wind Velocity` 绑定到场景中的风向量或角色的移动速度。
2.  **调整材质**：使用 `Set Material` 节点，增加 `Bending Stiffness` 可以使布料更硬，减少则更柔软。
3.  **响应事件**：当角色被击中时，可以调用 `Reset And Teleport (bTeleport = true)` 让布料瞬间回到正确位置，避免不自然的抖动。
这些节点通常在角色蓝图的 `Event Tick` 或特定事件（如跳跃、被击中）中被调用，以实现动态的布料效果。

## C++ 用法

在 C++ 中，可以通过 `Chaos::FClothingSimulation` 或更推荐的 `IClothingSimulationInterface` 来控制和查询布料模拟。`UChaosClothingSimulationInteractor` 和 `UChaosClothingInteractor` 是运行时交互的主要接口。

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
```

### 基本用法

首先需要从 `USkeletalMeshComponent` 获取布料模拟交互器。
```cpp
// 假设你有一个 USkeletalMeshComponent* SkeletalMeshComp
if (UClothingSimulationInteractor* Interactor = SkeletalMeshComp->GetClothingInteractor())
{
    // 将其转换为 Chaos 的交互器
    if (UChaosClothingSimulationInteractor* ChaosInteractor = Cast<UChaosClothingSimulationInteractor>(Interactor))
    {
        // 设置全局迭代次数（影响求解器精度和性能）
        ChaosInteractor->SetNumIterations(4);
        // 或者设置某个特定布料片的属性
        if (UChaosClothingInteractor* ClothInteractor = ChaosInteractor->CreateClothingInteractor())
        {
            ClothInteractor->SetDamping(0.02f, 0.0f);
            ClothInteractor->SetWind(FVector2D(0.1f, 0.5f), FVector2D(0.1f, 0.5f), 1.225e-6f, FVector::ZeroVector);
        }
    }
}
```
*(来源：基于 `ChaosClothingSimulationInteractor.h` 接口及常见用法推断)*

### 进阶用法

可以通过 `FClothingSimulationSolver` 直接操作求解器来获取调试信息或进行更底层的控制。
```cpp
#include "ChaosCloth/ChaosClothingSimulationSolver.h"

// 假设已经获取到 Chaos::FClothingSimulationSolver* Solver
if (Solver)
{
    // 获取求解器统计信息
    int32 NumIterations = Solver->GetNumUsedIterations();
    int32 NumLinearSolverIterations = Solver->GetNumLinearSolverIterations(/* ParticleRangeId */);
    float LinearSolverError = Solver->GetLinearSolverError(/* ParticleRangeId */);
    UE_LOG(LogChaosCloth, Log, TEXT("Solver Stats: Used Iterations: %d, Linear Iterations: %d, Error: %f"), NumIterations, NumLinearSolverIterations, LinearSolverError);

    // 获取当前模拟时间
    float CurrentTime = Solver->GetTime();
}
```
*(来源：基于 `ChaosClothingSimulationSolver.h` 中的 `GetNumUsedIterations`、`GetTime` 等方法)*

## Demo 示例

一个最小化的 C++ 示例，展示如何初始化并获取布料模拟的统计信息。

### `MyClothCharacter.h`
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "ChaosCloth/ChaosClothingSimulationSolver.h" // 前置声明
#include "MyClothCharacter.generated.h"

UCLASS()
class AMyClothCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime) override;
    virtual void BeginPlay() override;

private:
    Chaos::FClothingSimulationSolver* CachedClothSolver = nullptr;
};
```

### `MyClothCharacter.cpp`
```cpp
#include "MyClothCharacter.h"
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "Components/SkeletalMeshComponent.h"

void AMyClothCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 等待一帧，确保布料模拟已初始化
    GetWorldTimerManager().SetTimerForNextTick([this]()
    {
        if (USkeletalMeshComponent* SkelMesh = GetMesh())
        {
            if (Chaos::FClothingSimulation* Sim = static_cast<Chaos::FClothingSimulation*>(SkelMesh->GetClothingSimulation()))
            {
                CachedClothSolver = Sim->GetSolver();
            }
        }
    });
}

void AMyClothCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (CachedClothSolver)
    {
        // 在Tick中查询求解器状态（注意线程安全，通常在模拟完成后查询）
        int32 UsedIters = CachedClothSolver->GetNumUsedIterations();
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 0.0f, FColor::Yellow,
                FString::Printf(TEXT("Cloth Solver Used Iterations: %d"), UsedIters));
        }
    }
}
```

## 模块依赖

ChaosCloth 插件依赖于以下**不常见**或**核心**的模块，使用此插件时，你的项目或模块的 `Build.cs` 需要添加相应的依赖。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎的核心模块，提供物理求解器、粒子、碰撞等基础功能。 |
| `ClothingSystemRuntimeCommon` | 提供服装系统的运行时通用基类和接口（如 `IClothingSimulationInterface`）。 |
| `ClothingSystemRuntimeInterface` | 定义服装系统的运行时接口（`UClothingInteractor` 等）。 |
| `GeometryFramework` | 提供几何处理相关工具，可能用于布料网格数据处理。 |
| `PhysicsCore` | 物理核心模块，提供物理资产、碰撞配置等基础功能。 |
| `ChaosSolverEngine` | Chaos 求解器引擎，管理物理场景和求解器事件。 |
| `ChaosSolvers` | Chaos 求解器实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 钳制求解器LOD索引以防止越界崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的轻微改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | （标题）Chaos Cloth： |

### 维护评价

- **创建时间**：该插件于 2024 年 3 月创建，尚不足两年。
- **近期活跃度**：从 Git 历史看，**最近 3 个月内有多次提交**，内容涉及 Bug 修复（崩溃、警告）、代码现代化（日志宏迁移）和功能改进（调试绘制），表明该插件正在被**积极维护**。
- **维护状态**：**活跃维护中**。作为 UE5 Chaos 物理系统的重要组成部分，预计会长期更新以配合引擎版本。
- **已知限制**：该插件从 Experimental 目录正式移出，部分旧 API（如 `FClothingSimulation` 类）已被标记为废弃（`UE_DEPRECATED`），开发者应使用新接口（`IClothingSimulationInterface`）。
- **推荐使用**：**强烈推荐**。这是 Epic 官方的下一代布料解决方案，是 UE5 中实现布料效果的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth/Tests)（如果存在）