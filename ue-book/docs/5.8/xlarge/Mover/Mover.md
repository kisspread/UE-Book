# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.
Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 移动框架 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例内容） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 是一个**支持回滚网络（Rollback Networking）的 Actor 移动框架**。它为 UE5 提供了一套全新的、模块化的移动模拟系统，取代或补充传统的 `UCharacterMovementComponent`。

核心设计理念是**将移动逻辑拆分为独立、可组合的层**：
- **Movement Mode（移动模式）**：定义基础移动行为（行走、下落、游泳等），通过状态机管理模式切换
- **Layered Moves（分层移动）**：在基础移动之上叠加临时效果（跳跃冲量、冲刺、击退等），可并行叠加多个
- **Movement Modifiers（移动修改器）**：间接影响模拟参数（如改变摩擦力、重力方向等）
- **Instant Effects（瞬时效果）**：一帧生效的即时操作（传送、跳跃冲量等）

这套架构天然支持**客户端预测与服务器回滚**：模拟状态可通过 `FMoverSyncState` 进行网络同步，当检测到偏差时可回滚到先前状态并重新模拟。它通过 Backend Liaison 接口接入不同的网络后端（独立运行、Network Prediction Plugin、Chaos 物理等）。

**为什么存在**：传统 `UCharacterMovementComponent` 将所有移动逻辑耦合在一个巨大的类中，难以扩展和测试。Mover 将移动拆分为独立模块，每个模块可单独测试、组合和网络同步，更适合现代联网游戏的开发需求。

## 使用场景

- 你正在开发一个需要**精确客户端预测**的多人动作/射击游戏 → 用 Mover 作为移动后端
- 你需要**可组合的移动系统**，如同时叠加跳跃+冲刺+击退 → 用 Layered Moves 系统
- 你希望**自定义移动模式**（如攀爬、滑铲）而不修改基类 → 继承 `UBaseMovementMode`
- 你需要**NavMesh 导航移动**集成到自定义移动系统 → 用 `UNavMoverComponent` + `UNavWalkingMode`
- 你的游戏需要**异步物理模拟**支持（Chaos 集成） → Mover 的 Async 模式设计支持 worker 线程执行

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `K2_QueueLayeredMove` | 克隆并排队一个分层移动 | `UMoverComponent` |
| `K2_QueueLayeredMoveActivation` | 激活一个已注册的分层移动逻辑 | `UMoverComponent` |
| `K2_QueueLayeredMoveActivationWithContext` | 使用上下文激活分层移动 | `UMoverComponent` |
| `K2_QueueMovementModifier` | 克隆并排队一个移动修改器 | `UMoverComponent` |
| `K2_QueueInstantMovementEffect` | 克隆并排队一个瞬时移动效果 | `UMoverComponent` |
| `CancelModifierFromHandle` | 通过句柄取消移动修改器 | `UMoverComponent` |
| `CancelFeaturesWithTag` | 取消所有匹配 Tag 的移动特性 | `UMoverComponent` |
| `K2_RegisterMove` | 注册分层移动逻辑类 | `UMoverComponent` |
| `BindProcessGeneratedMovement` | 绑定移动生成后处理回调 | `UMoverComponent` |

**基于移动的工具函数：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsADynamicBase` | 判断移动基座是否可动 | `UBasedMovementUtils` |
| `GetMovementBaseVelocity` | 获取移动基座的世界空间速度 | `UBasedMovementUtils` |
| `TransformLocationToWorld` | 基座相对坐标转世界坐标 | `UBasedMovementUtils` |
| `ComputeControlledGroundMove` | 计算受控地面移动 | `UGroundMovementUtils` |
| `ComputeControlledFreeMove` | 计算自由飞行移动 | `UAirMovementUtils` |
| `ComputeControlledWaterMove` | 计算水中移动 | `UWaterMovementUtils` |
| `SetDirectionalInput` | 设置方向意图输入 | `UMoverDataModelBlueprintLibrary` |
| `SetVelocityInput` | 设置速度输入 | `UMoverDataModelBlueprintLibrary` |
| `GetLocationFromSyncState` | 从同步状态获取位置 | `UMoverDataModelBlueprintLibrary` |

**角色组件：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Jump` | 执行跳跃 | `UCharacterMoverComponent` |
| `Crouch` / `UnCrouch` | 蹲下/取消蹲下 | `UCharacterMoverComponent` |
| `CanActorJump` | 检查是否可以跳跃 | `UCharacterMoverComponent` |
| `IsFalling` / `IsSwimming` / `IsOnGround` | 查询移动状态 | `UCharacterMoverComponent` |

### 使用示例（蓝图描述）

**基本角色移动设置：**
1. 在角色 Actor 上添加 `UCharacterMoverComponent`
2. 添加 `UMoverStandaloneLiaisonComponent`（单机）或 `UMoverNetworkPredictionLiaisonComponent`（联网）
3. 在 MoverComponent 的 `MovementModes` 映射中配置 Walking/Falling 等模式
4. 设置 `StartingMovementMode` 为 `Walking`
5. 在 Input Producer 中实现输入采集，调用 `SetDirectionalInput`

**触发跳跃效果：**
1. 创建 `FJumpImpulseEffect` 结构体实例
2. 设置 `UpwardsSpeed`（如 500）
3. 调用 `K2_QueueInstantMovementEffect` 排入队列

**触发冲刺移动：**
1. 创建 `FLayeredMove_LinearVelocity` 结构体实例
2. 设置 `Velocity`、`DurationMs` 和 `SettingsFlags`
3. 调用 `K2_QueueLayeredMove` 排入队列
4. 也可注册 `ULinearVelocityMoveLogic` 类后用 `K2_QueueLayeredMoveActivation` 激活

## C++ 用法

### 头文件引入

```cpp
#include "MoverComponent.h"
#include "CharacterMoverComponent.h"
#include "DefaultMovementSet/LayeredMoves/BasicLayeredMoves.h"
#include "DefaultMovementSet/InstantMovementEffects/BasicInstantMovementEffects.h"
#include "DefaultMovementSet/Settings/CommonLegacyMovementSettings.h"
#include "MoverDataModelTypes.h"
```

### 基本用法

**来源：`Public/MoverComponent.h`**

```cpp
// 排队一个分层移动（跳跃冲刺效果）
UMoverComponent* MoverComp = /* 获取组件 */;

// 创建线性速度分层移动
TSharedPtr<FLayeredMove_LinearVelocity> LinearMove = MakeShared<FLayeredMove_LinearVelocity>();
LinearMove->Velocity = FVector(0, 0, 500);  // 向上 500 cm/s
LinearMove->DurationMs = 500.0;              // 持续 0.5 秒
LinearMove->MixMode = EMoveMixMode::AdditiveVelocity;  // 叠加模式
LinearMove->Priority = 0;

// 排入队列，在下一帧模拟时激活
MoverComp->QueueLayeredMove(LinearMove);
```

**来源：`Public/DefaultMovementSet/InstantMovementEffects/BasicInstantMovementEffects.h`**

```cpp
// 排队一个瞬时跳跃效果
TSharedPtr<FJumpImpulseEffect> JumpEffect = MakeShared<FJumpImpulseEffect>();
JumpEffect->UpwardsSpeed = 500.0f;

MoverComp->QueueInstantMovementEffect(JumpEffect);
```

**来源：`Public/DefaultMovementSet/InstantMovementEffects/BasicInstantMovementEffects.h`**

```cpp
// 排队一个传送效果
TSharedPtr<FTeleportEffect> Teleport = MakeShared<FTeleportEffect>();
Teleport->TargetLocation = FVector(100, 200, 300);
Teleport->bUseActorRotation = true;

MoverComp->QueueInstantMovementEffect(Teleport);
```

### 进阶用法

**来源：`Public/MoverComponent.h`、`Public/MovementModifier.h`**

```cpp
// 使用移动修改器临时改变模拟参数
TSharedPtr<FMovementModifierBase> Modifier = /* 创建自定义修改器 */;
FMovementModifierHandle Handle = MoverComp->QueueMovementModifier(Modifier);

// 稍后通过句柄取消
MoverComp->CancelModifierFromHandle(Handle);

// 通过 Tag 批量取消移动特性
MoverComp->CancelFeaturesWithTag(FGameplayTag::RequestGameplayTag("Status.Buff"));

// 绑定移动生成后回调
MoverComp->BindProcessGeneratedMovement(
    FMover_ProcessGeneratedMovement::CreateLambda(
        [](const FMoverTimeStep& TimeStep, FProposedMove& ProposedMove) {
            // 在移动执行前做最后修改
            ProposedMove.LinearVelocity *= 0.5f;  // 减半速度
        }
    )
);
```

**来源：`Public/MoverComponent.h`、`Public/MoverSimulationTypes.h`**

```cpp
// 使用实例化分层移动系统（新架构）
// 注册移动逻辑
MoverComp->RegisterMove<ULinearVelocityMoveLogic>();

// 使用上下文激活
FLinearVelocityMoveActivationParams Params;
Params.Velocity = FVector(1000, 0, 0);
Params.DurationMs = 1000.0;

MoverComp->QueueLayeredMoveActivationWithContext<ULinearVelocityMoveLogic>(Params);
```

## Demo 示例

**自定义瞬时移动效果：**

```cpp
// MyDashEffect.h
#pragma once
#include "DefaultMovementSet/InstantMovementEffects/BasicInstantMovementEffects.h"
#include "MyDashEffect.generated.h"

USTRUCT(BlueprintType, DisplayName = "Dash Instant Movement Effect")
struct FMyDashEffect : public FInstantMovementEffect
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Mover, meta = (ForceUnits = "cm/s"))
    float DashSpeed = 2000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Mover)
    FVector DashDirection = FVector::ForwardVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Mover)
    float DurationMs = 200.0f;

    virtual bool ApplyMovementEffect(FApplyMovementEffectParams& ApplyEffectParams, FMoverSyncState& OutputState) override;

    virtual FInstantMovementEffect* Clone() const override { return new FMyDashEffect(*this); }
    virtual UScriptStruct* GetScriptStruct() const override { return StaticStruct(); }
    virtual FString ToSimpleString() const override { return TEXT("MyDashEffect"); }
    virtual void NetSerialize(FArchive& Ar) override { Super::NetSerialize(Ar); Ar << DashSpeed; Ar << DashDirection; Ar << DurationMs; }
};
```

```cpp
// MyDashEffect.cpp
#include "MyDashEffect.h"
#include "MoverComponent.h"
#include "MoverSimulationTypes.h"

bool FMyDashEffect::ApplyMovementEffect(FApplyMovementEffectParams& ApplyEffectParams, FMoverSyncState& OutputState)
{
    // 通过 OutputState 的数据集合获取默认同步状态并修改速度
    FMoverDefaultSyncState* SyncState = OutputState.SyncStateCollection.FindDataByType<FMoverDefaultSyncState>();
    if (SyncState)
    {
        FVector CurrentVel = SyncState->GetVelocity_WorldSpace();
        FVector DashVel = DashDirection.GetSafeNormal() * DashSpeed;
        // 设置叠加速度到同步状态
        // 实际项目中可能需要通过 Layered Move 来持续施加
    }
    return true;
}
```

**使用方式：**

```cpp
TSharedPtr<FMyDashEffect> Dash = MakeShared<FMyDashEffect>();
Dash->DashDirection = GetActorForwardVector();
Dash->DashSpeed = 2000.0f;
Dash->DurationMs = 200.0f;
MoverComp->QueueInstantMovementEffect(Dash);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NetworkPrediction` | Network Prediction Plugin 后端集成（`MoverNetworkPredictionLiaison`） |
| `NavigationSystem` | NavMesh 导航移动支持（`NavWalkingMode`、`NavMoverComponent`） |
| `GameplayTags` | 移动特性的 Tag 系统（Tag 取消、模式标识） |
| `Chaos` / `PhysicsCore` | 物理模拟后端支持 |
| `MoverCVDData` | Chaos Visual Debugger 集成数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6ef46a3c` | Mover: update README for next release | 更新 README 文档以准备下一版本发布 |
| 2026-05-22 | `4ea45e21` | Mover: fix bug where skipping vertical anim root motion was not being respected in all montage cases | 修复垂直动画根运动跳过在某些蒙太奇场景下不生效的 bug |
| 2026-05-20 | `dd78e781` | Mover: fix for inconsistent behavior of mode-changed events (kinematic / NPP cases) resulting in que | 修复运动学和 NPP 模式下模式切换事件行为不一致的问题 |
| 2026-05-14 | `801be5dc` | Mover/ChaosMover: Just like moves, move instances are now using a pull mechanism so they can work in | 移动实例改用拉取机制以兼容异步物理工作线程 |
| 2026-05-14 | `d040bc9f` | Mover: adding simulation that's specific to kinematically-moved Actors | 为运动学驱动的 Actor 添加专用模拟类 |

### 维护评价

**活跃维护中。** Mover 插件处于高频开发阶段：

- **创建于 2024-02-02**，约 1 年前，是 UE5 新一代移动系统的实验性实现
- **最近 1 个月内有持续更新**（5 月多次提交），内容涉及 bug 修复、架构改进和新功能
- 引入了实例化分层移动（`FLayeredMoveInstance`/`ULayeredMoveLogic`）、专用运动学模拟（`UKinematicActorSimulation`）等新架构
- 仍在持续改进异步模拟兼容性和网络同步
- **已知限制**：位于 Experimental 文件夹，默认未启用，API 可能在后续版本中有破坏性变更
- **推荐使用**：对于新项目，尤其是需要精确客户端预测的联网游戏，建议关注并开始评估。但不建议在生产环境中使用，需等待其脱离 Experimental 状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
- 官方文档（暂无 URL）