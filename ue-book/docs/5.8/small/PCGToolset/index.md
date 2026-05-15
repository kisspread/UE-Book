# PCGToolset

> A collection of tools allowing the assistant to create and modify PCG graphs

| 属性 | 值 |
|---|---|
| 中文名 | PCG工具集 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PCGToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PCGToolset) | |

## 用途

PCGToolset 是一套面向 AI 助手的工具集，旨在通过程序化接口（而非图形化编辑器）来创建、查询和修改程序化内容生成（PCG）图。它解决了 AI 助手无法直接操作 PCG 编辑器的问题，使其能够根据用户指令自动生成或调整 PCG 散布规则、修改图参数、执行图实例，并检查执行结果。核心功能包括：创建新 PCG 图、添加和连接各类 PCG 节点、管理图参数与实例、以及查看节点输出数据。

## 使用场景

-   **AI 生成 PCG 内容**：AI 助手根据用户描述（如“生成一片森林”），自动创建包含 Surface Sampler、Static Mesh Spawner 等节点的 PCG 图，并连接它们。
-   **程序化修改现有规则**：通过代码或 AI 调整现有 PCG 图中节点的参数（如密度、缩放范围），而不必手动打开编辑器。
-   **批量执行与检查**：在场景中生成多个 PCG Volume 实例，批量执行并收集执行过程中的警告或错误信息。
-   **数据探查**：在执行 PCG 图后，检查特定节点输出的数据内容（如点位置、属性值），用于调试或数据验证。

## 蓝图用法

所有功能均通过 `UPCGToolset` 和 `UPCGSpatialToolset` 类的静态函数暴露，这些函数标记为 `AICallable`，专供 AI 工具系统调用。

### 核心节点

#### 图操作
| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateGraph` | 在指定路径创建一个新的 PCG 图资产 | `UPCGToolset` |
| `GetGraphStructure` | 获取图的完整结构信息（节点、边、参数） | `UPCGToolset` |
| `ListGraphInstances` | 列出场景中所有带有 PCG 图实例的 Actor | `UPCGToolset` |
| `SpawnGraphInstance` | 在场景中生成一个 PCG Volume 及其图实例 | `UPCGToolset` |
| `RunPCGInstantGraph` | 立即执行一个即时 PCG 图（一次性，不保存实例） | `UPCGSpatialToolset` |

#### 图参数
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGraphSchema` | 获取图的模式信息（参数、输入/输出引脚） | `UPCGToolset` |
| `SetGraphParams` | 向图添加用户可覆盖的参数 | `UPCGToolset` |
| `RemoveGraphParams` | 从图中移除参数 | `UPCGToolset` |
| `GetGraphDescription` / `SetGraphDescription` | 获取/设置图的描述文本 | `UPCGToolset` |

#### 图实例参数
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGraphInstanceParams` | 获取特定图实例（PCGVolume）的当前参数值 | `UPCGToolset` |
| `SetGraphInstanceParams` | 设置图实例的参数覆盖值 | `UPCGToolset` |
| `ResetGraphInstanceParams` | 将图实例的指定参数重置为图定义的默认值 | `UPCGToolset` |
| `ExecuteGraphInstance` | 执行图实例并返回执行消息（错误/警告） | `UPCGToolset` |

#### 节点操作
| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListNativeNodes` | 列出可用的原生 PCG 节点类型 | `UPCGToolset` |
| `ListAvailableSubgraphs` | 列出可用于“子图”节点的 PCG 图资产 | `UPCGToolset` |
| `GetNativeNodeSchema` | 获取特定原生节点类型的详细模式（参数、引脚） | `UPCGToolset` |
| `AddNode` / `AddSubgraphNode` | 向图中添加原生节点或子图节点 | `UPCGToolset` |
| `ConnectNodePins` / `DisconnectNodePins` | 连接或断开两个节点之间的引脚 | `UPCGToolset` |
| `UpdateNode` | 更新节点的参数或标题 | `UPCGToolset` |
| `RemoveNode` | 从图中移除一个节点及其所有连接 | `UPCGToolset` |
| `RepositionNode` | 在编辑器中移动节点的位置 | `UPCGToolset` |

#### 数据查看
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNodeDataView` | 查看节点在最近一次执行后输出的 JSON 数据 | `UPCGToolset` |

#### 注释框与辅助
| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddCommentBox` / `UpdateCommentBox` / `RemoveCommentBox` | 管理围绕节点的注释框 | `UPCGToolset` |
| `DrawSpline` | （异步）提示用户在视口中绘制样条线以用于世界构建 | `UPCGToolset` |

### 使用示例（蓝图描述）

1.  **创建一个简单的散布图**：
    -   调用 `CreateGraph` 创建名为 “MyForest” 的图。
    -   调用 `AddNode` 添加 “Surface Sampler” 节点，设置相关参数。
    -   调用 `AddNode` 添加 “Static Mesh Spawner” 节点，指定要散布的网格体。
    -   调用 `ConnectNodePins` 将 Sampler 的 “Out” 引脚连接到 Spawner 的 “In” 引脚。
    -   调用 `SpawnGraphInstance` 在场景中生成此图的实例。

2.  **调整现有实例的参数**：
    -   调用 `ListGraphInstances` 获取场景中的图实例列表。
    -   对某个实例调用 `GetGraphInstanceParams` 查看当前参数。
    -   调用 `SetGraphInstanceParams` 并传入 JSON 字符串（如 `{"Density": 5.0}`）来修改密度。
    -   调用 `ExecuteGraphInstance` 执行并检查返回的 `FPCGNodeExecutionMessage` 数组以确认是否成功。

## C++ 用法

此插件主要设计为通过 AI 工具系统调用，直接在 C++ 中使用的场景较少，但其底层库 `PCGToolsetLibrary` 提供了一些通用功能。

### 头文件引入

```cpp
#include "PCGToolset.h" // 主要工具定义类
#include "PCGToolsetLibraryCore.h" // 核心辅助函数库
#include "PCGToolsetCustomTypes.h" // 自定义数据结构
```

### 基本用法

从测试用例中提取的模式，用于创建临时图并添加节点。

```cpp
// 来源: Tests/PCGToolsetTestFixture.h
#include "PCGToolsetTestFixture.h"

// 创建一个用于测试的瞬态图
UPCGGraph* TestGraph = PCGToolsetTest::MakeTransientGraph(FName("MyTestGraph"));

// 使用 PCGToolsetLibrary 中的函数获取节点信息
TArray<FPCGNodeInfo> NodesInfo = PCGToolsetLibrary::Graph::GetGraphNodesInfo(TestGraph);
```

### 进阶用法

使用 `PCGToolsetLibrary::Graph` 命名空间下的函数处理图参数和JSON转换。

```cpp
#include "PCGToolsetLibraryCore.h"

// 解析 JSON 字符串
FString JsonString = TEXT("{\"Param1\": 1.0, \"Param2\": \"Text\"}");
TSharedPtr<FJsonObject> JsonObject = PCGToolsetLibrary::Json::ParseJson(JsonString);

// 获取图的用户参数（过滤掉内部参数）
const UPCGGraph* MyGraph = ...; // 假设已有一个图
FInstancedPropertyBag UserParams = PCGToolsetLibrary::Graph::GetGraphParams(MyGraph);

// 应用 JSON 参数到图实例
UPCGGraphInstance* MyGraphInstance = ...;
bool bSuccess = PCGToolsetLibrary::Graph::SetGraphInstanceParams(MyGraphInstance, JsonString);
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何使用 PCGToolset 库在代码中创建一个新 PCG 图。

```cpp
// PCGToolsetDemo.h
#pragma once
#include "CoreMinimal.h"

class FPCGToolsetDemo
{
public:
    static void CreateDemoGraph();
};
```

```cpp
// PCGToolsetDemo.cpp
#include "PCGToolsetDemo.h"
#include "PCGToolset.h"
#include "PCGGraph.h"

void FPCGToolsetDemo::CreateDemoGraph()
{
    // 1. 创建一个新的PCG图资产
    UPCGGraph* DemoGraph = UPCGToolset::CreateGraph(TEXT("DemoForest"), TEXT("/Game/PCG/Demos"));
    if (!DemoGraph)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create PCG graph."));
        return;
    }

    // 2. 添加一个Surface Sampler节点
    FString SamplerNodeName = TEXT("Sampler");
    // 参数通过Json字符串设置，这里使用默认参数
    FString SamplerParams = TEXT("{}"); 
    UPCGNode* SamplerNode = UPCGToolset::AddNode(
        DemoGraph,
        TEXT("Surface Sampler"), // 原生节点类型名
        SamplerNodeName,
        SamplerParams,
        TEXT("Sampler"), // 标题
        TEXT("Samples points on a surface"), // 注释
        0, // X位置
        0  // Y位置
    );

    // 3. 添加一个Static Mesh Spawner节点
    FString SpawnerNodeName = TEXT("Spawner");
    // 设置要生成的静态网格体资产路径
    FString SpawnerParams = TEXT("{\"StaticMesh\": \"/Game/Meshes/MyTree\"}");
    UPCGNode* SpawnerNode = UPCGToolset::AddNode(
        DemoGraph,
        TEXT("Static Mesh Spawner"),
        SpawnerNodeName,
        SpawnerParams,
        TEXT("Spawn Trees"),
        TEXT(""),
        400, // X位置
        0
    );

    // 4. 连接两个节点
    if (SamplerNode && SpawnerNode)
    {
        UPCGToolset::ConnectNodePins(SamplerNode, TEXT("Out"), SpawnerNode, TEXT("In"));
        UE_LOG(LogTemp, Log, TEXT("Demo graph '%s' created and nodes connected."), *DemoGraph->GetName());
    }
}
```

## 模块依赖

从插件的 `PCGToolset.Build.cs` 及其依赖的插件声明可知，使用此插件需要以下独特的依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | 提供 PCG 图、节点、设置、Volume 等核心框架和功能 |
| `ToolsetRegistry` | 提供工具集注册、JSON 转换器基础类、AI 可调用函数标记等基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9de7f591` | [PCGToolset] Small code cleanup pass | 对PCGToolset插件进行了一次小规模的代码清理 |
| 2026-05-14 | `02299b89` | [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties | 修复了ToolsetRegistry中设置对象属性时发出的容器更改通知不正确的问题 |
| 2026-05-13 | `978a5c16` | [Backout] - CL53875137 | 回滚了之前的某个提交CL53875137 |
| 2026-05-13 | `e58befb6` | [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties | （同上，可能是同一修复的不同分支提交） |
| 2026-05-12 | `8b443338` | Fix a crash where the FToolsetReferenceConverter cannot find the correct Outer to create a new insta | 修复了一个崩溃：当FToolsetReferenceConverter无法找到正确的Outer来创建新实例时导致的崩溃 |

### 维护评价

-   **活跃维护**：插件创建于 **2026-04-27**，是一个非常新的插件。从 git 历史看，最近一次提交在 **2026-05-14**，距今（以当前 2025 年模拟）时间很近，且包含功能性清理和 Bug 修复，表明处于 **活跃维护** 阶段。
-   **实验性状态**：插件明确标记为 `IsExperimentalVersion: true` 且默认不启用。这意味着其 API 和功能可能会发生变化，不建议用于生产项目的核心部分。
-   **依赖关系**：它依赖于同样可能处于实验性的 `ToolsetRegistry` 插件，增加了使用的复杂性。
-   **推荐使用**：如果你正在开发**面向 AI 助手的 PCG 内容生成工具**，并且愿意接受实验性 API 的变动，那么此插件提供了必要的底层能力。对于常规的游戏内容开发者，应优先使用 PCG 编辑器本身。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PCGToolset)
-   [官方文档]() （无）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PCGToolset/Source/PCGToolset/Private/Tests)