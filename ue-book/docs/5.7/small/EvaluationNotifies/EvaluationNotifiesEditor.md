# Evaluation Notifies

> A system for animation notifies which have animation evaluation time code.

| 属性 | 值 |
|---|---|
| 中文名 | 评估通知系统 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画节点蓝图资产、编辑器集成资源） |
| 模块 | `EvaluationNotifiesRuntime` (Runtime), `EvaluationNotifiesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies) | |

## 用途

该插件提供了一种 **带动画评估时间码的通知系统**。传统的动画通知（`UAnimNotify`）只在动画播放的固定时间点触发，而 **评估通知** 允许在动画评估阶段的特定时刻（例如骨骼控制节点执行前后、动画蓝图更新循环中的特定位置）执行自定义逻辑，并且通知本身携带评估时间码（Evaluation Time Code），可用于同步其他动画系统（如 Motion Warping、IK、物理交互）。

本质上，这是一个 **骨骼控制节点**，在动画蓝图的 AnimGraph 中作为节点使用，能够触发拥有时间码的动画通知。它解决了以下问题：
- 需要精确到 **动画评估帧** 而非播放时间的事件触发（例如格斗游戏中的打击判定帧、位移变换点）。
- 需要将通知触发信息传递给下游动画系统（通过时间码对齐）。
- 需要更高粒度的通知控制（如通知的重复、条件、回调）。

该插件是 **Unreal Animation Framework (UAF)** 生态的一部分，依赖 `AnimationWarping`、`RigVM` 等模块。

## 使用场景

- **格斗/动作游戏**：在动画的特定骨骼控制器生效瞬间触发打击检测，同时记录该时刻的时间码用于网络同步。
- **物理交互**：在动画评估过程中，当角色手部到达目标位置时触发抓取通知，并将时间码传递给物理约束系统。
- **Motion Warping 集成**：配合 `AnimationWarping` 插件，通过评估通知在动画特定阶段修改根骨骼位移，实现精准的碰撞箱对齐。
- **自定义动画蓝图**：创建需要细粒度事件回调的复杂动画节点，例如结合 `RigVM` 进行过程式动画。

## 蓝图用法

该插件主要作为 **动画蓝图 AnimGraph 节点** 使用，而非独立的蓝图函数库。开发者只需将 `Evaluation Notifies` 节点拖入动画蓝图的事件图（AnimGraph），并配置其属性。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluation Notifies` 动画节点 | 用于在动画评估期间触发带时间码的通知的骨骼控制节点 | `UAnimGraphNode_EvaluationNotifies` (编辑器表示) / `FAnimNode_EvaluationNotifies` (运行时) |

### 使用示例（蓝图描述）

1. 在动画蓝图的 **AnimGraph** 中，右键搜索 “Evaluation Notifies” 并放置节点。
2. 将节点连接到骨骼控制管线中（例如作为最终输出节点或中间节点）。
3. 在细节面板中配置：
   - **通知列表**：添加需要触发的通知类型（需要自行创建继承自特定通知基类的蓝图类）。
   - **时间码模式**：选择如何生成评估时间码（帧编号、绝对时间等）。
   - **触发条件**：设置通知仅在特定帧范围或条件成立时触发。
4. 编译动画蓝图并运行，节点将在动画评估过程中按配置触发通知，通知携带的时间码可通过动画节点的输出引脚或直接从通知回调获取。

> **注意**：因为该插件处于实验阶段，目前仅支持通过 C++ 或蓝图定义自定义通知类，仍需查阅后续更新的内置通知类型。

## C++ 用法

### 头文件引入

```cpp
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"
#include "AnimGraphNode_EvaluationNotifies.h" // 编辑器模块
```

### 基本用法

以下示例展示如何在自定义动画节点中嵌入 `FAnimNode_EvaluationNotifies`，并使其在动画评估期间触发通知（摘自 `AnimNode_EvaluationNotifies.h` 及测试用例模拟）。

```cpp
// 来自: Engine/Plugins/Experimental/EvaluationNotifies/Source/Runtime/Public/AnimNode_EvaluationNotifies.h（示例）
#include "AnimNode_EvaluationNotifies.h"

// 在你的自定义动画节点中
USTRUCT()
struct FMyCustomAnimNode : public FAnimNode_Base
{
    GENERATED_BODY()

    // 内嵌评估通知节点
    UPROPERTY()
    FAnimNode_EvaluationNotifies EvaluationNotifies;

    virtual void Evaluate_AnyThread(const FPoseContext& Output) override
    {
        // 先执行逻辑...
        // 然后触发评估通知
        EvaluationNotifies.Evaluate(Output); // 假设此类有 Evaluate 接口
    }

    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override
    {
        EvaluationNotifies.Update(Context);
    }
};
```

### 进阶用法

结合 `AnimationWarping` 插件，在根骨骼位移调整前后触发通知，并获取时间码：

```cpp
// 来自相关测试组合
#include "AnimationWarping.h"
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"

void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    // 在动画蓝图更新中手动物理通知触发
    if (MyEvalNotifyNode)
    {
        FEvalNotifyOutput NotifyOutput;
        MyEvalNotifyNode->TriggerNotifiesWithTimecode(NotifyOutput);
        // 从 NotifyOutput 获取时间码，用于校正后续 IK 或物理
    }
}
```

## Demo 示例

以下是一个最小化的动画节点示例，将 `FAnimNode_EvaluationNotifies` 作为子节点嵌入，以供在动画蓝图中使用。

**MyEvalNode.h**
```cpp
#pragma once
#include "Animation/AnimNodeBase.h"
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"
#include "MyEvalNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FMyEvalNode : public FAnimNode_Base
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Evaluation)
    FAnimNode_EvaluationNotifies EvalNotifyNode;

    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
};
```

**MyEvalNode.cpp**
```cpp
#include "MyEvalNode.h"

void FMyEvalNode::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    // 初始化子节点
    EvalNotifyNode.Initialize(Context);
}

void FMyEvalNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // 在评估前触发通知（示例）
    EvalNotifyNode.Evaluate(Output);
    // 后续处理骨骼姿势...
}

void FMyEvalNode::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    EvalNotifyNode.Update(Context);
}
```

随后需要为其创建对应的 `UAnimGraphNode_MyEvalNode`（继承 `UAnimGraphNode_Base`）以在动画蓝图中显示。此处省略，参考官方 AnimGraph 节点创建方式。

## 模块依赖

以下为使用此插件时，你的模块需要添加在 `Build.cs` 中的额外依赖（不包含标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `AnimationWarping` | 提供运动扭曲支持，与评估通知配合使用 |
| `RigVM` | 用于运行过程式动画逻辑 |
| `UAF` | Unreal Animation Framework 核心模块 |
| `UAFAnimGraph` | UAF 的动画蓝图编辑器集成 |

**注意**：若你的模块仅需要运行时功能，则只需依赖 `EvaluationNotifiesRuntime`；若需要在编辑器中使用动画节点，还需依赖 `EvaluationNotifiesEditor` 以及 `AnimGraph`、`AnimGraphRuntime`（后两者为常见依赖，不强制在此列出）。

## 维护状态

### 近期更新

- 2025-06-26 effdabd2 — UAF: Moved/renamed AnimNext and AnimNextAnimGraph plugins (涉及命名空间调整)
- 2025-06-25 bdc91c59 — UAF: Namespace renamed
- 2025-06-10 57979323 — AnimNext: Pass-by-ref runtime refactor
- 2025-05-26 4aabc348 — Alignment bug fixes (对齐错误修复)
- 2025-05-02 e63e0195 — Add options for flattening alignment transforms (添加展平对齐变换选项)

### 维护评价

- **创建时间**：2025-05-02（距今不到1年）
- **最近更新**：最近一个月内仍有提交（2025-06-26），属于**活跃开发**状态。
- **实验性**：插件标记为 `IsExperimentalVersion=true`，API 和行为可能不稳定，可能在未来版本发生重大变化。
- **内容**：目前仅提供基础的动画节点和编辑器支持，功能较为单一，与 UAF 生态深度绑定。
- **建议**：若项目已采用 UAF 且需要更细粒度的动画通知控制，可以尝试使用。但作为实验性功能，建议持续关注官方更新并做好兼容性准备。对于不依赖 UAF 的项目，当前阶段不推荐用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies)
- [官方文档]（暂无独立文档，可参考 UAF 及 AnimationWarping 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies/Tests)（可能位于插件内 Tests 目录）