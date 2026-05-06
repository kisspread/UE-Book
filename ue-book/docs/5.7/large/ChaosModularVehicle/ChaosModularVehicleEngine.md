# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、模拟模块组件） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

Chaos Modular Vehicle 是一个基于 Chaos 物理引擎的**模块化车辆构建系统**。它允许开发者通过将各个车辆子系统（如发动机、变速箱、悬挂、车轮、机翼、推进器等）作为独立的组件（`UVehicleSimBaseComponent` 子类）添加到 Actor 上，从而灵活组合出各种类型的车辆——从普通汽车到飞行器、气垫船等。

与传统的单块式车辆插件不同，该插件将车辆物理模拟拆分为多个可插拔的“模拟模块”（`ISimulationModuleBase`），每个模块负责一个独立的物理作用（如发动机扭矩、悬挂力、空气阻力）。所有模块通过一个模拟树（`FSimModuleTree`）组织，在物理线程上高效并行计算。

核心组件包括：

- **`UModularVehicleBaseComponent`**：车辆模拟的核心组件，管理模拟树、输入、网络同步。
- **`UVehicleSimXXXComponent`** 系列：定义各子系统的物理参数（如扭矩曲线、齿轮比、弹簧刚度）。
- **`FModularVehicleSimulation`**：物理线程上的模拟器，执行模块化物理计算。
- **`FChaosSimModuleManager`**：场景级别的管理器，负责注册/更新所有车辆。

此外，插件还提供了输入系统（`FModularVehicleInputs`、输入缓冲）、动画支持（`FAnimNode_ModularVehicleController`）、网络预测（基于 `FNetworkPhysicsComponent`）以及调试工具。

## 使用场景

- 你正在制作一个**开放世界驾驶游戏**，需要不同类型的车辆（轿车、卡车、越野车、飞机、船）。
- 你想**自定义车辆行为**，例如为某些车辆增加可变形机翼或推进器，而不必重写整个物理逻辑。
- 你需要**高性能的车辆物理**，利用 Chaos 多线程能力同时模拟数十辆车。
- 你的项目依赖**网络同步**（例如多人竞速游戏），该插件内置了基于 Iris 的输入历史与状态同步机制。

## 蓝图用法

该插件主要提供自定义的 Actor Component 和结构化参数，可在蓝图中直接使用。

### 核心车辆组件

| 组件 | 说明 |
|---|---|
| `ModularVehicleBaseComponent` | 车辆模拟的核心，必须添加到车辆 Actor 上。 |
| `ClusterUnionVehicleComponent` | 用于将多个物体合并为单个刚体（Cluster）的组件，与车辆挂接配合使用。 |

### 车辆子模块组件

所有子模块组件均为 `UVehicleSimBaseComponent` 的子类，作为子组件附加到车辆 Actor 上，每个组件定义一种物理子系统。

| 组件 | 作用 |
|---|---|
| `VehicleSimEngineComponent` | 发动机参数（扭矩曲线、最大 RPM、怠速转速、引擎制动） |
| `VehicleSimTransmissionComponent` | 变速箱（齿比、自动/手动换挡、换挡时间） |
| `VehicleSimSuspensionComponent` | 悬挂系统（弹簧刚度、阻尼、预载、行程） |
| `VehicleSimWheelComponent` | 车轮参数（半径、摩擦力、制动扭矩、转向角度、ABS/TCS） |
| `VehicleSimChassisComponent` | 车身空气阻力与角阻尼 |
| `VehicleSimClutchComponent` | 离合器强度 |
| `VehicleSimAerofoilComponent` | 机翼/舵面/升降舵（升力、阻力、控制角度） |
| `VehicleSimThrusterComponent` | 推进器（最大推力、可转向、加速倍率） |

### 输入系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UVehicleDefaultInputProducer` | 默认输入生产者：从玩家输入设备捕获输入并缓冲，供物理线程消费 |
| `UVehiclePlaybackInputProducer` | 回放输入生产者：从预记录输入缓冲区中依次回放，用于测试或重播 |
| `UVehicleRandomInputProducer` | 随机输入生产者：在运行期间生成随机输入，用于压力测试 |
| `UInputModifier_ModularVehicleSmooth` | 输入平滑修饰器：为 float 输入（如转向）增加滞后感，模拟惯性 |

### 动画与可视化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAnimNode_ModularVehicleController` | 动画控制器节点（在动画蓝图中使用），根据车辆模块状态驱动骨骼变换 | `AnimNode_ModularVehicleController` |
| `UModularVehicleAnimationInstance` | 动画实例，暴露 `GetVehicle()` 获取车辆 Actor | |

### 网络与调试

| 节点 | 说明 |
|---|---|
| `FNetworkModularVehicleInputs` | 网络输入数据，用于客户端预测与服务器回滚 |
| `FModularReplicatedState` | 附加的复制状态（反向、保持唤醒等） |
| `ModularVehicleClusterActor` / `ModularVehicleClusterPawn` | 预设的车辆 Actor/Pawn 蓝图基类（包含 ClusterUnionVehicleComponent 和 ModularVehicleBaseComponent） |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ModularVehicleBaseComponent.h"
#include "ChaosModularVehicle/VehicleSimEngineComponent.h"
#include "ChaosModularVehicle/ChaosModularVehicleEnginePlugin.h"
```

### 基本用法

1. **在 Actor 上创建车辆组件**：

```cpp
// AMyVehicle.h
#include "ModularVehicleClusterPawn.h"

UCLASS()
class AMyVehicle : public AModularVehicleClusterPawn
{
    GENERATED_BODY()
public:
    AMyVehicle(const FObjectInitializer& OI);
};

// AMyVehicle.cpp
#include "VehicleSimEngineComponent.h"
#include "VehicleSimTransmissionComponent.h"
#include "VehicleSimSuspensionComponent.h"
#include "VehicleSimWheelComponent.h"

AMyVehicle::AMyVehicle(const FObjectInitializer& OI)
    : Super(OI)
{
    // 添加发动机模块
    UVehicleSimEngineComponent* Engine = CreateDefaultSubobject<UVehicleSimEngineComponent>(TEXT("Engine"));
    Engine->MaxTorque = 500.0f;
    Engine->MaxRPM = 6000;
    Engine->EngineIdleRPM = 800;
    Engine->SetupAttachment(GetClusterUnionComponent()); // 挂接到刚体组件

    // 添加变速箱模块
    UVehicleSimTransmissionComponent* Transmission = CreateDefaultSubobject<UVehicleSimTransmissionComponent>(TEXT("Transmission"));
    Transmission->ForwardRatios = {4.0f, 2.5f, 1.5f, 1.0f, 0.8f};
    Transmission->FinalDriveRatio = 3.5f;
    Transmission->SetupAttachment(GetClusterUnionComponent());

    // 添加悬挂和车轮（假设你有四个）
    UVehicleSimSuspensionComponent* SuspensionFL = CreateDefaultSubobject<UVehicleSimSuspensionComponent>(TEXT("SuspensionFL"));
    SuspensionFL->SuspensionMaxRaise = 10.0f;
    SuspensionFL->SpringRate = 100.0f;
    SuspensionFL->SetupAttachment(GetClusterUnionComponent());

    UVehicleSimWheelComponent* WheelFL = CreateDefaultSubobject<UVehicleSimWheelComponent>(TEXT("WheelFL"));
    WheelFL->WheelRadius = 30.0f;
    WheelFL->FrictionMultiplier = 1.0f;
    WheelFL->bSteeringEnabled = true;
    WheelFL->MaxSteeringAngle = 45.0f;
    WheelFL->SetupAttachment(SuspensionFL); // 车轮挂在悬挂下
}
```

2. **运行时调整输入**：通过 `UVehicleDefaultInputProducer` 并绑定到增强输入动作。

```cpp
// 在玩家控制器中注入输入
void AMyPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(InputComponent))
    {
        // 假设定义了两个动作：IA_Throttle（float）、IA_Steer（float）
        EnhancedInput->BindAction(IA_Throttle, ETriggerEvent::Triggered, this, &AMyPlayerController::SetThrottleInput);
        EnhancedInput->BindAction(IA_Steer, ETriggerEvent::Triggered, this, &AMyPlayerController::SetSteerInput);
    }
}

void AMyPlayerController::SetThrottleInput(const FInputActionValue& Value)
{
    // 通过 ModularVehicleBaseComponent 设置输入（需要获得车辆上的该组件）
    if (UModularVehicleBaseComponent* Vehicle = GetVehicleSimComponent())
    {
        FModuleInputValue InputVal(EModuleInputValueType::Float, Value.Get<float>());
        Vehicle->BufferInput(FName("Throttle"), InputVal, EModuleInputBufferActionType::Replace);
    }
}
```

### 进阶用法

1. **自定义输入生产者**：继承 `UVehicleInputProducerBase`，实现自定义输入逻辑（如 AI 驱动车辆）。

```cpp
UCLASS()
class UMyAIInputProducer : public UVehicleInputProducerBase
{
    GENERATED_BODY()
public:
    virtual void BufferInput(const FInputNameMap& InNameMap, const FName InName,
        const FModuleInputValue& InValue, EModuleInputBufferActionType BufferAction) override
    {
        // 忽略玩家输入，直接通过 AI 逻辑填充 buffer
    }

    virtual void ProduceInput(int32 PhysicsStep, int32 NumSteps,
        const FInputNameMap& InNameMap, FModuleInputContainer& InOutContainer) override
    {
        // 设置 AI 驾驶输入
        InOutContainer.Set(FName("Throttle"), FModuleInputValue(1.0f));
        InOutContainer.Set(FName("Steer"), FModuleInputValue(0.5f));
    }
};
```

2. **网络同步**：数据通过 `FNetworkModularVehicleInputs` 和 `FNetworkModularVehicleStates` 进行预测与回滚。在 `UModularVehicleBaseComponent` 中启用 `bUsingNetworkPhysicsPrediction` 即可。

```cpp
// 在设置组件后
VehicleComponent->bUsingNetworkPhysicsPrediction = true;
VehicleComponent->SetIsReplicated(true);
```

## Demo 示例

以下是一个可以编译的最小示例，展示如何创建一个可驾驶的车辆 Pawn。

**AMyModularCar.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ModularVehicleClusterPawn.h"
#include "MyModularCar.generated.h"

UCLASS()
class AMyModularCar : public AModularVehicleClusterPawn
{
    GENERATED_BODY()

public:
    AMyModularCar(const FObjectInitializer& OI = FObjectInitializer::Get());
};
```

**AMyModularCar.cpp**

```cpp
#include "MyModularCar.h"
#include "VehicleSimEngineComponent.h"
#include "VehicleSimTransmissionComponent.h"
#include "VehicleSimSuspensionComponent.h"
#include "VehicleSimWheelComponent.h"
#include "ChaosModularVehicle/InputProducer.h"

AMyModularCar::AMyModularCar(const FObjectInitializer& OI)
    : Super(OI)
{
    // 启用网格
    GetClusterUnionComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);

    // --- 发动机 ---
    UVehicleSimEngineComponent* Engine = CreateDefaultSubobject<UVehicleSimEngineComponent>(TEXT("Engine"));
    Engine->MaxTorque = 400.0f;          // Nm
    Engine->MaxRPM = 6500;
    Engine->EngineIdleRPM = 800;
    Engine->EngineBrakeEffect = 0.3f;
    Engine->EngineInertia = 0.1f;
    Engine->SetupAttachment(GetClusterUnionComponent());

    // --- 变速箱 ---
    UVehicleSimTransmissionComponent* Transmission = CreateDefaultSubobject<UVehicleSimTransmissionComponent>(TEXT("Transmission"));
    Transmission->ForwardRatios = { 3.5f, 2.0f, 1.3f, 1.0f, 0.8f };
    Transmission->ReverseRatios = { 3.0f };
    Transmission->FinalDriveRatio = 3.5f;
    Transmission->ChangeUpRPM = 5500;
    Transmission->ChangeDownRPM = 2000;
    Transmission->GearChangeTime = 0.5f;
    Transmission->TransmissionType = EModuleTransType::Automatic;
    Transmission->SetupAttachment(GetClusterUnionComponent());

    // --- 四个悬挂 + 车轮 (前轮转向) ---
    const float WheelRadius = 30.0f;
    const FVector SuspensionOffset(0, 0, -10); // 向下偏移

    // 左前
    UVehicleSimSuspensionComponent* SuspFL = CreateDefaultSubobject<UVehicleSimSuspensionComponent>(TEXT("SuspFL"));
    SuspFL->SuspensionMaxRaise = 8.0f;
    SuspFL->SuspensionMaxDrop = 8.0f;
    SuspFL->SpringRate = 200.0f;
    SuspFL->SpringDamping = 50.0f;
    SuspFL->SetupAttachment(GetClusterUnionComponent());

    UVehicleSimWheelComponent* WheelFL = CreateDefaultSubobject<UVehicleSimWheelComponent>(TEXT("WheelFL"));
    WheelFL->WheelRadius = WheelRadius;
    WheelFL->FrictionMultiplier = 1.2f;
    WheelFL->bSteeringEnabled = true;
    WheelFL->MaxSteeringAngle = 35.0f;
    WheelFL->bABSEnabled = true;
    WheelFL->SetupAttachment(SuspFL);

    // 右前（对称）
    UVehicleSimSuspensionComponent* SuspFR = CreateDefaultSubobject<UVehicleSimSuspensionComponent>(TEXT("SuspFR"));
    SuspFR->SuspensionMaxRaise = 8.0f;
    SuspFR->SuspensionMaxDrop = 8.0f;
    SuspFR->SpringRate = 200.0f;
    SuspFR->SpringDamping = 50.0f;
    SuspFR->SetupAttachment(GetClusterUnionComponent());

    UVehicleSimWheelComponent* WheelFR = CreateDefaultSubobject<UVehicleSimWheelComponent>(TEXT("WheelFR"));
    WheelFR->WheelRadius = WheelRadius;
    WheelFR->FrictionMultiplier = 1.2f;
    WheelFR->bSteeringEnabled = true;
    WheelFR->MaxSteeringAngle = 35.0f;
    WheelFR->bABSEnabled = true;
    WheelFR->SetupAttachment(SuspFR);

    // 左后（非转向）
    UVehicleSimSuspensionComponent* SuspRL = CreateDefaultSubobject<UVehicleSimSuspensionComponent>(TEXT("SuspRL"));
    SuspRL->SuspensionMaxRaise = 8.0f;
    SuspRL->SuspensionMaxDrop = 8.0f;
    SuspRL->SpringRate = 200.0f;
    SuspRL->SpringDamping = 50.0f;
    SuspRL->SetupAttachment(GetClusterUnionComponent());

    UVehicleSimWheelComponent* WheelRL = CreateDefaultSubobject<UVehicleSimWheelComponent>(TEXT("WheelRL"));
    WheelRL->WheelRadius = WheelRadius;
    WheelRL->FrictionMultiplier = 1.2f;
    WheelRL->bHandbrakeEnabled = true;
    WheelRL->HandbrakeTorque = 2000.0f;
    WheelRL->SetupAttachment(SuspRL);

    // 右后（对称）
    UVehicleSimSuspensionComponent* SuspRR = CreateDefaultSubobject<UVehicleSimSuspensionComponent>(TEXT("SuspRR"));
    SuspRR->SuspensionMaxRaise = 8.0f;
    SuspRR->SuspensionMaxDrop = 8.0f;
    SuspRR->SpringRate = 200.0f;
    SuspRR->SpringDamping = 50.0f;
    SuspRR->SetupAttachment(GetClusterUnionComponent());

    UVehicleSimWheelComponent* WheelRR = CreateDefaultSubobject<UVehicleSimWheelComponent>(TEXT("WheelRR"));
    WheelRR->WheelRadius = WheelRadius;
    WheelRR->FrictionMultiplier = 1.2f;
    WheelRR->bHandbrakeEnabled = true;
    WheelRR->HandbrakeTorque = 2000.0f;
    WheelRR->SetupAttachment(SuspRR);

    // 设置默认输入生产者
    if (UModularVehicleBaseComponent* Vehicle = GetVehicleSimComponent())
    {
        Vehicle->SetInputProducer(UVehicleDefaultInputProducer::StaticClass(), 0);
    }
}
```

**注意**：在实际项目中，还需处理输入绑定（通过 EnhancedInput 系统）和物理场景注册（由 `FChaosSimModuleManager` 自动完成）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosSolverEngine` | Chaos 解算器引擎，管理物理场景 |
| `ChaosCore` | Chaos 核心数学与容器 |
| `GeometryCollectionEngine` | 几何体集合支持（Cluster 合并） |
| `IrisCore` | Iris 复制系统，网络同步输入与状态 |
| `NetCore` | 基础网络支持 |
| `EnhancedInput` | 增强输入系统（.uplugin 中显式依赖） |

常见依赖（Core、Engine 等）未列出。

## 维护状态

### 近期更新

- 2025-08-20 `d07f96e3` — Potential crash fix
- 2025-08-19 `750fd0ee` — [ModularVehicle] Fixes up invalid nettoken hashing and initialization.
- 2025-08-14 `38822c46` — Removed unnecessary dependencies from Chaos Modular Vehicle plugin
- 2025-07-28 `b8b21b7a` — Fixes a few cases where physics solver time was being cached as a 32-bit float and possibly losing p
- 2025-07-28 `50f458c9` — ModularVehicle: Threading issue fix

### 维护评价

| 维度 | 情况 |
|---|---|
| 创建时间 | 2025 年 7 月 28 日（约 0 年前） |
| 最近更新 | 2025 年 8 月 20 日（近期频繁修复） |
| 更新内容 | 修复崩溃、线程问题、网络标记初始化、清理依赖 |
| 是否活跃维护 | **是**：当前正处于快速开发修复阶段 |
| 已知问题 | 无公开已知严重问题（但插件为实验性，可能存在 API 不稳定） |
| 推荐使用 | 可尝试用于原型/实验项目，不建议用于生产级正式产品（实验性阶段） |

该插件处于早期实验阶段，API 和架构可能发生变动。如果你需要稳定的车辆系统，建议使用稳定的 `ChaosVehicles` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle)
- [较稳定的车辆替代方案 (ChaosVehicles)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVehicles)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle/Tests)（若存在）