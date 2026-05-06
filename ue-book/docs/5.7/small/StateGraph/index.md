# State Graph

> Generic state machine management class.

| 属性 | 值 |
|---|---|
| 中文名 | 状态图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StateGraph` (Runtime), `StateGraphManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph) | |

## 总体用途

**StateGraph** 提供一套泛型状态机管理框架，允许开发者以可组合的图（Graph）方式定义和运行状态机。它专注于运行时效率与灵活性，适用于 AI 决策、动画状态机、游戏流程控制等需要状态切换的场景。

该插件由两个运行时模块组成：`StateGraph` 提供核心节点（`FStateGraph`、`FStateGraphNode`）与运行时逻辑；`StateGraphManager` 封装了图形实例的创建、销毁与生命周期管理，提供更高级的抽象接口。

## 模块

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `StateGraph` (Runtime) | 状态图核心引擎，定义状态节点、过渡与执行逻辑。 | [StateGraph.md](./StateGraph.md) |
| `StateGraphManager` (Runtime) | 状态图实例管理器，处理图实例的创建、销毁与状态持久化。 | [StateGraphManager.md](./StateGraphManager.md) |
| `StateGraphTests` (Runtime) | 自动化测试模块，验证核心功能正确性（仅测试用途）。 | [StateGraphTests.md](./StateGraphTests.md) |

## 使用场景

- **AI 行为树替代/补充**：用有向图表示 NPC 行为状态，支持嵌套子状态与并行状态。
- **动画状态机（AnimStateMachine）**：定义动画状态过渡，附带条件与动作。
- **游戏流程控制**：管理 UI 流程、关卡加载序列、游戏规则状态。
- **自定义状态机扩展**：基于 `FStateGraph` 和 `FStateGraphNode` 实现专有状态逻辑。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph)
- [StateGraph 模块文档](./StateGraph.md)
- [StateGraphManager 模块文档](./StateGraphManager.md)
- [StateGraphTests 模块文档](./StateGraphTests.md)