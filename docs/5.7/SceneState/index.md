# Motion Design Scene State

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是一个面向虚拟制作（Virtual Production）的实验性场景状态管理系统。它旨在为 Motion Design（动态设计）场景提供一个可视化的、基于状态机的逻辑编排框架。该插件的核心目标是解决复杂场景中，多个对象、动画和交互逻辑的精确控制与同步问题。它允许设计师和开发者通过图形化界面（状态机、事件图）来定义场景的“状态”以及状态之间的“转换”，并将这些逻辑与场景中的 Actor 属性进行绑定，从而实现对场景动画和交互的精细控制。

## 使用场景

- **虚拟制作与动态设计**：在虚拟制片或 Motion Design 项目中，需要精确控制场景中多个元素（灯光、摄像机、模型、特效）的动画序列和交互逻辑。
- **复杂场景逻辑编排**：当场景需要基于时间、用户输入或特定事件来切换不同的视觉状态或播放不同的动画时。
- **可视化逻辑开发**：希望使用类似蓝图或状态机的可视化工具来编排场景逻辑，而不是完全依赖 C++ 或复杂的蓝图图表。

## 模块列表

以下是构成 SceneState 插件的 14 个模块及其核心职责概述：

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `SceneState` | 核心运行时模块，定义场景状态、状态机和执行逻辑的基础数据结构与框架。 | [SceneState.md](SceneState.md) |
| `SceneStateBinding` | 负责将场景状态机中的逻辑变量与场景中 Actor 的具体属性进行绑定。 | [SceneStateBinding.md](SceneStateBinding.md) |
| `SceneStateBlueprint` | 提供蓝图集成支持，允许在蓝图中访问和操作场景状态系统。 | [SceneStateBlueprint.md](SceneStateBlueprint.md) |
| `SceneStateBlueprintEditor` | 为场景状态蓝图资产提供编辑器内的自定义界面和功能。 | [SceneStateBlueprintEditor.md](SceneStateBlueprintEditor.md) |
| `SceneStateEditor` | 核心编辑器模块，提供场景状态资产（如状态机）的编辑器工具和界面。 | [SceneStateEditor.md](SceneStateEditor.md) |
| `SceneStateEvent` | 定义场景状态系统中使用的事件类型和事件处理机制。 | [SceneStateEvent.md](SceneStateEvent.md) |
| `SceneStateEventEditor` | 为场景状态事件资产提供编辑器支持。 | [SceneStateEventEditor.md](SceneStateEventEditor.md) |
| `SceneStateEventGraph` | 实现用于定义和编辑场景状态事件的图形化节点图。 | [SceneStateEventGraph.md](SceneStateEventGraph.md) |
| `SceneStateGameplay` | 将场景状态系统与游戏玩法框架（Gameplay）进行集成。 | [SceneStateGameplay.md](SceneStateGameplay.md) |
| `SceneStateGameplayEditor` | 为场景状态与游戏玩法的集成提供编辑器工具。 | [SceneStateGameplayEditor.md](SceneStateGameplayEditor.md) |
| `SceneStateMachineEditor` | 提供场景状态机资产的专用图形化编辑器。 | [SceneStateMachineEditor.md](SceneStateMachineEditor.md) |
| `SceneStateMachineGraph` | 实现场景状态机的图形化表示和编辑逻辑。 | [SceneStateMachineGraph.md](SceneStateMachineGraph.md) |
| `SceneStateTasks` | 定义和管理在场景状态转换或状态内可执行的任务（Tasks）。 | [SceneStateTasks.md](SceneStateTasks.md) |
| `SceneStateTransitionGraph` | 实现用于定义状态之间转换条件的图形化节点图。 | [SceneStateTransitionGraph.md](SceneStateTransitionGraph.md) |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)