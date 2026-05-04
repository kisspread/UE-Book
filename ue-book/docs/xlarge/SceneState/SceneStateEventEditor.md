# Motion Design Scene State

> （Description 字段为空，基于源码分析）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 是 Unreal Motion Design（虚拟制片中的动态图形工具集）的状态机系统。它为场景提供了一套完整的**可视化状态机编辑器**，允许美术和技术美术通过图形化界面定义场景中对象的行为状态、状态之间的转换条件、以及每个状态下执行的任务序列。

核心解决的问题：在广播图形和 Motion Design 工作流中，场景中的元素（如 Lower Third、Logo 动画、全屏图表等）需要根据节目流程在不同状态之间切换（如"待机"→"入场"→"显示"→"退场"）。传统做法需要手写大量蓝图逻辑，而 Scene State 提供了可视化的状态机编辑方式，让非程序员也能定义复杂的状态逻辑。

该插件包含 14 个模块，按功能可分为以下层次：

| 层次 | 模块 | 职责 |
|---|---|---|
| **核心运行时** | `SceneState`, `SceneStateBinding`, `SceneStateEvent`, `SceneStateTasks`, `SceneStateGameplay` | 状态机运行时逻辑、数据绑定、事件系统、任务执行、游戏玩法集成 |
| **蓝图集成** | `SceneStateBlueprint` | 蓝图类型支持，允许通过蓝图扩展状态行为 |
| **编辑器工具** | `SceneStateEditor`, `SceneStateBlueprintEditor`, `SceneStateEventEditor`, `SceneStateGameplayEditor`, `SceneStateMachineEditor` | 各类编辑器 UI、属性面板、资产编辑器 |
| **图表系统** | `SceneStateMachineGraph`, `SceneStateEventGraph`, `SceneStateTransitionGraph` | 状态机图表、事件图表、转换条件图表的可视化编辑 |

## 使用场景

- 你在做**虚拟制片/广播图形**，需要让场景元素根据节目流程自动切换状态 → 用 Scene State
- 你需要为 Motion Design 场景中的 UI 元素定义**入场/显示/退场**等状态序列 → 用 Scene State
- 你想通过**可视化图表**而非蓝图节点来定义场景行为逻辑 → 用 Scene State
- 你需要让场景中的多个对象**协同响应事件**并转换状态 → 用 Scene State 的事件系统

## 蓝图用法

> ⚠️ 本插件为实验性功能，API 可能在后续版本中发生变化。

### 核心节点

由于本插件为 xlarge 规模（701 个源文件），且处于实验阶段，蓝图 API 尚在快速迭代中。以下为从模块结构推断的核心功能分组：

| 功能分组 | 说明 | 所在模块 |
|---|---|---|
| 状态机实例管理 | 创建、启动、停止状态机实例 | `SceneState` |
| 状态绑定 | 将状态机与场景中的 Actor/Component 绑定 | `SceneStateBinding` |
| 事件触发 | 通过事件驱动状态转换 | `SceneStateEvent` |
| 任务执行 | 在特定状态下执行的任务逻辑 | `SceneStateTasks` |
| 游戏玩法集成 | 与 Gameplay 框架集成的状态管理 | `SceneStateGameplay` |

### 使用示例（蓝图描述）

典型的使用流程：

1. **创建状态机资产**：在 Content Browser 中右键 → Animation → Scene State Machine
2. **编辑状态**：双击打开状态机图表编辑器，添加状态节点（如 Idle、Show、Hide）
3. **定义转换**：在状态之间连线，设置转换条件（如事件触发、时间延迟）
4. **绑定场景对象**：将状态机资产拖拽到场景中的 Actor 上，或通过蓝图绑定
5. **触发状态变化**：通过蓝图发送事件或在状态机内部设置自动转换条件

## C++ 用法

### 头文件引入

```cpp
#include "SceneState.h"
#include "SceneStateBinding.h"
#include "SceneStateEvent.h"
```

### 基本用法

由于本插件处于实验阶段且源码规模庞大（701 文件），以下为基于模块结构推断的典型用法模式：

```cpp
// 获取场景中的状态机组件并查询当前状态
// 注：具体 API 需参考源码中的 Public/*.h 头文件
```

### 进阶用法

本插件的高级用法涉及：
- 自定义状态任务（继承 SceneStateTasks 中的基类）
- 自定义事件类型（扩展 SceneStateEvent）
- 通过 SceneStateBinding 实现自定义绑定逻辑
- 与 Gameplay Ability System 集成（SceneStateGameplay）

> 💡 建议直接阅读各模块的 `Public/` 目录下的头文件获取最新 API。

## Demo 示例

> ⚠️ 本插件为实验性功能，API 尚不稳定，暂不提供完整 Demo。建议参考引擎自带的 Motion Design 示例项目。

## 模块依赖

由于本插件包含 14 个模块，以下列出各模块间的关键依赖关系：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心状态机运行时，其他所有模块的基础依赖 |
| `SceneStateBinding` | 状态机与场景对象的数据绑定机制 |
| `SceneStateEvent` | 事件驱动的状态转换系统 |
| `SceneStateTasks` | 状态关联的任务执行框架 |
| `SceneStateGameplay` | 与 UE Gameplay 框架的集成层 |
| `SceneStateBlueprint` | 蓝图类型扩展支持 |
| `SceneStateMachineGraph` | 状态机可视化图表（EdGraph） |
| `SceneStateEventGraph` | 事件逻辑可视化图表 |
| `SceneStateTransitionGraph` | 转换条件可视化图表 |

> 各 Editor 模块（`SceneStateEditor`, `SceneStateBlueprintEditor`, `SceneStateEventEditor`, `SceneStateGameplayEditor`, `SceneStateMachineEditor`）为对应的编辑器 UI 支持。

## 维护状态

### 近期更新

```
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

仅有一条 commit 记录，表明该插件刚从 Experimental 目录迁移至 VirtualProduction 目录。

### 维护评价

- **创建时间**：2025-04-22，非常新的插件
- **更新频率**：仅有一次目录迁移 commit，尚无功能性更新记录
- **维护状态**：🆕 **新发布/实验阶段**
- **已知限制**：
  - `.uplugin` 中 `IsBetaVersion=true`，标记为 Beta
  - `.uplugin` 中 `Installed=false`，默认不安装
  - Description 字段为空，文档尚未完善
  - 仅有一条 git commit，API 稳定性未知
- **推荐程度**：⚠️ **谨慎使用**。适合对 Motion Design/Virtual Production 工作流有深入了解的开发者进行早期探索和评估。不建议在生产环境中使用。该插件是 UE5 Motion Design 工具链的重要组成部分，预计会持续迭代完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无
- 测试用例：暂未发现独立测试文件

---

## 子模块索引

由于本插件为 xlarge 规模（14 个模块，701 个源文件），以下为各子模块的快速索引：

| 子模块 | 类型 | 功能概述 |
|---|---|---|
| [SceneState](SceneState.md) | Runtime | 核心状态机运行时 |
| [SceneStateBinding](SceneStateBinding.md) | Runtime | 数据绑定机制 |
| [SceneStateBlueprint](SceneStateBlueprint.md) | Runtime | 蓝图类型支持 |
| [SceneStateBlueprintEditor](SceneStateBlueprintEditor.md) | Runtime | 蓝图编辑器 UI |
| [SceneStateEditor](SceneStateEditor.md) | Runtime | 通用编辑器工具 |
| [SceneStateEvent](SceneStateEvent.md) | Runtime | 事件系统 |
| [SceneStateEventEditor](SceneStateEventEditor.md) | Runtime | 事件编辑器 UI |
| [SceneStateEventGraph](SceneStateEventGraph.md) | Runtime | 事件图表可视化 |
| [SceneStateGameplay](SceneStateGameplay.md) | Runtime | Gameplay 集成 |
| [SceneStateGameplayEditor](SceneStateGameplayEditor.md) | Runtime | Gameplay 编辑器 UI |
| [SceneStateMachineEditor](SceneStateMachineEditor.md) | Runtime | 状态机编辑器 UI |
| [SceneStateMachineGraph](SceneStateMachineGraph.md) | Runtime | 状态机图表可视化 |
| [SceneStateTasks](SceneStateTasks.md) | Runtime | 任务执行框架 |
| [SceneStateTransitionGraph](SceneStateTransitionGraph.md) | Runtime | 转换条件图表可视化 |

> ⚠️ 各子模块文档待补充。本插件刚从 Experimental 迁出，源码结构可能随版本更新发生较大变化。