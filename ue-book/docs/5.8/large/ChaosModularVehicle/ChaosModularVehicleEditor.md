# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（车辆资产、调试资源） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

本插件基于 UE5 的 Chaos 物理系统，提供了一套模块化车辆框架。与标准的 `ChaosVehicleMovementComponent` 相比，它旨在让开发者能够更精细地组装和控制车辆的各个物理部件（如独立的引擎、变速箱、轮子等），而非仅将其视为一个黑盒整体。这对于需要高度自定义车辆物理行为、实现复杂车辆系统（如赛车模拟）或构建可编程车辆组件的项目非常有用。

## 使用场景

-   **赛车模拟游戏**：你需要分别控制引擎扭矩曲线、变速箱换挡逻辑、差速器类型等，以获得真实的驾驶感受。
-   **车辆改装系统**：你的游戏允许玩家更换不同的引擎、轮胎或悬挂，这些组件需要能动态影响整体车辆物理。
-   **物理原型开发**：你需要快速迭代和测试不同的车辆配置（如不同数量的驱动轮、不同的传动布局），而无需为每种配置编写新的代码。
-   **网络同步的车辆**：你希望车辆的物理状态能在网络游戏中准确、平滑地同步。

## 蓝图用法

### 核心节点

基于代码分析，本插件主要在动画蓝图和车辆配置资产层面提供蓝图接口。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Modular Vehicle Controller` (AnimGraphNode) | 动画蓝图节点，用于根据车辆的物理状态（如悬挂压缩、转向）驱动骨骼网格体的动画。 | `UAnimGraphNode_ModularVehicleController` |
| 车辆组件属性 | 在 `ChaosModularVehicleComponent` 或其子类上，各种标记为 `UPROPERTY(EditAnywhere, BlueprintReadWrite)` 的参数，如引擎扭矩、变速箱档位设置等，可在蓝图或资产中配置。 | (Various UClasses) |
| 调试绘制 | 用于在运行时显示车辆各模块的调试信息（如轮子碰撞、扭矩输出）。 | `UChaosModularVehicleDebugComponent` |

### 使用示例（蓝图描述）

1.  **动画蓝图设置**：
    -   在角色的动画蓝图中，添加 `UAnimGraphNode_ModularVehicleController` 节点。
    -   将该节点连接在状态机之后、最终输出节点之前。
    -   在节点的细节面板中，配置其 `Node` 属性，指定要读取哪个车辆组件的物理数据来驱动动画。
    -   **注意**：该节点仅能在继承自 `UVehicleAnimInstance` 的动画蓝图中使用。

2.  **车辆配置**：
    -   创建继承自 `UChaosModularVehicleComponent` 的蓝图类。
    -   在细节面板中，寻找并配置引擎、变速箱等子对象的参数（具体属性名需查看 `ChaosModularVehicleEngine` 模块）。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosModularVehicleComponent.h"
#include "ChaosModularVehicleSimulation.h"
```

### 基本用法（创建并配置车辆组件）

以下代码展示了如何以编程方式设置一个模块化车辆组件的基本参数。

```cpp
// MyVehicle.h
#pragma once
#include "GameFramework/Pawn.h"
#include "ChaosModularVehicleComponent.h"
#include "MyVehicle.generated.h"

UCLASS()
class AMyVehicle : public APawn
{
	GENERATED_BODY()

public:
	AMyVehicle();

	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	// 车辆物理组件
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Vehicle")
	TObjectPtr<UChaosModularVehicleComponent> VehicleComponent;
};

// MyVehicle.cpp
#include "MyVehicle.h"
#include "ChaosModularVehicleComponent.h"

AMyVehicle::AMyVehicle()
{
	VehicleComponent = CreateDefaultSubobject<UChaosModularVehicleComponent>(TEXT("VehicleComponent"));
	SetRootComponent(VehicleComponent);
	// 初始化后，可在此处设置初始配置，例如启用物理模拟
	// VehicleComponent->SetSimulatePhysics(true);
}

void AMyVehicle::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	// 绑定输入轴到车辆组件的对应方法
	// 例如：PlayerInputComponent->BindAxis("Throttle", this, &AMyVehicle::ApplyThrottle);
}

// 应用输入（示例）
void AMyVehicle::ApplyThrottle(float Value)
{
	if (VehicleComponent)
	{
		// 调用车辆组件公开的控制方法
		// VehicleComponent->SetThrottleInput(Value);
	}
}
```

*(注：具体的输入绑定函数如 `SetThrottleInput` 需从 `ChaosModularVehicleSimulation` 或相关类中查看)*

### 进阶用法（网络同步与调试）

模块化车辆设计考虑了网络同步。你需要重写 `GetLifetimeReplicatedProps` 来复制关键状态，并可能需要处理 `OnRep` 函数来平滑客户端预测。

```cpp
// 在 AMyVehicle.h 中
UPROPERTY(ReplicatedUsing=OnRep_VehicleState)
FChaosModularVehicleReplicatedState VehicleState;

UFUNCTION()
void OnRep_VehicleState();

// 在 AMyVehicle.cpp 中
void AMyVehicle::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(AMyVehicle, VehicleState);
}

void AMyVehicle::OnRep_VehicleState()
{
	// 根据服务器同步过来的状态更新本地车辆
	// VehicleComponent->ApplyReplicatedState(VehicleState);
}
```

*(注：`FChaosModularVehicleReplicatedState` 结构体需根据实际同步需求定义)*

## Demo 示例

一个最小的、可运行的模块化车辆 Pawn 示例。

```cpp
// MinimalModularVehiclePawn.h
#pragma once
#include "GameFramework/Pawn.h"
#include "MinimalModularVehiclePawn.generated.h"

class UChaosModularVehicleComponent;
class UFloatingPawnMovement; // 或使用Chaos车辆的移动

UCLASS()
class AMinimalModularVehiclePawn : public APawn
{
	GENERATED_BODY()

public:
	AMinimalModularVehiclePawn();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UChaosModularVehicleComponent> VehicleComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UFloatingPawnMovement> MovementComp; // 示例，实际可能用Chaos移动
};
```

```cpp
// MinimalModularVehiclePawn.cpp
#include "MinimalModularVehiclePawn.h"
#include "ChaosModularVehicleComponent.h"
#include "GameFramework/FloatingPawnMovement.h"

AMinimalModularVehiclePawn::AMinimalModularVehiclePawn()
{
	PrimaryActorTick.bCanEverTick = true;

	VehicleComp = CreateDefaultSubobject<UChaosModularVehicleComponent>(TEXT("VehiclePhysics"));
	SetRootComponent(VehicleComp);

	// 浮动移动组件仅用于本演示的简单控制，实际应接入Chaos车辆输入
	MovementComp = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("Movement"));
	MovementComp->UpdatedComponent = VehicleComp;
}

void AMinimalModularVehiclePawn::BeginPlay()
{
	Super::BeginPlay();
	// 确保物理组件开始模拟
	if (VehicleComp)
	{
		VehicleComp->SetSimulatePhysics(true);
		VehicleComp->SetEnableGravity(true);
	}
}

void AMinimalModularVehiclePawn::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AMinimalModularVehiclePawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	// 这里应绑定您的输入到VehicleComp的相关方法，例如转向、油门、刹车。
	// 例如：PlayerInputComponent->BindAxis("MoveForward", this, &AMinimalModularVehiclePawn::MoveForward);
}
```

## 模块依赖

从 Build.cs 文件分析，使用本插件需要在你的模块构建文件（.Build.cs）中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PhysicsCore` | Chaos 物理系统核心接口。 |
| `ChaosVehiclesCore` | Chaos 车辆系统的核心类型和接口。 |
| `ChaosSolverEngine` | Chaos 物理求解器引擎。 |
| `Chaos` | Chaos 物理框架。 |
| `ChaosModularVehicle` | 本插件的运行时核心模块。 |
| `ChaosModularVehicleEngine` | 本插件的车辆引擎模块（提供具体的发动机、变速箱等逻辑）。 |

*(注：`ChaosModularVehicleEditor` 模块是编辑器专用，你的运行时游戏模块不需要依赖它。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复了调试显示中引擎扭矩始终为 0 的问题 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复了在网络环境下，简化骨骼网格体模式的车辆设置问题 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复了模块化车辆中，物理线程上 `IsLocallyControlled` 的断言失败问题 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instead | 模块化车辆改为依赖 `NetworkPhysicsComponent` 的 `IsLocallyControlled` |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移至 UE_LOGF 格式 |

### 维护评价

-   **活跃度**：该插件处于**积极维护**状态。最近的提交（2026 年 5 月）集中在修复 bug 和改进网络同步，表明 Epic 团队仍在投入资源。
-   **稳定性**：从提交记录看，近期工作主要围绕稳定性修复，尤其是针对**网络同步**场景的准确性，这对于多人游戏至关重要。
-   **实验性**：插件仍标记为 `IsExperimentalVersion=true`，`Installed=false`（不默认安装），这表明 API 可能尚未完全稳定，未来版本存在变动的可能性。
-   **推荐度**：**推荐用于实验性项目或原型开发**。如果你需要高度模块化和可定制的车辆物理，并且愿意接受未来可能的 API 变更，这是一个很有潜力的选择。对于追求稳定性的生产项目，建议密切关注其版本变更，或作为技术储备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
-   [官方文档]() (暂无)
-   [测试用例]() (测试文件路径未在提供信息中明确列出，通常位于 `Engine/Tests/` 或插件内 `Tests/` 目录下，需自行查找)