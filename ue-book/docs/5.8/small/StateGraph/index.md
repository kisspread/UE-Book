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
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph) | |

## 用途

StateGraph 是一个通用的状态机框架，它将状态机建模为**有向图**。它解决了传统状态机实现中状态转换逻辑复杂、难以维护和扩展的问题。与简单的 FSM（有限状态机）不同，StateGraph 支持更高级的特性，如**超时**、**热修复**（运行时修改状态图）、以及**运行时动态修改**状态图结构。这使得它特别适用于需要高度可配置、可扩展状态管理逻辑的场景，如复杂的游戏流程（如匹配、登录流程）、AI行为树的简化替代方案，或任何需要清晰、可视化状态流转的应用程序。

## 使用场景

-   **复杂流程管理**：例如游戏中的多人匹配流程、玩家登录/认证流程、菜单导航系统，这些流程通常包含多个状态（如等待、搜索、连接、准备）和可能的超时、错误分支。
-   **AI状态机**：控制NPC的行为状态（如巡逻、追击、攻击、逃跑），状态之间可以根据条件和事件进行转换。
-   **热修复与调试**：由于支持运行时修改状态图，可以在不重新编译和重启的情况下，对线上系统的状态逻辑进行调试或紧急修复。
-   **需要高可读性和可维护性的系统**：状态图的结构比嵌套的switch-case或if-else语句更直观，易于理解和设计。

## 模块列表

| 模块 | 说明 |
|---|---|
| [**StateGraph**](StateGraph.md) | 核心状态图库，提供状态节点、边、图构建和状态机运行的基础类和框架。 |
| [**StateGraphManager**](StateGraphManager.md) | 状态图的管理器，负责创建、管理和驱动状态图实例的生命周期。 |
| [**StateGraphTests**](StateGraphTests.md) | 单元测试和功能测试，用于验证状态图框架的正确性和可靠性。（通常不直接被项目依赖） |

## C++ 用法概览

由于这是一个底层框架插件，典型的用法是：
1.  在项目的 `Build.cs` 中添加对 `StateGraph` 和 `StateGraphManager` 模块的依赖。
2.  定义你的状态图：使用提供的API（如`FStateGraphBuilder`）来构建包含状态节点和转换边的有向图。
3.  通过`UStateGraphManager`来实例化并运行你的状态图。
4.  在状态节点的回调或转换条件中编写你的业务逻辑。

详细 API 请参阅各子模块文档。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5b01134f` | Remove matchmaking attempt when CreateClientJoinStateGraph fails in TryMatchmaking. | 修复了当创建客户端加入状态图失败时，错误地尝试匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从旧的 `UE_LOG` 迁移到新的 `UE_LOGF`。 |
| 2026-02-10 | `0e0a7b5f` | UE: StateGraph remove timeout ticker when needed. | 优化了超时机制，在不再需要时移除超时计时器，避免资源浪费。 |
| 2025-12-09 | `bc24ccfb` | Complete PreLoginAsync stategraph with error if user disconnects before reaching PostLogin | 增强了登录流程：如果玩家在到达PostLogin状态前断开连接，现在会正确完成PreLogin异步状态图并报错。 |
| 2025-12-09 | `7a456323` | [Backout] - CL49078828 | 回退了之前的某次提交。 |

### 维护评价

-   **活跃度**：该插件近期（2026年）仍有实质性更新，主要集中在修复特定使用场景下的逻辑错误（如匹配流程、登录流程）和进行代码现代化（迁移日志宏）。这表明它仍在**积极维护**中，并被实际项目（如《堡垒之夜》）所使用。
-   **实验性**：插件仍处于 `Experimental` 目录，且默认未启用。这意味着其API可能会发生重大变化，不推荐在追求稳定的生产项目中直接使用，但非常适合用于学习、原型开发或特定内部项目。
-   **推荐度**：如果你需要一个强大、灵活且支持运行时修改的状态机框架，并且不介意处理实验性API的潜在变动，那么 StateGraph 是一个非常优秀的选择。建议通过测试用例深入理解其用法。

## 相关链接

-   [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph/Tests)