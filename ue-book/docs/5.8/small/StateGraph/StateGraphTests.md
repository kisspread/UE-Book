# State Graph

> Generic state machine management class.

| 属性 | 值 |
|---|---|
| 中文名 | 状态图框架 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StateGraph` (Runtime), `StateGraphManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph) | |

## 用途

StateGraph 是一个将状态机建模为**有向图**的运行时框架，区别于传统的线性状态机。它解决了复杂业务流程（如多人游戏的登录/匹配流程）中状态流转难以管理的问题。

核心特性包括：
- **有向图模型**：状态之间通过图结构连接，支持复杂的分支和条件跳转
- **超时管理**：内置超时机制，防止状态卡死（如匹配等待超时）
- **热修复支持**：允许在运行时修改状态图结构
- **运行时修改**：支持在运行时动态调整状态图

从 git 历史可以看出，Epic 内部已在多人游戏的 PreLogin → PostLogin 流程和匹配系统中实际使用该框架。

## 使用场景

- 你需要管理多人游戏的玩家登录流程（PreLogin → PostLogin 的异步状态流转）
- 你需要实现带超时和错误处理的匹配系统
- 你需要一个支持运行时修改的状态机，而不是硬编码的 switch-case
- 你需要将复杂的游戏流程分解为可视化的状态图

## 蓝图用法

基于当前可用的源码信息，该插件主要为 C++ 框架，蓝图接口信息有限。如有需要，可查阅 `StateGraphManager` 模块中可能暴露的蓝图接口。

## C++ 用法

> ⚠️ 由于未能获取完整的 Public API 源码，以下为基于 git 历史和模块结构推断的用法。建议直接阅读源码获取完整 API。

### 头文件引入

```cpp
#include "StateGraph.h"
```

### 模块依赖

在你的模块 `Build.cs` 中添加：

```cpp
PublicDependencyModuleNames.Add("StateGraph");
PublicDependencyModuleNames.Add("StateGraphManager");
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StateGraph` | 核心状态图框架（状态定义、图结构、状态流转） |
| `StateGraphManager` | 状态图管理器（实例管理、生命周期控制） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5b01134f` | Remove matchmaking attempt when CreateClientJoinStateGraph fails in TryMatchmaking. | 匹配失败时移除多余的重试逻辑 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到新格式 |
| 2026-02-10 | `0e0a7b5f` | UE: StateGraph remove timeout ticker when needed. | 修复超时计时器未正确清理的问题 |
| 2025-12-09 | `bc24ccfb` | Complete PreLoginAsync stategraph with error if user disconnects before reaching PostLogin | 玩家断开连接时正确完成异步登录状态图 |
| 2025-12-09 | `7a456323` | [Backout] - CL49078828 | 回退之前的提交 |

### 维护评价

- **活跃维护**：最近 6 个月内持续有功能性更新和 Bug 修复
- **实验性插件**：标记为 Experimental，`EnabledByDefault=false`，需手动启用
- **内部使用中**：从 commit 内容看，Epic 内部的多人游戏模块（OnlineSubsystem 相关）正在积极使用
- **推荐程度**：适合需要复杂状态管理的项目参考和学习，但作为实验性插件，生产环境使用需谨慎评估稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph/Tests/StateGraphTests)