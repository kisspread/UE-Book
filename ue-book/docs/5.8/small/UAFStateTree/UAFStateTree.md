# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Editor), `UAFStateTreeUncookedOnly` (UncookedOnly), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

本插件的核心用途是将 Unreal Animation Framework (UAF) 的动画图（Animation Graph）和共享变量系统与状态树（State Tree）框架进行深度集成。它解决了在复杂的动画状态机中，如何将程序化的动画图实例（如骨骼动画、IK 解算）作为状态任务（Task）进行管理，并允许状态树中的条件（Condition）和任务（Task）直接读取和操作 UAF 的共享变量（Shared Variables），从而实现数据驱动、可扩展的动画状态逻辑。

## 使用场景

- 你正在开发一个需要精细控制角色动画状态（如战斗、攀爬、特殊移动）的游戏，并且这些状态逻辑适合用状态树进行可视化管理。
- 你的动画系统大量使用了 UAF 的程序化动画图（RigVM Graphs）来生成动态动画（例如基于物理的布料、程序化 IK），并希望将这些图的播放和混合无缝集成到状态树的流程中。
- 你需要在状态树的不同状态间共享和修改动画变量（例如“速度”、“武器状态”、“姿态”），以便各个动画任务能够基于相同的全局数据做出反应。

## 蓝图用法

此插件主要提供状态树节点（Task/Condition），在状态树编辑器中使用，而非传统的蓝图函数库。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAF Graph` | 任务节点，用于在状态进入时将一个 UAF 动画图实例压入混合栈（Blend Stack）进行播放。可设置混合选项、混合轮廓、是否持续 tick 等参数。 | `FAnimNextStateTreeGraphInstanceTask` |
| `UAF Set Variable` | 任务节点，在状态进入时将指定的值写入一个 UAF 共享变量。可在此状态中叠加多个此任务以设置多个变量。 | `FUAFStateTreeSetVariableTask` |
| `(PROTOTYPE) UAF Float Variable Compare` | 条件节点（原型），用于比较一个 UAF 浮点型共享变量与一个右侧浮点值。 | `FUAFFloatCompareCondition` |
| `(PROTOTYPE) UAF Enum Variable Compare` | 条件节点（原型），用于比较一个 UAF 枚举型共享变量与一个右侧字节值。 | `FUAFEnumCompareCondition` |

### 使用示例（蓝图描述）

在状态树编辑器中：
1.  在一个状态（State）中，从任务列表添加“UAF Graph”节点。在其细节面板中，通过“Asset Data”属性选择你想要播放的 UAF 动画图资产（如 `UAnimNextStateTree` 或其他图资产），并配置混合时长、混合轮廓等。
2.  同一状态下，添加“UAF Set Variable”节点，指定要写入的变量引用（如“武器类型”）和新的值（如 `EWeaponType::Sword`）。
3.  在状态的转换条件中，添加“(PROTOTYPE) UAF Float Variable Compare”节点，设置左侧变量引用为“速度”，比较类型为“Greater”，右侧值设为 `100.0`，从而创建一个“当速度大于100时”的转换条件。

## C++ 用法

此插件主要通过其定义的结构体（`FStruct`）扩展状态树框架，供编辑器和运行时使用。

### 头文件引入

```cpp
// 核心类型
#include "UAFStateTreeTypes.h"

// 任务相关
#include "Tasks/AnimNextStateTreeGraphInstanceTask.h"
#include "Tasks/UAFStateTreeSetVariableTask.h"
#include "Tasks/AnimNextStateTreeRigVMTaskBase.h"

// 条件相关
#include "Conditions/AnimNextStateTreeRigVMConditionBase.h"
```

### 基本用法（创建自定义状态树任务）

此插件提供了基类，用于创建能调用 UAF RigVM 函数的任务。你可以继承这些基类来制作更专业的任务。

```cpp
// 自定义一个基于RigVM的任务，用于控制角色的IK
// 假设我们继承自 FAnimNextStateTreeRigVMTaskBase
USTRUCT(MinimalAPI, DisplayName = "Control Foot IK")
struct FMyFootIKStateTreeTask : public FAnimNextStateTreeRigVMTaskBase
{
	GENERATED_BODY()
	// 无需覆盖虚函数，基类已处理了函数调用、参数传递等通用逻辑。
	// 关键是在编辑器中配置 CallFunctionInfo 以指向你的UAF RigVM函数。
};
```

### 进阶用法（在 C++ 中运行状态树）

虽然运行状态树通常由动画蓝图驱动，但你可以通过 `FUAFStateTreeContext` 与运行中的状态树交互。以下为概念示例，展示上下文如何提供数据：

```cpp
// 在某个动画节点或 Trait 的更新逻辑中
// 假设你持有一个指向状态树执行上下文的指针
void FMyAnimNode::Update(FUAFAnimGraphUpdateContext& Context)
{
    // ... 更新逻辑 ...

    // 如果你需要将当前动画节点的上下文注入给状态树，需要构造相应的 Context。
    // 本插件提供了两种上下文：
    // 1. FUAFStateTreeNodeContext: 用于 AnimNode（动画节点）驱动的状态树。
    // 2. FUAFStateTreeTraitContext: 用于 Trait（特性）驱动的状态树。
    // 它们都实现了 PushAssetOntoBlendStack 和 GetVariablesOwner 等接口。

    // 状态树执行时，其内部任务（如FAnimNextStateTreeGraphInstanceTask）会通过这些接口
    // 与外部的动画图、混合栈和变量系统交互。
}
```

**关键点**：`FUAFStateTreeContext` 是一个虚基类，插件提供了两个具体实现（`Context` 和 `TraitContext`）来桥接状态树与 UAF 的核心功能（混合栈、变量系统）。

## Demo 示例

以下为一个最小示例，展示如何在 C++ 中定义一个可以被状态树使用的、基于UAF的自定义任务。

**MyCustomUAFStateTreeTask.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Tasks/AnimNextStateTreeRigVMTaskBase.h"
#include "MyCustomUAFStateTreeTask.generated.h"

USTRUCT(MinimalAPI, DisplayName = "My Custom RigVM Task")
struct FMyCustomUAFStateTreeTask : public FAnimNextStateTreeRigVMTaskBase
{
	GENERATED_BODY()

	// 基类已实现了 EnterState、Tick、ExitState 的通用逻辑，
	// 这些逻辑会根据 CallFunctionInfo 和 CallFunctionFrequency 调用指定的UAF函数。
	// 你只需要在状态树编辑器中配置它即可。

	// 如果需要，可以添加自定义属性，并重写相关函数进行特殊处理。
	UPROPERTY(EditAnywhere, Category = "Custom")
	float MyCustomParam = 1.0f;
};
```

这个任务结构体可以直接在状态树编辑器中作为节点使用。开发者需要：
1.  在状态树中选择此任务节点。
2.  在其细节面板的“Call Function”类别下，通过函数拾取器选择要调用的UAF RigVM函数。
3.  配置 `CallFunctionFrequency`（OnEnter, OnTick, OnExit）以控制函数的调用时机。
4.  `MyCustomParam` 可用于在节点上设置一个自定义参数。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StateTree` | 核心状态树框架，提供任务、条件、评估器等基类和运行时。 |
| `AnimNextRuntime` | UAF/AnimNext 动画运行时，提供动画图、共享变量、混合栈等核心功能。 |
| `UAFSharedAssets` | 提供 UAF 共享的内容资产，如混合轮廓（BlendProfile）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于引擎内部代码风格统一。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 改进状态树引用结构体的详情面板，显示结构体的友好名称。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增 UAFSharedAssets 插件，用于提供引用其他UAF插件中资产的共享内容。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 重命名为 GetOrAddComponent，使其函数名更符合实际功能。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复了尝试手动创建UAF状态树时可能发生的崩溃，通过隐藏UAF状态树的Schema来规避问题。 |

### 维护评价

- **活跃维护**：插件创建于2025年中，至今约1年。从Git历史看，在2026年4月有**频繁的更新**（一周内4次提交），包括功能改进、命名优化、Bug修复和依赖整理，表明该插件处于**积极开发和迭代**中。
- **实验性状态**：插件明确标记为 `IsExperimentalVersion: true`，且路径在 `Experimental` 下。这意味着其API和功能可能在未来版本中发生**重大变更**，不建议在正式产品中深度依赖。
- **推荐度**：适合用于**原型验证、技术预研或内部项目**，以探索UAF与状态树结合的强大潜力。对于生产环境，需密切关注其API稳定性，并做好随引擎升级进行适配的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree/Tests)