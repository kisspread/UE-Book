# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 混沌模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画资源） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle) | |

---

## 用途

Chaos Modular Vehicle 是 UE5 Chaos 物理系统下的模块化车辆插件。它允许将车辆分解为多个独立物理部件（如车身、车轮、悬挂等），每个部件作为独立的物理体通过约束连接，从而实现高度可定制的车辆行为。相比传统的单一刚体车辆，模块化车辆支持更真实的物理破坏、部件分离和复杂悬挂模拟。

该插件处于实验阶段，旨在为未来 Chaos Vehicle 系统提供更灵活的架构基础。

---

## 使用场景

- 制作需要真实物理悬挂和轮胎交互的越野车、赛车
- 实现车辆部件可损坏（如车轮脱落、车身变形）
- 开发需要多体动力学模拟的特种车辆（如卡车挂车、坦克履带）
- 与 Enhanced Input 输入系统结合，实现精确的油门、刹车、转向控制

---

## 蓝图用法

### 核心动画节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Modular Vehicle Controller` (动画图表节点) | 在动画蓝图中应用车辆物理状态到骨架网格体。需要连接在 SkeletalControl 链上，通常用于驱动车辆动画 | `UAnimGraphNode_ModularVehicleController` -> `FAnimNode_ModularVehicleController` |

**使用示例（蓝图描述）**：
1. 创建一个继承自 `VehicleAnimInstance` 的动画蓝图（插件提供的基础类）。
2. 在动画图表中放置“Modular Vehicle Controller”节点。
3. 将骨骼控制结果连接到输出姿势。
4. 设置节点属性：绑定目标车辆组件（`UModularVehicleComponent`）。
5. 编译动画蓝图并应用到车辆蓝图中的骨骼网格体组件。

### 车辆组件

插件运行时模块提供 `UModularVehicleComponent`，可在蓝图中通过“创建模块化车辆组件”节点（或直接添加组件）进行配置。该组件暴露了车轮数量、悬挂参数、发动机扭矩等属性，但当前版本中部分属性可能标记为实验性或仅 C++ 可访问。

---

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicle/ModularVehicleComponent.h"
#include "ChaosModularVehicle/AnimNode_ModularVehicleController.h"
```

### 基本用法

```cpp
// 在角色或 Actor 中创建组件
#include "ModularVehicleComponent.h"

AMyVehicle::AMyVehicle()
{
    VehicleComponent = CreateDefaultSubobject<UModularVehicleComponent>(TEXT("VehicleComponent"));
}

// 在 Tick 中更新输入（假设你使用 Enhanced Input）
void AMyVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (VehicleComponent)
    {
        VehicleComponent->SetThrottleInput(ThrottleValue);
        VehicleComponent->SetSteeringInput(SteeringValue);
        VehicleComponent->SetBrakeInput(BrakeValue);
    }
}
```

### 进阶用法

```cpp
// 访问车轮状态
TArray<FModularVehicleWheelState> WheelStates = VehicleComponent->GetWheelStates();
for (int32 i = 0; i < WheelStates.Num(); i++)
{
    const FModularVehicleWheelState& Wheel = WheelStates[i];
    // 读取车轮角速度、滑移率、接触力等
}

// 应用外力到特定部件
VehicleComponent->ApplyForceToPart(PartIndex, ForceVector, WorldPosition);

// 设置手刹
VehicleComponent->SetHandbrakeInput(true);

// 动画蓝图中的节点绑定
// 在 AnimInstance 中获取节点引用
FAnimNode_ModularVehicleController* VehicleNode = GetNodeFromGraph<FAnimNode_ModularVehicleController>();
if (VehicleNode)
{
    VehicleNode->SetVehicleComponent(VehicleComponent);
}
```

---

## Demo 示例

### MinimalVehicleActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "ModularVehicleComponent.h"
#include "MinimalVehicleActor.generated.h"

UCLASS()
class AMinimalVehicleActor : public APawn
{
    GENERATED_BODY()

public:
    AMinimalVehicleActor();

    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Vehicle")
    UModularVehicleComponent* VehicleComponent;

protected:
    void OnThrottle(const FInputActionValue& Value);
    void OnSteering(const FInputActionValue& Value);
    void OnBrake(const FInputActionValue& Value);
};
```

### MinimalVehicleActor.cpp

```cpp
#include "MinimalVehicleActor.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"

AMinimalVehicleActor::AMinimalVehicleActor()
{
    PrimaryActorTick.bCanEverTick = true;

    VehicleComponent = CreateDefaultSubobject<UModularVehicleComponent>(TEXT("VehicleComponent"));
    RootComponent = VehicleComponent; // 或将组件附加到场景根
}

void AMinimalVehicleActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 车辆物理自动由 Chaos 更新
}

void AMinimalVehicleActor::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        // 假设已经在项目中配置了 IA_Throttle, IA_Steering, IA_Brake
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetController<APlayerController>()))
        {
            // 这里可以添加映射上下文
        }

        EnhancedInput->BindAction(ThrottleAction, ETriggerEvent::Triggered, this, &AMinimalVehicleActor::OnThrottle);
        EnhancedInput->BindAction(SteeringAction, ETriggerEvent::Triggered, this, &AMinimalVehicleActor::OnSteering);
        EnhancedInput->BindAction(BrakeAction, ETriggerEvent::Triggered, this, &AMinimalVehicleActor::OnBrake);
    }
}

void AMinimalVehicleActor::OnThrottle(const FInputActionValue& Value)
{
    VehicleComponent->SetThrottleInput(Value.Get<float>());
}

void AMinimalVehicleActor::OnSteering(const FInputActionValue& Value)
{
    VehicleComponent->SetSteeringInput(Value.Get<float>());
}

void AMinimalVehicleActor::OnBrake(const FInputActionValue& Value)
{
    VehicleComponent->SetBrakeInput(Value.Get<float>());
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | 混沌物理引擎核心 |
| `ChaosVehiclesCore` | 车辆物理核心类型（车轮、悬挂等） |
| `AnimGraphRuntime` | 动画节点运行时支持 |
| `EnhancedInput` | 增强输入系统（插件显式依赖） |
| `ProceduralMeshComponent` | 可能用于部件网格生成（待确认） |

**编辑器模块额外依赖**：
- `AnimGraph` (编辑器动画图表)
- `BlueprintGraph` (蓝图节点)
- `UnrealEd` (编辑器基础)

> 注意：以上依赖基于插件 `.uplugin` 中声明的 `Plugins` 字段以及常见混沌车辆依赖推断。实际 Build.cs 中可能包含更多私有依赖。

---

## 维护状态

### 近期更新

```
- 2025-08-20 d07f96e 潜在崩溃修复
- 2025-08-19 750fd0e [ModularVehicle] 修复无效网络令牌哈希和初始化问题
- 2025-08-14 38822c4 移除不必要的依赖
- 2025-07-28 b8b21b7 修复物理求解器时间作为 32 位浮点数缓存可能丢失精度的问题
- 2025-07-28 50f458c ModularVehicle: 线程安全问题修复
```

### 维护评价

- **创建时间**：2025年7月28日，距今约3个月。
- **近期更新**：几乎每月都有提交，包括功能修复和稳定性改进，表明团队正在积极开发。
- **活跃度**：高，最近一个月内有多个提交。
- **实验性状态**：`IsExperimentalVersion=true`，版本号为0.1，说明功能尚未稳定，API 可能变动。
- **推荐使用**：适合愿意尝试新技术并反馈问题的开发者，不适用于生产项目。请定期关注更新以获取修复和改进。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle/Tests)（需验证是否存在）
- 官方文档：暂未提供