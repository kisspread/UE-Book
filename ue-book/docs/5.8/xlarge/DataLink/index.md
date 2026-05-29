# Motion Design Data Link

> （描述为空）

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计数据链接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途
该插件为 Unreal Engine 的运动设计（Motion Design）系统提供了一个统一、可扩展的**实时数据流框架**。其核心功能是定义、管理和执行数据源与数据目标之间的链接。它解决了从外部系统（如设备、网络API、数据表格等）实时获取数据并驱动场景内对象状态的问题，是构建数据驱动型运动设计内容的基础设施。

## 使用场景
- **实时接收外部设备数据**：通过 `DataLinkWebSocket` 模块连接 WebSocket 服务器，实时控制场景中的灯光、动画或UI元素。
- **调用外部 API**：使用 `DataLinkHttp` 模块发起 HTTP 请求（GET/POST）获取 JSON 数据，并通过 `DataLinkJson` 模块解析后应用到场景属性。
- **基于表格数据驱动**：利用 `DataLinkDataTable` 模块将 UE 的 DataTable 作为数据源，实现批量数据配置和读取。
- **可视化数据链接编辑**：通过 `DataLinkEdGraph` 和 `DataLinkEditor` 模块，在编辑器中使用节点图的方式直观地创建、调试和管理复杂的数据流。

## 蓝图用法
以下为各子模块提供的核心蓝图节点类别：

| 功能类别 | 说明 | 主要类/模块 |
|---|---|---|
| **数据链接源** | 创建和管理数据源，是数据流的起点。 | `UDataLinkSubsystem`, `UDataLinkNode` |
| **HTTP 数据源** | 提供发起 HTTP 请求并处理响应的功能节点。 | `UDataLinkHttpNode` |
| **WebSocket 数据源** | 提供连接 WebSocket 服务器并接收/发送消息的功能节点。 | `UDataLinkWebSocketNode` |
| **JSON 数据处理** | 提供解析 JSON 字符串、提取字段的功能节点。 | `UDataLinkJsonNode` |
| **数据表格源** | 提供从 DataTable 读取数据的功能节点。 | `UDataLinkDataTableNode` |

## C++ 用法
C++ 用法主要围绕创建和定制数据链接源。核心是继承自 `UDataLinkNode` 的基类来实现自定义数据源逻辑。

### 基本用法
创建一个简单的 HTTP 数据链接源（概念示例，实际需结合蓝图或配置）。
*来源：模块 `DataLinkHttp` 的使用模式*

```cpp
// 假设已存在 DataLinkSubsystem
UDataLinkSubsystem* DataLinkSubsystem = GetWorld()->GetSubsystem<UDataLinkSubsystem>();
// 在蓝图或配置中，可创建一个 “DataLinkHttpNode” 并设置其 URL，系统会自动处理请求与数据流
```

### 进阶用法
创建自定义的数据链接节点类，以接入特定协议或数据源。
*来源：模块 `DataLink` 的扩展点设计*

```cpp
// 自定义数据链接节点
UCLASS()
class UMyCustomDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

public:
    // 实现数据获取逻辑
    virtual void FetchData() override
    {
        // ... 从自定义源获取数据
        // 获取成功后调用回调
        OnDataFetched(FetchedData);
    }
};
```

## Demo 示例
一个最小化的 C++ 示例，展示如何定义自定义数据链接节点头文件。

```cpp
// MyDataLinkNode.h
#pragma once

#include "CoreMinimal.h"
#include "DataLinkNode.h"
#include "MyDataLinkNode.generated.h"

UCLASS(BlueprintType, EditInlineNew)
class MYPROJECT_API UMyDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

public:
    UMyDataLinkNode();

    // 重写数据获取逻辑
    virtual void FetchData() override;
};
```

```cpp
// MyDataLinkNode.cpp
#include "MyDataLinkNode.h"

UMyDataLinkNode::UMyDataLinkNode()
{
    // 设置一些默认属性
}

void UMyDataLinkNode::FetchData()
{
    // 实现你的数据获取逻辑，例如从文件、网络或硬件读取
    // ... (此处省略具体实现)

    // 获取到数据后，通知框架
    if (bSuccess)
    {
        OnDataFetched(YourFetchedDataStructure);
    }
    else
    {
        OnFetchError(ErrorMessage);
    }
}
```

## 模块依赖
使用本插件，你的模块通常需要依赖以下非通用模块：
| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架，所有数据链接功能的基础依赖 |
| `DataLinkJson` | 处理 JSON 格式的数据解析与生成 |
| `DataLinkHttp` | 发起 HTTP 请求 |
| `DataLinkWebSocket` | 连接 WebSocket 服务器 |
| `DataLinkDataTable` | 与 UE DataTable 交互 |
| `Json` | (引擎模块) 提供 JSON 对象操作基础 |
| `HTTP` | (引擎模块) 提供 HTTP 传输层支持 |
| `WebSockets` | (引擎模块) 提供 WebSocket 协议支持 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和共享字符串，优化内存。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至 UE_LOGF。 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复前次提交，彻底移除 FJsonObject 中的字符串重复以释放内存。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以优化内存占用。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退了之前的某次提交。 |

### 维护评价
- **创建时间**: 约 1 年前（2025年8月）。
- **活跃度**: **非常活跃**。自2026年2月至4月有持续的提交，内容涵盖内存优化、代码重构和日志改进，表明插件正在积极开发与优化中。
- **已知状态**: 仍标记为 `IsBetaVersion`，意味着功能可能尚未完全稳定，API 存在未来变更的可能。
- **推荐度**: **推荐关注与尝试**。作为运动设计系统的重要数据管道，其架构设计清晰（模块化好），且维护活跃。适合在虚拟制作项目中，特别是需要实时数据流集成的场景下评估使用。由于是Beta版，在生产环境中使用需充分测试。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)
- [核心模块 DataLink 文档](DataLink.md)
- [DataLinkDataTable 模块文档](DataLinkDataTable.md)
- [DataLinkEdGraph 模块文档](DataLinkEdGraph.md)
- [DataLinkEditor 模块文档](DataLinkEditor.md)
- [DataLinkHttp 模块文档](DataLinkHttp.md)
- [DataLinkJson 模块文档](DataLinkJson.md)
- [DataLinkJsonEditor 模块文档](DataLinkJsonEditor.md)
- [DataLinkWebSocket 模块文档](DataLinkWebSocket.md)