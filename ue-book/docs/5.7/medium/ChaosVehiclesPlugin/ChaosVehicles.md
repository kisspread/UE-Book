# ChaosVehiclesPlugin

> Chaos Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 车辆插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画节点） |
| 模块 | `ChaosVehicles` (Runtime), `ChaosVehiclesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin) | |

## 用途

ChaosVehiclesPlugin 是 Epic 基于 Chaos 物理引擎构建的车辆模拟框架。它取代了旧版 PhysX 车辆系统（PhysicsVehicle），提供更稳定、可扩展的物理模拟，支持：

- 车轮与悬挂的精细控制（射线/球体/形状扫描）
- 多种驱动类型（前驱、后驱、四驱、差速器）
- 变速箱（自动/手动，含倒挡）
- 空气动力学（机翼、阻力）
- 推进系统（螺旋桨、喷气）
- 抗侧倾杆、转向控制、刹车/手刹
- 动画驱动的车轮旋转与转向（含马车轮效果）

该插件将车辆物理计算移至异步线程（`FChaosVehicleManagerAsyncCallback`），避免阻塞主线程，适合高性能需求的车辆模拟。

## 使用场景

- 制作驾驶模拟游戏（赛车、越野、卡车）
- 需要物理精确的车辆行为（漂移、悬挂压缩、碰撞反馈）
- 需要在动画蓝图中驱动车轮旋转和转向
- 需要支持多人在线时同步车辆状态（网络复制）

## 蓝图用法

插件公开了以下可用的蓝图节点与属性，主要位于 `UChaosVehicleMovementComponent`（车轮式车辆）和 `UChaosVehicleWheel` 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVehicle` | 获取该动画实例绑定的车辆 Pawn | `UVehicleAnimationInstance` |
| `GetForwardSpeed` | 获取车辆当前前进速度（km/h） | `UChaosVehicleMovementComponent` |
| `GetEngineRotationSpeed` | 获取发动机当前 RPM | `UChaosVehicleMovementComponent` |
| `GetCurrentGear` | 获取当前档位（0=空档，正数=前进，负数=倒车） | `UChaosVehicleMovementComponent` |
| `GetTransmissionType` | 获取变速箱类型（自动/手动） | `UChaosVehicleMovementComponent` |
| `SetSteeringInput` | 设置转向输入（-1~1） | `UChaosVehicleMovementComponent` |
| `SetThrottleInput` | 设置油门输入（0~1） | `UChaosVehicleMovementComponent` |
| `SetBrakeInput` | 设置刹车输入（0~1） | `UChaosVehicleMovementComponent` |
| `SetHandbrakeInput` | 设置手刹输入（0~1） | `UChaosVehicleMovementComponent` |
| `SetGearUp` | 升档 | `UChaosVehicleMovementComponent` |
| `SetGearDown` | 降档 | `UChaosVehicleMovementComponent` |
| `GetWheelStatus` | 获取指定车轮的状态（接触、位置、法线） | `UChaosWheeledVehicleMovementComponent` |
| `GetNumWheels` | 获取车轮总数 | `UChaosVehicleMovementComponent` |
| `EnableParking` | 启用/禁用驻车制动 | `UChaosVehicleMovementComponent` |
| `SetTargetGear` | 强制设定目标档位 | `UChaosVehicleMovementComponent` |

### 使用示例（蓝图描述）

**基本驾驶控制**  
在 Pawn 或 PlayerController 的事件图表中，每帧调用 `SetThrottleInput`、`SetSteeringInput`、`SetBrakeInput`，输入值来自玩家输入（如 WASD 或手柄摇杆）。  
将 `MovementComponent` 引用（从 `WheeledVehiclePawn` 获取）连接到上述节点。

**获取车速并显示**  
使用 `GetForwardSpeed` 节点，输出值连接到 HUD 文本的 `SetText` 节点。

**车轮动画**  
在动画蓝图中使用 `AnimNode_WheelController` 或 `AnimNode_StageCoachWheelController` 节点。  
- `AnimNode_WheelController`：根据物理车轮旋转和转向自动驱动骨骼。需要在动画蓝图中设置 `WheeledVehicleComponent` 引用。  
- `AnimNode_StageCoachWheelController`：模拟旧电影中马车轮旋转效果（通过帧速率的视觉错觉），参数包括 `WheelSpokeCount`（辐条数）、`MaxAngularVelocity`、`ShutterSpeed`、`StageCoachBlend`。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVehicleMovementComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "WheeledVehiclePawn.h"
```

### 基本用法

**创建车轮式车辆 Pawn**  
继承 `AWheeledVehiclePawn`，并在构造函数中设置默认组件。`ChaosVehiclesPlugin` 已提供默认的 `UChaosWheeledVehicleMovementComponent`。

```cpp
// MyVehicle.h
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
AMyVehicle::AMyVehicle(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer.SetDefaultSubobjectClass<UChaosWheeledVehicleMovementComponent>(VehicleMovementComponentName))
{
    // 可在此处设置默认车辆参数
    UChaosWheeledVehicleMovementComponent* MovementComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
    if (MovementComp)
    {
        MovementComp->EngineSetup.MaxRPM = 6000.f;
        MovementComp->EngineSetup.MaxTorque = 400.f;
        MovementComp->TransmissionSetup.bUseAutomaticGears = true;
    }
}
```

**为车辆添加车轮配置**  
在 `AWheeledVehiclePawn` 子类蓝图中，通过创建 `UChaosVehicleWheel` 的子类蓝图，设置车轮半径、悬挂参数、摩擦曲线等。C++ 中可通过构造函数动态创建：

```cpp
// 在构造函数中
UChaosVehicleWheel* RearWheel = NewObject<UChaosVehicleWheel>(this, UChaosVehicleWheel::StaticClass(), TEXT("RearWheel"));
RearWheel->WheelRadius = 35.f;
RearWheel->WheelWidth = 25.f;
RearWheel->SuspensionMaxRaise = 10.f;
RearWheel->SuspensionMaxDrop = 15.f;
```

**控制输入（在 PlayerController 中）**

```cpp
// 获取车辆 Pawn 的 MovementComponent
AWheeledVehiclePawn* VehiclePawn = Cast<AWheeledVehiclePawn>(GetPawn());
if (VehiclePawn)
{
    UChaosVehicleMovementComponent* VC = VehiclePawn->GetVehicleMovement();
    if (VC)
    {
        VC->SetThrottleInput(1.0f);  // 油门全开
        VC->SetSteeringInput(0.5f);  // 右转
        VC->SetBrakeInput(0.2f);     // 轻微刹车
    }
}
```

### 进阶用法

**自定义悬挂扫描类型**  
在 `UChaosVehicleWheel` 子类中设置 `SweepShape` 和 `SweepType` 属性，可在蓝图或 C++ 中调整：

```cpp
// 在 VehicleWheel 子类构造函数中
SweepShape = ESweepShape::Spherecast;
SweepType = ESweepType::ComplexSweep;
```

**异步物理与调试绘制**  
通过 `FVehicleDebugParams` 和 `FWheeledVehicleDebugParams` 控制调试显示（需要编译时启用 `VEHICLE_DEBUGGING_ENABLED`）：

```cpp
// 在 GameInstance 中设置
FVehicleDebugParams DebugParams;
DebugParams.ShowCOM = true;
DebugParams.ShowAerofoilForces = true;
// 复制到全局单例中...
```

**网络复制**  
`UChaosVehicleMovementComponent` 内置 `FVehicleReplicatedState` 用于同步输入。派生类可实现自定义复制属性：

```cpp
void MyVehicleMovementComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION(MyVehicleMovementComponent, MySpecialInput, COND_SkipOwner);
}
```

## Demo 示例

一个完整的最小示例，创建可驾驶的汽车（.h + .cpp）。

### MyWheeledVehicle.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "WheeledVehiclePawn.h"
#include "MyWheeledVehicle.generated.h"

UCLASS()
class MYGAME_API AMyWheeledVehicle : public AWheeledVehiclePawn
{
    GENERATED_BODY()

public:
    AMyWheeledVehicle(const FObjectInitializer& ObjectInitializer);
};
```

### MyWheeledVehicle.cpp

```cpp
#include "MyWheeledVehicle.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "ChaosVehicleWheel.h"
#include "Components/SkeletalMeshComponent.h"

AMyWheeledVehicle::AMyWheeledVehicle(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer.SetDefaultSubobjectClass<UChaosWheeledVehicleMovementComponent>(VehicleMovementComponentName))
{
    // 获取 Movement Component
    UChaosWheeledVehicleMovementComponent* VehicleMovement = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
    if (VehicleMovement)
    {
        // 车辆物理参数
        VehicleMovement->EngineSetup.MaxRPM = 7000.f;
        VehicleMovement->EngineSetup.MaxTorque = 500.f;
        VehicleMovement->EngineSetup.EngineIdleRPM = 800.f;
        VehicleMovement->TransmissionSetup.bUseAutomaticGears = true;
        VehicleMovement->TransmissionSetup.GearChangeTime = 0.5f;
        VehicleMovement->SteeringSetup.SteeringCurve.EditorCurveData.AddKey(0.0f, 1.0f);
        VehicleMovement->SteeringSetup.SteeringCurve.EditorCurveData.AddKey(100.0f, 0.5f);
    }

    // 加载车辆网格（可从 Content 路径引入）
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> CarMesh(TEXT("/Game/Vehicles/Sedan/Sedan.Sedan"));
    if (CarMesh.Succeeded())
    {
        GetMesh()->SetSkeletalMesh(CarMesh.Object);
    }

    // 设置车轮碰撞形状 & 物理材质
    // 注意：更推荐在蓝图子类中配置车轮属性
}
```

### 使用方法

1. 将 `AMyWheeledVehicle` 派生蓝图类（或 C++ 类）放置到关卡中。
2. 在项目设置中启用 ChaosVehiclesPlugin（见下方注意事项）。
3. 创建一个 PlayerController，每帧调用 `SetThrottleInput` 等函数。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心（粒子、约束、碰撞） |
| `ChaosSolverEngine` | 物理求解器管理（FChaosScene） |
| `PhysicsCore` | 物理接口基础（FPhysScene） |
| `AnimGraphRuntime` | 动画节点运行时（FAnimNode_SkeletalControlBase） |

**特别说明**：ChaosVehicles 依赖于 Chaos 物理模块，需要在项目 Build.cs 中添加：

```cpp
PublicDependencyModuleNames.AddRange(new string[] {
    "Chaos",
    "ChaosSolverEngine",
    "PhysicsCore",
    "AnimGraphRuntime"
});
```

## 维护状态

### 近期更新

- 2025-07-28 `b8b21b7a` — 修复物理求解器时间作为 32 位浮点数缓存导致精度丢失的问题
- 2025-06-09 `87ed9fc8` — 抑制 `UChaosWheeledVehicleMovementComponent::DrawDebug` 中的编译器 SA 除零警告
- 2025-06-09 `4e0b9b90` — 修复关闭时崩溃的 bug
- 2025-06-05 `0500d1c4` — 修复车辆低速时因错误法线被微小台阶阻挡的问题
- 2025-05-22 `39d3ddff` — 将日志警告改为低优先级日志

### 维护评价

该插件自 2025 年 5 月创建以来，处于积极维护中，最近一个月内有多次功能性修复。作为 UE5.5+ 的新实验性特性，它正逐步完善。虽然目前仍标记为实验性，但功能基本稳定，可以用于实际项目。建议使用时关注后续版本更新，并注意调试参数 `VEHICLE_DEBUGGING_ENABLED` 在发布版本中需关闭。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/HardwareTests/Private/Vehicles)（含部分车辆自动化测试）