# Motion Design Scene State

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、状态机图、任务定义等） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Motion Design Scene State 是一个为虚拟制片（Virtual Production）和动态设计（Motion Design）工作流设计的复杂状态管理系统。它提供了一个基于图（Graph）的可视化编辑器，允许用户创建、管理和驱动场景中各种元素（如灯光、特效、动画序列、材质参数等）的状态逻辑。

该插件的核心是**状态机（State Machine）**，它通过节点和转换来定义场景元素在不同状态之间的流转规则。与简单的蓝图状态机不同，它深度集成了任务（Task）系统、事件（Event）系统和数据绑定（Binding）机制，旨在处理实时、复杂的场景控制需求，例如在虚拟制片中根据导演指令或交互事件实时切换灯光场景、播放动画序列或调整视觉效果。

## 使用场景

- **虚拟制片现场控制**：在拍摄现场，通过状态机图预定义和快速切换不同的灯光、特效和摄像机预设。
- **动态设计与实时视觉**：创建复杂的、可交互的视觉序列，例如音乐可视化、数据驱动的动态图形。
- **交互式场景原型**：快速搭建具有复杂状态逻辑的交互式场景原型，用于测试和演示。
- **自动化场景流程**：定义场景元素的生命周期和状态转换，实现一定程度的场景自动化。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetEntryNode` | 获取状态机图的入口节点 | `USceneStateMachineGraph` |
| `GetParentStateNode` | 如果当前状态机嵌套在另一个状态节点内，则返回父状态节点 | `USceneStateMachineGraph` |
| `IsRootStateMachine` | 判断当前状态机是否为顶层（根）状态机 | `USceneStateMachineGraph` |
| `GatherTransitions` | 收集连接到当前状态节点的所有转换节点 | `USceneStateMachineNode` |
| `GetBoundGraph` | 获取与当前节点关联的绑定图（如任务图、转换条件图） | `USceneStateMachineNode` |
| `GetTask` | 获取任务节点中定义的任务数据 | `USceneStateMachineTaskNode` |
| `GetSourceNode` / `GetTargetNode` | 获取转换节点的源状态和目标状态 | `USceneStateMachineTransitionNode` |
| `GetParameters` | 获取状态机或转换节点的参数属性包 | `USceneStateMachineGraph`, `USceneStateMachineTransitionNode` |

### 使用示例（蓝图描述）

1.  **获取并遍历状态机**：首先获取一个 `USceneStateMachineGraph` 对象（通常从资产或组件中获取）。使用 `GetEntryNode` 找到起点，然后通过 `GatherTransitions` 和 `GetTargetNode` 遍历整个状态机图。
2.  **读取任务数据**：对于一个 `USceneStateMachineTaskNode`，调用 `GetTask` 获取其 `FSceneStateTask` 结构体视图，从中读取任务类型和配置参数。
3.  **检查转换条件**：对于一个 `USceneStateMachineTransitionNode`，使用 `GetParameters` 获取其条件参数，并在蓝图逻辑中评估这些参数以决定是否触发转换。
4.  **响应事件**：状态节点（`USceneStateMachineStateNode`）实现了 `ISceneStateEventHandlerProvider` 接口。在蓝图中，可以通过 `FindEventHandlerId` 查找特定事件模式的处理器ID，并连接相应的逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateMachineGraph.h"
#include "Nodes/SceneStateMachineNode.h"
#include "Nodes/SceneStateMachineStateNode.h"
#include "Nodes/SceneStateMachineTransitionNode.h"
#include "Nodes/SceneStateMachineTaskNode.h"
```

### 基本用法

以下代码演示如何获取一个状态机图的入口状态，并遍历其直接转换。

```cpp
// 假设 InStateMachineGraph 是一个有效的 USceneStateMachineGraph* 指针
if (USceneStateMachineEntryNode* EntryNode = InStateMachineGraph->GetEntryNode())
{
    // 获取入口节点连接的第一个状态节点
    if (USceneStateMachineStateNode* FirstState = EntryNode->GetStateNode())
    {
        UE_LOG(LogTemp, Log, TEXT("First State Name: %s"), *FirstState->GetNodeName().ToString());

        // 收集该状态的所有出向转换
        TArray<USceneStateMachineTransitionNode*> Transitions = FirstState->GatherTransitions();
        for (USceneStateMachineTransitionNode* Transition : Transitions)
        {
            if (USceneStateMachineNode* TargetNode = Transition->GetTargetNode())
            {
                UE_LOG(LogTemp, Log, TEXT("Transition leads to: %s"), *TargetNode->GetNodeName().ToString());
            }
        }
    }
}
```
*来源：基于 `SceneStateMachineGraph.h` 和 `SceneStateMachineNode.h` 中的接口推断。*

### 进阶用法

以下代码演示如何检查一个状态机是否为根状态机，并获取其运行模式和参数。

```cpp
// 检查状态机层级和配置
if (InStateMachineGraph->IsRootStateMachine())
{
    UE_LOG(LogTemp, Log, TEXT("This is a root state machine."));

    // 获取运行模式 (ESceneStateMachineRunMode)
    ESceneStateMachineRunMode RunMode = InStateMachineGraph->RunMode;
    UE_LOG(LogTemp, Log, TEXT("Run Mode: %s"), *UEnum::GetValueAsString(RunMode));

    // 获取并遍历参数
    const FInstancedPropertyBag& Parameters = InStateMachineGraph->Parameters;
    for (const FPropertyBagPropertyDesc& Desc : Parameters.GetPropertyDescs())
    {
        UE_LOG(LogTemp, Log, TEXT("Parameter: %s, Type: %s"), *Desc.Name.ToString(), *Desc.ValueType.ToString());
    }
}
else
{
    // 获取嵌套的父状态节点
    if (USceneStateMachineStateNode* ParentState = InStateMachineGraph->GetParentStateNode())
    {
        UE_LOG(LogTemp, Log, TEXT("Nested under state: %s"), *ParentState->GetNodeName().ToString());
    }
}
```
*来源：基于 `SceneStateMachineGraph.h` 中的 `IsRootStateMachine`, `RunMode`, `Parameters` 属性。*

## Demo 示例

一个最小的示例，展示如何在 C++ 中创建一个简单的状态机图结构并查询其信息。

**MyStateMachineHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "SceneStateMachineGraph.h"

class UMyStateMachineHelper
{
public:
    /** 打印给定状态机图的基本信息 */
    static void PrintStateMachineInfo(USceneStateMachineGraph* StateMachineGraph);
};
```

**MyStateMachineHelper.cpp**
```cpp
#include "MyStateMachineHelper.h"
#include "Nodes/SceneStateMachineEntryNode.h"
#include "Nodes/SceneStateMachineStateNode.h"

void UMyStateMachineHelper::PrintStateMachineInfo(USceneStateMachineGraph* StateMachineGraph)
{
    if (!StateMachineGraph)
    {
        UE_LOG(LogTemp, Warning, TEXT("StateMachineGraph is null."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("--- State Machine Info ---"));
    UE_LOG(LogTemp, Log, TEXT("Is Root: %s"), StateMachineGraph->IsRootStateMachine() ? TEXT("Yes") : TEXT("No"));

    if (USceneStateMachineEntryNode* Entry = StateMachineGraph->GetEntryNode())
    {
        if (USceneStateMachineStateNode* FirstState = Entry->GetStateNode())
        {
            UE_LOG(LogTemp, Log, TEXT("Entry leads to state: %s"), *FirstState->GetNodeName().ToString());
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Entry node has no connected state."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No entry node found in the graph."));
    }
    UE_LOG(LogTemp, Log, TEXT("--------------------------"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心运行时逻辑，包含状态、任务、事件等基础数据结构和执行引擎。 |
| `SceneStateBinding` | 处理状态数据与场景中实际对象（如Actor、Component）属性之间的绑定。 |
| `SceneStateBlueprint` | 提供蓝图集成，允许在蓝图中定义和扩展状态逻辑。 |
| `SceneStateEvent` | 定义和管理系统事件，用于触发状态转换。 |
| `SceneStateTasks` | 提供内置的任务类型（如播放动画、设置材质参数等）。 |
| `StructUtils` | 提供 `FInstancedPropertyBag` 等高级结构体工具，用于动态参数管理。 |

## 维护状态

### 近期更新

- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
- 2025-04-22 35e014880fab Motion Design Scene State: fixed issue where Transition Parameter enums were unusable in the graph

### 维护评价

- **创建时间**：插件非常新，创建于 2025 年 4 月。
- **最近更新**：最近的两次提交均发生在同一天（2025-04-22），内容是将插件从实验性目录迁移至正式虚拟制片目录，并修复了一个关键的编辑器图功能缺陷。这表明插件正处于**积极开发和功能稳定化阶段**。
- **活跃维护**：是，作为 Epic 官方虚拟制片工具链的新成员，预计会持续更新。
- **已知问题/限制**：作为实验性/Beta 插件，API 和功能可能在未来版本中发生变化。文档和示例目前可能不完善。
- **推荐使用**：**推荐**给正在使用或计划使用 UE5 进行复杂虚拟制片和动态设计项目的团队。它提供了强大的可视化状态管理能力，但需注意其 Beta 状态，建议在非关键路径上先行试用和验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() （暂无）