# Gameplay Graph

> A graph representation model and common graph alogrithms that can be used for gameplay.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏图 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayGraph) | |

## 用途

GameplayGraph 插件提供了一套轻量级、可序列化的 **无向图数据结构** 以及相关的通用算法，旨在为游戏玩法（Gameplay）系统提供基础的图关系表示能力。

它主要解决以下问题：
1.  **关系建模**：需要表示游戏世界中实体之间的复杂连接关系（如房间连通性、社交网络、技能树等）。
2.  **连接性查询**：快速回答两个节点是否相连、如何相连、距离多远等问题。
3.  **结构管理**：自动维护图结构的“岛”（连通分量），当图结构发生改变时（如添加/删除节点或边），自动处理岛的合并、分裂和销毁。
4.  **数据持久化**：提供完善的序列化（Serialization）与增量序列化（Incremental Serialization）机制，方便图的存档（Save/Load）和网络同步。

该插件的核心设计是 **面向数据** 和 **易于扩展** 的。基础的 `UGraph`、`UGraphVertex` 和 `UGraphIsland` 类提供了图的核心框架，使用者通常需要派生自定义的顶点和边子类来存储具体的游戏数据。

## 使用场景

-   **地图/房间生成系统**：在程序化生成的地图中，将每个房间视为一个节点，房间之间的门或通道视为边，构建一个“房间图”来管理整个地图的结构、连通性检查和寻路。
-   **状态机/行为树的关系图**：管理复杂状态之间可能存在的多路径转换关系。
-   **社交关系系统**：表示玩家、NPC 之间的友谊、敌对、团队等关系网络。
-   **任务/技能依赖图**：表示任务之间的前后置条件，或技能树的解锁路径。
-   **任何需要解析“图”结构数据的游戏逻辑**：例如解谜游戏中的电路连接、网络节点的布线等。

## 蓝图用法

目前，该插件的核心类（`UGraph`, `UGraphVertex`, `UGraphIsland`）及其句柄结构（`FGraphVertexHandle`）均为 `UCLASS` 或 `USTRUCT`，但其主要的创建、修改和查询接口均为 C++ 接口（`UE_API`），并未标记为 `BlueprintCallable`。因此，**暂无直接的蓝图节点**。若需要在蓝图中使用，建议通过编写 C++ 蓝图函数库（Blueprint Function Library）进行封装。

## C++ 用法

### 头文件引入

```cpp
#include “Graph/Graph.h”
#include “Graph/GraphVertex.h”
#include “Graph/GraphIsland.h”
```

### 基本用法

1.  **创建和初始化图**：
    ```cpp
    // 创建一个图对象
    UGraph* MyGraph = NewObject<UGraph>();

    // 使用属性初始化（可选），例如启用岛检测
    FGraphProperties Properties;
    Properties.bGenerateIslands = true;
    MyGraph->InitializeFromProperties(Properties);
    ```
    *来源：基于 `UGraph::InitializeFromProperties` 接口*

2.  **创建顶点**：
    ```cpp
    // 创建一个节点，返回一个句柄
    FGraphVertexHandle VertexHandleA = MyGraph->CreateVertex();
    FGraphVertexHandle VertexHandleB = MyGraph->CreateVertex();

    // 通过句柄获取顶点对象（如果需要设置自定义数据）
    UGraphVertex* VertexA = VertexHandleA.GetVertex();
    ```
    *来源：基于 `UGraph::CreateVertex` 和 `FGraphVertexHandle::GetVertex` 接口*

3.  **创建边（连接节点）**：
    ```cpp
    // 在两个节点之间创建一条边
    MyGraph->CreateBulkEdges({ FEdgeSpecifier(VertexHandleA, VertexHandleB) });

    // 或者单个创建（内部会调用 CreateBulkEdges）
    // MyGraph->CreateEdge(VertexHandleA, VertexHandleB); // 注意：CreateEdge 是私有方法
    ```
    *来源：基于 `UGraph::CreateBulkEdges` 和 `FEdgeSpecifier` 结构*

### 进阶用法

1.  **监听图的变化**：
    ```cpp
    // 绑定顶点创建的委托
    MyGraph->OnVertexCreated.AddLambda([](const FGraphVertexHandle& NewHandle) {
        UE_LOG(LogTemp, Log, TEXT(“新顶点被创建， ID: %s”), *NewHandle.GetUniqueIndex().ToString());
    });

    // 绑定边创建的委托
    MyGraph->OnEdgeCreated.AddLambda([](const FEdgeSpecifier& NewEdge) {
        UE_LOG(LogTemp, Log, TEXT(“新边被创建， 连接 %s 与 %s”),
            *NewEdge.GetVertexHandle1().GetUniqueIndex().ToString(),
            *NewEdge.GetVertexHandle2().GetUniqueIndex().ToString());
    });
    ```
    *来源：基于 `UGraph` 的委托成员变量 `OnVertexCreated`, `OnEdgeCreated` 等*

2.  **遍历图的结构**：
    ```cpp
    // 遍历图中的所有岛
    MyGraph->ForEachIsland([](const FGraphIslandHandle& IslandHandle, UGraphIsland* Island) {
        UE_LOG(LogTemp, Log, TEXT(“岛屿 %s 包含 %d 个节点”), *IslandHandle.GetUniqueIndex().ToString(), Island->Num());
        // 遍历岛屿中的所有节点
        Island->ForEachVertex([](const FGraphVertexHandle& VH) {
            // 处理节点
        });
    });

    // 遍历某个节点的所有邻居
    if (UGraphVertex* V = VertexHandleA.GetVertex())
    {
        V->ForEachAdjacentVertex([](const FGraphVertexHandle& NeighborHandle) {
            UE_LOG(LogTemp, Log, TEXT(“邻居节点 ID: %s”), *NeighborHandle.GetUniqueIndex().ToString());
        });
    }
    ```
    *来源：基于 `UGraph::ForEachIsland`、`UGraphIsland::ForEachVertex` 和 `UGraphVertex::ForEachAdjacentVertex` 接口*

3.  **使用内置算法**：
    ```cpp
    #include “Graph/Algorithms/Search/Search.h”
    #include “Graph/Algorithms/Connectivity/ConnectedComponents.h”

    // 使用广度优先搜索（BFS）查找节点
    FGraphVertexHandle Found = Graph::Algorithms::BFS(VertexHandleA, [](const FGraphVertexHandle& Current) {
        // 返回 true 表示找到目标，停止搜索
        return Current.GetUniqueIndex().ToString() == TEXT(“TARGET_NODE_ID”);
    });

    // 查找一组节点中的连通分量
    TSet<FGraphVertexHandle> MyNodeSet = { VertexHandleA, VertexHandleB /* ... */ };
    TArray<TSet<FGraphVertexHandle>> Components = Graph::Algorithms::FindConnectedComponents(MyNodeSet);
    ```
    *来源：基于 `Graph::Algorithms::BFS`, `Graph::Algorithms::DFS`, `Graph::Algorithms::FindConnectedComponents` 函数*

## Demo 示例

一个完整的最小示例，演示如何创建一个简单的三角形图。

```cpp
// MyGameGraphExample.h
#pragma once
#include “CoreMinimal.h”
#include “Graph/Graph.h”
#include “Graph/GraphVertex.h”

class UMyGraphExample
{
public:
    static void RunExample();
};
```

```cpp
// MyGameGraphExample.cpp
#include “MyGameGraphExample.h”
#include “Graph/GraphHandle.h”

void UMyGraphExample::RunExample()
{
    // 1. 创建图
    UGraph* TriangleGraph = NewObject<UGraph>();
    FGraphProperties Props;
    Props.bGenerateIslands = true; // 启用岛检测
    TriangleGraph->InitializeFromProperties(Props);

    // 2. 创建三个顶点
    FGraphVertexHandle V1 = TriangleGraph->CreateVertex();
    FGraphVertexHandle V2 = TriangleGraph->CreateVertex();
    FGraphVertexHandle V3 = TriangleGraph->CreateVertex();

    UE_LOG(LogTemp, Log, TEXT(“创建了三个节点: %s, %s, %s”),
        *V1.GetUniqueIndex().ToString(),
        *V2.GetUniqueIndex().ToString(),
        *V3.GetUniqueIndex().ToString());

    // 3. 创建三条边，连接成三角形
    TArray<FEdgeSpecifier> EdgesToCreate;
    EdgesToCreate.Emplace(FEdgeSpecifier(V1, V2));
    EdgesToCreate.Emplace(FEdgeSpecifier(V2, V3));
    EdgesToCreate.Emplace(FEdgeSpecifier(V3, V1));
    TriangleGraph->CreateBulkEdges(MoveTemp(EdgesToCreate));

    UE_LOG(LogTemp, Log, TEXT(“创建了 %d 条边”), 3);

    // 4. 验证结构
    UE_LOG(LogTemp, Log, TEXT(“图中有 %d 个节点， %d 个岛屿”), TriangleGraph->NumVertices(), TriangleGraph->NumIslands());

    // 5. 检查连通性（应该只有一个岛）
    if (UGraphVertex* Vertex1 = V1.GetVertex())
    {
        bool bConnected = Vertex1->HasEdgeTo(V2);
        UE_LOG(LogTemp, Log, TEXT(“节点1和节点2是否相连: %s”), bConnected ? TEXT(“是”) : TEXT(“否”));
    }

    // 6. 删除一个节点，观察岛的变化
    TriangleGraph->RemoveVertex(V3);
    UE_LOG(LogTemp, Log, TEXT(“删除节点V3后，图中有 %d 个节点， %d 个岛屿”), TriangleGraph->NumVertices(), TriangleGraph->NumIslands());
    // 此时，V1 和 V2 仍然相连，它们应该还在同一个岛里。
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件的 `Build.cs` 文件通常只依赖于 `Core`, `CoreUObject`, `Engine` 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为新的 `UE_LOGF` 宏。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码风格规范化，将空的析构函数体替换为 `= default`。 |
| 2025-10-29 | `fa2900e1` | UGraph serialization optimization | 对图的序列化功能进行了优化，提升了存档/加载性能。 |
| 2025-10-28 | `62678ca9` | [Backout] - CL47459196 - Backed out due to 39.10 CIS issue | 回滚了一次提交，原因是其引入了持续集成（CIS）问题。 |
| 2025-10-28 | `ec6d63d6` | UGraph serialization optimization | 图的序列化优化（可能被后续提交回滚）。 |

### 维护评价

-   **活跃度**：该插件处于**活跃维护**状态。从提交记录看，自 2023 年 2 月创建以来，至 2026 年 4 月仍有实质性功能优化（序列化）和代码维护（日志迁移、代码风格修复）。
-   **状态**：标记为 **实验性 (IsExperimentalVersion = true)** 且**默认不启用 (EnabledByDefault = false)**。这表明 Epic 官方认为该插件尚未达到稳定生产可用的状态，API 和功能在未来版本中可能会发生变化。
-   **已知限制**：目前没有蓝图接口，主要面向 C++ 开发者。核心功能（如图遍历算法）相对基础，复杂的图论算法（如最短路径、最小生成树）需要使用者自行扩展或结合其他库实现。
-   **推荐度**：**推荐在 C++ 项目中谨慎使用**。如果你的项目有一个清晰、明确的图结构需求，且不介意应对未来可能的 API 变动，这是一个很好的官方基础框架。对于关键的、长期稳定的生产项目，建议将其作为参考，或做好封装以隔离可能的变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayGraph)
-   [官方文档]() （暂无）
-   [测试用例]() （暂无公开测试用例路径，但插件包含 `GameplayGraphTests` 模块）