# Chaos Modular Vehicle

> Modular Vehicle Integration（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

该插件是一个**模块化的车辆物理系统**，允许开发者通过组合和配置不同的物理模拟模块（如发动机、变速箱、悬挂、车轮、气动翼面等）来构建车辆。它旨在替代或增强传统的“单体式”车辆物理模型，提供更高的灵活性和可定制性。

核心解决的问题是：当游戏需要高度定制化的载具物理行为（例如，赛车游戏中的精细调校、载具组装玩法、模拟飞机/气垫船等特殊载具）时，传统车辆组件难以满足需求。该插件通过将车辆分解为独立的物理模拟组件，并提供网络同步（预测与回滚）、物理线程异步模拟、输入缓冲/量化等高级功能，使开发者能够构建复杂、可联网的模块化载具系统。

## 使用场景

-   **开发赛车或竞速游戏**：需要精细调校悬挂软硬、发动机扭矩曲线、变速箱齿比、空气动力学等参数，并支持网络同步。
-   **制作载具组装玩法**：允许玩家在运行时动态添加或移除车辆部件（如轮子、引擎），部件的变化会实时影响车辆的物理行为。
-   **模拟非传统载具**：需要实现飞机（通过 Wing/Propeller 组件）、气垫船（通过 Balloon/Thruster 组件）、或带有特殊物理效果的科幻载具。
-   **需要高保真网络同步**：载具状态需要在网络游戏中平滑预测和回滚，以减少延迟感。

## 蓝图用法

该插件的核心功能通过 `UModularVehicleBaseComponent` 类暴露给蓝图。大部分交互是设置输入和查询状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputBool` | 设置布尔类型输入（如手刹、倒车） | `UModularVehicleBaseComponent` |
| `SetInputAxis1D` | 设置一维轴输入（如油门、刹车、转向） | `UModularVehicleBaseComponent` |
| `SetGearInput` | 设置目标档位 | `UModularVehicleBaseComponent` |
| `GetCurrentGear` | 获取当前实际档位 | `UModularVehicleBaseComponent` |
| `IsReversing` | 查询是否处于倒车状态 | `UModularVehicleBaseComponent` |
| `SetInputProducerClass` | 设置用于处理输入的生成器类 | `UModularVehicleBaseComponent` |
| `SetLocallyControlled` | 设置该载具是否由本地控制（用于网络） | `UModularVehicleBaseComponent` |
| `AddActorsToIgnore` / `RemoveActorsToIgnore` | 管理悬挂检测（Raycast/Spherecast）要忽略的 Actor | `UModularVehicleBaseComponent` |
| `OnModuleAddedEvent` | 当模块被添加到载具模拟树时触发的事件 | `UModularVehicleBaseComponent` |

### 使用示例（蓝图描述）

1.  **创建载具**：从 `AModularVehicleClusterPawn` 或 `AModularVehicleClusterActor` 开始，它们在 `BeginPlay` 时会自动创建 `UClusterUnionVehicleComponent` 和 `UModularVehicleBaseComponent`。
2.  **组装模块**：在编辑器中将各种 `UVehicleSim*Component`（如 `UVehicleSimEngineComponent`）作为子组件附加到 `UClusterUnionVehicleComponent` 下。确保组件间有正确的父子关系（例如，车轮组件是悬挂组件的子级）。
3.  **输入处理**：在载具的 Pawn/Controller 蓝图中，在 `Tick` 或输入事件中，调用 `SetInputAxis1D` 等节点来传递油门、转向等值给 `ModularVehicleBaseComponent`。
4.  **查询状态**：使用 `GetCurrentGear`、`IsReversing` 等节点来获取载具当前状态，用于 UI 显示或音效控制。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ModularVehicleBaseComponent.h"
#include "ChaosModularVehicle/ChaosSimModuleManagerAsyncCallback.h"
// 包含具体模块组件，例如：
#include "ChaosModularVehicle/VehicleSimEngineComponent.h"
#include "ChaosModularVehicle/VehicleSimWheelComponent.h"
```

### 基本用法

以下代码展示了如何在 C++ 中设置模块化车辆输入和获取状态。
（来源文件：`Public/ChaosModularVehicle/ModularVehicleBaseComponent.h`）

```cpp
// 假设你已经通过 GetVehicleSimulationComponent() 获取了有效的 UModularVehicleBaseComponent* VehicleComp
if (VehicleComp)
{
    // 设置转向输入（范围通常为 -1.0 到 1.0）
    VehicleComp->SetInputAxis1D(FName("Steer"), CurrentSteerValue);

    // 设置油门输入（0.0 到 1.0）
    VehicleComp->SetInputAxis1D(FName("Throttle"), CurrentThrottleValue);

    // 设置手刹（布尔输入）
    VehicleComp->SetInputBool(FName("Handbrake"), bWantsHandbrake);

    // 设置目标档位
    VehicleComp->SetGearInput(TargetGear);

    // 查询状态
    int32 CurrentGear = VehicleComp->GetCurrentGear();
    bool bIsReversing = VehicleComp->IsReversing();

    // 设置本地控制（对网络同步很重要）
    VehicleComp->SetLocallyControlled(true);
}
```

### 进阶用法

**1. 动态添加/移除模拟模块：**
可以通过 `AddSimModule` 和 `RemoveSimModule` 在运行时修改载具的模拟树结构。这通常在载具组装逻辑中使用。
（来源：`Public/ChaosModularVehicle/ModularVehicleBaseComponent.h`）

```cpp
// 创建一个新的模拟模块（例如，一个自定义的 FSuspensionSimModule）
Chaos::FSuspensionSettings Settings;
Settings.SpringRate = 5000.f;
// ... 配置其他参数 ...
auto NewSuspensionModule = MakeUnique<FSuspensionSimModule>(Settings);

// 将其添加到车辆模拟树中
int32 NewGuid = VehicleComp->AddSimModule(NewSuspensionModule.Get(), ComponentTransform, ParentIndex, TransformIndex);
// 模块所有权转移给车辆组件，无需手动删除指针

// 稍后移除该模块
VehicleComp->RemoveSimModule(NewGuid);
VehicleComp->FinalizeModuleUpdates(); // 提交树结构的变更
```

**2. 配置输入系统：**
输入名称（如 "Throttle"）需要与 `InputConfig` 数组中的 `FModuleInputSetup` 的 `Name` 字段匹配。
（来源：`Public/ChaosModularVehicle/ModularVehicleBaseComponent.h`）

```cpp
// 在构造函数或初始化函数中配置输入
void AMyVehicle::SetupInputs()
{
    UModularVehicleBaseComponent* VehicleComp = GetVehicleSimulationComponent();
    if (VehicleComp)
    {
        // 使用预设的配置数组，或在代码中动态添加
        FModuleInputSetup ThrottleSetup;
        ThrottleSetup.Name = FName("Throttle");
        ThrottleSetup.Type = EModuleInputType::Axis1D; // 或根据你的输入类型
        ThrottleSetup.QuantizationType = EModuleInputQuantizationType::Default_16Bits;
        VehicleComp->InputConfig.Add(ThrottleSetup);
        // ... 为 Steer, Brake 等添加类似配置
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个包含基础组件的模块化车辆 Actor。
（注意：这是一个简化示例，实际项目需要根据需求配置物理参数和约束。）

**MyModularVehicle.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosModularVehicle/ModularVehicleClusterActor.h"
#include "MyModularVehicle.generated.h"

UCLASS()
class AMyModularVehicle : public AModularVehicleClusterActor
{
    GENERATED_BODY()

public:
    AMyModularVehicle();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UVehicleSimEngineComponent> EngineComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UVehicleSimWheelComponent> FrontLeftWheelComponent;

    // ... 其他组件
};
```

**MyModularVehicle.cpp**
```cpp
#include "MyModularVehicle.h"
#include "ChaosModularVehicle/VehicleSimEngineComponent.h"
#include "ChaosModularVehicle/VehicleSimWheelComponent.h"

AMyModularVehicle::AMyModularVehicle()
{
    PrimaryActorTick.bCanEverTick = true;

    // 父类 (AModularVehicleClusterActor) 已经创建了 ClusterUnionVehicleComponent 和 VehicleSimComponent
    // 我们只需创建并附加子组件

    EngineComponent = CreateDefaultSubobject<UVehicleSimEngineComponent>(TEXT("Engine"));
    EngineComponent->SetupAttachment(ClusterUnionVehicleComponent);
    // 配置引擎参数
    EngineComponent->MaxRPM = 8000;
    EngineComponent->EngineIdleRPM = 800;
    // ... 设置其他属性

    FrontLeftWheelComponent = CreateDefaultSubobject<UVehicleSimWheelComponent>(TEXT("FLWheel"));
    FrontLeftWheelComponent->SetupAttachment(EngineComponent); // 假设轮子挂在引擎下（示例）
    FrontLeftWheelComponent->WheelRadius = 30.f;
    FrontLeftWheelComponent->bSteeringEnabled = true;
    // ... 设置其他属性

    // 在编辑器中，你可以继续添加悬挂、变速箱等组件，并通过属性面板设置参数
}

void AMyModularVehicle::BeginPlay()
{
    Super::BeginPlay();
    // 车辆物理模拟会在父类的 BeginPlay 中基于附加的组件自动初始化
}

void AMyModularVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 这里可以添加每帧的游戏逻辑，例如根据输入更新 UI
    // 物理模拟的输入设置应在控制器或 Pawn 的输入处理逻辑中调用 VehicleSimComponent->SetInput...
}
```

## 模块依赖

要使用此插件，你的游戏模块需要依赖以下独特模块（通过你的模块的 `Build.cs` 文件）：

| 模块 | 用途 |
|---|---|
| `ChaosModularVehicle` | 提供基础车辆组件和网络结构体 |
| `ChaosModularVehicleEngine` | 提供核心的物理模拟逻辑和工厂 |
| `ChaosPhysics` | Chaos 物理系统的核心 |
| `ChaosVehicles` | Chaos 车辆框架（提供基础车辆模拟接口） |
| `ChaosSolverEngine` | Chaos 物理求解器引擎 |
| `NetworkPhysics` | 网络物理同步组件和预测/回滚框架 |
| `ClusterUnion` | 用于组合多个物理体（VehicleSimComponents）为一个刚体 |
| `EnhancedInput` | （插件依赖声明）用于处理输入映射 |

**注意**：如果只使用 `AModularVehicleClusterActor` 或 `AModularVehicleClusterPawn` 进行蓝图开发，可能只需在 `.uplugin` 中启用插件即可。但若要在 C++ 中继承或深度集成，需要添加以上模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复调试信息中发动机扭矩始终显示为0的问题 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复简化骨骼网格体在网络模式下的车辆设置问题 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复模块化车辆在物理线程上访问 IsLocallyControlled 时的断言失败 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instea | 改用 NetworkPhysicsComponent 来判断本地控制状态 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出迁移到新的 UE_LOGF 宏 |

### 维护评价

该插件**处于积极维护状态**。
- **年龄**：创建于 2023 年底，是一个相对年轻的插件。
- **活跃度**：从 Git 历史看，最近几个月（2026年4-5月）有**持续且实质性**的更新，主要聚焦于**网络同步稳定性**、**物理线程安全性**和**调试功能**的修复与改进。
- **实验性**：插件明确标记为实验性 (`IsExperimentalVersion=true`)，且默认未启用 (`EnabledByDefault=false`)，表明 Epic 仍在对其进行开发和验证，API 可能会有变动。
- **推荐使用**：非常适合**实验性项目**或需要高度定制化、联网载具物理的**正式项目**。由于其模块化和网络同步能力强，是 UE5 中构建复杂载具系统的优选方案。但开发者需做好应对 API 变更和潜在 Bug 的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- 官方文档（插件 .uplugin 中未提供 `DocsURL`）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle/Tests) （如果存在，路径通常如此）