# Animation Warping

> Framework for animation and pose warping. This plugin includes Stride, Orientation, and Slope Warping alongside the Root Motion Delta animation attribute.

| 属性 | 值 |
|---|---|
| 中文名 | 动画变形 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `AnimationWarpingRuntime` (Runtime), `AnimationWarpingEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-12-04 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping) | |

## 用途

Animation Warping 是一个高级动画系统框架，用于在运行时根据角色与环境的交互，动态地“扭曲”或调整动画姿势。它解决了传统动画系统难以完美匹配复杂地形（如上下楼梯、斜坡）和快速运动变化（如转向）的问题，通过计算动画根运动与实际运动的差异，生成更自然、准确的最终姿势。其核心是**步幅变形（Stride Warping）**、**方向变形（Orientation Warping）** 和**斜坡变形（Slope Warping）** 三大技术。

## 使用场景

- 你需要一个角色在斜坡上行走或奔跑时，身体能自然地适应坡度，而不是滑稽地悬空或陷入地面。
- 你在开发一个动作游戏，角色在快速转向时，其身体的倾斜和脚步的调整需要与移动轨迹精确匹配。
- 你希望在上下楼梯或跨越障碍时，角色的脚部能够精确地踩在正确的阶梯上，实现平滑的过渡，避免动画滑步。
- 你的游戏角色需要根据Root Motion之外的物理驱动移动（例如被推动）来调整其动画表现。

## 蓝图用法

通过蓝图节点调用变形功能，通常在动画蓝图的“事件图表”或“AnimGraph”中与动画节点结合使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Slope Warping` | 基于地面法线调整角色在斜坡上的姿态。 | `UAnimNode_SlopeWarping` |
| `Orientation Warping` | 根据移动方向动态旋转角色的下半身或上半身。 | `UAnimNode_OrientationWarping` |
| `Stride Warping` | 调整动画步幅长度以匹配实际移动速度。 | `UAnimNode_StrideWarping` |
| `Set Root Motion Delta` | 为动画节点应用一个额外的根运动增量。 | `UAnimNode_SetRootMotionDelta` |

### 使用示例（蓝图描述）

1.  在角色的**动画蓝图**中，添加一个 `Slope Warping` 动画节点，将其放置在状态机输出之后、最终姿势输出之前。
2.  为其输入的 `Delta Time`、`Character Movement` 等参数连接到相应变量（可通过蓝图函数获取）。
3.  根据需要，可以在其之前串联 `Orientation Warping` 和 `Stride Warping` 节点，形成一个变形处理链。

## C++ 用法

在 C++ 中，你需要设置动画节点的属性并计算所需的输入数据。

### 头文件引入

```cpp
#include "AnimationWarpingRuntime.h"
// 根据具体节点，可能需要
#include "AnimNodes/AnimNode_SlopeWarping.h"
#include "AnimNodes/AnimNode_OrientationWarping.h"
#include "AnimNodes/AnimNode_StrideWarping.h"
```

### 基本用法

以下示例展示了如何在 C++ 中配置并评估一个斜坡变形节点（简化逻辑）。
（来源：`Tests/AnimationWarpingRuntimeTests/SlopeWarpingTest.cpp`）

```cpp
// 在动画实例或AnimNode类的成员中
FAnimNode_SlopeWarping SlopeWarpingNode;

// 在初始化时配置参数
SlopeWarpingNode.SlopeAngleInterpSpeed = 10.0f;
SlopeWarpingNode.MaxSlopeAngle = 45.0f;

// 在评估动画时（例如，在NativeUpdateAnimation或Evaluate中）
// 1. 准备输入：计算移动速度、地面法线等
FVector GroundNormal = /* 通过射线检测获得 */;
FVector Velocity = /* 从CharacterMovement组件获得 */;

// 2. 设置节点输入
FAnimationUpdateContext UpdateContext(this);
UpdateContext.SetDeltaTime(DeltaSeconds);
SlopeWarpingNode.EvaluateSkeletalControl_AnyThread(
    UpdateContext,
    InOutPose,
    /* ... 其他输出 ... */
    GroundNormal,
    Velocity.GetSafeNormal()
);
```

### 进阶用法

组合使用多种变形技术，实现复杂的角色运动表现。需要为每个节点准备上下文数据。
（来源：组合测试用例逻辑）

```cpp
// 假设我们有三个变形节点：Slope, Orientation, Stride
FAnimNode_SlopeWarping SlopeNode;
FAnimNode_OrientationWarping OrientNode;
FAnimNode_StrideWarping StrideNode;

// 评估链：顺序很重要
// 1. 先评估斜坡变形，调整基础姿态
SlopeNode.EvaluateSkeletalControl_AnyThread(...);

// 2. 然后进行方向变形
OrientNode.OrientationDirection = /* 基于输入计算的方向 */;
OrientNode.EvaluateSkeletalControl_AnyThread(...);

// 3. 最后进行步幅变形，调整步长
StrideNode.StrideScale = /* 基于速度计算的比例 */;
StrideNode.EvaluateSkeletalControl_AnyThread(...);
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在自定义动画节点中使用 `FAnimNode_SlopeWarping`。
（文件：`MyAnimNode.h`）

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNodeBase.h"
#include "AnimNodes/AnimNode_SlopeWarping.h"
#include "MyAnimNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MySlopeAdjusted : public FAnimNode_Base
{
    GENERATED_USTRUCT_BODY()

    // 输入动画
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category=Links)
    FPoseLink Source;

    // 嵌入的斜坡变形节点
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category=Settings)
    FAnimNode_SlopeWarping SlopeWarping;

    // FAnimNode_Base interface
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    // End of FAnimNode_Base interface
};
```

（文件：`MyAnimNode.cpp`）

```cpp
#include "MyAnimNode.h"

void FAnimNode_MySlopeAdjusted::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    FAnimNode_Base::Initialize_AnyThread(Context);
    Source.Initialize(Context);
    // 斜坡节点在这里不需要单独初始化，它将在Evaluate时通过我们传递的上下文工作
}

void FAnimNode_MySlopeAdjusted::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    // 首先更新输入动画
    Source.Update(Context);

    // 收集斜坡变形所需数据（示例）
    // 注意：实际实现中，这些数据可能需要从角色组件获取，这里仅为示意
    FVector GroundNormal = FVector::UpVector; // 替换为实际检测
    FVector Velocity = Context.AnimInstanceProxy->GetSkelMeshComponent()->GetOwner()->GetVelocity();

    // 准备并更新内部的斜坡变形节点
    SlopeWarping.GroundNormal = GroundNormal;
    SlopeWarping.Velocity = Velocity;
    SlopeWarping.SlopeWarpingAlpha = 1.0f; // 启用
    SlopeWarping.Update_AnyThread(Context);
}

void FAnimNode_MySlopeAdjusted::Evaluate_AnyThread(FPoseContext& Output)
{
    // 先评估源动画
    Source.Evaluate(Output);

    // 将结果传递给斜坡变形节点进行二次评估
    SlopeWarping.Evaluate_AnyThread(Output);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationWarpingLibrary` | 提供变形功能的核心数学库 |
| `PoseSearch` | 用于高级动画匹配，为变形提供上下文 |
| `PhysicsCore` | 用于获取物理世界信息（如地面法线检测） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `42c8bcfa` | Fix tooltip on ABP steering node | 修复动画蓝图转向节点的工具提示显示问题 |
| 2026-04-24 | `afab60f0` | UE-363190 - Replace crash-assert NaN guards with UE_LOGF + safe-default in StrideWarping and Orienta | 将步幅/方向变形中的NaN崩溃断言改为日志警告和安全默认值 |
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非统一构建错误，在头文件中前置声明UAnimationAsset |
| 2026-04-23 | `23ccd2bd` | Add Anim Node Functions to support applying a delta to the offset root bone's internal simulated tra | 添加动画节点函数，支持对偏移根骨骼的模拟变换应用增量 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移到更安全的UE_LOGF宏 |

### 维护评价

该插件于 **2021年底** 从实验阶段迁移出来，目前处于**活跃维护**状态。最近在 **2026年4月** 仍有数次实质性更新，包括修复崩溃问题、改善代码健壮性（NaN处理）和添加新功能（模拟变换增量）。这表明 Epic Games 内部仍在积极使用并维护此插件。虽然它默认未启用，但作为官方提供的、相对成熟的动画解决方案，**推荐在需要高级动画交互的项目中进行评估和使用**。无已知的重大长期未修复问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping)
- [官方文档](https://epicgames.com) (插件作者链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping/Tests)