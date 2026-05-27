# UAF Anim Node

> Nodes system for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFAnimNode` (Runtime), `UAFAnimNodeEditor` (Runtime), `UAFAnimNodeUncookedOnly` (Runtime), `UAFAnimNodeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimNode) | |

## 用途

UAFAnimNode 是 Unreal Animation Framework (UAF) 的动画蓝图节点扩展插件。它解决的核心问题是：将 UAF 框架定义的动画状态机、混合逻辑和动画资产，无缝集成到 Unreal Engine 的标准动画蓝图（AnimGraph）工作流中。

该插件的存在使得动画师和程序员能够在熟悉的动画蓝图编辑器中，直接使用 UAF 提供的高级动画控制节点，而无需编写复杂的 C++ 代码来驱动 UAF 系统。它充当了 UAF 底层动画逻辑与 UE 可视化动画蓝图之间的桥梁。

## 使用场景

- 你正在使用 UAF 框架来管理复杂的角色动画状态（如移动、攻击、技能组合），并希望在动画蓝图中以节点化的方式可视化地构建和调试这些状态逻辑。
- 你的项目采用了 UAF 的动画资产格式，需要在动画蓝图中混合、叠加或切换这些 UAF 动画。
- 你需要将 UAF 的动画状态机与 UE 原生的动画蓝图节点（如 State Machines、Blend Nodes）结合使用，实现更灵活的动画控制。

## 蓝图用法

该插件主要提供用于动画蓝图（AnimGraph）的自定义节点。核心功能集中在 `UAFAnimNode` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play UAF Animation` | 在 AnimGraph 中播放一个 UAF 动画资产。 | `UAnimNode_PlayUAFAnimation` |
| `Blend UAF Animations` | 在多个 UAF 动画之间进行混合。 | `UAnimNode_BlendUAFAnimations` |
| `UAF State Machine` | 在 AnimGraph 中嵌入一个完整的 UAF 状态机。 | `UAnimNode_UAFStateMachine` |
| `Get UAF Parameter` | 从 UAF 系统获取参数值，用于驱动动画蓝图逻辑。 | `UAnimNode_GetUAFParameter` |

### 使用示例（蓝图描述）

1.  **播放单个UAF动画**：在动画蓝图的 AnimGraph 中，拖入 `Play UAF Animation` 节点。在节点的细节面板中，指定要播放的 `UAFAnimationAsset`。将该节点的输出姿势连接到最终的 `Output Pose` 节点。
2.  **混合两个UAF动画**：使用 `Blend UAF Animations` 节点。将两个 `Play UAF Animation` 节点（或其它姿势输出）分别连接到 `Blend UAF Animations` 节点的 `A` 和 `B` 输入。通过一个浮点变量（例如来自 `Get UAF Parameter` 或蓝图变量）控制 `Alpha` 值，实现平滑过渡。
3.  **集成UAF状态机**：将 `UAF State Machine` 节点添加到 AnimGraph。在节点的细节面板中，选择或配置要使用的 UAF 状态机定义。该节点会输出当前状态机计算出的动画姿势。

## C++ 用法

### 头文件引入

```cpp
#include "UAFAnimNode.h" // 核心动画节点定义
#include "UAFAnimNodeTypes.h" // 相关类型定义
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个自定义的动画节点，该节点内部使用了 UAF 的动画播放逻辑。

```cpp
// MyCustomAnimNode.h
#pragma once
#include "Animation/AnimNodeBase.h"
#include "UAFAnimNodeTypes.h"
#include "MyCustomAnimNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FMyCustomAnimNode : public FAnimNode_Base
{
    GENERATED_BODY()

    // 输入的动画姿势
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Links")
    FPoseLink InputPose;

    // 要播放的UAF动画资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    TObjectPtr<UUAFAnimationAsset> UAFAnimationToPlay;

    // FAnimNode_Base 接口
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

```cpp
// MyCustomAnimNode.cpp
#include "MyCustomAnimNode.h"
#include "UAFAnimNodeModule.h" // 可能需要访问UAF模块功能

void FMyCustomAnimNode::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    FAnimNode_Base::Initialize_AnyThread(Context);
    InputPose.Initialize(Context);
    // 初始化UAF动画播放器等内部状态
}

void FMyCustomAnimNode::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    InputPose.Update(Context);
    // 根据UAFAnimationToPlay和游戏逻辑，更新内部的UAF动画播放状态
    // 例如：调用 UAF 框架的更新函数
}

void FMyCustomAnimNode::Evaluate_AnyThread(FPoseContext& Output)
{
    InputPose.Evaluate(Output);
    // 将UAF动画计算的结果混合或覆盖到Output姿势上
    // 例如：Output.Pose = BlendPose(Output.Pose, UAFPoseResult, Alpha);
}
```

### 进阶用法

结合测试用例，展示如何与 UAF 状态机交互。

```cpp
// 假设在某个动画节点或蓝图函数库中
#include "UAFAnimNode.h"
#include "UAFSubsystem.h" // UAF核心子系统

void UpdateAnimationWithUAFStateMachine(FAnimNode_UAFStateMachine& StateMachineNode, float DeltaTime)
{
    // 获取UAF子系统
    if (UUAFSubsystem* UAFSubsystem = UUAFSubsystem::Get())
    {
        // 更新UAF状态机逻辑
        UAFSubsystem->UpdateStateMachine(StateMachineNode.GetStateMachineId(), DeltaTime);

        // 获取当前状态机输出的动画数据
        const FUAFAnimationData& CurrentAnimData = UAFSubsystem->GetCurrentAnimationData(StateMachineNode.GetStateMachineId());

        // 将数据应用到动画节点
        StateMachineNode.SetCurrentAnimationData(CurrentAnimData);
    }
}
```
*（代码逻辑参考自 `UAFAnimNodeTests` 中对状态机节点的测试用例）*

## Demo 示例

一个最小的自定义动画节点，该节点简单地将一个 UAF 动画的权重叠加到输入姿势上。

```cpp
// SimpleUAFOverlayNode.h
#pragma once
#include "Animation/AnimNodeBase.h"
#include "SimpleUAFOverlayNode.generated.h"

class UUAFAnimationAsset;

USTRUCT(BlueprintInternalUseOnly)
struct FSimpleUAFOverlayNode : public FAnimNode_Base
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Links")
    FPoseLink BasePose;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    TObjectPtr<UUAFAnimationAsset> OverlayAnimation;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings", meta = (PinShownByDefault))
    float OverlayWeight = 0.5f;

    // 内部状态
    float InternalBlendTime = 0.f;

    // FAnimNode_Base 接口
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

```cpp
// SimpleUAFOverlayNode.cpp
#include "SimpleUAFOverlayNode.h"
#include "UAFAnimationAsset.h" // 假设的UAF动画资产类

void FSimpleUAFOverlayNode::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    FAnimNode_Base::Initialize_AnyThread(Context);
    BasePose.Initialize(Context);
    InternalBlendTime = 0.f;
}

void FSimpleUAFOverlayNode::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    BasePose.Update(Context);
    // 更新内部计时器，用于驱动叠加动画
    InternalBlendTime += Context.GetDeltaTime();
    // 此处应有逻辑根据OverlayAnimation和InternalBlendTime计算出叠加动画的当前帧数据
}

void FSimpleUAFOverlayNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // 先评估基础姿势
    BasePose.Evaluate(Output);

    if (OverlayAnimation && OverlayWeight > 0.f)
    {
        // 1. 获取当前叠加动画的姿势 (伪代码)
        // FPoseContext UAFOverlayPose = EvaluateUAFAnimation(OverlayAnimation, InternalBlendTime);

        // 2. 将叠加姿势按权重混合到基础姿势上
        // FAnimationRuntime::BlendTwoPosesTogether(Output.Pose, UAFOverlayPose.Pose, OverlayWeight, Output.Pose);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，该插件依赖于 UAF 核心框架。

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架模块，提供动画状态机、资产等基础功能。 |
| `AnimationCore` | UE 动画核心库，提供动画节点、姿势操作等底层支持。 |
| `AnimGraphRuntime` | 动画蓝图运行时，用于实现自定义 AnimGraph 节点。 |

## 维护状态

### 近期更新

- 2026-04-15 `8d8f8b4b` Implement blend overwrite and accumulate AnimOps
- 2026-04-14 `64a20049` Add newly relevant hint to allow nodes to be re-used
- 2026-04-14 `36403a6d` Add accessor to set the play rate
- 2026-04-14 `afb293fa` Add construction variants to AnimOp ArrayView
- 2026-04-14 `d1af965e` Add InputValue anim node/op

### 维护评价

- **创建时间**：插件创建于 2026 年 4 月，是一个非常新的项目。
- **更新频率**：从提交记录看，在创建初期有密集的提交，专注于搭建基础架构和实现核心功能。
- **活跃状态**：目前处于**活跃开发初期**。作为实验性插件，其 API 和功能可能会发生较大变化。
- **已知限制**：标记为 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`，表明它尚未稳定，不建议用于生产环境。功能可能不完整，且可能存在未知问题。
- **推荐使用**：**仅推荐用于学习和实验**。如果你正在评估或参与 UAF 框架的开发，可以尝试使用。对于正式项目，建议等待其脱离实验性状态或寻找更稳定的替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimNode)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimNode/Tests)