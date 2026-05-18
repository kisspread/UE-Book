# PCGToolset

> A collection of tools allowing the assistant to create and modify PCG graphs

| 属性 | 值 |
|---|---|
| 中文名 | PCG工具集 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（开发者设置资产） |
| 模块 | `PCGToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PCGToolset) | |

## 用途

PCGToolset 是一个为 AI 助手设计的编程工具集，用于自动化创建和修改 PCG (Procedural Content Generation) 图形。它基于 `ToolsetRegistry` 框架，将一系列 PCG 操作封装成 AI 可调用的函数（标记有 `AICallable` 元数据）。其核心目的是让 AI 模型能够通过一套明确的 API 来理解、构建、调试和执行 PCG 图形，从而实现程序化内容生成的自动化创作。它不是一个面向最终用户的编辑器 UI 插件，而是一个底层的“AI 工具箱”。

## 使用场景

- **AI 辅助内容创作**：你希望集成一个大语言模型（LLM）助手，让它能根据自然语言描述（如“创建一个用于生成城市街区散布的 PCG 图形”）自动生成完整的 PCG 图形资产。
- **自动化工作流**：你需要在测试或构建流水线中，通过脚本批量创建、修改或验证 PCG 图形的正确性。
- **PCG 图形调试与检查**：你需要以编程方式获取 PCG 图形的详细结构（节点、边、参数），用于日志记录或自定义分析。
- **快速原型**：你想通过几行代码快速创建并运行一个 PCG 图形，验证一个程序化生成的想法，而无需手动在编辑器中拖拽节点。

## 蓝图用法

该插件主要通过标记为 `AICallable` 的静态函数暴露功能，这些函数在蓝图中也可用，但设计上更偏向由 AI 系统调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateGraph` | 创建一个空的 PCG 图形资产，并保存到指定路径。 | `UPCGToolset` |
| `GetGraphStructure` | 获取一个 PCG 图形的完整结构信息，包括所有节点、连接、参数和注释。 | `UPCGToolset` |
| `SetGraphParams` | 向指定的 PCG 图形添加或更新用户参数（可覆盖参数）。 | `UPCGToolset` |
| `AddNode` | 在指定 PCG 图形中，根据类型名称创建一个新节点。 | `UPCGToolset` |
| `ConnectPins` | 在两个节点的指定引脚之间创建一条连接边。 | `UPCGToolset` |
| `RunPCGInstantGraph` | 以“即发即忘”模式运行一个 PCG 图形，并传入参数映射。 | `UPCGSpatialToolset` |

### 使用示例（蓝图描述）

1.  **创建并构建一个简单的 PCG 图形**：
    *   调用 `CreateGraph` 创建名为 `MyGraph` 的图形。
    *   调用 `AddNode` 为该图形添加一个 `Surface Sampler` 节点和一个 `Static Mesh Spawner` 节点。
    *   调用 `ConnectPins` 将 `Surface Sampler` 的 `Points` 输出引脚连接到 `Static Mesh Spawner` 的 `Points` 输入引脚。
    *   调用 `SetGraphParams` 设置一个名为 `Mesh` 的图参数，用于指定要生成的网格体。

2.  **检查并运行一个现有图形**：
    *   使用 `GetGraphStructure` 获取 `MyGraph` 的结构，可以将其序列化为 JSON 供 AI 理解。
    *   准备一个参数映射（`TMap<FString, FString>`），包含对 `Mesh` 参数的覆盖值。
    *   调用 `RunPCGInstantGraph`，传入图形和参数映射来执行生成。

## C++ 用法

### 头文件引入

```cpp
#include "PCGToolset.h"          // 主要工具集类
#include "PCGSpatialToolset.h"   // 包含运行图等空间操作
#include "PCGToolsetCustomTypes.h" // 用于 FPCGGraphStructure 等自定义结构体
```

### 基本用法

从测试用例结构推断的典型用法，创建图形资产并添加节点。
```cpp
// 假设在某个编辑器上下文中执行，例如一个自定义的编辑器工具或测试
#include "PCGToolset.h"
#include "PCGToolsetCustomTypes.h"

void CreateSimplePCGGraph()
{
    // 1. 创建一个 PCG 图形资产
    // 路径: /Game/PCG/AutoGenGraph
    UPCGGraph* NewGraph = UPCGToolset::CreateGraph(TEXT("AutoGenGraph"), TEXT("/Game/PCG"));

    if (!NewGraph)
    {
        UE_LOG(LogPCGToolset, Error, TEXT("Failed to create PCG graph."));
        return;
    }

    // 2. 获取图形结构（可选，用于调试或日志）
    FPCGGraphStructure GraphStruct = UPCGToolset::GetGraphStructure(NewGraph);
    UE_LOG(LogPCGToolset, Log, TEXT("Graph '%s' created with %d nodes."), *GraphStruct.GraphName, GraphStruct.Nodes.Num());

    // 3. 添加一个节点
    // 节点类型名称需要是 PCG 注册的类名或显示名，例如 "Surface Sampler"
    const FString NodeName = TEXT("Surface Sampler");
    UPCGNode* SamplerNode = UPCGToolset::AddNode(NewGraph, NodeName);

    if (SamplerNode)
    {
        UE_LOG(LogPCGToolset, Log, TEXT("Added node: %s"), *SamplerNode->GetName());
    }
}
```

### 进阶用法

结合工具集进行图形参数设置和执行。
```cpp
#include "PCGToolset.h"
#include "PCGSpatialToolset.h"
#include "PCGToolsetCustomTypes.h"

void ConfigureAndRunGraph()
{
    // 假设 Graph 是之前创建或加载的 UPCGGraph 指针
    UPCGGraph* Graph = ...;

    // 1. 设置图参数（添加一个名为 “Density” 的浮点参数）
    TArray<FPCGParamDefinition> ParamDefs;
    FPCGParamDefinition& DensityParam = ParamDefs.AddDefaulted_GetRef();
    DensityParam.Name = TEXT("Density");
    DensityParam.Type = EPCGMetadataTypes::Float;
    DensityParam.Description = TEXT("Controls the density of scattered points.");
    // 可以设置 DefaultValueJson 来指定默认值
    DensityParam.DefaultValueJson = TEXT("0.5");

    bool bSuccess = UPCGToolset::SetGraphParams(Graph, ParamDefs);
    check(bSuccess);

    // 2. 准备参数覆盖值，并执行图形
    TMap<FString, FString> RunParams;
    RunParams.Add(TEXT("Density"), TEXT("0.8")); // 覆盖默认密度

    // 以“即发即忘”模式运行，结果通过返回的异步对象处理（如果关心消息）
    UPCGExecuteGraphInstanceAsyncResult* AsyncResult = UPCGSpatialToolset::RunPCGInstantGraph(Graph, RunParams);
    // 注意：AsyncResult 的生命周期管理需要根据 Async 模式处理。
}
```

## Demo 示例

一个最小化的示例，演示如何在编辑器工具中创建一个 PCG 图形并添加两个节点。
```cpp
// MyPCGGenerator.h
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyPCGGenerator.generated.h"

class UButton;
class UPCGGraph;

UCLASS()
class UMyPCGGenerator : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UButton> GenerateButton;

    UFUNCTION()
    void OnGenerateClicked();

private:
    UPROPERTY()
    TObjectPtr<UPCGGraph> CurrentGraph;
};

// MyPCGGenerator.cpp
#include "MyPCGGenerator.h"
#include "PCGToolset.h"
#include "Components/Button.h"

void UMyPCGGenerator::OnGenerateClicked()
{
    // 使用工具集创建图形
    CurrentGraph = UPCGToolset::CreateGraph(TEXT("MyProceduralForest"));

    if (CurrentGraph)
    {
        // 添加一个 Surface Sampler 节点
        UPCGNode* SamplerNode = UPCGToolset::AddNode(CurrentGraph, TEXT("Surface Sampler"));

        // 添加一个 Static Mesh Spawner 节点
        UPCGNode* SpawnerNode = UPCGToolset::AddNode(CurrentGraph, TEXT("Static Mesh Spawner"));

        // 连接它们的引脚（假设节点已成功创建）
        if (SamplerNode && SpawnerNode)
        {
            UPCGToolset::ConnectPins(SamplerNode, TEXT("Points"), SpawnerNode, TEXT("Points"));
        }

        UE_LOG(LogTemp, Warning, TEXT("PCG Graph '%s' generated with nodes."), *CurrentGraph->GetName());
    }
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段和 `PCGToolsetCustomTypes.h` 的包含可推断：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心 PCG 框架，提供图、节点、设置等基础类。 |
| `ToolsetRegistry` | 提供 `UToolsetDefinition`、`UAgentSkill`、异步调用等 AI 工具集基础架构。 |
| `StructUtils` | 用于 `FInstancedStruct` 和 `FInstancedPropertyBag`。 |

## 维护状态

### 近期更新
```
- 2026-05-14 9de7f591 [PCGToolset] Small code cleanup pass (小范围代码清理)
- 2026-05-14 02299b89 [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties (修复ToolsetRegistry中容器属性更改通知问题)
- 2026-05-13 978a5c16 [Backout] - CL53875137 (回滚一次提交)
- 2026-05-13 e58befb6 [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties (修复容器属性更改通知)
- 2026-05-12 8b443338 Fix a crash where the FToolsetReferenceConverter cannot find the correct Outer to create a new insta (修复FToolsetReferenceConverter崩溃)
```

### 维护评价

- **创建时间**：2026年5月12日，这是一个非常新的插件。
- **最近更新**：提交记录显示，在创建后两天内有多次密集的代码清理和bug修复（包括关键的崩溃修复），表明插件正处于积极的初始开发和完善阶段。
- **维护状态**：**活跃维护中**。作为实验性插件，它正被快速迭代以稳定功能。
- **已知限制**：作为实验性功能，其API和行为可能在未来版本中发生变化。它严重依赖于 `ToolsetRegistry` 框架。
- **推荐使用**：**仅推荐用于研究、实验或集成AI工具链**。不建议用于生产环境项目，除非你愿意接受实验性API的风险并为其未来变化做好准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PCGToolset)
- 官方文档：暂无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：源码目录中包含 `Private/Tests/` 子目录，可用于参考用法。