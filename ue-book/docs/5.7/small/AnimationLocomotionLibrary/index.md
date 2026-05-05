# Animation Locomotion Library

> Collection of techniques for driving locomotion animations

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ✅ `CanContainContent: true` |
| 模块 | `AnimationLocomotionLibraryRuntime` (Runtime), `AnimationLocomotionLibraryEditor` (UncookedOnly) |
| 创建时间 | 2021-09-17 |
| 年龄标签 | 🆕 (约 4.6 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationLocomotionLibrary) | |

⚠️ **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，API 可能在未来版本中发生变化。

⚠️ **需要手动启用**：默认未启用，需在项目设置或 `.uproject` 中手动添加。

## 用途

AnimationLocomotionLibrary 提供了一套基于**距离匹配 (Distance Matching)** 的动画驱动技术，用于解决角色移动时脚部滑步（foot sliding）的问题。

传统做法是按时间线性播放动画，当角色移动速度与动画速度不一致时就会出现脚滑。这个 plugin 通过以下方式解决这个问题：

1. **距离匹配播放**：根据角色实际移动的距离来推进动画时间，而非固定时间步进，自动调整播放速率使动画与移动同步
2. **目标距离匹配**：根据角色到停止/转向点的距离，自动选择动画中最合适的时间点，实现无滑步的停止和转身
3. **速度匹配播放率**：对于循环动画（走/跑循环），自动调整播放率使其与实际移动速度匹配
4. **运动预测**：基于 `UCharacterMovementComponent` 的物理参数，预测角色停止和转向的位置

该 plugin 被 Lyra 示例项目广泛使用，是 Epic 推荐的角色移动动画方案之一。

## 使用场景

- 你正在做第三人称/第一人称角色控制器，需要让角色的行走/跑步动画与实际移动速度完美同步 → 使用 `SetPlayrateToMatchSpeed`
- 你的角色需要快速停止而脚部不能滑动 → 使用 `DistanceMatchToTarget` + `UDistanceCurveModifier`
- 你的角色需要急转向（pivot）而不滑步 → 使用 `PredictGroundMovementPivotLocation` + `DistanceMatchToTarget`
- 你需要过渡动画（起动、停止、转向）与移动完美同步 → 使用 `AdvanceTimeByDistanceMatching`

## 蓝图用法

本 plugin 所有 Runtime 函数均为 `BlueprintCallable` / `BlueprintPure` 且标记 `BlueprintThreadSafe`，可在动画蓝图中安全使用。

### 核心节点

#### 距离匹配（AnimDistanceMatchingLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AdvanceTimeByDistanceMatching` | 按距离推进动画时间（用于过渡动画） | `UAnimDistanceMatchingLibrary` |
| `DistanceMatchToTarget` | 根据目标距离设置动画时间（用于停止/转向动画） | `UAnimDistanceMatchingLibrary` |
| `SetPlayrateToMatchSpeed` | 调整播放率以匹配移动速度（用于循环动画） | `UAnimDistanceMatchingLibrary` |

#### 移动预测（AnimCharacterMovementLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PredictGroundMovementStopLocation` | 预测角色停止位置（本地空间） | `UAnimCharacterMovementLibrary` |
| `PredictGroundMovementPivotLocation` | 预测角色转向枢轴位置（本地空间） | `UAnimCharacterMovementLibrary` |

### 使用示例（蓝图描述）

#### 示例 1：跑步循环的速度匹配

1. 在 AnimGraph 中添加 **Sequence Player** 节点，选择跑步循环动画
2. 将 Sequence Player 的引脚连接到 **SetPlayrateToMatchSpeed** 节点
3. `SpeedToMatch` 输入连接到角色移动组件的 `GetVelocity` → `VectorLength`（获取当前速度）
4. `PlayRateClamp` 保持默认 `(0.75, 1.25)` 或根据需要调整
5. 输出连接到 Result 引脚

#### 示例 2：停止动画的距离匹配

1. 对停止动画应用 **Distance Curve Modifier**（在动画资产上右键 → Add Modifier）
2. 在 AnimGraph 中添加 **Sequence Evaluator** 节点，选择停止动画
3. 将 Sequence Evaluator 连接到 **DistanceMatchToTarget** 节点
4. `DistanceToTarget` 连接到 `PredictGroundMovementStopLocation` 的返回值长度（`VectorLength`）
5. `DistanceCurveName` 设置为 `"Distance"`（与 Modifier 的曲线名一致）
6. Sequence Evaluator 的 Explicit Time 设置为 **Always Dynamic**

#### 示例 3：起动动画的距离推进

1. 对起动动画应用 Distance Curve Modifier
2. 在 AnimGraph 中添加 **Sequence Evaluator** 节点，选择起动动画
3. 连接到 **AdvanceTimeByDistanceMatching** 节点
4. `DistanceTraveled` 连接到角色当前帧的移动距离（通常通过 `GetVelocity * DeltaTime` 计算）
5. `DistanceCurveName` 设置为 `"Distance"`

## C++ 用法

### 头文件引入

```cpp
#include "AnimDistanceMatchingLibrary.h"
#include "AnimCharacterMovementLibrary.h"
```

### 基本用法

这些函数主要设计用于动画蓝图的 ThreadSafe 节点中，通过 `FSequenceEvaluatorReference` / `FSequencePlayerReference` 操作动画节点。

**SetPlayrateToMatchSpeed** — 循环动画速度匹配：

```cpp
// 在 AnimGraph 节点函数中使用
// 来源: Source/Runtime/Private/AnimDistanceMatchingLibrary.cpp:240-285
FSequencePlayerReference Result = UAnimDistanceMatchingLibrary::SetPlayrateToMatchSpeed(
    SequencePlayer,    // Sequence Player 引用
    SpeedToMatch,      // 角色当前移动速度（通常来自 GetVelocity().Size2D()）
    FVector2D(0.75f, 1.25f)  // 播放率范围限制
);
```

**DistanceMatchToTarget** — 停止动画距离匹配：

```cpp
// 来源: Source/Runtime/Private/AnimDistanceMatchingLibrary.cpp:214-238
FSequenceEvaluatorReference Result = UAnimDistanceMatchingLibrary::DistanceMatchToTarget(
    SequenceEvaluator,  // Sequence Evaluator 引用
    DistanceToTarget,   // 到停止点的距离
    FName("Distance")   // 距离曲线名称
);
```

**PredictGroundMovementStopLocation** — 预测停止位置：

```cpp
// 来源: Source/Runtime/Private/AnimCharacterMovementLibrary.cpp:7-30
FVector StopLocation = UAnimCharacterMovementLibrary::PredictGroundMovementStopLocation(
    CharacterMovement->Velocity,
    CharacterMovement->bUseSeparateBrakingFriction,
    CharacterMovement->BrakingFriction,
    CharacterMovement->GroundFriction,
    CharacterMovement->BrakingFrictionFactor,
    CharacterMovement->BrakingDecelerationWalking
);
float DistanceToStop = StopLocation.Size2D();
```

### 进阶用法

完整的停止预测 + 距离匹配组合：

```cpp
// 1. 预测停止位置
FVector StopLocation = UAnimCharacterMovementLibrary::PredictGroundMovementStopLocation(
    Velocity, bUseSeparateBrakingFriction, BrakingFriction,
    GroundFriction, BrakingFrictionFactor, BrakingDecelerationWalking
);
float DistanceToStop = StopLocation.Size2D();

// 2. 用停止距离匹配动画时间
FSequenceEvaluatorReference EvalResult = UAnimDistanceMatchingLibrary::DistanceMatchToTarget(
    SequenceEvaluator, DistanceToStop, FName("Distance")
);

// 3. 如果是循环动画，用速度匹配播放率
FSequencePlayerReference PlayerResult = UAnimDistanceMatchingLibrary::SetPlayrateToMatchSpeed(
    SequencePlayer, Velocity.Size2D(), FVector2D(0.75f, 1.25f)
);
```

## Demo 示例

### Build.cs 依赖

```csharp
// 如果只需要运行时功能（动画蓝图中使用）
PublicDependencyModuleNames.AddRange(new string[] {
    "AnimationLocomotionLibraryRuntime",
    "AnimGraphRuntime",
    "AnimationCore"
});

// 如果需要在编辑器工具中使用 DistanceCurveModifier
PublicDependencyModuleNames.AddRange(new string[] {
    "AnimationLocomotionLibraryEditor",
    "AnimationModifiers",
    "AnimationBlueprintLibrary"
});
```

### 最小使用示例（AnimBP 函数）

```cpp
// MyAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "AnimDistanceMatchingLibrary.h"
#include "AnimCharacterMovementLibrary.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 用于 Property Access 获取移动速度
    UPROPERTY(BlueprintReadOnly, Category = "Movement")
    float GroundSpeed = 0.0f;

    // 用于 Property Access 获取到停止点的距离
    UPROPERTY(BlueprintReadOnly, Category = "Movement")
    float DistanceToStop = 0.0f;

    // 用于 Property Access 获取本帧移动距离
    UPROPERTY(BlueprintReadOnly, Category = "Movement")
    float DistanceTraveled = 0.0f;
};
```

> **注意**：由于本 plugin 的函数都标记为 `BlueprintThreadSafe`，推荐在 AnimGraph 中通过蓝图节点使用。C++ 中直接调用主要用于扩展自定义 AnimGraph 节点。

## 模块依赖

### Runtime 模块（AnimationLocomotionLibraryRuntime）

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 动画图节点运行时支持（SequencePlayer/SequenceEvaluator） |
| `AnimationCore` | 动画核心基础设施 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |

### Editor 模块（AnimationLocomotionLibraryEditor）

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 动画图运行时支持 |
| `AnimationModifiers` | Animation Modifier 基类支持 |
| `AnimationBlueprintLibrary` | 动画蓝图工具库（曲线操作） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 自动化代码整理，无功能变更 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 同上，批量应用 |
| 2025-04-23 | `93a13080` | dllstorage conversion for LyraGame build target | 构建系统适配，无功能变更 |

### 维护评价

- **创建时间**：2021 年 9 月，约 4.6 年历史
- **Beta 状态**：`IsBetaVersion: true`，自创建以来一直是 Beta
- **最近更新**：近 3 次提交均为自动化工具生成的代码整理，无实质性功能更新
- **活跃度**：低。最后一次实质性功能更新需追溯到更早的 commit
- **无测试用例**：Engine 目录下未找到此 plugin 的自动化测试
- **Lyra 依赖**：此 plugin 是 Lyra 示例项目的核心组件之一，Epic 不太可能完全废弃

**综合评价**：⚠️ **使用需注意 Beta 状态**。虽然 plugin 功能稳定且被 Lyra 项目采用，但 API 仍标记为 Beta，未来可能有 Breaking Changes。建议在使用时做好版本适配准备。推荐在需要距离匹配动画的项目中使用，这是 Epic 官方推荐的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationLocomotionLibrary)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（Engine 目录下未找到相关测试文件）
- [Lyra 示例项目](https://github.com/EpicGames/UnrealEngine/tree/5.7/Samples/Games/Lyra) — 距离匹配技术的实际应用参考
