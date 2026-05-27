# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (UncookedOnly), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

此插件将 Unreal 的 **StateTree** 状态机系统集成到 **UAF (Unreal Animation Framework)** 动画框架中。它并非一个独立的状态树插件，而是为了让 StateTree 能够作为 UAF 动画图（AnimGraph）中的一个高级状态容器存在。

**解决的问题**：在 UAF 框架下，为动画资产（如 AnimNext 动画图）提供一种可视化的、数据驱动的方式来管理复杂的动画状态逻辑，允许美术设计师或技术美术师直接在 UAF 的动画资产编辑器中设计和调试状态树逻辑，而无需编写额外的 C++ 代码来驱动状态切换。

## 使用场景

- 你正在使用 **UAF (Unreal Animation Framework)** 来构建复杂的动画蓝图，并且其中的动画逻辑涉及多个状态（如待机、奔跑、攻击、受击、死亡）以及它们之间的转换条件。
- 你希望利用 **StateTree** 强大的并行执行、条件判断和任务系统能力来组织动画状态逻辑，而不是仅使用传统的状态机节点。
- 你需要将动画状态逻辑与 UAF 动画图中的其他 RigVM 逻辑（如 IK、物理模拟）无缝集成。
- 你为游戏中的复杂角色（如 Boss、拥有多种攻击模式的敌人）设计动画状态机。

## 蓝图用法

本插件主要提供编辑器集成和运行时数据结构，其核心功能体现在 UAF 动画资产编辑器中对 StateTree 的集成与编辑。插件本身未暴露大量直接在动画蓝图事件图表中调用的蓝图节点。

### 核心节点

此插件通过扩展 UAF 编辑器的数据模型和工作区导出功能，使得 StateTree 数据能够被 UAF 系统识别和处理。主要的交互发生在资产编辑器内部，而非蓝图事件图表。

### 使用示例（蓝图描述）

1.  在 UAF 动画资产（例如一个 `AnimNext` 动画图）中，通过插件提供的编辑器功能，添加一个 StateTree 节点或将其设置为资产的根逻辑。
2.  在该 StateTree 的编辑器内，设计状态树的架构（状态、转换、任务）。
3.  当 UAF 动画资产在运行时执行时，其内部的 StateTree 逻辑会根据设定的条件（如游戏逻辑变量、动画通知等）自动驱动状态转换和执行相应任务。

## C++ 用法

本插件的核心功能是编辑器和数据层的集成，通常不直接在用户编写的 Gameplay C++ 代码中调用。其提供的类主要用于扩展 UAF 和 StateTree 编辑器的功能。

### 头文件引入

若需要访问插件提供的工作区导出数据等结构体，可以包含：
```cpp
#include "AnimNextStateTreeWorkspaceExports.h"
```

### 基本用法

插件的核心是定义数据结构和编辑器逻辑。例如，`FAnimNextStateTreeStateOutlinerData` 结构体用于在 UAF 的资源浏览器中展示状态树的状态信息。

### 进阶用法

开发者可以继承 `UAnimNextStateTree_EditorData` 或 `UAnimNextStateTreeTreeEditorData` 等类，以进一步自定义 StateTree 在 UAF 资产中的编译、序列化或编辑行为。但这属于引擎扩展层面，而非常规 Gameplay 开发。

## Demo 示例

由于本插件是编辑器集成与数据驱动插件，没有简单的运行时 C++ 示例。其“示例”即为在 UAF 动画资产编辑器中创建并配置一个包含 StateTree 逻辑的动画资产。用户需要启用插件，然后在支持 UAF 的资产（如 `AnimNext` Graph）中找到并使用 StateTree 相关功能。

## 模块依赖

使用此插件，意味着你已在使用 UAF 框架。因此，其依赖关系是基于 UAF 生态的。

| 模块 | 用途 |
|---|---|
| `StateTree` | 提供核心的 StateTree 运行时和编辑器数据结构 |
| `UAFRigVM` / `AnimNextRigVM` | 提供 UAF 框架的基础 RigVM 集成 |
| `UAFAnimGraph` | 提供 UAF 动画图资产和编辑器基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的格式化日志宏，属于代码现代化改进。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 更新了 StateTree 引用结构的细节面板，使其显示结构体的更友好名称。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增了 UAFSharedAssets 插件，用于存放需要被其他插件引用的 UAF 相关资产。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将函数名 `GetComponent` 重命名为 `GetOrAddComponent`，更准确地反映其功能。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 通过隐藏 UAF StateTree 的 Schema，修复了尝试手动创建 UAF ST 时导致的崩溃。 |

### 维护评价

该插件创建于 2025 年 6 月，非常年轻。从近期的提交记录来看，它处于**活跃开发**状态，更新频繁（最近一个月内有多次提交），且内容涵盖功能修复、UI 改进和代码维护。由于它被标记为 **Experimental（实验性）**，表明其 API 和功能可能尚未完全稳定，未来版本可能发生 breaking changes。**目前可以尝试使用**，但不建议在追求长期稳定性的项目核心功能中过度依赖。它体现了 Epic Games 在动画系统（UAF 与 StateTree）集成方面的最新探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree/Tests)