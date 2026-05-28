# Gameplay Graph

> A graph representation model and common graph alogrithms that can be used for gameplay.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏图 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayGraph` (Runtime), `GameplayGraphTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayGraph) | |

## 用途

这是一个用于游戏玩法的图数据结构运行时库。它提供了一个基础框架，用于在内存中创建、操作和序列化图（Graph）结构。插件本身不直接实现具体游戏功能（如导航、对话），而是为需要图模型的游戏系统（如导航网格、对话树、技能树、任务系统）提供底层支持。它解决了游戏开发中需要通用图形表示和算法的问题。

## 使用场景

- **关卡与导航**：构建可查询的路径图或区域连接图。
- **对话与任务系统**：建模复杂的对话分支或任务依赖关系。
- **技能与科技树**：管理技能解锁的前置条件和关联。
- **社交与关系网络**：模拟游戏内角色间的复杂关系。
- **任何需要建模“节点与连接”关系**的游戏逻辑系统。

## 蓝图用法

此插件主要为 C++ 运行时库，其核心功能（图的创建、节点操作）通常通过 C++ API 直接使用。详细的蓝图暴露 API 请参阅子模块文档。一般而言，可能通过蓝图函数库或自定义蓝图节点来暴露部分查询功能。

## C++ 用法

详细的类结构和 API 请参阅子模块文档。典型的用法流程是：
1.  创建一个图对象 (`UGraph`)。
2.  向图中添加节点 (`UGraphNode`)。
3.  在节点之间建立边 (`UGraphEdge`) 连接。
4.  使用提供的算法（如路径查找、遍历）操作图。
5.  根据需要将图序列化到资产或保存数据中。

**头文件引入**：通常需要引入 `Graph` 相关的头文件，具体路径请参考模块文档。

## Demo 示例

一个概念性的 C++ 使用示例：
```cpp
// 假设已正确包含相关头文件
#include “Graph.h”
#include “GraphNode.h”
#include “GraphEdge.h”

// 创建图
UGraph* MyGraph = NewObject<UGraph>();

// 创建并添加节点
UGraphNode* NodeA = MyGraph->CreateNode(…);
UGraphNode* NodeB = MyGraph->CreateNode(…);

// 创建连接节点的边
MyGraph->CreateEdge(NodeA, NodeB, …);

// 使用算法（例如，寻找节点A和B之间的路径）
TArray<UGraphNode*> Path = MyGraph->FindPath(NodeA, NodeB);
```
**注意**：以上为示意代码，具体 API 调用需根据实际类定义调整。

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。此插件旨在提供通用数据结构，对其他游戏特定模块依赖极低。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 进行全局日志宏迁移。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 执行引擎范围的代码规范修正。 |
| 2025-10-29 | `fa2900e1` | UGraph serialization optimization | 优化图的序列化性能。 |
| 2025-10-28 | `62678ca9` | [Backout] - CL47459196 - Backed out due to 39.10 CIS issue | 回退了一次提交以解决构建问题。 |
| 2025-10-28 | `ec6d63d6` | UGraph serialization optimization | 进行了图的序列化优化。 |

### 维护评价

- **状态**：**活跃维护中**。插件创建约 3 年，最近一次更新在 2026 年 4 月，且 2025 年 10 月有多次实质性优化和代码修复提交。
- **趋势**：开发者持续进行性能优化和代码质量改进，表明插件仍处于积极开发和打磨阶段。
- **实验性**：插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明其 API 和功能可能在未来版本中发生变化，不建议在稳定项目中深度依赖。
- **建议**：适合在实验性项目或原型开发中使用，用于探索基于图的玩法系统。在生产环境中使用需谨慎，并准备应对 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayGraph)
- [GameplayGraph 模块文档](GameplayGraph.md)
- [GameplayGraphTests 模块文档](GameplayGraphTests.md)