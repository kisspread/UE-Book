# Network Prediction Extras

> Non essential classes for Network Prediction. Samples, test maps, etc intended to help developers start using the system. Not intended to be used directly in a shipping product.

| 属性 | 值 |
|---|---|
| 中文名 | 网络预测额外示例 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产、代码） |
| 模块 | `NetworkPredictionExtras` (Runtime), `NetworkPredictionExtrasLatentLoad` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-27 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionExtras) | |

## 用途

`NetworkPredictionExtras` 是 `NetworkPrediction` 插件的配套示例与扩展模块。其核心价值在于提供了**一套完整的、可用于学习的网络预测移动系统实现**。它并非一个独立的网络预测框架，而是展示了如何将 `NetworkPrediction` 插件的核心功能（如预测、回滚、状态同步）应用于具体的移动模拟场景中。

该插件解决了以下问题：
1.  **学习门槛**：通过提供开箱即用的、具有完整移动逻辑（如行走、飞行、参数化运动）的示例，降低开发者理解和使用 `NetworkPrediction` 系统的难度。
2.  **实现参考**：它不是一个黑盒，其所有状态定义（输入、同步、辅助）和模拟循环（`SimulationTick`）都对开发者开放，提供了如何自定义网络预测模拟的最佳实践。
3.  **功能扩展**：提供了诸如 Mock 能力系统（模拟冲刺、闪现、开火）和根运动集成等进阶示例，展示了如何在预测系统中实现更复杂的游戏逻辑。

**重要提示**：如其描述所言，这些代码主要用于示例和测试，**不建议**直接用于正式发布的项目。开发者应将其作为学习模板和原型参考，根据自己的项目需求进行重写和优化。

## 使用场景

-   你正在使用或计划使用 UE5 的 `NetworkPrediction` 插件来构建多人游戏 → 用 `NetworkPredictionExtras` 作为学习和原型开发的起点。
-   你需要一个基于网络预测的、可预测和回滚的**角色移动**组件（类似但不同于 `CharacterMovementComponent`） → 参考 `UCharacterMotionComponent` 和 `FCharacterMotionSimulation`。
-   你需要一个基于网络预测的、可预测和回滚的**飞行器移动**组件 → 参考 `UFlyingMovementComponent` 和 `FFlyingMovementSimulation`。
-   你需要一个基于网络预测的、沿预定义路径（如样条线、曲线）运动的物体 → 参考 `UParametricMovementComponent` 和 `FParametricMovementSimulation`。
-   你想要研究如何在**网络预测**框架下集成和实现可预测的**动画根运动** → 参考 `UMockRootMotionComponent` 和 `FMockRootMotionSimulation`。
-   你想要快速搭建一个用于测试 `NetworkPrediction` 功能的多人游戏原型场景 → 可以直接使用或参考 `ANetworkPredictionExtrasCharacter` 和 `ANetworkPredictionExtrasFlyingPawn` 这类示例 Pawn。

## 蓝图用法

该插件的蓝图接口主要集中在几个核心组件和 Pawn 上，用于控制和查询预测移动的状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsSprinting` | 查询当前是否处于冲刺状态 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `IsDashing` | 查询当前是否处于冲刺状态 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `IsBlinking` | 查询当前是否处于闪现状态 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `IsJumping` | 查询当前是否处于跳跃状态 | `UMockCharacterAbilityComponent` |
| `GetStamina` | 获取当前的体力值 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `GetMaxStamina` | 获取最大体力值 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `GetMaxMoveSpeed` | 获取最大移动速度 | `ANetworkPredictionExtrasCharacter`, `ANetworkPredictionExtrasFlyingPawn` |
| `SetMaxMoveSpeed` | 设置最大移动速度 | `ANetworkPredictionExtrasCharacter`, `ANetworkPredictionExtrasFlyingPawn` |
| `EnableInterpolationMode` | 启用或禁用插值模式（用于观察效果） | `UParametricMovementComponent` |
| `OnSprintStateChange` | 蓝图可分配事件，当冲刺状态改变时触发 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `OnDashStateChange` | 蓝图可分配事件，当冲刺状态改变时触发 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `OnBlinkStateChange` | 蓝图可分配事件，当闪现状态改变时触发 | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |
| `OnBlinkActivateEvent` | 蓝图可分配事件，当闪现激活时触发（可回滚） | `UMockFlyingAbilityComponent`, `UMockCharacterAbilityComponent` |

### 使用示例（蓝图描述）

**场景：控制一个使用 MockCharacterAbilityComponent 的角色**

1.  在你的角色蓝图中，添加一个 `UMockCharacterAbilityComponent` 组件（通常会自动替换默认的移动组件）。
2.  在角色蓝图的事件图表中：
    *   绑定 `InputAction` 事件（如 `IA_Sprint`）到 `Action_Sprint_Pressed` 和 `Action_Sprint_Released` 节点。这些函数会在按下/松开按键时设置内部的 `bSprintPressed` 标志，从而影响输入命令。
    *   绑定 `IA_Jump` 事件到 `Action_Jump_Pressed` 和 `Action_Jump_Released`。
    *   使用 `IsJumping` 节点来查询角色当前是否正在跳跃，并据此播放跳跃动画或调整摄像机。
    *   绑定 `OnBlinkActivateEvent` 事件。当事件触发时，你会收到 `DestinationLocation`（闪现目的地）和 `RandomValue`（用于可预测的随机效果）。你可以在事件中播放闪现特效。同时，实现 `OnBlinkActivateEventRollback` 事件来处理预测回滚时的特效清理（如瞬间移动特效）。
3.  在 HUD 蓝图中，可以获取角色的 `MockCharacterAbilityComponent` 引用，并使用 `GetStamina` 和 `GetMaxStamina` 节点来更新体力条 UI。

## C++ 用法

### 头文件引入

```cpp
// 引入核心模拟类型（角色运动为例）
#include "CharacterMotionSimulation.h"

// 引入移动组件
#include "CharacterMotionComponent.h"

// 如果要自定义模拟，可能需要引入基类
#include "BaseMovementSimulation.h"
```

### 基本用法：定义自己的移动状态

要使用 `NetworkPrediction` 系统，首先需要定义三个核心状态结构体。以下示例基于 `CharacterMotionSimulation.h` 简化而来。

```cpp
// 来源: Engine/Plugins/Runtime/NetworkPredictionExtras/Source/NetworkPredictionExtras/Public/CharacterMotionSimulation.h
// 1. 输入命令：由客户端每帧生成
struct FMyInputCmd
{
    FVector MovementInput = FVector::ZeroVector;
    FRotator RotationInput = FRotator::ZeroRotator;

    void NetSerialize(const FNetSerializeParams& P)
    {
        P.Ar << MovementInput;
        P.Ar << RotationInput;
    }
};

// 2. 同步状态：需要在服务器和客户端之间保持同步的关键状态
struct FMySyncState
{
    FVector Location = FVector::ZeroVector;
    FRotator Rotation = FRotator::ZeroRotator;
    FVector Velocity = FVector::ZeroVector;

    void NetSerialize(const FNetSerializeParams& P)
    {
        P.Ar << Location;
        P.Ar << Rotation;
        P.Ar << Velocity;
    }

    // 判断客户端状态是否需要与权威服务器状态进行调和（回滚）
    bool ShouldReconcile(const FMySyncState& AuthorityState) const
    {
        // 例如，如果位置误差超过阈值
        const float Tolerance = 1.0f;
        return !Location.Equals(AuthorityState.Location, Tolerance);
    }

    void Interpolate(const FMySyncState* From, const FMySyncState* To, float PCT)
    {
        Location = FMath::Lerp(From->Location, To->Location, PCT);
        Rotation = FMath::Lerp(From->Rotation, To->Rotation, PCT);
        Velocity = FMath::Lerp(From->Velocity, To->Velocity, PCT);
    }
};

// 3. 辅助状态：不经常改变的配置参数，输入到模拟中
struct FMyAuxState
{
    float MaxSpeed = 600.0f;
    float Acceleration = 2048.0f;

    void NetSerialize(const FNetSerializeParams& P)
    {
        P.Ar << MaxSpeed;
        P.Ar << Acceleration;
    }

    void Interpolate(const FMyAuxState* From, const FMyAuxState* To, float PCT)
    {
        MaxSpeed = FMath::Lerp(From->MaxSpeed, To->MaxSpeed, PCT);
        Acceleration = FMath::Lerp(From->Acceleration, To->Acceleration, PCT);
    }
};
```

### 进阶用法：实现自定义的移动模拟类

定义了状态类型后，需要创建一个模拟类来处理每帧的移动逻辑。

```cpp
// 来源: Engine/Plugins/Runtime/NetworkPredictionExtras/Source/NetworkPredictionExtras/Public/CharacterMotionSimulation.h 的简化版本
// 4. 定义状态类型元组
using MyMovementStateTypes = TNetworkPredictionStateTypes<FMyInputCmd, FMySyncState, FMyAuxState>;

// 5. 实现模拟类
class FMyMovementSimulation : public FBaseMovementSimulation
{
public:
    // NetworkPrediction 系统每帧调用此函数
    void SimulationTick(const FNetSimTimeStep& TimeStep,
                        const TNetSimInput<MyMovementStateTypes>& Input,
                        const TNetSimOutput<MyMovementStateTypes>& Output)
    {
        // DeltaTime
        const float DeltaSeconds = TimeStep.StepMs * 0.001f;

        // 获取当前状态和输出引用
        const FMySyncState* Sync = Input.SyncState;
        const FMyAuxState* Aux = Input.AuxState;
        const FMyInputCmd* Cmd = Input.InputCmd;
        FMySyncState* OutSync = Output.SyncState;

        // 1. 计算新的速度（基于输入和当前速度）
        FVector Acceleration = Cmd->MovementInput.GetSafeNormal() * Aux->Acceleration;
        FVector NewVelocity = Sync->Velocity + (Acceleration * DeltaSeconds);
        NewVelocity = NewVelocity.GetClampedToMaxSize(Aux->MaxSpeed);

        // 2. 计算位移
        FVector Delta = NewVelocity * DeltaSeconds;

        // 3. 执行移动（带碰撞检测）
        FHitResult Hit;
        SafeMoveUpdatedComponent(Delta, Sync->Rotation, true, Hit);

        // 4. 如果发生碰撞，尝试滑动
        if (Hit.IsValidBlockingHit())
        {
            SlideAlongSurface(Delta, 1.f - Hit.Time, Hit.Normal, Hit, true);
        }

        // 5. 更新输出状态
        OutSync->Location = GetUpdateComponentTransform().GetLocation();
        OutSync->Velocity = NewVelocity;
        // Rotation 的更新可能涉及其他逻辑，此处简化
    }
};
```

## Demo 示例

以下是一个完整的、可编译的最小自定义移动模拟示例。它实现了一个简单的、无重力的“漂浮”移动。

**MySimpleMovementSimulation.h**
```cpp
// 一个简单的网络预测移动模拟示例
#pragma once
#include "BaseMovementSimulation.h"
#include "NetworkPredictionStateTypes.h"

// 定义我们的状态类型
struct FSimpleInputCmd { FVector MoveInput; ... /* NetSerialize */ };
struct FSimpleSyncState { FVector Location; ... /* NetSerialize, ShouldReconcile */ };
struct FSimpleAuxState { float Speed; ... /* NetSerialize */ };
using SimpleStateTypes = TNetworkPredictionStateTypes<FSimpleInputCmd, FSimpleSyncState, FSimpleAuxState>;

class FMySimpleMovementSimulation : public FBaseMovementSimulation
{
public:
    void SimulationTick(const FNetSimTimeStep& TimeStep,
                        const TNetSimInput<SimpleStateTypes>& Input,
                        const TNetSimOutput<SimpleStateTypes>& Output);
};
```

**MySimpleMovementSimulation.cpp**
```cpp
#include "MySimpleMovementSimulation.h"

void FMySimpleMovementSimulation::SimulationTick(const FNetSimTimeStep& TimeStep,
                                                  const TNetSimInput<SimpleStateTypes>& Input,
                                                  const TNetSimOutput<SimpleStateTypes>& Output)
{
    const float DeltaSeconds = TimeStep.StepMs * 0.001f;
    const FSimpleInputCmd* Cmd = Input.InputCmd;
    const FSimpleAuxState* Aux = Input.AuxState;
    FSimpleSyncState* OutSync = Output.SyncState;

    // 简单的位移计算：输入方向 * 速度 * 时间
    FVector Delta = Cmd->MoveInput.GetSafeNormal() * Aux->Speed * DeltaSeconds;

    // 使用基类函数移动组件
    FHitResult Hit;
    SafeMoveUpdatedComponent(Delta, FQuat::Identity, true, Hit);

    // 将结果写回输出状态
    OutSync->Location = GetUpdateComponentTransform().GetLocation();
}
```

## 模块依赖

要使用此插件的功能，你的项目或模块需要依赖以下模块（除了 Core/Engine 等常见依赖外）：

| 模块 | 用途 |
|---|---|
| `NetworkPrediction` | **必需**。本插件提供的所有移动模拟和能力系统示例都构建于此插件提供的网络预测框架之上。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生的编译器警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化打印函数中 32/64 位参数与格式化说明符不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 `UE_LOG` 宏调用迁移到新的 `UE_LOGF` 宏。 |
| 2026-03-05 | `af6df933` | Fixed various callsites of FString::Printf/Appendf that used scoped enums | 修复了多处 `FString::Printf/Appendf` 调用中使用作用域枚举导致的潜在问题。 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 移除了受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4` 宏保护的过时头文件包含。 |

### 维护评价

**综合评价：可用作学习参考，但谨慎用于生产**

-   **创建时间与年龄**：该插件创建于 2019 年，已有约 6 年历史。
-   **最近更新频率和内容**：最近的提交（截至 2026 年）集中在**代码质量维护**上，如修复编译警告、统一宏用法、清理过时代码。**没有发现新的功能更新或重大重构**。
-   **维护活跃度**：**不活跃**。最近的更新都是技术债清理，而非针对 `NetworkPrediction` 插件本身或其示例功能的演进。
-   **已知问题与限制**：
    1.  **实验性/非生产就绪**：`.uplugin` 中 `IsBetaVersion=true`，且描述明确指出不用于正式产品。
    2.  **依赖主插件**：其有效性完全依赖于 `NetworkPrediction` 核心插件的稳定性和接口。
    3.  **示例代码性质**：代码以演示为目的，可能在复杂项目中表现不佳或需要大量定制优化。
-   **是否推荐使用**：
    *   **推荐用于学习**：对于想要深入理解 UE5 `NetworkPrediction` 系统如何应用于移动模拟的开发者，这是绝佳的参考。
    *   **不推荐直接用于产品**：正式项目应基于从中学习到的知识，自行实现更精简、更符合项目需求的移动和预测逻辑。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionExtras)
-   官方文档 (无)
-   测试用例 (插件内未发现独立测试目录，测试可能集成在 `NetworkPrediction` 主插件中)