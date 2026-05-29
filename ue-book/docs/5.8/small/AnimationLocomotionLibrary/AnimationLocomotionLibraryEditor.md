# Animation Locomotion Library

> Collection of techniques for driving locomotion animations

| 属性 | 值 |
|---|---|
| 中文名 | 动画运动库 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画资源） |
| 模块 | `AnimationLocomotionLibraryRuntime` (Runtime), `AnimationLocomotionLibraryEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-17 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationLocomotionLibrary) | |

## 用途

该插件提供了一套用于驱动角色运动动画的高级技术集合，旨在解决传统基于时间的动画播放与角色实际移动不同步的问题。其核心功能是实现“距离匹配”动画播放，让动画的播放进度（如起步、停止、转向）与角色在游戏世界中实际移动的距离精确同步，从而获得更真实、响应更迅速的动画效果。

## 使用场景

- 你正在制作一个第三人称动作游戏，希望角色的起步和停止动画能根据玩家按键时长/时机产生精确匹配，而不是播放固定的、时长一致的动画片段。
- 你需要实现“急停”或“转向”动画，希望动画中的根骨骼运动（Root Motion）能准确地在游戏世界中计算出停止点或转向点，避免滑步或视觉上的不协调。
- 你的角色动画系统需要根据实时速度或朝向变化，平滑地在不同运动状态的动画之间切换，并确保动画的相位（Phase）与移动距离挂钩。

## 蓝图用法

插件主要通过蓝图函数库（`AnimDistanceMatchingLibrary`, `AnimTurnInPlaceLibrary`）和动画修改器（`UDistanceCurveModifier`）提供蓝图支持。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Distance Matched Sequence` | 根据当前移动速度启动一个距离匹配的动画序列，并设置预期的停止距离。 | `UAnimDistanceMatchingLibrary` |
| `Stop Distance Matched Sequence` | 停止一个距离匹配的动画序列。 | `UAnimDistanceMatchingLibrary` |
| `Update Distance Matched Sequence Phase` | 更新距离匹配动画序列的播放相位，通常在 `Update Animation` 事件中调用。 | `UAnimDistanceMatchingLibrary` |
| `Apply Turn in Place` | 在动画蓝图中应用原地转向逻辑，通过偏移旋转来保持动画姿态稳定。 | `UAnimTurnInPlaceLibrary` |
| `Distance Curve Modifier` | (动画修改器) 从动画序列的根运动中提取距离信息，并将其烘焙为曲线。 | `UDistanceCurveModifier` |

### 使用示例（蓝图描述）

1.  **准备动画资产**：使用 `DistanceCurveModifier` 修改器（在动画编辑器中应用）为你的动画序列（如起步、停止、转向动画）生成一条距离曲线。曲线名称默认为 `"Distance"`。
2.  **设置动画蓝图**：
    *   在 `Event Blueprint Update Animation` 事件中，调用 `Update Distance Matched Sequence Phase` 节点，输入当前的速度和动画状态参数。
    *   当角色开始移动（例如 `InputAction Move` 触发时），调用 `Start Distance Matched Sequence` 节点，传入对应的动画序列、当前速度、以及可选的“预期停止距离”（例如根据剩余移动输入计算）。
    *   当角色停止移动时，调用 `Stop Distance Matched Sequence` 节点。
3.  **驱动状态机**：将上述节点的输出（如动画序列、播放位置、播放速率）连接到动画状态机（AnimGraph）中的状态节点或混合节点。

## C++ 用法

### 头文件引入

```cpp
#include "AnimationLocomotionLibraryRuntime.h"
// 以及具体使用的类，例如：
#include "AnimDistanceMatchingLibrary.h"
#include "AnimTurnInPlaceLibrary.h"
#include "CharacterMovementLibrary.h"
```

### 基本用法

```cpp
// 来源: Engine/Plugins/Animation/AnimationLocomotionLibrary/Source/Runtime/Private/AnimDistanceMatchingLibrary.cpp
// 测试用例: Engine/Tests/Animation/AnimationLocomotionLibraryRuntimeTests/Private/AnimDistanceMatchingLibraryTest.cpp

// 假设你在动画实例的某个函数中
UAnimDistanceMatchingLibrary::StartDistanceMatchedSequence(
    AnimInstance, // UAnimInstance*
    DistanceMatchedSequenceArgs, // FDistanceMatchingSequenceArgs 结构体，包含动画资产、播放速度等
    CurrentSpeed, // 当前角色速度
    ExpectedStopDistance // 预计停止距离（例如，松开移动键时角色会滑行的距离）
);
```

### 进阶用法

```cpp
// 来源: Engine/Plugins/Animation/AnimationLocomotionLibrary/Source/Runtime/Private/AnimTurnInPlaceLibrary.cpp
// 测试用例: Engine/Tests/Animation/AnimationLocomotionLibraryRuntimeTests/Private/AnimTurnInPlaceLibraryTest.cpp

// 1. 捕获运动快照
UCharacterMovementLibrary::FillCharacterMovementSnapshot(
    CharacterMovementComponent, // UCharacterMovementComponent*
    CharacterSnapshot // 出参，保存速度、加速度、朝向等信息
);

// 2. 更新原地转向
FAnimTurnInPlaceResult TurnInPlaceResult;
UAnimTurnInPlaceLibrary::UpdateTurnInPlace(
    AnimInstance,
    DeltaTime,
    TurnInPlaceArgs, // 包含转向阈值、动画资源等参数
    CharacterSnapshot,
    TurnInPlaceResult // 输出转向状态和动画播放信息
);
```

## Demo 示例

一个最小化的 C++ 示例，演示如何在动画实例中启动距离匹配动画。

**MyAnimInstance.h**
```cpp
#pragma once
#include "Animation/AnimInstance.h"
#include "AnimDistanceMatchingLibrary.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;

    /** 开始移动时调用 */
    UFUNCTION(BlueprintCallable)
    void StartLocomotion(float CurrentSpeed);

protected:
    /** 距离匹配动画序列参数 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    FDistanceMatchingSequenceArgs DistanceMatchArgs;
};
```

**MyAnimInstance.cpp**
```cpp
#include "MyAnimInstance.h"
#include "AnimDistanceMatchingLibrary.h"

void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    // 在每帧更新中驱动距离匹配序列的相位
    UAnimDistanceMatchingLibrary::UpdateDistanceMatchedSequencePhase(this, DeltaSeconds, GetOwningActor()->GetVelocity().Size());
}

void UMyAnimInstance::StartLocomotion(float CurrentSpeed)
{
    // 启动一个距离匹配的起步动画序列
    // ExpectedStopDistance 设置为0表示我们立即开始播放，不预测停止点（常用于起步）
    UAnimDistanceMatchingLibrary::StartDistanceMatchedSequence(
        this,
        DistanceMatchArgs,
        CurrentSpeed,
        0.0f // ExpectedStopDistance
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供核心的动画计算和插值功能。 |
| `AnimationLocomotionLibraryRuntime` | 本插件的运行时核心模块，包含距离匹配、转向等核心逻辑。 |
| `AnimGraphRuntime` | 用于支持动画图节点和模板化动画节点。 |
| `PhysicsCore` | 提供物理模拟基础，用于计算运动和碰撞。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统宏更新，替换 UE_LOG 为 UE_LOGF。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 优化编译，为源文件添加了内联生成宏。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 同上，继续推进内联生成宏的部署。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage... | 代码维护，统一修改了函数/变量的DLL导出属性。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复编译器报出的微不足道的不可达代码警告。 |

### 维护评价

- **创建时间**：约4年前创建。
- **近期更新频率**：最近一年有多次提交，但内容均为代码维护性更改（日志宏、编译属性、警告修复），**没有新的功能性更新**。
- **活跃程度**：核心功能自2021年添加后未见更新。近期提交表明项目仍在仓库维护列表中，但开发重心可能已转移。
- **已知限制**：插件被标记为 `IsBetaVersion: true`，且默认不启用 (`EnabledByDefault: false`)，表明它仍被视为实验性功能，其API和行为在未来版本中可能发生变化。
- **推荐使用**：适合用于**学习、研究和原型开发**。如果你想了解 Epic 官方的距离匹配动画等高级运动动画技术，这是一个绝佳的参考。但在正式的生产项目中使用需谨慎，因为它是实验性功能且长期没有功能迭代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationLocomotionLibrary)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Animation/AnimationLocomotionLibraryRuntimeTests)