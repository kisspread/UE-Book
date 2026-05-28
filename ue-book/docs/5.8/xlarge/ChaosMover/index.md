# Chaos Mover

> Chaos Mover is an Unreal Engine plugin to support Chaos physics based character movement using the Mover framework.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌运动器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、物理约束配置） |
| 模块 | `ChaosMover` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosMover) | |

## 用途

ChaosMover 是 Mover 框架的 Chaos 物理后端实现，解决的核心问题是：**将角色移动模拟完全运行在物理线程上**，同时保持网络同步和预测回滚能力。

传统 Mover 插件的移动模拟运行在游戏线程，无法与 Chaos 物理引擎深度集成。ChaosMover 引入了一个异步后端，创建了专门的 `FSimulation` 类，只操作线程安全对象，并构建了一套完整的、仅使用线程安全参数的移动状态机。

### 核心架构

ChaosMover 采用了 **Source + Executor 分离**的组合式架构：

- **Move Source**（`UChaosMoverSourceBase`）：负责生成提议移动（ProposedMove），即"要以什么速度移动"
- **Move Executor**（`UChaosMoveExecutorBase`）：负责将提议移动应用到物理模拟，即"如何驱动物理体"
- **Composite Movement Mode**（`UChaosCompositeMovementMode`）：将 Source 和 Executor 组合在一起，两者可以独立配置和替换

这种设计使得行走、自由移动、路径运动等物理行为可以独立于移动生成逻辑进行组合。

## 使用场景

- 你需要 Chaos 物理驱动的角色移动（行走、下落、游泳）→ 使用 ChaosMover 的 Character Modes
- 你需要在移动平台上沿路径运动的物体（电梯、旋转机关）→ 使用 PathedMovement 模式
- 你需要网络同步的角色移动，支持客户端预测和服务端权威回滚 → ChaosMover 内置网络支持
- 你需要将角色移动模拟卸载到物理线程以获得更好的性能 → ChaosMover 的异步后端
- 你需要将不同移动逻辑（生成 + 执行）独立组合 → 使用 CompositeMovementMode

## 子模块文档

| 文档 | 描述 |
|---|---|
| [Character](./Character.md) | 角色移动模式：行走、下落、游泳、蹲伏 |
| [PathedMovement](./PathedMovement.md) | 路径运动：样条线、点序列路径模式 |
| [Networking](./Networking.md) | 网络同步：权威操作、调度移动、SimAction 系统 |
| [SimulationCore](./SimulationCore.md) | 模拟核心：状态机、后端组件、事件系统 |

## 蓝图用法

### 角色移动控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Launch` | 以冲量或速度发射角色 | `UChaosCharacterMoverComponent` |
| `OverrideMovementSettings` | 覆盖当前移动模式的速度/加速度设置 | `UChaosCharacterMoverComponent` |
| `CancelMovementSettingsOverrides` | 取消移动设置覆盖 | `UChaosCharacterMoverComponent` |
| `TryGetFloorCheckHitResult` | 获取最近一次地面检测结果 | `UChaosCharacterMoverComponent` |
| `TryGetLastWaterResult` | 获取最近一次水体检测结果 | `UChaosCharacterMoverComponent` |

### 路径运动控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RequestStartPlayingPath` | 请求开始/恢复路径运动 | `UChaosPathedMovementControllerComponent` |
| `RequestStopPlayingPath` | 请求停止路径运动 | `UChaosPathedMovementControllerComponent` |
| `RequestReversePlayback` | 请求正向/反向播放 | `UChaosPathedMovementControllerComponent` |
| `RequestLoopingPlayback` | 请求循环/单次播放 | `UChaosPathedMovementControllerComponent` |
| `RequestOneWayPlayback` | 请求单程/往返播放 | `UChaosPathedMovementControllerComponent` |
| `WantsPlayingPath` | 查询是否希望播放 | `UChaosPathedMovementControllerComponent` |
| `IsPlayingPath` | 查询是否正在播放 | `UChaosPathedMovementControllerComponent` |

### 模拟层操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `K2_QueueInstantMovementEffect` | 队列即时移动效果（如传送） | `UChaosMoverSimulation` |
| `K2_QueueLayeredMove` | 队列分层移动（如跳跃、冲刺） | `UChaosMoverSimulation` |
| `K2_QueueMovementModifier` | 队列移动修饰器（如蹲伏） | `UChaosMoverSimulation` |
| `CancelModifierFromHandle` | 通过句柄取消移动修饰器 | `UChaosMoverSimulation` |
| `QueueNextMovementMode` | 请求切换到指定移动模式 | `UChaosMoverSimulation` |

### 网络操作（服务端）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `K2_QueueLayeredMove_Authority` | 服务端队列权威分层移动 | `UChaosMoverBlueprintLibrary` |
| `K2_QueueInstantMovementEffect_Authority` | 服务端队列权威即时效果 | `UChaosMoverBlueprintLibrary` |
| `K2_ScheduleLayeredMove_Authority` | 调度分层移动（帧同步） | `UChaosMoverBlueprintLibrary` |
| `K2_ScheduleInstantMovementEffect_Authority` | 调度即时效果（帧同步） | `UChaosMoverBlueprintLibrary` |

### 使用示例（蓝图描述）

**发射角色：**
1. 获取角色的 `UChaosCharacterMoverComponent` 引用
2. 调用 `Launch`，传入速度向量（如 `(0, 0, 1000)`），模式选择 `AdditiveVelocity`

**路径运动控制：**
1. 在 Actor 上添加 `UChaosPathedMovementControllerComponent`
2. 确保 Actor 有 `MoverComponent` 且激活了 `UChaosPathedMovementMode`
3. 调用 `RequestStartPlayingPath`，设置 `ExecutionType` 和 `bIsScheduled`

**动态蹲伏：**
1. 构造 `FChaosMoverCrouchInputs`，设置 `bWantsToCrouch = true`
2. 将其添加到输入数据集合中传递给 Mover 模拟

## C++ 用法

### 头文件引入

```cpp
#include "ChaosMover/ChaosMoverSimulation.h"
#include "ChaosMover/Character/ChaosCharacterMoverComponent.h"
#include "ChaosMover/PathedMovement/ChaosPathedMovementControllerComponent.h"
#include "ChaosMover/ChaosMoverSimulationTypes.h"
#include "ChaosMover/Character/ChaosCharacterInputs.h"
```

### 基本用法：发射角色

```cpp
// 在角色类中获取 ChaosCharacterMoverComponent 并发射
void AMyCharacter::LaunchCharacter()
{
    UChaosCharacterMoverComponent* ChaosMover = FindComponentByClass<UChaosCharacterMoverComponent>();
    if (ChaosMover)
    {
        // 向上发射角色，附加速度模式
        ChaosMover->Launch(FVector(0.f, 0.f, 800.f), EChaosMoverVelocityEffectMode::AdditiveVelocity);
    }
}
```

### 基本用法：覆盖移动设置

```cpp
void AMyCharacter::SetSprintSpeed()
{
    UChaosCharacterMoverComponent* ChaosMover = FindComponentByClass<UChaosCharacterMoverComponent>();
    if (ChaosMover)
    {
        FChaosMovementSettingsOverrides Overrides;
        Overrides.ModeName = NAME_None; // 应用到当前模式
        Overrides.MaxSpeedOverride = 1200.f;
        Overrides.AccelerationOverride = 6000.f;
        ChaosMover->OverrideMovementSettings(Overrides);
    }
}
```

### 进阶用法：路径运动控制

```cpp
void AMyActor::SetupPathedMovement()
{
    UChaosPathedMovementControllerComponent* Controller = FindComponentByClass<UChaosPathedMovementControllerComponent>();
    if (Controller)
    {
        // 绑定回调
        Controller->OnPathedMovementStarted.AddDynamic(this, &AMyActor::OnPathStarted);
        Controller->OnPathedMovementStopped.AddDynamic(this, &AMyActor::OnPathStopped);
        Controller->OnPathedMovementBounced.AddDynamic(this, &AMyActor::OnPathBounced);

        // 设置为循环、往返模式
        Controller->RequestLoopingPlayback(true, EChaosPathedMovementExecutionType::ClientPredicted_AutonomousOnly, true);
        Controller->RequestOneWayPlayback(false, EChaosPathedMovementExecutionType::ClientPredicted_AutonomousOnly, true);

        // 开始播放（延迟调度以保证所有端同步）
        Controller->RequestStartPlayingPath(EChaosPathedMovementExecutionType::ClientPredicted_AutonomousOnly, true);
    }
}
```

### 进阶用法：直接操作模拟层

```cpp
void AMyCharacter::QueueKnockback(UChaosMoverSimulation* Simulation)
{
    if (!Simulation) return;

    // 构造即时移动效果（传送类调试效果）
    auto Effect = MakeShared<FDebugTeleportToInstantMovementEffect>();
    Effect->TeleportLocation = FVector(100.f, 0.f, 0.f);
    Effect->TeleportRotation = FRotator(0.f, 90.f, 0.f);

    // 通过内部接口队列
    Simulation->QueueInstantMovementEffect_Internal(Effect, true);
}
```

## Demo 示例

### 基于 CompositeMovementMode 的自定义角色

**MyChaosCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ChaosMover/Character/ChaosCharacterMoverComponent.h"
#include "MyChaosCharacter.generated.h"

UCLASS()
class AMyChaosCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyChaosCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mover")
    TObjectPtr<UChaosCharacterMoverComponent> ChaosMoverComponent;

    UFUNCTION(BlueprintCallable, Category = "Mover")
    void DoJump();

    UFUNCTION(BlueprintCallable, Category = "Mover")
    void DoCrouch();

    UFUNCTION(BlueprintCallable, Category = "Mover")
    void DoUncrouch();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnLanded(const FLandedEventData& Event);

    UFUNCTION()
    void OnJumped();

    UPROPERTY()
    bool bWantsCrouch = false;
};
```

**MyChaosCharacter.cpp**
```cpp
#include "MyChaosCharacter.h"
#include "ChaosMover/Character/ChaosCharacterInputs.h"

AMyChaosCharacter::AMyChaosCharacter()
{
    // 用 ChaosMoverComponent 替代默认的 CharacterMovement
    ChaosMoverComponent = CreateDefaultSubobject<UChaosCharacterMoverComponent>(TEXT("ChaosMover"));
}

void AMyChaosCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (ChaosMoverComponent)
    {
        ChaosMoverComponent->OnLandedDelegate.AddDynamic(this, &AMyChaosCharacter::OnLanded);
        ChaosMoverComponent->OnJumped.AddDynamic(this, &AMyChaosCharacter::OnJumped);
    }
}

void AMyChaosCharacter::DoJump()
{
    if (ChaosMoverComponent)
    {
        ChaosMoverComponent->Launch(FVector(0.f, 0.f, 600.f), EChaosMoverVelocityEffectMode::AdditiveVelocity);
    }
}

void AMyChaosCharacter::DoCrouch()
{
    bWantsCrouch = true;
}

void AMyChaosCharacter::DoUncrouch()
{
    bWantsCrouch = false;
}

void AMyChaosCharacter::OnLanded(const FLandedEventData& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Character landed!"));
}

void AMyChaosCharacter::OnJumped()
{
    UE_LOG(LogTemp, Log, TEXT("Character jumped!"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mover` | 上层移动框架，提供移动模式、移动修饰器、同步状态等基础抽象 |
| `NetworkPhysics` | 网络物理同步，提供 SimAction 调度系统和预测回滚基础设施 |
| `Chaos` / `ChaosSolverEngine` | Chaos 物理引擎核心，约束、粒子、求解器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `4ea45e21` | Mover: fix bug where skipping vertical anim root motion was not being respected in all montage cases | 修复垂直动画根运动跳过逻辑在某些动画蒙太奇场景中未生效的 Bug |
| 2026-05-21 | `457df8ff` | ChaosMover: Fixing layered moves and instant movement effects in standalone mode, they cannot use si | 修复独立模式下分层移动和即时效果无法使用 SimAction 系统的问题 |
| 2026-05-14 | `801be5dc` | Mover/ChaosMover: Just like moves, move instances are now using a pull mechanism so they can work in | 移动实例改用拉取机制，使其在复合移动模式中正常工作 |
| 2026-05-14 | `d040bc9f` | Mover: adding simulation that's specific to kinematically-moved Actors | 新增针对运动学驱动 Actor 的专用模拟 |
| 2026-05-14 | `6db6dceb` | Remove deprecated PhysicsMover/NetworkPhysicsLiaison code from Mover plugin and internal projects. | 移除已废弃的 PhysicsMover 和 NetworkPhysicsLiaison 代码 |

### 维护评价

- **创建时间**：2025 年 3 月，是一个相当新的插件
- **实验性标记**：`IsExperimentalVersion=true`，尚未稳定，API 可能发生破坏性变更
- **活跃度**：最近更新集中在 2026 年 5 月，一周内有多次功能性提交，属于**活跃开发中**
- **已知限制**：作为实验性插件，部分功能仍在完善（如注释中提到的 `//@todo` 项）
- **依赖关系**：依赖 Mover 插件，后者本身也是较新的框架
- **⚠️ 警告**：此插件处于实验阶段，生产环境使用需谨慎。API 和行为可能在后续版本中发生变化。注释中包含多处 `@todo` 标记，表明仍有功能待完成。
- **推荐**：如果你的项目已经在使用 Mover 框架并需要 Chaos 物理后端，这是一个值得关注和提前试用的插件。不建议在正式项目中依赖它，但非常适合原型验证和技术探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosMover)
- [官方文档]()（暂无）