# Motion Design Data Link

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个用于虚拟制作（Virtual Production）场景的数据链接和流处理框架。它提供了一套基于节点图（Node Graph）的数据处理系统，允许用户通过可视化方式连接不同的数据源（如 HTTP、WebSocket、JSON、DataTable）和数据处理节点，构建复杂的数据流。`DataLinkHttp` 模块是该框架中的一个具体实现，专注于提供 HTTP 请求功能，使得用户可以在数据流图中方便地发送 HTTP 请求并获取响应数据，用于驱动场景中的动态内容或与外部服务交互。

## 使用场景

- 你在虚拟制作场景中需要从远程 API（如天气服务、股票数据、自定义后端）实时获取数据，并将其映射到场景中的物体或UI上。
- 你需要构建一个动态的 URL，其中包含来自其他数据节点的变量（如用户ID、时间戳），然后发送 HTTP 请求。
- 你希望将 HTTP 请求的响应（如 JSON 字符串）作为输入，传递给其他数据处理节点（如 `DataLinkJson` 模块）进行解析和转换。

## 蓝图用法

`DataLinkHttp` 模块主要通过其提供的节点类在数据流图中使用，而非传统的蓝图函数调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Http Request` | 发送一个 HTTP 请求。输入为 `FDataLinkHttpSettings` 结构体，输出为响应字符串。 | `UDataLinkHttpSource` |
| `Http Settings Builder` | 一个辅助构建器节点，用于通过分段方式构建 URL，并组合其他 HTTP 设置（Verb, Headers, Body）。 | `UDataLinkNodeHttpSettingsBuilder` |

### 使用示例（蓝图描述）

1.  **基本 HTTP 请求**：
    - 在数据流图中添加一个 `Http Request` 节点。
    - 创建一个 `FDataLinkHttpSettings` 结构体变量，设置其 `URL`（例如 `https://api.example.com/data`）、`Verb`（例如 `GET`）等属性。
    - 将该结构体变量连接到 `Http Request` 节点的 `InputHttpSettings` 引脚。
    - `Http Request` 节点的输出引脚将包含服务器的响应字符串，可以连接到后续的 `Json Parse` 节点或其他处理节点。

2.  **动态 URL 构建**：
    - 添加一个 `Http Settings Builder` 节点。
    - 在其 `URL Segments` 数组中，将 URL 拆分为静态部分和动态部分。例如：`["https://api.example.com/users/", "{UserId}", "/profile"]`。
    - 节点会自动识别 `{UserId}` 为一个 Token，并生成一个名为 `UserId` 的输入引脚。
    - 将其他数据节点（如一个输出用户ID的节点）连接到 `UserId` 引脚。
    - 设置 `Verb`、`Headers`、`Body` 等其他属性。
    - 将 `Http Settings Builder` 节点的输出（一个完整的 `FDataLinkHttpSettings`）连接到 `Http Request` 节点的输入。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkHttpSettings.h"
#include "DataLinkHttpSource.h"
#include "DataLinkNodeHttpSettingsBuilder.h"
```

### 基本用法

`FDataLinkHttpSettings` 是一个简单的 POD 结构体，用于封装 HTTP 请求参数。

```cpp
// 创建并配置 HTTP 设置
FDataLinkHttpSettings HttpSettings;
HttpSettings.URL = TEXT("https://jsonplaceholder.typicode.com/posts/1");
HttpSettings.Verb = TEXT("GET");
HttpSettings.Headers.Add(TEXT("Accept"), TEXT("application/json"));
// HttpSettings.Body = TEXT("{\"key\":\"value\"}"); // 对于 POST/PUT 请求

// 在自定义的数据链接节点中，你可能会在 OnExecute 函数里使用它
// 假设 InExecutor 能够提供执行 HTTP 请求的服务
```

### 进阶用法

你可以继承 `UDataLinkNode` 来创建自定义的 HTTP 相关节点，或者直接使用 `UDataLinkNodeHttpSettingsBuilder` 的逻辑来构建设置。

```cpp
// 示例：一个简化的自定义节点，它内部使用了 HttpSettings
UCLASS()
class UMyCustomHttpNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override
    {
        // 定义输入引脚，例如一个 URL 字符串
        Inputs.Add<FString>(TEXT("TargetURL"));
        // 定义输出引脚
        Outputs.Add<FString>(TEXT("Response"));
    }

    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
    {
        // 从输入引脚获取数据
        const FString* URL = InExecutor.GetInputData<FString>(TEXT("TargetURL"));
        if (!URL)
        {
            return EDataLinkExecutionReply::Unhandled;
        }

        // 构建设置
        FDataLinkHttpSettings Settings;
        Settings.URL = *URL;
        Settings.Verb = TEXT("GET");

        // 此处应调用实际的 HTTP 执行逻辑（通常由框架或另一个服务提供）
        // FString Response = ExecuteHttpRequest(Settings);

        // 将结果设置到输出引脚
        // InExecutor.SetOutputData(TEXT("Response"), Response);

        return EDataLinkExecutionReply::Handled;
    }
};
```

## Demo 示例

以下是一个最小化的自定义数据链接节点示例，它封装了一个简单的 GET 请求。

**MySimpleHttpGetNode.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "DataLinkNode.h"
#include "MySimpleHttpGetNode.generated.h"

UCLASS(MinimalAPI, DisplayName="Simple GET Request", Category="Custom")
class UMySimpleHttpGetNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;

private:
    UPROPERTY(EditAnywhere, Category="Request")
    FString URL;
};
```

**MySimpleHttpGetNode.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MySimpleHttpGetNode.h"
#include "DataLinkExecutor.h"
#include "DataLinkPinBuilder.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"

void UMySimpleHttpGetNode::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
    // 本节点没有动态输入引脚，URL 在属性面板设置
    Outputs.Add<FString>(TEXT("Response Body"));
}

EDataLinkExecutionReply UMySimpleHttpGetNode::OnExecute(FDataLinkExecutor& InExecutor) const
{
    if (URL.IsEmpty())
    {
        return EDataLinkExecutionReply::Unhandled;
    }

    // 创建 HTTP 请求
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
    HttpRequest->SetURL(URL);
    HttpRequest->SetVerb(TEXT("GET"));

    // 设置完成回调（注意：在实际的数据链接框架中，执行可能是异步的，需要正确处理）
    HttpRequest->OnProcessRequestComplete().BindLambda(
        [&InExecutor](FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnectedSuccessfully)
        {
            if (bConnectedSuccessfully && Response.IsValid())
            {
                FString ResponseString = Response->GetContentAsString();
                // 将结果设置到输出引脚
                InExecutor.SetOutputData(TEXT("Response Body"), ResponseString);
                // 通知执行器此节点已完成（具体机制取决于框架）
            }
            // ... 错误处理
        }
    );

    HttpRequest->ProcessRequest();

    // 由于请求是异步的，这里返回 Pending 或类似状态，具体取决于 DataLinkExecutor 的设计
    // 此示例仅为演示结构，实际实现需遵循框架的异步执行模型。
    return EDataLinkExecutionReply::Handled; // 或 Pending
}
```

## 模块依赖

从模块名称和常见实践推断，`DataLinkHttp` 模块很可能依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DataLink` | DataLink 核心框架，提供节点基类 `UDataLinkNode`、执行器 `FDataLinkExecutor` 等基础类型。 |
| `HTTP` | UE 内置的 HTTP 模块，用于实际执行网络请求。 |

## 维护状态

### 近期更新

```
- 2025-04-22 2ed8c4615e0d Data Link: trivial rename of http request 'response' output pin to 'response string' for clarity on type
- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

- 第一条提交对 `DataLinkHttpSource` 节点的输出引脚进行了重命名，提升了类型清晰度。
- 第二条提交将整个插件从实验性（Experimental）目录迁移到了虚拟制作（VirtualProduction）目录，标志着其重要性和稳定性的提升。

### 维护评价

`DataLink` 及其 `DataLinkHttp` 模块是一个非常新的插件（创建于 2025 年 4 月），目前处于 **Beta** 状态。从最近的提交记录看，它正在被积极地整合和优化到虚拟制作工作流中。虽然功能可能还在完善中，但作为 Epic 官方推动的虚拟制作数据流解决方案，其长期维护和更新是有保障的。**推荐在虚拟制作项目中关注和试用此插件**，但需注意其 Beta 标签可能意味着 API 或功能在未来版本中会有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现）