# Motion Design Scene State

> （空）

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图/图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Motion Design Scene State 是一个用于在虚幻引擎中定义、管理和驱动复杂场景状态逻辑的实验性框架。它解决的核心问题是：如何让设计师和开发者能够通过可视化图表（状态机、事件图）而非纯C++代码，来编排场景中物体的状态、行为以及它们之间的数据流。该插件提供了一个状态机系统、事件驱动机制和数据绑定功能，旨在创建动态、可交互的场景体验，尤其适用于运动设计（Motion Design）领域，其中场景元素需要根据时间、用户输入或逻辑事件精确地变换状态。

## 使用场景

-   你需要为虚拟制作或互动展览创建一套场景状态系统，其中多个物体（如灯光、模型、UI）需要根据预设逻辑（如时间线、按钮点击）协同改变状态。
-   你希望使用蓝图和可视化图表来定义复杂的状态转换和事件响应，而无需编写大量底层C++代码。
-   你的项目需要清晰的数据流，将场景中不同资产的属性绑定到一起，由状态逻辑驱动。

## 模块概览

此插件由14个模块构成，可分为核心运行时、事件系统、状态机系统和编辑器扩展几个部分。

| 模块 | 一句话说明 | 文档链接 |
|---|---|---|
| `SceneState` | 核心运行时模块，提供场景状态、上下文和组件管理的基础框架。 | [SceneState.md](SceneState.md) |
| `SceneStateBinding` | 实现数据绑定功能，用于连接不同对象之间的属性。 | [SceneStateBinding.md](SceneStateBinding.md) |
| `SceneStateEvent` | 定义和管理场景状态事件系统。 | [SceneStateEvent.md](SceneStateEvent.md) |
| `SceneStateEventGraph` | 提供事件图表资产和编辑器支持，用于可视化编辑事件逻辑。 | [SceneStateEventGraph.md](SceneStateEventGraph.md) |
| `SceneStateTasks` | 包含一系列预定义的、可在状态机中执行的任务节点。 | [SceneStateTasks.md](SceneStateTasks.md) |
| `SceneStateMachineGraph` | 提供状态机图表资产和编辑器支持，用于可视化定义状态和转换。 | [SceneStateMachineGraph.md](SceneStateMachineGraph.md) |
| `SceneStateTransitionGraph` | 专注于状态转换逻辑的图表实现。 | [SceneStateTransitionGraph.md](SceneStateTransitionGraph.md) |
| `SceneStateBlueprint` | 将场景状态功能与蓝图系统集成。 | [SceneStateBlueprint.md](SceneStateBlueprint.md) |
| `SceneStateGameplay` | 将场景状态框架与游戏玩法系统（如Gameplay Ability System）连接。 | [SceneStateGameplay.md](SceneStateGameplay.md) |
| `SceneStateEditor` | 提供核心的编辑器工具和自定义资产编辑器。 | [SceneStateEditor.md](SceneStateEditor.md) |
| `SceneStateBlueprintEditor` | 提供蓝图相关的编辑器扩展。 | [SceneStateBlueprintEditor.md](SceneStateBlueprintEditor.md) |
| `SceneStateEventEditor` | 提供事件系统的编辑器支持。 | [SceneStateEventEditor.md](SceneStateEventEditor.md) |
| `SceneStateGameplayEditor` | 提供Gameplay集成部分的编辑器支持。 | [SceneStateGameplayEditor.md](SceneStateGameplayEditor.md) |
| `SceneStateMachineEditor` | 提供状态机图表的高级编辑器支持。 | [SceneStateMachineEditor.md](SceneStateMachineEditor.md) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口关联逻辑，通过客户端通知简化了代码。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复了数据绑定在检查事件负载结构体是否为空时的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF。 |

### 维护评价

该插件创建于2025年8月，至今约1年，是一个非常新的插件。从Git历史看，最近一个月（2026年5月）仍有活跃的功能性提交和重构，表明其正在**积极开发**中。`IsBetaVersion=true` 表明它仍处于测试阶段，可能存在不稳定或API变动。由于其包含内容众多（424个文件）且为实验性功能，建议在需要此类高级状态管理系统的项目中小范围试用，并做好应对未来API变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无
- 测试用例：路径待定，可能位于 `Engine/Tests/` 目录下。