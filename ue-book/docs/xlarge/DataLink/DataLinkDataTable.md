# Motion Design Data Link

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个为 Motion Design（运动设计）工作流构建的数据连接和转换框架。它提供了一个基于节点图的系统，用于从各种外部源（如 HTTP 服务、WebSocket、JSON 文件、数据表）获取数据，并将其转换为引擎内部可用的格式。该插件的核心目标是实现数据驱动的动态内容生成，特别适用于虚拟制作中需要实时更新数据的场景，例如体育转播、新闻直播或交互式展览。

## 使用场景

- 你正在为虚拟制作项目构建一个实时数据驱动的图形界面（Motion Graphics），需要从后端 API 获取比分、股票或天气信息 → 使用 `DataLinkHttp` 节点。
- 你需要通过 WebSocket 接收来自外部控制软件（如 TouchDesigner）的实时参数，并驱动场景中的材质或动画 → 使用 `DataLinkWebSocket` 节点。
- 你希望将 JSON 配置文件中的数据映射到场景中的多个 Actor 属性上 → 使用 `DataLinkJson` 节点进行解析和分发。
- 你需要将引擎内的 `UDataTable` 资产作为数据源，供其他 DataLink 节点使用 → 使用 `DataLinkDataTable` 节点。
- 你需要一个可视化的编辑器来编排这些数据获取、转换和输出的逻辑流程 → 使用 `DataLinkEdGraph` 和 `DataLinkEditor` 模块提供的图表编辑器。

## 蓝图用法

DataLink 的核心逻辑通过节点图定义，但部分节点和功能也暴露给蓝图系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnBuildPins` | 定义节点的输入和输出引脚（数据接口）。这是创建自定义数据源或处理器节点的起点。 | `UDataLinkNode` |
| `OnExecute` | 节点的核心执行逻辑。当数据流经此节点时被调用，负责处理输入数据并产生输出。 | `UDataLinkNode` |

### 使用示例（蓝图描述）

DataLink 的主要使用方式是在其专用的图表编辑器中（由 `DataLinkEdGraph` 模块提供）创建和连接节点。蓝图主要用于定义自定义节点的行为。

1.  **创建自定义数据源节点**：创建一个继承自 `UDataLinkNode` 的蓝图类。
2.  **定义引脚**：在蓝图中重写 `OnBuildPins` 函数。使用 `FDataLinkPinBuilder` 添加输入和输出引脚。例如，一个简单的数据源可能只有一个输出引脚。
3.  **实现执行逻辑**：重写 `OnExecute` 函数。在此函数中编写获取数据的逻辑（例如，从某个游戏实例变量读取），然后通过 `InExecutor` 将数据传递到输出引脚。
4.  **在图表中使用**：在 DataLink 图表编辑器中，将你的自定义节点拖入图表，并将其输出引脚连接到其他处理节点或最终输出节点。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkNode.h"
#include "DataLinkPinBuilder.h"
```

### 基本用法

创建一个自定义的 DataLink 节点，用于提供一个简单的字符串数据源。

```cpp
// MyStringSourceNode.h
#pragma once
#include "DataLinkNode.h"
#include "MyStringSourceNode.generated.h"

UCLASS()
class UMyStringSourceNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;
};
```

```cpp
// MyStringSourceNode.cpp
#include "MyStringSourceNode.h"
#include "DataLinkExecutor.h"

void UMyStringSourceNode::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
    // 此节点没有输入，只有一个名为“StringValue”的字符串输出
    Outputs.Add(TEXT("StringValue")).As<FString>();
}

EDataLinkExecutionReply UMyStringSourceNode::OnExecute(FDataLinkExecutor& InExecutor) const
{
    // 生成一些示例数据
    const FString MyData = TEXT("Hello from DataLink!");
    
    // 将数据写入输出引脚
    InExecutor.SetValue(TEXT("StringValue"), MyData);
    
    // 返回成功，表示执行完成
    return EDataLinkExecutionReply::Continue;
}
```

### 进阶用法

创建一个处理节点，它接收一个字符串输入，将其转换为大写后输出。

```cpp
// StringToUpperNode.h
#pragma once
#include "DataLinkNode.h"
#include "StringToUpperNode.generated.h"

UCLASS()
class UStringToUpperNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;
};
```

```cpp
// StringToUpperNode.cpp
#include "StringToUpperNode.h"
#include "DataLinkExecutor.h"

void UStringToUpperNode::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
    // 定义一个字符串输入和一个字符串输出
    Inputs.Add(TEXT("InputString")).As<FString>();
    Outputs.Add(TEXT("OutputString")).As<FString>();
}

EDataLinkExecutionReply UStringToUpperNode::OnExecute(FDataLinkExecutor& InExecutor) const
{
    // 从输入引脚获取数据
    FString InputValue;
    if (!InExecutor.GetValue(TEXT("InputString"), InputValue))
    {
        // 如果获取失败，返回错误
        return EDataLinkExecutionReply::Error;
    }

    // 处理数据
    const FString OutputValue = InputValue.ToUpper();

    // 将结果写入输出引脚
    InExecutor.SetValue(TEXT("OutputString"), OutputValue);

    return EDataLinkExecutionReply::Continue;
}
```

## Demo 示例

以下是一个完整的自定义 DataLink 节点示例，该节点从游戏模式中读取一个整数分数并输出。

```cpp
// GameScoreSourceNode.h
#pragma once
#include "DataLinkNode.h"
#include "GameScoreSourceNode.generated.h"

UCLASS()
class UGameScoreSourceNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;
};
```

```cpp
// GameScoreSourceNode.cpp
#include "GameScoreSourceNode.h"
#include "DataLinkExecutor.h"
#include "Kismet/GameplayStatics.h"
#include "MyGameMode.h" // 假设这是你的游戏模式头文件

void UGameScoreSourceNode::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
    // 无输入，一个整数输出
    Outputs.Add(TEXT("CurrentScore")).As<int32>();
}

EDataLinkExecutionReply UGameScoreSourceNode::OnExecute(FDataLinkExecutor& InExecutor) const
{
    // 获取当前世界上下文
    UWorld* World = InExecutor.GetWorldContext();
    if (!World)
    {
        return EDataLinkExecutionReply::Error;
    }

    // 获取游戏模式并读取分数
    AMyGameMode* GameMode = Cast<AMyGameMode>(UGameplayStatics::GetGameMode(World));
    if (!GameMode)
    {
        return EDataLinkExecutionReply::Error;
    }

    const int32 Score = GameMode->GetCurrentScore();

    // 输出分数
    InExecutor.SetValue(TEXT("CurrentScore"), Score);

    return EDataLinkExecutionReply::Continue;
}
```

## 模块依赖

从 `DataLinkDataTable.Build.cs` 分析，该模块依赖于核心的 `DataLink` 模块和引擎的 `DataTable` 功能。

| 模块 | 用途 |
|---|---|
| `DataLink` | DataLink 框架的核心运行时模块，提供节点基类、执行器等基础功能。 |
| `DataTable` | 引擎的数据表系统，用于访问 `UDataTable` 资产。 |

## 维护状态

### 近期更新

```
- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```
*解读：这是该插件目录下的唯一一次提交，标志着它从实验性（Experimental）分类正式迁移到虚拟制作（VirtualProduction）分类，表明其功能已趋于稳定并准备用于生产环境。*

### 维护评价

- **创建时间**：插件于 2025 年 4 月创建，非常年轻。
- **最近更新**：仅有一次目录迁移的提交，没有功能更新或 bug 修复记录。
- **活跃度**：基于现有信息，无法判断其活跃维护状态。目录迁移可能意味着 Epic 内部已将其视为成熟组件。
- **已知问题**：`.uplugin` 中 `IsBetaVersion=true`，表明官方仍将其标记为测试版，可能存在未发现的 bug 或 API 变更。
- **推荐使用**：**谨慎推荐**。该插件功能明确，架构清晰，非常适合虚拟制作中的数据驱动场景。但由于其测试版状态和缺乏公开的维护历史，建议在非关键路径或原型项目中使用，并密切关注引擎更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [官方文档]() （暂无）
- [测试用例]() （暂未在提供的路径中发现公开测试文件）