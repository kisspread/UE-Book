# DataflowAgent

> AI Agent toolset for editing Dataflow graphs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataflowAgent` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataflowAgent) | |

## 用途

DataflowAgent 插件为 Unreal Engine 的 Dataflow 图编辑提供了一套 AI 代理工具集。它解决的核心问题是：如何让 AI 助手能够理解、创建和编辑用于模拟（Simulation）和变形（Deformation）的 Dataflow 图。Dataflow 图通常包含复杂的节点和连接关系，手动编辑繁琐。此插件通过暴露一系列标准化的操作（如创建图、添加节点、连接引脚）作为 AI 可调用的工具，使得 AI 代理能够自动化地生成和修改这些图，从而辅助用户进行程序化内容生成或复杂模拟的搭建。

## 使用场景

- 你需要快速搭建一个用于几何体破碎模拟的 Dataflow 图，但手动拖拽节点和连接过于耗时 → 使用此插件让 AI 代理根据你的描述自动生成图结构。
- 你正在开发一个程序化资产生成管线，需要批量创建具有相似结构的 Dataflow 图 → 使用此插件通过脚本或 AI 代理批量生成。
- 你想探索不同 Dataflow 节点组合的效果，但不想手动反复调整 → 使用此插件让 AI 代理根据你的目标（如“创建一个产生球形碎片的效果”）来尝试不同的节点配置。

## 蓝图用法

此插件的核心功能主要通过 `UDataflowAgentToolset` 类暴露，其函数标记为 `AICallable`，主要设计为供 AI 代理框架调用，而非传统的蓝图节点。`UDataflowGraphEditingSkill` 类定义了 AI 技能，可能在 AI 代理的技能系统中被蓝图引用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateGraph` | 创建一个新的 Dataflow 图资产 | `UDataflowAgentToolset` |
| `GetGraphStructure` | 获取指定 Dataflow 图的完整结构（JSON格式） | `UDataflowAgentToolset` |
| `ListNodeTypes` | 列出所有可用的 Dataflow 节点类型（JSON格式） | `UDataflowAgentToolset` |
| `GetNodeTypeSchema` | 获取指定节点类型的详细信息（引脚、属性等） | `UDataflowAgentToolset` |
| `AddNode` | 向图中添加一个指定类型的节点 | `UDataflowAgentToolset` |
| `ConnectNodes` | 连接两个节点的指定引脚 | `UDataflowAgentToolset` |

### 使用示例（蓝图描述）

由于这些函数主要为 AI 代理设计，在传统蓝图中直接使用的场景有限。更典型的用法是通过 C++ 代码或 AI 代理脚本调用。在蓝图中，你可能会在 AI 代理的技能配置中引用 `UDataflowGraphEditingSkill` 类。

## C++ 用法

### 头文件引入

```cpp
#include "DataflowAgentToolset.h"
#include "DataflowAgentCustomTypes.h"
```

### 基本用法

以下示例展示了如何使用 `UDataflowAgentToolset` 的静态函数来创建一个简单的 Dataflow 图并添加节点。

```cpp
// 假设在某个编辑器工具或命令中
#include "DataflowAgentToolset.h"

void CreateSimpleDataflowGraph()
{
    // 1. 创建一个新的 Dataflow 图
    FString GraphPath = UDataflowAgentToolset::CreateGraph(TEXT("MySimulationGraph"), TEXT("/Game/Dataflow"));
    if (GraphPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Dataflow graph."));
        return;
    }

    // 2. 加载创建的图资产 (需要知道如何加载 UDataflow 资产，此处为示意)
    // UDataflow* MyGraph = LoadObject<UDataflow>(nullptr, *GraphPath);

    // 3. 列出可用的节点类型
    FString NodeTypesJson = UDataflowAgentToolset::ListNodeTypes(true);
    UE_LOG(LogTemp, Log, TEXT("Available node types: %s"), *NodeTypesJson);

    // 4. 获取某个节点类型的详细信息
    FString SchemaJson = UDataflowAgentToolset::GetNodeTypeSchema(TEXT("FAddFloatsDataflowNode"));
    UE_LOG(LogTemp, Log, TEXT("Node schema: %s"), *SchemaJson);

    // 5. 向图中添加节点 (需要有效的 UDataflow* 指针)
    // UDataflowEdNode* NewNode = UDataflowAgentToolset::AddNode(MyGraph, TEXT("FAddFloatsDataflowNode"), TEXT("AddNode_1"), TEXT("{}"), 100, 100);
}
```

### 进阶用法

结合多个操作，构建一个包含连接的小图。

```cpp
void BuildConnectedGraph(UDataflow* Graph)
{
    if (!Graph) return;

    // 添加两个节点
    UDataflowEdNode* NodeA = UDataflowAgentToolset::AddNode(Graph, TEXT("FMakeFloatDataflowNode"), TEXT("ConstValue"), TEXT("{\"Value\": 5.0}"), 0, 0);
    UDataflowEdNode* NodeB = UDataflowAgentToolset::AddNode(Graph, TEXT("FAddFloatsDataflowNode"), TEXT("Adder"), TEXT("{}"), 300, 0);
    UDataflowEdNode* NodeC = UDataflowAgentToolset::AddNode(Graph, TEXT("FPrintStringDataflowNode"), TEXT("Printer"), TEXT("{}"), 600, 0);

    if (NodeA && NodeB && NodeC)
    {
        // 连接节点：将 ConstValue 的输出连接到 Adder 的第一个输入
        UDataflowAgentToolset::ConnectNodes(Graph, TEXT("ConstValue"), TEXT("Value"), TEXT("Adder"), TEXT("A"));

        // 连接节点：将 Adder 的输出连接到 Printer 的输入
        UDataflowAgentToolset::ConnectNodes(Graph, TEXT("Adder"), TEXT("Result"), TEXT("Printer"), TEXT("InString"));
    }
}
```

## Demo 示例

以下是一个最小化的编辑器工具类示例，演示如何调用 DataflowAgent 的功能。

```cpp
// MyDataflowTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyDataflowTool.generated.h"

UCLASS()
class UMyDataflowTool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "DataflowTool")
    void CreateDemoGraph();
};

// MyDataflowTool.cpp
#include "MyDataflowTool.h"
#include "DataflowAgentToolset.h"

void UMyDataflowTool::CreateDemoGraph()
{
    // 创建图
    FString Path = UDataflowAgentToolset::CreateGraph(TEXT("DemoGraph"), TEXT("/Game/Demo"));
    if (Path.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("Graph creation failed."));
        return;
    }

    // 此处可以加载图并继续添加节点和连接
    // 为简化示例，仅打印创建成功
    UE_LOG(LogTemp, Log, TEXT("Demo graph created at: %s"), *Path);
}
```

## 模块依赖

从插件的 `.uplugin` 文件和其功能推断，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionPlugin` | 提供几何体集合和破碎模拟相关的 Dataflow 节点基础 |
| `ToolsetRegistry` | 提供 AI 代理工具集（`UToolsetDefinition`）和技能（`UAgentSkill`）的注册框架 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] 调整 UToolsetDefinitions 确定哪些 UFunctions 是工具的方式。
- 2026-04-17 `8c911af5` [回退] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] 调整 UToolsetDefinitions 确定哪些 UFunctions 是工具的方式。
- 2026-04-16 `bf01197f` 将（大部分）ToolsetDefinitions 移动到 Private 目录。
- 2026-04-02 `103f5b7a` [AI 工具集]：将 DataFlowAgent 工具集移动到 Toolsets 目录下。

### 维护评价

- **创建时间**：非常新（2026年4月创建）。
- **最近更新频率**：在创建后两周内有多次提交，主要围绕 AI 工具集框架的调整和重构，表明处于**活跃开发**阶段。
- **维护状态**：**活跃维护中**。作为实验性插件，其API和结构可能随着底层AI代理框架（ToolsetRegistry）的演进而变化。
- **已知限制**：这是一个实验性（`IsExperimentalVersion=true`）且默认禁用的插件，意味着其API不稳定，不建议在生产环境中依赖。
- **推荐使用**：仅推荐用于**实验、原型开发或研究AI辅助内容创作**的场景。不推荐用于需要稳定性的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataflowAgent)
- [官方文档] (无)
- [测试用例] (未在提供的信息中找到明确的测试文件路径)