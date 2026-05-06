# Mover Examples

> Non-essential classes and content for the Mover plugin. Includes sample code, test maps, etc to help developers start using the system. Not intended to be used directly in a shipping product. 
> Please refer to the Mover plugin's README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 移动示例 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试地图、示例代码） |
| 模块 | `MoverExamples` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-08 |
| 年龄标签 | 🆕（约 0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverExamples) | |

## 用途

Mover Examples 是 [Mover 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover) 的配套示例包。它提供了多个可参考的实现：

- **基础角色类**：`AMoverExamplesCharacter` —— 一个抽象的 Pawn 基类，封装了输入收集（支持 EIS）和移动请求接口。
- **扩展输入数据**：`FMoverExampleAbilityInputs` —— 用于传递冲刺、瞄准、攀爬、滑索、蹲伏等额外按键状态的数据块。
- **物理角色变体**：`UMoverExamplesPhysicsCharacterMoverComponent` —— 演示如何在 Mover 的物理角色基础上执行自定义逻辑。
- **滑索 (Ziplining)**：完整的运动模式 (`UZipliningMode`) 和进出过渡 (`UZiplineStartTransition`, `UZiplineEndTransition`)，以及一个可被滑索交互的接口 (`IZipline`)。
- **路径跟随**：两种基础运动模式——`UFollowPathMode`（基于控制点）和 `UFollowSplineMode`（基于 Spline 组件），支持速度控制、朝向调整和循环行为。
- **游戏模式/游戏状态**：`AMoverExamplesGameMode`（重写了 `ChoosePlayerStart` 以确保玩家能生成在合适地点）和 `AMoverExamplesGameState`（空实现，方便扩展）。

该插件的目的是帮助开发者快速入门 Mover 系统，通过阅读和运行这些示例，理解如何构建自定义的运动模式、输入处理、网络同步等。

## 使用场景

- 你需要学习如何使用 Mover 插件创建一个带冲刺、滑索等能力的角色。
- 你正在开发一个需要路径跟随或 Spline 移动的关卡元素（如过场动画、平台）。
- 你想要在物理角色（Chaos Physics）上叠加 Mover 的运动逻辑。
- 你需要在蓝图中实现自定义输入生产逻辑（`OnProduceInput` 事件）。

## 蓝图用法

### 核心节点

#### 角色控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMoverComponent` | 获取角色的移动组件（UCharacterMoverComponent） | `AMoverExamplesCharacter` |
| `Request Move by Intent` | 设置移动方向意图（向量长度表示加速程度） | `AMoverExamplesCharacter` |
| `Request Move by Velocity` | 直接设置期望移动速度（覆盖其他输入） | `AMoverExamplesCharacter` |
| `On Produce Input` (事件) | 在每个模拟帧开始时触发，用于编写输入逻辑（返回 `FMoverInputCmdContext`） | `AMoverExamplesCharacter` (BlueprintImplementableEvent) |

#### 滑索 (Zipline)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Start Component` | 获取滑索起点的 Scene Component | `IZipline` (接口) |
| `Get End Component` | 获取滑索终点的 Scene Component | `IZipline` (接口) |

#### 路径跟随

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Control Spline` | 为 FollowSplineMode 设置目标 Spline 组件（可指定开始/结束偏移） | `UFollowSplineMode` |

#### 可配置属性（蓝图读写）

- `AMoverExamplesCharacter` 的输入动作绑定属性（`MoveInputAction`, `LookInputAction`, `JumpInputAction`, `DashInputAction`, `AimInputAction`, `VaultInputAction` 等）。
- `UZipliningMode` 的 `MaxSpeed`。
- `UFollowPathMode` 的 `ControlPoints`, `BehaviourType`, `RotationType`, `Duration`。
- `UFollowSplineMode` 的 `BehaviourType`, `RotationType`, `bOrientMoverToMovement`, `bConstantFollowVelocity` 等。
- `FMoverExampleAbilityInputs` 结构体的所有布尔字段（`bIsDashJustPressed` 等），可用于在蓝图中读取或设置。

### 使用示例（蓝图描述）

1. **设置角色输入**  
   在 `AMoverExamplesCharacter` 蓝图的事件图中，调用 `On Produce Input` 事件。在该事件内，从 Enhanced Input 子系统获取当前帧的输入值（通过 UEnhancedInputLocalPlayerSubsystem），构造 `FMoverInputCmdContext` 并设置 `bIsDashJustPressed` 等字段（来自 `AbilityInputs` 数据块），最后返回该上下文。

2. **使用滑索模式**  
   - 创建滑索 Actor，实现 `IZipline` 接口，重写 `GetStartComponent` / `GetEndComponent` 返回两个 Scene Component 的位置。  
   - 在角色蓝图中，通过 Mover 组件添加 `UZipliningMode` 运动模式，并添加对应的过渡模式 `UZiplineStartTransition`（设置 `ZipliningModeName` 为 "Ziplining"）。  
   - 玩家按下滑索按键时，设置 `AbilityInputs.bWantsToStartZiplining = true`，过渡模式会自动检测并切换到滑索模式。

3. **使用 FollowSplineMode 让角色沿 Spline 移动**  
   - 在关卡中放置一个 Spline 组件（如 BP_SplineActor），并在角色蓝图的事件 `BeginPlay` 中调用节点 `Set Control Spline`，目标为 Spline 的拥有 Actor。  
   - 通过 Mover 组件将当前运动模式设置为 `UFollowSplineMode` 的名称（例如 "FollowSpline"），角色便会沿 Spline 移动。

## C++ 用法

### 头文件引入

```cpp
#include "MoverExamplesCharacter.h"
#include "CharacterVariants/Ziplining/ZipliningMode.h"
#include "CharacterVariants/Ziplining/ZiplineInterface.h"
#include "MovementBases/FollowSplineMode.h"
#include "MovementBases/FollowPathMode.h"
```

### 基本用法

#### 创建自定义角色并重写输入生产

```cpp
// MyCharacter.h
#pragma once
#include "MoverExamplesCharacter.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public AMoverExamplesCharacter
{
    GENERATED_BODY()

protected:
    virtual void OnProduceInput(float DeltaMs, FMoverInputCmdContext& InputCmdResult) override;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "CharacterVariants/AbilityInputs.h"

void AMyCharacter::OnProduceInput(float DeltaMs, FMoverInputCmdContext& InputCmdResult)
{
    Super::OnProduceInput(DeltaMs, InputCmdResult);

    // 设置扩展能力输入
    FMoverExampleAbilityInputs& AbilityInputs = InputCmdResult.InputCollection.FindOrAddData<FMoverExampleAbilityInputs>();
    AbilityInputs.bIsDashJustPressed = GetDashInput(); // 你的自定义输入检测
}
```

#### 使用滑索运动模式

```cpp
#include "CharacterVariants/Ziplining/ZipliningMode.h"
#include "CharacterVariants/Ziplining/ZipliningTransitions.h"

// 在角色初始化时注册滑索模式和过渡
void AMyCharacter::SetupMoverModes()
{
    UCharacterMoverComponent* MoverComp = GetMoverComponent();
    if (!MoverComp) return;

    // 添加滑索模式
    UZipliningMode* ZiplineMode = NewObject<UZipliningMode>(MoverComp);
    ZiplineMode->MaxSpeed = 1200.0f;
    MoverComp->AddMovementMode(ExtendedModeNames::Ziplining, ZiplineMode);

    // 添加滑索开始过渡（从跳跃/下落进入滑索）
    UZiplineStartTransition* StartTransition = NewObject<UZiplineStartTransition>(MoverComp);
    StartTransition->ZipliningModeName = ExtendedModeNames::Ziplining;
    MoverComp->AddMovementModeTransition(StartTransition);

    // 添加滑索结束过渡（退出滑索回到下落）
    UZiplineEndTransition* EndTransition = NewObject<UZiplineEndTransition>(MoverComp);
    EndTransition->AutoExitToMode = DefaultModeNames::Falling;
    MoverComp->AddMovementModeTransition(EndTransition);
}
```

### 进阶用法

#### 实现滑索接口（供角色抓取）

```cpp
// MyZipline.h
UCLASS()
class AMyZipline : public AActor, public IZipline
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere)
    USceneComponent* StartPoint;

    UPROPERTY(EditAnywhere)
    USceneComponent* EndPoint;

    virtual USceneComponent* GetStartComponent_Implementation() override { return StartPoint; }
    virtual USceneComponent* GetEndComponent_Implementation() override { return EndPoint; }
};
```

#### 使用 FollowSplineMode 动态控制 Spline

```cpp
#include "MovementBases/FollowSplineMode.h"

void AMyCharacter::StartSplineMove(AActor* SplineActor)
{
    UFollowSplineMode* SplineMode = FindComponentByClass<UFollowSplineMode>();
    if (!SplineMode)
    {
        SplineMode = NewObject<UFollowSplineMode>(GetMoverComponent());
        // 需要将模式注册到 MoverComponent 中并切换
    }
    SplineMode->SetControlSpline(SplineActor, FSplineOffsetRangeInput());
    GetMoverComponent()->SetMovementMode(TEXT("FollowSpline"));
}
```

## Demo 示例

以下是一个完整的、最小化示例，展示如何创建一个使用 MoverExamples 的角色并注册滑索模式。

### MyMoverCharacter.h

```cpp
#pragma once

#include "MoverExamplesCharacter.h"
#include "MyMoverCharacter.generated.h"

/**
 * 一个使用 MoverExamples 的简单角色，演示如何添加滑索能力。
 */
UCLASS()
class AMyMoverCharacter : public AMoverExamplesCharacter
{
    GENERATED_BODY()

public:
    AMyMoverCharacter(const FObjectInitializer& OI);

protected:
    virtual void BeginPlay() override;
    virtual void OnProduceInput(float DeltaMs, FMoverInputCmdContext& InputCmdResult) override;

private:
    void SetupZiplineSystem();
};
```

### MyMoverCharacter.cpp

```cpp
#include "MyMoverCharacter.h"
#include "CharacterVariants/AbilityInputs.h"
#include "CharacterVariants/Ziplining/ZipliningMode.h"
#include "CharacterVariants/Ziplining/ZipliningTransitions.h"
#include "CharacterVariants/Ziplining/ZiplineInterface.h"
#include "Mover/MoverComponent.h"

AMyMoverCharacter::AMyMoverCharacter(const FObjectInitializer& OI)
    : Super(OI)
{
}

void AMyMoverCharacter::BeginPlay()
{
    Super::BeginPlay();
    SetupZiplineSystem();
}

void AMyMoverCharacter::SetupZiplineSystem()
{
    UCharacterMoverComponent* MoverComp = GetMoverComponent();
    if (!MoverComp) return;

    // 注册滑索模式
    UZipliningMode* ZiplineMode = NewObject<UZipliningMode>(MoverComp);
    ZiplineMode->MaxSpeed = 1500.0f;
    MoverComp->AddMovementMode(ExtendedModeNames::Ziplining, ZiplineMode);

    // 注册开始过渡（空中检测）
    UZiplineStartTransition* StartTrans = NewObject<UZiplineStartTransition>(MoverComp);
    StartTrans->ZipliningModeName = ExtendedModeNames::Ziplining;
    MoverComp->AddMovementModeTransition(StartTrans);

    // 注册结束过渡（按退出键回到下落）
    UZiplineEndTransition* EndTrans = NewObject<UZiplineEndTransition>(MoverComp);
    EndTrans->AutoExitToMode = DefaultModeNames::Falling;
    MoverComp->AddMovementModeTransition(EndTrans);
}

void AMyMoverCharacter::OnProduceInput(float DeltaMs, FMoverInputCmdContext& InputCmdResult)
{
    Super::OnProduceInput(DeltaMs, InputCmdResult);

    // 检测滑索输入（假设你有一个 GEtHasZiplineInput() 方法）
    bool bWantsZipline = false;
    // ... 从 Enhanced Input 或其他来源获取
    if (bWantsZipline)
    {
        FMoverExampleAbilityInputs& AbilityInputs = InputCmdResult.InputCollection.FindOrAddData<FMoverExampleAbilityInputs>();
        AbilityInputs.bWantsToStartZiplining = true;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mover` | 核心移动系统，提供角色移动组件、数据块、运动模式基类 |
| `ChaosMover` | 物理角色移动组件（`UPhysicsCharacterMoverComponent`）的基础实现 |
| `CableComponent` | 滑索可视化（示例中使用缆绳组件渲染滑索线），也可用于其他绳索物理 |
| `EnhancedInput` | 增强输入系统，提供输入动作和值绑定 |

构建时你的模块只需将 `MoverExamples` 加入 `PublicDependencyModuleNames`，它会自动拉取上述依赖。

## 维护状态

### 近期更新

- 2025-09-24 — `661fc2ea` — [Mover] Consistent angular velocity when changing movement modes
- 2025-04-15 — `9790e052` — Mover: improving copy implementation of data collections and sync state to avoid memory reallocation
- 2025-04-14 — `3511dea4` — Making CharacterMotionComponent Transient in MoverExamplesCharacter.h
- 2025-04-10 — `e53193a0` — MoverExamples:  (初始提交或批量导入)
- 2025-04-08 — `d02d278b` — Chaos Visual Debugger: Adding local sim data to what CVD records for Mover

### 维护评价

- **创建时间**：2025-04-08（约 0.5 年）。
- **近期更新**：最近 5 个月内有实质性功能更新和关键 bug 修复，项目处于活跃开发中。
- **内容完整性**：包含了滑索、路径跟随、物理角色扩展等完整示例，且有蓝图接口和 C++ 重写点。
- **实验性警告**：`.uplugin` 标记为 `IsExperimentalVersion=true`，API 可能在未来版本中变化。
- **推荐使用**：非常适合作为学习 Mover 系统的起点，但不应直接用于发行产品。建议根据示例自定义自己的角色类。

## 相关链接

- [源码（github.com，5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverExamples)
- [Mover 插件 README（包括概念概述和已知问题）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Mover/README.md)
- [Mover 官方文档（如有）](https://docs.unrealengine.com/5.7/en-US/mover-system-in-unreal-engine/)