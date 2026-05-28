# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是 UE5 的 Chaos 物理引擎提供的布料模拟系统。它替代了旧版的 NVIDIA PhysX 布料方案，为骨骼网格体（Skeletal Mesh）提供完整的布料物理模拟能力。

该插件解决的核心问题：让角色衣物、旗帜、窗帘等柔性物体拥有真实的物理表现。它提供了基于粒子的布料模拟，支持多种物理约束（边缘弹簧、弯曲、长程附着、自碰撞等），并与 Chaos 物理引擎的碰撞系统深度集成。

插件从 Experimental 目录正式迁移出来，说明 Epic 已经将其视为稳定可用的功能。

## 使用场景

- 你有一个角色需要穿披风/斗篷 → 使用 ChaosCloth 设置布料资产并配置约束
- 你需要旗帜或窗帘在风中飘动 → 配置风力、气动阻力和压力参数
- 你需要衣物的自碰撞（衣袖不会穿入身体） → 启用自碰撞约束
- 你需要实时调整布料物理参数（如动画驱动强度） → 使用 `UChaosClothingInteractor` 蓝图节点
- 你需要录制/回放布料模拟数据 → 通过 ChaosCache 系统集成

## 蓝图用法

ChaosCloth 的蓝图接口主要通过 `UChaosClothingInteractor` 暴露，用于在运行时动态修改布料模拟参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterial` | 设置边缘/弯曲/面积刚度（支持权重贴图的 Low/High 值） | `UChaosClothingInteractor` |
| `SetMaterialLinear` | 设置边缘/弯曲/面积刚度（统一值，不区分权重区域） | `UChaosClothingInteractor` |
| `SetMaterialBuckling` | 设置弯曲屈曲比和屈曲刚度 | `UChaosClothingInteractor` |
| `SetLongRangeAttachment` | 设置长程附着的系绳刚度和缩放（支持权重贴图） | `UChaosClothingInteractor` |
| `SetLongRangeAttachmentLinear` | 设置长程附着的系绳刚度和缩放（统一值） | `UChaosClothingInteractor` |
| `SetCollision` | 设置碰撞厚度、摩擦系数、CCD、自碰撞厚度 | `UChaosClothingInteractor` |
| `SetBackstop` | 启用/禁用背停约束 | `UChaosClothingInteractor` |
| `SetDamping` | 设置全局和局部阻尼系数 | `UChaosClothingInteractor` |
| `SetWind` | 设置风力参数：阻力、升力、空气密度、风速、外层阻力/升力 | `UChaosClothingInteractor` |
| `SetPressure` | 设置布料压力（正值向外膨胀，负值向内收缩） | `UChaosClothingInteractor` |
| `SetGravity` | 设置重力缩放和重力覆盖 | `UChaosClothingInteractor` |
| `SetAnimDrive` | 设置动画驱动刚度和阻尼（支持权重贴图） | `UChaosClothingInteractor` |
| `SetAnimDriveLinear` | 设置动画驱动刚度（统一值） | `UChaosClothingInteractor` |
| `SetVelocityScale` | 设置线性/角速度缩放和离心力缩放 | `UChaosClothingInteractor` |
| `SetVelocityClamps` | 启用/设置线性速度、线性加速度、角速度、角加速度的上限 | `UChaosClothingInteractor` |
| `ResetAndTeleport` | 重置布料状态或传送（避免高速移动时的穿模） | `UChaosClothingInteractor` |

模拟级控制节点（`UChaosClothingSimulationInteractor`）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNumIterations` | 设置求解器迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetMaxNumIterations` | 设置最大迭代次数上限 | `UChaosClothingSimulationInteractor` |
| `SetNumSubsteps` | 设置子步数 | `UChaosClothingSimulationInteractor` |
| `EnableGravityOverride` | 启用重力覆盖 | `UChaosClothingSimulationInteractor` |
| `DisableGravityOverride` | 禁用重力覆盖 | `UChaosClothingSimulationInteractor` |

### 使用示例（蓝图描述）

**设置布料材质属性**：
1. 获取 `SkeletalMeshComponent` → 调用 `GetClothingInteractor` → 转换为 `UChaosClothingInteractor`
2. 连接 `SetMaterial` 节点，设置 `EdgeStiffness = (1, 1)`, `BendingStiffness = (0.5, 0.8)`, `AreaStiffness = (1, 1)`

**在运行时添加风力效果**：
1. 获取 `UChaosClothingInteractor` 引用
2. 连接 `SetWind` 节点，设置 `Drag = (0.07, 0.5)`, `Lift = (0.07, 0.5)`, `AirDensity = 1.225e-6`, `WindVelocity = (500, 0, 0)`

**角色快速移动时防止穿模**：
1. 当角色速度超过阈值时，调用 `ResetAndTeleport(bReset=false, bTeleport=true)`

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothConfig.h"
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "ChaosCloth/ChaosClothingSimulationCloth.h"
#include "ChaosCloth/ChaosClothingSimulationSolver.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
```

### 基本用法

通过 Interactor 在运行时调整布料参数：

```cpp
// 获取布料交互器（通常通过 USkeletalMeshComponent 获取）
UChaosClothingInteractor* ClothInteractor = Cast<UChaosClothingInteractor>(
    SkeletalMeshComponent->GetClothingInteractor());

if (ClothInteractor)
{
    // 设置材料刚度（支持权重贴图插值的 Low/High 值）
    ClothInteractor->SetMaterial(
        FVector2D(1.f, 1.f),   // EdgeStiffness
        FVector2D(0.5f, 0.8f), // BendingStiffness
        FVector2D(1.f, 1.f));  // AreaStiffness

    // 设置风力效果
    ClothInteractor->SetWind(
        FVector2D(0.07f, 0.5f), // Drag
        FVector2D(0.07f, 0.5f), // Lift
        1.225e-6f,              // AirDensity
        FVector(500.f, 0, 0));  // WindVelocity

    // 设置重力
    ClothInteractor->SetGravity(1.f, false, FVector::ZeroVector);
}
```
*来源: Public/ChaosCloth/ChaosClothingSimulationInteractor.h*

### 进阶用法

直接操作布料模拟核心对象：

```cpp
// 获取求解器
Chaos::FClothingSimulationSolver* Solver = ClothSimulation->GetSolver();

// 设置本地空间（用于远距离角色避免浮点精度问题）
Solver->SetLocalSpaceLocation(CharacterLocation, bReset);
Solver->SetLocalSpaceScale(CharacterScale, bReset);

// 设置每组布料的重力覆盖
Solver->EnableClothGravityOverride(true);
Solver->SetGravity(TVec3<FRealSingle>(0.f, 0.f, -490.f)); // 半重力

// 设置每帧风速
Solver->SetWindVelocity(TVec3<FRealSingle>(200.f, 0.f, 0.f));

// 通过布料对象重置状态
FClothingSimulationCloth* Cloth = ClothSimulation->GetCloth(ClothId);
Cloth->Reset();      // 重置布料状态
Cloth->Teleport();   // 传送（快速移动时使用）
```
*来源: Public/ChaosCloth/ChaosClothingSimulationSolver.h, Public/ChaosCloth/ChaosClothingSimulationCloth.h*

配置布料物理参数：

```cpp
// 通过 UChaosClothConfig 设置布料资产级别的配置
UChaosClothConfig* Config = NewObject<UChaosClothConfig>();

// 质量设置
Config->MassMode = EClothMassMode::Density;
Config->Density = 0.35f; // 棉布密度

// 材料属性
Config->EdgeStiffnessWeighted = {1.f, 1.f};
Config->BendingStiffnessWeighted = {0.5f, 0.8f};
Config->bUseBendingElements = true; // 使用更精确的弯曲约束

// 长程附着
Config->TetherStiffness = {1.f, 1.f};
Config->TetherScale = {1.f, 1.f};
Config->bUseGeodesicDistance = true; // 使用测地线距离（更精确）

// 碰撞
Config->CollisionThickness = 1.f;
Config->FrictionCoefficient = 0.8f;
Config->bUseCCD = false;

// 风力和气动
Config->Drag = {0.035f, 1.f};
Config->Lift = {0.035f, 1.f};
Config->Pressure = {0.f, 1.f};
```
*来源: Public/ChaosCloth/ChaosClothConfig.h*

共享配置（所有服装资产共用）：

```cpp
// 通过 UChaosClothSharedSimConfig 设置骨骼网格体级别的共享参数
UChaosClothSharedSimConfig* SharedConfig = NewObject<UChaosClothSharedSimConfig>();

SharedConfig->IterationCount = 3;     // 迭代次数（60fps 下）
SharedConfig->MaxIterationCount = 10; // 最大迭代次数
SharedConfig->SubdivisionCount = 1;   // 子步数
```
*来源: Public/ChaosCloth/ChaosClothConfig.h 中的 UChaosClothSharedSimConfig*

## Demo 示例

完整的自定义布料模拟管理示例：

```cpp
// MyClothManager.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ChaosCloth/ChaosClothConfig.h"
#include "MyClothManager.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyClothManager : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyClothManager();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    /** 在蓝图中设置风力强度 */
    UFUNCTION(BlueprintCallable)
    void SetWindStrength(float Strength);

    /** 切换低重力模式（水下效果） */
    UFUNCTION(BlueprintCallable)
    void SetUnderwaterMode(bool bUnderwater);

protected:
    UPROPERTY(EditAnywhere, Category = "Cloth")
    float BaseWindStrength = 200.f;

private:
    TWeakObjectPtr<class UChaosClothingInteractor> ClothInteractor;
};
```

```cpp
// MyClothManager.cpp
#include "MyClothManager.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
#include "Components/SkeletalMeshComponent.h"

UMyClothManager::UMyClothManager()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyClothManager::BeginPlay()
{
    Super::BeginPlay();

    // 获取宿主 Actor 的骨骼网格体组件
    AActor* Owner = GetOwner();
    if (USkeletalMeshComponent* SkelMesh = Owner->FindComponentByClass<USkeletalMeshComponent>())
    {
        UClothingInteractor* Interactor = SkelMesh->GetClothingInteractor();
        ClothInteractor = Cast<UChaosClothingInteractor>(Interactor);
    }
}

void UMyClothManager::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (ClothInteractor.IsValid())
    {
        // 每帧更新风力方向（可模拟阵风效果）
        FVector WindDir = FMath::VRand();
        WindDir.Z = FMath::Abs(WindDir.Z) * 0.3f; // 风主要水平吹
        ClothInteractor->SetWind(
            FVector2D(0.07f, 0.5f),   // Drag
            FVector2D(0.07f, 0.5f),   // Lift
            1.225e-6f,                // AirDensity
            WindDir * BaseWindStrength, // WindVelocity
            FVector2D(0.07f, 0.5f),   // OuterDrag
            FVector2D(0.07f, 0.5f));  // OuterLift
    }
}

void UMyClothManager::SetWindStrength(float Strength)
{
    BaseWindStrength = FMath::Clamp(Strength, 0.f, 1000.f);
}

void UMyClothManager::SetUnderwaterMode(bool bUnderwater)
{
    if (ClothInteractor.IsValid())
    {
        if (bUnderwater)
        {
            // 水下：降低重力，增加阻尼，增加压力
            ClothInteractor->SetGravity(0.3f, false, FVector::ZeroVector);
            ClothInteractor->SetDamping(0.1f, 0.05f);
            ClothInteractor->SetPressure(FVector2D(0.5f, 0.5f));
        }
        else
        {
            // 恢复正常
            ClothInteractor->SetGravity(1.f, false, FVector::ZeroVector);
            ClothInteractor->SetDamping(0.01f, 0.f);
            ClothInteractor->SetPressure(FVector2D(0.f, 1.f));
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心（粒子、求解器、约束） |
| `ChaosSolverEngine` | Chaos 求解器引擎集成 |
| `ClothingSystemRuntimeCommon` | 布料系统运行时公共基类（UClothConfigCommon 等） |
| `ClothingSystemRuntimeInterface` | 布料系统运行时接口（IClothingSimulationInterface） |
| `ChaosCaching` | Chaos 缓存系统（布录/回放布料模拟数据） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 到 float 截断警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制 SolverLOD 防止越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的微小改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化宏 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos Cloth 相关更新（提交信息被截断） |

### 维护评价

- **活跃维护**：最近 1 年内有多次实质性更新，包括 bug 修复、崩溃修复、代码质量改进和 API 清理
- **从 Experimental 正式毕业**：2024 年 3 月从 Experimental 目录迁移出来，并合并了独立的 ChaosClothEditor 插件，标志着进入稳定状态
- **持续改进中**：大量 5.7/5.8 版本的 API 废弃标记和新接口替换，说明 API 正在不断优化
- **推荐使用**：作为 UE5 的默认布料模拟方案（EnabledByDefault=true），已被 Epic 官方正式支持，推荐用于生产环境

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth/Source/ChaosCloth/Private/Tests)（如存在）