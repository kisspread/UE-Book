# Gameplay Graph

> A graph representation model and common graph alogrithms that can be used for gameplay.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏玩法图 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayGraph` (Runtime), `GameplayGraphTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph) | |

## 总体用途

GameplayGraph 提供了一套图数据结构（节点、边、图）以及常见的图算法，专门为游戏玩法逻辑设计。它允许开发者以图的形式建模各种游戏内关系，例如 AI 寻路网络、资源流通路径、社交关系图、关卡连通性等，并在此基础上执行 BFS/DFS、最短路径等经典算法。该插件目前处于实验阶段，适用于快速原型和需要动态图操作的场景。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [GameplayGraph](./GameplayGraph.md) | Runtime | 核心模块：定义图数据结构（`UGraph`, `UGraphNode`, `UGraphEdge`）及基础图算法（添加/移除节点边、连通分量、BFS、Dijkstra 等）。 |
| [GameplayGraphTests](./GameplayGraphTests.md) | Runtime | 测试模块：包含自动化测试用例，验证图操作的正确性和算法行为（如 BFS 遍历、最短路径、连通性检测）。 |

## 使用场景

- **AI 寻路**：将导航网格抽象为图节点，动态计算最短路径或避开障碍。
- **资源网络**：模拟电力、水流、通信等资源的流动，通过图算法查找瓶颈或失效路径。
- **社交关系**：表示角色之间的好感度或势力关系，利用图聚类算法分析阵营。
- **关卡拓扑**：建模门、房间、走廊的连接，实现室内定位或事件触发。
- **逻辑谜题**：在谜题中构建状态图，利用 DFS/BFS 搜索解或验证可达性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph)
- [核心模块文档](./GameplayGraph.md)
- [测试模块文档](./GameplayGraphTests.md)
- [测试用例目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph/Tests)