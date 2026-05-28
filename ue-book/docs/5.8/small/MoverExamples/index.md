# Mover Examples

> Non-essential classes and content for the Mover plugin. Includes sample code, test maps, etc to help developers start using the system. Not intended to be used directly in a shipping product. 
Please refer to the Mover plugin's README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | Mover 示例 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例角色、移动模式、测试地图） |
| 模块 | `MoverExamples` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverExamples) | |

## 用途

MoverExamples 是 Mover 插件的配套教学插件，提供了一组**可直接运行的示例移动模式和角色基类**，帮助开发者理解并上手 Mover 移动框架。

它不用于生产环境，而是作为学习材料，展示了如何：
- 实现自定义移动模式（沿样条线移动、沿路径移动、滑索移动）
- 通过 `IMoverInputProducerInterface` 将 Enhanced Input 转换为 Mover 输入命令
- 定义和处理自定义能力输入数据（冲刺、瞄准、翻越、滑索等）
- 使用状态同步与网络插值机制

简而言之：**想学会怎么写自己的 Mover 移动模式？先看这个插件。**

## 使用场景

- 你正在使用 Mover 插件构建角色移动系统，需要参考示例代码 → 研究本插件的 `FollowPathMode`、`FollowSplineMode`
- 你需要让角色沿样条线自动移动（如过山车、缆车） → 使用 `UFollowSplineMode`
- 你需要让角色按预设路径点移动（如巡逻路线、动画路径） → 使用 `UFollowPathMode`
- 你想实现滑索移动机制 → 参考 `UZipliningMode` 和 `IZipline` 接口
- 你想了解如何将 Enhanced Input 集成到 Mover 输入管线 → 参考 `AMoverExamplesCharacter`

## 蓝图用法

### 角色控制（MoverExamplesCharacter）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Mover Component` | 获取角色的 CharacterMoverComponent | `AMoverExamplesCharacter` |
| `Request Move By Intent` | 以意向方向请求移动，长度 1 表示最大加速度 | `AMoverExamplesCharacter` |
| `Request Move By Velocity` | 以指定速度请求移动，会忽略其他输入 | `AMoverExamplesCharacter` |
| `On Produce Input` | 蓝图可实现事件，在此编写每帧的自定义输入逻辑 | `AMoverExamplesCharacter` |

### 样条线跟随（FollowSplineMode）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Control Spline` | 设置跟随的样条线（通过提供 Actor）及偏移量 | `UFollowSplineMode` |

可配置属性：
- `BehaviourType` — 循环/乒乓/单次等跟随模式
- `RotationType` — 是否跟随样条切线旋转
- `bOrientMoverToMovement` — 始终朝向移动方向
- `bConstantFollowVelocity` — 恒速跟随
- `StartOffset` / `EndOffset` — 定义跟随的起止范围（百分比/时间/距离）
- `InterpolationCurve` — 自定义速度曲线

### 能力输入获取

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Mover Example Ability Inputs` | 从 MoverDataCollection 中提取示例能力输入 | `UMoverExampleAbilityInputsLibrary` |

### 滑索接口（IZipline）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Start Component` | 获取滑索起点场景组件 | `IZipline` |
| `Get End Component` | 获取滑索终点场景组件 | `IZipline` |

### 使用示例（蓝图描述）

**设置角色沿路径移动：**
1. 创建继承自 `AMoverExamplesCharacter` 的蓝图角色
2. 在角色上添加 `CharacterMoverComponent`，配置移动模式
3. 创建 `UFollowPathMode` 实例，设置 `ControlPoints` 数组（路径点列表）
4. 设置 `Duration`（移动总时间）和 `BehaviourType`（如乒乓）
5. 将该模式注册到 Mover 系统中

**设置角色沿样条线移动：**
1. 在场景中放置一个带 `SplineComponent` 的 Actor
2. 创建 `UFollowSplineMode` 实例
3. 调用 `Set Control Spline` 节点，传入样条线 Actor
4. 配置 `StartOffset`、`EndOffset` 及 `InterpolationCurve` 控制运动节奏

## C++ 用法

### 头文件引入

```cpp
#include "MovementBases/FollowSplineMode.h"
#include "MovementBases/FollowPathMode.h"
#include "CharacterVariants/Ziplining/ZipliningMode.h"
#include "CharacterVariants/AbilityInputs.h"
#include "MoverExamplesCharacter.h"
```

### 基本用法 — 设置样条线跟随

```cpp
// 获取或创建 FollowSplineMode 实例（通常在 Mover 组件初始化时完成）
UFollowSplineMode* SplineMode = NewObject<UFollowSplineMode>(MoverComponent);

// 配置跟随行为
SplineMode->BehaviourType = EInterpToBehaviourType::OneShot;
SplineMode->RotationType = EFollowSplineRotationType::FollowSplineTangent;
SplineMode->bOrientMoverToMovement = true;
SplineMode->bConstantFollowVelocity = false;

// 设置偏移范围（从 20% 到 80% 的样条线位置）
FSplineOffsetRangeInput StartOffset;
StartOffset.Value = 0.2f;
StartOffset.OffsetUnit = ESplineOffsetUnit::Percentage;

FSplineOffsetRangeInput EndOffset;
EndOffset.Value = 0.8f;
EndOffset.OffsetUnit = ESplineOffsetUnit::Percentage;

SplineMode->StartOffset = StartOffset;
SplineMode->EndOffset = EndOffset;

// 设置控制样条线（SplineProviderActor 需要包含 USplineComponent）
SplineMode->SetControlSpline(SplineProviderActor);
```

*来源：`FollowSplineMode.h` 中 `UFollowSplineMode` 类定义*

### 基本用法 — 路径点跟随

```cpp
// 创建 FollowPathMode
UFollowPathMode* PathMode = NewObject<UFollowPathMode>(MoverComponent);

// 设置路径控制点
PathMode->ControlPoints.Add(FInterpControlPoint(Location1));
PathMode->ControlPoints.Add(FInterpControlPoint(Location2));
PathMode->ControlPoints.Add(FInterpControlPoint(Location3));

// 配置行为
PathMode->BehaviourType = EInterpToBehaviourType::PingPong;
PathMode->RotationType = EFollowPathRotationType::AlignWithPathTangents;
PathMode->Duration = 5.0f;  // 从起点到终点需要 5 秒
```

*来源：`FollowPathMode.h` 中 `UFollowPathMode` 类定义*

### 进阶用法 — 自定义角色输入生产者

继承 `AMoverExamplesCharacter` 并重写输入逻辑：

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
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"

void AMyCharacter::OnProduceInput(float DeltaMs, FMoverInputCmdContext& InputCmdResult)
{
    // 调用父类处理标准移动/跳跃/飞行输入
    Super::OnProduceInput(DeltaMs, InputCmdResult);

    // 在自定义数据集合中写入能力输入
    FMoverExampleAbilityInputs AbilityInputs;
    AbilityInputs.bIsAimPressed = bIsAiming;
    AbilityInputs.bIsDashJustPressed = bIsDashTriggered;

    // 写入到输入命令的数据集合中
    InputCmdResult.InputCollection.SetData(AbilityInputs);
}
```

*来源：`MoverExamplesCharacter.h` 中 `OnProduceInput` 声明，`AbilityInputs.h` 中 `FMoverExampleAbilityInputs` 结构*

### 进阶用法 — 实现滑索接口

```cpp
// ZiplineActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "CharacterVariants/Ziplining/ZiplineInterface.h"
#include "ZiplineActor.generated.h"

UCLASS()
class AZiplineActor : public AActor, public IZipline
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere)
    USceneComponent* StartPoint;

    UPROPERTY(VisibleAnywhere)
    USceneComponent* EndPoint;

    // IZipline 接口实现
    virtual USceneComponent* GetStartComponent_Implementation() override { return StartPoint; }
    virtual USceneComponent* GetEndComponent_Implementation() override { return EndPoint; }
};
```

*来源：`ZiplineInterface.h` 中 `IZipline` 接口定义*

## Demo 示例

完整的自定义移动模式示例 — 创建一个从当前位置平滑移动到目标点的模式：

```cpp
// SimpleMoveToMode.h
#pragma once
#include "MovementModes/BaseMovementMode.h"
#include "SimpleMoveToMode.generated.h"

UCLASS(Blueprintable, BlueprintType)
class USimpleMoveToMode : public UBaseMovementMode
{
    GENERATED_UCLASS_BODY()

public:
    // 目标位置
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SimpleMoveTo")
    FVector TargetLocation;

    // 移动速度
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SimpleMoveTo", meta = (ClampMin = "1"))
    float Speed = 500.0f;

    virtual void GenerateMove_Implementation(
        const FMoverSimContext& SimContext,
        const FMoverTickStartData& StartState,
        const FMoverTimeStep& TimeStep,
        FProposedMove& OutProposedMove) const override;

    virtual void SimulationTick_Implementation(
        const FSimulationTickParams& Params,
        FMoverTickEndData& OutputState) override;
};
```

```cpp
// SimpleMoveToMode.cpp
#include "SimpleMoveToMode.h"

USimpleMoveToMode::USimpleMoveToMode(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    TargetLocation = FVector::ZeroVector;
}

void USimpleMoveToMode::GenerateMove_Implementation(
    const FMoverSimContext& SimContext,
    const FMoverTickStartData& StartState,
    const FMoverTimeStep& TimeStep,
    FProposedMove& OutProposedMove) const
{
    const FVector CurrentLocation = StartState.SyncState.MoveStartIntent.Location;
    const FVector ToTarget = TargetLocation - CurrentLocation;
    const float Distance = ToTarget.Size();

    if (Distance < KINDA_SMALL_NUMBER)
    {
        OutProposedMove.MovementIntent = FVector::ZeroVector;
        return;
    }

    const FVector Direction = ToTarget.GetSafeNormal();
    const float MoveDistance = FMath::Min(Speed * TimeStep.StepMs * 0.001f, Distance);
    OutProposedMove.MovementIntent = Direction * MoveDistance;
}

void USimpleMoveToMode::SimulationTick_Implementation(
    const FSimulationTickParams& Params,
    FMoverTickEndData& OutputState)
{
    // 使用默认的物理移动处理
    // 在实际项目中，这里可以添加自定义的碰撞检测和状态转换逻辑
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等，以及运行时依赖的 Mover/ChaosMover）。

该插件的 `.uplugin` 声明了以下插件依赖，你的项目需要启用它们：

| 依赖插件 | 用途 |
|---|---|
| `Mover` | 核心移动框架，提供 `UBaseMovementMode`、`FMoverSimContext` 等基础类型 |
| `ChaosMover` | 基于 Chaos 物理的移动实现 |
| `EnhancedInput` | 输入系统，用于角色输入绑定（`UInputAction`） |
| `CableComponent` | 示例中可能用于可视化调试绳索/滑索效果 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `569fea65` | Mover/ChaosMover: Fixing interpolate so it can't easily skip a button press | 修复输入插值可能导致按键丢失的问题 |
| 2026-05-14 | `6db6dceb` | Remove deprecated PhysicsMover/NetworkPhysicsLiaison code from Mover plugin and internal projects. | 移除已废弃的 PhysicsMover 和 NetworkPhysicsLiaison 代码 |
| 2026-05-14 | `05775cc0` | [Backout] - CL53867378 | 回退一次变更 |
| 2026-05-13 | `86f038af` | Remove deprecated PhysicsMover/NetworkPhysicsLiaison code from Mover plugin and internal projects. | 移除废弃代码（前一次的尝试） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |

### 维护评价

- **状态**：活跃维护中。最近更新集中在 2026 年 5 月，有多次功能性改动
- **实验性警告**：该插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 随时可能变更
- **代码质量**：提供了完善的网络序列化、状态插值和调和（reconciliation）机制，代码结构清晰
- **注意事项**：这是一个**教学/示例插件**，不建议直接用于生产项目。应将其作为参考，提取所需逻辑到自己的代码中
- **推荐程度**：⭐⭐⭐⭐ — 学习 Mover 框架的最佳起点，但需注意 API 不稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverExamples)
- [Mover 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
- [ChaosMover 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosMover)