# Chaos Mover

> Chaos Mover is an Unreal Engine plugin to support Chaos physics based character movement using the Mover framework.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌运动器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、物理设置） |
| 模块 | `ChaosMover` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosMover) | |

## 用途

**解决什么问题？**  
UE 默认的角色运动组件（`UCharacterMovementComponent`）基于简单物理近似，不适合需要精确物理互动（如推拉、碰撞冲量传递、韧性地面等）的场景。  
`ChaosMover` 插件将 **Mover 框架**（抽象的运动状态机）与 **Chaos Physics**（Unreal 新一代物理引擎）结合，提供：

- **基于 Chaos 物理的角色运动**：角色通过物理约束与场景交互（如地面约束、关节约束），实现更加真实、稳定的运动响应。
- **可扩展的运动模式系统**：继承自 Mover 的 `UBaseMovementMode`，支持步行、飞行、游泳、降落、路径运动等模式，并允许用户通过蓝图/C++ 自定义。
- **异步物理模拟**：运动计算在物理线程（PT）上执行，减轻游戏线程负担，支持高帧率物理驱动。

## 使用场景

- 你需要角色在移动时与物理对象（如可推动的箱子、可破坏的墙壁）发生真实碰撞力，或需要角色在斜坡上精确贴合地面。
- 你想用 **Mover 框架** 管理复杂的状态切换（如行走→降落→游泳→飞行），但需底层使用 Chaos 物理解算。
- 制作需要精确物理交互的角色，如平台跳跃、VR 运动、载具驾驶员、攀爬系统等。
- 需要预定义路径的动画运动（如沿着椭圆轨道移动的敌人或传送带），可使用插件的 **Pathed Movement** 子系统。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UChaosCharacterMoverComponent::Launch` | 使用冲量或速度启动角色（启动发射模式） | `UChaosCharacterMoverComponent` |
| `UChaosCharacterMoverComponent::OverrideMovementSettings` | 临时覆盖当前运动模式的速度/加速度 | `UChaosCharacterMoverComponent` |
| `UChaosCharacterMoverComponent::CancelMovementSettingsOverrides` | 取消之前设置覆盖 | `UChaosCharacterMoverComponent` |
| `UChaosMoverSimulation::QueueInstantMovementEffect` | 立即执行一个瞬时运动效果（如爆炸冲击） | `UChaosMoverSimulation` |
| `UChaosMoverSimulation::QueueMovementModifier` | 队列一个运动修饰器（例如改变胶囊体大小） | `UChaosMoverSimulation` |
| `UChaosMoverSimulation::HasGameplayTag` | 检查模拟状态是否包含指定标签 | `UChaosMoverSimulation` |
| `UChaosMoverSimulation::FindMovementModeByName` | 按名称查找已注册的运动模式 | `UChaosMoverSimulation` |
| `UChaosPathedMovementControllerComponent::RequestStartPlayingPath` | 请求开始沿路径运动 | `UChaosPathedMovementControllerComponent` |
| `UChaosPathedMovementControllerComponent::RequestSetPathPlaybackPosition` | 设置路径播放进度（0~1） | `UChaosPathedMovementControllerComponent` |
| `UChaosPathedMovementMode::BP_FindPattern` | 按类型查找路径模式 | `UChaosPathedMovementMode` |
| `UChaosCharacterMovementMode::GetMaxSpeed` | 获取当前运动模式的最大速度（可被覆盖） | `UChaosCharacterMovementMode` |

### 使用示例（蓝图描述）

**1. 角色跳跃**  
- 在 `UChaosCharacterMoverComponent` 上挂钩 `OnJumped` 事件（`FChaosMover_OnJumped`）。
- 当 `UChaosCharacterJumpCheck` 检测到跳按钮输入时，会自动应用垂直速度并切换到指定运动模式。

**2. 临时加速**  
- 调用 `OverrideMovementSettings`，传入 `FChaosMovementSettingsOverrides` 结构体，设置 `MaxSpeedOverride = 1200.0`。
- 调用 `CancelMovementSettingsOverrides` 移除覆盖。

**3. 路径运动**  
- 在蓝图类中添加 `UChaosPathedMovementMode` 作为运动模式，并添加一个 `UChaosEllipticalMovementPathPattern` 子对象，设置椭圆半径。
- 挂载 `UChaosPathedMovementControllerComponent`，在 BeginPlay 调用 `RequestStartPlayingPath`（执行类型选 `ClientPredicted_AutonomousOnly` 以支持预测）。

**4. 发射角色**  
- 调用 `UChaosCharacterMoverComponent` 的 `Launch` 节点，指定速度和模式（AdditiveVelocity 或 SetVelocity）。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosMover/ChaosCharacterMoverComponent.h"
#include "ChaosMover/ChaosMoverSimulation.h"
#include "ChaosMover/Character/Modes/ChaosWalkingMode.h"
```

### 基本用法

从测试用例提取（假设测试位于 `Engine/Source/Programs/UnrealInsights/Private/Tests/ChaosMover`，但插件自身测试较少，我们使用公开头文件接口）：

```cpp
// 创建 Chaos 角色运动组件
UChaosCharacterMoverComponent* MoverComp = NewObject<UChaosCharacterMoverComponent>(GetOwner());
MoverComp->RegisterComponent();

// 注册运动模式（示例：行走模式）
UChaosWalkingMode* WalkMode = NewObject<UChaosWalkingMode>();
WalkMode->MaxWalkSpeed = 600.0f;
WalkMode->Acceleration = 2000.0f;
MoverComp->AddMovementMode("Walking", WalkMode, /*bDefault=*/true);
```

### 进阶用法

**1. 使用运动修饰器改变胶囊体**  
```cpp
#include "ChaosMover/Character/Modifiers/ChaosStanceModifier.h"

TSharedPtr<FChaosStanceModifier> Modifier = MakeShared<FChaosStanceModifier>();
Modifier->ModifiedCapsuleHalfHeight = 40.0f;
Modifier->ModifiedCapsuleRadius = 30.0f;
MoverComp->GetSimulation()->QueueMovementModifier(Modifier);
```

**2. 创建自定义运动模式**  
```cpp
// CustomChaosFlyingMode.h
#include "ChaosMover/Character/Modes/ChaosFlyingMode.h"
UCLASS()
class UMyFlyingMode : public UChaosFlyingMode
{
    GENERATED_BODY()
public:
    virtual void GenerateMove_Implementation(const FMoverTickStartData& StartState, 
        const FMoverTimeStep& TimeStep, FProposedMove& OutProposedMove) const override;
};
```

## Demo 示例

以下是一个最小示例，展示如何创建一个使用 Chaos Mover 的 Pawn 并覆盖其运动模式。

**PawnPawn.h**  
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "ChaosMover/ChaosCharacterMoverComponent.h"
#include "ChaosMover/Character/Modes/ChaosFlyingMode.h"
#include "PawnPawn.generated.h"

UCLASS()
class APawnPawn : public APawn
{
    GENERATED_BODY()

public:
    APawnPawn();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "ChaosMover")
    UChaosCharacterMoverComponent* MoverComponent;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ChaosMover")
    TSubclassOf<UChaosFlyingMode> FlyingModeClass;
};
```

**PawnPawn.cpp**  
```cpp
#include "PawnPawn.h"

APawnPawn::APawnPawn()
{
    PrimaryActorTick.bCanEverTick = true;
    MoverComponent = CreateDefaultSubobject<UChaosCharacterMoverComponent>(TEXT("ChaosMover"));
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("RootComponent"));
}

void APawnPawn::BeginPlay()
{
    Super::BeginPlay();

    // 注册一个默认的飞行模式
    if (FlyingModeClass)
    {
        UChaosFlyingMode* FlyingMode = NewObject<UChaosFlyingMode>(this, FlyingModeClass);
        FlyingMode->MaxSpeed = 1000.0f;
        MoverComponent->AddMovementMode("Flying", FlyingMode, /*bDefault=*/true);
    }
}
```

在项目设置中启用 ChaosMover 插件，并将该 Pawn 放置到场景中，即可体验基于 Chaos 物理的飞行。

## 模块依赖

**特有依赖**（省略标准 Core/Engine/UMG 等）：

| 模块 | 用途 |
|---|---|
| `Mover` | 提供运动框架核心（状态机、输入、同步等） |
| `Chaos` | Chaos 物理引擎（粒子、约束、求解器） |
| `StructUtils` | 使用 `TInstancedStruct` 支持动态结构体 |
| `GameplayTags` | 用于运动模式、修饰器的标签系统 |
| `NetCore` | 网络序列化和复制 |

## 维护状态

### 近期更新

- 2025-10-14 [8159775] — [Newton] - Fixes for maintaining sprint when landing
- 2025-10-02 [b71eb52] — ChaosMover - Update floor each frame
- 2025-10-02 [945db01] — Avoid possible null refs when using blackboard
- 2025-10-01 [ddf89af] — Mover: adding rollback blackboard support to Chaos Mover simulations, along with mode change records
- 2025-09-27 [2c206fe] — Merging //Fortnite/Main to Release-38.00 (初始导入)

### 维护评价

- **创建时间**：2025 年 9 月（约 0 年）。
- **近期更新**：几乎周更，涉及物理同步、空指针修复、功能增强（如落地保持冲刺）。
- **状态**：活跃维护中，更新密集且聚焦于物理运动体验。
- **已知限制**：属于实验性插件，API 可能不稳定；需要同时启用 `Mover` 插件；异步物理调试较复杂。
- **推荐**：对于需要 Chaos 物理驱动的角色运动项目，此插件是官方首选方案。适合 UE5.5+ 项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosMover)
- [Mover 插件文档](https://docs.unrealengine.com/5.4/zh-CN/mover-plugin-in-unreal-engine/)（当 Mover 有独立文档时参考）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosMover/Tests)（存在时，插件当前可能没有公开测试文件）