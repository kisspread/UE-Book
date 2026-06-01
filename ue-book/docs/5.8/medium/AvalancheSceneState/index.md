# Motion Design Scene State Integration

> （Description from .uplugin）

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计场景状态集成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表） |
| 模块 | `AvalancheSceneState` (Runtime), `AvalancheSceneStateBlueprint` (UncookedOnly), `AvalancheSceneStateEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState) | |

## 用途

本插件是 **Motion Design** 虚拟制片系统与 **Scene State** 场景状态管理系统的集成桥梁。它解决了在 Motion Design 工作流中，需要根据复杂的场景状态变化来驱动、同步和自动化运动设计任务的问题。通过将 Scene State 的状态机逻辑引入 Motion Design，可以实现更智能、上下文感知的视觉效果控制，例如根据镜头或场景阶段自动切换和调整运动设计元素。

## 使用场景

-   **虚拟制片**：在 LED 墙上运行实时视觉效果时，需要根据当前拍摄的镜头（例如近景、中景、远景）或导演指令，自动切换不同的 Motion Design 图形、粒子效果或灯光场景。
-   **自动化演出控制**：在音乐会、发布会等现场活动中，通过预先定义的场景状态（如“开场”、“高潮”、“谢幕”）来自动触发对应的 Motion Design 动画序列。
-   **交互式展览**：在博物馆或展厅中，观众通过触摸屏或传感器选择不同的主题，触发相应的 Motion Design 内容。

## 蓝图用法

本插件主要提供 **Editor** 和 **UncookedOnly** 模块，其核心蓝图功能集成在 Motion Design 和 Scene State 的现有节点中，具体通过图表节点（Graph Node）实现。

### 核心功能模块

| 模块 | 说明 |
|---|---|
| `AvalancheSceneStateEditor` | 提供在编辑器中创建和配置基于场景状态的 Motion Design 任务所需的工具和图表节点。 |
| `AvalancheSceneStateBlueprint` | 提供在蓝图（非编辑器打包环境）中访问和操作场景状态集成任务的接口。 |

*详细 API 和节点列表，请参考各子模块文档。*

## C++ 用法

本插件主要作为胶水层，将 `SceneState` 模块的功能暴露给 `Avalanche` (Motion Design) 系统。开发者通常不需要直接在自己的 C++ 模块中使用本插件的 API，而是通过蓝图或 Motion Design 的编辑器界面来配置集成逻辑。

### 头文件引入

若需在 C++ 中引用，可引入：
```cpp
#include "AvalancheSceneStateModule.h" // 核心运行时模块
```

### 基本用法

本插件的用法主要体现在 **蓝图图表编辑** 中。在 Motion Design 的图表中，可以添加与 Scene State 状态绑定的“任务”节点，这些节点只有在对应的场景状态被激活时才会执行。

## 模块依赖

本插件依赖于其他两个 Epic 官方插件。

| 插件 | 用途 |
|---|---|
| `Avalanche` | Motion Design 虚拟制片系统的核心插件。 |
| `SceneState` | 场景状态管理插件，提供状态机和状态驱动的任务系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 `UE_LOGF` 格式。 |
| 2026-02-22 | `977f0c20` | Motion Design Scene State: added an extra 'utility task' metadata + updating from deprecated api | 新增“工具任务”元数据，并从已弃用的 API 迁移。 |
| 2026-02-16 | `22f3bb17` | Motion Design Scene State: changed schema to only check for task type metadata in the task itself | 调整架构，仅检查任务自身的类型元数据。 |
| 2026-02-15 | `5c9f991d` | Motion Design Scene State: made some schema functions editor-only, and added metadata to tasks | 将部分架构函数限定为编辑器专用，并为任务添加元数据。 |
| 2026-02-03 | `d2e06058` | Motion Design Scene State: added schema to set the rules of which tasks are allowed. | 新增架构以设定允许哪些任务执行的规则。 |

### 维护评价

**活跃维护中**。该插件于 2025 年 8 月创建，历史很短，且近几个月（截至 2026 年 4 月）持续有功能性的提交，主要集中在完善任务元数据、架构规则和 API 更新上，表明它处于**积极开发阶段**。由于 `.uplugin` 中标记为 `IsBetaVersion=true`，说明功能和 API 可能还不稳定，不建议在需要长期稳定的核心项目中作为唯一方案使用，但非常适合用于**原型开发**和**探索 Motion Design 与 Scene State 集成可能性**的场景。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState)
-   [子模块文档](./AvalancheSceneState.md), [子模块文档](./AvalancheSceneStateBlueprint.md), [子模块文档](./AvalancheSceneStateEditor.md)