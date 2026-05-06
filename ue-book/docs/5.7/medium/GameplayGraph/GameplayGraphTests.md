# Gameplay Graph

> A graph representation model and common graph alogrithms that can be used for gameplay.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏玩法图 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph) | |

## 用途

GameplayGraph 提供了一套通用的图表示模型和基础图算法（如全连接边构建、线性边构建、岛屿划分等），专门为游戏逻辑场景设计。它解决了在游戏中管理实体间复杂连接关系的需求，例如资源运输网络、领土占领链路、对话树、关系图谱等。与一般图库不同，它原生集成到 UE 的对象系统和内存管理框架中，支持运行时动态构建和操作。

## 使用场景

- **策略游戏**：定义城市之间的道路连接、势力范围边界、单位移动路径限制。
- **RPG/冒险游戏**：构建可交互的对话图、技能树升级路径、物品合成配方网络。
- **模拟经营**：管理生产线上的资源流转路径、员工社交网络、任务依赖关系。
- **多人对战**：实时计算队伍间通讯拓扑、玩家配对图、地图区域可达性。

## 蓝图用法

由于本插件仍处于**实验性**阶段，目前并未暴露出大量可直接在蓝图使用的函数节点。以下是根据代码推断的、常用于蓝图的核心操作（实际可用节点以插件版本为准）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Graph` | 创建一个新的图对象 | `UGraph` |
| `Add Vertex` | 向图中添加一个顶点，返回其句柄 | `UGraph` |
| `Add Edge` | 在两个顶点之间添加一条边 | `UGraph` |
| `Remove Edge` | 移除一条指定的边 | `UGraph` |
| `Get Edges for Vertex` | 获取与指定顶点相连的所有边 | `UGraph` |
| `Finalize Vertices` | 完成顶点添加，固化内部索引 | `UGraph` |
| `Finalize Edges` | 完成边添加，固化连接数据 | `UGraph` |

### 使用示例（蓝图描述）

1. 在关卡蓝图中创建 `UGraph` 对象（使用“Spawn Actor from Class”或“Construct Object from Class”）。
2. 调用 `Add Vertex` 多次生成多个顶点，并将返回的 `FGraphVertexHandle` 存入变量。
3. 调用 `Add Edge` 依次连接顶点（需指定两个顶点的句柄）。
4. 所有顶点和边添加完成后，依次调用 `Finalize Vertices` 和 `Finalize Edges` 固化数据。
5. 使用 `Get Edges for Vertex` 查询某个顶点的邻居边，用于游戏逻辑判断。

> ⚠️ 注意：蓝图中直接使用 `FGraphVertexHandle` 等结构可能需要额外转换步骤，建议在 C++ 中封装蓝图调用接口。

## C++ 用法

### 头文件引入

```cpp
#include "Graph/Graph.h"
```

### 基本用法

从测试模块 `Tests/TestGraphBuilder.cpp` 提取的典型构建流程：

```cpp
// 创建图对象
UGraph* MyGraph = NewObject<UGraph>();

// 添加顶点（返回句柄）
TArray<FGraphVertexHandle> Vertices;
constexpr int32 NumVertices = 10;
for (int32 i = 0; i < NumVertices; ++i)
{
    FGraphVertexHandle Vertex = MyGraph->AddVertex();
    Vertices.Add(Vertex);
}

// 构建全连接边（演示构建器模式）
FTestGraphBuilder Builder; // 实际使用中可自定义构建器
Builder.PopulateVertices(NumVertices, false);
for (int32 i = 0; i < NumVertices; ++i)
{
    Builder.BuildFullyConnectedEdges(NumVertices);
}
Builder.FinalizeVertices();
Builder.FinalizeEdges();

// 查询某个顶点的所有边
TArray<FEdgeSpecifier> Edges = MyGraph->GetEdgesForVertex(Vertices[0]);
for (const FEdgeSpecifier& Edge : Edges)
{
    // 处理边信息
}
```

来源：`Engine/Plugins/Experimental/GameplayGraph/Tests/TestGraphBuilder.cpp`（略经简化）

### 进阶用法

使用图岛屿（Island）功能分组顶点，并验证岛屿内部连通性：

```cpp
// 创建两个岛屿，每个岛屿中包含线性连接的顶点
constexpr int32 NodesPerIsland = 5;
TArray<FGraphIslandHandle> Islands;
for (int32 i = 0; i < 2; ++i)
{
    FTestGraphBuilder Builder;
    Builder.PopulateVertices(NodesPerIsland, false);
    Builder.BuildLinearEdges(NodesPerIsland);
    Builder.FinalizeVertices();
    Builder.FinalizeEdges();
    // 从 Builder 中获取岛屿句柄（内部实现）
    // Islands.Add(Builder.GetIslandHandle());
}

// 验证每个岛屿内部顶点到父岛屿的关联正确性
void VerifyIslandSanity(const FGraphIslandHandle& IslandHandle)
{
    // 测试代码中的检查函数，可参考
    // IslandVertexParentIslandSanityCheck(IslandHandle);
}
```

来源于 `TestGraphBuilder::IslandVertexParentIslandSanityCheck`。

## Demo 示例

一个最小化的 C++ 示例，演示创建图、添加边、最终化并检查连通性。

**GraphDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Graph/Graph.h"

DECLARE_LOG_CATEGORY_EXTERN(LogGraphDemo, Log, All);

class FGraphDemo
{
public:
    void RunDemo();
};
```

**GraphDemo.cpp**

```cpp
#include "GraphDemo.h"
#include "Graph/Graph.h"

DEFINE_LOG_CATEGORY(LogGraphDemo);

void FGraphDemo::RunDemo()
{
    // 1. 创建图
    UGraph* DemoGraph = NewObject<UGraph>();

    // 2. 添加 4 个顶点
    TArray<FGraphVertexHandle> Vertices;
    for (int32 i = 0; i < 4; ++i)
    {
        FGraphVertexHandle V = DemoGraph->AddVertex();
        Vertices.Add(V);
        UE_LOG(LogGraphDemo, Log, TEXT("Added vertex %d"), i);
    }

    // 3. 构建线性边 (0-1, 1-2, 2-3)
    for (int32 i = 0; i < Vertices.Num() - 1; ++i)
    {
        DemoGraph->AddEdge(Vertices[i], Vertices[i + 1]);
    }

    // 4. 最终化
    DemoGraph->FinalizeVertices();
    DemoGraph->FinalizeEdges();

    // 5. 验证：顶点1应该有两个邻居（0和2）
    TArray<FEdgeSpecifier> EdgesOfVertex1 = DemoGraph->GetEdgesForVertex(Vertices[1]);
    const int32 ExpectedCount = 2;
    check(EdgesOfVertex1.Num() == ExpectedCount);
    UE_LOG(LogGraphDemo, Log, TEXT("Vertex 1 has %d edges (expected %d)"), EdgesOfVertex1.Num(), ExpectedCount);
}
```

## 模块依赖

使用本插件时，你的项目模块需要在 `Build.cs` 中引用 `GameplayGraph`。该模块自身没有特殊的非标准依赖，仅依赖常见的引擎核心模块。

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine/Slate 等 |

## 维护状态

### 近期更新

- 2025-06-26 `ec900998` — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-05-27 `716a7183` — Fixed up code using UnrealCodeFixup (moved dllstorage from types to methods/static vars...)
- 2025-04-26 `e6092d43` — Fixed dllstorage. Removed dllstorage on types and moved to variables/methods plus removed dllstorage
- 2025-04-23 `939cc6e5` — Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv
- 2024-12-03 `7742c432` — Re-expose the RemoveEdge function in UGraph, which was removed in 31844651 in order to protect against

### 维护评价

- **创建时间**：2024-12-03，距今约 8 个月（实验性插件）。
- **更新频率**：2025 年有多次提交，集中在代码规范（dllstorage 迁移、内联声明）。最后一次功能性提交是 2024-12-03 重新暴露 `RemoveEdge` 函数，显示仍在修复和调整 API。
- **活跃状态**：维护活跃，因为最近 2 个月内仍有编译修复提交。
- **已知问题/限制**：实验性标记，API 可能不稳定；`FGraphVertexHandle`、`FEdgeSpecifier` 等结构体还未提供完整的蓝图暴露；图算法目前仅包含基础构建功能（全连接、线性），高级算法（最短路径、最小生成树）缺失。
- **推荐使用**：可以用于非生产项目或实验性原型；对于正式产品，建议等到插件脱离实验性阶段或自行封装稳定接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph)
- [官方文档](https://docs.unrealengine.com/)（尚未提供专用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayGraph/Tests)