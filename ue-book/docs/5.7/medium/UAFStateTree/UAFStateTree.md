# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Editor), `UAFStateTreeUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

UAF State Tree 插件是 Unreal Animation Framework (UAF) 与 StateTree 系统之间的桥梁。它允许开发者将 **StateTree** 状态机逻辑嵌入到 **AnimNext** 动画图中，从而实现复杂的、可维护的角色动画行为控制。

核心能力包括：

- 在 AnimNext 的动画评估链中直接运行 StateTree。
- 提供专用的 StateTree Schema（`UStateTreeAnimNextSchema`），限制可用的节点类型（仅允许任务、条件，禁用评估器和工具考量）。
- 通过 `FAnimNextStateTreeTrait`（Trait）将 StateTree 实例附加到动画图中，实现状态切换、图实例推送、Blend 等操作。
- 支持基于 RigVM 的自定义条件和任务，允许在 StateTree 节点中调用 UAF 函数（如读写变量、播放动画图）。

该插件解决了在传统动画蓝图或混合空间难以表达复杂逻辑的问题，例如基于环境、AI 决策、多重状态叠加上下文敏感的变化。

## 使用场景

- 你正在使用 **AnimNext** 开发程序化动画系统，需要一种声明式状态机来管理动画状态（如 idle、walk、run、jump、attack）。
- 你希望利用 **StateTree** 强大的条件/任务系统，而不是用繁琐的蓝图逻辑或 C++ 状态机。
- 你需要在一个动画图中支持多个并发的状态机（例如基础移动 + 交互），并且状态切换需要平滑 blend。
- 你的动画逻辑需要与游戏逻辑（如 AI 决策、输入）紧密结合，StateTree 的数据绑定和外部环境引用能力恰好满足需求。

## 蓝图用法

### 核心节点

插件主要暴露一个蓝图标点类型 `UAnimNextStateTree`，它继承自 `UAnimNextAnimationGraph`，并包含一个 `UStateTree` 子对象。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建/打开 AnimNext StateTree 资产` | 在内容浏览器中创建 UAF State Tree 资产（类似于创建动画图资产） | 编辑器工厂 |
| `获取 StateTree 引用` | 通过 `AnimNextStateTree->StateTree` 访问内部的 `UStateTree` 对象 | `UAnimNextStateTree` |
| `StateTree 上下文` | 在 Trait 内部，通过 `FAnimNextStateTreeTraitContext` 暴露的方法与动画图通信 | `FAnimNextStateTreeTraitContext` |

> 说明：当前版本未导出标记为 `BlueprintCallable` 的函数。大部分操作在 C++ 层完成。蓝图用户主要通过 StateTree 资产编辑器配置任务和条件。

### 使用示例（蓝图描述）

1. **创建资产**：在内容浏览器中右键选择 “Animation → UAF State Tree”。
2. **配置状态机**：双击打开资产，在 StateTree 编辑器中添加状态，每个状态可以添加任务（如“播放动画图”）和条件（如“输入方向 > 阈值”）。
3. **关联动画图**：在任务属性 `Asset` 中选择一个 `UAnimNextAnimationGraph` 作为要播放的动画图。
4. **在 AnimNext 中使用**：在 Animate 图编辑器中添加 “State Tree” Trait，并填入刚创建的 UAF State Tree 资产。该 Trait 会自动运行 StateTree 并根据结果驱动动画。

## C++ 用法

### 头文件引入

```cpp
#include "AnimStateTreeTrait.h"
#include "AnimNextStateTreeSchema.h"
#include "Tasks/AnimNextStateTreeGraphInstanceTask.h"
```

### 基本用法

创建一个自己的 Trait 并嵌入 StateTree：

```cpp
// 引入核心头文件
#include "AnimStateTreeTrait.h"
#include "TraitInterfaces/IUpdate.h"
#include "StateTreeExecutionContext.h"
#include "StateTreeReference.h"

// 在 Trait 类中使用 FStateTreeTrait
class FCustomTrait : public UE::UAF::FAdditiveTrait, public UE::UAF::IUpdate
{
    using FSharedData = FAnimNextStateTreeTraitSharedData;
    // 实例数据包含 StateTree 实例
    struct FInstanceData : FTrait::FInstanceData
    {
        TObjectPtr<const UStateTree> StateTree;
        FStateTreeInstanceData InstanceData;
        // ...
    };

    virtual void PreUpdate(...) override
    {
        // 每帧更新 StateTree
        FStateTreeExecutionContext ExecContext(*InstanceData.StateTree, InstanceData.InstanceData, ...);
        ExecContext.Tick(DeltaTime);
    }
};
```

来源：`Engine/Plugins/Experimental/UAF/UAFStateTree/Source/UAFStateTree/Internal/AnimStateTreeTrait.h`

### 进阶用法

任务中推送动画图到 Blend Stack：

```cpp
// 在任务实例的 EnterState 中
if (FAnimNextStateTreeTraitContext* Context = ...)
{
    FAlphaBlendArgs BlendArgs;
    BlendArgs.BlendTime = 0.2f;
    BlendArgs.BlendOption = EAlphaBlendOption::Cubic;
    FAnimNextFactoryParams FactoryParams;
    Context->PushAssetOntoBlendStack(MyAnimationGraph, BlendArgs, FactoryParams);
}
```

来源：`Engine/Plugins/Experimental/UAF/UAFStateTree/Source/UAFStateTree/Private/AnimNextStateTreeContext.h`

自定义 RigVM 条件：

```cpp
USTRUCT()
struct FMyCondition : public FAnimNextStateTreeRigVMConditionBase
{
    GENERATED_BODY()
    // 重写 TestCondition 逻辑
    virtual bool TestCondition(FStateTreeExecutionContext& Context) const override
    {
        // 获取参数并调用 RigVM
        FAnimNextStateTreeRigVMConditionInstanceData& InstanceData = Context.GetInstanceData(*this);
        return ...;
    }
};
```

来源：`Engine/Plugins/Experimental/UAF/UAFStateTree/Source/UAFStateTree/Internal/Conditions/AnimNextStateTreeRigVMConditionBase.h`

## Demo 示例

以下是一个简单的 C++ 模块，演示如何使用 UAF State Tree 在 AnimNext Trait 中运行 StateTree：

```cpp
// MyTrait.h
#pragma once

#include "AnimStateTreeTrait.h"
#include "TraitInterfaces/IUpdate.h"
#include "StateTree.h"

USTRUCT(meta = (DisplayName = "Demo State Tree"))
struct FMyStateTreeTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, Category = "Default")
    TObjectPtr<UStateTree> StateTreeAsset;
};

namespace UE::UAF
{
struct FMyStateTreeTrait : FAdditiveTrait, IUpdate
{
    DECLARE_ANIM_TRAIT(FMyStateTreeTrait, FAdditiveTrait)
    using FSharedData = FMyStateTreeTraitSharedData;

    struct FInstanceData : FTrait::FInstanceData
    {
        FStateTreeInstanceData InstanceData;
        TObjectPtr<const UStateTree> StateTree;
    };

    virtual void PreUpdate(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const override
    {
        const auto& SharedData = Binding.GetSharedData<FSharedData>();
        auto& InstanceData = Binding.GetInstanceData<FInstanceData>();

        if (!InstanceData.StateTree)
        {
            InstanceData.StateTree = SharedData.StateTreeAsset;
            FStateTreeExecutionContext::FExternalGlobalParameters Params;
            InstanceData.InstanceData.Reset();
            return;
        }

        FStateTreeExecutionContext ExecContext(*InstanceData.StateTree, InstanceData.InstanceData, nullptr, nullptr);
        ExecContext.Tick(TraitState.GetDeltaTime());
    }
};
}
```

在模块的 Startup 调用 `DECLARE_ANIM_TRAIT` 注册即可在动画图中使用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StateTree` | 状态机核心运行时和编辑 |
| `UAF` (UAFAnimGraph, UAFBase) | 动画框架 Trait、ExecutionContext、BlendStack |
| `RigVM` | 编程式条件和任务的后端 |
| `AnimNext` (UAFAnimGraph?) | 动画图资产和执行 |
| `PropertyBag` | 动态参数存储 |

> 注意：由于插件仍处于实验阶段，所列依赖可能随版本变更。实际使用请参考 Build.cs 文件。

**排除常见依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-09-23 `9a934fb4` — Fix UAF leaking callbacks causing UAF state tree selection to be cleared.
- 2025-08-28 `9273c535` — Add missing IUpdate propagation to StateTree
- 2025-08-15 `031b08ff` — UAF StateTree autocomplete on graph timeline complete
- 2025-08-01 `7aace74a` — Downgrade check to ensure on statetree failure
- 2025-07-30 `3ac8187c` — UAF Read / Write Variable in Function Fixes

### 维护评价

插件创建于 2025 年 7 月底，至今不足半年，属于非常新的实验性功能。从近期提交看，开发活跃，持续修复问题并添加功能（如自动完成、IUpdate 传播）。提交消息均为功能性更新，没有单纯的编译修复，表明团队正在积极扩展能力。**推荐用于学习和探索**，但在生产环境中使用需谨慎（实验性标记可能意味着 API 不稳定）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree/Source)（内部包含部分自动化测试，但未单独列出 Tests 目录）
- [UFUNCTION 在线文档](https://docs.unrealengine.com/5.7/en-US/state-tree-in-unreal-engine/)（若官方文档更新，可参考 StateTree 通用文档）