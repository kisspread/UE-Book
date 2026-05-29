# UAF Chooser

> Chooser integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFChooser` (Runtime), `UAFChooserEditor` (Runtime), `UAFChooserUncookedOnly` (Runtime), `UAFChooserTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser) | |

## 用途

该插件是 UAF (Unreal Animation Framework) 与 Chooser 系统的集成模块。它的核心功能是在 UAF 的动画图（AnimGraph）和特征（Trait）系统中，利用 Chooser 表（`ChooserTable`）来动态选择并播放动画资产。它解决了在 UAF 框架下，如何基于上下文、输入变量或条件，从一组动画选项中智能选择最合适动画的问题。这为创建复杂的、数据驱动的动画状态机提供了底层支持。

## 使用场景

- 你正在使用 UAF 构建角色动画系统，需要根据角色状态（如移动速度、武器类型）或输入，动态选择播放不同的动画片段或子图。
- 你需要一个可视化的、数据驱动的工具（如 Chooser 表）来定义复杂的动画选择逻辑，而不是在代码中硬编码 `if-else` 或 `switch`。
- 你的项目正在使用或计划使用 AnimNext 的特性（Traits）来组织动画逻辑，希望在 Trait 中集成基于条件的动画选择能力。

## 蓝图用法

主要通过 RigVM 图中的节点进行集成和使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Chooser` | 评估一个 Chooser 表，并根据连接情况输出一个对象（`UObject*`）或对象数组。兼容 ControlRig 和 AnimNext 图。 | `FRigVMDispatch_EvaluateChooser` |
| `OwningObject` | 获取拥有当前图的对象。通常用作 Chooser 评估时的上下文对象。 | `FRigUnit_OwningObject` |

### 使用示例（蓝图描述）

1.  **在 AnimNext 特性图中使用**：
    *   创建一个 AnimNext 特性图。
    *   拖入 `Evaluate Chooser` 节点。
    *   将 `OwningObject` 节点的输出（或代表当前角色/动画实例的对象）连接到 `Evaluate Chooser` 节点的 `ContextObject` 引脚。
    *   将配置好的 `UAFAnimChooserTable` 资产拖放到 `Chooser` 引脚上。
    *   `Result` 引脚输出的对象将根据 Chooser 表的选择结果，可以用于驱动后续的动画播放逻辑。

2.  **在 ControlRig 图中使用**：
    *   流程与 AnimNext 图类似，同样使用 `Evaluate Chooser` 节点。该节点会自动适配上下文。

## C++ 用法

### 头文件引入

```cpp
#include "UAFAnimChooser.h"
#include "ChooserPlayerTraitData.h"
#include "Internal/AnimNode/UAFChooserPlayerNode.h"
#include "Internal/ChooserParameters.h"
```

### 基本用法

创建一个基于 Chooser 表的 UAF 动画节点实例。

```cpp
// 假设你已有一个 UAFAnimChooserTable 资产指针 ChooserTable
// 在 UAF AnimGraph 的更新上下文中创建节点
FUAFAnimNodePtr ChooserNode = FUAFChooserPlayerNode::CreateInstance(
    GraphContext, // FUAFAnimGraphUpdateContext&
    ChooserTable, // const UUAFAnimChooserTable*
    EChooserEvaluationFrequency::OnInitialUpdate, // 初始评估频率
    nullptr // 无过渡数据
);

// 将创建的节点添加到你的动画图中进行求值
```

### 进阶用法

在自定义的 AnimNext Trait 中集成 Chooser 播放逻辑。

```cpp
// 定义一个使用 Chooser 的自定义 Trait
struct FMyCustomTrait : public FAdditiveTrait, public IUpdate
{
    DECLARE_ANIM_TRAIT(FMyCustomTrait, FAdditiveTrait)

    // 定义共享数据，包含 Chooser 参数
    struct FSharedData : public FChooserPlayerData
    {
        // 可以在此添加其他共享参数
    };

    // Trait 实例数据
    struct FInstanceData : public FTrait::FInstanceData
    {
        // 存储当前选择状态，例如来自 FChooserPlayerTrait::FInstanceData
        TObjectPtr<UObject> CurrentSelection = nullptr;
    };

    // Trait 接口实现...
};
```

## Demo 示例

**场景**：创建一个简单的 Trait，使用 Chooser 表来决定播放哪个子动画图。

**MyChooserDrivenTrait.h**
```cpp
#pragma once

#include "Animation/AnimNextTrait.h"
#include "ChooserPlayerTraitData.h"

namespace UE::UAF
{

struct FMyChooserDrivenTrait : public FAdditiveTrait, public IUpdate
{
    DECLARE_ANIM_TRAIT(FMyChooserDrivenTrait, FAdditiveTrait)

    // 使用插件提供的共享数据结构作为基础
    using FSharedData = FChooserPlayerData;

    struct FInstanceData : public FTrait::FInstanceData
    {
        // 插件内部用于跟踪选择状态的数据
        TObjectPtr<UObject> CurrentSelection = nullptr;
    };

    // 当特征变为相关时评估 Chooser
    virtual void OnBecomeRelevant(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const override;
};

} // namespace UE::UAF
```

**MyChooserDrivenTrait.cpp**
```cpp
#include "MyChooserDrivenTrait.h"
#include "ChooserPlayerTrait.h" // 复用插件内部的评估逻辑

namespace UE::UAF
{

void FMyChooserDrivenTrait::OnBecomeRelevant(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const
{
    const FSharedData* SharedData = Binding.GetSharedData<FSharedData>();
    FInstanceData* InstanceData = Binding.GetInstanceData<FInstanceData>();

    if (SharedData && InstanceData)
    {
        // 复用插件 FChooserPlayerTrait 中封装的评估逻辑
        FChooserPlayerTrait::EvaluateChooser(Context, Binding, TraitState);
    }
    // 实际实现中需要更完整地调用基类或复用逻辑
}

} // namespace UE::UAF
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心的 Unreal Animation Framework 模块。 |
| `Chooser` | Chooser 系统的核心模块，提供 `ChooserTable`、`FObjectChooserBase` 等基础类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 添加修改器动画节点基类，用于具有单个子节点的动画节点 |
| 2026-03-19 | `910301d3` | UAF Anim Node rewind debugger track | 为UAF动画节点添加倒带调试器跟踪功能 |
| 2026-03-11 | `bda4ef8e` | Add debug update counter to UAF anim node to enforce invariants | 为UAF动画节点添加调试更新计数器，以强制执行不变量 |
| 2026-03-11 | `7da85466` | Implement AnimOp system for new UAF runtime | 为新UAF运行时实现AnimOp系统 |
| 2026-03-10 | `5a95823d` | AnimNodes Blend stack helper class to avoid too much code duplication (it can be used as either a b... | AnimNodes混合栈助手类，用于避免过多的代码重复（它既可作为 b...） |

### 维护评价

**积极维护中**。该插件创建于2025年中，是一个非常新的实验性模块。从近期Git提交记录来看（最近一次更新在2026年4月），它正处于**密集活跃开发阶段**。近期更新主要围绕UAF动画节点系统的完善、调试工具支持以及新运行时特性的实现，表明这是一个正在快速发展的核心功能模块。作为实验性插件，其API和功能可能会有变动，但鉴于其由Epic Games开发并持续投入，是探索UAF高级动画功能（如基于条件的动画选择）的**推荐途径**。建议关注其更新日志和API变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser)