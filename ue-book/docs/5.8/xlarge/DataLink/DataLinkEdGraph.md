# Motion Design Data Link

> 

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (UncookedOnly), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个面向 **Motion Design（动态设计）** 的**节点式数据流图编辑器**系统。它允许用户在蓝图编辑器中通过可视化的节点图来定义数据获取、处理和输出的完整流程。

核心设计理念是将数据链路抽象为可组合的节点（`UDataLinkNode`），通过编辑器图（`UDataLinkEdGraph`）进行可视化编排。系统支持多种数据源（HTTP、WebSocket、JSON、DataTable）并通过统一的图编辑器进行编排，适用于广播级动态图形场景中实时数据驱动内容的需求。

`DataLinkEdGraph` 模块专门负责**编辑器端的图编辑体验**——包括节点的创建、连接、布局以及蓝图集成，是整个 DataLink 系统的可视化编排层。

## 使用场景

- 你在做广播级动态图形（Motion Graphics）→ 需要从外部 API、WebSocket 实时获取数据驱动 UI/3D 内容 → 用 DataLink 编排数据流
- 你需要一个可视化节点图来定义数据获取和转换逻辑，而非编写 C++/蓝图代码 → 用 DataLink 的图编辑器
- 你需要通过 HTTP 或 WebSocket 从外部服务获取实时数据（比分板、股票行情、天气等）→ 用 DataLinkHttp / DataLinkWebSocket 模块
- 你需要将 JSON 数据解析并映射到 Unreal 属性 → 用 DataLinkJson 模块

## 蓝图用法

DataLinkEdGraph 模块本身提供编辑器图功能，同时暴露了蓝图集成节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Async Data Link Request` | 异步执行 DataLink 图，完成后返回输出数据（推荐用法） | `UK2Node_AsyncDataLinkRequest` |
| `Data Link Request` | ~~同步执行 DataLink 请求（已废弃，5.7 起）~~ | `UK2Node_DataLinkRequest` |

### 编辑器图操作

DataLink 图编辑器中的核心操作：

1. **创建节点**：在图中右键，可通过上下文菜单创建原生节点（Native Node）或脚本节点（Script Node）
2. **连接引脚**：拖拽引脚进行连接，系统会自动检测连接兼容性并防止环路（Loop Detection）
3. **输出节点**：每个 DataLink 图有一个固定的"Output"节点（`UDataLinkEdOutputNode`），标记图的最终输出

### 使用示例（蓝图描述）

**异步数据链路请求**（推荐）：
1. 从蓝图中拖出 `Async Data Link Request` 节点
2. 连接 `Data Link Instance` 引脚 → 指定要执行的 DataLink 图资产
3. 连接 `Execution Context` 引脚 → 提供执行上下文
4. 连接 `Data Link Sink Provider` 引脚 → 指定数据接收者
5. `On Output Data` 输出引脚 → 连接后续处理逻辑，获取实时输出数据

**注意**：`UK2Node_DataLinkRequest` 已在 5.7 版本废弃，改用 `UK2Node_AsyncDataLinkRequest` 或 Data Link Executor Object。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkEdGraph.h"
#include "DataLinkEdNode.h"
#include "DataLinkEdGraphSchema.h"
```

### 基本用法

**遍历节点引脚连接关系**：

```cpp
// 来源: Public/Nodes/DataLinkEdNode.h

// 获取 DataLink 编辑器节点并遍历其引脚连接
UDataLinkEdNode* EdNode = /* 获取节点 */;
EdNode->ForEachPinConnection([](const UEdGraphPin& Pin, const UDataLinkEdNode& ConnectedNode, const UEdGraphPin& ConnectedPin)
{
    // 处理每个引脚连接
    // Pin: 当前节点的引脚
    // ConnectedNode: 连接的另一个节点
    // ConnectedPin: 另一个节点的引脚
    UE_LOG(LogTemp, Log, TEXT("Pin %s connected to %s:%s"), 
        *Pin.PinName.ToString(),
        *ConnectedNode.GetName(),
        *ConnectedPin.PinName.ToString());
});
```

**设置节点模板类并重建节点**：

```cpp
// 来源: Public/Nodes/DataLinkEdNode.h

// 将编辑器节点绑定到特定的 DataLink 节点类型
UDataLinkEdNode* EdNode = /* 获取或创建编辑器节点 */;
TSubclassOf<UDataLinkNode> NodeClass = UMyCustomDataLinkNode::StaticClass();
EdNode->SetTemplateNodeClass(NodeClass, true); // true = 自动重建节点引脚

// 获取底层模板节点
UDataLinkNode* TemplateNode = EdNode->GetTemplateNode();
```

### 进阶用法

**图编译状态检查与节点初始化**：

```cpp
// 来源: Public/DataLinkEdGraph.h

// 获取 DataLink 编辑器图
UDataLinkEdGraph* EdGraph = /* 获取图 */;

// 查找输出节点（用于确定图的最终输出）
UDataLinkEdOutputNode* OutputNode = EdGraph->FindOutputNode();
if (OutputNode)
{
    UEdGraphPin* OutputPin = OutputNode->GetOutputResultPin();
    // 处理输出引脚...
}

// 初始化所有节点（将过时的节点引脚更新为与模板同步）
EdGraph->InitializeNodes();

// 检查编译状态
if (!EdGraph->IsCompiledGraphUpToDate())
{
    // 图有未编译的修改，需要重新编译
    EdGraph->DirtyGraph();
}
```

**连接兼容性与环路检测**：

```cpp
// 来源: Public/DataLinkEdGraphSchema.h

const UDataLinkEdGraphSchema* Schema = EdGraph->GetSchema<UDataLinkEdGraphSchema>();

// 检测连接是否会导致环路
bool bWouldLoop = Schema->IsConnectionLooping(InputPin, OutputPin);
if (bWouldLoop)
{
    UE_LOG(LogTemp, Warning, TEXT("Connection would create a loop!"));
}
```

## Demo 示例

### 自定义 DataLink 编辑器节点

```cpp
// MyCustomEdNode.h
#pragma once

#include "CoreMinimal.h"
#include "Nodes/DataLinkEdNode.h"
#include "MyCustomEdNode.generated.h"

UCLASS()
class UMyCustomEdNode : public UDataLinkEdNode
{
    GENERATED_BODY()

public:
    // 自定义节点标题颜色
    virtual FLinearColor GetNodeTitleColor() const override
    {
        return FLinearColor(0.2f, 0.8f, 0.4f);
    }

    virtual FText GetNodeTitle(ENodeTitleType::Type InTitleType) const override
    {
        return NSLOCTEXT("MyCustom", "Title", "Custom Data Source");
    }
};
```

```cpp
// MyCustomEdNode.cpp
#include "MyCustomEdNode.h"
```

### 自定义图 Schema 操作

```cpp
// MyGraphUtils.h
#pragma once

#include "CoreMinimal.h"
#include "DataLinkEdGraph.h"
#include "DataLinkEdNode.h"
#include "DataLinkEdOutputNode.h"

class FMyGraphUtils
{
public:
    /** 验证 DataLink 图的完整性 */
    static bool ValidateGraph(UDataLinkEdGraph* InGraph)
    {
        if (!InGraph) return false;

        // 1. 检查是否存在输出节点
        UDataLinkEdOutputNode* OutputNode = InGraph->FindOutputNode();
        if (!OutputNode)
        {
            UE_LOG(LogTemp, Error, TEXT("DataLink Graph is missing an Output node"));
            return false;
        }

        // 2. 检查输出节点是否已连接
        UEdGraphPin* OutputResultPin = OutputNode->GetOutputResultPin();
        if (!OutputResultPin || OutputResultPin->LinkedTo.Num() == 0)
        {
            UE_LOG(LogTemp, Warning, TEXT("Output node has no connected input"));
            return false;
        }

        // 3. 检查编译状态
        if (!InGraph->IsCompiledGraphUpToDate())
        {
            UE_LOG(LogTemp, Warning, TEXT("Graph has uncompiled changes"));
            InGraph->DirtyGraph();
        }

        return true;
    }

    /** 收集图中所有节点的连接拓扑 */
    static void CollectNodeTopology(UDataLinkEdGraph* InGraph, 
        TMap<FName, TArray<FName>>& OutConnections)
    {
        if (!InGraph) return;

        for (UEdGraphNode* RawNode : InGraph->Nodes)
        {
            UDataLinkEdNode* DataNode = Cast<UDataLinkEdNode>(RawNode);
            if (!DataNode) continue;

            TArray<FName> ConnectedNames;
            DataNode->ForEachPinConnection(
                [&ConnectedNames](const UEdGraphPin& Pin, 
                    const UDataLinkEdNode& ConnectedNode, 
                    const UEdGraphPin& ConnectedPin)
                {
                    ConnectedNames.Add(FName(*ConnectedNode.GetName()));
                });

            OutConnections.Add(FName(*DataNode->GetName()), ConnectedNames);
        }
    }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该模块依赖 UnrealEd 编辑器图基础设施（UEdGraph / UEdGraphSchema / UEdGraphNode），这些属于引擎标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString 双类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF 新宏 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复 FJsonObject 中的字符串重复问题以释放内存 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以减少内存占用 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退变更 CL51209244 |

### 维护评价

- **创建时间**：2025-08-27，约 1 年前
- **Beta 状态**：`IsBetaVersion = true`，尚处于测试阶段
- **从实验区迁移**：首次提交即为从 Experimental 目录迁移到 VirtualProduction 目录（JIRA: UE-314973, UE-314972），说明已通过初步评审
- **近期活跃度**：2026 年 2-4 月有持续更新，集中在性能优化（内存）和代码规范化
- **模块类型**：DataLinkEdGraph 为 UncookedOnly 类型，仅在编辑器和开发环境中加载
- **已废弃节点**：`UK2Node_DataLinkRequest` 在 5.7 被废弃，建议使用 Data Link Executor Object

**评价**：该插件处于活跃开发中，属于 Epic 官方维护的 Motion Design 工具链的一部分。虽然标记为 Beta，但更新频率稳定。推荐在 Motion Design / Virtual Production 工作流中使用，但需注意 API 可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)