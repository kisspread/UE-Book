# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.  
> Please refer to the README document for information about getting started, an overview of concepts, and known issues.

| 属性 | 值 |
|---|---|
| 中文名 | 移动系统框架 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 是 Epic Games 为 UE5 设计的新一代角色移动系统，旨在取代传统的 `CharacterMovementComponent`。它提供了：

- **模块化、可扩展的运动模式**：通过 `UBaseMovementMode` 派生类定义不同的移动行为（行走、坠落、飞行、游泳、导航网格行走等），可自由组合和切换。
- **网络回滚支持**：基于 Network Prediction 插件（`MoverNetworkPredictionLiaisonComponent`）或 Chaos Physics 网络预测（`MoverNetworkPhysicsLiaisonComponent`），实现低延迟、高一致性的网络同步。
- **分层移动（Layered Moves）**：允许同时叠加多个移动效果（如线性速度、跳跃冲量、动画根运动、多跳、发射等），彼此互不干扰。
- **即时移动效果（Instant Movement Effects）**：用于一次性操作（传送、冲量、强制模式切换等），不影响后续 tick。
- **独立（Standalone）模式**：提供 `MoverStandaloneLiaisonComponent`，用于非网络游戏（单机/本地多玩家）的简单驱动。
- **调试与可视化**：内含 `MoverDebugComponent`（轨迹、拖尾、纠错显示）以及与 Gameplay Debugger 和 Chaos Visual Debugger 的集成。
- **AI 导航集成**：`NavMoverComponent` 实现 `INavMovementInterface`，使 Mover 可与 UE 的路径寻路系统一起使用。
- **角色专用扩展**：`UCharacterMoverComponent` 提供跳跃、蹲下、姿态管理等高级角色行为。

Mover 解决了传统 `CharacterMovementComponent` 在扩展性、网络回滚、异步物理、模块化方面的痛点，尤其适合需要精细网络同步和复杂移动机制的项目。

## 使用场景

- **需要精确网络回滚的在线射击游戏**：利用 Network Prediction 后端点，客户端预测与服务器校验无缝结合。
- **需要高度定制移动模式的游戏**（如平台跳跃、潜行、飞行）：可通过派生 `UBaseMovementMode` 快速实现新模式，无需重写整个移动逻辑。
- **需要同时叠加多种移动效果的场景**（如加速道具、缓动、击退）：使用分层移动系统，每种效果独立且可混合。
- **需要 AI 角色使用导航网格并保持与玩家一致移动行为的游戏**：`NavMoverComponent` 配合路径寻路，同时享受 Mover 的网络回滚优势。
- **需要可视化调试移动轨迹和网络纠错的开发阶段**：`MoverDebugComponent` 提供轨迹预测和历史回放。

## 蓝图用法

### 核心组件

| 组件 | 说明 |
|---|---|
| `MoverComponent` | 移动系统核心，管理运动模式、同步状态和后端点 |
| `CharacterMoverComponent` | 继承自 `MoverComponent`，增加跳跃、蹲下、姿态管理等角色行为 |
| `NavMoverComponent` | 为 Mover 提供 AI 导航接口 |
| `MoverDebugComponent` | 显示轨迹、拖尾、网络纠错 |
| `MoverStandaloneLiaisonComponent` | 单机模式下驱动移动 |
| `MoverNetworkPredictionLiaisonComponent` | 基于 Network Prediction 插件的后端点 |
| `MoverNetworkPhysicsLiaisonComponent` | 基于 Chaos Physics 网络物理的后端点（已废弃） |

### 常用节点 (CharacterMoverComponent)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Jump` | 执行跳跃 | `UCharacterMoverComponent` |
| `CanActorJump` | 检查能否跳跃 | `UCharacterMoverComponent` |
| `Crouch` | 执行蹲下 | `UCharacterMoverComponent` |
| `UnCrouch` | 站起 | `UCharacterMoverComponent` |
| `CanCrouch` | 检查能否蹲下 | `UCharacterMoverComponent` |
| `IsCrouching` | 是否在蹲下状态 | `UCharacterMoverComponent` |
| `IsFalling` | 是否在坠落状态 | `UCharacterMoverComponent` |
| `IsOnGround` | 是否在地面 | `UCharacterMoverComponent` |
| `IsFlying` | 是否在飞行 | `UCharacterMoverComponent` |
| `IsSwimming` | 是否在游泳 | `UCharacterMoverComponent` |
| `IsAirborne` | 是否在空中（飞行或坠落） | `UCharacterMoverComponent` |
| `IsSlopeSliding` | 是否在滑动 | `UCharacterMoverComponent` |

### 运动模式相关节点

运动模式本身是蓝图类，可以在蓝图类设置中配置属性（如 WalkingMode 的 MaxWalkSlopeCosine、FallingMode 的 AirControlPercentage 等）。常用事件绑定：

| 事件 | 说明 | 所属类 |
|---|---|---|
| `OnLanded` | 着陆时广播，返回着陆模式名和 HitResult | `UFallingMode`, `UAsyncFallingMode` |
| `OnStanceChanged` | 姿态改变时广播（蹲下/站立） | `UCharacterMoverComponent` |

### 分层移动效果（Layered Moves）

这些结构体可通过 `UMoverComponent` 的 `AddLayeredMove` 或直接修改输入控制上下文中的分层移动列表来应用。

| 结构体 | 说明 |
|---|---|
| `FLayeredMove_LinearVelocity` | 施加恒线速度，可受曲线控制强度 |
| `FLayeredMove_JumpImpulseOverDuration` | 在一段时间内持续向上的跳跃冲量 |
| `FLayeredMove_Launch` | 一次性发射，可强制切换运动模式 |
| `FLayeredMove_MultiJump` | 支持多段跳跃（如二段跳） |
| `FLayeredMove_AnimRootMotion` | 从动画蒙太奇提取根运动 |
| `FLayeredMove_RootMotionAttribute` | 从网格体自定义属性提取根运动（实验性） |

### 即时移动效果（Instant Movement Effects）

| 结构体 | 说明 |
|---|---|
| `FTeleportEffect` | 传送至指定位置/旋转（非异步安全） |
| `FAsyncTeleportEffect` | 异步安全的传送 |
| `FJumpImpulseEffect` | 单次向上的速度冲量 |
| `FApplyVelocityEffect` | 施加速度冲量，可强制切换模式 |

### 使用示例（蓝图）

**添加分层移动（线性速度）**：

1. 在 `Event Tick` 或 `自定义事件` 中，获取 `MoverComponent` 的 `InputCmd`（即 `FMoverInputCmdContext`）。
2. 从 `InputCmd` 的 `LayeredMoves` 数组添加一个新的 `FLayeredMove_LinearVelocity`，设置 `Velocity`、`DurationMs` 等。
3. 或者直接调用 `AddLayeredMove` 函数（如果有封装）—— 实际接口可能需通过函数库访问。

**响应着陆**：

1. 在拥有 `FallingMode` 或 `AsyncFallingMode` 的蓝图类中，将 `OnLanded` 事件绑定到自定义事件。
2. 在自定义事件中获取 `NextMovementModeName` 和 `HitResult`，执行如播放着陆音效、改变动画等逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "MoverComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
```

### 基本用法

创建一个使用 Mover 的角色类（继承自 `ACharacter` 或自定义 Actor），添加 `UCharacterMoverComponent` 作为移动组件。

```cpp
// MyCustomCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCustomCharacter.generated.h"

class UCharacterMoverComponent;
class UMoverStandaloneLiaisonComponent;

UCLASS()
class AMyCustomCharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyCustomCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
    UCharacterMoverComponent* MoverComponent;

    // 用于单机模式的后端点（若需要网络，则使用 UMoverNetworkPredictionLiaisonComponent）
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
    UMoverStandaloneLiaisonComponent* StandaloneLiaison;
};
```

```cpp
// MyCustomCharacter.cpp
#include "MyCustomCharacter.h"

#include "MoverComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
#include "Backends/MoverStandaloneLiaison.h"

AMyCustomCharacter::AMyCustomCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建 MoverComponent
    MoverComponent = CreateDefaultSubobject<UCharacterMoverComponent>(TEXT("MoverComponent"));
    MoverComponent->SetUpdatedComponent(RootComponent);

    // 创建并设置后端点（单机模式）
    StandaloneLiaison = CreateDefaultSubobject<UMoverStandaloneLiaisonComponent>(TEXT("StandaloneLiaison"));
    MoverComponent->SetBackendLiaison(StandaloneLiaison);
}
```

**来源**：`Engine/Plugins/Experimental/Mover/Source/Mover/Public/DefaultMovementSet/CharacterMoverComponent.h`  
**来源**：`Engine/Plugins/Experimental/Mover/Source/Mover/Public/Backends/MoverStandaloneLiaison.h`

### 网络预测后端点

若要启用 Network Prediction 回滚，使用 `UMoverNetworkPredictionLiaisonComponent` 代替 Standalone 版本：

```cpp
#include "Backends/MoverNetworkPredictionLiaison.h"

// 在构造函数中
MoverComponent->SetBackendLiaison(CreateDefaultSubobject<UMoverNetworkPredictionLiaisonComponent>(TEXT("NetworkLiaison")));
```

### 添加分层移动

```cpp
#include "DefaultMovementSet/LayeredMoves/BasicLayeredMoves.h"

void AMyCustomCharacter::ApplyKnockback(const FVector& Direction, float Speed)
{
    if (!MoverComponent) return;

    // 创建分层移动：线性速度，持续 500ms，方向为冲击方向
    FLayeredMove_LinearVelocity KnockbackMove;
    KnockbackMove.Velocity = Direction.GetSafeNormal() * Speed;
    KnockbackMove.DurationMs = 500;
    KnockbackMove.MixMode = ELayeredMoveMixMode::OverrideVelocity; // 覆盖当前速度

    // 直接添加到输入命令（需要获取当前输入命令）
    // 通常建议通过 MoverComponent 的接口添加，但这需要查阅具体 API
    // 此处为示意：实际可通过 InputCmd.LayeredMoves.Add(...)
}
```

### 设置运动模式

```cpp
// 强制切换运动模式
MoverComponent->SetMovementMode("Falling");
```

## Demo 示例

下面是一个完整的最小示例，创建一个 Actor 并使其使用 Mover 移动系统，在单机模式下每秒朝前移动。

**MyMoverActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMoverActor.generated.h"

class UCharacterMoverComponent;
class UMoverStandaloneLiaisonComponent;

UCLASS()
class AMyMoverActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMoverActor();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mover")
    UCharacterMoverComponent* MoverComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mover")
    UMoverStandaloneLiaisonComponent* StandaloneLiaison;

    UPROPERTY(EditAnywhere, Category = "Mover")
    float MoveSpeed = 100.0f;
};
```

**MyMoverActor.cpp**
```cpp
#include "MyMoverActor.h"

#include "MoverComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
#include "Backends/MoverStandaloneLiaison.h"
#include "MoverTypes.h" // 包含 FMoverInputCmdContext

AMyMoverActor::AMyMoverActor()
{
    PrimaryActorTick.bCanEverTick = true;

    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

    MoverComponent = CreateDefaultSubobject<UCharacterMoverComponent>(TEXT("MoverComponent"));
    MoverComponent->SetUpdatedComponent(RootComponent);

    StandaloneLiaison = CreateDefaultSubobject<UMoverStandaloneLiaisonComponent>(TEXT("StandaloneLiaison"));
    MoverComponent->SetBackendLiaison(StandaloneLiaison);
}

void AMyMoverActor::BeginPlay()
{
    Super::BeginPlay();
    // 初始设置运动模式为行走
    MoverComponent->SetMovementMode(FName("Walking"));
}

void AMyMoverActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 设置输入：持续朝前移动
    if (MoverComponent)
    {
        FMoverInputCmdContext& InputCmd = MoverComponent->GetInputCmd();
        InputCmd.MoveInput = FVector(MoveSpeed, 0.0f, 0.0f);
        InputCmd.OrientationIntent = FRotator::ZeroRotator;
    }
}
```

**说明**：

- 需要确保项目启用了 `Mover` 和 `MoverCVDData` 以及 `MoverStandaloneLiaison` 等模块（See 模块依赖）。
- 实际使用时后端选择需根据网络需求调整。此示例使用 Standalone 后端点。
- 需要为 Actor 添加碰撞形状（如胶囊体）才能使移动碰撞生效。可在构造函数中添加 `UCapsuleComponent` 并传递给 `SetUpdatedComponent`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MoverCVDData` | Chaos Visual Debugger 数据通道定义，用于调试追踪 |
| `ChaosVisualDebugger` | 可选，用于可视化调试 |
| `NetCore` | 网络序列化和预测基础（如果使用网络后端点） |
| `ChaosPhysicsCore` | 如果使用 Chaos Physics 后端点 |

**特殊依赖**：在使用 Network Prediction 后端点时，还需要启用 `NetworkPrediction` 插件。

**推荐设置（Minimal）**：对于单机项目，只需依赖 `Mover` 和 `MoverCVDData`（但 CVD 数据在非调试版本可忽略）。在项目 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Mover",
    "MoverCVDData"
});
```

若需编辑器扩展，还需添加 `MoverEditor`。

## 维护状态

### 近期更新

- 2025-11-18 c94b0582 — Mover: fix issue where montages with a non-zero start time would be played from the wrong position
- 2025-11-18 0b7174b5 — Mover: Fixing debug editor crash when initializing a CircularBuffer with a capacity of 0 on MoverComponent
- 2025-11-18 025130bc — [Backout] - CL47742330
- 2025-11-18 796d840a — Mover: Fixing debug editor crash when initializing a CircularBuffer with a capacity of 0 on MoverComponent
- 2025-11-18 0c5c955f — Mover: Adding virtual destructor to BlackboardEntryBase struct to fix a memory leak.

### 维护评价

- **创建时间**：2025-11-18（距今不到1个月），非常新。
- **更新频率**：最近一周内有多次提交，集中在 Bug 修复和内存泄漏修复。
- **活跃度**：作为实验性插件，目前由 Epic Games 持续开发，频繁修复问题。
- **已知问题**：部分类标记为 `DEPRECATED`（如 `UMoverNetworkPhysicsLiaisonComponent`），未来可能移除；某些功能（如根运动属性分层移动）仍为实验性。
- **推荐使用**：适合对网络回滚有高要求的项目，但由于仍处于实验阶段且接口可能变动，不建议用于即将发布的大型项目。对于单机或原型开发，其模块化设计极具价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（Mover 相关章节尚未单独列出，可参阅 Network Prediction 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Mover/Tests)（部分测试位于 `Engine/Tests/` 下）