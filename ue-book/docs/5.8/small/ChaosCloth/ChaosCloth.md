# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

Chaos Cloth 是一个基于 Chaos 物理系统的完整布料模拟解决方案。它取代了旧版的布料系统，提供高性能、高保真的物理模拟，用于模拟角色服装、旗帜、织物、柔性物体等。其核心是将布料网格的顶点视为带有物理属性的粒子，通过求解一系列约束（如边、弯曲、气压等）来模拟布料的动态行为，并能与游戏世界中的碰撞体进行精确交互。它支持复杂的材质属性（如各向异性、弯曲刚度）、先进的风力和空气动力学模型、精确的自碰撞检测、以及与动画驱动的平滑集成。

## 使用场景

-   你需要为游戏角色制作逼真的动态服装、披风或布料装饰。
-   你需要模拟旗帜、横幅、窗帘等环境中的织物。
-   你需要实现与布料物理相关的游戏机制，如可被风吹动的旗帜或可被拉扯的织物。
-   你需要记录和回放布料模拟状态，用于动画制作或游戏机制。

## 蓝图用法

Chaos Cloth 主要通过 `UChaosClothingInteractor` 和 `UChaosClothingSimulationInteractor` 这两个蓝图交互器对象来控制。通常通过 `GetClothingSimulationInteractor` 节点从绑定了布料资产的骨骼网格组件上获取。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterial` | 设置边、弯曲、面积等约束的整体刚度参数（支持 Low/High 权重图插值）。 | `UChaosClothingInteractor` |
| `SetMaterialLinear` | 线性设置边、弯曲、面积刚度（等同于将 Low 和 High 设置为相同值）。 | `UChaosClothingInteractor` |
| `SetLongRangeAttachment` | 设置长程附着约束（防止布料过度拉伸）的刚度和缩放比例。 | `UChaosClothingInteractor` |
| `SetCollision` | 设置碰撞厚度、摩擦系数、连续碰撞检测(CCD)以及自碰撞厚度。 | `UChaosClothingInteractor` |
| `SetBackstop` | 启用或禁用后挡板约束（防止布料穿透身体）。 | `UChaosClothingInteractor` |
| `SetDamping` | 设置全局和局部阻尼系数。局部阻尼用于减少抖动而不影响整体运动。 | `UChaosClothingInteractor` |
| `SetWind` | 设置空气动力学参数（阻力、升力、空气密度）和风速。支持内外表面差异化设置。 | `UChaosClothingInteractor` |
| `SetGravity` | 设置重力缩放或覆盖重力向量。 | `UChaosClothingInteractor` |
| `SetAnimDrive` | 设置动画驱动的刚度和阻尼，用于将布料拉向目标动画姿势。 | `UChaosClothingInteractor` |
| `SetVelocityScale` | 设置从参考骨骼传递到布料模拟空间的线性/角速度缩放比例。 | `UChaosClothingInteractor` |
| `ResetAndTeleport` | 立即重置或传送布料状态。用于角色瞬移或状态剧变时。 | `UChaosClothingInteractor` |
| `SetNumIterations` | 设置求解器迭代次数（影响约束精度和性能）。 | `UChaosClothingSimulationInteractor` |
| `SetNumSubsteps` | 设置模拟子步数（提高碰撞精度）。 | `UChaosClothingSimulationInteractor` |

### 使用示例（蓝图描述）

1.  获取交互器：从拥有布料资产的 `SkeletalMeshComponent` 获取 `ClothingSimulationInteractor`，并将其转换为 `UChaosClothingSimulationInteractor`。
2.  获取布料交互器：对于每个应用了布料资产的网格部分，从 `UChaosClothingSimulationInteractor` 调用 `GetClothingInteractor`，并将其转换为 `UChaosClothingInteractor`。
3.  调整参数：在事件图表中（如 `BeginPlay` 或 `Tick`），调用上述蓝图节点。例如，调用 `SetWind` 节点，传入 `Drag = (0.07, 0.5)`, `Lift = (0.035, 0.5)`, `WindVelocity = (100, 0, 0)` 来让风从 X 方向吹来。
4.  同步：所有对交互器的调用都是异步的，会在下一个物理模拟帧开始时应用。确保在需要的时间点之前设置好参数。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
#include "ChaosCloth/ChaosClothConfig.h"
```

### 基本用法

创建和配置布料模拟的关键类是 `FClothingSimulationCloth`，但更常见的用法是通过交互器或修改配置对象。以下示例展示了如何通过 C++ 代码动态获取并修改布料配置。

```cpp
// 假设你有一个 USkeletalMeshComponent* SkeletalMeshComp
// 1. 获取布料模拟交互器
if (UChaosClothingSimulationInteractor* SimulationInteractor = Cast<UChaosClothingSimulationInteractor>(
        SkeletalMeshComp->GetClothingSimulationInteractor()))
{
    // 2. 获取特定网格部分的布料交互器
    if (UChaosClothingInteractor* ClothInteractor = Cast<UChaosClothingInteractor>(
            SimulationInteractor->GetClothingInteractor(/*LODIndex*/ 0, /*SectionIndex*/ 0)))
    {
        // 3. 通过交互器设置运行时参数
        ClothInteractor->SetWind(
            FVector2D(0.07f, 0.5f), // Drag (Low, High)
            FVector2D(0.035f, 0.5f), // Lift (Low, High)
            1.225e-6f, // Air Density
            FVector(100.f, 0.f, 0.f) // Wind Velocity
        );
        ClothInteractor->SetCollision(1.0f, 0.8f, false, 2.0f); // Thickness, Friction, CCD, SelfThickness
    }
}
```
*（来源：基于 `UChaosClothingInteractor` 的公共接口设计）*

### 进阶用法

要进行更底层的配置，需要访问和修改布料资产的 `UChaosClothConfig` 对象。这通常在资产编辑器或通过代码初始化时进行。

```cpp
#include "ChaosCloth/ChaosClothConfig.h"

// 假设你从某个 UClothingAsset 或相关对象获得了 UChaosClothConfig* ClothConfig
if (UChaosClothConfig* ChaosConfig = Cast<UChaosClothConfig>(ClothConfig))
{
    // 修改基础材质属性
    ChaosConfig->EdgeStiffnessWeighted.Low = 0.5f;
    ChaosConfig->BendingStiffnessWeighted.Low = 0.2f;
    
    // 启用并配置自碰撞
    ChaosConfig->bUseSelfCollisions = true;
    ChaosConfig->SelfCollisionThickness = 3.0f;
    ChaosConfig->SelfCollisionFriction = 0.5f;
    
    // 配置环境参数
    ChaosConfig->DampingCoefficient = 0.05f;
    ChaosConfig->Drag.Low = 0.05f;
    ChaosConfig->Lift.Low = 0.02f;
    
    // 使用密度模式设置质量
    ChaosConfig->MassMode = EClothMassMode::Density;
    ChaosConfig->Density = 0.4f; // 类似牛仔布的密度
    
    // 需要调用 PostEditChange 或重新初始化资产使更改生效
}
```
*（来源：基于 `UChaosClothConfig` 头文件中定义的 UPROPERTY 属性）*

## Demo 示例

一个最小的 C++ 示例，展示如何在运行时通过交互器控制布料。

```cpp
// MyChaosClothActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyChaosClothActor.generated.h"

class UChaosClothingInteractor;
class USkeletalMeshComponent;

UCLASS()
class AMyChaosClothActor : public AActor
{
    GENERATED_BODY()

public:
    AMyChaosClothActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* SkeletalMeshComp;

    // 存储布料交互器的引用
    UPROPERTY()
    UChaosClothingInteractor* ClothInteractor;

    // 风力参数，可在编辑器调整
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Cloth Wind")
    FVector WindVelocity = FVector(50.f, 0.f, 0.f);
};

// MyChaosClothActor.cpp
#include "MyChaosClothActor.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
#include "Components/SkeletalMeshComponent.h"

AMyChaosClothActor::AMyChaosClothActor()
{
    PrimaryActorTick.bCanEverTick = true;
    SkeletalMeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMeshComp;
}

void AMyChaosClothActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取并缓存布料交互器
    if (UChaosClothingSimulationInteractor* SimInteractor = Cast<UChaosClothingSimulationInteractor>(
            SkeletalMeshComp->GetClothingSimulationInteractor()))
    {
        // 注意：实际中需要根据布料资产的LOD和Section索引来获取正确的交互器
        ClothInteractor = Cast<UChaosClothingInteractor>(
            SimInteractor->GetClothingInteractor(0, 0));
    }

    if (ClothInteractor)
    {
        // 设置一些初始参数
        ClothInteractor->SetDamping(0.01f, 0.0f);
        ClothInteractor->SetCollision(1.0f, 0.8f, false, 2.0f);
    }
}

// 在 Tick 中或通过其他逻辑调用
// ClothInteractor->SetWind(FVector2D(0.07f, 0.5f), FVector2D(0.035f, 0.5f), 1.225e-6f, WindVelocity);
```

## 模块依赖

从 `Build.cs` 和 `.uplugin` 的 `Plugins` 字段分析，使用此插件需要确保以下模块或插件可用：

| 模块/插件 | 用途 |
|---|---|
| `ChaosCaching` | 用于记录和回放布料模拟状态，实现动画缓存功能。 |
| `Buoyancy` | 提供浮力场支持，使布料能与水体交互。 |
| `Water` | 提供水体系统，与 Buoyancy 配合使用。 |

你的项目模块如果需要直接使用 Chaos Cloth 的 C++ 接口，应在 `Build.cs` 中添加 `ChaosCloth` 依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制 `ChaosClothingSimulationSolver` 中的 `SolverLOD`，防止越界崩溃。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的小改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos Cloth 相关提交（信息不完整）。 |

### 维护评价

Chaos Cloth 是 UE5 中布料模拟的核心系统，自2024年3月从实验性状态移出并集成后，一直保持活跃维护。从git记录看，直至2026年5月仍有功能性更新和缺陷修复（如内存越界、浮点精度问题），表明该模块处于**活跃维护**状态。它是官方推荐的布料模拟解决方案，取代了旧版系统，**推荐在新项目中使用**。需要注意，该插件默认启用，但需要配合正确的物理资产设置和布料绘制工作流才能发挥最佳效果。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/chaos-cloth-in-unreal-engine/)（UE官方文档 - Chaos Cloth）