# Gameplay Graph

> A graph representation model and common graph alogrithms that can be used for gameplay.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏玩法图 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayGraph` (Runtime), `GameplayGraphTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayGraph) | |

## 用途

GameplayGraph 插件提供了一个用于游戏逻辑的**图数据结构**及其基础算法。它旨在为游戏中需要“连接关系”的场景提供一个通用、可扩展的解决方案。该插件不依赖任何特定的 UE 子系统（如导航网格或对话树），而是定义了一套抽象的图模型，开发者可以基于此模型构建具体的功能，例如：
*   复杂的技能树或科技树系统。
*   非线性的叙事分支或对话系统。
*   基于图的关卡设计或区域连接。
*   自定义寻路或状态机系统。

它解决的核心问题是：避免每个游戏系统都重新实现一套图结构，提供统一、可靠、可序列化的基础模型。

## 使用场景

- 你需要在项目中实现一个**技能树**，玩家解锁技能需要前置条件，且技能之间存在复杂的依赖关系 → 使用 GameplayGraph 来建模技能节点和它们的前置关系。
- 你正在制作一个**文字冒险游戏**，对话流程是一个由多个对话节点和选择组成的复杂网络 → 使用 GameplayGraph 来存储和管理对话图，实现灵活的分支跳转。
- 你开发一个**开放世界游戏**，需要一个系统来管理不同区域（如城堡、村庄、森林）之间的连接路径和传送关系 → 使用 GameplayGraph 中的“岛”（Island）概念来表示区域，边（Edge）表示连接。
- 你需要实现一个**复杂的任务系统**，任务可以并行、串行或存在条件关联 → 使用 GameplayGraph 来建模任务状态和依赖关系。

## 蓝图用法

该插件主要为 C++ 设计，蓝图 API 相对较少，主要用于数据访问和基础操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddVertex` | 向图中添加一个新的顶点。 | `UGraph` |
| `FindVertex` | 根据唯一索引查找图中的一个顶点。 | `UGraph` |
| `GetVertices` | 获取图中所有顶点的数组。 | `UGraph` |
| `GetAllIslands` | 获取图中所有逻辑“岛”（子图）的数组。 | `UGraph` |
| `GetUniqueIndex` | 获取图元素（顶点、岛等）的唯一标识符。 | `UGraphElement` |

### 使用示例（蓝图描述）

1.  **创建图**：创建一个 `UGraph` 对象。
2.  **添加顶点**：在蓝图中多次调用 `UGraph::AddVertex` 节点，为每个顶点分配一个 `FGraphUniqueIndex`（通常通过一个结构体构造节点）。
3.  **添加边**：调用 `UGraph::AddEdge` 节点，传入两个顶点的句柄（Handle）来建立连接。
4.  **查询与遍历**：使用 `GetVertices` 获取所有节点，或使用 `FindVertex` 定位特定节点。通过节点句柄可以访问其连接的边和其他属性。

## C++ 用法

### 头文件引入

```cpp
#include "Graph.h" // UGraph 核心类
#include "GraphElement.h" // UGraphElement 基类
#include "GraphVertex.h" // 顶点相关
#include "GraphIsland.h" // 岛（子图）相关
```

### 基本用法

从测试用例 `FTestGraphBuilder` 提取，展示了图的基本构建流程。

```cpp
// 源码来源: Engine/Plugins/Experimental/GameplayGraph/Tests/Private/TestGraphBuilder.cpp
#include "Graph.h"
#include "GraphVertex.h"
#include "GraphIsland.h"
#include "GraphElement.h"

// 假设我们有一个自定义的顶点数据结构
struct FMyNodeData {
    FString Name;
    int32 Value;
};

void BuildSimpleGraph()
{
    // 1. 创建图对象
    UGraph* MyGraph = NewObject<UGraph>();

    // 2. 添加顶点（这里使用测试工具类中的逻辑，实际项目需自行创建）
    // 每个顶点都是一个 UGraphElement 或其子类实例
    TArray<UGraphVertex*> Vertices;
    for (int32 i = 0; i < 5; ++i)
    {
        UGraphVertex* Vertex = MyGraph->AddVertex<UGraphVertex>();
        // 可以在此为顶点附加自定义数据
        Vertices.Add(Vertex);
    }

    // 3. 添加边（连接顶点）
    // 创建一个线性链: 0-1-2-3-4
    for (int32 i = 0; i < Vertices.Num() - 1; ++i)
    {
        MyGraph->AddEdge(Vertices[i], Vertices[i + 1]);
    }

    // 4. 查询
    // 获取某个顶点的所有邻居
    UGraphVertex* StartVertex = Vertices[0];
    TArray<FGraphVertexHandle> Neighbors;
    StartVertex->GetNeighbors(Neighbors); // 注意：实际API需查阅源码，此处为示意
    UE_LOG(LogTemp, Log, TEXT("Vertex 0 has %d neighbors."), Neighbors.Num());
}
```

### 进阶用法

结合“岛”（Island）概念组织图结构。岛可以看作图中的一个逻辑子图或分组。

```cpp
// 源码来源: Engine/Plugins/Experimental/GameplayGraph/Tests/Private/TestGraphBuilder.cpp
#include "GraphIsland.h"

void BuildGraphWithIslands()
{
    UGraph* GameGraph = NewObject<UGraph>();

    // 假设我们创建两个独立的图区域（岛）
    // 岛通常代表一个连续的区域或一组相关联的节点
    FGraphIslandHandle Island1 = GameGraph->AddIsland();
    FGraphIslandHandle Island2 = GameGraph->AddIsland();

    // 将顶点分配到不同的岛中
    UGraphVertex* VillageCenter = GameGraph->AddVertexToIsland<UGraphVertex>(Island1);
    UGraphVertex* Blacksmith = GameGraph->AddVertexToIsland<UGraphVertex>(Island1);
    UGraphVertex* ForestEntrance = GameGraph->AddVertexToIsland<UGraphVertex>(Island2);

    // 在同一个岛内添加边
    GameGraph->AddEdge(VillageCenter, Blacksmith);

    // 在两个岛之间添加边（例如，从村庄中心到森林入口）
    GameGraph->AddEdge(VillageCenter, ForestEntrance);

    // 查询属于特定岛的所有顶点
    TArray<FGraphVertexHandle> IslandVertices;
    GameGraph->GetVerticesForIsland(Island1, IslandVertices);
    // 此时 IslandVertices 包含 VillageCenter 和 Blacksmith
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建一个带权的图并计算简单的路径。

```cpp
// MyGraphDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Graph.h"

class FWeightedEdge
{
public:
    FGraphVertexHandle Target;
    float Weight;
};

// 自定义带权图节点
UCLASS()
class UWeightedGraphNode : public UGraphVertex
{
    GENERATED_BODY()

public:
    // 存储该节点所有出边的权重信息
    TMap<FGraphVertexHandle, float> WeightedEdges;
};
```

```cpp
// MyGraphDemo.cpp
#include "MyGraphDemo.h"
#include "GraphIsland.h"

void RunGraphDemo()
{
    // 创建图
    UGraph* NavigationGraph = NewObject<UGraph>();

    // 创建节点
    UWeightedGraphNode* NodeA = NavigationGraph->AddVertex<UWeightedGraphNode>();
    UWeightedGraphNode* NodeB = NavigationGraph->AddVertex<UWeightedGraphNode>();
    UWeightedGraphNode* NodeC = NavigationGraph->AddVertex<UWeightedGraphNode>();

    // 建立带权边
    auto AddWeightedEdge = [&](UWeightedGraphNode* From, UWeightedGraphNode* To, float Weight)
    {
        NavigationGraph->AddEdge(From, To);
        From->WeightedEdges.Add(To->GetGraphVertexHandle(), Weight);
        // 如果是无向图，也需要在 To 节点添加
        // To->WeightedEdges.Add(From->GetGraphVertexHandle(), Weight);
    };

    AddWeightedEdge(NodeA, NodeB, 1.5f); // A->B, 权重1.5
    AddWeightedEdge(NodeA, NodeC, 2.0f); // A->C, 权重2.0
    AddWeightedEdge(NodeB, NodeC, 0.5f); // B->C, 权重0.5

    // 简单的遍历示例：从A出发，找到权重最小的下一步
    UWeightedGraphNode* CurrentNode = NodeA;
    float MinWeight = TNumericLimits<float>::Max();
    UWeightedGraphNode* BestNextNode = nullptr;

    for (auto& EdgePair : CurrentNode->WeightedEdges)
    {
        if (EdgePair.Value < MinWeight)
        {
            MinWeight = EdgePair.Value;
            // 通过Handle获取实际对象（示意）
            BestNextNode = Cast<UWeightedGraphNode>(NavigationGraph->FindVertex(EdgePair.Key));
        }
    }

    if (BestNextNode)
    {
        UE_LOG(LogTemp, Log, TEXT("From NodeA, the cheapest next step is with weight: %.1f"), MinWeight);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/CoreUObject 等）。

| 模块 | 用途 |
|---|---|
| （无） | 该插件仅依赖 UE 核心模块，如 `Core`, `CoreUObject`, `Engine`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，遵循引擎新规范。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 批量代码规范化，将空析构函数改为 `= default`。 |
| 2025-10-29 | `fa2900e1` | UGraph serialization optimization | 对 `UGraph` 的序列化进行了优化。 |
| 2025-10-28 | `ec6d63d6` | UGraph serialization optimization | 同上，序列化优化的另一个提交（可能与回退后重新提交有关）。 |

### 维护评价

**维护状态：维护中**

*   **创建时间**：2023年2月，相对年轻。
*   **活跃度**：最近一次实质性更新（序列化优化）发生在2025年10月，距今约6个月。2026年4月有编译规范更新。这表明该插件**仍处于维护中**，但更新频率不高，属于周期性维护。
*   **已知限制**：作为 `Experimental` 且 `EnabledByDefault=false` 的插件，其 API 可能随着版本迭代发生变化，不建议用于面向最终发布的核心功能。目前看来 API 设计已经比较稳定。
*   **推荐使用**：**适合原型开发和特定子系统使用**。如果你的游戏玩法确实需要一个轻量级、可定制的图数据结构，并且你愿意承担未来 API 微调的风险，那么它是一个很好的起点。对于生产环境项目，建议密切跟踪其更新或考虑自行维护一个分支。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayGraph)
- [官方文档]( ) （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/GameplayGraph/Tests)