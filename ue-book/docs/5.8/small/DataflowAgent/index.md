# DataflowAgent

> AI Agent toolset for editing Dataflow graphs

| 属性 | 值 |
|---|---|
| 中文名 | 数据流代理 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataflowAgent` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataflowAgent) | |

## 用途

该插件为 UE5 的 AI Agent（人工智能助手）提供了一套工具集，使其能够以编程方式创建、查询、修改和删除 Dataflow 图表。Dataflow 是 UE5 中用于驱动模拟（如 Chaos Cloth、几何体集合）的基于节点的数据流图。此插件的目的是让 AI 助手能够充当“Dataflow 图表工程师”，自动化图表搭建过程，或根据用户指令进行智能的图表编辑。

## 使用场景

- **AI 辅助内容创作**：你需要 AI 助手帮你快速搭建一个用于 Chaos Cloth 模拟的 Dataflow 流程图。
- **自动化图表生成**：你需要根据一组预定义的规则或模板，通过脚本批量生成或修改多个 Dataflow 资产。
- **教学与探索**：通过 AI 对话，逐步学习 Dataflow 图表中不同节点的功能和连接方式。

## 蓝图用法

本插件的所有函数均标记为 `UFUNCTION(meta=(AICallable))`，这意味着它们主要设计用于 AI Agent 工具调用系统，但同样可以在蓝图（或 C++）中直接调用。所有函数均为静态函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateGraph` | 创建一个新的 Dataflow 图表资产 | `UDataflowAgentToolset` |
| `AddNode` | 向图表中添加一个指定类型的节点 | `UDataflowAgentToolset` |
| `ConnectNodePins` | 连接两个节点的输入输出引脚 | `UDataflowAgentToolset` |
| `UpdateNode` | 通过 JSON 更新节点的属性 | `UDataflowAgentToolset` |
| `GetGraphStructure` | 获取图表的完整结构（JSON 格式） | `UDataflowAgentToolset` |
| `ListNodeTypes` | 列出所有可用的节点类型 | `UDataflowAgentToolset` |
| `AddVariable` | 为图表添加一个变量 | `UDataflowAgentToolset` |
| `CreateDataflowCompatibleAsset` | 创建一个兼容 Dataflow 的资产（如 ChaosClothAsset） | `UDataflowAgentToolset` |
| `AssignDataflowTemplate` | 为资产分配一个预定义的 Dataflow 模板 | `UDataflowAgentToolset` |

### 使用示例（蓝图描述）

1.  创建一个名为 `NewGraph` 的 Dataflow 资产：
    调用 `CreateGraph` 节点，设置 `Name` 为 “NewGraph”，`Path` 为 “/Game/Dataflow”，将返回的路径保存到变量 `GraphAssetPath`。
2.  加载创建的资产：
    使用 `LoadAsset` 节点，输入 `GraphAssetPath`，将输出对象转换为 `UDataflow` 类型，保存为 `MyGraph`。
3.  添加一个加法节点：
    调用 `AddNode` 节点，设置 `Graph` 为 `MyGraph`，`TypeName` 为 “FAddFloatsDataflowNode”，`NodeName` 为 “Add1”，`JsonParams` 为 “{"Value": 1.0}”，`X` 和 `Y` 为 0。
4.  添加一个输出节点：
    再次调用 `AddNode`，类型为 “FPrintDataflowNode”，名称为 “Print1”，位置设为 (200, 0)。
5.  连接节点：
    调用 `ConnectNodePins`，将 `Add1` 节点的 “Out” 引脚连接到 `Print1` 节点的 “In” 引脚。
6.  获取图表结构：
    调用 `GetGraphStructure`，输入 `MyGraph`，可查看当前图表的所有节点和连接信息（JSON 格式）。

## C++ 用法

由于该插件未提供公开的测试用例，且所有 API 均为静态函数，用法相对直接。以下示例展示了如何在编辑器工具或命令中调用这些函数。

### 头文件引入

```cpp
#include “DataflowAgentToolset.h”
```

### 基本用法

```cpp
// 创建一个新的 Dataflow 图表
FString GraphPath = UDataflowAgentToolset::CreateGraph(“AI_SimulationGraph”, “/Game/Dataflow/AI”);
if (!GraphPath.IsEmpty())
{
    // 加载创建的资产
    UDataflow* MyGraph = Cast<UDataflow>(StaticLoadObject(UDataflow::StaticClass(), nullptr, *GraphPath));
    if (MyGraph)
    {
        // 添加一个节点
        UDataflowEdNode* AddNode = UDataflowAgentToolset::AddNode(
            MyGraph,
            TEXT(“FAddFloatsDataflowNode”),
            TEXT(“MyAddNode”),
            TEXT(‘{\”Value\”: 2.5}’),
            100, 100);

        // 添加另一个节点
        UDataflowEdNode* PrintNode = UDataflowAgentToolset::AddNode(
            MyGraph,
            TEXT(“FPrintDataflowNode”),
            TEXT(“MyPrintNode”),
            TEXT(‘{}’),
            300, 100);

        // 连接节点
        if (AddNode && PrintNode)
        {
            UDataflowAgentToolset::ConnectNodePins(AddNode, TEXT(“Out”), PrintNode, TEXT(“In”));
        }

        // 为图表添加一个变量
        UDataflowAgentToolset::AddVariable(MyGraph, TEXT(“BaseValue”), TEXT(“Float”));
        UDataflowAgentToolset::SetVariable(MyGraph, TEXT(“BaseValue”), TEXT(“10.0”));
    }
}
```

### 进阶用法

```cpp
// 创建一个兼容 Dataflow 的资产并应用模板
FString ClothAssetPath = UDataflowAgentToolset::CreateDataflowCompatibleAsset(
    TEXT(“ChaosClothAsset”), // 或 “UChaosClothAsset”
    TEXT(“AI_Cloth”),
    TEXT(“/Game/Characters/Cloth”));

if (!ClothAssetPath.IsEmpty())
{
    UObject* ClothAsset = StaticLoadObject(UObject::StaticClass(), nullptr, *ClothAssetPath);
    // 获取可用于 ChaosClothAsset 的模板列表
    FString TemplatesJson = UDataflowAgentToolset::ListDataflowTemplatesForAssetClass(TEXT(“ChaosClothAsset”));
    // 解析 TemplatesJson 获取 templateId... (假设我们已知一个模板ID)
    FString TemplateIdToApply = TEXT(“ClothSimulation_Default”);
    // 为资产分配模板
    UDataflowAgentToolset::AssignDataflowTemplate(ClothAsset, TemplateIdToApply);
}
```

## Demo 示例

以下是一个简单的编辑器工具命令示例，演示了如何使用 DataflowAgent 创建一个基础图表。

```cpp
// .h
#pragma once

#include “CoreMinimal.h”
#include “EditorUtilityWidget.h”
#include “DataflowAgentToolset.h” // 引入工具集
#include “DataflowDemoWidget.generated.h”

UCLASS()
class UDataflowDemoWidget : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = “Demo”)
    void CreateSimpleDataflowDemo();
};

// .cpp
#include “DataflowDemoWidget.h”
#include “Dataflow/Dataflow.h” // 假设 UDataflow 在此定义

void UDataflowDemoWidget::CreateSimpleDataflowDemo()
{
    // 1. 创建图
    FString GraphPath = UDataflowAgentToolset::CreateGraph(“DemoFlow”, “/Game/Demo”);
    if (GraphPath.IsEmpty()) return;

    UDataflow* DemoGraph = Cast<UDataflow>(StaticLoadObject(UDataflow::StaticClass(), nullptr, *GraphPath));
    if (!DemoGraph) return;

    // 2. 添加节点
    UDataflowEdNode* FloatConstNode = UDataflowAgentToolset::AddNode(
        DemoGraph, TEXT(“FFloatConstantDataflowNode”), TEXT(“Constant1”), TEXT(‘{\”Value\”: 3.14}’), 0, 0);

    UDataflowEdNode* AddNode = UDataflowAgentToolset::AddNode(
        DemoGraph, TEXT(“FAddFloatsDataflowNode”), TEXT(“Adder”), TEXT(‘{}’), 200, 0);

    UDataflowEdNode* PrintNode = UDataflowAgentToolset::AddNode(
        DemoGraph, TEXT(“FPrintDataflowNode”), TEXT(“Output”), TEXT(‘{\”Message\”: \”Result:\”}’), 400, 0);

    // 3. 连接节点
    if (FloatConstNode && AddNode && PrintNode)
    {
        UDataflowAgentToolset::ConnectNodePins(FloatConstNode, TEXT(“Out”), AddNode, TEXT(“A”));
        // 假设我们还有另一个常量或直接连接，这里为演示只连接一边
        UDataflowAgentToolset::ConnectNodePins(AddNode, TEXT(“Out”), PrintNode, TEXT(“In”));
    }

    // 4. 添加注释
    TArray<UDataflowEdNode*> NodesForComment = {FloatConstNode, AddNode, PrintNode};
    UDataflowAgentToolset::AddCommentBox(DemoGraph, NodesForComment, TEXT(“Demo Calculation Block”));
}
```

## 模块依赖

该插件的 `Build.cs` 文件显示其依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionPlugin` | 提供几何体集合资产及相关功能，是 Dataflow 的主要应用场景之一 |
| `ToolsetRegistry` | 注册和发现 AI 工具集（UToolsetDefinition）的核心框架模块 |

**注意**：该插件是一个**编辑器插件** (`EditorOnly: true`)，只能在编辑器环境中使用，不能打包到运行时。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `c203c966` | Dataflow: add asset creation and support for template assignment and discovery to Datafliow toolset | 为工具集添加了资产创建功能，并增加了对模板分配和发现的支持 |
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 修改了 UToolsetDefinition 识别可调用工具函数的方式 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退了 CL52878047 的更改 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 再次修改工具函数识别逻辑 |
| 2026-04-16 | `bf01197f` | Move (most) ToolsetDefinitions to Private directories. | 将大部分工具集定义文件移动到了 Private 目录 |

### 维护评价

- **创建时间**：2026年4月，非常新的插件。
- **近期活跃度**：最近一次更新在2026年5月，新增了重要功能（资产创建与模板支持），表明插件正处于**活跃开发**阶段。
- **当前状态**：标记为 `IsExperimentalVersion: true`，属于**实验性**插件。功能、接口和稳定性可能随时发生变化。
- **限制与已知问题**：作为实验性插件，其 API 设计和依赖关系尚未完全稳定。使用时需注意版本兼容性问题。
- **推荐使用**：适合对 UE5 AI 工具链感兴趣、且愿意接受实验性功能风险的**开发者或技术美术**进行尝试和学习。**不推荐**用于生产环境或关键项目中，应密切关注其版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataflowAgent)
- 官方文档（暂无）
- 测试用例（暂未发现公开测试用例）