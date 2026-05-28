# ChaosVehiclesPlugin

> Chaos Vehicle Integration（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 车辆插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例蓝图资产、动画蓝图、材质、输入配置） |
| 模块 | `ChaosVehicles` (Runtime), `ChaosVehiclesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin) | |

## 用途

ChaosVehiclesPlugin 是一个基于 Unreal Engine 5 的 Chaos 物理系统构建的完整车辆模拟插件。它解决的核心问题是为开发者提供一套高性能、物理驱动的车辆模拟框架，用于在 UE5 中创建从现实赛车到未来载具等各种类型的轮式及部分飞行载具。

与基于旧版 PhysX 的车辆系统不同，ChaosVehiclesPlugin 深度集成了 Chaos 物理引擎，利用其现代架构（如异步物理线程模拟、确定性网络同步）来提供更强大、更灵活且性能更佳的车辆物理行为。它不仅仅是一套轮子和悬挂，而是涵盖了发动机、变速箱、差速器、转向、空气动力学、飞行控制面（翼型）等完整的载具子系统，并提供了针对网络多人游戏的预测与回滚（Prediction & Resimulation）支持。

## 使用场景

-   你在开发一款拟真赛车游戏，需要精确模拟引擎扭矩曲线、变速箱齿比、轮胎摩擦力和滑移。
-   你正在制作一个包含车辆载具的开放世界游戏，需要车辆能够进行真实的网络同步。
-   你需要实现飞行汽车或带有可控翼面的飞行器，可以利用其提供的“翼型”（Aerofoil）和“推力”（Thrust）配置。
-   你希望车辆动画（如车轮旋转、悬挂压缩）能够与物理模拟完全同步，而无需编写大量同步逻辑。

## 蓝图用法

该插件主要通过组件和Pawn类在蓝图中使用。核心的配置和监控都发生在组件属性面板中，但也暴露了一些蓝图可调用函数用于运行时查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSteerAngle` | 获取当前车轮的转向角度 | `UChaosVehicleWheel` |
| `GetRotationAngle` | 获取车轮当前的旋转角度（用于动画） | `UChaosVehicleWheel` |
| `GetRotationAngularVelocity` | 获取车轮的角速度 | `UChaosVehicleWheel` |
| `GetSuspensionOffset` | 获取悬挂的压缩/拉伸偏移量 | `UChaosVehicleWheel` |
| `GetWheelRadius` | 获取车轮半径 | `UChaosVehicleWheel` |
| `GetWheelAngularVelocity` | 获取车轮角速度 | `UChaosVehicleWheel` |
| `GetSuspensionAxis` | 获取悬挂施加力的局部方向 | `UChaosVehicleWheel` |
| `IsInAir` | 检测车轮是否离开地面 | `UChaosVehicleWheel` |
| `GetAxleType` | 获取车轮的车轴类型（前/后） | `UChaosVehicleWheel` |
| `GetWheelStatus` | 获取指定车轮的详细状态（接触、滑移等） | `UChaosWheeledVehicleMovementComponent` |

### 使用示例（蓝图描述）

1.  **创建基础车辆**：在场景中放置一个 `AWheeledVehiclePawn` 的子类，或创建一个 `APawn` 并添加 `UChaosWheeledVehicleMovementComponent` 作为组件。确保 Pawn 有一个 `USkeletalMeshComponent` 作为根组件（用于车身）。
2.  **配置车辆**：在组件的详细信息（Details）面板中，展开 “Vehicle Setup”，配置 `EngineSetup` (引擎)、`TransmissionSetup` (变速箱)、`DifferentialSetup` (差速器) 和 `SteeringSetup` (转向)。在 “Wheels” 部分，定义车轮的布局和 `WheelSetups`，每个 `WheelSetups` 引用一个 `UChaosVehicleWheel` 蓝图子类来配置车轮的具体属性（半径、摩擦力、悬挂等）。
3.  **输入处理**：通常使用增强输入系统（Enhanced Input）或在 `PlayerController` 中获取 `UChaosVehicleMovementComponent` 引用，调用 `SetThrottleInput`、`SetSteeringInput`、`SetBrakeInput` 等函数来控制车辆。
4.  **读取状态**：在需要更新仪表盘或音效时，可以调用 `GetEngineRPM`、`GetForwardSpeed`，以及通过 `GetWheelStatus` 获取每个车轮的详细信息（如 `SpringForce`, `SlipMagnitude`）。

## C++ 用法

### 头文件引入

```cpp
// 核心车辆运动组件
#include "ChaosVehicles/ChaosVehicleMovementComponent.h"
// 轮式车辆具体实现
#include "ChaosVehicles/ChaosWheeledVehicleMovementComponent.h"
// 车轮配置
#include "ChaosVehicles/ChaosVehicleWheel.h"
// 车辆Pawn基类
#include "ChaosVehicles/WheeledVehiclePawn.h"
```

### 基本用法

创建自定义车辆Pawn，并在其构造函数中设置使用 `UChaosWheeledVehicleMovementComponent`。

```cpp
// MyVehicle.h
#pragma once
#include "WheeledVehiclePawn.h"
#include "MyVehicle.generated.h"

UCLASS()
class AMyVehicle : public AWheeledVehiclePawn
{
    GENERATED_BODY()

public:
    AMyVehicle(const FObjectInitializer& ObjectInitializer);
};
```

```cpp
// MyVehicle.cpp
#include "MyVehicle.h"

AMyVehicle::AMyVehicle(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 构造函数中，AWheeledVehiclePawn 已经创建了 SkeletalMeshComponent 和
    // 默认的 ChaosWheeledVehicleMovementComponent。
    // 可以在这里进行进一步的默认配置。
    UChaosWheeledVehicleMovementComponent* VehicleComp = GetVehicleMovementComponent<UChaosWheeledVehicleMovementComponent>();
    if (VehicleComp)
    {
        // 示例：在代码中配置变速箱为手动模式
        VehicleComp->TransmissionSetup.bUseAutomaticGears = false;
        // 配置一个4挡前进，1挡倒退的变速箱
        VehicleComp->TransmissionSetup.ForwardGearRatios = {3.5f, 2.5f, 1.8f, 1.0f};
        VehicleComp->TransmissionSetup.ReverseGearRatios = {3.2f};
    }
}
```

### 进阶用法

通过继承 `UChaosVehicleMovementComponent` 或 `UChaosWheeledVehicleMovementComponent` 来扩展或覆盖模拟逻辑。

```cpp
// MyCustomMovementComponent.h
#pragma once
#include "ChaosWheeledVehicleMovementComponent.h"
#include "MyCustomMovementComponent.generated.h"

UCLASS()
class UMyCustomMovementComponent : public UChaosWheeledVehicleMovementComponent
{
    GENERATED_BODY()

public:
    UMyCustomMovementComponent();

protected:
    // 覆盖引擎扭矩计算，例如实现一个特殊的引擎增压系统
    virtual void UpdateEngine(const float DeltaTime) override;

    // 在每帧物理模拟前注入自定义逻辑
    virtual void PreTick(float DeltaTime) override;

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Vehicle")
    bool bTurboBoostActive = false;
};
```

```cpp
// MyCustomMovementComponent.cpp
#include "MyCustomMovementComponent.h"

UMyCustomMovementComponent::UMyCustomMovementComponent()
{
    // 自定义默认值
}

void UMyCustomMovementComponent::UpdateEngine(const float DeltaTime)
{
    // 先执行基类（ChaosWheeledVehicleMovementComponent）的引擎逻辑
    Super::UpdateEngine(DeltaTime);

    // 如果涡轮增压激活，额外施加扭矩
    if (bTurboBoostActive)
    {
        // 获取当前引擎状态
        float ExtraTorque = 500.0f; // 牛顿米
        // 这里需要访问内部的 Chaos::FSimpleEngineSim 对象进行操作
        // 简化示例：通常通过扩展输入或覆盖其他函数来实现类似效果
    }
}

void UMyCustomMovementComponent::PreTick(float DeltaTime)
{
    Super::PreTick(DeltaTime);
    // 在物理模拟前添加自定义车辆逻辑，例如根据速度调整重心
}
```

## Demo 示例

一个最小的自定义车辆 Pawn 实现，带有可配置的引擎属性。

```cpp
// SimpleChaosVehicle.h
#pragma once
#include "WheeledVehiclePawn.h"
#include "SimpleChaosVehicle.generated.h"

UCLASS()
class ASimpleChaosVehicle : public AWheeledVehiclePawn
{
    GENERATED_BODY()

public:
    ASimpleChaosVehicle(const FObjectInitializer& ObjectInitializer);
};
```

```cpp
// SimpleChaosVehicle.cpp
#include "SimpleChaosVehicle.h"
#include "ChaosWheeledVehicleMovementComponent.h"

ASimpleChaosVehicle::ASimpleChaosVehicle(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // AWheeledVehiclePawn 基类已经创建了 Mesh 和 VehicleMovementComponent。
    // 获取运动组件并进行一些简单配置。
    UChaosWheeledVehicleMovementComponent* VehicleComp = GetVehicleMovementComponent<UChaosWheeledVehicleMovementComponent>();
    if (VehicleComp)
    {
        // 配置一辆拥有400Nm最大扭矩，7000RPM红区的引擎
        VehicleComp->EngineSetup.MaxTorque = 400.0f;
        VehicleComp->EngineSetup.MaxRPM = 7000.0f;

        // 配置为后轮驱动
        VehicleComp->DifferentialSetup.DifferentialType = EVehicleDifferential::RearWheelDrive;

        // 在蓝图中，我们还需要为VehicleComp的Wheels数组配置WheelSetups，每个指向一个
        // 继承自UChaosVehicleWheel的蓝图资产，来定义具体车轮的物理属性。
    }
}
```

## 模块依赖

从 `ChaosVehicles.Build.cs` 和 `ChaosVehiclesEditor.Build.cs` 中提取。

| 模块 | 用途 |
|---|---|
| `ChaosVehiclesCore` | Chaos 车辆模拟的核心物理逻辑 |
| `Chaos` | Chaos 物理引擎接口 |
| `PhysicsCore` | 引擎物理系统基础类型 |
| `Core` | （标准依赖） |
| `CoreUObject` | （标准依赖） |
| `Engine` | （标准依赖） |
| `InputCore` | （标准依赖） |
| `ChaosSolverEngine` | Chaos 求解器支持 |
| `PhysicsInterfaceCore` | 物理接口核心 |
| `NetCore` | 网络预测/回滚支持 |

`ChaosVehiclesEditor` 模块额外依赖：
| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器核心功能 |
| `Slate`, `SlateCore` | 编辑器UI |
| `PropertyEditor` | 编辑器属性面板自定义 |
| `ChaosVehiclesCore` | 与运行时模块共享核心类型 |

**注意**：使用者通常只需依赖 `ChaosVehicles` 模块。`ChaosVehiclesEditor` 仅在开发自定义车辆编辑器工具时需要。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量转换为浮点型时产生的编译警告。 |
| 2026-05-12 | `400ae955` | OG Vehicle Plugin - Fix automatic transmission stuck in neutral when RPM exceeds ChangeUpRPM | 修复原版车辆插件中，自动变速箱在转速超过升档转速时卡在空挡的 bug。 |
| 2026-05-12 | `6d7bcebe` | Fix UE-376288: Add HasEngine() checks before GetEngine() calls | 修复 UE-376288 问题：在调用 GetEngine() 前添加 HasEngine() 检查，防止崩溃。 |
| 2026-04-30 | `194ad803` | Simple crash bug fix in original vehicle plugin | 修复原版车辆插件的一个简单崩溃 bug。 |
| 2026-04-23 | `97afe1bb` | [NetPhysics] Feature: Adaptive resim coalescing + MergeData semantics | [网络物理] 功能：自适应回滚合并 + MergeData 语义，提升网络同步效率。 |

### 维护评价

-   **活跃程度**：该插件仍在**维护中**。最近一个月（2026年5月）有多次提交，主要集中在修复实际游戏项目中遇到的 bug（如变速箱、崩溃问题）和编译警告，同时也在持续增强其网络物理功能。
-   **实验状态**：`.uplugin` 文件中 `IsExperimentalVersion` 标记为 `true`，且默认未启用。这意味着该 API 仍可能发生变化，不适合追求绝对稳定性的生产项目直接依赖。
-   **推荐使用**：**推荐在实验性或原型项目中使用**。如果你的项目需要基于 Chaos 物理的先进车辆模拟，并且可以接受未来 API 的潜在调整，这是一个强大且功能全面的选择。对于长期稳定的商业项目，建议密切关注其从 Experimental 移出到正式分类的进展。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin)
-   官方文档：（暂无）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin/Source/ChaosVehicles/Private/Tests)