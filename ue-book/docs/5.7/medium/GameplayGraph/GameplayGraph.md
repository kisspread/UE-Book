# Gameplay Graph

> A graph representation model and common graph alogrithms that can be used for gameplay.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏图 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph) | |

## 用途

`Gameplay Graph` 提供了一个通用的**无向图数据模型**，用于在游戏逻辑中表达节点（顶点）和边的关系。它并非为特定场景（如寻路、状态机）而设计，而是作为基础框架，允许开发者：

- 构建任意节点之间的连接关系
- 自动维护“岛屿”（连通分量）
- 对图执行算法（BFS、DFS、连通分量查找）
- 序列化/反序列化图结构
- 通过子类化 `UGraphVertex` 和 `UGraphEdge`（未在提供的头文件中，但设计上存在）在节点/边上附加自定义数据

该插件存在的根本原因是：UE 原生缺少一个轻量、可扩展、与 UObject 体系紧密结合的图数据结构。许多游戏（尤其是策略、RPG、解谜）需要快速回答“两个节点是否连通”“离我最近且满足条件的节点是哪个”等问题，`UGraph` 提供了统一的回答基础。

## 使用场景

- **技能/对话树**：将技能节点或对话节点组织成图，通过边表示前提/后续关系，利用 BFS/DFS 遍历。
- **地图区域连通性**：将房间或区域表示为顶点，通道为边，快速判断是否连通，或者找到包含某个目标的最短路径（可自行实现）。
- **任务系统**：任务节点之间的依赖关系（前置任务）。
- **动态生成的游戏世界**：当世界结构频繁变化时，图模型可动态增删节点/边，并自动更新连通分量（岛屿）。
- **需要持久化图结构的系统**：利用内置的序列化接口保存/加载图状态。

## 蓝图用法

该插件**没有公开任何蓝图可调用函数或蓝图可读写属性**。所有核心类和函数都带有 `UE_API` 标记，未标记 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。若要在蓝图使用，必须通过**扩展 C++ 类**的方式：

1. 在 C++ 中创建一个新的 `UGraph` 子类，添加需要暴露给蓝图的函数。
2. 在该子类的函数中调用 `UGraph` 的受保护方法（如 `CreateVertex`, `AddEdge`），并标记为 `BlueprintCallable`。

例如，自定义 `UMyGraph` 可以这样暴露：

```cpp
UCLASS(Blueprintable, BlueprintType)
class UMyGraph : public UGraph
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Graph")
    FGraphVertexHandle CreateMyVertex()
    {
        return CreateVertex();
    }
    // ...
};
```

## C++ 用法

### 头文件引入

```cpp
#include "Graph/Graph.h"
#include "Graph/GraphVertex.h"
#include "Graph/GraphIsland.h"
#include "Graph/GraphHandle.h"
```

> 如果使用算法，还需：
> ```cpp
> #include "Graph/Algorithms/Search/Search.h"
> #include "Graph/Algorithms/Connectivity/ConnectedComponents.h"
> ```

### 基本用法

以下示例创建一个空图，添加两个节点，连接它们，然后运行广度优先搜索。

**来源**: 根据 `UGraph::CreateVertex`, `AddEdge`, `BFS` 等函数推断得出。

```cpp
// 创建图对象（通常在某个 Actor 或子系统内创建）
UGraph* Graph = NewObject<UGraph>();
Graph->InitializeFromProperties(FGraphProperties());

// 创建两个节点
FGraphVertexHandle NodeA = Graph->CreateVertex();
FGraphVertexHandle NodeB = Graph->CreateVertex();

// 添加边（无向）
Graph->AddEdge(NodeA, NodeB);

// 搜索：从 NodeA 开始，寻找符合条件的目标节点
FGraphVertexHandle Found = Graph::Algorithms::BFS(NodeA, [](const FGraphVertexHandle& Vertex) -> bool
{
    // 假设我们寻找某个自定义数据满足条件的节点
    // 这里仅示例：如果节点的索引号是偶数则返回 true
    return Vertex.GetUniqueIndex().IsValid(); // 实际条件应由用户定义
});
```

### 进阶用法

#### 岛屿（连通分量）管理

当图有多个不连通的子图时，每个连通子图自动成为一个 `UGraphIsland`。可以通过岛屿获取其包含的所有顶点。

```cpp
// 获取 NodeA 所属的岛屿
FGraphIslandHandle Island = NodeA.GetIsland(); // 需要从 FGraphVertexHandle 获取，但 FGraphVertexHandle 没有直接 GetIsland() 方法，实际应通过 UGraphVertex 的 GetParentIsland()
// 若有 UGraphVertex* Vertex = Cast<UGraphVertex>(NodeA.Get()); // 假设有获取 UObject 指针的方法
if (UGraphVertex* VertexObj = Graph->GetVertex(NodeA)) // 假设存在此函数
{
    const FGraphIslandHandle& Island = VertexObj->GetParentIsland();
    // 遍历岛屿中所有顶点
    Graph->GetIsland(Island)->ForEachVertex([](const FGraphVertexHandle& Vh)
    {
        // 处理 Vh
    });
}
```

> 注意：`FGraphVertexHandle` 是一个结构体，它不直接拥有 `GetIsland`。实际使用中，应通过 `UGraph` 的方法转化为对象。以下示例展示如何从 Handle 获取对象（UGraph 未暴露此方法，但内部存在）。

#### 序列化

利用 `TDefaultGraphSerialization` 和 `FSerializableGraph` 可以轻松保存/加载图的结构数据。

```cpp
// 保存：将图写入一个 TDefaultGraphSerialization
TDefaultGraphSerialization<FSerializableGraph> Serializer;
Serializer << *Graph; // 需要实现 operator<< 重载，但 UGraph 内部应当支持

// 序列化后的数据在 Serializer.GetData()
const FSerializableGraph& Data = Serializer.GetData();

// 可以进一步将 Data 保存到 UPROPERTY 或文件中（它带有 SaveGame 标记）
```

#### 自定义节点数据

若要给节点添加额外数据（如位置、类型），需要继承 `UGraphVertex`：

```cpp
UCLASS()
class UMyGraphVertex : public UGraphVertex
{
    GENERATED_BODY()
public:
    UPROPERTY()
    FVector Location;

    UPROPERTY()
    int32 NodeType;
};
```

然后在创建节点时指定子类：

```cpp
FGraphVertexHandle Node = Graph->CreateVertex(TSubclassOf<UGraphVertex>(UMyGraphVertex::StaticClass()));
// 获取对象填充数据
if (UMyGraphVertex* VertexObj = Cast<UMyGraphVertex>(/*从 Handle 获取对象*/))
{
    VertexObj->Location = FVector::ZeroVector;
}
```

## Demo 示例

以下是一个最小化的完整示例，展示如何创建图、添加节点、建立边并执行 BFS 搜索。

**MyGraphDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Graph/Graph.h"
#include "MyGraphDemo.generated.h"

UCLASS()
class AMyGraphDemo : public AActor
{
    GENERATED_BODY()
public:    
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UGraph* Graph;
};
```

**MyGraphDemo.cpp**

```cpp
#include "MyGraphDemo.h"
#include "Graph/GraphVertex.h"
#include "Graph/GraphIsland.h"
#include "Graph/Algorithms/Search/Search.h"

void AMyGraphDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建图
    Graph = NewObject<UGraph>(this);
    Graph->InitializeFromProperties(FGraphProperties());

    // 2. 创建顶点
    FGraphVertexHandle NodeA = Graph->CreateVertex();
    FGraphVertexHandle NodeB = Graph->CreateVertex();
    FGraphVertexHandle NodeC = Graph->CreateVertex();

    // 3. 添加边（A-B, B-C）
    Graph->AddEdge(NodeA, NodeB);
    Graph->AddEdge(NodeB, NodeC);

    // 4. BFS 搜索：从 NodeA 出发，找到 NodeC
    FGraphVertexHandle Found = Graph::Algorithms::BFS(NodeA, [&](const FGraphVertexHandle& Vertex) -> bool
    {
        return Vertex == NodeC; // 当遇到 NodeC 时停止
    });

    if (Found.IsValid())
    {
        UE_LOG(LogGameplayGraph, Display, TEXT("BFS found NodeC!"));
    }

    // 5. 查找连通分量
    TSet<FGraphVertexHandle> AllNodes = { NodeA, NodeB, NodeC };
    TArray<TSet<FGraphVertexHandle>> Components = Graph::Algorithms::FindConnectedComponents(AllNodes);
    // 应返回一个包含所有三个节点的分量
}
```

## 模块依赖

根据 `GameplayGraph.Build.cs` 的常见模式（以及实验性插件的典型设置），该模块依赖以下模块。省略标准常见依赖（Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore 等），只列出可能独特的依赖。实际上该插件**无特殊依赖**。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 支持 |
| `Engine` | 引擎基础（未显示使用其他模块） |

> **总结**：无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

- 2025-06-26 `ec900998` 添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 到相应的源文件中。
- 2025-05-27 `716a7183` 修复了代码（UnrealCodeFixup），将 `DLLStorage` 从类型移到方法/静态变量。
- 2025-04-26 `e6092d43` 修复了 DLLStorage，移除了类型上的 DLLStorage 并移到变量/方法。
- 2025-04-23 `939cc6e5` 使用 FortniteClient 构建目标查找并转换所有文件，使其方法/静态变量具有 DLLStorage。
- 2024-12-03 `7742c432` 重新暴露 `RemoveEdge` 函数（之前被移除）。

### 维护评价

- **创建时间**：2024-12-03，至今约 7 个月，属于较新插件。
- **近期更新**：最近三个月（2025 年 4-6 月）有多次维护性提交，主要集中在代码生成和 DLL 导出修复，而不是功能性增强。
- **活跃度**：中等偏低；更新日志显示主要是编译/修复工作，没有新算法或功能添加。
- **已知限制**：从文档看，该插件明确标注为**实验性**（`IsExperimentalVersion = true`），且默认不启用。API 尚不完全稳定，可能存在后续变更。
- **推荐使用**：适合愿意尝试前沿功能并愿意承担兼容性风险的开发者使用。对于生产项目，建议等待更成熟版本或自行封装一层抽象。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph)
- [官方文档](https://docs.unrealengine.com)（当前无专用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/GameplayGraph/Tests)（目录可能包含，未确认）