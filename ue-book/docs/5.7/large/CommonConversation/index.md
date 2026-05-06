# Common Conversation

> An *experimental* plugin for authoring graph-based conversation trees

| 属性 | 值 |
|---|---|
| 中文名 | 通用对话 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CommonConversationRuntime` (Runtime), `CommonConversationGraph` (UncookedOnly), `CommonConversationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕 (约 0 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation) | |

## 总体用途

Common Conversation 提供了一套基于图的对话树创作框架。它允许开发者通过可视化编辑器设计分支对话，并利用运行时系统在游戏中执行对话流程。插件包含三个模块：**运行时模块**负责对话数据与节点求值；**图形模块**定义资产类型与节点图表示；**编辑器模块**提供完整的编辑器界面、节点绘制、引脚连接与上下文菜单。适合需要复杂分支交互叙事（如RPG、冒险游戏）的项目。

## 模块列表

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `CommonConversationRuntime` | 对话资产、节点类型与运行时执行逻辑 | [CommonConversationRuntime.md](./CommonConversationRuntime.md) |
| `CommonConversationGraph` | 资产引擎的图表示、节点类及资产工厂 | [CommonConversationGraph.md](./CommonConversationGraph.md) |
| `CommonConversationEditor` | 编辑器 UI、节点绘制、引脚处理与上下文菜单 | [CommonConversationEditor.md](./CommonConversationEditor.md) |

## 使用场景

- **交互式对话**：为游戏中的 NPC 创建多分支、条件触发的对话树，支持玩家选择与响应。
- **任务/事件触发**：在对话节点中绑定游戏事件、任务进度、物品检测等逻辑，实现动态剧情。
- **视觉剧本创作**：设计师可在编辑器中直观地拖拽节点、连接分支，无需编写代码即可设计对话流程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CommonConversation)